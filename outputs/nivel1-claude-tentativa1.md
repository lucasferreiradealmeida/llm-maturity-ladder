<!--
nivel: 1 - CRUD com persistencia em banco
provider: claude
model: claude-sonnet-5
tentativa: 1
temperature: 0.2
timestamp: 2026-08-18T22:36:16.927Z
metadata: {"model":"claude-sonnet-5","usage":{"input_tokens":381,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"cache_creation":{"ephemeral_5m_input_tokens":0,"ephemeral_1h_input_tokens":0},"output_tokens":7421,"output_tokens_details":{"thinking_tokens":442},"service_tier":"standard","inference_geo":"global"},"stop_reason":"end_turn"}
-->

## Prompt enviado
```
Voce e um(a) engenheiro(a) de software responsavel por implementar o sistema
descrito abaixo. Gere o codigo completo, pronto para rodar, incluindo
instrucoes de execucao (como instalar dependencias e como rodar).

TAREFA:
Crie uma aplicacao de linha de comando (CLI) que permita cadastrar, listar,
atualizar e remover usuarios (nome, e-mail, data de nascimento), persistindo
os dados em um banco de dados relacional (SQLite), incluindo o script de
criacao do schema. Valide o formato do e-mail e impeca duplicidade de
e-mail. Trate erros de entrada de forma amigavel.

RESTRICOES:
- Linguagem: Node.js (JavaScript).
- Nao use frameworks alem dos estritamente necessarios para a tarefa.
- Nao peca esclarecimentos: assuma decisoes razoaveis e documente-as em comentarios.
- Entregue todos os arquivos necessarios, indicando o nome do arquivo antes de cada bloco de codigo.
```

## Resposta do modelo

# Solução: CLI de Gerenciamento de Usuários (Node.js + SQLite)

## Decisões de projeto (documentadas)

- **Banco de dados**: SQLite via `better-sqlite3` (API síncrona, evita complexidade de callbacks/promises para uma CLI simples, sem necessidade de framework ORM).
- **Parsing de argumentos**: implementado manualmente (sem `commander`/`yargs`), pois a tarefa pede o mínimo de dependências.
- **Validação de e-mail**: regex pragmática (cobre a grande maioria dos casos reais, sem exigir libs externas).
- **Data de nascimento**: formato `YYYY-MM-DD`, validada com `Date` nativo.
- **Duplicidade de e-mail**: garantida tanto por `UNIQUE` no schema quanto por checagem prévia amigável na aplicação.
- **Estrutura**: separação em `db.js` (conexão/schema), `validators.js`, `userService.js` (regras de negócio) e `cli.js` (interface).

---

## Estrutura de arquivos

```
user-cli/
├── package.json
├── schema.sql
├── src/
│   ├── db.js
│   ├── validators.js
│   ├── userService.js
│   └── cli.js
└── README.md
```

---

### `package.json`

```json
{
  "name": "user-cli",
  "version": "1.0.0",
  "description": "CLI para cadastro, listagem, atualizacao e remocao de usuarios usando SQLite",
  "main": "src/cli.js",
  "bin": {
    "user-cli": "src/cli.js"
  },
  "scripts": {
    "start": "node src/cli.js"
  },
  "license": "MIT",
  "dependencies": {
    "better-sqlite3": "^11.3.0"
  }
}
```

---

### `schema.sql`

```sql
-- Script de criacao do schema do banco de dados.
-- E executado automaticamente na inicializacao (db.js),
-- mas tambem pode ser rodado manualmente com:
--   sqlite3 usuarios.db < schema.sql

CREATE TABLE IF NOT EXISTS usuarios (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nome            TEXT NOT NULL,
    email           TEXT NOT NULL UNIQUE,
    data_nascimento TEXT NOT NULL, -- formato YYYY-MM-DD
    criado_em       TEXT NOT NULL DEFAULT (datetime('now')),
    atualizado_em   TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Indice extra para buscas por email (alem da constraint UNIQUE, que ja cria indice,
-- mas deixamos explicito para clareza do schema)
CREATE UNIQUE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios (email);
```

---

### `src/db.js`

```javascript
'use strict';

/**
 * Modulo responsavel por abrir a conexao com o SQLite
 * e garantir que o schema exista (idempotente).
 */

const path = require('path');
const fs = require('fs');
const Database = require('better-sqlite3');

// Caminho do arquivo de banco de dados (fica na raiz do projeto)
const DB_PATH = path.join(__dirname, '..', 'usuarios.db');
const SCHEMA_PATH = path.join(__dirname, '..', 'schema.sql');

function criarConexao() {
  const db = new Database(DB_PATH);

  // Boas praticas de configuracao para SQLite
  db.pragma('journal_mode = WAL');
  db.pragma('foreign_keys = ON');

  // Aplica o schema (CREATE TABLE IF NOT EXISTS...) sempre que a app inicia
  const schemaSql = fs.readFileSync(SCHEMA_PATH, 'utf8');
  db.exec(schemaSql);

  return db;
}

module.exports = { criarConexao, DB_PATH };
```

