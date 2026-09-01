<!--
nivel: 1 - CRUD com persistencia em banco
provider: claude
model: claude-sonnet-5
tentativa: 2
temperature: 0.2
timestamp: 2026-08-18T22:37:15.531Z
metadata: {"model":"claude-sonnet-5","usage":{"input_tokens":381,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"cache_creation":{"ephemeral_5m_input_tokens":0,"ephemeral_1h_input_tokens":0},"output_tokens":8660,"output_tokens_details":{"thinking_tokens":908},"service_tier":"standard","inference_geo":"global"},"stop_reason":"end_turn"}
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

# Solução

Aplicação CLI em Node.js puro, usando apenas a dependência estritamente necessária para acesso ao SQLite (`better-sqlite3`, já que o Node não possui um driver SQLite nativo estável em todas as versões LTS). Toda a interação com o usuário (menu, parsing de argumentos, prompts) é feita com módulos nativos (`readline`, `process.argv`), sem frameworks de CLI (sem commander/inquirer/yargs).

## Decisões de projeto (documentadas também em comentários no código)

- **better-sqlite3**: driver síncrono, simples, sem callbacks/promises, ideal para CLI simples.
- Suporta dois modos de uso:
  - **Modo com argumentos** (não interativo): `node index.js add --name "..." --email "..." --birthdate "YYYY-MM-DD"`
  - **Modo interativo** (menu): `node index.js` sem argumentos.
- E-mail validado por regex (RFC simplificada, cobre 99% dos casos reais).
- Data de nascimento validada no formato `YYYY-MM-DD`, precisa ser uma data real e não pode ser no futuro.
- Duplicidade de e-mail é garantida em dois níveis: constraint `UNIQUE` no banco (garantia final) + verificação prévia amigável na aplicação.
- Banco de dados: arquivo `data.db` criado automaticamente na primeira execução, a partir do `schema.sql`.
- Erros de entrada (validação, duplicidade, id inexistente) são capturados e exibidos como mensagens amigáveis, nunca stack trace cru.

---

### `package.json`

```json
{
  "name": "cli-usuarios-sqlite",
  "version": "1.0.0",
  "description": "CLI para CRUD de usuarios persistido em SQLite",
  "main": "index.js",
  "type": "commonjs",
  "scripts": {
    "start": "node index.js"
  },
  "dependencies": {
    "better-sqlite3": "^11.3.0"
  }
}
```

---

### `schema.sql`

```sql
-- Schema do banco de dados de usuarios.
-- Executado automaticamente na inicializacao da aplicacao (ver src/db.js).

CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    email       TEXT NOT NULL UNIQUE,   -- garante nao duplicidade a nivel de banco
    birthdate   TEXT NOT NULL,          -- armazenado como TEXT no formato YYYY-MM-DD
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Indice extra para buscas rapidas por email (alem do UNIQUE, que ja cria indice,
-- mas deixamos explicito por clareza/documentacao).
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
```

---

### `src/db.js`

```javascript
'use strict';

/**
 * Modulo responsavel por abrir a conexao com o SQLite e garantir que o
 * schema exista antes de qualquer operacao.
 *
 * Decisao: usamos better-sqlite3 por ser sincrono e simples, evitando
 * a complexidade de callbacks/promises para uma CLI simples de CRUD.
 */

const path = require('path');
const fs = require('fs');
const Database = require('better-sqlite3');

const DB_PATH = path.join(__dirname, '..', 'data.db');
const SCHEMA_PATH = path.join(__dirname, '..', 'schema.sql');

function createConnection() {
  const db = new Database(DB_PATH);
  db.pragma('foreign_keys = ON');

  const schema = fs.readFileSync(SCHEMA_PATH, 'utf-8');
  db.exec(schema);

  return db;
}

module.exports = { createConnection, DB_PATH };
```

---

### `src/validators.js`

