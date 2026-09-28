# Relatório dos testes automáticos

Sugestões para a planilha: confira as evidências antes de registrar as notas.

## nivel0-claude-t1

- Instalação: ok — npm install ok
- [x] registra o nome no CSV
- [x] grava a data de cadastro
- [x] acrescenta sem sobrescrever (2 execuções = 2 linhas)
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "rodar register.js \"Ana Teste\"",
   "codigo": 0,
   "saida": "Usuario registrado com sucesso!\n  Nome: Ana Teste\n  Data: 2026-09-28T18:55:40.434Z\n  Arquivo: /home/claude/resultados-testes/projetos/nivel0-claude-t1/usuarios.csv"
  },
  {
   "passo": "rodar register.js \"Bruno Teste\"",
   "codigo": 0,
   "saida": "Usuario registrado com sucesso!\n  Nome: Bruno Teste\n  Data: 2026-09-28T18:55:40.487Z\n  Arquivo: /home/claude/resultados-testes/projetos/nivel0-claude-t1/usuarios.csv"
  }
 ],
 "evidencias": {
  "csv": {
   "arquivo": "usuarios.csv",
   "linhas": [
    "nome,data_cadastro",
    "Ana Teste,2026-09-28T18:55:40.434Z",
    "Bruno Teste,2026-09-28T18:55:40.487Z"
   ]
  }
 }
}
```
</details>

## nivel0-claude-t2

- Instalação: ok — npm install ok
- [x] registra o nome no CSV
- [x] grava a data de cadastro
- [x] acrescenta sem sobrescrever (2 execuções = 2 linhas)
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "rodar registrar_usuario.js \"Ana Teste\"",
   "codigo": 0,
   "saida": "✔ Usuário registrado com sucesso!\n  Nome: Ana Teste\n  Data: 2026-09-28T18:55:40.831Z\n  Arquivo: /home/claude/resultados-testes/projetos/nivel0-claude-t2/usuarios.csv"
  },
  {
   "passo": "rodar registrar_usuario.js \"Bruno Teste\"",
   "codigo": 0,
   "saida": "✔ Usuário registrado com sucesso!\n  Nome: Bruno Teste\n  Data: 2026-09-28T18:55:40.869Z\n  Arquivo: /home/claude/resultados-testes/projetos/nivel0-claude-t2/usuarios.csv"
  }
 ],
 "evidencias": {
  "csv": {
   "arquivo": "usuarios.csv",
   "linhas": [
    "nome,data_cadastro",
    "Ana Teste,2026-09-28T18:55:40.831Z",
    "Bruno Teste,2026-09-28T18:55:40.869Z"
   ]
  }
 }
}
```
</details>

## nivel0-claude-t3

- Instalação: ok — npm install ok
- [x] registra o nome no CSV
- [x] grava a data de cadastro
- [x] acrescenta sem sobrescrever (2 execuções = 2 linhas)
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "rodar registrarUsuario.js \"Ana Teste\"",
   "codigo": 0,
   "saida": "Usuario registrado com sucesso!\n  Nome: Ana Teste\n  Data de cadastro: 2026-09-28T18:55:41.207Z\n  Arquivo: /home/claude/resultados-testes/projetos/nivel0-claude-t3/usuarios.csv"
  },
  {
   "passo": "rodar registrarUsuario.js \"Bruno Teste\"",
   "codigo": 0,
   "saida": "Usuario registrado com sucesso!\n  Nome: Bruno Teste\n  Data de cadastro: 2026-09-28T18:55:41.248Z\n  Arquivo: /home/claude/resultados-testes/projetos/nivel0-claude-t3/usuarios.csv"
  }
 ],
 "evidencias": {
  "csv": {
   "arquivo": "usuarios.csv",
   "linhas": [
    "nome,data_cadastro",
    "Ana Teste,2026-09-28T18:55:41.207Z",
    "Bruno Teste,2026-09-28T18:55:41.248Z"
   ]
  }
 }
}
```
</details>

## nivel0-gemini-t1

- Instalação: não se aplica — sem package.json e sem dependências externas (nada a instalar)
- [x] registra o nome no CSV
- [x] grava a data de cadastro
- [x] acrescenta sem sobrescrever (2 execuções = 2 linhas)
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "rodar index.js \"Ana Teste\"",
   "codigo": 0,
   "saida": "Arquivo usuarios.csv criado com sucesso.\nSucesso: Usuário \"Ana Teste\" registrado em usuarios.csv."
  },
  {
   "passo": "rodar index.js \"Bruno Teste\"",
   "codigo": 0,
   "saida": "Sucesso: Usuário \"Bruno Teste\" registrado em usuarios.csv."
  }
 ],
 "evidencias": {
  "csv": {
   "arquivo": "usuarios.csv",
   "linhas": [
    "nome,data_de_cadastro",
    "\"Ana Teste\",2026-09-28T18:55:41.287Z",
    "\"Bruno Teste\",2026-09-28T18:55:41.327Z"
   ]
  }
 }
}
```
</details>

## nivel0-gemini-t2

- Instalação: não se aplica — sem package.json e sem dependências externas (nada a instalar)
- [x] registra o nome no CSV
- [x] grava a data de cadastro
- [x] acrescenta sem sobrescrever (2 execuções = 2 linhas)
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "rodar index.js \"Ana Teste\"",
   "codigo": 0,
   "saida": "Arquivo CSV criado com cabeçalho.\nSucesso! Usuário \"Ana Teste\" registrado em /home/claude/resultados-testes/projetos/nivel0-gemini-t2/usuarios.csv."
  },
  {
   "passo": "rodar index.js \"Bruno Teste\"",
   "codigo": 0,
   "saida": "Sucesso! Usuário \"Bruno Teste\" registrado em /home/claude/resultados-testes/projetos/nivel0-gemini-t2/usuarios.csv."
  }
 ],
 "evidencias": {
  "csv": {
   "arquivo": "usuarios.csv",
   "linhas": [
    "\"Nome\",\"Data de Cadastro\"",
    "\"Ana Teste\",\"2026-09-28T18:55:41.369Z\"",
    "\"Bruno Teste\",\"2026-09-28T18:55:41.411Z\""
   ]
  }
 }
}
```
</details>

## nivel0-gemini-t3

- Instalação: não se aplica — sem package.json e sem dependências externas (nada a instalar)
- [x] registra o nome no CSV
- [x] grava a data de cadastro
- [x] acrescenta sem sobrescrever (2 execuções = 2 linhas)
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "rodar index.js \"Ana Teste\"",
   "codigo": 0,
   "saida": "Arquivo usuarios.csv criado com sucesso.\n✅ Sucesso: Usuário \"Ana Teste\" registrado em 2026-09-28T18:55:41.449Z."
  },
  {
   "passo": "rodar index.js \"Bruno Teste\"",
   "codigo": 0,
   "saida": "✅ Sucesso: Usuário \"Bruno Teste\" registrado em 2026-09-28T18:55:41.490Z."
  }
 ],
 "evidencias": {
  "csv": {
   "arquivo": "usuarios.csv",
   "linhas": [
    "\"Nome\",\"Data de Cadastro\"",
    "\"Ana Teste\",\"2026-09-28T18:55:41.449Z\"",
    "\"Bruno Teste\",\"2026-09-28T18:55:41.490Z\""
   ]
  }
 }
}
```
</details>

## nivel0-gpt-t1

- Instalação: ok — npm install ok
- [x] registra o nome no CSV
- [x] grava a data de cadastro
- [x] acrescenta sem sobrescrever (2 execuções = 2 linhas)
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "rodar cadastro.js \"Ana Teste\"",
   "codigo": 0,
   "saida": "Usuário cadastrado com sucesso.\nNome: Ana Teste\nData de cadastro: 2026-09-28T18:55:41.920Z\nArquivo: /home/claude/resultados-testes/projetos/nivel0-gpt-t1/usuarios.csv"
  },
  {
   "passo": "rodar cadastro.js \"Bruno Teste\"",
   "codigo": 0,
   "saida": "Usuário cadastrado com sucesso.\nNome: Bruno Teste\nData de cadastro: 2026-09-28T18:55:41.967Z\nArquivo: /home/claude/resultados-testes/projetos/nivel0-gpt-t1/usuarios.csv"
  }
 ],
 "evidencias": {
  "csv": {
   "arquivo": "usuarios.csv",
   "linhas": [
    "nome,data_cadastro",
    "\"Ana Teste\",\"2026-09-28T18:55:41.920Z\"",
    "\"Bruno Teste\",\"2026-09-28T18:55:41.967Z\""
   ]
  }
 }
}
```
</details>

## nivel0-gpt-t2

- Instalação: ok — npm install ok
- [x] registra o nome no CSV
- [x] grava a data de cadastro
- [x] acrescenta sem sobrescrever (2 execuções = 2 linhas)
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "rodar cadastrar.js \"Ana Teste\"",
   "codigo": 0,
   "saida": "Usuário cadastrado com sucesso.\nNome: Ana Teste\nData de cadastro: 2026-09-28T18:55:42.327Z\nArquivo: /home/claude/resultados-testes/projetos/nivel0-gpt-t2/cadastros.csv"
  },
  {
   "passo": "rodar cadastrar.js \"Bruno Teste\"",
   "codigo": 0,
   "saida": "Usuário cadastrado com sucesso.\nNome: Bruno Teste\nData de cadastro: 2026-09-28T18:55:42.373Z\nArquivo: /home/claude/resultados-testes/projetos/nivel0-gpt-t2/cadastros.csv"
  }
 ],
 "evidencias": {
  "csv": {
   "arquivo": "cadastros.csv",
   "linhas": [
    "\"nome\",\"data_de_cadastro\"",
    "\"Ana Teste\",\"2026-09-28T18:55:42.327Z\"",
    "\"Bruno Teste\",\"2026-09-28T18:55:42.373Z\""
   ]
  }
 }
}
```
</details>

## nivel0-gpt-t3

- Instalação: ok — npm install ok
- [x] registra o nome no CSV
- [x] grava a data de cadastro
- [x] acrescenta sem sobrescrever (2 execuções = 2 linhas)
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "rodar cadastro.js \"Ana Teste\"",
   "codigo": 0,
   "saida": "Usuário cadastrado com sucesso.\nNome: Ana Teste\nData de cadastro: 2026-09-28T18:55:42.734Z\nArquivo: /home/claude/resultados-testes/projetos/nivel0-gpt-t3/usuarios.csv"
  },
  {
   "passo": "rodar cadastro.js \"Bruno Teste\"",
   "codigo": 0,
   "saida": "Usuário cadastrado com sucesso.\nNome: Bruno Teste\nData de cadastro: 2026-09-28T18:55:42.779Z\nArquivo: /home/claude/resultados-testes/projetos/nivel0-gpt-t3/usuarios.csv"
  }
 ],
 "evidencias": {
  "csv": {
   "arquivo": "usuarios.csv",
   "linhas": [
    "nome,data_de_cadastro",
    "\"Ana Teste\",\"2026-09-28T18:55:42.734Z\"",
    "\"Bruno Teste\",\"2026-09-28T18:55:42.779Z\""
   ]
  }
 }
}
```
</details>

## nivel0-groq-t1

- Instalação: ok — npm install ok
- **Teste manual:** script interativo que exige terminal: rode duas vezes à mão, informe dois nomes e confira o CSV (nome, data de cadastro, duas linhas).
- Completude sugerida: None (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "rodar index.js \"Ana Teste\"",
   "codigo": 1,
   "saida": "…loader:1441:32)\n    at Function._load (node:internal/modules/cjs/loader:1263:12)\n    at TracingChannel.traceSync (node:diagnostics_channel:328:14)\n    at wrapModuleLoad (node:internal/modules/cjs/loader:237:24) {\n  errno: -6,\n  code: 'ENXIO',\n  syscall: 'open',\n  path: '/dev/tty'\n}\n\nNode.js v22.22.2"
  },
  {
   "passo": "rodar index.js \"Bruno Teste\"",
   "codigo": 1,
   "saida": "…loader:1441:32)\n    at Function._load (node:internal/modules/cjs/loader:1263:12)\n    at TracingChannel.traceSync (node:diagnostics_channel:328:14)\n    at wrapModuleLoad (node:internal/modules/cjs/loader:237:24) {\n  errno: -6,\n  code: 'ENXIO',\n  syscall: 'open',\n  path: '/dev/tty'\n}\n\nNode.js v22.22.2"
  }
 ],
 "evidencias": {}
}
```
</details>

## nivel0-groq-t2

- Instalação: ok — npm install ok
- [x] registra o nome no CSV
- [x] grava a data de cadastro
- [x] acrescenta sem sobrescrever (2 execuções = 2 linhas)
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "rodar index.js \"Ana Teste\"",
   "codigo": 0,
   "saida": "Usuário \"Ana Teste\" registrado com sucesso em 2026-09-28 15:55:43."
  },
  {
   "passo": "rodar index.js \"Bruno Teste\"",
   "codigo": 0,
   "saida": "Usuário \"Bruno Teste\" registrado com sucesso em 2026-09-28 15:55:43."
  }
 ],
 "evidencias": {
  "csv": {
   "arquivo": "users.csv",
   "linhas": [
    "Ana Teste,2026-09-28 15:55:43",
    "Bruno Teste,2026-09-28 15:55:43"
   ]
  }
 }
}
```
</details>

## nivel0-groq-t3

- Instalação: ok — npm install ok
- [x] registra o nome no CSV
- [x] grava a data de cadastro
- [x] acrescenta sem sobrescrever (2 execuções = 2 linhas)
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "rodar registerUser.js \"Ana Teste\"",
   "codigo": 0,
   "saida": "✅ Usuário \"Ana Teste\" registrado em /home/claude/resultados-testes/projetos/nivel0-groq-t3/users.csv"
  },
  {
   "passo": "rodar registerUser.js \"Bruno Teste\"",
   "codigo": 0,
   "saida": "✅ Usuário \"Bruno Teste\" registrado em /home/claude/resultados-testes/projetos/nivel0-groq-t3/users.csv"
  }
 ],
 "evidencias": {
  "csv": {
   "arquivo": "users.csv",
   "linhas": [
    "\"Ana Teste\",\"2026-09-28 15:55:44\"",
    "\"Bruno Teste\",\"2026-09-28 15:55:44\""
   ]
  }
 }
}
```
</details>

## nivel1-claude-t1

