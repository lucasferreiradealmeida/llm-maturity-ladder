<!--
nivel: 1 - CRUD com persistencia em banco
provider: claude
model: claude-sonnet-5
tentativa: 3
temperature: 0.2
timestamp: 2026-08-31T09:12:25.972Z
metadata: {"model":"claude-sonnet-5","usage":{"input_tokens":381,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"cache_creation":{"ephemeral_5m_input_tokens":0,"ephemeral_1h_input_tokens":0},"output_tokens":7720,"service_tier":"standard","inference_geo":"global","output_tokens_details":{"thinking_tokens":615}},"stop_reason":"end_turn"}
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

# Sistema de Gerenciamento de Usuários (CLI + SQLite)

Abaixo está a implementação completa. Decisões de projeto (documentadas também nos comentários do código):

- **Node.js puro + `sqlite3`**: a única dependência externa é o driver do SQLite, que é estritamente necessário para persistência. Não uso frameworks de CLI (como `commander`/`yargs`); o parsing de argumentos é feito manualmente.
- **Interface por comandos** (`add`, `list`, `update`, `remove`, `help`), no estilo `node cli.js <comando> --opcao valor`, por ser simples de testar e scriptar.
- **Datas** no formato `YYYY-MM-DD` (ISO simplificado), validadas com regex + verificação de data real (evita `2024-02-31`).
- **E-mail** validado com regex pragmática (não 100% RFC, mas cobre os casos práticos) e restringido por `UNIQUE` no banco + verificação prévia amigável.
- **Camadas separadas**: `db.js` (conexão), `validators.js` (validações), `userRepository.js` (acesso a dados), `cli.js` (interface).

---

### Estrutura de arquivos

```
user-cli/
├── package.json
├── schema.sql
├── src/
│   ├── db.js
│   ├── validators.js
│   ├── userRepository.js
│   └── cli.js
└── data/            (criado automaticamente, contém o arquivo .sqlite)
```

---

**package.json**
```json
{
  "name": "user-cli",
  "version": "1.0.0",
  "description": "CLI para cadastro de usuarios com persistencia em SQLite",
  "main": "src/cli.js",
  "type": "commonjs",
  "bin": {
    "user-cli": "src/cli.js"
  },
  "scripts": {
    "start": "node src/cli.js",
    "init-db": "node -e \"require('./src/db.js').initSchema().then(()=>{console.log('Schema criado/atualizado com sucesso.'); process.exit(0);}).catch(e=>{console.error(e); process.exit(1);})\""
  },
  "dependencies": {
    "sqlite3": "^5.1.7"
  }
}
```

---

**schema.sql**
```sql
-- Script de criacao do schema do banco de dados.
-- Executado automaticamente na inicializacao (ver src/db.js),
-- mas tambem pode ser aplicado manualmente com:
--   sqlite3 data/users.db < schema.sql

CREATE TABLE IF NOT EXISTS users (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL,
    email      TEXT NOT NULL UNIQUE,   -- garante nao haver duplicidade de e-mail no nivel do banco
    birthdate  TEXT NOT NULL,          -- armazenado como 'YYYY-MM-DD'
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Indice auxiliar para buscas rapidas por e-mail (alem da constraint UNIQUE)
CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
```

---

**src/db.js**
```javascript
/**
 * Modulo responsavel pela conexao com o banco SQLite e pela aplicacao
 * do schema. Usa apenas a biblioteca 'sqlite3', driver minimo necessario
 * para persistencia em SQLite a partir do Node.js.
 */

const sqlite3 = require('sqlite3');
const path = require('path');
const fs = require('fs');

// Diretorio e arquivo de dados. Criado automaticamente se nao existir.
const DATA_DIR = path.join(__dirname, '..', 'data');
const DB_PATH = path.join(DATA_DIR, 'users.db');
const SCHEMA_PATH = path.join(__dirname, '..', 'schema.sql');

if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

let dbInstance = null;

/**
 * Retorna uma instancia unica (singleton) de conexao com o banco.
 */
function getDb() {
  if (!dbInstance) {
    dbInstance = new sqlite3.Database(DB_PATH, (err) => {
      if (err) {
        console.error('Erro ao conectar ao banco de dados:', err.message);
        process.exit(1);
      }
    });
  }
  return dbInstance;
}

/**
 * Aplica o schema.sql ao banco (cria tabelas/indices caso nao existam).
 * E chamado automaticamente antes de qualquer operacao da CLI.
 */
function initSchema() {
  return new Promise((resolve, reject) => {
    const db = getDb();
    const schema = fs.readFileSync(SCHEMA_PATH, 'utf-8');
    db.exec(schema, (err) => {
      if (err) return reject(err);
      resolve();
    });
  });
}

/**
 * Encerra a conexao com o banco.
 */
function closeDb() {
  return new Promise((resolve, reject) => {
    if (!dbInstance) return resolve();
    dbInstance.close((err) => {
      if (err) return reject(err);
      resolve();
    });
  });
}

module.exports = { getDb, initSchema, closeDb, DB_PATH };
```