```javascript
'use strict';

/**
 * Funcoes de validacao de entrada do usuario.
 * Nao usamos bibliotecas externas: as regras sao simples o suficiente
 * para serem implementadas com regex/Date nativo.
 */

// Regex razoavel para e-mails (cobre a grande maioria dos casos reais,
// sem tentar implementar o RFC 5322 completo, que e desnecessariamente complexo).
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function isValidEmail(email) {
  if (typeof email !== 'string') return false;
  return EMAIL_REGEX.test(email.trim());
}

// Valida datas no formato estrito YYYY-MM-DD, verifica se e uma data
// real (ex: rejeita 2023-02-30) e se nao esta no futuro.
function isValidBirthdate(dateStr) {
  if (typeof dateStr !== 'string') return false;
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(dateStr.trim());
  if (!match) return false;

  const [, yearStr, monthStr, dayStr] = match;
  const year = Number(yearStr);
  const month = Number(monthStr);
  const day = Number(dayStr);

  const date = new Date(Date.UTC(year, month - 1, day));
  const isRealDate =
    date.getUTCFullYear() === year &&
    date.getUTCMonth() === month - 1 &&
    date.getUTCDate() === day;

  if (!isRealDate) return false;

  const today = new Date();
  const todayUTC = new Date(Date.UTC(today.getFullYear(), today.getMonth(), today.getDate()));
  if (date > todayUTC) return false; // data de nascimento nao pode ser futura

  return true;
}

function isNonEmptyString(value) {
  return typeof value === 'string' && value.trim().length > 0;
}

module.exports = { isValidEmail, isValidBirthdate, isNonEmptyString };
```

---

### `src/userRepository.js`

```javascript
'use strict';

/**
 * Camada de acesso a dados (repository) para usuarios.
 * Encapsula todas as queries SQL, mantendo a logica de CLI/validacao
 * separada da persistencia.
 */

const { isValidEmail, isValidBirthdate, isNonEmptyString } = require('./validators');

class ValidationError extends Error {}
class NotFoundError extends Error {}
class DuplicateEmailError extends Error {}

class UserRepository {
  constructor(db) {
    this.db = db;
  }

  _validate({ name, email, birthdate }) {
    if (!isNonEmptyString(name)) {
      throw new ValidationError('Nome e obrigatorio e nao pode ser vazio.');
    }
    if (!isValidEmail(email)) {
      throw new ValidationError(`E-mail invalido: "${email}".`);
    }
    if (!isValidBirthdate(birthdate)) {
      throw new ValidationError(
        `Data de nascimento invalida: "${birthdate}". Use o formato YYYY-MM-DD e uma data real, nao futura.`
      );
    }
  }

  create({ name, email, birthdate }) {
    this._validate({ name, email, birthdate });
    const normalizedEmail = email.trim().toLowerCase();

    const existing = this.getByEmail(normalizedEmail);
    if (existing) {
      throw new DuplicateEmailError(`Ja existe um usuario cadastrado com o e-mail "${normalizedEmail}".`);
    }

    try {
      const stmt = this.db.prepare(
        `INSERT INTO users (name, email, birthdate) VALUES (?, ?, ?)`
      );
      const info = stmt.run(name.trim(), normalizedEmail, birthdate.trim());
      return this.getById(info.lastInsertRowid);
    } catch (err) {
      if (String(err.message).includes('UNIQUE')) {
        throw new DuplicateEmailError(`Ja existe um usuario cadastrado com o e-mail "${normalizedEmail}".`);
      }
      throw err;
    }
  }

  list() {
    return this.db.prepare(`SELECT * FROM users ORDER BY id ASC`).all();
  }

  getById(id) {
    return this.db.prepare(`SELECT * FROM users WHERE id = ?`).get(id);
  }

  getByEmail(email) {
    return this.db
      .prepare(`SELECT * FROM users WHERE email = ?`)
      .get(email.trim().toLowerCase());
  }

  update(id, { name, email, birthdate }) {
    const current = this.getById(id);
    if (!current) {
      throw new NotFoundError(`Usuario com id ${id} nao encontrado.`);
    }

    const updated = {
      name: name !== undefined ? name : current.name,
      email: email !== undefined ? email : current.email,
      birthdate: birthdate !== undefined ? birthdate : current.birthdate,
    };

    this._validate(updated);
    const normalizedEmail = updated.email.trim().toLowerCase();

    const emailOwner = this.getByEmail(normalizedEmail);
    if (emailOwner && emailOwner.id !== id) {
      throw new DuplicateEmailError(`O e-mail "${normalizedEmail}" ja esta em uso por outro usuario.`);
    }

    try {
      this.db
        .prepare(
          `UPDATE users SET name = ?, email = ?, birthdate = ?, updated_at = datetime('now') WHERE id = ?`
        )
        .run(updated.name.trim(), normalizedEmail, updated.birthdate.trim(), id);
    } catch (err) {
      if (String(err.message).includes('UNIQUE')) {
        throw new DuplicateEmailError(`O e-mail "${normalizedEmail}" ja esta em uso por outro usuario.`);
      }
      throw err;
    }

    return this.getById(id);
  }

  remove(id) {
    const current = this.getById(id);
    if (!current) {
      throw new NotFoundError(`Usuario com id ${id} nao encontrado.`);
    }
    this.db.prepare(`DELETE FROM users WHERE id = ?`).run(id);
    return current;
  }
}

module.exports = { UserRepository, ValidationError, NotFoundError, DuplicateEmailError };
```

