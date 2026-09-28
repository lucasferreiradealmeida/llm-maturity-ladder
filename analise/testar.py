#!/usr/bin/env python3
"""Testes automáticos dos sistemas gerados pelos modelos (níveis 0 a 4).

Uso (a partir da raiz do repositório; no Windows, troque python3 por py):
    python3 analise/testar.py --outputs outputs --filtro "nivel*-gemini-*" --saida resultados-testes

Para cada resposta bruta (.md), o script extrai o código (extrair.py), instala as dependências
sem alterar nada, roda o sistema e executa os testes do nível:

  nível 0  roda o script duas vezes e confere o CSV (nome, data, sem sobrescrever)
  nível 1  descobre no código os comandos da CLI (cadastrar, listar, atualizar, remover e sinônimos)
           e testa cadastro, listagem, e-mail repetido, e-mail inválido, atualização e remoção;
           CLI só interativa (menu) vira teste manual
  nível 2  sobe o servidor e testa a API REST: criar, listar, duplicidade, atualizar, remover, JSON
  nível 3  os testes do nível 2 e a interface no navegador (página e chamadas da API no front-end)
  nível 4  listagem pública, escrita sem autenticação, credencial padrão, cadastro e login, escrita
           autenticada, requisição forjada sem token (CSRF), atributos do cookie, enumeração de
           usuários e inspeção do código (hash de senha, segredo de sessão, tempo de login)

Saídas em --saida: um .json por execução, relatorio.md (evidências legíveis) e resumo.csv
(sugestões para a planilha). As notas sugeridas seguem as regras da aba Instrucoes da planilha,
mas são SUGESTÕES: o avaliador confere as evidências e decide.
Requer Python 3.9+, Node.js e npm. Os projetos rodam na sua máquina: use um ambiente descartável.
"""
import argparse
import csv
import fnmatch
import http.cookiejar
import json
import os
import pathlib
import re
import shlex
import shutil
import signal
import socket
import stat
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import extrair  # noqa: E402

NPM = shutil.which("npm") or "npm"
NODE = shutil.which("node") or "node"
EMAIL = "ana.teste@exemplo.com"
DATA = "1990-05-10"
SENHA = "SenhaForte!2026x"
IGNORAR = {"node_modules", ".git"}


# ------------------------------------------------------------------ utilidades
def rodar(cmd, cwd, entrada=None, timeout=60, env=None):
    ambiente = os.environ.copy()
    ambiente.update(env or {})
    try:
        # UTF-8 explícito: no Windows o padrão seria cp1252, e a saída do Node vem em UTF-8
        p = subprocess.run(cmd, cwd=cwd, input=entrada, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout, env=ambiente)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as ex:
        out = ex.stdout.decode(errors="replace") if isinstance(ex.stdout, bytes) else (ex.stdout or "")
        return None, out, "TIMEOUT"
    except OSError as ex:
        return None, "", str(ex)


def cauda(texto, n=600):
    texto = (texto or "").strip()
    return texto if len(texto) <= n else "…" + texto[-n:]


def arquivos(base, exts=(".js", ".mjs", ".cjs")):
    for p in sorted(pathlib.Path(base).rglob("*")):
        if p.is_file() and not (IGNORAR & set(p.parts)) and p.suffix in exts:
            yield p