- Instalação: ok — npm install ok
- [x] cadastra usuário
- [x] lista usuários
- [x] bloqueia e-mail duplicado
- [x] valida formato do e-mail
- [x] atualiza usuário
- [x] remove usuário
- [x] persiste em SQLite
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "cadastrar",
   "comando": "add --nome Ana Teste --email ana.teste@exemplo.com --nascimento 1990-05-10",
   "codigo": 0,
   "saida": "Usuario cadastrado com sucesso:\nID: 1 | Nome: Ana Teste | E-mail: ana.teste@exemplo.com | Nascimento: 1990-05-10 | Criado em: 2026-09-28 18:55:46 | Atualizado em: 2026-09-28 18:55:46"
  },
  {
   "passo": "listar",
   "comando": "list",
   "codigo": 0,
   "saida": "Total de usuarios: 1\n\nID: 1 | Nome: Ana Teste | E-mail: ana.teste@exemplo.com | Nascimento: 1990-05-10 | Criado em: 2026-09-28 18:55:46 | Atualizado em: 2026-09-28 18:55:46"
  },
  {
   "passo": "cadastrar de novo (duplicidade)",
   "comando": "add --nome Ana Teste --email ana.teste@exemplo.com --nascimento 1990-05-10",
   "codigo": 1,
   "saida": "Erro: Ja existe um usuario cadastrado com o e-mail \"ana.teste@exemplo.com\"."
  },
  {
   "passo": "cadastrar com e-mail inválido",
   "comando": "add --nome Ana Teste --email email-invalido --nascimento 1990-05-10",
   "codigo": 1,
   "saida": "Erro: E-mail invalido: \"email-invalido\". Use um formato como usuario@dominio.com"
  },
  {
   "passo": "atualizar",
   "comando": "update 1 --nome Ana Atualizada",
   "codigo": 1,
   "saida": "Erro: Informe o --id do usuario que deseja atualizar."
  },
  {
   "passo": "atualizar",
   "comando": "update --id 1 --nome Ana Atualizada",
   "codigo": 0,
   "saida": "Usuario atualizado com sucesso:\nID: 1 | Nome: Ana Atualizada | E-mail: ana.teste@exemplo.com | Nascimento: 1990-05-10 | Criado em: 2026-09-28 18:55:46 | Atualizado em: 2026-09-28 18:55:46"
  },
  {
   "passo": "listar",
   "comando": "list",
   "codigo": 0,
   "saida": "Total de usuarios: 1\n\nID: 1 | Nome: Ana Atualizada | E-mail: ana.teste@exemplo.com | Nascimento: 1990-05-10 | Criado em: 2026-09-28 18:55:46 | Atualizado em: 2026-09-28 18:55:46"
  },
  {
   "passo": "remover",
   "comando": "remove 1",
   "codigo": 1,
   "saida": "Erro: Informe o --id do usuario que deseja remover."
  },
  {
   "passo": "remover",
   "comando": "remove --id 1",
   "codigo": 0,
   "saida": "Usuario com ID 1 removido com sucesso."
  },
  {
   "passo": "listar",
   "comando": "list",
   "codigo": 0,
   "saida": "Nenhum usuario cadastrado ainda."
  }
 ],
 "evidencias": {
  "subcomandos encontrados": {
   "add": [
    "add"
   ],
   "list": [
    "list"
   ],
   "update": [
    "update"
   ],
   "remove": [
    "remove"
   ]
  },
  "id do cadastro": "1",
  "arquivos de banco criados": [
   "usuarios.db"
  ]
 }
}
```
</details>

## nivel1-claude-t2

- Instalação: ok — npm install ok
- [x] cadastra usuário
- [x] lista usuários
- [x] bloqueia e-mail duplicado
- [x] valida formato do e-mail
- [x] atualiza usuário
- [x] remove usuário
- [x] persiste em SQLite
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "cadastrar",
   "comando": "add --name Ana Teste --email ana.teste@exemplo.com --birthdate 1990-05-10",
   "codigo": 0,
   "saida": "Usuario cadastrado com sucesso:\n#1 | Nome: Ana Teste | E-mail: ana.teste@exemplo.com | Nascimento: 1990-05-10"
  },
  {
   "passo": "listar",
   "comando": "list",
   "codigo": 0,
   "saida": "Total de usuarios: 1\n#1 | Nome: Ana Teste | E-mail: ana.teste@exemplo.com | Nascimento: 1990-05-10"
  },
  {
   "passo": "cadastrar de novo (duplicidade)",
   "comando": "add --name Ana Teste --email ana.teste@exemplo.com --birthdate 1990-05-10",
   "codigo": 1,
   "saida": "Erro: Ja existe um usuario cadastrado com o e-mail \"ana.teste@exemplo.com\"."
  },
  {
   "passo": "cadastrar com e-mail inválido",
   "comando": "add --name Ana Teste --email email-invalido --birthdate 1990-05-10",
   "codigo": 1,
   "saida": "Erro: E-mail invalido: \"email-invalido\"."
  },
  {
   "passo": "atualizar",
   "comando": "update 1 --name Ana Atualizada",
   "codigo": 1,
   "saida": "Erro: Informe --id do usuario a ser atualizado."
  },
  {
   "passo": "atualizar",
   "comando": "update --id 1 --name Ana Atualizada",
   "codigo": 0,
   "saida": "Usuario atualizado com sucesso:\n#1 | Nome: Ana Atualizada | E-mail: ana.teste@exemplo.com | Nascimento: 1990-05-10"
  },
  {
   "passo": "listar",
   "comando": "list",
   "codigo": 0,
   "saida": "Total de usuarios: 1\n#1 | Nome: Ana Atualizada | E-mail: ana.teste@exemplo.com | Nascimento: 1990-05-10"
  },
  {
   "passo": "remover",
   "comando": "remove 1",
   "codigo": 1,
   "saida": "Erro: Informe --id do usuario a ser removido."
  },
  {
   "passo": "remover",
   "comando": "remove --id 1",
   "codigo": 0,
   "saida": "Usuario removido com sucesso:\n#1 | Nome: Ana Atualizada | E-mail: ana.teste@exemplo.com | Nascimento: 1990-05-10"
  },
  {
   "passo": "listar",
   "comando": "list",
   "codigo": 0,
   "saida": "Nenhum usuario cadastrado."
  }
 ],
 "evidencias": {
  "subcomandos encontrados": {
   "add": [
    "add"
   ],
   "list": [
    "list"
   ],
   "update": [
    "update"
   ],
   "remove": [
    "remove"
   ]
  },
  "id do cadastro": "1",
  "arquivos de banco criados": [
   "data.db"
  ]
 }
}
```
</details>

## nivel1-claude-t3

- Instalação: ok — npm install ok
- [x] cadastra usuário
- [x] lista usuários
- [x] bloqueia e-mail duplicado
- [x] valida formato do e-mail
- [x] atualiza usuário
- [x] remove usuário
- [x] persiste em SQLite
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "criar schema",
   "comando": "npm run init-db",
   "codigo": 0,
   "saida": "… user-cli@1.0.0 init-db\n> node -e \"require('./src/db.js').initSchema().then(()=>{console.log('Schema criado/atualizado com sucesso.'); process.exit(0);}).catch(e=>{console.error(e); process.exit(1);})\"\n\nSchema criado/atualizado com sucesso."
  },
  {
   "passo": "cadastrar",
   "comando": "add --name Ana Teste --email ana.teste@exemplo.com --dob 1990-05-10",
   "codigo": 0,
   "saida": "…        │ birthdate    │\n├─────────┼────┼─────────────┼─────────────────────────┼──────────────┤\n│ 0       │ 1  │ 'Ana Teste' │ 'ana.teste@exemplo.com' │ '1990-05-10' │\n└─────────┴────┴─────────────┴─────────────────────────┴──────────────┘"
  },
  {
   "passo": "listar",
   "comando": "list",
   "codigo": 0,
   "saida": "…\n│ 0       │ 1  │ 'Ana Teste' │ 'ana.teste@exemplo.com' │ '1990-05-10' │ '2026-09-28 18:55:53' │ '2026-09-28 18:55:53' │\n└─────────┴────┴─────────────┴─────────────────────────┴──────────────┴───────────────────────┴───────────────────────┘"
  },
  {
   "passo": "cadastrar de novo (duplicidade)",
   "comando": "add --name Ana Teste --email ana.teste@exemplo.com --dob 1990-05-10",
   "codigo": 1,
   "saida": "Erro: Ja existe um usuario cadastrado com o e-mail \"ana.teste@exemplo.com\" (id 1)."
  },
  {
   "passo": "cadastrar com e-mail inválido",
   "comando": "add --name Ana Teste --email email-invalido --dob 1990-05-10",
   "codigo": 1,
   "saida": "Erro: O e-mail \"email-invalido\" e invalido. Formato esperado: usuario@dominio.com"
  },
  {
   "passo": "atualizar",
   "comando": "update 1 --name Ana Atualizada",
   "codigo": 1,
   "saida": "Erro: Informe um --id valido (numero inteiro positivo)."
  },
  {
   "passo": "atualizar",
   "comando": "update --id 1 --name Ana Atualizada",
   "codigo": 0,
   "saida": "…date    │\n├─────────┼────┼──────────────────┼─────────────────────────┼──────────────┤\n│ 0       │ 1  │ 'Ana Atualizada' │ 'ana.teste@exemplo.com' │ '1990-05-10' │\n└─────────┴────┴──────────────────┴─────────────────────────┴──────────────┘"
  },
  {
   "passo": "listar",
   "comando": "list",
   "codigo": 0,
   "saida": "… │ 1  │ 'Ana Atualizada' │ 'ana.teste@exemplo.com' │ '1990-05-10' │ '2026-09-28 18:55:53' │ '2026-09-28 18:55:53' │\n└─────────┴────┴──────────────────┴─────────────────────────┴──────────────┴───────────────────────┴───────────────────────┘"
  },
  {
   "passo": "remover",
   "comando": "remove 1",
   "codigo": 1,
   "saida": "Erro: Informe um --id valido (numero inteiro positivo)."
  },
  {
   "passo": "remover",
   "comando": "remove --id 1",
   "codigo": 0,
   "saida": "Usuario com id 1 removido com sucesso."
  },
  {
   "passo": "listar",
   "comando": "list",
   "codigo": 0,
   "saida": "Nenhum usuario cadastrado."
  }
 ],
 "evidencias": {
  "subcomandos encontrados": {
   "add": [
    "add"
   ],
   "list": [
    "list"
   ],
   "update": [
    "update"
   ],
   "remove": [
    "remove"
   ]
  },
  "id do cadastro": "1",
  "arquivos de banco criados": [
   "data/users.db"
  ]
 }
}
```
</details>

## nivel1-gemini-t1

- Instalação: ok — npm install ok
- [x] cadastra usuário
- [x] lista usuários
- [x] bloqueia e-mail duplicado
- [x] valida formato do e-mail
- [x] atualiza usuário
- [x] remove usuário
- [x] persiste em SQLite
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "criar schema",
   "comando": "init",
   "codigo": 0,
   "saida": "✅ Banco de dados e tabelas inicializados com sucesso!"
  },
  {
   "passo": "cadastrar",
   "comando": "add --name Ana Teste --email ana.teste@exemplo.com --birthdate 1990-05-10",
   "codigo": 0,
   "saida": "❌ Erro: Formato de e-mail inválido."
  },
  {
   "passo": "cadastrar",
   "comando": "add --name Ana Teste --email ana.teste@exemplo.com --birth-date 1990-05-10",
   "codigo": 0,
   "saida": "❌ Erro: Formato de e-mail inválido."
  },
  {
   "passo": "cadastrar",
   "comando": "add --nome Ana Teste --email ana.teste@exemplo.com --birthdate 1990-05-10",
   "codigo": 0,
   "saida": "❌ Erro: Formato de e-mail inválido."
  },
  {
   "passo": "cadastrar",
   "comando": "add --nome Ana Teste --email ana.teste@exemplo.com --birth-date 1990-05-10",
   "codigo": 0,
   "saida": "❌ Erro: Formato de e-mail inválido."
  },
  {
   "passo": "cadastrar",
   "comando": "add Ana Teste ana.teste@exemplo.com 1990-05-10",
   "codigo": 0,
   "saida": "✅ Usuário 'Ana Teste' cadastrado com sucesso!"
  },
  {
   "passo": "listar",
   "comando": "list",
   "codigo": 0,
   "saida": "…        │ dob          │\n├─────────┼────┼─────────────┼─────────────────────────┼──────────────┤\n│ 0       │ 1  │ 'Ana Teste' │ 'ana.teste@exemplo.com' │ '1990-05-10' │\n└─────────┴────┴─────────────┴─────────────────────────┴──────────────┘"
  },
  {
   "passo": "cadastrar de novo (duplicidade)",
   "comando": "add Ana Teste ana.teste@exemplo.com 1990-05-10",
   "codigo": 0,
   "saida": "❌ Erro: O e-mail informado já está cadastrado no sistema."
  },
  {
   "passo": "cadastrar com e-mail inválido",
   "comando": "add Ana Teste email-invalido 1990-05-10",
   "codigo": 0,
   "saida": "❌ Erro: Formato de e-mail inválido."
  },
  {
   "passo": "atualizar",
   "comando": "update 1 --name Ana Atualizada",
   "codigo": 0,
   "saida": "Uso correto: node index.js update <id> \"<novo_nome>\" \"<novo_email>\" \"<nova_data YYYY-MM-DD>\""
  },
  {
   "passo": "listar",
   "comando": "list",
   "codigo": 0,
   "saida": "…        │ dob          │\n├─────────┼────┼─────────────┼─────────────────────────┼──────────────┤\n│ 0       │ 1  │ 'Ana Teste' │ 'ana.teste@exemplo.com' │ '1990-05-10' │\n└─────────┴────┴─────────────┴─────────────────────────┴──────────────┘"
  },
  {
   "passo": "atualizar",
   "comando": "update --id 1 --name Ana Atualizada",
   "codigo": 0,
   "saida": "❌ Erro: Formato de e-mail inválido."
  },
  {
   "passo": "atualizar",
   "comando": "update 1 --nome Ana Atualizada",
   "codigo": 0,
   "saida": "Uso correto: node index.js update <id> \"<novo_nome>\" \"<novo_email>\" \"<nova_data YYYY-MM-DD>\""
  },
  {
   "passo": "listar",
   "comando": "list",
   "codigo": 0,
   "saida": "…        │ dob          │\n├─────────┼────┼─────────────┼─────────────────────────┼──────────────┤\n│ 0       │ 1  │ 'Ana Teste' │ 'ana.teste@exemplo.com' │ '1990-05-10' │\n└─────────┴────┴─────────────┴─────────────────────────┴──────────────┘"
  },
  {
   "passo": "atualizar",
   "comando": "update --id 1 --nome Ana Atualizada",
   "codigo": 0,
   "saida": "❌ Erro: Formato de e-mail inválido."
  },
  {
   "passo": "atualizar",
   "comando": "update 1 Ana Atualizada ana.teste@exemplo.com 1990-05-10",
   "codigo": 0,
   "saida": "✅ Usuário ID 1 atualizado com sucesso!"
  },
  {
   "passo": "listar",
   "comando": "list",
   "codigo": 0,
   "saida": "…        │\n├─────────┼────┼──────────────────┼─────────────────────────┼──────────────┤\n│ 0       │ 1  │ 'Ana Atualizada' │ 'ana.teste@exemplo.com' │ '1990-05-10' │\n└─────────┴────┴──────────────────┴─────────────────────────┴──────────────┘"
  },
  {
   "passo": "remover",
   "comando": "delete 1",
   "codigo": 0,
   "saida": "✅ Usuário ID 1 removido com sucesso!"
  },
  {
   "passo": "listar",
   "comando": "list",
   "codigo": 0,
   "saida": "Nenhum usuário cadastrado."
  }
 ],
 "evidencias": {
  "subcomandos encontrados": {
   "init": [
    "init"
   ],
   "add": [
    "add"
   ],
   "list": [
    "list"
   ],
   "update": [
    "update"
   ],
   "remove": [
    "delete"
   ]
  },
  "id do cadastro": "1",
  "arquivos de banco criados": [
   "database.sqlite"
  ]
 }
}
```
</details>

## nivel1-gemini-t2

- Instalação: ok — npm install ok
- **Teste manual:** CLI interativa (menu): teste manual. Rode o programa, cadastre um usuário com ana.teste@exemplo.com, liste, tente o mesmo e-mail de novo, tente 'email-invalido', atualize, remova e anote o resultado.
- Completude sugerida: None (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [],
 "evidencias": {}
}
```
</details>

## nivel1-gemini-t3

- Instalação: ok — npm install ok
- **Teste manual:** CLI interativa (menu): teste manual. Rode o programa, cadastre um usuário com ana.teste@exemplo.com, liste, tente o mesmo e-mail de novo, tente 'email-invalido', atualize, remova e anote o resultado.
- Completude sugerida: None (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [],
 "evidencias": {}
}
```
</details>

## nivel1-gpt-t1

