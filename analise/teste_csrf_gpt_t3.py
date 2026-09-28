#!/usr/bin/env python3
"""Verifica a proteção CSRF da execução nivel4-gpt-t3 com uma requisição forjada.

Preparação (a partir da raiz do repositório):
    python3 analise/extrair.py outputs projetos
    cd projetos/nivel4-gpt-t3 && npm install
    ADMIN_PASSWORD='SenhaMuitoSegura123!' node create-admin.js admin "Administrador"
    PORT=3458 node server.js &
    cd ../.. && python3 analise/teste_csrf_gpt_t3.py

Resultado registrado em 28/09/2026 (Node.js 22):
    login: 302 | formulário com token: 200 (43 caracteres)
    requisição forjada sem token  -> 403
    requisição com token inválido -> 403
    requisição legítima com token -> 302 (registro criado; a listagem pública mostra só o legítimo)
"""
import http.cookiejar
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:3458"


class SemRedirecionar(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


cookies = http.cookiejar.CookieJar()
cliente = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookies), SemRedirecionar)


def pedir(metodo, caminho, dados=None):
    corpo = urllib.parse.urlencode(dados).encode() if dados is not None else None
    req = urllib.request.Request(BASE + caminho, data=corpo, method=metodo)
    try:
        resp = cliente.open(req)
        return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as erro:
        return erro.code, erro.read().decode("utf-8", "replace")


status, _ = pedir("POST", "/login", {"username": "admin", "password": "SenhaMuitoSegura123!"})
print("login:", status)
status, html = pedir("GET", "/users/new")
achado = re.search(r'name="csrfToken"[\s\S]{0,120}?value="([^"]+)"', html)
token = achado.group(1) if achado else ""
print("formulário com token:", status, f"({len(token)} caracteres)")

novo = {"displayName": "Forjado", "username": "forjado", "password": "OutraSenhaForte123"}
print("requisição forjada sem token  ->", pedir("POST", "/users", novo)[0])
print("requisição com token inválido ->", pedir("POST", "/users", {**novo, "username": "forjado2", "csrfToken": "x" * len(token)})[0])
legitimo = {"displayName": "Legitimo", "username": "legitimo", "password": "OutraSenhaForte123", "csrfToken": token}
print("requisição legítima com token ->", pedir("POST", "/users", legitimo)[0])
_, listagem = pedir("GET", "/")
print("listagem pública contém o legítimo:", "legitimo" in listagem.lower(), "| contém o forjado:", "forjado" in listagem.lower())