---

**src/validators.js**
```javascript
/**
 * Funcoes de validacao de dados de entrada.
 * Mantidas simples e sem dependencias externas.
 */

// Regex pragmatica para e-mail: cobre a grande maioria dos casos reais
// sem tentar implementar a especificacao RFC 5322 completa.
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

// Formato esperado de data: YYYY-MM-DD
const DATE_REGEX = /^\d{4}-\d{2}-\d{2}$/;

function isValidEmail(email) {
  if (typeof email !== 'string') return false;
  return EMAIL_REGEX.test(email.trim());
}

/**
 * Valida se a string representa uma data real no formato YYYY-MM-DD
 * (rejeita, por exemplo, '2024-02-31').
 */
function isValidDate(dateStr) {
  if (typeof dateStr !== 'string' || !DATE_REGEX.test(dateStr)) return false;

  const [year, month, day] = dateStr.split('-').map(Number);
  const date = new Date(Date.UTC(year, month - 1, day));

  const isRealDate =
    date.getUTCFullYear() === year &&
    date.getUTCMonth() === month - 1 &&
    date.getUTCDate() === day;

  if (!isRealDate) return false;

  // Nao aceita datas de nascimento no futuro
  const today = new Date();
  today.setUTCHours(0, 0, 0, 0);
  if (date > today) return false;

  return true;
}

function isNonEmptyString(value) {
  return typeof value === 'string' && value.trim().length > 0;
}

module.exports = { isValidEmail, isValidDate, isNonEmptyString };
```

---

**src/userRepository.js**
```javascript
/**
 * Camada de acesso a dados (repository) para a entidade User.
 * Encapsula todas as queries SQL usadas pela CLI.
 */

const { getDb } = require('./db');

/**
 * Erro customizado para violacao de regra de negocio (ex: email duplicado,
 * usuario nao encontrado), permitindo tratamento amigavel na CLI.
 */
class RepositoryError extends Error {}

function createUser({ name, email, birthdate }) {
  return new Promise((resolve, reject) => {
    const db = getDb();
    const sql = `INSERT INTO users (name, email, birthdate) VALUES (?, ?, ?)`;
    db.run(sql, [name, email, birthdate], function (err) {
      if (err) {
        if (err.message && err.message.includes('UNIQUE')) {
          return reject(new RepositoryError(`Ja existe um usuario cadastrado com o e-mail "${email}".`));
        }
        return reject(err);
      }
      resolve({ id: this.lastID, name, email, birthdate });
    });
  });
}

function listUsers() {
  return new Promise((resolve, reject) => {
    const db = getDb();
    db.all(`SELECT id, name, email, birthdate, created_at, updated_at FROM users ORDER BY id`, [], (err, rows) => {
      if (err) return reject(err);
      resolve(rows);
    });
  });
}

function findUserById(id) {
  return new Promise((resolve, reject) => {
    const db = getDb();
    db.get(`SELECT id, name, email, birthdate FROM users WHERE id = ?`, [id], (err, row) => {
      if (err) return reject(err);
      resolve(row || null);
    });
  });
}

function findUserByEmail(email) {
  return new Promise((resolve, reject) => {
    const db = getDb();
    db.get(`SELECT id, name, email, birthdate FROM users WHERE email = ?`, [email], (err, row) => {
      if (err) return reject(err);
      resolve(row || null);
    });
  });
}

function updateUser(id, fields) {
  return new Promise((resolve, reject) => {
    const db = getDb();
    const allowed = ['name', 'email', 'birthdate'];
    const keys = Object.keys(fields).filter((k) => allowed.includes(k));

    if (keys.length === 0) {
      return reject(new RepositoryError('Nenhum campo valido para atualizacao foi informado.'));
    }

    const setClause = keys.map((k) => `${k} = ?`).join(', ');
    const values = keys.map((k) => fields[k]);
    const sql = `UPDATE users SET ${setClause}, updated_at = datetime('now') WHERE id = ?`;

    db.run(sql, [...values, id], function (err) {
      if (err) {
        if (err.message && err.message.includes('UNIQUE')) {
          return reject(new RepositoryError(`Ja existe um usuario cadastrado com o e-mail "${fields.email}".`));
        }
        return reject(err);
      }
      if (this.changes === 0) {
        return reject(new RepositoryError(`Nenhum usuario encontrado com id ${id}.`));
      }
      resolve();
    });
  });
}

function deleteUser(id) {
  return new Promise((resolve, reject) => {
    const db = getDb();
    db.run(`DELETE FROM users WHERE id = ?`, [id], function (err) {
      if (err) return reject(err);
      if (this.changes === 0) {
        return reject(new RepositoryError(`Nenhum usuario encontrado com id ${id}.`));
      }
      resolve();
    });
  });
}

module.exports = {
  RepositoryError,
  createUser,
  listUsers,
  findUserById,
  findUserByEmail,
  updateUser,
  deleteUser,
};
```