- Instalação: ok — npm install ok
- [x] cadastra usuário
- [x] lista usuários
- [x] bloqueia e-mail duplicado
- [x] valida formato do e-mail
- [x] atualiza usuário
- [x] remove usuário
- [x] persiste em SQLite
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "criar schema",
   "comando": "npm run init-db",
   "codigo": 0,
   "saida": "> usuarios-cli@1.0.0 init-db\n> node src/cli.js init\n\nBanco de dados inicializado com sucesso.\nArquivo: /home/claude/resultados-testes/projetos/nivel1-gpt-t1/data/users.db"
  },
  {
   "passo": "cadastrar",
   "comando": "cadastrar --nome Ana Teste --email ana.teste@exemplo.com --nascimento 1990-05-10",
   "codigo": 0,
   "saida": "Usuário cadastrado com sucesso.\nID: 1\nNome: Ana Teste\nE-mail: ana.teste@exemplo.com\nNascimento: 1990-05-10\nCriado em: 2026-09-28T18:56:00.984Z\nAtualizado em: 2026-09-28T18:56:00.984Z"
  },
  {
   "passo": "listar",
   "comando": "listar",
   "codigo": 0,
   "saida": "… 1  | Ana Teste | ana.teste@exemplo.com | 1990-05-10 | 2026-09-28T18:56:00.984Z | 2026-09-28T18:56:00.984Z |\n+----+-----------+-----------------------+------------+--------------------------+--------------------------+\n\nTotal: 1 usuário(s)."
  },
  {
   "passo": "cadastrar de novo (duplicidade)",
   "comando": "cadastrar --nome Ana Teste --email ana.teste@exemplo.com --nascimento 1990-05-10",
   "codigo": 1,
   "saida": "Erro: já existe um usuário cadastrado com este e-mail."
  },
  {
   "passo": "cadastrar com e-mail inválido",
   "comando": "cadastrar --nome Ana Teste --email email-invalido --nascimento 1990-05-10",
   "codigo": 1,
   "saida": "Erro: Formato de e-mail inválido. Exemplo esperado: usuario@dominio.com"
  },
  {
   "passo": "atualizar",
   "comando": "atualizar 1 --nome Ana Atualizada",
   "codigo": 0,
   "saida": "Usuário atualizado com sucesso.\nID: 1\nNome: Ana Atualizada\nE-mail: ana.teste@exemplo.com\nNascimento: 1990-05-10\nCriado em: 2026-09-28T18:56:00.984Z\nAtualizado em: 2026-09-28T18:56:01.191Z"
  },
  {
   "passo": "listar",
   "comando": "listar",
   "codigo": 0,
   "saida": "…Atualizada | ana.teste@exemplo.com | 1990-05-10 | 2026-09-28T18:56:00.984Z | 2026-09-28T18:56:01.191Z |\n+----+----------------+-----------------------+------------+--------------------------+--------------------------+\n\nTotal: 1 usuário(s)."
  },
  {
   "passo": "remover",
   "comando": "remover 1",
   "codigo": 0,
   "saida": "Usuário removido com sucesso.\nID: 1\nNome: Ana Atualizada\nE-mail: ana.teste@exemplo.com"
  },
  {
   "passo": "listar",
   "comando": "listar",
   "codigo": 0,
   "saida": "Nenhum usuário cadastrado."
  }
 ],
 "evidencias": {
  "subcomandos encontrados": {
   "init": [
    "init"
   ],
   "add": [
    "cadastrar"
   ],
   "list": [
    "listar"
   ],
   "update": [
    "atualizar"
   ],
   "remove": [
    "remover"
   ]
  },
  "id do cadastro": "1",
  "arquivos de banco criados": [
   "data/users.db"
  ]
 }
}
```
</details>

## nivel1-gpt-t2

- Instalação: ok — npm install ok
- [x] cadastra usuário
- [x] lista usuários
- [x] bloqueia e-mail duplicado
- [x] valida formato do e-mail
- [x] atualiza usuário
- [x] remove usuário
- [x] persiste em SQLite
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "criar schema",
   "comando": "npm run init-db",
   "codigo": 0,
   "saida": "> usuarios-cli@1.0.0 init-db\n> node src/index.js inicializar\n\nBanco de dados inicializado com sucesso.\nArquivo: /home/claude/resultados-testes/projetos/nivel1-gpt-t2/data/usuarios.db"
  },
  {
   "passo": "cadastrar",
   "comando": "cadastrar --nome Ana Teste --email ana.teste@exemplo.com --nascimento 1990-05-10",
   "codigo": 0,
   "saida": "…\n│ 0       │ 1  │ 'Ana Teste' │ 'ana.teste@exemplo.com' │ '1990-05-10' │ '2026-09-28 18:56:02' │ '2026-09-28 18:56:02' │\n└─────────┴────┴─────────────┴─────────────────────────┴──────────────┴───────────────────────┴───────────────────────┘"
  },
  {
   "passo": "listar",
   "comando": "listar",
   "codigo": 0,
   "saida": "…\n│ 0       │ 1  │ 'Ana Teste' │ 'ana.teste@exemplo.com' │ '1990-05-10' │ '2026-09-28 18:56:02' │ '2026-09-28 18:56:02' │\n└─────────┴────┴─────────────┴─────────────────────────┴──────────────┴───────────────────────┴───────────────────────┘"
  },
  {
   "passo": "cadastrar de novo (duplicidade)",
   "comando": "cadastrar --nome Ana Teste --email ana.teste@exemplo.com --nascimento 1990-05-10",
   "codigo": 1,
   "saida": "Erro: já existe um usuário cadastrado com esse e-mail."
  },
  {
   "passo": "cadastrar com e-mail inválido",
   "comando": "cadastrar --nome Ana Teste --email email-invalido --nascimento 1990-05-10",
   "codigo": 1,
   "saida": "Erro: Formato de e-mail inválido. Exemplo esperado: usuario@dominio.com."
  },
  {
   "passo": "atualizar",
   "comando": "atualizar 1 --nome Ana Atualizada",
   "codigo": 0,
   "saida": "… │ 1  │ 'Ana Atualizada' │ 'ana.teste@exemplo.com' │ '1990-05-10' │ '2026-09-28 18:56:02' │ '2026-09-28 18:56:02' │\n└─────────┴────┴──────────────────┴─────────────────────────┴──────────────┴───────────────────────┴───────────────────────┘"
  },
  {
   "passo": "listar",
   "comando": "listar",
   "codigo": 0,
   "saida": "… │ 1  │ 'Ana Atualizada' │ 'ana.teste@exemplo.com' │ '1990-05-10' │ '2026-09-28 18:56:02' │ '2026-09-28 18:56:02' │\n└─────────┴────┴──────────────────┴─────────────────────────┴──────────────┴───────────────────────┴───────────────────────┘"
  },
  {
   "passo": "remover",
   "comando": "remover 1",
   "codigo": 0,
   "saida": "Usuário removido com sucesso: Ana Atualizada <ana.teste@exemplo.com>."
  },
  {
   "passo": "listar",
   "comando": "listar",
   "codigo": 0,
   "saida": "Nenhum usuário cadastrado."
  }
 ],
 "evidencias": {
  "subcomandos encontrados": {
   "init": [
    "inicializar"
   ],
   "add": [
    "cadastrar"
   ],
   "list": [
    "listar"
   ],
   "update": [
    "atualizar"
   ],
   "remove": [
    "remover"
   ]
  },
  "id do cadastro": "1",
  "arquivos de banco criados": [
   "data/usuarios.db"
  ]
 }
}
```
</details>

## nivel1-gpt-t3

- Instalação: ok — npm install ok
- [x] cadastra usuário
- [x] lista usuários
- [x] bloqueia e-mail duplicado
- [x] valida formato do e-mail
- [x] atualiza usuário
- [x] remove usuário
- [x] persiste em SQLite
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "criar schema",
   "comando": "npm run init",
   "codigo": 0,
   "saida": "> usuarios-cli@1.0.0 init\n> node src/cli.js inicializar\n\nBanco de dados inicializado com sucesso.\nArquivo: /home/claude/resultados-testes/projetos/nivel1-gpt-t3/data/usuarios.db"
  },
  {
   "passo": "cadastrar",
   "comando": "cadastrar --nome Ana Teste --email ana.teste@exemplo.com --nascimento 1990-05-10",
   "codigo": 0,
   "saida": "Usuário cadastrado com sucesso.\nID: 1\nNome: Ana Teste\nE-mail: ana.teste@exemplo.com\nData de nascimento: 1990-05-10"
  },
  {
   "passo": "listar",
   "comando": "listar",
   "codigo": 0,
   "saida": "… │\n├─────────┼────┼─────────────┼─────────────────────────┼──────────────┤\n│ 0       │ 1  │ 'Ana Teste' │ 'ana.teste@exemplo.com' │ '1990-05-10' │\n└─────────┴────┴─────────────┴─────────────────────────┴──────────────┘\n1 usuário encontrado."
  },
  {
   "passo": "cadastrar de novo (duplicidade)",
   "comando": "cadastrar --nome Ana Teste --email ana.teste@exemplo.com --nascimento 1990-05-10",
   "codigo": 1,
   "saida": "Erro: Já existe um usuário cadastrado com o e-mail \"ana.teste@exemplo.com\"."
  },
  {
   "passo": "cadastrar com e-mail inválido",
   "comando": "cadastrar --nome Ana Teste --email email-invalido --nascimento 1990-05-10",
   "codigo": 1,
   "saida": "Erro: Formato de e-mail inválido. Exemplo esperado: usuario@dominio.com."
  },
  {
   "passo": "atualizar",
   "comando": "atualizar 1 --nome Ana Atualizada",
   "codigo": 0,
   "saida": "Usuário atualizado com sucesso.\nID: 1\nNome: Ana Atualizada\nE-mail: ana.teste@exemplo.com\nData de nascimento: 1990-05-10"
  },
  {
   "passo": "listar",
   "comando": "listar",
   "codigo": 0,
   "saida": "…───┼──────────────────┼─────────────────────────┼──────────────┤\n│ 0       │ 1  │ 'Ana Atualizada' │ 'ana.teste@exemplo.com' │ '1990-05-10' │\n└─────────┴────┴──────────────────┴─────────────────────────┴──────────────┘\n1 usuário encontrado."
  },
  {
   "passo": "remover",
   "comando": "remover 1 --sim",
   "codigo": 0,
   "saida": "Usuário com ID 1 removido com sucesso."
  },
  {
   "passo": "listar",
   "comando": "listar",
   "codigo": 0,
   "saida": "Nenhum usuário cadastrado."
  }
 ],
 "evidencias": {
  "subcomandos encontrados": {
   "init": [
    "inicializar"
   ],
   "add": [
    "cadastrar"
   ],
   "list": [
    "listar"
   ],
   "update": [
    "atualizar"
   ],
   "remove": [
    "remover"
   ]
  },
  "id do cadastro": "1",
  "arquivos de banco criados": [
   "data/usuarios.db"
  ]
 }
}
```
</details>

## nivel1-groq-t1

- Instalação: ok — npm install ok
- [x] cadastra usuário
- [x] lista usuários
- [x] bloqueia e-mail duplicado
- [x] valida formato do e-mail
- [x] atualiza usuário
- [x] remove usuário
- [x] persiste em SQLite
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "criar schema",
   "comando": "npm run setup",
   "codigo": 0,
   "saida": "> user-cli@1.0.0 setup\n> node db.js init\n\nBanco de dados e schema criados com sucesso."
  },
  {
   "passo": "cadastrar",
   "comando": "add --name Ana Teste --email ana.teste@exemplo.com --birthdate 1990-05-10",
   "codigo": 0,
   "saida": "✔ Usuário cadastrado com sucesso."
  },
  {
   "passo": "listar",
   "comando": "list",
   "codigo": 0,
   "saida": "…        │ birthdate    │\n├─────────┼────┼─────────────┼─────────────────────────┼──────────────┤\n│ 0       │ 1  │ 'Ana Teste' │ 'ana.teste@exemplo.com' │ '1990-05-10' │\n└─────────┴────┴─────────────┴─────────────────────────┴──────────────┘"
  },
  {
   "passo": "cadastrar de novo (duplicidade)",
   "comando": "add --name Ana Teste --email ana.teste@exemplo.com --birthdate 1990-05-10",
   "codigo": 1,
   "saida": "✖ Já existe um usuário com esse e‑mail."
  },
  {
   "passo": "cadastrar com e-mail inválido",
   "comando": "add --name Ana Teste --email email-invalido --birthdate 1990-05-10",
   "codigo": 1,
   "saida": "✖ E‑mail inválido."
  },
  {
   "passo": "atualizar",
   "comando": "update 1 --name Ana Atualizada",
   "codigo": 0,
   "saida": "✔ Usuário atualizado com sucesso."
  },
  {
   "passo": "listar",
   "comando": "list",
   "codigo": 0,
   "saida": "…date    │\n├─────────┼────┼──────────────────┼─────────────────────────┼──────────────┤\n│ 0       │ 1  │ 'Ana Atualizada' │ 'ana.teste@exemplo.com' │ '1990-05-10' │\n└─────────┴────┴──────────────────┴─────────────────────────┴──────────────┘"
  },
  {
   "passo": "remover",
   "comando": "delete 1",
   "codigo": 0,
   "saida": "Tem certeza que deseja remover o usuário com id 1? (y/n): ✔ Usuário removido com sucesso."
  },
  {
   "passo": "listar",
   "comando": "list",
   "codigo": 0,
   "saida": "Nenhum usuário cadastrado."
  }
 ],
 "evidencias": {
  "subcomandos encontrados": {
   "init": [
    "init"
   ],
   "add": [
    "add"
   ],
   "list": [
    "list"
   ],
   "update": [
    "update"
   ],
   "remove": [
    "delete"
   ]
  },
  "id do cadastro": "1",
  "arquivos de banco criados": [
   "users.db"
  ]
 }
}
```
</details>

## nivel1-groq-t2

- Instalação: FALHOU — …ync run (/opt/node22/lib/node_modules/npm/node_modules/node-gyp/bin/node-gyp.js:81:18)
npm error gyp ERR! System Linux 6.18.44-fc-v42
npm error gyp ERR! command "/opt/node22/bin/node" "/opt/node22/lib/node_modules/npm/node_modules/node-gyp/bin/node-gyp.js" "rebuild" "--release"
npm error gyp ERR! c
- Problemas: npm install falhou sem alterações: veja o detalhe
- Completude sugerida: None (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [],
 "evidencias": {}
}
```
</details>

## nivel1-groq-t3

- Instalação: FALHOU — …ync run (/opt/node22/lib/node_modules/npm/node_modules/node-gyp/bin/node-gyp.js:81:18)
npm error gyp ERR! System Linux 6.18.44-fc-v42
npm error gyp ERR! command "/opt/node22/bin/node" "/opt/node22/lib/node_modules/npm/node_modules/node-gyp/bin/node-gyp.js" "rebuild" "--release"
npm error gyp ERR! c
- Problemas: npm install falhou sem alterações: veja o detalhe
- Completude sugerida: None (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [],
 "evidencias": {}
}
```
</details>

## nivel2-claude-t1