---

### `src/cli.js`

```javascript
'use strict';

/**
 * Interface de linha de comando.
 *
 * Suporta dois modos:
 *  1) Comandos diretos via argv: add | list | update | remove | help
 *  2) Modo interativo (menu), acionado quando nenhum comando e passado.
 *
 * Nao usamos bibliotecas de parsing de CLI (commander/yargs) para manter
 * a stack minima, conforme restricao do projeto.
 */

const readline = require('readline');
const {
  UserRepository,
  ValidationError,
  NotFoundError,
  DuplicateEmailError,
} = require('./userRepository');

function printUser(user) {
  console.log(
    `#${user.id} | Nome: ${user.name} | E-mail: ${user.email} | Nascimento: ${user.birthdate}`
  );
}

function handleKnownErrors(err) {
  if (
    err instanceof ValidationError ||
    err instanceof NotFoundError ||
    err instanceof DuplicateEmailError
  ) {
    console.error(`Erro: ${err.message}`);
    return true;
  }
  return false;
}

// --------------------- Parsing simples de flags --------------------------
// Converte algo como ["--name", "Joao", "--email", "a@b.com"] em
// { name: "Joao", email: "a@b.com" }
function parseFlags(args) {
  const result = {};
  for (let i = 0; i < args.length; i += 1) {
    const token = args[i];
    if (token.startsWith('--')) {
      const key = token.slice(2);
      const value = args[i + 1];
      result[key] = value;
      i += 1;
    }
  }
  return result;
}

// --------------------- Comandos via argumentos ----------------------------

function runAdd(repo, flags) {
  const user = repo.create({
    name: flags.name,
    email: flags.email,
    birthdate: flags.birthdate,
  });
  console.log('Usuario cadastrado com sucesso:');
  printUser(user);
}

function runList(repo) {
  const users = repo.list();
  if (users.length === 0) {
    console.log('Nenhum usuario cadastrado.');
    return;
  }
  console.log(`Total de usuarios: ${users.length}`);
  users.forEach(printUser);
}

function runUpdate(repo, flags) {
  if (!flags.id) {
    throw new ValidationError('Informe --id do usuario a ser atualizado.');
  }
  const id = Number(flags.id);
  if (!Number.isInteger(id)) {
    throw new ValidationError('--id deve ser um numero inteiro.');
  }

  const user = repo.update(id, {
    name: flags.name,
    email: flags.email,
    birthdate: flags.birthdate,
  });
  console.log('Usuario atualizado com sucesso:');
  printUser(user);
}