---

**src/cli.js**
```javascript
#!/usr/bin/env node
/**
 * Ponto de entrada da CLI.
 *
 * Uso:
 *   node src/cli.js add --name "Joao Silva" --email "joao@exemplo.com" --dob "1990-05-20"
 *   node src/cli.js list
 *   node src/cli.js update --id 1 --name "Novo Nome"
 *   node src/cli.js update --id 1 --email "novo@exemplo.com"
 *   node src/cli.js remove --id 1
 *   node src/cli.js help
 *
 * Parsing de argumentos feito manualmente (sem libs externas de CLI),
 * conforme restricao do projeto.
 */

const { initSchema, closeDb, DB_PATH } = require('./db');
const { isValidEmail, isValidDate, isNonEmptyString } = require('./validators');
const repo = require('./userRepository');

/**
 * Converte argv no formato ["--name", "Joao", "--email", "x@x.com"]
 * em um objeto { name: "Joao", email: "x@x.com" }.
 */
function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i++) {
    const token = argv[i];
    if (token.startsWith('--')) {
      const key = token.slice(2);
      const next = argv[i + 1];
      if (next === undefined || next.startsWith('--')) {
        args[key] = true; // flag booleana sem valor
      } else {
        args[key] = next;
        i++;
      }
    }
  }
  return args;
}

function printHelp() {
  console.log(`
Uso: node src/cli.js <comando> [opcoes]

Comandos disponiveis:
  add --name <nome> --email <email> --dob <YYYY-MM-DD>
      Cadastra um novo usuario.

  list
      Lista todos os usuarios cadastrados.

  update --id <id> [--name <nome>] [--email <email>] [--dob <YYYY-MM-DD>]
      Atualiza um ou mais campos de um usuario existente.

  remove --id <id>
      Remove um usuario pelo id.

  help
      Exibe esta ajuda.