- Instalação: ok — npm install ok
- [x] cria usuário
- [x] lista usuários
- [x] atualiza usuário
- [x] remove usuário
- [x] respostas em JSON
- [x] recusa e-mail duplicado com 4xx
- [x] persiste em SQLite
- (info) código de criação: 201
- (info) código para duplicidade: 409
- (info) recusa e-mail inválido: True
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "POST /users",
   "resultado": "201 {\"id\":1,\"name\":\"Ana Teste\",\"email\":\"ana.teste@exemplo.com\",\"birth_date\":\"1990-05-10\",\"created_at\":\"2026-09-28 18:56:19\",\"updated_at\":\"2026-09-28 18:56:19\"}"
  },
  {
   "passo": "POST duplicado",
   "resultado": "409 {\"error\":\"Ja existe um usuario cadastrado com este e-mail.\"}"
  },
  {
   "passo": "POST e-mail inválido",
   "resultado": "400 {\"error\":\"Dados invalidos.\",\"details\":[\"O campo \\\"email\\\" deve ser um endereco de e-mail valido.\"]}"
  },
  {
   "passo": "POST sem campos",
   "resultado": "400 …er uma string entre 2 e 100 caracteres.\",\"O campo \\\"email\\\" deve ser um endereco de e-mail valido.\",\"O campo \\\"birth_date\\\" deve estar no formato YYYY-MM-DD.\"]}"
  },
  {
   "passo": "PUT/PATCH /users/1",
   "resultado": "200 {\"id\":1,\"name\":\"Ana Atualizada\",\"email\":\"ana.teste@exemplo.com\",\"birth_date\":\"1990-05-10\",\"created_at\":\"2026-09-28 18:56:19\",\"updated_at\":\"2026-09-28 18:56:19\"}"
  },
  {
   "passo": "DELETE /users/1",
   "resultado": "204 "
  }
 ],
 "evidencias": {
  "porta": 47935,
  "rotas encontradas no código": [
   "DELETE /users/:id",
   "GET /users",
   "GET /users/:id",
   "POST /users",
   "PUT /users/:id"
  ],
  "rota": "/users",
  "status": {
   "criar": 201,
   "duplicado": 409,
   "email_invalido": 400,
   "sem_campos": 400,
   "atualizar": 200,
   "remover": 204,
   "campos": [
    "birthDate",
    "birth_date",
    "birthdate",
    "dataNascimento",
    "data_nascimento",
    "dateOfBirth",
    "dob",
    "email",
    "name",
    "nascimento",
    "nome"
   ]
  },
  "arquivos de banco criados": [
   "users.db"
  ]
 }
}
```
</details>

## nivel2-claude-t2

- Instalação: ok — npm install ok
- [x] cria usuário
- [x] lista usuários
- [x] atualiza usuário
- [x] remove usuário
- [x] respostas em JSON
- [x] recusa e-mail duplicado com 4xx
- [x] persiste em SQLite
- (info) código de criação: 201
- (info) código para duplicidade: 409
- (info) recusa e-mail inválido: True
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "POST /users",
   "resultado": "201 …ome\":\"Ana Teste\",\"email\":\"ana.teste@exemplo.com\",\"data_nascimento\":\"1990-05-10\",\"created_at\":\"2026-09-28T18:56:21.855Z\",\"updated_at\":\"2026-09-28T18:56:21.855Z\"}"
  },
  {
   "passo": "POST duplicado",
   "resultado": "409 {\"errors\":[\"Ja existe um usuario cadastrado com este e-mail.\"]}"
  },
  {
   "passo": "POST e-mail inválido",
   "resultado": "400 {\"errors\":[\"O campo \\\"email\\\" e obrigatorio e deve conter um e-mail valido.\"]}"
  },
  {
   "passo": "POST sem campos",
   "resultado": "400 …\\\"email\\\" e obrigatorio e deve conter um e-mail valido.\",\"O campo \\\"data_nascimento\\\" e obrigatorio e deve estar no formato YYYY-MM-DD e ser uma data valida.\"]}"
  },
  {
   "passo": "PUT/PATCH /users/1",
   "resultado": "200 …\"Ana Atualizada\",\"email\":\"ana.teste@exemplo.com\",\"data_nascimento\":\"1990-05-10\",\"created_at\":\"2026-09-28T18:56:21.855Z\",\"updated_at\":\"2026-09-28T18:56:21.866Z\"}"
  },
  {
   "passo": "DELETE /users/1",
   "resultado": "204 "
  }
 ],
 "evidencias": {
  "porta": 34467,
  "rotas encontradas no código": [
   "DELETE /users/:id",
   "GET /",
   "GET /users/",
   "GET /users/:id",
   "POST /users/",
   "PUT /users/:id"
  ],
  "rota": "/users",
  "status": {
   "criar": 201,
   "duplicado": 409,
   "email_invalido": 400,
   "sem_campos": 400,
   "atualizar": 200,
   "remover": 204,
   "campos": [
    "birthDate",
    "birth_date",
    "birthdate",
    "dataNascimento",
    "data_nascimento",
    "dateOfBirth",
    "dob",
    "email",
    "name",
    "nascimento",
    "nome"
   ]
  },
  "arquivos de banco criados": [
   "usuarios.db"
  ]
 }
}
```
</details>

## nivel2-claude-t3

- Instalação: ok — npm install ok
- [x] cria usuário
- [x] lista usuários
- [x] atualiza usuário
- [x] remove usuário
- [x] respostas em JSON
- [x] recusa e-mail duplicado com 4xx
- [x] persiste em SQLite
- (info) código de criação: 201
- (info) código para duplicidade: 409
- (info) recusa e-mail inválido: True
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "POST /usuarios",
   "resultado": "201 …e\":\"Ana Teste\",\"email\":\"ana.teste@exemplo.com\",\"data_nascimento\":\"1990-05-10\",\"criado_em\":\"2026-09-28T18:56:23.831Z\",\"atualizado_em\":\"2026-09-28T18:56:23.831Z\"}"
  },
  {
   "passo": "POST duplicado",
   "resultado": "409 {\"erro\":\"Ja existe um usuario cadastrado com este e-mail.\"}"
  },
  {
   "passo": "POST e-mail inválido",
   "resultado": "400 {\"erros\":[\"O campo \\\"email\\\" e obrigatorio e deve conter um endereco de e-mail valido.\"]}"
  },
  {
   "passo": "POST sem campos",
   "resultado": "400 …,\"O campo \\\"email\\\" e obrigatorio e deve conter um endereco de e-mail valido.\",\"O campo \\\"data_nascimento\\\" e obrigatorio e deve estar no formato YYYY-MM-DD.\"]}"
  },
  {
   "passo": "PUT/PATCH /usuarios/1",
   "resultado": "200 …na Atualizada\",\"email\":\"ana.teste@exemplo.com\",\"data_nascimento\":\"1990-05-10\",\"criado_em\":\"2026-09-28T18:56:23.831Z\",\"atualizado_em\":\"2026-09-28T18:56:23.840Z\"}"
  },
  {
   "passo": "DELETE /usuarios/1",
   "resultado": "204 "
  }
 ],
 "evidencias": {
  "porta": 32981,
  "rotas encontradas no código": [
   "DELETE /usuarios/:id",
   "GET /usuarios",
   "GET /usuarios/:id",
   "POST /usuarios",
   "PUT /usuarios/:id"
  ],
  "rota": "/usuarios",
  "status": {
   "criar": 201,
   "duplicado": 409,
   "email_invalido": 400,
   "sem_campos": 400,
   "atualizar": 200,
   "remover": 204,
   "campos": [
    "birthDate",
    "birth_date",
    "birthdate",
    "dataNascimento",
    "data_nascimento",
    "dateOfBirth",
    "dob",
    "email",
    "name",
    "nascimento",
    "nome"
   ]
  },
  "arquivos de banco criados": [
   "database.sqlite"
  ]
 }
}
```
</details>

## nivel2-gemini-t1

- Instalação: ok — npm install ok
- [x] cria usuário
- [x] lista usuários
- [x] atualiza usuário
- [x] remove usuário
- [x] respostas em JSON
- [x] recusa e-mail duplicado com 4xx
- [x] persiste em SQLite
- (info) código de criação: 201
- (info) código para duplicidade: 400
- (info) recusa e-mail inválido: False
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "POST /users",
   "resultado": "201 {\"id\":1,\"name\":\"Ana Teste\",\"email\":\"ana.teste@exemplo.com\",\"birthdate\":\"1990-05-10\"}"
  },
  {
   "passo": "POST duplicado",
   "resultado": "400 {\"error\":\"Este e-mail já está cadastrado.\"}"
  },
  {
   "passo": "POST e-mail inválido",
   "resultado": "201 {\"id\":2,\"name\":\"Ana Teste\",\"email\":\"email-invalido\",\"birthdate\":\"1990-05-10\"}"
  },
  {
   "passo": "POST sem campos",
   "resultado": "400 {\"error\":\"Nome, e-mail e data de nascimento são obrigatórios.\"}"
  },
  {
   "passo": "PUT/PATCH /users/1",
   "resultado": "200 {\"id\":1,\"name\":\"Ana Atualizada\",\"email\":\"ana.teste@exemplo.com\",\"birthdate\":\"1990-05-10\"}"
  },
  {
   "passo": "DELETE /users/1",
   "resultado": "204 "
  }
 ],
 "evidencias": {
  "porta": 3000,
  "rotas encontradas no código": [
   "DELETE /users/:id",
   "GET /users",
   "GET /users/:id",
   "POST /users",
   "PUT /users/:id"
  ],
  "rota": "/users",
  "status": {
   "criar": 201,
   "duplicado": 400,
   "email_invalido": 201,
   "sem_campos": 400,
   "atualizar": 200,
   "remover": 204,
   "campos": [
    "birthDate",
    "birth_date",
    "birthdate",
    "dataNascimento",
    "data_nascimento",
    "dateOfBirth",
    "dob",
    "email",
    "name",
    "nascimento",
    "nome"
   ]
  },
  "arquivos de banco criados": [
   "database.sqlite"
  ]
 }
}
```
</details>

## nivel2-gemini-t2

- Instalação: ok — npm install ok
- [x] cria usuário
- [x] lista usuários
- [x] atualiza usuário
- [x] remove usuário
- [x] respostas em JSON
- [x] recusa e-mail duplicado com 4xx
- [x] persiste em SQLite
- (info) código de criação: 201
- (info) código para duplicidade: 400
- (info) recusa e-mail inválido: False
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "POST /users",
   "resultado": "201 {\"id\":1,\"name\":\"Ana Teste\",\"email\":\"ana.teste@exemplo.com\",\"birthdate\":\"1990-05-10\"}"
  },
  {
   "passo": "POST duplicado",
   "resultado": "400 {\"error\":\"Este e-mail já está cadastrado.\"}"
  },
  {
   "passo": "POST e-mail inválido",
   "resultado": "201 {\"id\":2,\"name\":\"Ana Teste\",\"email\":\"email-invalido\",\"birthdate\":\"1990-05-10\"}"
  },
  {
   "passo": "POST sem campos",
   "resultado": "400 {\"error\":\"Nome, e-mail e data de nascimento são obrigatórios.\"}"
  },
  {
   "passo": "PUT/PATCH /users/1",
   "resultado": "200 {\"id\":1,\"name\":\"Ana Atualizada\",\"email\":\"ana.teste@exemplo.com\",\"birthdate\":\"1990-05-10\"}"
  },
  {
   "passo": "DELETE /users/1",
   "resultado": "204 "
  }
 ],
 "evidencias": {
  "porta": 3000,
  "rotas encontradas no código": [
   "DELETE /users/:id",
   "GET /users",
   "GET /users/:id",
   "POST /users",
   "PUT /users/:id"
  ],
  "rota": "/users",
  "status": {
   "criar": 201,
   "duplicado": 400,
   "email_invalido": 201,
   "sem_campos": 400,
   "atualizar": 200,
   "remover": 204,
   "campos": [
    "birthDate",
    "birth_date",
    "birthdate",
    "dataNascimento",
    "data_nascimento",
    "dateOfBirth",
    "dob",
    "email",
    "name",
    "nascimento",
    "nome"
   ]
  },
  "arquivos de banco criados": [
   "database.sqlite"
  ]
 }
}
```
</details>

## nivel2-gemini-t3

- Instalação: ok — npm install ok
- [x] cria usuário
- [x] lista usuários
- [x] atualiza usuário
- [x] remove usuário
- [x] respostas em JSON
- [x] recusa e-mail duplicado com 4xx
- [x] persiste em SQLite
- (info) código de criação: 201
- (info) código para duplicidade: 409
- (info) recusa e-mail inválido: False
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "POST /users",
   "resultado": "201 {\"id\":1,\"name\":\"Ana Teste\",\"email\":\"ana.teste@exemplo.com\",\"birthdate\":\"1990-05-10\"}"
  },
  {
   "passo": "POST duplicado",
   "resultado": "409 {\"error\":\"Este e-mail já está cadastrado.\"}"
  },
  {
   "passo": "POST e-mail inválido",
   "resultado": "201 {\"id\":2,\"name\":\"Ana Teste\",\"email\":\"email-invalido\",\"birthdate\":\"1990-05-10\"}"
  },
  {
   "passo": "POST sem campos",
   "resultado": "400 {\"error\":\"Nome, e-mail e data de nascimento são obrigatórios.\"}"
  },
  {
   "passo": "PUT/PATCH /users/1",
   "resultado": "200 {\"id\":1,\"name\":\"Ana Atualizada\",\"email\":\"ana.teste@exemplo.com\",\"birthdate\":\"1990-05-10\"}"
  },
  {
   "passo": "DELETE /users/1",
   "resultado": "204 "
  }
 ],
 "evidencias": {
  "porta": 51491,
  "rotas encontradas no código": [
   "DELETE /users/:id",
   "GET /users",
   "GET /users/:id",
   "POST /users",
   "PUT /users/:id"
  ],
  "rota": "/users",
  "status": {
   "criar": 201,
   "duplicado": 409,
   "email_invalido": 201,
   "sem_campos": 400,
   "atualizar": 200,
   "remover": 204,
   "campos": [
    "birthDate",
    "birth_date",
    "birthdate",
    "dataNascimento",
    "data_nascimento",
    "dateOfBirth",
    "dob",
    "email",
    "name",
    "nascimento",
    "nome"
   ]
  },
  "arquivos de banco criados": [
   "database.sqlite"
  ]
 }
}
```
</details>

## nivel2-gpt-t1

- Instalação: ok — npm install ok
- [x] cria usuário
- [x] lista usuários
- [x] atualiza usuário
- [x] remove usuário
- [x] respostas em JSON
- [x] recusa e-mail duplicado com 4xx
- [x] persiste em SQLite
- (info) código de criação: 201
- (info) código para duplicidade: 409
- (info) recusa e-mail inválido: True
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "POST /usuarios",
   "resultado": "201 {\"id\":1,\"nome\":\"Ana Teste\",\"email\":\"ana.teste@exemplo.com\",\"dataNascimento\":\"1990-05-10\"}"
  },
  {
   "passo": "POST duplicado",
   "resultado": "409 {\"erro\":\"Já existe um usuário cadastrado com este e-mail.\"}"
  },
  {
   "passo": "POST e-mail inválido",
   "resultado": "400 {\"erro\":\"O campo \\\"email\\\" deve conter um endereço de e-mail válido.\"}"
  },
  {
   "passo": "POST sem campos",
   "resultado": "400 {\"erro\":\"O campo \\\"nome\\\" é obrigatório e deve ser uma string.\"}"
  },
  {
   "passo": "PUT/PATCH /usuarios/1",
   "resultado": "200 {\"id\":1,\"nome\":\"Ana Atualizada\",\"email\":\"ana.teste@exemplo.com\",\"dataNascimento\":\"1990-05-10\"}"
  },
  {
   "passo": "DELETE /usuarios/1",
   "resultado": "204 "
  }
 ],
 "evidencias": {
  "porta": 45097,
  "rotas encontradas no código": [
   "DELETE /usuarios/:id",
   "GET /",
   "GET /usuarios",
   "GET /usuarios/:id",
   "POST /usuarios",
   "PUT /usuarios/:id"
  ],
  "rota": "/usuarios",
  "status": {
   "criar": 201,
   "duplicado": 409,
   "email_invalido": 400,
   "sem_campos": 400,
   "atualizar": 200,
   "remover": 204,
   "campos": [
    "dataNascimento",
    "email",
    "nome"
   ]
  },
  "arquivos de banco criados": [
   "data/usuarios.sqlite"
  ]
 }
}
```
</details>

## nivel2-gpt-t2

- Instalação: ok — npm install ok
- [x] cria usuário
- [x] lista usuários
- [x] atualiza usuário
- [x] remove usuário
- [x] respostas em JSON
- [x] recusa e-mail duplicado com 4xx
- [x] persiste em SQLite
- (info) código de criação: 201
- (info) código para duplicidade: 409
- (info) recusa e-mail inválido: True
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "POST /usuarios",
   "resultado": "201 …id\":1,\"nome\":\"Ana Teste\",\"email\":\"ana.teste@exemplo.com\",\"data_nascimento\":\"1990-05-10\",\"criado_em\":\"2026-09-28 18:56:35\",\"atualizado_em\":\"2026-09-28 18:56:35\"}"
  },
  {
   "passo": "POST duplicado",
   "resultado": "409 {\"erro\":{\"status\":409,\"mensagem\":\"Já existe um usuário com este e-mail.\"}}"
  },
  {
   "passo": "POST e-mail inválido",
   "resultado": "422 {\"erro\":{\"status\":422,\"mensagem\":\"Os dados informados são inválidos.\",\"detalhes\":{\"email\":\"Informe um endereço de e-mail válido.\"}}}"
  },
  {
   "passo": "POST sem campos",
   "resultado": "400 {\"erro\":{\"status\":400,\"mensagem\":\"Existem campos obrigatórios ausentes.\",\"detalhes\":{\"campos\":[\"nome\",\"email\",\"data_nascimento\"]}}}"
  },
  {
   "passo": "PUT/PATCH /usuarios/1",
   "resultado": "200 …,\"nome\":\"Ana Atualizada\",\"email\":\"ana.teste@exemplo.com\",\"data_nascimento\":\"1990-05-10\",\"criado_em\":\"2026-09-28 18:56:35\",\"atualizado_em\":\"2026-09-28 18:56:35\"}"
  },
  {
   "passo": "DELETE /usuarios/1",
   "resultado": "200 {\"mensagem\":\"Usuário removido com sucesso.\",\"id\":1}"
  }
 ],
 "evidencias": {
  "porta": 47671,
  "rotas encontradas no código": [],
  "rota": "/usuarios",
  "status": {
   "criar": 201,
   "duplicado": 409,
   "email_invalido": 422,
   "sem_campos": 400,
   "atualizar": 200,
   "remover": 200,
   "campos": [
    "data_nascimento",
    "email",
    "nome"
   ]
  },
  "arquivos de banco criados": [
   "data/usuarios.db"
  ]
 }
}
```
</details>