function runRemove(repo, flags) {
  if (!flags.id) {
    throw new ValidationError('Informe --id do usuario a ser removido.');
  }
  const id = Number(flags.id);
  if (!Number.isInteger(id)) {
    throw new ValidationError('--id deve ser um numero inteiro.');
  }
  const removed = repo.remove(id);
  console.log('Usuario removido com sucesso:');
  printUser(removed);
}

function printHelp() {
  console.log(`
Uso: node index.js <comando> [opcoes]

Comandos:
  add      --name "Nome" --email "email@ex.com" --birthdate "YYYY-MM-DD"
  list
  update   --id <id> [--name ...] [--email ...] [--birthdate ...]
  remove   --id <id>
  help

Sem argumentos, inicia o modo interativo (menu).
`);
}

function runCommand(repo, argv) {
  const [command, ...rest] = argv;
  const flags = parseFlags(rest);

  try {
    switch (command) {
      case 'add':
        runAdd(repo, flags);
        break;
      case 'list':
        runList(repo);
        break;
      case 'update':
        runUpdate(repo, flags);
        break;
      case 'remove':
        runRemove(repo, flags);
        break;
      case 'help':
      case undefined:
        printHelp();
        break;
      default:
        console.error(`Comando desconhecido: "${command}"`);
        printHelp();
        process.exitCode = 1;
    }
  } catch (err) {
    if (!handleKnownErrors(err)) {
      console.error('Erro inesperado:', err.message);
      process.exitCode = 1;
    } else {
      process.exitCode = 1;
    }
  }
}

// --------------------- Modo interativo (menu) -----------------------------

function ask(rl, question) {
  return new Promise((resolve) => rl.question(question, (answer) => resolve(answer)));
}

async function interactiveAdd(repo, rl) {
  const name = await ask(rl, 'Nome: ');
  const email = await ask(rl, 'E-mail: ');
  const birthdate = await ask(rl, 'Data de nascimento (YYYY-MM-DD): ');
  const user = repo.create({ name, email, birthdate });
  console.log('Usuario cadastrado com sucesso:');
  printUser(user);
}

async function interactiveList(repo) {
  runList(repo);
}

async function interactiveUpdate(repo, rl) {
  const idStr = await ask(rl, 'ID do usuario a atualizar: ');
  const id = Number(idStr);
  if (!Number.isInteger(id)) {
    throw new ValidationError('ID invalido.');
  }
  const current = repo.getById(id);
  if (!current) {
    throw new NotFoundError(`Usuario com id ${id} nao encontrado.`);
  }
  console.log('Deixe em branco para manter o valor atual.');
  const name = await ask(rl, `Nome [${current.name}]: `);
  const email = await ask(rl, `E-mail [${current.email}]: `);
  const birthdate = await ask(rl, `Nascimento [${current.birthdate}]: `);

  const user = repo.update(id, {
    name: name.trim() === '' ? undefined : name,
    email: email.trim() === '' ? undefined : email,
    birthdate: birthdate.trim() === '' ? undefined : birthdate,
  });
  console.log('Usuario atualizado com sucesso:');
  printUser(user);
}

async function interactiveRemove(repo, rl) {
  const idStr = await ask(rl, 'ID do usuario a remover: ');
  const id = Number(idStr);
  if (!Number.isInteger(id)) {
    throw new ValidationError('ID invalido.');
  }
  const removed = repo.remove(id);
  console.log('Usuario removido com sucesso:');
  printUser(removed);
}