Banco de dados utilizado: ${DB_PATH}
`);
}

/**
 * Valida os campos de um usuario. Lanca Error com mensagem amigavel
 * caso algum dado seja invalido.
 * @param {{name?: string, email?: string, birthdate?: string}} data
 * @param {boolean} requireAll - se true, todos os campos sao obrigatorios (uso: add)
 */
function validateUserFields(data, requireAll) {
  if (requireAll || data.name !== undefined) {
    if (!isNonEmptyString(data.name)) {
      throw new Error('O campo "name" e obrigatorio e nao pode ser vazio.');
    }
  }

  if (requireAll || data.email !== undefined) {
    if (!isValidEmail(data.email)) {
      throw new Error(`O e-mail "${data.email}" e invalido. Formato esperado: usuario@dominio.com`);
    }
  }

  if (requireAll || data.birthdate !== undefined) {
    if (!isValidDate(data.birthdate)) {
      throw new Error(`Data de nascimento invalida: "${data.birthdate}". Use o formato YYYY-MM-DD e uma data real, nao futura.`);
    }
  }
}

async function cmdAdd(args) {
  const name = args.name;
  const email = args.email && args.email.trim().toLowerCase();
  const birthdate = args.dob;

  validateUserFields({ name, email, birthdate }, true);

  const existing = await repo.findUserByEmail(email);
  if (existing) {
    throw new Error(`Ja existe um usuario cadastrado com o e-mail "${email}" (id ${existing.id}).`);
  }

  const user = await repo.createUser({ name: name.trim(), email, birthdate });
  console.log('Usuario cadastrado com sucesso:');
  console.table([user]);
}

async function cmdList() {
  const users = await repo.listUsers();
  if (users.length === 0) {
    console.log('Nenhum usuario cadastrado.');
    return;
  }
  console.table(users);
}

async function cmdUpdate(args) {
  const id = Number(args.id);
  if (!Number.isInteger(id) || id <= 0) {
    throw new Error('Informe um --id valido (numero inteiro positivo).');
  }

  const existing = await repo.findUserById(id);
  if (!existing) {
    throw new Error(`Nenhum usuario encontrado com id ${id}.`);
  }

  const fields = {};
  if (args.name !== undefined) fields.name = args.name;
  if (args.email !== undefined) fields.email = args.email.trim().toLowerCase();
  if (args.dob !== undefined) fields.birthdate = args.dob;

  if (Object.keys(fields).length === 0) {
    throw new Error('Informe ao menos um campo para atualizar: --name, --email ou --dob.');
  }

  validateUserFields(
    { name: fields.name, email: fields.email, birthdate: fields.birthdate },
    false
  );

  if (fields.email) {
    const emailOwner = await repo.findUserByEmail(fields.email);
    if (emailOwner && emailOwner.id !== id) {
      throw new Error(`O e-mail "${fields.email}" ja esta em uso por outro usuario (id ${emailOwner.id}).`);
    }
  }

  await repo.updateUser(id, fields);
  const updated = await repo.findUserById(id);
  console.log('Usuario atualizado com sucesso:');
  console.table([updated]);
}

async function cmdRemove(args) {
  const id = Number(args.id);
  if (!Number.isInteger(id) || id <= 0) {
    throw new Error('Informe um --id valido (numero inteiro positivo).');
  }
  await repo.deleteUser(id);
  console.log(`Usuario com id ${id} removido com sucesso.`);
}

async function main() {
  const [, , command, ...rest] = process.argv;
  const args = parseArgs(rest);

  if (!command || command === 'help' || args.help) {
    printHelp();
    return;
  }

  await initSchema();

  try {
    switch (command) {
      case 'add':
        await cmdAdd(args);
        break;
      case 'list':
        await cmdList();
        break;
      case 'update':
        await cmdUpdate(args);
        break;
      case 'remove':
        await cmdRemove(args);
        break;
      default:
        console.error(`Comando desconhecido: "${command}".`);
        printHelp();
        process.exitCode = 1;
    }
  } catch (err) {
    // Tratamento amigavel de erros: nunca expoe stack trace ao usuario final.
    console.error(`Erro: ${err.message}`);
    process.exitCode = 1;
  } finally {
    await closeDb();
  }
}

main();
```

---

## Instruções de execução

### 1. Pré-requisitos
- Node.js instalado (versão 16 ou superior recomendada).

### 2. Instalação

```bash
# dentro da pasta user-cli/
npm install
```

Isso instalará a única dependência do projeto: `sqlite3`.

> O banco de dados (`data/users.db`) e o schema são criados **automaticamente** na primeira execução de qualquer comando (não é necessário passo manual), mas se preferir aplicar o schema manualmente antes:
> ```bash
> npm run init-db
> ```

### 3. Uso da CLI

**Cadastrar usuário:**
```bash
node src/cli.js add --name "Joao Silva" --email "joao@exemplo.com" --dob "1990-05-20"
```

**Listar usuários:**
```bash
node src/cli.js list
```

**Atualizar usuário (id 1), alterando nome e e-mail:**
```bash
node src/cli.js update --id 1 --name "Joao S. Silva" --email "joao.silva@exemplo.com"
```

**Remover usuário:**
```bash
node src/cli.js remove --id 1
```

**Ajuda:**
```bash
node src/cli.js help
```

### 4. Exemplos de erros tratados de forma amigável
- E-mail em formato inválido (`node src/cli.js add --name "X" --email "invalido" --dob "1990-01-01"`) → mensagem clara sem stack trace.
- E-mail duplicado (cadastro ou atualização) → mensagem informando o id do usuário que já possui aquele e-mail.
- Data inválida ou futura → mensagem explicando o formato esperado.
- Atualização/remoção de `id` inexistente → mensagem informando que o usuário não foi encontrado.

### 5. Onde os dados são armazenados
O arquivo do banco SQLite é criado em `data/users.db`. O schema (`schema.sql`) pode ser inspecionado ou aplicado manualmente com:
```bash
sqlite3 data/users.db < schema.sql
```