## nivel2-gpt-t3

- Instalação: ok — npm install ok
- [x] cria usuário
- [x] lista usuários
- [x] atualiza usuário
- [x] remove usuário
- [x] respostas em JSON
- [x] recusa e-mail duplicado com 4xx
- [x] persiste em SQLite
- (info) código de criação: 201
- (info) código para duplicidade: 409
- (info) recusa e-mail inválido: True
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "POST /usuarios",
   "resultado": "201 …e\":\"Ana Teste\",\"email\":\"ana.teste@exemplo.com\",\"data_nascimento\":\"1990-05-10\",\"criado_em\":\"2026-09-28T18:56:36.947Z\",\"atualizado_em\":\"2026-09-28T18:56:36.947Z\"}"
  },
  {
   "passo": "POST duplicado",
   "resultado": "409 {\"erro\":{\"codigo\":\"EMAIL_JA_CADASTRADO\",\"mensagem\":\"Já existe um usuário cadastrado com este e-mail.\"}}"
  },
  {
   "passo": "POST e-mail inválido",
   "resultado": "422 {\"erro\":{\"codigo\":\"DADOS_INVALIDOS\",\"mensagem\":\"Os dados informados são inválidos.\",\"detalhes\":{\"email\":\"O e-mail informado é inválido.\"}}}"
  },
  {
   "passo": "POST sem campos",
   "resultado": "422 …formados são inválidos.\",\"detalhes\":{\"nome\":\"O nome é obrigatório.\",\"email\":\"O e-mail é obrigatório.\",\"data_nascimento\":\"A data de nascimento é obrigatória.\"}}}"
  },
  {
   "passo": "PUT/PATCH /usuarios/1",
   "resultado": "200 …na Atualizada\",\"email\":\"ana.teste@exemplo.com\",\"data_nascimento\":\"1990-05-10\",\"criado_em\":\"2026-09-28T18:56:36.947Z\",\"atualizado_em\":\"2026-09-28T18:56:36.956Z\"}"
  },
  {
   "passo": "DELETE /usuarios/1",
   "resultado": "204 "
  }
 ],
 "evidencias": {
  "porta": 33451,
  "rotas encontradas no código": [
   "DELETE /usuarios/:id",
   "GET /health",
   "GET /usuarios",
   "GET /usuarios/:id",
   "POST /usuarios",
   "PUT /usuarios/:id"
  ],
  "rota": "/usuarios",
  "status": {
   "criar": 201,
   "duplicado": 409,
   "email_invalido": 422,
   "sem_campos": 422,
   "atualizar": 200,
   "remover": 204,
   "campos": [
    "birthDate",
    "birth_date",
    "birthdate",
    "dataNascimento",
    "data_nascimento",
    "dateOfBirth",
    "dob",
    "email",
    "name",
    "nascimento",
    "nome"
   ]
  },
  "arquivos de banco criados": [
   "data/usuarios.db"
  ]
 }
}
```
</details>

## nivel2-groq-t1

- Instalação: FALHOU — package.json inválido (não é JSON válido)
- Problemas: npm install falhou sem alterações: veja o detalhe
- Completude sugerida: None (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [],
 "evidencias": {}
}
```
</details>

## nivel2-groq-t2

- Instalação: ok — npm install ok
- Problemas: o servidor não subiu (dependência ausente: sqlite; exige correção manual)
- Completude sugerida: None (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [],
 "evidencias": {}
}
```
</details>

## nivel2-groq-t3

- Instalação: FALHOU — package.json inválido (não é JSON válido)
- Problemas: npm install falhou sem alterações: veja o detalhe
- Completude sugerida: None (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [],
 "evidencias": {}
}
```
</details>

## nivel3-claude-t1

- Instalação: ok — npm install ok
- [x] cria usuário
- [x] lista usuários
- [x] atualiza usuário
- [x] remove usuário
- [x] serve interface no navegador
- [x] front-end cadastra, edita e remove
- [x] persiste em SQLite
- (info) respostas em JSON: True
- (info) recusa e-mail duplicado com 4xx: True
- (info) código de criação: 201
- (info) código para duplicidade: 409
- (info) recusa e-mail inválido: True
- (info) métodos usados pelo front-end: ['DELETE', 'POST', 'PUT']
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "POST /api/usuarios",
   "resultado": "201 {\"id\":1,\"nome\":\"Ana Teste\",\"email\":\"ana.teste@exemplo.com\",\"telefone\":null,\"criado_em\":\"2026-09-28 18:56:43\"}"
  },
  {
   "passo": "POST duplicado",
   "resultado": "409 {\"erro\":\"Ja existe um usuario com este email.\"}"
  },
  {
   "passo": "POST e-mail inválido",
   "resultado": "400 {\"erro\":\"Dados invalidos.\",\"detalhes\":[\"O campo \\\"email\\\" possui formato invalido.\"]}"
  },
  {
   "passo": "POST sem campos",
   "resultado": "400 {\"erro\":\"Dados invalidos.\",\"detalhes\":[\"O campo \\\"nome\\\" e obrigatorio.\",\"O campo \\\"email\\\" e obrigatorio.\"]}"
  },
  {
   "passo": "PUT/PATCH /api/usuarios/1",
   "resultado": "200 {\"id\":1,\"nome\":\"Ana Atualizada\",\"email\":\"ana.teste@exemplo.com\",\"telefone\":null,\"criado_em\":\"2026-09-28 18:56:43\"}"
  },
  {
   "passo": "DELETE /api/usuarios/1",
   "resultado": "204 "
  }
 ],
 "evidencias": {
  "porta": 57005,
  "rotas encontradas no código": [
   "DELETE /api/usuarios/:id",
   "GET /api/usuarios",
   "GET /api/usuarios/:id",
   "POST /api/usuarios",
   "PUT /api/usuarios/:id"
  ],
  "rota": "/api/usuarios",
  "status": {
   "criar": 201,
   "duplicado": 409,
   "email_invalido": 400,
   "sem_campos": 400,
   "atualizar": 200,
   "remover": 204,
   "campos": [
    "birthDate",
    "birth_date",
    "birthdate",
    "dataNascimento",
    "data_nascimento",
    "dateOfBirth",
    "dob",
    "email",
    "name",
    "nascimento",
    "nome"
   ]
  },
  "arquivos de banco criados": [
   "usuarios.db"
  ]
 }
}
```
</details>

## nivel3-claude-t2

- Instalação: ok — npm install ok
- [x] cria usuário
- [x] lista usuários
- [x] atualiza usuário
- [x] remove usuário
- [x] serve interface no navegador
- [x] front-end cadastra, edita e remove
- [x] persiste em SQLite
- (info) respostas em JSON: True
- (info) recusa e-mail duplicado com 4xx: True
- (info) código de criação: 201
- (info) código para duplicidade: 409
- (info) recusa e-mail inválido: True
- (info) métodos usados pelo front-end: ['DELETE', 'POST', 'PUT']
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "POST /api/users",
   "resultado": "201 {\"id\":1,\"name\":\"Ana Teste\",\"email\":\"ana.teste@exemplo.com\",\"created_at\":\"2026-09-28 18:56:45\"}"
  },
  {
   "passo": "POST duplicado",
   "resultado": "409 {\"error\":\"Ja existe um usuario com este email.\"}"
  },
  {
   "passo": "POST e-mail inválido",
   "resultado": "400 {\"error\":\"O campo \\\"email\\\" possui formato invalido.\"}"
  },
  {
   "passo": "POST sem campos",
   "resultado": "400 {\"error\":\"O campo \\\"name\\\" e obrigatorio. O campo \\\"email\\\" e obrigatorio.\"}"
  },
  {
   "passo": "PUT/PATCH /api/users/1",
   "resultado": "200 {\"id\":1,\"name\":\"Ana Atualizada\",\"email\":\"ana.teste@exemplo.com\",\"created_at\":\"2026-09-28 18:56:45\"}"
  },
  {
   "passo": "DELETE /api/users/1",
   "resultado": "204 "
  }
 ],
 "evidencias": {
  "porta": 44315,
  "rotas encontradas no código": [
   "DELETE /api/users/:id",
   "GET /api/users",
   "GET /api/users/:id",
   "POST /api/users",
   "PUT /api/users/:id"
  ],
  "rota": "/api/users",
  "status": {
   "criar": 201,
   "duplicado": 409,
   "email_invalido": 400,
   "sem_campos": 400,
   "atualizar": 200,
   "remover": 204,
   "campos": [
    "birthDate",
    "birth_date",
    "birthdate",
    "dataNascimento",
    "data_nascimento",
    "dateOfBirth",
    "dob",
    "email",
    "name",
    "nascimento",
    "nome"
   ]
  },
  "arquivos de banco criados": [
   "data/database.sqlite"
  ]
 }
}
```
</details>

## nivel3-claude-t3

- Instalação: ok — npm install ok
- [x] cria usuário
- [x] lista usuários
- [x] atualiza usuário
- [x] remove usuário
- [x] serve interface no navegador
- [x] front-end cadastra, edita e remove
- [x] persiste em SQLite
- (info) respostas em JSON: True
- (info) recusa e-mail duplicado com 4xx: True
- (info) código de criação: 201
- (info) código para duplicidade: 409
- (info) recusa e-mail inválido: True
- (info) métodos usados pelo front-end: ['DELETE', 'POST', 'PUT']
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "POST /api/users",
   "resultado": "201 {\"id\":1,\"name\":\"Ana Teste\",\"email\":\"ana.teste@exemplo.com\",\"phone\":null,\"created_at\":\"2026-09-28 18:56:48\"}"
  },
  {
   "passo": "POST duplicado",
   "resultado": "409 {\"error\":\"Ja existe um usuario com esse email.\"}"
  },
  {
   "passo": "POST e-mail inválido",
   "resultado": "400 {\"errors\":[\"O campo \\\"email\\\" e obrigatorio e deve ser um email valido.\"]}"
  },
  {
   "passo": "POST sem campos",
   "resultado": "400 {\"errors\":[\"O campo \\\"name\\\" e obrigatorio e deve ter ao menos 2 caracteres.\",\"O campo \\\"email\\\" e obrigatorio e deve ser um email valido.\"]}"
  },
  {
   "passo": "PUT/PATCH /api/users/1",
   "resultado": "200 {\"id\":1,\"name\":\"Ana Atualizada\",\"email\":\"ana.teste@exemplo.com\",\"phone\":null,\"created_at\":\"2026-09-28 18:56:48\"}"
  },
  {
   "passo": "DELETE /api/users/1",
   "resultado": "204 "
  }
 ],
 "evidencias": {
  "porta": 52869,
  "rotas encontradas no código": [
   "DELETE /api/users/:id",
   "GET /api/users/",
   "GET /api/users/:id",
   "POST /api/users/",
   "PUT /api/users/:id"
  ],
  "rota": "/api/users",
  "status": {
   "criar": 201,
   "duplicado": 409,
   "email_invalido": 400,
   "sem_campos": 400,
   "atualizar": 200,
   "remover": 204,
   "campos": [
    "birthDate",
    "birth_date",
    "birthdate",
    "dataNascimento",
    "data_nascimento",
    "dateOfBirth",
    "dob",
    "email",
    "name",
    "nascimento",
    "nome"
   ]
  },
  "arquivos de banco criados": [
   "database.sqlite"
  ]
 }
}
```
</details>

## nivel3-gemini-t1

- Instalação: ok — npm install ok
- [x] cria usuário
- [x] lista usuários
- [x] atualiza usuário
- [x] remove usuário
- [x] serve interface no navegador
- [x] front-end cadastra, edita e remove
- [x] persiste em SQLite
- (info) respostas em JSON: True
- (info) recusa e-mail duplicado com 4xx: True
- (info) código de criação: 201
- (info) código para duplicidade: 400
- (info) recusa e-mail inválido: False
- (info) métodos usados pelo front-end: ['DELETE', 'POST', 'PUT']
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "POST /api/users",
   "resultado": "201 {\"id\":1,\"name\":\"Ana Teste\",\"email\":\"ana.teste@exemplo.com\"}"
  },
  {
   "passo": "POST duplicado",
   "resultado": "400 {\"error\":\"Erro ao cadastrar. Email pode já estar em uso.\"}"
  },
  {
   "passo": "POST e-mail inválido",
   "resultado": "201 {\"id\":2,\"name\":\"Ana Teste\",\"email\":\"email-invalido\"}"
  },
  {
   "passo": "POST sem campos",
   "resultado": "400 {\"error\":\"Nome e email são obrigatórios.\"}"
  },
  {
   "passo": "PUT/PATCH /api/users/1",
   "resultado": "200 {\"message\":\"Usuário atualizado com sucesso.\"}"
  },
  {
   "passo": "DELETE /api/users/1",
   "resultado": "200 {\"message\":\"Usuário removido com sucesso.\"}"
  }
 ],
 "evidencias": {
  "porta": 3000,
  "rotas encontradas no código": [
   "DELETE /api/users/:id",
   "GET /api/users",
   "POST /api/users",
   "PUT /api/users/:id"
  ],
  "rota": "/api/users",
  "status": {
   "criar": 201,
   "duplicado": 400,
   "email_invalido": 201,
   "sem_campos": 400,
   "atualizar": 200,
   "remover": 200,
   "campos": [
    "birthDate",
    "birth_date",
    "birthdate",
    "dataNascimento",
    "data_nascimento",
    "dateOfBirth",
    "dob",
    "email",
    "name",
    "nascimento",
    "nome"
   ]
  },
  "arquivos de banco criados": [
   "database.sqlite"
  ]
 }
}
```
</details>

## nivel3-gemini-t2

