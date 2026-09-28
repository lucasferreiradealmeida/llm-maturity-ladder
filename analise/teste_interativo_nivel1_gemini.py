#!/usr/bin/env python3
"""Teste roteirizado dos menus interativos do Gemini no nível 1 (tentativas 2 e 3).

Os dois programas são menus em readline, que o testar.py marca para teste manual. Este script faz
o teste manual num terminal simulado (pseudo-TTY): responde a cada pergunta só depois de ela
aparecer, cobre os requisitos do prompt do nível 1 e grava a transcrição da sessão.

Uso (Linux ou macOS; requer pexpect: pip install pexpect):
    python3 analise/testar.py --outputs outputs --filtro "nivel1-gemini-t[23]" --saida resultados-testes
    python3 analise/teste_interativo_nivel1_gemini.py resultados-testes/projetos/nivel1-gemini-t2 t2
    python3 analise/teste_interativo_nivel1_gemini.py resultados-testes/projetos/nivel1-gemini-t3 t3
"""
import pathlib
import re
import sys

import pexpect

MENU = "Escolha uma opção:"
EMAIL = "ana.teste@exemplo.com"


def main():
    app = pathlib.Path(sys.argv[1]).resolve()
    perfil = sys.argv[2]
    if perfil not in ("t2", "t3"):
        sys.exit("perfil deve ser t2 ou t3")
    destino = sys.argv[3] if len(sys.argv) > 3 else f"transcricao-nivel1-gemini-{perfil}.txt"
    transcricao = open(destino, "w", encoding="utf-8")
    for banco in app.glob("*.sqlite"):
        banco.unlink()  # começa com o banco vazio
    resultados = {}
    estado = {"menu_lido": False}  # True quando o prompt do menu já foi consumido

    def sessao():
        estado["menu_lido"] = False
        p = pexpect.spawn("node", ["index.js"], cwd=str(app), encoding="utf-8", timeout=15)
        p.logfile_read = transcricao
        return p

    def opcao(p, n):
        if not estado["menu_lido"]:
            p.expect(MENU)
        estado["menu_lido"] = False
        p.sendline(n)

    def responder(p, pares):
        for pergunta, resposta in pares:
            p.expect(pergunta)
            p.sendline(resposta)

    def listar(p):
        opcao(p, "2")
        p.expect("Lista de Usuários")
        p.expect(MENU)
        estado["menu_lido"] = True
        return p.before

    def atualizar(p, ident, nome):
        """t2 pede os campos com o valor atual entre colchetes (vazio mantém); t3 pede todos de novo."""
        opcao(p, "3")
        responder(p, [("ID do usuário", ident)])
        if perfil == "t2":
            if not ident.isdigit():
                return
            responder(p, [(r"Nome \[", nome), (r"E-mail \[", ""), (r"Data de Nascimento \[", "")])
        else:
            responder(p, [("Novo Nome:", nome), ("Novo E-mail:", EMAIL), ("Nova Data de Nascimento", "1990-05-10")])

    p = sessao()
    opcao(p, "1")
    responder(p, [("Nome:", "Ana Teste"), ("E-mail:", EMAIL), ("Data de Nascimento", "1990-05-10")])
    resultados["cadastra usuário"] = p.expect(["cadastrado com sucesso", "Erro"]) == 0
    resultados["lista usuários"] = EMAIL in listar(p)
    opcao(p, "1")
    responder(p, [("Nome:", "Ana Repetida"), ("E-mail:", EMAIL), ("Data de Nascimento", "1991-01-01")])
    resultados["bloqueia e-mail duplicado"] = p.expect(["já está cadastrado", "cadastrado com sucesso"]) == 0
    opcao(p, "1")
    responder(p, [("Nome:", "Bruno Teste"), ("E-mail:", "email-invalido")])
    resultados["valida formato do e-mail"] = p.expect(["e-mail inválido", "Data de Nascimento"]) == 0
    atualizar(p, "abc", "Ana Atualizada")
    resultados["trata ID inválido com mensagem amigável"] = p.expect(["ID inválido", "não encontrado", MENU]) in (0, 1)
    atualizar(p, "1", "Ana Atualizada")
    atualizou = p.expect(["atualizado com sucesso", "Erro"]) == 0
    resultados["atualiza usuário"] = atualizou and "Ana Atualizada" in listar(p)
    opcao(p, "5")
    p.expect(pexpect.EOF)

    p = sessao()  # nova execução: os dados precisam continuar no SQLite
    resultados["persiste entre execuções"] = "Ana Atualizada" in listar(p)
    opcao(p, "4")
    responder(p, [("ID do usuário", "1")])
    removeu = p.expect(["removido com sucesso", "Erro"]) == 0
    resultados["remove usuário"] = removeu and "Nenhum usuário cadastrado" in listar(p)
    opcao(p, "5")
    p.expect(pexpect.EOF)
    transcricao.close()
    # remove os códigos de controle do terminal (cores e posicionamento do cursor) da transcrição
    texto = pathlib.Path(destino).read_text(encoding="utf-8")
    texto = re.sub(r"\x1b\[[0-9;?]*[A-Za-z]", "", texto).replace("\r", "")
    pathlib.Path(destino).write_text(texto, encoding="utf-8")

    for k, v in resultados.items():
        print(f"[{'x' if v else ' '}] {k}")
    print(f"transcrição: {destino}")
    sys.exit(0 if all(resultados.values()) else 1)


if __name__ == "__main__":
    main()