async function interactiveMenu(repo) {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });

  let running = true;
  while (running) {
    console.log(`
===== Gerenciador de Usuarios =====
1. Cadastrar usuario
2. Listar usuarios
3. Atualizar usuario
4. Remover usuario
5. Sair
`);
    const choice = (await ask(rl, 'Escolha uma opcao: ')).trim();

    try {
      switch (choice) {
        case '1':
          await interactiveAdd(repo, rl);
          break;
        case '2':
          await interactiveList(repo);
          break;
        case '3':
          await interactiveUpdate(repo, rl);
          break;
        case '4':
          await interactiveRemove(repo, rl);
          break;
        case '5':
          running = false;
          break;
        default:
          console.log('Opcao invalida. Tente novamente.');
      }
    } catch (err) {
      if (!handleKnownErrors(err)) {
        console.error('Erro inesperado:', err.message);
      }
    }
  }

  rl.close();
}

module.exports = { runCommand, interactiveMenu, UserRepository };
```

---

### `index.js`

```javascript
'use strict';

/**
 * Ponto de entrada da aplicacao.
 */

const { createConnection } = require('./src/db');
const { UserRepository } = require('./src/userRepository');
const { runCommand, interactiveMenu } = require('./src/cli');

async function main() {
  const db = createConnection();
  const repo = new UserRepository(db);

  const argv = process.argv.slice(2);

  if (argv.length === 0) {
    await interactiveMenu(repo);
  } else {
    runCommand(repo, argv);
  }

  db.close();
}

main().catch((err) => {
  console.error('Erro fatal:', err.message);
  process.exitCode = 1;
});
```

---

### `README.md`

```markdown
# CLI de Usuarios (Node.js + SQLite)

Aplicacao de linha de comando para cadastrar, listar, atualizar e remover
usuarios (nome, e-mail, data de nascimento), persistindo os dados em SQLite.

## Requisitos

- Node.js 18+ (recomendado)
- npm

## Instalacao

```bash
npm install
```

Isso instalara a unica dependencia externa do projeto: `better-sqlite3`
(necessaria para acessar o banco SQLite).

O banco de dados (`data.db`) e o schema (`schema.sql`) sao criados/aplicados
automaticamente na primeira execucao.

## Como rodar

### Modo interativo (menu)

```bash
node index.js
```

Sera exibido um menu com as opcoes de cadastrar, listar, atualizar, remover
e sair.

### Modo direto (argumentos de linha de comando)

Cadastrar usuario:
```bash
node index.js add --name "Maria Silva" --email "maria@exemplo.com" --birthdate "1995-08-20"
```

Listar usuarios:
```bash
node index.js list
```

Atualizar usuario (campos omitidos permanecem inalterados):
```bash
node index.js update --id 1 --name "Maria S. Silva"
```

Remover usuario:
```bash
node index.js remove --id 1
```

Ajuda:
```bash
node index.js help
```

## Validacoes implementadas

- **Nome**: obrigatorio, nao pode ser vazio.
- **E-mail**: precisa ter formato valido (`algo@dominio.tld`) e ser unico
  no banco (nao permite cadastro duplicado, verificado tanto na aplicacao
  quanto por constraint `UNIQUE` no banco).
- **Data de nascimento**: formato `YYYY-MM-DD`, precisa ser uma data
  calendarica real e nao pode estar no futuro.

Erros de validacao, e-mail duplicado ou ID inexistente sao exibidos em
mensagens amigaveis, sem stack trace.

## Estrutura de arquivos

```
.
├── index.js              # ponto de entrada
├── schema.sql            # script de criacao do schema
├── data.db               # criado automaticamente (banco SQLite)
├── package.json
└── src/
    ├── db.js              # conexao com o banco + aplicacao do schema
    ├── validators.js      # validacao de email e data
    ├── userRepository.js  # CRUD de usuarios (camada de dados)
    └── cli.js             # logica de CLI (comandos e menu interativo)
```

## Resetando o banco de dados

Para recomecar do zero, basta apagar o arquivo `data.db`:

```bash
rm data.db
```

Ele sera recriado automaticamente na proxima execucao.
```