- Instalação: ok — npm install ok
- [x] cria usuário
- [x] lista usuários
- [x] atualiza usuário
- [x] remove usuário
- [x] serve interface no navegador
- [x] front-end cadastra, edita e remove
- [x] persiste em SQLite
- (info) respostas em JSON: True
- (info) recusa e-mail duplicado com 4xx: False
- (info) código de criação: 201
- (info) código para duplicidade: 500
- (info) recusa e-mail inválido: False
- (info) métodos usados pelo front-end: ['DELETE', 'POST', 'PUT']
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "POST /api/users",
   "resultado": "201 {\"id\":1,\"name\":\"Ana Teste\",\"email\":\"ana.teste@exemplo.com\"}"
  },
  {
   "passo": "POST duplicado",
   "resultado": "500 {\"error\":\"SQLITE_CONSTRAINT: UNIQUE constraint failed: users.email\"}"
  },
  {
   "passo": "POST e-mail inválido",
   "resultado": "201 {\"id\":2,\"name\":\"Ana Teste\",\"email\":\"email-invalido\"}"
  },
  {
   "passo": "POST sem campos",
   "resultado": "400 {\"error\":\"Nome e email são obrigatórios.\"}"
  },
  {
   "passo": "PUT/PATCH /api/users/1",
   "resultado": "200 {\"message\":\"Usuário atualizado com sucesso.\"}"
  },
  {
   "passo": "DELETE /api/users/1",
   "resultado": "200 {\"message\":\"Usuário removido com sucesso.\"}"
  }
 ],
 "evidencias": {
  "porta": 3000,
  "rotas encontradas no código": [
   "DELETE /api/users/:id",
   "GET /api/users",
   "POST /api/users",
   "PUT /api/users/:id"
  ],
  "rota": "/api/users",
  "status": {
   "criar": 201,
   "duplicado": 500,
   "email_invalido": 201,
   "sem_campos": 400,
   "atualizar": 200,
   "remover": 200,
   "campos": [
    "birthDate",
    "birth_date",
    "birthdate",
    "dataNascimento",
    "data_nascimento",
    "dateOfBirth",
    "dob",
    "email",
    "name",
    "nascimento",
    "nome"
   ]
  },
  "arquivos de banco criados": [
   "database.sqlite"
  ]
 }
}
```
</details>

## nivel3-gemini-t3

- Instalação: ok — npm install ok
- [x] cria usuário
- [x] lista usuários
- [x] atualiza usuário
- [x] remove usuário
- [x] serve interface no navegador
- [x] front-end cadastra, edita e remove
- [x] persiste em SQLite
- (info) respostas em JSON: True
- (info) recusa e-mail duplicado com 4xx: True
- (info) código de criação: 201
- (info) código para duplicidade: 400
- (info) recusa e-mail inválido: False
- (info) métodos usados pelo front-end: ['DELETE', 'POST', 'PUT']
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "POST /api/users",
   "resultado": "201 {\"id\":1,\"name\":\"Ana Teste\",\"email\":\"ana.teste@exemplo.com\"}"
  },
  {
   "passo": "POST duplicado",
   "resultado": "400 {\"error\":\"SQLITE_CONSTRAINT: UNIQUE constraint failed: users.email\"}"
  },
  {
   "passo": "POST e-mail inválido",
   "resultado": "201 {\"id\":2,\"name\":\"Ana Teste\",\"email\":\"email-invalido\"}"
  },
  {
   "passo": "POST sem campos",
   "resultado": "400 {\"error\":\"Nome e email são obrigatórios.\"}"
  },
  {
   "passo": "PUT/PATCH /api/users/1",
   "resultado": "200 {\"message\":\"Usuário atualizado com sucesso.\"}"
  },
  {
   "passo": "DELETE /api/users/1",
   "resultado": "200 {\"message\":\"Usuário removido com sucesso.\"}"
  }
 ],
 "evidencias": {
  "porta": 3000,
  "rotas encontradas no código": [
   "DELETE /api/users/:id",
   "GET /api/users",
   "POST /api/users",
   "PUT /api/users/:id"
  ],
  "rota": "/api/users",
  "status": {
   "criar": 201,
   "duplicado": 400,
   "email_invalido": 201,
   "sem_campos": 400,
   "atualizar": 200,
   "remover": 200,
   "campos": [
    "birthDate",
    "birth_date",
    "birthdate",
    "dataNascimento",
    "data_nascimento",
    "dateOfBirth",
    "dob",
    "email",
    "name",
    "nascimento",
    "nome"
   ]
  },
  "arquivos de banco criados": [
   "database.sqlite"
  ]
 }
}
```
</details>

## nivel3-gpt-t1

- Instalação: ok — npm install ok
- [x] cria usuário
- [x] lista usuários
- [x] atualiza usuário
- [x] remove usuário
- [x] serve interface no navegador
- [x] front-end cadastra, edita e remove
- [x] persiste em SQLite
- (info) respostas em JSON: True
- (info) recusa e-mail duplicado com 4xx: True
- (info) código de criação: 201
- (info) código para duplicidade: 409
- (info) recusa e-mail inválido: True
- (info) métodos usados pelo front-end: ['DELETE', 'POST', 'PUT']
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "POST /api/usuarios",
   "resultado": "201 {\"id\":1,\"nome\":\"Ana Teste\",\"email\":\"ana.teste@exemplo.com\",\"criadoEm\":\"2026-09-28 18:56:58\",\"atualizadoEm\":\"2026-09-28 18:56:58\"}"
  },
  {
   "passo": "POST duplicado",
   "resultado": "409 {\"mensagem\":\"Já existe um usuário cadastrado com este e-mail.\"}"
  },
  {
   "passo": "POST e-mail inválido",
   "resultado": "400 {\"mensagem\":\"Os dados informados são inválidos.\",\"erros\":[\"Informe um endereço de e-mail válido.\"]}"
  },
  {
   "passo": "POST sem campos",
   "resultado": "400 {\"mensagem\":\"Os dados informados são inválidos.\",\"erros\":[\"O nome é obrigatório.\",\"O e-mail é obrigatório.\"]}"
  },
  {
   "passo": "PUT/PATCH /api/usuarios/1",
   "resultado": "200 {\"id\":1,\"nome\":\"Ana Atualizada\",\"email\":\"ana.teste@exemplo.com\",\"criadoEm\":\"2026-09-28 18:56:58\",\"atualizadoEm\":\"2026-09-28 18:56:58\"}"
  },
  {
   "passo": "DELETE /api/usuarios/1",
   "resultado": "204 "
  }
 ],
 "evidencias": {
  "porta": 51475,
  "rotas encontradas no código": [
   "DELETE /api/usuarios/:id",
   "GET /api/usuarios",
   "GET /api/usuarios/:id",
   "POST /api/usuarios",
   "PUT /api/usuarios/:id"
  ],
  "rota": "/api/usuarios",
  "status": {
   "criar": 201,
   "duplicado": 409,
   "email_invalido": 400,
   "sem_campos": 400,
   "atualizar": 200,
   "remover": 204,
   "campos": [
    "birthDate",
    "birth_date",
    "birthdate",
    "dataNascimento",
    "data_nascimento",
    "dateOfBirth",
    "dob",
    "email",
    "name",
    "nascimento",
    "nome"
   ]
  },
  "arquivos de banco criados": [
   "usuarios.sqlite"
  ]
 }
}
```
</details>

## nivel3-gpt-t2

- Instalação: ok — npm install ok
- [x] cria usuário
- [x] lista usuários
- [x] atualiza usuário
- [x] remove usuário
- [x] serve interface no navegador
- [x] front-end cadastra, edita e remove
- [x] persiste em SQLite
- (info) respostas em JSON: True
- (info) recusa e-mail duplicado com 4xx: True
- (info) código de criação: 201
- (info) código para duplicidade: 409
- (info) recusa e-mail inválido: True
- (info) métodos usados pelo front-end: ['DELETE', 'POST', 'PUT']
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "POST /api/users",
   "resultado": "201 {\"id\":1,\"name\":\"Ana Teste\",\"email\":\"ana.teste@exemplo.com\",\"createdAt\":\"2026-09-28T18:57:00.562Z\",\"updatedAt\":\"2026-09-28T18:57:00.562Z\"}"
  },
  {
   "passo": "POST duplicado",
   "resultado": "409 {\"error\":\"Já existe um usuário cadastrado com este e-mail.\",\"fields\":{\"email\":\"Este e-mail já está cadastrado.\"}}"
  },
  {
   "passo": "POST e-mail inválido",
   "resultado": "400 {\"error\":\"Dados inválidos.\",\"fields\":{\"email\":\"Informe um endereço de e-mail válido.\"}}"
  },
  {
   "passo": "POST sem campos",
   "resultado": "400 {\"error\":\"Dados inválidos.\",\"fields\":{\"name\":\"O nome é obrigatório.\",\"email\":\"O e-mail é obrigatório.\"}}"
  },
  {
   "passo": "PUT/PATCH /api/users/1",
   "resultado": "200 {\"id\":1,\"name\":\"Ana Atualizada\",\"email\":\"ana.teste@exemplo.com\",\"createdAt\":\"2026-09-28T18:57:00.562Z\",\"updatedAt\":\"2026-09-28T18:57:00.571Z\"}"
  },
  {
   "passo": "DELETE /api/users/1",
   "resultado": "204 "
  }
 ],
 "evidencias": {
  "porta": 43539,
  "rotas encontradas no código": [
   "DELETE /api/users/:id",
   "GET /api/health",
   "GET /api/users",
   "GET /api/users/:id",
   "POST /api/users",
   "PUT /api/users/:id"
  ],
  "rota": "/api/users",
  "status": {
   "criar": 201,
   "duplicado": 409,
   "email_invalido": 400,
   "sem_campos": 400,
   "atualizar": 200,
   "remover": 204,
   "campos": [
    "birthDate",
    "birth_date",
    "birthdate",
    "dataNascimento",
    "data_nascimento",
    "dateOfBirth",
    "dob",
    "email",
    "name",
    "nascimento",
    "nome"
   ]
  },
  "arquivos de banco criados": [
   "data/usuarios.db"
  ]
 }
}
```
</details>

## nivel3-gpt-t3

- Instalação: ok — npm install ok
- [x] cria usuário
- [x] lista usuários
- [x] atualiza usuário
- [x] remove usuário
- [x] serve interface no navegador
- [x] front-end cadastra, edita e remove
- [x] persiste em SQLite
- (info) respostas em JSON: True
- (info) recusa e-mail duplicado com 4xx: True
- (info) código de criação: 201
- (info) código para duplicidade: 409
- (info) recusa e-mail inválido: True
- (info) métodos usados pelo front-end: ['DELETE', 'POST', 'PUT']
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "POST /api/users",
   "resultado": "201 {\"dados\":{\"id\":1,\"nome\":\"Ana Teste\",\"email\":\"ana.teste@exemplo.com\",\"createdAt\":\"2026-09-28 18:57:01\",\"updatedAt\":\"2026-09-28 18:57:01\"}}"
  },
  {
   "passo": "POST duplicado",
   "resultado": "409 {\"erro\":\"Já existe um usuário cadastrado com este e-mail.\"}"
  },
  {
   "passo": "POST e-mail inválido",
   "resultado": "400 {\"erro\":\"Dados de usuário inválidos.\",\"detalhes\":[\"Informe um endereço de e-mail válido.\"]}"
  },
  {
   "passo": "POST sem campos",
   "resultado": "400 {\"erro\":\"Dados de usuário inválidos.\",\"detalhes\":[\"O nome deve possuir pelo menos 2 caracteres.\",\"O e-mail é obrigatório.\"]}"
  },
  {
   "passo": "PUT/PATCH /api/users/1",
   "resultado": "200 {\"dados\":{\"id\":1,\"nome\":\"Ana Atualizada\",\"email\":\"ana.teste@exemplo.com\",\"createdAt\":\"2026-09-28 18:57:01\",\"updatedAt\":\"2026-09-28 18:57:01\"}}"
  },
  {
   "passo": "DELETE /api/users/1",
   "resultado": "204 "
  }
 ],
 "evidencias": {
  "porta": 40975,
  "rotas encontradas no código": [],
  "rota": "/api/users",
  "status": {
   "criar": 201,
   "duplicado": 409,
   "email_invalido": 400,
   "sem_campos": 400,
   "atualizar": 200,
   "remover": 204,
   "campos": [
    "birthDate",
    "birth_date",
    "birthdate",
    "dataNascimento",
    "data_nascimento",
    "dateOfBirth",
    "dob",
    "email",
    "name",
    "nascimento",
    "nome"
   ]
  },
  "arquivos de banco criados": [
   "data/users.db"
  ]
 }
}
```
</details>

## nivel3-groq-t1

- Instalação: ok — npm install ok
- [x] cria usuário
- [x] lista usuários
- [x] atualiza usuário
- [x] remove usuário
- [x] serve interface no navegador
- [x] front-end cadastra, edita e remove
- [x] persiste em SQLite
- (info) respostas em JSON: True
- (info) recusa e-mail duplicado com 4xx: True
- (info) código de criação: 201
- (info) código para duplicidade: 409
- (info) recusa e-mail inválido: False
- (info) métodos usados pelo front-end: ['DELETE', 'POST', 'PUT']
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "POST /api/users",
   "resultado": "201 {\"id\":1}"
  },
  {
   "passo": "POST duplicado",
   "resultado": "409 {\"error\":\"Email já cadastrado\"}"
  },
  {
   "passo": "POST e-mail inválido",
   "resultado": "201 {\"id\":2}"
  },
  {
   "passo": "POST sem campos",
   "resultado": "400 {\"error\":\"Nome e email são obrigatórios\"}"
  },
  {
   "passo": "PUT/PATCH /api/users/1",
   "resultado": "200 {\"message\":\"Usuário atualizado\"}"
  },
  {
   "passo": "DELETE /api/users/1",
   "resultado": "200 {\"message\":\"Usuário removido\"}"
  }
 ],
 "evidencias": {
  "porta": 43675,
  "rotas encontradas no código": [
   "DELETE /users/:id",
   "GET /users",
   "GET /users/:id",
   "POST /users",
   "PUT /users/:id"
  ],
  "rota": "/api/users",
  "status": {
   "criar": 201,
   "duplicado": 409,
   "email_invalido": 201,
   "sem_campos": 400,
   "atualizar": 200,
   "remover": 200,
   "campos": [
    "birthDate",
    "birth_date",
    "birthdate",
    "dataNascimento",
    "data_nascimento",
    "dateOfBirth",
    "dob",
    "email",
    "name",
    "nascimento",
    "nome"
   ]
  },
  "arquivos de banco criados": [
   "data.db"
  ]
 }
}
```
</details>

## nivel3-groq-t2

- Instalação: ok — npm install ok
- [x] cria usuário
- [x] lista usuários
- [x] atualiza usuário
- [x] remove usuário
- [x] serve interface no navegador
- [x] front-end cadastra, edita e remove
- [x] persiste em SQLite
- (info) respostas em JSON: True
- (info) recusa e-mail duplicado com 4xx: True
- (info) código de criação: 201
- (info) código para duplicidade: 409
- (info) recusa e-mail inválido: False
- (info) métodos usados pelo front-end: ['DELETE', 'POST', 'PUT']
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "POST /api/users",
   "resultado": "201 {\"id\":1,\"name\":\"Ana Teste\",\"email\":\"ana.teste@exemplo.com\"}"
  },
  {
   "passo": "POST duplicado",
   "resultado": "409 {\"error\":\"E‑mail já cadastrado\"}"
  },
  {
   "passo": "POST e-mail inválido",
   "resultado": "201 {\"id\":2,\"name\":\"Ana Teste\",\"email\":\"email-invalido\"}"
  },
  {
   "passo": "POST sem campos",
   "resultado": "400 {\"error\":\"Nome e e‑mail são obrigatórios\"}"
  },
  {
   "passo": "PUT/PATCH /api/users/1",
   "resultado": "200 {\"id\":1,\"name\":\"Ana Atualizada\",\"email\":\"ana.teste@exemplo.com\",\"age\":null}"
  },
  {
   "passo": "DELETE /api/users/1",
   "resultado": "204 "
  }
 ],
 "evidencias": {
  "porta": 48983,
  "rotas encontradas no código": [
   "DELETE /api/users/:id",
   "GET /api/users",
   "GET /api/users/:id",
   "POST /api/users",
   "PUT /api/users/:id"
  ],
  "rota": "/api/users",
  "status": {
   "criar": 201,
   "duplicado": 409,
   "email_invalido": 201,
   "sem_campos": 400,
   "atualizar": 200,
   "remover": 204,
   "campos": [
    "birthDate",
    "birth_date",
    "birthdate",
    "dataNascimento",
    "data_nascimento",
    "dateOfBirth",
    "dob",
    "email",
    "name",
    "nascimento",
    "nome"
   ]
  },
  "arquivos de banco criados": [
   "users.db"
  ]
 }
}
```
</details>

## nivel3-groq-t3

- Instalação: ok — npm install ok
- Problemas: o servidor não subiu (dependência ausente: cors; exige correção manual)
- Completude sugerida: None (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [],
 "evidencias": {}
}
```
</details>

## nivel4-claude-t1