---

### `src/validators.js`

```javascript
'use strict';

/**
 * Funcoes de validacao de dados de entrada do usuario.
 * Cada funcao lanca um Error com mensagem amigavel em caso de falha.
 */

// Regex pragmatica para validacao de e-mail (cobre a maioria dos casos reais)
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function validarNome(nome) {
  if (!nome || typeof nome !== 'string' || nome.trim().length === 0) {
    throw new Error('O nome e obrigatorio e nao pode ser vazio.');
  }
  if (nome.trim().length > 150) {
    throw new Error('O nome deve ter no maximo 150 caracteres.');
  }
  return nome.trim();
}

function validarEmail(email) {
  if (!email || typeof email !== 'string' || email.trim().length === 0) {
    throw new Error('O e-mail e obrigatorio.');
  }
  const emailNormalizado = email.trim().toLowerCase();
  if (!EMAIL_REGEX.test(emailNormalizado)) {
    throw new Error(`E-mail invalido: "${email}". Use um formato como usuario@dominio.com`);
  }
  return emailNormalizado;
}

function validarDataNascimento(data) {
  if (!data || typeof data !== 'string') {
    throw new Error('A data de nascimento e obrigatoria (formato YYYY-MM-DD).');
  }
  const formatoOk = /^\d{4}-\d{2}-\d{2}$/.test(data);
  if (!formatoOk) {
    throw new Error(`Data de nascimento invalida: "${data}". Use o formato YYYY-MM-DD (ex: 1990-05-20).`);
  }

  const [ano, mes, dia] = data.split('-').map(Number);
  const dataObj = new Date(Date.UTC(ano, mes - 1, dia));

  const dataValida =
    dataObj.getUTCFullYear() === ano &&
    dataObj.getUTCMonth() === mes - 1 &&
    dataObj.getUTCDate() === dia;

  if (!dataValida) {
    throw new Error(`Data de nascimento invalida: "${data}" nao corresponde a uma data real.`);
  }

  const hoje = new Date();
  if (dataObj > hoje) {
    throw new Error('A data de nascimento nao pode ser no futuro.');
  }

  return data;
}

function validarId(id) {
  const idNum = Number(id);
  if (!id || Number.isNaN(idNum) || !Number.isInteger(idNum) || idNum <= 0) {
    throw new Error(`ID invalido: "${id}". Informe um numero inteiro positivo.`);
  }
  return idNum;
}

module.exports = {
  validarNome,
  validarEmail,
  validarDataNascimento,
  validarId,
};
```

---

### `src/userService.js`

