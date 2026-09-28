#!/usr/bin/env python3
"""Extrai os arquivos de código de cada resposta bruta (outputs/*.md) para uma pasta de projeto.

Uso:
    python3 analise/extrair.py outputs/ projetos/

Para cada bloco de código cercado (```), o nome do arquivo é procurado, nesta ordem:
  1. nas até três linhas não vazias anteriores ao bloco, como caminho entre crases, em negrito
     ou no próprio título (ex.: ### `src/db.js`, **src/db.js**, "## 2. Arquivo **package.json**",
     "Script de criação (`db/schema.sql`)"); um nome incompatível com a linguagem do bloco,
     citado na prosa entre o título e o bloco, é pulado e a busca continua nas linhas acima;
  2. na primeira linha do bloco, como comentário com um caminho
     (ex.: // package.json, # .env.example, <!-- public/index.html -->, -- db/schema.sql),
     caso em que essa linha é removida do arquivo gerado.
O bloco só é aceito se a linguagem declarada na cerca for compatível com a extensão do arquivo
(um bloco ```bash logo após "rode `node server.js`" não vira server.js).
Blocos sem nome de arquivo (exemplos de uso, comandos de terminal) são ignorados.
Se o mesmo arquivo aparece mais de uma vez, vale a última versão.
"""
import json
import pathlib
import re
import sys

EXT = r"(?:js|mjs|cjs|json|sql|html|css|env|example|ejs|sh)"
PATH = r"(?:\.?[\w\-]+/)*\.?[\w\-]+(?:\.[\w\-]+)*\." + EXT
RE_BACKTICK = re.compile(r"`(" + PATH + r")`")
RE_NEGRITO = re.compile(r"\*\*(" + PATH + r")\*\*")
RE_TITULO = re.compile(r"^\s*#{1,6}\s.*?(?<![\w/.])(" + PATH + r")(?![\w/])")
RE_COMMENT = re.compile(r"^\s*(?://|#|--|<!--|/\*)\s*(?:arquivo:|file:)?\s*(" + PATH + r")\b", re.I)
RE_FENCE = re.compile(r"^(\s*)(```+|~~~+)\s*([\w+\-]*)\s*$")

COMPATIVEIS = {
    "js": {"", "js", "javascript", "node", "jsx"},
    "mjs": {"", "js", "javascript", "node"},
    "cjs": {"", "js", "javascript", "node"},
    "json": {"", "json", "jsonc"},
    "sql": {"", "sql", "sqlite"},
    "html": {"", "html", "htm", "xml"},
    "ejs": {"", "html", "ejs"},
    "css": {"", "css"},
    "env": {"", "env", "dotenv", "ini", "bash", "sh", "text", "plaintext"},
    "example": {"", "env", "dotenv", "ini", "bash", "sh", "text", "plaintext"},
    "sh": {"", "bash", "sh", "shell"},
}


def blocos(texto):
    """Percorre os blocos cercados. Dentro de um bloco ```markdown, cercas internas
    com linguagem abrem um nível de aninhamento (READMEs gerados costumam conter exemplos)."""
    linhas = texto.split("\n")
    i = 0
    while i < len(linhas):
        m = RE_FENCE.match(linhas[i])
        if not m:
            i += 1
            continue
        cerca = m.group(2)
        lang = m.group(3).lower()
        j = i + 1
        corpo = []
        profundidade = 0
        while j < len(linhas):
            interna = RE_FENCE.match(linhas[j])
            if interna and interna.group(2).startswith(cerca[:3]):
                if lang in ("markdown", "md") and interna.group(3):
                    profundidade += 1
                elif profundidade > 0:
                    profundidade -= 1
                else:
                    break
            corpo.append(linhas[j])
            j += 1
        anteriores = [l for l in linhas[max(0, i - 6):i] if l.strip()][-3:]
        yield lang, corpo, anteriores
        i = j + 1


NAO_SAO_ARQUIVOS = {"node.js", "express.js", "next.js", "vue.js", "react.js", "nuxt.js"}


def eh_arvore(corpo):
    """Blocos com a árvore de diretórios do projeto não são arquivos."""
    return any(("├" in l or "└" in l or "│" in l) for l in corpo)


def nome_arquivo(corpo, anteriores, lang=""):
    for linha in reversed(anteriores):
        achados = []
        for regex in (RE_BACKTICK, RE_NEGRITO, RE_TITULO):
            achados += [a for a in regex.findall(linha) if a.lower() not in NAO_SAO_ARQUIVOS]
        distintos = list(dict.fromkeys(achados))
        if len(distintos) == 1:
            if compativel(distintos[0], lang):
                return distintos[0], corpo
            # prosa entre o título e o bloco citando outro arquivo (ex.: "ao lado do `server.js`"
            # antes de um bloco html): o nome não serve para este bloco, segue procurando acima
            continue
        # linha de prosa citando vários arquivos não identifica o bloco
    if corpo:
        m = RE_COMMENT.match(corpo[0])
        if m:
            return m.group(1), corpo[1:]
    return None, corpo


def json_valido(texto):
    try:
        json.loads(texto)
        return True
    except ValueError:
        return False


def compativel(nome, lang):
    ext = nome.rsplit(".", 1)[-1].lower()
    return lang in COMPATIVEIS.get(ext, {""})


def extrair(md_path, destino):
    texto = pathlib.Path(md_path).read_text(encoding="utf-8")
    if "## Resposta do modelo" in texto:
        texto = texto.split("## Resposta do modelo", 1)[1]
    arquivos = {}
    for lang, corpo, anteriores in blocos(texto):
        if eh_arvore(corpo):
            continue
        nome, conteudo = nome_arquivo(corpo, anteriores, lang)
        if not nome or nome.startswith("/") or ".." in nome or not compativel(nome, lang):
            continue
        if nome.startswith("./"):
            nome = nome[2:]
        novo = "\n".join(conteudo) + "\n"
        if nome.endswith(".json") and nome in arquivos and json_valido(arquivos[nome]) and not json_valido(novo):
            continue  # trecho "adicione ao package.json" não substitui o arquivo completo
        arquivos[nome] = novo
    for nome, conteudo in arquivos.items():
        alvo = pathlib.Path(destino) / nome
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_text(conteudo, encoding="utf-8")
    return sorted(arquivos)


def main():
    origem, destino = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    indice = {}
    for md in sorted(origem.glob("nivel*-*-t*.md")):
        indice[md.stem] = extrair(md, destino / md.stem)
    destino.mkdir(parents=True, exist_ok=True)
    (destino / "indice.json").write_text(json.dumps(indice, indent=1, ensure_ascii=False), encoding="utf-8")
    for k, v in indice.items():
        print(f"{k}: {len(v)} arquivos -> {', '.join(v)}")


if __name__ == "__main__":
    main()