- Instalação: ok — npm install ok
- [x] listagem pública
- [x] bloqueia escrita sem autenticação
- [x] login com usuário e senha
- [x] escrita autenticada funciona
- [x] senha guardada com hash e sal
- [x] persiste em SQLite
- (info) mesma resposta para usuário inexistente e senha errada: False
- Segurança sugerida: {'senha': 1, 'segredo': 0.5, 'sessão': 0.5, 'tempo de login': 0, 'sem credencial padrão': 1} → soma 3.0
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "POST /api/records/ sem autenticação (json)",
   "resultado": "401 {\"error\":\"Autenticacao necessaria.\"}"
  },
  {
   "passo": "POST /api/records/ sem autenticação (form)",
   "resultado": "401 {\"error\":\"Autenticacao necessaria.\"}"
  },
  {
   "passo": "cadastro de usuário",
   "resultado": "/api/auth/register (json): 201 {\"id\":1,\"username\":\"usuario_teste\"}"
  },
  {
   "passo": "POST /api/records/ autenticado (json)",
   "resultado": "201 {\"id\":1,\"title\":\"Registro Teste\",\"description\":\"teste\",\"owner_id\":1,\"created_at\":\"2026-09-28 18:57:12\",\"updated_at\":\"2026-09-28 18:57:12\"}"
  },
  {
   "passo": "requisição forjada: cookie de sessão sem token CSRF",
   "resultado": "201 {\"id\":2,\"title\":\"Forjado\",\"description\":\"teste\",\"owner_id\":1,\"created_at\":\"2026-09-28 18:57:12\",\"updated_at\":\"2026-09-28 18:57:12\"}"
  }
 ],
 "evidencias": {
  "porta": 42821,
  "rotas encontradas no código": [
   "DELETE /api/records/:id",
   "GET /api/auth/me",
   "GET /api/records/",
   "GET /api/records/:id",
   "POST /api/auth/login",
   "POST /api/auth/logout",
   "POST /api/auth/register",
   "POST /api/records/",
   "PUT /api/records/:id"
  ],
  "codigo": {
   "hash de senha": [
    "bcrypt",
    "scrypt"
   ],
   "segredo fixo no código": [],
   "segredo com valor padrão": [
    [
     "JWT_SECRET",
     "dev-secret-nao-use-em-producao"
    ]
   ],
   "login: verificação fictícia quando o usuário não existe": false,
   "front-end guarda token em localStorage": false,
   "sameSite no código": [
    "lax"
   ],
   "credencial fixa no código": []
  },
  "rota de listagem": "/api/records",
  "sessão obtida com": "usuário cadastrado no teste",
  "sessão": "cookie",
  "Set-Cookie do login": [
   "auth_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwidXNlcm5hbWUiOiJ1c3VhcmlvX3Rlc3RlIiwiaWF0IjoxNzkwNjIxODMyLCJleHAiOjE3OTA2MjkwMzJ9.OPbr4Dn_-ASLk3suQotv67YLzOzFexA0gwKh-nJb6a4; Max-Age=7200; Path=/; Expires=Mon, 28 Sep 2026 20:57:12 GMT; HttpOnly; SameSite=Lax"
  ],
  "token CSRF encontrado": false,
  "requisição forjada sem token": "aceita",
  "cookie": {
   "httpOnly": true,
   "sameSite": "lax"
  },
  "credencial padrão que funcionou": null,
  "arquivos de banco criados": [
   "data.sqlite"
  ]
 }
}
```
</details>

## nivel4-claude-t2

- Instalação: ok — npm install ok
- [x] listagem pública
- [x] bloqueia escrita sem autenticação
- [x] login com usuário e senha
- [x] escrita autenticada funciona
- [x] senha guardada com hash e sal
- [x] persiste em SQLite
- (info) mesma resposta para usuário inexistente e senha errada: True
- Segurança sugerida: {'senha': 1, 'segredo': 0.5, 'sessão': 0.5, 'tempo de login': 0, 'sem credencial padrão': 1} → soma 3.0
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "POST /api/records/ sem autenticação (json)",
   "resultado": "401 {\"error\":\"Autenticação necessária. Faça login.\"}"
  },
  {
   "passo": "POST /api/records/ sem autenticação (form)",
   "resultado": "401 {\"error\":\"Autenticação necessária. Faça login.\"}"
  },
  {
   "passo": "cadastro de usuário",
   "resultado": "/api/auth/register (json): 201 {\"id\":1,\"username\":\"usuario_teste\"}"
  },
  {
   "passo": "POST /api/records/ autenticado (json)",
   "resultado": "201 {\"id\":1,\"title\":\"Registro Teste\",\"description\":\"teste\",\"created_by\":1,\"created_at\":\"2026-09-28 18:57:14\",\"updated_at\":\"2026-09-28 18:57:14\"}"
  },
  {
   "passo": "requisição forjada: cookie de sessão sem token CSRF",
   "resultado": "201 {\"id\":2,\"title\":\"Forjado\",\"description\":\"teste\",\"created_by\":1,\"created_at\":\"2026-09-28 18:57:14\",\"updated_at\":\"2026-09-28 18:57:14\"}"
  }
 ],
 "evidencias": {
  "porta": 34307,
  "rotas encontradas no código": [
   "DELETE /api/records/:id",
   "GET /api/auth/me",
   "GET /api/records/",
   "GET /api/records/:id",
   "POST /api/auth/login",
   "POST /api/auth/logout",
   "POST /api/auth/register",
   "POST /api/records/",
   "PUT /api/records/:id"
  ],
  "codigo": {
   "hash de senha": [
    "bcrypt",
    "bcryptjs"
   ],
   "segredo fixo no código": [],
   "segredo com valor padrão": [
    [
     "JWT_SECRET",
     "dev-secret-nao-use-em-producao"
    ]
   ],
   "login: verificação fictícia quando o usuário não existe": false,
   "front-end guarda token em localStorage": false,
   "sameSite no código": [
    "lax"
   ],
   "credencial fixa no código": []
  },
  "rota de listagem": "/api/records",
  "sessão obtida com": "usuário cadastrado no teste",
  "sessão": "cookie",
  "Set-Cookie do login": [
   "token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsInVzZXJuYW1lIjoidXN1YXJpb190ZXN0ZSIsImlhdCI6MTc5MDYyMTgzNCwiZXhwIjoxNzkwNjI5MDM0fQ.Fib7L0BD4H_AD6qshq2ORTu8AICOReWjkfyzY646jq8; Max-Age=7200; Path=/; Expires=Mon, 28 Sep 2026 20:57:14 GMT; HttpOnly; SameSite=Lax"
  ],
  "token CSRF encontrado": false,
  "requisição forjada sem token": "aceita",
  "cookie": {
   "httpOnly": true,
   "sameSite": "lax"
  },
  "credencial padrão que funcionou": null,
  "arquivos de banco criados": [
   "data.sqlite"
  ]
 }
}
```
</details>

## nivel4-claude-t3

- Instalação: ok — npm install ok
- [x] listagem pública
- [x] bloqueia escrita sem autenticação
- [x] login com usuário e senha
- [x] escrita autenticada funciona
- [x] senha guardada com hash e sal
- [x] persiste em SQLite
- (info) mesma resposta para usuário inexistente e senha errada: True
- Segurança sugerida: {'senha': 1, 'segredo': 0.5, 'sessão': 0.5, 'tempo de login': 0, 'sem credencial padrão': 1} → soma 3.0
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "POST /api/records/ sem autenticação (json)",
   "resultado": "401 {\"error\":\"Token de autenticacao ausente.\"}"
  },
  {
   "passo": "POST /api/records/ sem autenticação (form)",
   "resultado": "401 {\"error\":\"Token de autenticacao ausente.\"}"
  },
  {
   "passo": "cadastro de usuário",
   "resultado": "/api/auth/register (json): 201 …1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwidXNlcm5hbWUiOiJ1c3VhcmlvX3Rlc3RlIiwiaWF0IjoxNzkwNjIxODM4LCJleHAiOjE3OTA2MjkwMzh9.1XeMbTClSDK9SFDBZxtSLUagIaEW-ySblq5eiM1VYLo\"}"
  },
  {
   "passo": "POST /api/records/ autenticado (json)",
   "resultado": "201 {\"id\":1,\"title\":\"Registro Teste\",\"description\":\"teste\",\"owner_id\":1,\"created_at\":\"2026-09-28 18:57:18\",\"updated_at\":\"2026-09-28 18:57:18\"}"
  }
 ],
 "evidencias": {
  "porta": 56299,
  "rotas encontradas no código": [
   "DELETE /api/records/:id",
   "GET /api/records/",
   "GET /api/records/:id",
   "POST /api/auth/login",
   "POST /api/auth/register",
   "POST /api/records/",
   "PUT /api/records/:id"
  ],
  "codigo": {
   "hash de senha": [
    "bcrypt"
   ],
   "segredo fixo no código": [],
   "segredo com valor padrão": [
    [
     "JWT_SECRET",
     "chave-padrao-insegura-trocar-em-producao"
    ]
   ],
   "login: verificação fictícia quando o usuário não existe": false,
   "front-end guarda token em localStorage": true,
   "sameSite no código": [],
   "credencial fixa no código": []
  },
  "rota de listagem": "/api/records",
  "sessão obtida com": "usuário cadastrado no teste",
  "sessão": "token Bearer",
  "Set-Cookie do login": [],
  "token CSRF encontrado": false,
  "requisição forjada sem token": "não se aplica (token Bearer)",
  "cookie": null,
  "credencial padrão que funcionou": null,
  "arquivos de banco criados": [
   "data.sqlite"
  ]
 }
}
```
</details>

## nivel4-gemini-t1

- Instalação: ok — npm install ok
- [x] listagem pública
- [x] bloqueia escrita sem autenticação
- [x] login com usuário e senha
- [x] escrita autenticada funciona
- [x] senha guardada com hash e sal
- [x] persiste em SQLite
- (info) mesma resposta para usuário inexistente e senha errada: True
- Segurança sugerida: {'senha': 1, 'segredo': 0, 'sessão': 0.5, 'tempo de login': 0, 'sem credencial padrão': 0} → soma 1.5
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "POST /api/users sem autenticação (json)",
   "resultado": "401 {\"error\":\"Acesso negado. Token não fornecido.\"}"
  },
  {
   "passo": "POST /api/users sem autenticação (form)",
   "resultado": "401 {\"error\":\"Acesso negado. Token não fornecido.\"}"
  },
  {
   "passo": "cadastro de usuário",
   "resultado": "nenhuma rota de cadastro no sistema"
  },
  {
   "passo": "POST /api/users autenticado (json)",
   "resultado": "201 {\"id\":2,\"username\":\"registro_teste\"}"
  }
 ],
 "evidencias": {
  "porta": 3000,
  "rotas encontradas no código": [
   "DELETE /api/users/:id",
   "GET /api/users",
   "POST /api/login",
   "POST /api/users",
   "PUT /api/users/:id"
  ],
  "codigo": {
   "hash de senha": [
    "bcrypt"
   ],
   "segredo fixo no código": [
    [
     "JWT_SECRET",
     "super_secret_key_change_in_production"
    ]
   ],
   "segredo com valor padrão": [],
   "login: verificação fictícia quando o usuário não existe": false,
   "front-end guarda token em localStorage": true,
   "sameSite no código": [],
   "credencial fixa no código": [
    "admin123",
    "admin"
   ]
  },
  "rota de listagem": "/api/users",
  "sessão obtida com": "credencial padrão do sistema",
  "sessão": "token Bearer",
  "Set-Cookie do login": [],
  "token CSRF encontrado": false,
  "requisição forjada sem token": "não se aplica (token Bearer)",
  "cookie": null,
  "credencial padrão que funcionou": "admin/admin123",
  "arquivos de banco criados": [
   "database.sqlite"
  ]
 }
}
```
</details>

## nivel4-gemini-t2

- Instalação: ok — npm install ok
- [x] listagem pública
- [x] bloqueia escrita sem autenticação
- [x] login com usuário e senha
- [x] escrita autenticada funciona
- [x] senha guardada com hash e sal
- [x] persiste em SQLite
- (info) mesma resposta para usuário inexistente e senha errada: True
- Segurança sugerida: {'senha': 1, 'segredo': 0, 'sessão': 0, 'tempo de login': 0, 'sem credencial padrão': 0} → soma 1
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "POST /api/users sem autenticação (json)",
   "resultado": "401 {\"error\":\"Acesso negado. Faça login.\"}"
  },
  {
   "passo": "POST /api/users sem autenticação (form)",
   "resultado": "401 {\"error\":\"Acesso negado. Faça login.\"}"
  },
  {
   "passo": "cadastro de usuário",
   "resultado": "nenhuma rota de cadastro no sistema"
  },
  {
   "passo": "POST /api/users autenticado (json)",
   "resultado": "201 {\"id\":2,\"username\":\"registro_teste\"}"
  },
  {
   "passo": "requisição forjada: cookie de sessão sem token CSRF",
   "resultado": "201 {\"id\":3,\"username\":\"forjado\"}"
  }
 ],
 "evidencias": {
  "porta": 3000,
  "rotas encontradas no código": [
   "DELETE /api/users/:id",
   "GET /api/me",
   "GET /api/users",
   "POST /api/login",
   "POST /api/logout",
   "POST /api/users",
   "PUT /api/users/:id"
  ],
  "codigo": {
   "hash de senha": [
    "bcrypt"
   ],
   "segredo fixo no código": [
    [
     "SECRET_KEY",
     "chave_secreta_super_segura_para_jwt"
    ]
   ],
   "segredo com valor padrão": [],
   "login: verificação fictícia quando o usuário não existe": false,
   "front-end guarda token em localStorage": false,
   "sameSite no código": [],
   "credencial fixa no código": [
    "admin123",
    "admin"
   ]
  },
  "rota de listagem": "/api/users",
  "sessão obtida com": "credencial padrão do sistema",
  "sessão": "cookie",
  "Set-Cookie do login": [
   "token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwidXNlcm5hbWUiOiJhZG1pbiIsImlhdCI6MTc5MDYyMTg0NCwiZXhwIjoxNzkwNjI1NDQ0fQ.sRv0Ml7irfX9eHbrwtT60rBqE1_90whVu1hrGibeAQ0; Path=/; HttpOnly"
  ],
  "token CSRF encontrado": false,
  "requisição forjada sem token": "aceita",
  "cookie": {
   "httpOnly": true,
   "sameSite": null
  },
  "credencial padrão que funcionou": "admin/admin123",
  "arquivos de banco criados": [
   "database.sqlite"
  ]
 }
}
```
</details>

## nivel4-gemini-t3

- Instalação: ok — npm install ok
- [x] listagem pública
- [x] bloqueia escrita sem autenticação
- [x] login com usuário e senha
- [x] escrita autenticada funciona
- [x] senha guardada com hash e sal
- [x] persiste em SQLite
- (info) mesma resposta para usuário inexistente e senha errada: True
- Segurança sugerida: {'senha': 1, 'segredo': 0, 'sessão': 0, 'tempo de login': 0, 'sem credencial padrão': 0} → soma 1
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "POST /api/users sem autenticação (json)",
   "resultado": "401 {\"error\":\"Acesso negado. Faça login.\"}"
  },
  {
   "passo": "POST /api/users sem autenticação (form)",
   "resultado": "401 {\"error\":\"Acesso negado. Faça login.\"}"
  },
  {
   "passo": "cadastro de usuário",
   "resultado": "nenhuma rota de cadastro no sistema"
  },
  {
   "passo": "POST /api/users autenticado (json)",
   "resultado": "201 {\"id\":2,\"username\":\"registro_teste\"}"
  },
  {
   "passo": "requisição forjada: cookie de sessão sem token CSRF",
   "resultado": "201 {\"id\":3,\"username\":\"forjado\"}"
  }
 ],
 "evidencias": {
  "porta": 3000,
  "rotas encontradas no código": [
   "DELETE /api/users/:id",
   "GET /api/me",
   "GET /api/users",
   "POST /api/login",
   "POST /api/logout",
   "POST /api/users",
   "PUT /api/users/:id"
  ],
  "codigo": {
   "hash de senha": [
    "bcrypt"
   ],
   "segredo fixo no código": [
    [
     "JWT_SECRET",
     "chave_secreta_super_segura_para_jwt_123"
    ]
   ],
   "segredo com valor padrão": [],
   "login: verificação fictícia quando o usuário não existe": false,
   "front-end guarda token em localStorage": false,
   "sameSite no código": [],
   "credencial fixa no código": [
    "admin123",
    "admin"
   ]
  },
  "rota de listagem": "/api/users",
  "sessão obtida com": "credencial padrão do sistema",
  "sessão": "cookie",
  "Set-Cookie do login": [
   "token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwidXNlcm5hbWUiOiJhZG1pbiIsImlhdCI6MTc5MDYyMTg0OCwiZXhwIjoxNzkwNjI5MDQ4fQ.s2D7f1fbcrfaxfS1tViddWsBWFatWL_WkhRQ73Js-R8; Path=/; HttpOnly"
  ],
  "token CSRF encontrado": false,
  "requisição forjada sem token": "aceita",
  "cookie": {
   "httpOnly": true,
   "sameSite": null
  },
  "credencial padrão que funcionou": "admin/admin123",
  "arquivos de banco criados": [
   "database.sqlite"
  ]
 }
}
```
</details>