def ler_pacote(app):
    try:
        return json.loads((app / "package.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def porta_livre():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def endereco_aberto(porta):
    """Endereço de loopback (IPv4 ou IPv6) em que a porta aceita conexão, já no formato de URL, ou None."""
    for familia, host, url in ((socket.AF_INET, "127.0.0.1", "127.0.0.1"), (socket.AF_INET6, "::1", "[::1]")):
        try:
            with socket.socket(familia) as s:
                s.settimeout(0.3)
                if s.connect_ex((host, porta)) == 0:
                    return url
        except OSError:  # IPv6 desativado, por exemplo
            continue
    return None


def porta_aberta(porta):
    return endereco_aberto(porta) is not None


def apagar_pasta(pasta):
    """shutil.rmtree que também apaga arquivos somente leitura (comum no node_modules do Windows)."""
    def forcar(funcao, caminho, _erro):
        os.chmod(caminho, stat.S_IWRITE)
        funcao(caminho)
    if sys.version_info >= (3, 12):
        shutil.rmtree(pasta, onexc=forcar)
    else:
        shutil.rmtree(pasta, onerror=forcar)


# ------------------------------------------------------------------ projeto
def pasta_app(proj):
    """Pasta com o package.json principal (a raiz ou, por exemplo, backend/)."""
    if (proj / "package.json").exists():
        return proj
    for p in sorted(proj.rglob("package.json")):
        if not (IGNORAR & set(p.parts)):
            pj = ler_pacote(p.parent) or {}
            if pj.get("scripts", {}).get("start") or pj.get("main"):
                return p.parent
    return proj


EMBUTIDOS = {"fs", "path", "http", "https", "crypto", "readline", "os", "url", "util", "events", "child_process",
             "zlib", "stream", "buffer", "querystring", "net", "process", "assert", "timers", "worker_threads",
             "fs/promises", "readline/promises", "string_decoder", "dns", "tls", "perf_hooks"}


def dependencias_externas(fontes):
    codigo = "\n".join(t for a, t in fontes.items() if a.endswith((".js", ".mjs", ".cjs")))
    nomes = re.findall(r"""require\(\s*['"]([^./'"][^'"]*)['"]\s*\)""", codigo)
    nomes += re.findall(r"""import\s+(?:[\w{}*\s,]+\s+from\s+)?['"]([^./'"][^'"]*)['"]""", codigo)
    pacotes = set()
    for n in nomes:
        n = n.replace("node:", "")
        base = "/".join(n.split("/")[:2]) if n.startswith("@") else n.split("/")[0]
        if base not in EMBUTIDOS and n not in EMBUTIDOS:
            pacotes.add(base)
    return sorted(pacotes)


def instalar(app, md_texto="", fontes=None):
    if not (app / "package.json").exists():
        externos = dependencias_externas(fontes or {})
        if not externos:
            return {"ok": None, "detalhe": "sem package.json e sem dependências externas (nada a instalar)"}
        # O modelo não entregou o package.json. Segue as instruções da própria resposta (não conta como correção,
        # mas falha o requisito de entregar todos os arquivos necessários).
        pedidos = []
        for trecho in re.findall(r"npm\s+(?:install|i)\s+([^\n`&|;]+)", md_texto):
            pedidos += [t for t in trecho.split() if not t.startswith("-")]
        pacotes = sorted(set(pedidos) | set(externos))
        rodar([NPM, "init", "-y"], app, timeout=60)
        codigo, out, err = rodar([NPM, "install", "--no-audit", "--no-fund", "--loglevel=error"] + pacotes, app, timeout=900)
        return {"ok": codigo == 0, "sem_package_json": True,
                "detalhe": f"sem package.json: seguiu as instruções do modelo (npm init -y; npm install {' '.join(pacotes)})"
                           + ("" if codigo == 0 else " — falhou: " + cauda(err or out))}
    if ler_pacote(app) is None:
        return {"ok": False, "detalhe": "package.json inválido (não é JSON válido)"}
    codigo, out, err = rodar([NPM, "install", "--no-audit", "--no-fund", "--loglevel=error"], app, timeout=900)
    return {"ok": codigo == 0, "detalhe": cauda(err or out) if codigo != 0 else "npm install ok"}


def comando_inicio(app):
    pj = ler_pacote(app) or {}
    start = pj.get("scripts", {}).get("start", "")
    m = re.search(r"node\s+(?:--[\w-]+(?:=\S+)?\s+)*([\w./-]+\.(?:c|m)?js)", start)
    if m and (app / m.group(1)).exists():
        return [NODE, m.group(1)]
    if pj.get("main") and (app / pj["main"]).exists():
        return [NODE, pj["main"]]
    bins = pj.get("bin")
    if isinstance(bins, str) and (app / bins).exists():
        return [NODE, bins]
    if isinstance(bins, dict):
        for alvo in bins.values():
            if (app / alvo).exists():
                return [NODE, alvo]
    for c in ["server.js", "app.js", "index.js", "main.js", "cli.js", "src/server.js", "src/app.js",
              "src/index.js", "src/cli.js"]:
        if (app / c).exists():
            return [NODE, c]
    raiz = [p.name for p in app.glob("*.js")]
    return [NODE, raiz[0]] if len(raiz) == 1 else None


def codigo_fonte(proj):
    # chaves sempre com "/" (as_posix), para as regras de caminho valerem também no Windows
    return {p.relative_to(proj).as_posix(): p.read_text(encoding="utf-8", errors="replace") for p in arquivos(proj)}


# ------------------------------------------------------------------ servidor e HTTP
class Servidor:
    def __init__(self, app, cmd, porta):
        self.porta_pedida = porta
        self.saida = []
        # uma porta já ocupada antes do teste nunca é tomada como a do sistema testado
        self.ocupadas = {p for p in (3000, 3001, 5000, 8080) if porta_aberta(p)}
        env = os.environ.copy()
        env.update({"PORT": str(porta), "HOST": "127.0.0.1", "NODE_ENV": "development",
                    # configurações que os READMEs dos modelos pedem para definir antes de subir o sistema
                    "JWT_SECRET": "segredo-de-teste-" + str(porta), "SESSION_SECRET": "segredo-de-teste-" + str(porta),
                    "ADMIN_USERNAME": "usuario_teste", "ADMIN_PASSWORD": SENHA, "ADMIN_DISPLAY_NAME": "Usuario Teste"})
        # grupo de processos próprio, para encerrar o servidor e os filhos dele ao final do teste
        grupo = ({"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt"
                 else {"start_new_session": True})
        self.proc = subprocess.Popen(cmd, cwd=app, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     stdin=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace", **grupo)
        threading.Thread(target=self._ler, daemon=True).start()

    def _ler(self):
        for linha in self.proc.stdout:
            self.saida.append(linha)

    def esperar(self, timeout=30):
        fim = time.time() + timeout
        while time.time() < fim:
            if self.proc.poll() is not None:
                return None
            candidatas = [self.porta_pedida]
            texto = "".join(self.saida)
            candidatas += [int(p) for p in re.findall(r"(?:localhost|127\.0\.0\.1|0\.0\.0\.0|porta|port)\D{0,3}(\d{4,5})", texto, re.I)]
            candidatas += [3000]
            for p in candidatas:
                if p in self.ocupadas and p != self.porta_pedida:
                    continue
                if porta_aberta(p):
                    return p
            time.sleep(0.4)
        return None

    def parar(self):
        if self.proc.poll() is None:
            if os.name == "nt":
                # o Windows não tem os.killpg: o taskkill /T encerra a árvore de processos
                subprocess.run(["taskkill", "/PID", str(self.proc.pid), "/T", "/F"], capture_output=True)
                try:
                    self.proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.proc.kill()
            else:
                try:
                    os.killpg(self.proc.pid, signal.SIGTERM)
                    self.proc.wait(timeout=5)
                except (ProcessLookupError, subprocess.TimeoutExpired):
                    try:
                        os.killpg(self.proc.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
        return cauda("".join(self.saida), 800)


class SemRedirecionar(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class Resposta:
    def __init__(self, status, cabecalhos, texto):
        self.status = status
        self.cabecalhos = cabecalhos
        self.texto = texto
        try:
            self.json = json.loads(texto)
        except ValueError:
            self.json = None

    @property
    def ok(self):
        return self.status is not None and 200 <= self.status < 300

    @property
    def local(self):
        """Caminho do redirecionamento, sem a query (ex.: /admin?ok=login -> /admin)."""
        bruto = self.cabecalhos.get("Location", "") if self.cabecalhos else ""
        return urllib.parse.urlparse(bruto).path if bruto else ""

    def resumo(self):
        return f"{self.status} {cauda(self.texto, 160)}"


class Cliente:
    def __init__(self, base):
        self.base = base
        self.cookies = http.cookiejar.CookieJar()
        self.abridor = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookies), SemRedirecionar)
        self.token = None
        self.ultimos_set_cookie = []

    def pedir(self, metodo, caminho, json_=None, form=None, cabecalhos=None, timeout=10):
        dados, hdr = None, {"Accept": "application/json, text/html;q=0.9, */*;q=0.8"}
        if json_ is not None:
            dados, hdr["Content-Type"] = json.dumps(json_).encode(), "application/json"
        elif form is not None:
            dados, hdr["Content-Type"] = urllib.parse.urlencode(form).encode(), "application/x-www-form-urlencoded"
        if self.token:
            hdr["Authorization"] = f"Bearer {self.token}"
        hdr.update(cabecalhos or {})
        req = urllib.request.Request(self.base + caminho, data=dados, method=metodo, headers=hdr)
        try:
            r = self.abridor.open(req, timeout=timeout)
            resp = Resposta(r.status, r.headers, r.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            resp = Resposta(e.code, e.headers, e.read().decode("utf-8", "replace"))
        except (urllib.error.URLError, OSError) as e:
            resp = Resposta(None, {}, f"erro de conexão: {e}")
        if resp.cabecalhos:
            self.ultimos_set_cookie = resp.cabecalhos.get_all("Set-Cookie") or [] if hasattr(resp.cabecalhos, "get_all") else []
        return resp


# ------------------------------------------------------------------ rotas (análise estática)
RE_ROTA = re.compile(r"""\b(\w+)\.(get|post|put|patch|delete)\(\s*['"`](/[^'"`]*)['"`]""")
RE_ROTA_ENCADEADA = re.compile(r"""\.route\(\s*['"`](/[^'"`]*)['"`]\s*\)((?:\s*\.(?:get|post|put|patch|delete)\()+)""")
RE_REQUIRE = re.compile(r"""(?:const|let|var)\s+(\w+)\s*=\s*require\(\s*['"](\.[^'"]+)['"]\s*\)""")
RE_IMPORT = re.compile(r"""import\s+(\w+)\s+from\s+['"](\.[^'"]+)['"]""")
RE_USE = re.compile(r"""\.use\(\s*['"`](/[^'"`]*)['"`]\s*,\s*(?:[\w.]+\s*,\s*)*(require\(\s*['"](\.[^'"]+)['"]\s*\)|\w+)""")


def resolver(origem, relativo, fontes):
    base = (pathlib.PurePosixPath(origem).parent / relativo)
    partes = []
    for p in base.parts:
        if p == "..":
            if partes:
                partes.pop()
        elif p != ".":
            partes.append(p)
    alvo = "/".join(partes)
    for cand in (alvo, alvo + ".js", alvo + "/index.js", alvo + ".mjs", alvo + ".cjs"):
        if cand in fontes:
            return cand
    return None


def descobrir_rotas(fontes):
    prefixos = {}
    for arq, texto in fontes.items():
        variaveis = {v: resolver(arq, r, fontes) for v, r in RE_REQUIRE.findall(texto) + RE_IMPORT.findall(texto)}
        for prefixo, alvo, req_rel in RE_USE.findall(texto):
            destino = resolver(arq, req_rel, fontes) if req_rel else variaveis.get(alvo)
            if destino:
                prefixos[destino] = prefixo.rstrip("/")
    rotas = set()
    for arq, texto in fontes.items():
        prefixo = prefixos.get(arq, "")
        for _obj, metodo, caminho in RE_ROTA.findall(texto):
            rotas.add((metodo.upper(), (prefixo + caminho).replace("//", "/") or "/"))
        for caminho, cadeia in RE_ROTA_ENCADEADA.findall(texto):
            for metodo in re.findall(r"\.(get|post|put|patch|delete)\(", cadeia):
                rotas.add((metodo.upper(), (prefixo + caminho).replace("//", "/") or "/"))
    return sorted(rotas)


PALAVRAS_RECURSO = ("user", "usuario", "record", "registro", "item", "profile", "perfil", "cadastro", "pessoa")
PALAVRAS_AUTH = ("login", "logout", "register", "signup", "signin", "registrar", "cadastr-se", "session", "sessao", "auth", "csrf", "me")


def eh_rota_auth(caminho):
    return any(p in caminho.lower() for p in ("login", "logout", "register", "signup", "signin", "registrar",
                                               "session", "sessao", "csrf", "/me", "/auth"))


def ordenar_recursos(caminhos):
    def chave(c):
        c_low = c.lower()
        return (0 if c_low.startswith("/api") else 1, 0 if any(p in c_low for p in PALAVRAS_RECURSO) else 1, len(c))
    return sorted(dict.fromkeys(caminhos), key=chave)


# ------------------------------------------------------------------ nível 0
def testar_nivel0(proj, app, fontes, res):
    cmd = comando_inicio(app)
    if not cmd:
        res["falhas"].append("não foi possível identificar o script")
        return
    antes = {p: p.stat().st_mtime for p in app.rglob("*.csv") if not (IGNORAR & set(p.parts))}
    for nome in ("Ana Teste", "Bruno Teste"):
        codigo, out, err = rodar(cmd + [nome], app, entrada=nome + "\n", timeout=20)
        res["passos"].append({"passo": f"rodar {' '.join(cmd[1:])} \"{nome}\"", "codigo": codigo, "saida": cauda(out + err, 300)})
    csvs = [p for p in app.rglob("*.csv") if not (IGNORAR & set(p.parts)) and (p not in antes or p.stat().st_mtime != antes[p])]
    if not csvs:
        if re.search(r"prompt-sync|inquirer|readline", "\n".join(fontes.values())):
            res["manual"] = ("script interativo que exige terminal: rode duas vezes à mão, informe dois nomes e confira o CSV "
                             "(nome, data de cadastro, duas linhas).")
        else:
            res["falhas"].append("nenhum CSV criado ou alterado")
        return
    texto = csvs[0].read_text(encoding="utf-8", errors="replace")
    linhas = [l for l in texto.splitlines() if l.strip()]
    res["evidencias"]["csv"] = {"arquivo": csvs[0].relative_to(proj).as_posix(), "linhas": linhas[:6]}
    tem_ana = any("Ana Teste" in l for l in linhas)
    tem_bruno = any("Bruno Teste" in l for l in linhas)
    datas = [l for l in linhas if re.search(r"\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}", l)]
    res["checagens"]["registra o nome no CSV"] = tem_ana or tem_bruno
    res["checagens"]["grava a data de cadastro"] = len(datas) >= 2
    res["checagens"]["acrescenta sem sobrescrever (2 execuções = 2 linhas)"] = tem_ana and tem_bruno


# ------------------------------------------------------------------ nível 1
SUBCOMANDOS = {
    "init": ["init", "inicializar", "setup", "init-db", "migrate", "schema"],
    "add": ["add", "cadastrar", "create", "criar", "adicionar", "novo", "insert", "registrar"],
    "list": ["list", "listar", "ls", "todos", "all"],
    "update": ["update", "atualizar", "editar", "edit"],
    "remove": ["remove", "remover", "delete", "excluir", "deletar", "rm", "del"],
}
FLAGS_NOME = ["name", "nome"]
FLAGS_DATA = ["birthdate", "birth-date", "birthDate", "birth_date", "nascimento", "data-nascimento", "dataNascimento",
              "data_nascimento", "dob", "data"]
FLAGS_CONFIRMA = ["--yes", "-y", "--sim", "--force", "-f", "--confirm", "--confirmar"]
ERRO = re.compile(r"\berro\b|\berror\b|inválid|invalid|obrigat|required|\buso:|\busage\b|não encontrad|not found|desconhecid|unknown", re.I)


def vocabulario(codigo):
    literais = set(re.findall(r"""['"`]([\w-]+)['"`]""", codigo)) | set(re.findall(r"""case\s+['"]([\w-]+)['"]""", codigo))
    literais |= set(re.findall(r"""\.command\(\s*['"`]([\w-]+)""", codigo))  # commander: .command('delete <id>')
    subs = {cat: [s for s in nomes if s in literais] for cat, nomes in SUBCOMANDOS.items()}
    flags = set(re.findall(r"--([a-zA-Z][\w-]*)", codigo))
    return subs, flags


def candidatos(subs, flags, cat, campos, ident=None):
    """Formas plausíveis de chamar a operação: subcomando + flags (se o código as cita) ou posicionais."""
    nomes = subs.get(cat) or SUBCOMANDOS[cat]
    fn = [f for f in FLAGS_NOME if f in flags] or FLAGS_NOME
    fd = [f for f in FLAGS_DATA if f in flags] or FLAGS_DATA[:2]
    saida = []
    for sub in nomes:
        base_id = [] if ident is None else [str(ident)]
        id_flag = [] if ident is None else ["--id", str(ident)]
        if cat == "add":
            for a in fn:
                for d in fd:
                    saida.append([sub, f"--{a}", campos["nome"], "--email", campos["email"], f"--{d}", campos["data"]])
            saida.append([sub, campos["nome"], campos["email"], campos["data"]])
        elif cat == "update":
            for a in fn:
                saida += [[sub] + base_id + [f"--{a}", campos["nome"]], [sub] + id_flag + [f"--{a}", campos["nome"]]]
            saida.append([sub] + base_id + [campos["nome"], campos["email"], campos["data"]])
        elif cat == "remove":
            confirma = [f for f in FLAGS_CONFIRMA if f.lstrip("-") in flags]
            saida += [[sub] + base_id + confirma, [sub] + id_flag + confirma]
        else:
            saida.append([sub])
    return [list(x) for x in dict.fromkeys(tuple(c) for c in saida)]


def testar_nivel1(proj, app, fontes, md_texto, res):
    codigo = "\n".join(fontes.values())
    le_args = bool(re.search(r"process\.argv|commander|yargs|minimist|parseArgs", codigo))
    cmd = comando_inicio(app)
    if not le_args or not cmd:
        res["manual"] = ("CLI interativa (menu): teste manual. Rode o programa, cadastre um usuário com "
                         f"{EMAIL}, liste, tente o mesmo e-mail de novo, tente 'email-invalido', atualize, remova e anote o resultado.")
        return
    subs, flags = vocabulario(codigo)
    res["evidencias"]["subcomandos encontrados"] = {k: v for k, v in subs.items() if v}

    def executar(rotulo, argumentos, entrada="\n"):
        codigo_saida, out, err = rodar(cmd + argumentos, app, entrada=entrada, timeout=20)
        texto = (out or "") + (err or "")
        res["passos"].append({"passo": rotulo, "comando": " ".join(argumentos), "codigo": codigo_saida, "saida": cauda(texto, 240)})
        return codigo_saida, texto

    def listar():
        for argumentos in candidatos(subs, flags, "list", {}):
            c, t = executar("listar", argumentos)
            if c == 0 and not ERRO.search(t):
                return t
        return ""

    scripts = (ler_pacote(app) or {}).get("scripts", {})
    init_npm = [k for k in scripts if re.fullmatch(r"(setup|init|init-db|initdb|db:init|db:setup|migrate|schema)", k)]
    if init_npm:
        codigo_saida, out, err = rodar([NPM, "run", init_npm[0]], app, timeout=60)
        res["passos"].append({"passo": "criar schema", "comando": f"npm run {init_npm[0]}", "codigo": codigo_saida, "saida": cauda(out + err, 240)})
    elif subs.get("init"):
        executar("criar schema", candidatos(subs, flags, "init", {})[0])
    campos = {"nome": "Ana Teste", "email": EMAIL, "data": DATA}
    forma_add = None
    for argumentos in candidatos(subs, flags, "add", campos):
        c, t = executar("cadastrar", argumentos)
        if c == 0 and not ERRO.search(t):
            forma_add = argumentos
            break
    lista = listar() if forma_add else ""
    res["checagens"]["cadastra usuário"] = forma_add is not None
    res["checagens"]["lista usuários"] = EMAIL in lista
    if not forma_add:
        res["falhas"].append("nenhuma forma de cadastro funcionou: confira os comandos manualmente")
        return
    c, t = executar("cadastrar de novo (duplicidade)", forma_add)
    res["checagens"]["bloqueia e-mail duplicado"] = c not in (0, None) or bool(re.search(r"já|exist|duplic|already|unique|cadastrad", t, re.I))
    invalido = [("email-invalido" if a == EMAIL else a) for a in forma_add]
    c, t = executar("cadastrar com e-mail inválido", invalido)
    res["checagens"]["valida formato do e-mail"] = c not in (0, None) or bool(re.search(r"inválid|invalid|formato", t, re.I))
    linha = next((l for l in lista.splitlines() if EMAIL in l), "")
    # ignora o índice 0 do console.table e a data; o banco novo começa no id 1
    numeros = [n for n in re.findall(r"\b(\d+)\b", linha.replace(DATA, "")) if n != "0"]
    ident = numeros[0] if numeros else "1"
    res["evidencias"]["id do cadastro"] = ident
    novo = {"nome": "Ana Atualizada", "email": EMAIL, "data": DATA}
    atualizou = False
    for argumentos in candidatos(subs, flags, "update", novo, ident):
        c, t = executar("atualizar", argumentos)
        if c == 0 and not ERRO.search(t) and "Ana Atualizada" in listar():
            atualizou = True
            break
    res["checagens"]["atualiza usuário"] = atualizou
    removeu = False
    for argumentos in candidatos(subs, flags, "remove", {}, ident):
        for resposta in ("y\n", "s\n", "sim\n", "yes\n"):  # confirmação em inglês ou português
            c, t = executar("remover", argumentos, entrada=resposta)
            if c == 0 and EMAIL not in listar():
                removeu = True
                break
            if not re.search(r"\?|confirm|certeza|sure", t, re.I):
                break  # não pediu confirmação: não adianta repetir
        if removeu:
            break
    res["checagens"]["remove usuário"] = removeu


# ------------------------------------------------------------------ níveis 2 e 3
def cargas(nome, email):
    base = {"name": nome, "email": email}
    datas = ["birthDate", "birth_date", "dateOfBirth", "birthdate", "dob", "data_nascimento", "dataNascimento", "nascimento"]
    tudo = {"name": nome, "nome": nome, "email": email, **{d: DATA for d in datas}}
    variantes = [tudo] + [{**base, d: DATA} for d in datas[:5]]
    variantes += [{"nome": nome, "email": email, d: DATA} for d in datas[5:]] + [base, {"nome": nome, "email": email}]
    return variantes


def extrair_id(r):
    j = r.json
    if isinstance(j, dict):
        for chave in ("id", "_id", "userId", "usuarioId"):
            if chave in j:
                return j[chave]
        for sub in ("data", "user", "usuario", "dados", "item", "record", "registro"):
            if isinstance(j.get(sub), dict):
                for chave in ("id", "_id"):
                    if chave in j[sub]:
                        return j[sub][chave]
    return None


def lista_de(r):
    j = r.json
    if isinstance(j, list):
        return j
    if isinstance(j, dict):
        for v in j.values():
            if isinstance(v, list):
                return v
    return None


def testar_api(cli, rotas, res, nivel):
    candidatos = [c for m, c in rotas if m in ("GET", "POST") and ":" not in c and not eh_rota_auth(c) and c != "/"]
    candidatos += ["/api/users", "/users", "/api/usuarios", "/usuarios", "/api/v1/users"]
    recurso = None
    for c in ordenar_recursos(candidatos):
        r = cli.pedir("GET", c)
        if r.ok and lista_de(r) is not None:
            recurso = c
            break
    if not recurso:
        res["falhas"].append("rota de listagem não encontrada")
        return None
    res["evidencias"]["rota"] = recurso
    criado, carga = None, None
    for variante in cargas("Ana Teste", EMAIL):
        r = cli.pedir("POST", recurso, json_=variante)
        if r.ok:
            criado, carga = r, variante
            break
    res["passos"].append({"passo": f"POST {recurso}", "resultado": criado.resumo() if criado else "nenhuma variante de campos aceita"})
    if not criado:
        res["checagens"]["cria usuário"] = False
        return recurso
    ident = extrair_id(criado)
    r_lista = cli.pedir("GET", recurso)
    itens = lista_de(r_lista) or []
    if ident is None:
        for item in itens:
            if isinstance(item, dict) and EMAIL in json.dumps(item):
                ident = item.get("id", item.get("_id"))
    json_ok = "json" in (criado.cabecalhos.get("Content-Type", "") if criado.cabecalhos else "") and \
              "json" in (r_lista.cabecalhos.get("Content-Type", "") if r_lista.cabecalhos else "")
    dup = cli.pedir("POST", recurso, json_=carga)
    inval = cli.pedir("POST", recurso, json_={**carga, "email": "email-invalido"})
    vazio = cli.pedir("POST", recurso, json_={})
    atualizado = None
    if ident is not None:
        nova = {k: ("Ana Atualizada" if k in ("name", "nome") else v) for k, v in carga.items()}
        atualizado = cli.pedir("PUT", f"{recurso}/{ident}", json_=nova)
        if atualizado.status in (404, 405) or atualizado.status is None:
            atualizado = cli.pedir("PATCH", f"{recurso}/{ident}", json_=nova)
    apos_update = json.dumps(lista_de(cli.pedir("GET", recurso)) or [])
    removido = cli.pedir("DELETE", f"{recurso}/{ident}") if ident is not None else None
    apos_delete = json.dumps(lista_de(cli.pedir("GET", recurso)) or [])
    res["passos"] += [
        {"passo": "POST duplicado", "resultado": dup.resumo()},
        {"passo": "POST e-mail inválido", "resultado": inval.resumo()},
        {"passo": "POST sem campos", "resultado": vazio.resumo()},
        {"passo": f"PUT/PATCH {recurso}/{ident}", "resultado": atualizado.resumo() if atualizado else "sem id"},
        {"passo": f"DELETE {recurso}/{ident}", "resultado": removido.resumo() if removido else "sem id"},
    ]
    res["evidencias"]["status"] = {"criar": criado.status, "duplicado": dup.status, "email_invalido": inval.status,
                                   "sem_campos": vazio.status, "atualizar": atualizado.status if atualizado else None,
                                   "remover": removido.status if removido else None, "campos": sorted(carga)}
    res["checagens"]["cria usuário"] = True
    res["checagens"]["lista usuários"] = EMAIL in json.dumps(itens)
    res["checagens"]["atualiza usuário"] = bool(atualizado and atualizado.ok and "Ana Atualizada" in apos_update)
    res["checagens"]["remove usuário"] = bool(removido and removido.ok and EMAIL not in apos_delete)
    res["checagens"]["respostas em JSON"] = json_ok
    res["checagens"]["recusa e-mail duplicado com 4xx"] = dup.status is not None and 400 <= dup.status < 500
    res["informativo"]["código de criação"] = criado.status
    res["informativo"]["código para duplicidade"] = dup.status
    res["informativo"]["recusa e-mail inválido"] = inval.status is not None and 400 <= inval.status < 500
    return recurso


def testar_front(cli, fontes, recurso, res):
    r = cli.pedir("GET", "/")
    html = r.texto if r.ok else ""
    res["checagens"]["serve interface no navegador"] = bool(re.search(r"<(form|input|table|script)", html, re.I))
    front = "\n".join(t for a, t in fontes.items() if re.search(r"(^|/)(public|frontend|static|client|views)/", a))
    front += "\n".join(t for a, t in fontes.items() if a.endswith(".html"))
    metodos = {m.upper() for m in re.findall(r"['\"`](POST|PUT|PATCH|DELETE)['\"`]", front, re.I)}
    metodos |= {m.upper() for m in re.findall(r"axios\.(post|put|patch|delete)\b", front, re.I)}
    res["informativo"]["métodos usados pelo front-end"] = sorted(metodos) or "nenhum encontrado"
    res["checagens"]["front-end cadastra, edita e remove"] = "POST" in metodos and bool(metodos & {"PUT", "PATCH"}) and "DELETE" in metodos


# ------------------------------------------------------------------ nível 4
def buscar_token_csrf(cli, paginas, resp_login):
    if resp_login is not None and isinstance(resp_login.json, dict):
        for chave in ("csrfToken", "csrf", "_csrf", "xsrfToken"):
            if resp_login.json.get(chave):
                return resp_login.json[chave]
    for pagina in paginas + ["/api/csrf-token", "/api/csrf", "/csrf-token", "/api/session", "/api/me", "/me"]:
        r = cli.pedir("GET", pagina)
        if not r.texto:
            continue
        if isinstance(r.json, dict):
            for chave in ("csrfToken", "csrf", "_csrf", "token"):
                if isinstance(r.json.get(chave), str) and chave != "token":
                    return r.json[chave]
        m = re.search(r"""name=["'](?:csrfToken|_csrf|csrf)["'][^>]*?value=["']([^"']+)["']""", r.texto) or \
            re.search(r"""value=["']([^"']+)["'][^>]*?name=["'](?:csrfToken|_csrf|csrf)["']""", r.texto) or \
            re.search(r"""<meta[^>]+name=["']csrf-token["'][^>]+content=["']([^"']+)["']""", r.texto)
        if m:
            return m.group(1)
    return None


def cabecalhos_csrf(token):
    return {"X-CSRF-Token": token, "CSRF-Token": token, "X-XSRF-TOKEN": token} if token else {}


CARGA_ESCRITA = {"name": "Registro Teste", "nome": "Registro Teste", "title": "Registro Teste", "titulo": "Registro Teste",
                 "description": "teste", "descricao": "teste", "email": "registro.teste@exemplo.com",
                 "username": "registro_teste", "password": SENHA, "displayName": "Registro Teste",
                 "birthDate": DATA, "birth_date": DATA, "dataNascimento": DATA}


def aceito(r):
    return r is not None and (r.ok or (r.status in (301, 302, 303) and "login" not in r.local.lower()))


def bloqueada(r):
    return r is not None and (r.status in (401, 403) or (r.status in (301, 302, 303) and "login" in r.local.lower()))


def rotas_de_escrita(rotas, lista):
    estaticas = [c for m, c in rotas if m == "POST" and ":" not in c and not eh_rota_auth(c)]
    if estaticas:
        return ordenar_recursos(estaticas)
    return ordenar_recursos(([lista] if lista and lista != "/" else []) +
                            ["/api/records", "/api/users", "/api/items", "/records", "/users", "/items"])


def tentar_escrita(cli, rotas_escrita, token_csrf=None, carga=None):
    """Tenta criar um registro; devolve (rota, modo, resposta) da primeira escrita aceita ou a última resposta
    de uma rota existente. Rotas ou métodos inexistentes (404/405) são ignorados."""
    carga = dict(carga or CARGA_ESCRITA)
    if token_csrf:
        carga.update({"csrfToken": token_csrf, "_csrf": token_csrf})
    ultimo = None
    for rota in rotas_escrita:
        for modo in ("json", "form"):
            r = cli.pedir("POST", rota, json_=carga if modo == "json" else None, form=carga if modo == "form" else None,
                          cabecalhos=cabecalhos_csrf(token_csrf))
            if r.status in (404, 405) or r.status is None:
                continue
            ultimo = (rota, modo, r)
            if aceito(r):
                return ultimo
    return ultimo


def escrita_anonima(base, rotas_escrita):
    """Todas as respostas de escrita sem autenticação nas rotas existentes."""
    respostas = []
    for rota in rotas_escrita[:4]:
        for modo in ("json", "form"):
            r = Cliente(base).pedir("POST", rota, json_=CARGA_ESCRITA if modo == "json" else None,
                                    form=CARGA_ESCRITA if modo == "form" else None)
            if r.status in (404, 405) or r.status is None:
                continue
            respostas.append((rota, modo, r))
    return respostas


def login(cli, rotas_login, usuario, senha, email=None):
    """Tenta autenticar; devolve a sessão, {"limite": True} se o sistema limitou as tentativas, ou None."""
    variantes = ({"username": usuario, "password": senha}, {"email": email or usuario, "password": senha},
                 {"usuario": usuario, "senha": senha}, {"user": usuario, "password": senha})
    for rota in rotas_login:
        rota_existe = False
        for campos in variantes:
            for modo in ("json", "form"):
                r = cli.pedir("POST", rota, json_=campos if modo == "json" else None, form=campos if modo == "form" else None)
                if r.status in (404, 405) or r.status is None:
                    continue
                rota_existe = True
                if r.status == 429:
                    return {"limite": True, "resposta": r}
                token = None
                if isinstance(r.json, dict):
                    for chave in ("token", "accessToken", "access_token", "jwt"):
                        if isinstance(r.json.get(chave), str):
                            token = r.json[chave]
                    if isinstance(r.json.get("data"), dict) and isinstance(r.json["data"].get("token"), str):
                        token = r.json["data"]["token"]
                sucesso = token or (r.ok and cli.ultimos_set_cookie) or \
                    (r.status in (301, 302, 303) and "login" not in r.local.lower() and cli.ultimos_set_cookie)
                if sucesso:
                    return {"rota": rota, "modo": modo, "token": token, "resposta": r, "set_cookie": list(cli.ultimos_set_cookie)}
            if not rota_existe:
                break
    return None


def sessao_valida(s):
    return bool(s) and not s.get("limite")


def inspecao_estatica(fontes, res):
    codigo = "\n".join(t for a, t in fontes.items() if not re.search(r"(^|/)(public|frontend|static|client)/", a))
    front = "\n".join(t for a, t in fontes.items() if re.search(r"(^|/)(public|frontend|static|client|views)/", a) or a.endswith(".html"))
    ev = res["evidencias"].setdefault("codigo", {})
    kdf = re.findall(r"\b(bcryptjs|bcrypt|argon2|scrypt|pbkdf2)\b", codigo, re.I)
    ev["hash de senha"] = sorted({k.lower() for k in kdf}) or "nenhuma função de derivação encontrada"
    fixo = re.findall(r"""(?:const|let|var)\s+(\w*(?:SECRET|Secret|secret|KEY)\w*)\s*=\s*['"]([^'"]{4,})['"]""", codigo)
    fallback = re.findall(r"""process\.env\.(\w+)\s*(?:\|\||\?\?)\s*['"]([^'"]+)['"]""", codigo)
    fallback = [f for f in fallback if re.search(r"SECRET|KEY|TOKEN", f[0], re.I)]
    usa_jwt = bool(re.search(r"jsonwebtoken|jwt\.sign", codigo))
    usa_express_session = bool(re.search(r"express-session|cookie-session", codigo))
    exige_env = bool(re.search(r"if\s*\(\s*!\s*(?:process\.env\.)?\w*SECRET\w*\s*\)\s*\{?[^}]{0,120}(throw|process\.exit)", codigo))
    ev["segredo fixo no código"] = fixo[:3]
    ev["segredo com valor padrão"] = fallback[:3]
    if fixo:
        seg = 0
    elif fallback:
        seg = 0.5
    elif (usa_jwt or usa_express_session) and not exige_env:
        seg = None  # não deu para concluir
    else:
        seg = 1
    ev["login: verificação fictícia quando o usuário não existe"] = bool(re.search(
        r"dummy|fake.?(hash|password|senha)|mesmo quando o usu[aá]rio n[aã]o existe|usu[aá]rio n[aã]o existe[^\n]{0,80}(scrypt|bcrypt|hash|verifica)"
        r"|even (if|when) the user (does not|doesn't) exist|enumera", codigo, re.I))
    ev["front-end guarda token em localStorage"] = bool(re.search(r"localStorage\.setItem", front))
    ev["sameSite no código"] = re.findall(r"sameSite\s*:\s*['\"]?(\w+)", codigo, re.I)[:3]
    ev["credencial fixa no código"] = re.findall(r"""['"](admin123|admin|123456|password|senha123)['"]""", codigo)[:4]
    return seg


def testar_nivel4(cli, fontes, rotas, res, app):
    seg_segredo = inspecao_estatica(fontes, res)
    codigo = "\n".join(fontes.values())
    gets = [c for m, c in rotas if m == "GET" and ":" not in c and not eh_rota_auth(c)]
    lista = None
    for c in ordenar_recursos(gets + ["/api/records", "/records", "/api/users", "/users", "/api/items", "/items", "/"]):
        r = cli.pedir("GET", c)
        if r.ok:
            lista = c
            break
    res["checagens"]["listagem pública"] = lista is not None
    res["evidencias"]["rota de listagem"] = lista
    escrita = rotas_de_escrita(rotas, lista)

    anonimas = escrita_anonima(cli.base, escrita)
    aceitas = [x for x in anonimas if aceito(x[2])]
    res["checagens"]["bloqueia escrita sem autenticação"] = bool(anonimas) and not aceitas
    for rota, modo, r in anonimas[:4]:
        res["passos"].append({"passo": f"POST {rota} sem autenticação ({modo})", "resultado": r.resumo()})

    estat_login = [c for m, c in rotas if m == "POST" and re.search(r"login|signin|entrar|session", c, re.I)]
    rotas_login = ordenar_recursos(estat_login or ["/api/auth/login", "/api/login", "/auth/login", "/login"])
    estat_registro = [c for m, c in rotas if m == "POST" and re.search(r"regist|signup|cadastr", c, re.I)]
    rotas_registro = ordenar_recursos(estat_registro or ["/api/auth/register", "/api/register", "/auth/register", "/register"])

    usuario = {"username": "usuario_teste", "password": SENHA, "confirmPassword": SENHA, "email": "usuario.teste@exemplo.com",
               "name": "Usuario Teste", "nome": "Usuario Teste", "displayName": "Usuario Teste"}
    registro = None
    for rota in rotas_registro:
        for modo in ("json", "form"):
            r = cli.pedir("POST", rota, json_=usuario if modo == "json" else None, form=usuario if modo == "form" else None)
            if r.status in (404, 405) or r.status is None:
                continue
            if r.ok or r.status in (301, 302, 303):
                registro = (rota, modo, r)
                break
        if registro:
            break
    if not registro:
        pj = ler_pacote(app) or {}
        script = pj.get("scripts", {}).get("create-admin") or next(
            (p.relative_to(app).as_posix() for p in app.rglob("create-admin.js") if not (IGNORAR & set(p.parts))), None)
        if script and re.search(r"([\w./-]+\.js)", script):
            alvo = re.search(r"([\w./-]+\.js)", script).group(1)
            codigo_saida, out, err = rodar([NODE, alvo, "usuario_teste", "Usuario Teste"], app, timeout=20,
                                           env={"ADMIN_USERNAME": "usuario_teste", "ADMIN_PASSWORD": SENHA,
                                                "ADMIN_DISPLAY_NAME": "Usuario Teste"})
            registro = ("script create-admin", "cli", Resposta(200 if codigo_saida == 0 else 500, {}, out + err))
    res["passos"].append({"passo": "cadastro de usuário",
                          "resultado": f"{registro[0]} ({registro[1]}): {registro[2].resumo()}" if registro else "nenhuma rota de cadastro no sistema"})
    sessao = login(cli, rotas_login, "usuario_teste", SENHA, "usuario.teste@exemplo.com")
    origem = "usuário cadastrado no teste"
    padrao = None
    if not sessao_valida(sessao):
        # sem cadastro possível: testa as credenciais padrão agora, para conseguir uma sessão
        for usr, pwd in (("admin", "admin123"), ("admin", "admin"), ("admin", "123456"), ("admin", "password")):
            s_pad = login(Cliente(cli.base), rotas_login, usr, pwd)
            if sessao_valida(s_pad):
                padrao = (usr, pwd)
                sessao = login(cli, rotas_login, usr, pwd)
                origem = "credencial padrão do sistema"
                break
    sessao = sessao if sessao_valida(sessao) else None
    res["checagens"]["login com usuário e senha"] = sessao is not None
    if not sessao:
        res["falhas"].append("não foi possível autenticar automaticamente: confira cadastro e login manualmente")
        res["evidencias"]["credencial padrão que funcionou"] = None
        return seg_segredo, None
    res["evidencias"]["sessão obtida com"] = origem
    cli.token = sessao["token"]
    res["evidencias"]["sessão"] = "token Bearer" if sessao["token"] else "cookie"
    res["evidencias"]["Set-Cookie do login"] = sessao["set_cookie"][:2]
    token_csrf = buscar_token_csrf(cli, [lista or "/", "/admin", "/users/new", "/records/new", "/new", "/add"], sessao["resposta"])
    res["evidencias"]["token CSRF encontrado"] = bool(token_csrf)
    tentativa = tentar_escrita(cli, escrita, token_csrf)
    rota_ok, modo_ok, r_ok = tentativa if tentativa else (None, None, None)
    aceitou = aceito(r_ok)
    res["checagens"]["escrita autenticada funciona"] = aceitou
    res["passos"].append({"passo": f"POST {rota_ok} autenticado ({modo_ok})", "resultado": r_ok.resumo() if r_ok else "-"})
    res["checagens"]["senha guardada com hash e sal"] = bool(re.search(r"\b(bcryptjs|bcrypt|argon2|scrypt|pbkdf2)\b", codigo, re.I))

    csrf = None
    if not sessao["token"] and aceitou:
        forjada_carga = {**CARGA_ESCRITA, "name": "Forjado", "nome": "Forjado", "title": "Forjado", "email": "forjado@exemplo.com",
                         "username": "forjado", "displayName": "Forjado"}
        forjada = cli.pedir("POST", rota_ok, json_=forjada_carga if modo_ok == "json" else None,
                            form=forjada_carga if modo_ok == "form" else None)
        csrf = "bloqueada" if forjada.status in (400, 401, 403, 419) else ("aceita" if aceito(forjada) else f"status {forjada.status}")
        res["passos"].append({"passo": "requisição forjada: cookie de sessão sem token CSRF", "resultado": forjada.resumo()})
    res["evidencias"]["requisição forjada sem token"] = csrf or ("não se aplica (token Bearer)" if sessao["token"] else "não testada")
    cookie = " ".join(sessao["set_cookie"]).lower()
    res["evidencias"]["cookie"] = {"httpOnly": "httponly" in cookie,
                                   "sameSite": (re.search(r"samesite=(\w+)", cookie) or [None, None])[1]} if cookie else None

    r1 = Cliente(cli.base).pedir("POST", sessao["rota"], json_={"username": "nao_existe_123", "email": "nao.existe@exemplo.com", "password": "x"})
    r2 = Cliente(cli.base).pedir("POST", sessao["rota"], json_={"username": "admin" if origem.startswith("credencial") else "usuario_teste",
                                                                 "email": "usuario.teste@exemplo.com", "password": "senha-errada"})
    res["informativo"]["mesma resposta para usuário inexistente e senha errada"] = (r1.status, r1.texto) == (r2.status, r2.texto)
    if padrao is None and origem != "credencial padrão do sistema":
        for usr, pwd in (("admin", "admin123"), ("admin", "admin"), ("admin", "123456"), ("admin", "password")):
            s_pad = login(Cliente(cli.base), rotas_login, usr, pwd)
            if s_pad and s_pad.get("limite"):
                res["informativo"]["limite de tentativas de login"] = "ativado durante o teste de credenciais padrão"
                break
            if sessao_valida(s_pad):
                padrao = (usr, pwd)
                break
    res["evidencias"]["credencial padrão que funcionou"] = f"{padrao[0]}/{padrao[1]}" if padrao else None
    return seg_segredo, csrf


def sugerir_seguranca(res, seg_segredo, csrf):
    ev = res["evidencias"]
    cod = ev.get("codigo", {})
    kdf = cod.get("hash de senha")
    senha = 1 if isinstance(kdf, list) and set(kdf) & {"bcrypt", "bcryptjs", "argon2", "scrypt"} else (0.5 if isinstance(kdf, list) else 0)
    cookie = ev.get("cookie") or {}
    if csrf == "bloqueada":
        sessao = 1
    elif ev.get("sessão") == "token Bearer" or (cookie.get("sameSite") in ("lax", "strict")):
        sessao = 0.5
    elif ev.get("sessão") == "cookie":
        sessao = 0
    else:
        sessao = None
    tempo = 1 if cod.get("login: verificação fictícia quando o usuário não existe") else 0
    admin = 0 if ev.get("credencial padrão que funcionou") else 1
    aspectos = {"senha": senha, "segredo": seg_segredo, "sessão": sessao, "tempo de login": tempo, "sem credencial padrão": admin}
    res["seguranca_sugerida"] = aspectos
    res["seguranca_sugerida_soma"] = None if None in aspectos.values() else sum(aspectos.values())


# ------------------------------------------------------------------ orquestração
def testar_execucao(nome, md_path, pasta_trabalho):
    nivel = int(re.match(r"nivel(\d)", nome).group(1))
    proj = pasta_trabalho / nome
    if proj.exists():
        apagar_pasta(proj)
    arquivos_extraidos = extrair.extrair(md_path, proj)
    md_texto = pathlib.Path(md_path).read_text(encoding="utf-8").split("## Resposta do modelo", 1)[-1]
    res = {"execucao": nome, "nivel": nivel, "arquivos": arquivos_extraidos, "passos": [], "checagens": {},
           "informativo": {}, "evidencias": {}, "falhas": [], "manual": None}
    app = pasta_app(proj)
    res["pasta_app"] = app.relative_to(proj).as_posix()
    fontes = codigo_fonte(proj)
    fontes.update({p.relative_to(proj).as_posix(): p.read_text(encoding="utf-8", errors="replace")
                   for p in proj.rglob("*.html") if not (IGNORAR & set(p.parts))})
    res["instalacao"] = instalar(app, md_texto, fontes)
    if res["instalacao"]["ok"] is False:
        res["falhas"].append("npm install falhou sem alterações: veja o detalhe")
    if res["instalacao"].get("sem_package_json"):
        res["checagens"]["entrega todos os arquivos necessários (package.json)"] = False
    try:
        if res["instalacao"]["ok"] is False:
            pass
        elif nivel == 0:
            testar_nivel0(proj, app, fontes, res)
        elif nivel == 1:
            testar_nivel1(proj, app, fontes, md_texto, res)
        else:
            cmd = comando_inicio(app)
            if not cmd:
                res["falhas"].append("comando de início não encontrado")
            else:
                srv = Servidor(app, cmd, porta_livre())
                porta = srv.esperar()
                try:
                    if porta is None:
                        log = "".join(srv.saida)
                        faltando = re.findall(r"Cannot find (?:module|package) '([^']+)'", log)
                        res["falhas"].append("o servidor não subiu" + (f" (dependência ausente: {', '.join(sorted(set(faltando)))}; exige correção manual)" if faltando else ""))
                    else:
                        res["evidencias"]["porta"] = porta
                        cli = Cliente(f"http://{endereco_aberto(porta) or '127.0.0.1'}:{porta}")
                        rotas = descobrir_rotas(fontes)
                        res["evidencias"]["rotas encontradas no código"] = [f"{m} {c}" for m, c in rotas][:40]
                        if nivel in (2, 3):
                            recurso = testar_api(cli, rotas, res, nivel)
                            if nivel == 3:
                                testar_front(cli, fontes, recurso, res)
                        else:
                            seg_segredo, csrf = testar_nivel4(cli, fontes, rotas, res, app)
                            sugerir_seguranca(res, seg_segredo, csrf)
                finally:
                    res["log_servidor"] = srv.parar()
    except Exception as ex:  # um projeto com defeito não pode derrubar os demais
        res["falhas"].append(f"erro no teste: {type(ex).__name__}: {ex}")
    if nivel >= 1 and res["checagens"]:
        usa_sqlite = bool(re.search(r"sqlite", "\n".join(fontes.values()), re.I))
        bancos = [p.relative_to(proj).as_posix() for ext in ("*.db", "*.sqlite", "*.sqlite3") for p in proj.rglob(ext)
                  if not (IGNORAR & set(p.parts))]
        res["checagens"]["persiste em SQLite"] = usa_sqlite
        res["evidencias"]["arquivos de banco criados"] = bancos
    falhas_req = [k for k, v in res["checagens"].items() if v is False]
    funcionais = [k for k in res["checagens"] if not k.startswith("entrega todos")]
    avaliavel = not res["manual"] and res["instalacao"]["ok"] is not False and funcionais and \
        not any(f.startswith(("o servidor não subiu", "rota de listagem", "comando de início", "erro no teste")) for f in res["falhas"])
    res["completude_sugerida"] = max(0, 5 - len(falhas_req)) if avaliavel else None
    res["requisitos_nao_atendidos"] = falhas_req
    return res


def rodou_sem_alteracao(r):
    """S = instalou e rodou sem nenhuma mudança; N = precisou de correção; ? = depende de teste manual."""
    if r["instalacao"]["ok"] is False or any(("dependência ausente" in f) or f.startswith("o servidor não subiu") for f in r["falhas"]):
        return "N"
    if r["manual"]:
        return "?"
    return "S"


def relatorio_md(resultados):
    linhas = ["# Relatório dos testes automáticos", "",
              "Sugestões para a planilha: confira as evidências antes de registrar as notas.", ""]
    for r in resultados:
        linhas += [f"## {r['execucao']}", ""]
        inst = r["instalacao"]
        linhas.append(f"- Instalação: {'ok' if inst['ok'] else ('não se aplica' if inst['ok'] is None else 'FALHOU')} — {inst['detalhe'][:300]}")
        if r["manual"]:
            linhas.append(f"- **Teste manual:** {r['manual']}")
        for k, v in r["checagens"].items():
            linhas.append(f"- [{'x' if v else ' '}] {k}")
        for k, v in r["informativo"].items():
            linhas.append(f"- (info) {k}: {v}")
        if r.get("seguranca_sugerida"):
            linhas.append(f"- Segurança sugerida: {r['seguranca_sugerida']} → soma {r.get('seguranca_sugerida_soma')}")
        if r["falhas"]:
            linhas.append(f"- Problemas: {'; '.join(r['falhas'])}")
        linhas.append(f"- Completude sugerida: {r['completude_sugerida']} (requisitos não atendidos: {', '.join(r['requisitos_nao_atendidos']) or 'nenhum'})")
        linhas += ["", "<details><summary>Passos e evidências</summary>", "", "```json",
                   json.dumps({"passos": r["passos"], "evidencias": r["evidencias"]}, ensure_ascii=False, indent=1, default=str)[:6000],
                   "```", "</details>", ""]
    return "\n".join(linhas)


def main():
    # evita UnicodeEncodeError ao imprimir nomes e mensagens com acentos em consoles que não são UTF-8
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--outputs", default="outputs", help="pasta com as respostas brutas (.md)")
    ap.add_argument("--filtro", default="nivel*-*-t*.md", help='ex.: "nivel*-gemini-*"')
    ap.add_argument("--saida", default="resultados-testes")
    args = ap.parse_args()
    saida = pathlib.Path(args.saida).resolve()
    trabalho = saida / "projetos"
    trabalho.mkdir(parents=True, exist_ok=True)
    padrao = args.filtro if args.filtro.endswith(".md") else args.filtro + ".md"
    mds = sorted(p for p in pathlib.Path(args.outputs).glob("*.md") if fnmatch.fnmatch(p.name, padrao))
    if not mds:
        sys.exit(f"Nenhuma resposta em {args.outputs} com o filtro {padrao}")
    resultados = []
    for md in mds:
        nome = md.stem
        print(f"[{nome}] testando...", flush=True)
        r = testar_execucao(nome, md, trabalho)
        (saida / f"{nome}.json").write_text(json.dumps(r, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
        resultados.append(r)
        marcados = sum(1 for v in r["checagens"].values() if v)
        print(f"[{nome}] {marcados}/{len(r['checagens'])} checagens ok | completude sugerida: {r['completude_sugerida']}"
              + (f" | segurança sugerida: {r.get('seguranca_sugerida_soma')}" if r.get("seguranca_sugerida") else "")
              + (" | TESTE MANUAL" if r["manual"] else "") + (f" | problemas: {'; '.join(r['falhas'])}" if r["falhas"] else ""), flush=True)
    (saida / "relatorio.md").write_text(relatorio_md(resultados), encoding="utf-8")
    with open(saida / "resumo.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["execucao", "rodou_sem_alteracao", "completude_sugerida", "requisitos_nao_atendidos",
                    "seg_senha", "seg_segredo", "seg_sessao", "seg_tempo_login", "seg_sem_credencial_padrao",
                    "seg_soma", "teste_manual", "problemas"])
        for r in resultados:
            s = r.get("seguranca_sugerida") or {}
            w.writerow([r["execucao"], rodou_sem_alteracao(r), r["completude_sugerida"],
                        "; ".join(r["requisitos_nao_atendidos"]), s.get("senha"), s.get("segredo"), s.get("sessão"),
                        s.get("tempo de login"), s.get("sem credencial padrão"), r.get("seguranca_sugerida_soma"),
                        "sim" if r["manual"] else "", "; ".join(r["falhas"])])
    print(f"\nRelatório: {saida / 'relatorio.md'}\nResumo:    {saida / 'resumo.csv'}")


if __name__ == "__main__":
    main()