```javascript
'use strict';

/**
 * Camada de regras de negocio / acesso a dados para usuarios.
 * Isola o SQL do restante da aplicacao.
 */

const {
  validarNome,
  validarEmail,
  validarDataNascimento,
  validarId,
} = require('./validators');

class UserService {
  constructor(db) {
    this.db = db;
  }

  /** Verifica se ja existe um usuario com o e-mail informado (opcionalmente ignorando um id) */
  emailJaExiste(email, ignorarId = null) {
    const stmt = ignorarId
      ? this.db.prepare('SELECT id FROM usuarios WHERE email = ? AND id != ?')
      : this.db.prepare('SELECT id FROM usuarios WHERE email = ?');

    const row = ignorarId ? stmt.get(email, ignorarId) : stmt.get(email);
    return !!row;
  }

  cadastrar({ nome, email, dataNascimento }) {
    const nomeValido = validarNome(nome);
    const emailValido = validarEmail(email);
    const dataValida = validarDataNascimento(dataNascimento);

    if (this.emailJaExiste(emailValido)) {
      throw new Error(`Ja existe um usuario cadastrado com o e-mail "${emailValido}".`);
    }

    const stmt = this.db.prepare(`
      INSERT INTO usuarios (nome, email, data_nascimento)
      VALUES (?, ?, ?)
    `);

    try {
      const info = stmt.run(nomeValido, emailValido, dataValida);
      return this.buscarPorId(info.lastInsertRowid);
    } catch (err) {
      // Protecao extra caso a checagem acima tenha uma condicao de corrida
      if (err.message.includes('UNIQUE')) {
        throw new Error(`Ja existe um usuario cadastrado com o e-mail "${emailValido}".`);
      }
      throw err;
    }
  }

  listar() {
    const stmt = this.db.prepare('SELECT * FROM usuarios ORDER BY id ASC');
    return stmt.all();
  }

  buscarPorId(id) {
    const idValido = validarId(id);
    const stmt = this.db.prepare('SELECT * FROM usuarios WHERE id = ?');
    const usuario = stmt.get(idValido);
    if (!usuario) {
      throw new Error(`Usuario com ID ${idValido} nao encontrado.`);
    }
    return usuario;
  }

  atualizar(id, { nome, email, dataNascimento }) {
    const idValido = validarId(id);
    const usuarioAtual = this.buscarPorId(idValido); // lanca erro se nao existir

    const nomeFinal = nome !== undefined ? validarNome(nome) : usuarioAtual.nome;
    const emailFinal = email !== undefined ? validarEmail(email) : usuarioAtual.email;
    const dataFinal = dataNascimento !== undefined
      ? validarDataNascimento(dataNascimento)
      : usuarioAtual.data_nascimento;

    if (email !== undefined && this.emailJaExiste(emailFinal, idValido)) {
      throw new Error(`Ja existe outro usuario cadastrado com o e-mail "${emailFinal}".`);
    }

    const stmt = this.db.prepare(`
      UPDATE usuarios
      SET nome = ?, email = ?, data_nascimento = ?, atualizado_em = datetime('now')
      WHERE id = ?
    `);

    try {
      stmt.run(nomeFinal, emailFinal, dataFinal, idValido);
    } catch (err) {
      if (err.message.includes('UNIQUE')) {
        throw new Error(`Ja existe outro usuario cadastrado com o e-mail "${emailFinal}".`);
      }
      throw err;
    }

    return this.buscarPorId(idValido);
  }

  remover(id) {
    const idValido = validarId(id);
    this.buscarPorId(idValido); // lanca erro se nao existir

    const stmt = this.db.prepare('DELETE FROM usuarios WHERE id = ?');
    stmt.run(idValido);
    return true;
  }
}

module.exports = UserService;
```

---

### `src/cli.js`

```javascript
#!/usr/bin/env node
'use strict';

/**
 * Ponto de entrada da CLI.
 *
 * Comandos suportados:
 *   node src/cli.js add --nome "Fulano" --email "fulano@ex.com" --nascimento "1990-01-20"
 *   node src/cli.js list
 *   node src/cli.js update --id 1 [--nome ...] [--email ...] [--nascimento ...]
 *   node src/cli.js remove --id 1
 *   node src/cli.js help
 */

const { criarConexao } = require('./db');
const UserService = require('./userService');

// --- Parsing simples de argumentos no formato --chave valor ---
function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (token.startsWith('--')) {
      const chave = token.slice(2);
      const valor = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[i + 1] : true;
      args[chave] = valor;
      if (valor !== true) i += 1;
    }
  }
  return args;
}

function formatarUsuario(u) {
  return [
    `ID: ${u.id}`,
    `Nome: ${u.nome}`,
    `E-mail: ${u.email}`,
    `Nascimento: ${u.data_nascimento}`,
    `Criado em: ${u.criado_em}`,
    `Atualizado em: ${u.atualizado_em}`,
  ].join(' | ');
}

function imprimirAjuda() {
  console.log(`
Uso: node src/cli.js <comando> [opcoes]

Comandos disponiveis:
  add     --nome "Nome Completo" --email "email@dominio.com" --nascimento "YYYY-MM-DD"
              Cadastra um novo usuario.

  list
              Lista todos os usuarios cadastrados.

  update  --id <id> [--nome ...] [--email ...] [--nascimento ...]
              Atualiza um ou mais campos de um usuario existente.

  remove  --id <id>
              Remove um usuario pelo ID.

  help
              Exibe esta mensagem de ajuda.

Exemplos:
  node src/cli.js add --nome "Maria Silva" --email "maria@exemplo.com" --nascimento "1995-08-12"
  node src/cli.js list
  node src/cli.js update --id 1 --email "novo@exemplo.com"
  node src/cli.js remove --id 1