## nivel4-gpt-t1

- Instalação: ok — npm install ok
- [x] listagem pública
- [x] bloqueia escrita sem autenticação
- [x] login com usuário e senha
- [x] escrita autenticada funciona
- [x] senha guardada com hash e sal
- [x] persiste em SQLite
- (info) mesma resposta para usuário inexistente e senha errada: True
- (info) limite de tentativas de login: ativado durante o teste de credenciais padrão
- Segurança sugerida: {'senha': 1, 'segredo': 1, 'sessão': 1, 'tempo de login': 1, 'sem credencial padrão': 1} → soma 5
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "POST /api/users sem autenticação (json)",
   "resultado": "401 {\"error\":\"Autenticação necessária.\"}"
  },
  {
   "passo": "POST /api/users sem autenticação (form)",
   "resultado": "401 {\"error\":\"Autenticação necessária.\"}"
  },
  {
   "passo": "cadastro de usuário",
   "resultado": "script create-admin (cli): 200 Usuário inicial \"usuario_teste\" criado com sucesso.\nBanco SQLite: /home/claude/resultados-testes/projetos/nivel4-gpt-t1/data/app.db"
  },
  {
   "passo": "POST /api/users autenticado (json)",
   "resultado": "201 {\"message\":\"Usuário cadastrado.\",\"user\":{\"id\":2,\"username\":\"registro_teste\",\"created_at\":\"2026-09-28T18:57:30.826Z\",\"updated_at\":\"2026-09-28T18:57:30.826Z\"}}"
  },
  {
   "passo": "requisição forjada: cookie de sessão sem token CSRF",
   "resultado": "403 {\"error\":\"Token CSRF inválido ou ausente.\"}"
  }
 ],
 "evidencias": {
  "porta": 51049,
  "rotas encontradas no código": [
   "DELETE /api/users/:id",
   "GET /api/session",
   "GET /api/users",
   "POST /api/login",
   "POST /api/logout",
   "POST /api/users",
   "PUT /api/users/:id"
  ],
  "codigo": {
   "hash de senha": [
    "scrypt"
   ],
   "segredo fixo no código": [],
   "segredo com valor padrão": [],
   "login: verificação fictícia quando o usuário não existe": true,
   "front-end guarda token em localStorage": false,
   "sameSite no código": [
    "lax",
    "lax"
   ],
   "credencial fixa no código": []
  },
  "rota de listagem": "/api/users",
  "sessão obtida com": "usuário cadastrado no teste",
  "sessão": "cookie",
  "Set-Cookie do login": [
   "session_token=F1C-ZodQ_XAbSWUMRfEf18n1UjSEjYa2scqQvW6XomE; Max-Age=28800; Path=/; Expires=Tue, 29 Sep 2026 02:57:30 GMT; HttpOnly; SameSite=Lax"
  ],
  "token CSRF encontrado": true,
  "requisição forjada sem token": "bloqueada",
  "cookie": {
   "httpOnly": true,
   "sameSite": "lax"
  },
  "credencial padrão que funcionou": null,
  "arquivos de banco criados": [
   "data/app.db"
  ]
 }
}
```
</details>

## nivel4-gpt-t2

- Instalação: ok — npm install ok
- [x] listagem pública
- [x] bloqueia escrita sem autenticação
- [x] login com usuário e senha
- [x] escrita autenticada funciona
- [x] senha guardada com hash e sal
- [x] persiste em SQLite
- (info) mesma resposta para usuário inexistente e senha errada: True
- (info) limite de tentativas de login: ativado durante o teste de credenciais padrão
- Segurança sugerida: {'senha': 1, 'segredo': 1, 'sessão': 1, 'tempo de login': 1, 'sem credencial padrão': 1} → soma 5
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "POST /api/users sem autenticação (json)",
   "resultado": "401 {\"error\":\"Autenticação necessária.\"}"
  },
  {
   "passo": "POST /api/users sem autenticação (form)",
   "resultado": "401 {\"error\":\"Autenticação necessária.\"}"
  },
  {
   "passo": "cadastro de usuário",
   "resultado": "nenhuma rota de cadastro no sistema"
  },
  {
   "passo": "POST /api/users autenticado (json)",
   "resultado": "201 {\"user\":{\"id\":2,\"username\":\"registro_teste\",\"displayName\":\"Registro Teste\",\"createdAt\":\"2026-09-28T18:57:33.582Z\",\"updatedAt\":\"2026-09-28T18:57:33.582Z\"}}"
  },
  {
   "passo": "requisição forjada: cookie de sessão sem token CSRF",
   "resultado": "403 {\"error\":\"Token CSRF ausente ou inválido.\"}"
  }
 ],
 "evidencias": {
  "porta": 38405,
  "rotas encontradas no código": [
   "DELETE /api/users/:id",
   "GET /api/auth/me",
   "GET /api/users",
   "POST /api/auth/login",
   "POST /api/auth/logout",
   "POST /api/users",
   "PUT /api/users/:id"
  ],
  "codigo": {
   "hash de senha": [
    "scrypt"
   ],
   "segredo fixo no código": [],
   "segredo com valor padrão": [],
   "login: verificação fictícia quando o usuário não existe": true,
   "front-end guarda token em localStorage": false,
   "sameSite no código": [
    "strict",
    "strict"
   ],
   "credencial fixa no código": []
  },
  "rota de listagem": "/api/users",
  "sessão obtida com": "usuário cadastrado no teste",
  "sessão": "cookie",
  "Set-Cookie do login": [
   "session_token=-fBXFq3YVFsqHbt_71ydcJn4hmVvI8kDp5gC5AQzwv4; Max-Age=28800; Path=/; Expires=Tue, 29 Sep 2026 02:57:33 GMT; HttpOnly; SameSite=Strict"
  ],
  "token CSRF encontrado": true,
  "requisição forjada sem token": "bloqueada",
  "cookie": {
   "httpOnly": true,
   "sameSite": "strict"
  },
  "credencial padrão que funcionou": null,
  "arquivos de banco criados": [
   "data/app.db"
  ]
 }
}
```
</details>

## nivel4-gpt-t3

- Instalação: ok — npm install ok
- [x] listagem pública
- [x] bloqueia escrita sem autenticação
- [x] login com usuário e senha
- [x] escrita autenticada funciona
- [x] senha guardada com hash e sal
- [x] persiste em SQLite
- (info) mesma resposta para usuário inexistente e senha errada: True
- (info) limite de tentativas de login: ativado durante o teste de credenciais padrão
- Segurança sugerida: {'senha': 1, 'segredo': 1, 'sessão': 1, 'tempo de login': 1, 'sem credencial padrão': 1} → soma 5
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "POST /users sem autenticação (json)",
   "resultado": "302 <p>Found. Redirecting to /login</p>"
  },
  {
   "passo": "POST /users sem autenticação (form)",
   "resultado": "302 <p>Found. Redirecting to /login</p>"
  },
  {
   "passo": "cadastro de usuário",
   "resultado": "script create-admin (cli): 200 Usuário inicial criado com sucesso.\nID: 1\nUsuário: usuario_teste\nBanco: /home/claude/resultados-testes/projetos/nivel4-gpt-t3/data/app.db"
  },
  {
   "passo": "POST /users autenticado (form)",
   "resultado": "302 <p>Found. Redirecting to /admin?ok=created</p>"
  },
  {
   "passo": "requisição forjada: cookie de sessão sem token CSRF",
   "resultado": "403 …      Voltar\n      </a>\n    </div>\n  \n  </main>\n\n  <footer class=\"site-footer\">\n    <p>Sistema de cadastro com Node.js e SQLite.</p>\n  </footer>\n</body>\n</html>"
  }
 ],
 "evidencias": {
  "porta": 56355,
  "rotas encontradas no código": [
   "GET /",
   "GET /admin",
   "GET /login",
   "GET /users/:id/edit",
   "GET /users/new",
   "POST /login",
   "POST /logout",
   "POST /users",
   "POST /users/:id/delete",
   "POST /users/:id/edit"
  ],
  "codigo": {
   "hash de senha": [
    "scrypt"
   ],
   "segredo fixo no código": [],
   "segredo com valor padrão": [],
   "login: verificação fictícia quando o usuário não existe": true,
   "front-end guarda token em localStorage": false,
   "sameSite no código": [
    "strict",
    "strict"
   ],
   "credencial fixa no código": [
    "password",
    "password",
    "password",
    "password"
   ]
  },
  "rota de listagem": "/",
  "sessão obtida com": "usuário cadastrado no teste",
  "sessão": "cookie",
  "Set-Cookie do login": [
   "session=GEw4zEFndw3sX9lhq9d1AoyIHcg5b3YvwTOhYmkTRS4; Max-Age=28800; Path=/; Expires=Tue, 29 Sep 2026 02:57:35 GMT; HttpOnly; SameSite=Strict"
  ],
  "token CSRF encontrado": true,
  "requisição forjada sem token": "bloqueada",
  "cookie": {
   "httpOnly": true,
   "sameSite": "strict"
  },
  "credencial padrão que funcionou": null,
  "arquivos de banco criados": [
   "data/app.db"
  ]
 }
}
```
</details>

## nivel4-groq-t1

- Instalação: ok — npm install ok
- Problemas: o servidor não subiu (dependência ausente: dotenv; exige correção manual)
- Completude sugerida: None (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [],
 "evidencias": {}
}
```
</details>

## nivel4-groq-t2

- Instalação: ok — npm install ok
- [x] listagem pública
- [x] bloqueia escrita sem autenticação
- [x] login com usuário e senha
- [x] escrita autenticada funciona
- [x] senha guardada com hash e sal
- [x] persiste em SQLite
- (info) mesma resposta para usuário inexistente e senha errada: True
- Segurança sugerida: {'senha': 1, 'segredo': 0.5, 'sessão': 0, 'tempo de login': 0, 'sem credencial padrão': 1} → soma 2.5
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "POST /api/users/ sem autenticação (json)",
   "resultado": "401 {\"error\":\"Token ausente. Autentique-se.\"}"
  },
  {
   "passo": "POST /api/users/ sem autenticação (form)",
   "resultado": "401 {\"error\":\"Token ausente. Autentique-se.\"}"
  },
  {
   "passo": "cadastro de usuário",
   "resultado": "/api/auth/register (json): 201 {\"id\":1,\"name\":\"Usuario Teste\",\"email\":\"usuario.teste@exemplo.com\"}"
  },
  {
   "passo": "POST /api/users/ autenticado (json)",
   "resultado": "201 {\"id\":2,\"name\":\"Registro Teste\",\"email\":\"registro.teste@exemplo.com\"}"
  },
  {
   "passo": "requisição forjada: cookie de sessão sem token CSRF",
   "resultado": "201 {\"id\":3,\"name\":\"Forjado\",\"email\":\"forjado@exemplo.com\"}"
  }
 ],
 "evidencias": {
  "porta": 38785,
  "rotas encontradas no código": [
   "DELETE /api/users/:id",
   "GET /",
   "GET /api/users/",
   "POST /api/auth/login",
   "POST /api/auth/logout",
   "POST /api/auth/register",
   "POST /api/users/",
   "PUT /api/users/:id"
  ],
  "codigo": {
   "hash de senha": [
    "bcrypt"
   ],
   "segredo fixo no código": [],
   "segredo com valor padrão": [
    [
     "JWT_SECRET",
     "supersecretkey"
    ]
   ],
   "login: verificação fictícia quando o usuário não existe": false,
   "front-end guarda token em localStorage": false,
   "sameSite no código": [],
   "credencial fixa no código": []
  },
  "rota de listagem": "/api/users",
  "sessão obtida com": "usuário cadastrado no teste",
  "sessão": "cookie",
  "Set-Cookie do login": [
   "token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwiZW1haWwiOiJ1c3VhcmlvLnRlc3RlQGV4ZW1wbG8uY29tIiwiaWF0IjoxNzkwNjIxODYyLCJleHAiOjE3OTA2MjU0NjJ9.CY_-DA58wpOYWYzgnvU_Fs3ZN_LZ-CJzSme41sh_4LA; Max-Age=3600; Path=/; Expires=Mon, 28 Sep 2026 19:57:42 GMT; HttpOnly"
  ],
  "token CSRF encontrado": false,
  "requisição forjada sem token": "aceita",
  "cookie": {
   "httpOnly": true,
   "sameSite": null
  },
  "credencial padrão que funcionou": null,
  "arquivos de banco criados": [
   "data.db"
  ]
 }
}
```
</details>

## nivel4-groq-t3

- Instalação: ok — npm install ok
- [x] listagem pública
- [x] bloqueia escrita sem autenticação
- [x] login com usuário e senha
- [x] escrita autenticada funciona
- [x] senha guardada com hash e sal
- [x] persiste em SQLite
- (info) mesma resposta para usuário inexistente e senha errada: True
- Segurança sugerida: {'senha': 1, 'segredo': 0.5, 'sessão': 0.5, 'tempo de login': 0, 'sem credencial padrão': 1} → soma 3.0
- Completude sugerida: 5 (requisitos não atendidos: nenhum)

<details><summary>Passos e evidências</summary>

```json
{
 "passos": [
  {
   "passo": "POST /api/profiles sem autenticação (json)",
   "resultado": "401 {\"error\":\"Token ausente\"}"
  },
  {
   "passo": "POST /api/profiles sem autenticação (form)",
   "resultado": "401 {\"error\":\"Token ausente\"}"
  },
  {
   "passo": "cadastro de usuário",
   "resultado": "/api/register (json): 201 {\"message\":\"Usuário criado\",\"userId\":1}"
  },
  {
   "passo": "POST /api/profiles autenticado (json)",
   "resultado": "201 {\"message\":\"Perfil criado\",\"profileId\":1}"
  }
 ],
 "evidencias": {
  "porta": 53717,
  "rotas encontradas no código": [
   "DELETE /api/profiles/:id",
   "GET /",
   "GET /api/profiles",
   "POST /api/login",
   "POST /api/profiles",
   "POST /api/register",
   "PUT /api/profiles/:id"
  ],
  "codigo": {
   "hash de senha": [
    "bcrypt"
   ],
   "segredo fixo no código": [],
   "segredo com valor padrão": [
    [
     "JWT_SECRET",
     "super_secret_key_change_me"
    ]
   ],
   "login: verificação fictícia quando o usuário não existe": false,
   "front-end guarda token em localStorage": true,
   "sameSite no código": [],
   "credencial fixa no código": []
  },
  "rota de listagem": "/api/profiles",
  "sessão obtida com": "usuário cadastrado no teste",
  "sessão": "token Bearer",
  "Set-Cookie do login": [],
  "token CSRF encontrado": false,
  "requisição forjada sem token": "não se aplica (token Bearer)",
  "cookie": null,
  "credencial padrão que funcionou": null,
  "arquivos de banco criados": [
   "data.sqlite"
  ]
 }
}
```
</details>