`);
}

function main() {
  const [, , comando, ...resto] = process.argv;
  const args = parseArgs(resto);

  if (!comando || comando === 'help' || args.help) {
    imprimirAjuda();
    return;
  }

  let db;
  try {
    db = criarConexao();
  } catch (err) {
    console.error('Erro fatal ao conectar ao banco de dados:', err.message);
    process.exitCode = 1;
    return;
  }

  const service = new UserService(db);

  try {
    switch (comando) {
      case 'add': {
        const novoUsuario = service.cadastrar({
          nome: args.nome,
          email: args.email,
          dataNascimento: args.nascimento,
        });
        console.log('Usuario cadastrado com sucesso:');
        console.log(formatarUsuario(novoUsuario));
        break;
      }

      case 'list': {
        const usuarios = service.listar();
        if (usuarios.length === 0) {
          console.log('Nenhum usuario cadastrado ainda.');
        } else {
          console.log(`Total de usuarios: ${usuarios.length}\n`);
          usuarios.forEach((u) => console.log(formatarUsuario(u)));
        }
        break;
      }

      case 'update': {
        if (!args.id) {
          throw new Error('Informe o --id do usuario que deseja atualizar.');
        }
        const usuarioAtualizado = service.atualizar(args.id, {
          nome: args.nome,
          email: args.email,
          dataNascimento: args.nascimento,
        });
        console.log('Usuario atualizado com sucesso:');
        console.log(formatarUsuario(usuarioAtualizado));
        break;
      }

      case 'remove': {
        if (!args.id) {
          throw new Error('Informe o --id do usuario que deseja remover.');
        }
        service.remover(args.id);
        console.log(`Usuario com ID ${args.id} removido com sucesso.`);
        break;
      }

      default: {
        console.error(`Comando desconhecido: "${comando}"`);
        imprimirAjuda();
        process.exitCode = 1;
      }
    }
  } catch (err) {
    // Tratamento amigavel de erros de entrada / regra de negocio
    console.error(`Erro: ${err.message}`);
    process.exitCode = 1;
  } finally {
    db.close();
  }
}

main();
```

---

### `README.md`

```markdown
# User CLI

Aplicacao de linha de comando para cadastrar, listar, atualizar e remover
usuarios (nome, e-mail e data de nascimento), persistindo os dados em um
banco SQLite local.

## Requisitos

- Node.js 18+ (recomendado)
- npm

## Instalacao

```bash
cd user-cli
npm install
```

Isso instalara a unica dependencia externa do projeto: `better-sqlite3`
(necessaria para persistencia em SQLite).

Ao instalar as dependencias, um arquivo `usuarios.db` sera criado
automaticamente na raiz do projeto na primeira execucao, com o schema
definido em `schema.sql`.

## Uso

Todos os comandos sao executados via `node src/cli.js <comando> [opcoes]`.

### Ajuda

```bash
node src/cli.js help
```

### Cadastrar usuario

```bash
node src/cli.js add --nome "Maria Silva" --email "maria@exemplo.com" --nascimento "1995-08-12"
```

### Listar usuarios

```bash
node src/cli.js list
```

### Atualizar usuario

Pode-se atualizar um ou mais campos por vez, informando o `--id`:

```bash
node src/cli.js update --id 1 --email "novo.email@exemplo.com"
node src/cli.js update --id 1 --nome "Maria Souza" --nascimento "1995-08-13"
```

### Remover usuario

```bash
node src/cli.js remove --id 1
```

## Validacoes implementadas

- **Nome**: obrigatorio, nao vazio, ate 150 caracteres.
- **E-mail**: obrigatorio, formato validado por regex, normalizado para
  minusculas, e verificado quanto a duplicidade (tanto na aplicacao quanto
  via constraint `UNIQUE` no banco).
- **Data de nascimento**: obrigatoria, formato `YYYY-MM-DD`, deve
  corresponder a uma data real e nao pode estar no futuro.
- **ID** (para update/remove): deve ser um numero inteiro positivo
  correspondente a um usuario existente.

Erros de validacao e de regra de negocio (ex.: e-mail duplicado, usuario
inexistente) sao exibidos de forma amigavel no terminal, sem stack trace,
e o processo termina com codigo de saida 1.

## Estrutura do projeto

```
user-cli/
├── package.json
├── schema.sql          # Script de criacao das tabelas
├── usuarios.db          # Criado automaticamente (SQLite)
├── README.md
└── src/
    ├── db.js            # Conexao e inicializacao do banco
    ├── validators.js    # Validacoes de entrada
    ├── userService.js   # Regras de negocio / SQL
    └── cli.js            # Interface de linha de comando
```

## Resetando o banco de dados

Para recomecar do zero, basta apagar o arquivo `usuarios.db`
(e os arquivos `usuarios.db-wal` / `usuarios.db-shm`, se existirem):

```bash
rm usuarios.db usuarios.db-wal usuarios.db-shm
```

O schema sera recriado automaticamente na proxima execucao de qualquer
comando da CLI.
```

---

## Resumo de como rodar rapidamente

```bash
cd user-cli
npm install
node src/cli.js add --nome "Joao Souza" --email "joao@exemplo.com" --nascimento "1988-03-15"
node src/cli.js list
node src/cli.js update --id 1 --nome "Joao Pedro Souza"
node src/cli.js remove --id 1
```