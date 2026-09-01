<!--
nivel: 1 - CRUD com persistencia em banco
provider: gpt
model: gpt-5.6
tentativa: 2
temperature: 0.2
timestamp: 2026-08-18T16:59:42.862Z
metadata: {"model":"gpt-5.6-sol","usage":{"prompt_tokens":221,"completion_tokens":6264,"total_tokens":6485,"prompt_tokens_details":{"cached_tokens":0,"cache_write_tokens":0,"audio_tokens":0},"completion_tokens_details":{"reasoning_tokens":1181,"audio_tokens":0,"accepted_prediction_tokens":0,"rejected_prediction_tokens":0}},"finish_reason":"stop"}
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

Abaixo está uma implementação completa em Node.js, usando apenas o driver SQLite `better-sqlite3` como dependência externa.

## Estrutura do projeto

```text
usuarios-cli/
├── data/
│   └── .gitkeep
├── src/
│   ├── database.js
│   ├── index.js
│   └── validation.js
├── .gitignore
├── package.json
├── README.md
└── schema.sql
```

---

### `package.json`

```json
{
  "name": "usuarios-cli",
  "version": "1.0.0",
  "description": "Aplicação CLI para gerenciamento de usuários com Node.js e SQLite",
  "private": true,
  "type": "commonjs",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "init-db": "node src/index.js inicializar"
  },
  "engines": {
    "node": ">=18"
  },
  "dependencies": {
    "better-sqlite3": "^11.8.1"
  }
}
```

---

### `schema.sql`

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    nome TEXT NOT NULL
        CHECK (
            length(trim(nome)) >= 2
            AND length(nome) <= 200
        ),

    email TEXT NOT NULL
        CHECK (
            length(email) <= 254
            AND instr(email, '@') > 1
        ),

    -- Datas são armazenadas no formato ISO YYYY-MM-DD.
    data_nascimento TEXT NOT NULL
        CHECK (
            data_nascimento GLOB
            '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
        ),

    criado_em TEXT NOT NULL DEFAULT (datetime('now')),
    atualizado_em TEXT NOT NULL DEFAULT (datetime('now'))
);

-- COLLATE NOCASE impede e-mails duplicados mesmo que tenham diferenças
-- entre letras maiúsculas e minúsculas.
CREATE UNIQUE INDEX IF NOT EXISTS usuarios_email_unique
    ON usuarios(email COLLATE NOCASE);
```

---

### `src/validation.js`

```javascript
'use strict';

/**
 * Erro utilizado para entradas inválidas fornecidas pelo usuário.
 * Ele permite que a camada de CLI exiba mensagens amigáveis sem stack trace.
 */
class InputError extends Error {
  constructor(message) {
    super(message);
    this.name = 'InputError';
  }
}

function validateName(value) {
  if (typeof value !== 'string') {
    throw new InputError('O nome é obrigatório.');
  }

  const name = value.trim();

  if (name.length < 2) {
    throw new InputError('O nome deve possuir pelo menos 2 caracteres.');
  }

  if (name.length > 200) {
    throw new InputError('O nome deve possuir no máximo 200 caracteres.');
  }

  return name;
}

function validateEmail(value) {
  if (typeof value !== 'string') {
    throw new InputError('O e-mail é obrigatório.');
  }

  // E-mails são normalizados para minúsculas para facilitar comparação.
  const email = value.trim().toLowerCase();

  if (email.length === 0) {
    throw new InputError('O e-mail é obrigatório.');
  }

  if (email.length > 254) {
    throw new InputError('O e-mail deve possuir no máximo 254 caracteres.');
  }

  /*
   * Validação propositalmente simples e prática:
   * - não permite espaços;
   * - exige conteúdo antes e depois de @;
   * - exige ao menos um ponto depois de @.
   *
   * A validação completa da RFC de e-mail seria excessivamente complexa
   * para este cadastro e poderia rejeitar ou aceitar endereços inesperados.
   */
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (!emailPattern.test(email)) {
    throw new InputError(
      'Formato de e-mail inválido. Exemplo esperado: usuario@dominio.com.'
    );
  }

  return email;
}

function validateBirthDate(value) {
  if (typeof value !== 'string' || value.trim() === '') {
    throw new InputError('A data de nascimento é obrigatória.');
  }

  const birthDate = value.trim();
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(birthDate);

  if (!match) {
    throw new InputError(
      'Data de nascimento inválida. Use o formato YYYY-MM-DD, por exemplo: 1990-05-21.'
    );
  }

  const year = Number(match[1]);
  const month = Number(match[2]);
  const day = Number(match[3]);

  if (year < 1 || month < 1 || month > 12) {
    throw new InputError('A data de nascimento informada não é uma data válida.');
  }

  const daysInMonth = [
    31,
    isLeapYear(year) ? 29 : 28,
    31,
    30,
    31,
    30,
    31,
    31,
    30,
    31,
    30,
    31
  ];

  if (day < 1 || day > daysInMonth[month - 1]) {
    throw new InputError('A data de nascimento informada não é uma data válida.');
  }

  // Assume-se que uma data de nascimento futura não é válida.
  const today = new Date();
  const todayAsNumber =
    today.getFullYear() * 10000 +
    (today.getMonth() + 1) * 100 +
    today.getDate();

  const birthDateAsNumber = year * 10000 + month * 100 + day;

  if (birthDateAsNumber > todayAsNumber) {
    throw new InputError('A data de nascimento não pode estar no futuro.');
  }

  return birthDate;
}

function isLeapYear(year) {
  return year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0);
}

function validateId(value) {
  if (value === undefined || value === null || String(value).trim() === '') {
    throw new InputError('O identificador do usuário é obrigatório.');
  }

  const text = String(value).trim();

  if (!/^\d+$/.test(text)) {
    throw new InputError('O identificador deve ser um número inteiro positivo.');
  }

  const id = Number(text);

  if (!Number.isSafeInteger(id) || id <= 0) {
    throw new InputError('O identificador deve ser um número inteiro positivo.');
  }

  return id;
}

module.exports = {
  InputError,
  validateName,
  validateEmail,
  validateBirthDate,
  validateId
};
```

---

### `src/database.js`

```javascript
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const Database = require('better-sqlite3');

const PROJECT_ROOT = path.resolve(__dirname, '..');
const DEFAULT_DATABASE_PATH = path.join(PROJECT_ROOT, 'data', 'usuarios.db');
const SCHEMA_PATH = path.join(PROJECT_ROOT, 'schema.sql');

/**
 * A variável USERS_DB pode ser usada para escolher outro arquivo SQLite.
 * Se não for informada, o banco será criado em data/usuarios.db.
 */
function getDatabasePath() {
  if (process.env.USERS_DB) {
    return path.resolve(process.env.USERS_DB);
  }

  return DEFAULT_DATABASE_PATH;
}

function openDatabase() {
  const databasePath = getDatabasePath();
  const databaseDirectory = path.dirname(databasePath);

  fs.mkdirSync(databaseDirectory, { recursive: true });

  const database = new Database(databasePath);

  // Aguarda brevemente caso outra execução esteja escrevendo no SQLite.
  database.pragma('busy_timeout = 5000');
  database.pragma('foreign_keys = ON');

  initializeSchema(database);

  return database;
}

function initializeSchema(database) {
  if (!fs.existsSync(SCHEMA_PATH)) {
    throw new Error(`Arquivo de schema não encontrado: ${SCHEMA_PATH}`);
  }

  const schema = fs.readFileSync(SCHEMA_PATH, 'utf8');
  database.exec(schema);
}

function createUser(database, user) {
  const statement = database.prepare(`
    INSERT INTO usuarios (nome, email, data_nascimento)
    VALUES (@nome, @email, @dataNascimento)
  `);

  const result = statement.run(user);

  return findUserById(database, result.lastInsertRowid);
}

function listUsers(database) {
  return database.prepare(`
    SELECT
      id,
      nome,
      email,
      data_nascimento AS dataNascimento,
      criado_em AS criadoEm,
      atualizado_em AS atualizadoEm
    FROM usuarios
    ORDER BY id ASC
  `).all();
}

function findUserById(database, id) {
  return database.prepare(`
    SELECT
      id,
      nome,
      email,
      data_nascimento AS dataNascimento,
      criado_em AS criadoEm,
      atualizado_em AS atualizadoEm
    FROM usuarios
    WHERE id = ?
  `).get(id);
}

function updateUser(database, id, fields) {
  const columns = [];
  const parameters = { id };

  if (fields.nome !== undefined) {
    columns.push('nome = @nome');
    parameters.nome = fields.nome;
  }

  if (fields.email !== undefined) {
    columns.push('email = @email');
    parameters.email = fields.email;
  }

  if (fields.dataNascimento !== undefined) {
    columns.push('data_nascimento = @dataNascimento');
    parameters.dataNascimento = fields.dataNascimento;
  }

  if (columns.length === 0) {
    return findUserById(database, id);
  }

  columns.push("atualizado_em = datetime('now')");

  const statement = database.prepare(`
    UPDATE usuarios
    SET ${columns.join(', ')}
    WHERE id = @id
  `);

  const result = statement.run(parameters);

  if (result.changes === 0) {
    return null;
  }

  return findUserById(database, id);
}

function removeUser(database, id) {
  const user = findUserById(database, id);

  if (!user) {
    return null;
  }

  database.prepare('DELETE FROM usuarios WHERE id = ?').run(id);

  return user;
}

module.exports = {
  getDatabasePath,
  openDatabase,
  initializeSchema,
  createUser,
  listUsers,
  findUserById,
  updateUser,
  removeUser
};
```

---

### `src/index.js`

```javascript
#!/usr/bin/env node
'use strict';

const {
  getDatabasePath,
  openDatabase,
  createUser,
  listUsers,
  updateUser,
  removeUser
} = require('./database');

const {
  InputError,
  validateName,
  validateEmail,
  validateBirthDate,
  validateId
} = require('./validation');

const HELP_TEXT = `
Gerenciador de usuários

Uso:
  node src/index.js <comando> [opções]

Comandos:
  inicializar
      Cria o banco e as tabelas, caso ainda não existam.

  cadastrar --nome <nome> --email <email> --nascimento <YYYY-MM-DD>
      Cadastra um novo usuário.

  listar
      Lista todos os usuários cadastrados.

  atualizar <id> [--nome <nome>] [--email <email>] [--nascimento <YYYY-MM-DD>]
      Atualiza um ou mais campos de um usuário.

  remover <id>
      Remove um usuário.

  ajuda
      Exibe esta ajuda.

Exemplos:
  node src/index.js inicializar

  node src/index.js cadastrar \\
    --nome "Ana Silva" \\
    --email "ana@example.com" \\
    --nascimento "1992-08-15"

  node src/index.js listar

  node src/index.js atualizar 1 --email "novo-email@example.com"

  node src/index.js remover 1

Também é possível usar opções com sinal de igual:
  node src/index.js cadastrar --nome="Ana Silva" --email="ana@example.com" --nascimento="1992-08-15"

Banco padrão:
  data/usuarios.db

Para usar outro arquivo:
  USERS_DB=/caminho/usuarios.db node src/index.js listar
`.trim();

/**
 * Faz o parsing manual dos argumentos para evitar uma dependência externa
 * apenas para a interface de linha de comando.
 */
function parseArguments(args) {
  const positional = [];
  const options = {};

  for (let index = 0; index < args.length; index += 1) {
    const argument = args[index];

    if (!argument.startsWith('--')) {
      positional.push(argument);
      continue;
    }

    const equalIndex = argument.indexOf('=');
    let optionName;
    let optionValue;

    if (equalIndex >= 0) {
      optionName = argument.slice(2, equalIndex);
      optionValue = argument.slice(equalIndex + 1);
    } else {
      optionName = argument.slice(2);
      optionValue = args[index + 1];

      if (optionValue === undefined || optionValue.startsWith('--')) {
        throw new InputError(`A opção --${optionName} precisa de um valor.`);
      }

      index += 1;
    }

    if (!optionName) {
      throw new InputError('Foi informada uma opção inválida.');
    }

    if (Object.prototype.hasOwnProperty.call(options, optionName)) {
      throw new InputError(`A opção --${optionName} foi informada mais de uma vez.`);
    }

    options[optionName] = optionValue;
  }

  return { positional, options };
}

function assertAllowedOptions(options, allowedOptions) {
  for (const optionName of Object.keys(options)) {
    if (!allowedOptions.includes(optionName)) {
      throw new InputError(`Opção desconhecida: --${optionName}.`);
    }
  }
}

function assertNoExtraPositionals(positional, expectedCount) {
  if (positional.length > expectedCount) {
    throw new InputError(
      `Argumento inesperado: ${positional[expectedCount]}. Consulte o comando "ajuda".`
    );
  }
}

function ensureRequiredOption(options, optionName) {
  if (
    !Object.prototype.hasOwnProperty.call(options, optionName) ||
    String(options[optionName]).trim() === ''
  ) {
    throw new InputError(`A opção --${optionName} é obrigatória.`);
  }

  return options[optionName];
}

function displayUser(user) {
  console.table([
    {
      ID: user.id,
      Nome: user.nome,
      'E-mail': user.email,
      Nascimento: user.dataNascimento,
      Criado: user.criadoEm,
      Atualizado: user.atualizadoEm
    }
  ]);
}

function handleCreate(database, args) {
  const { positional, options } = parseArguments(args);

  assertNoExtraPositionals(positional, 0);
  assertAllowedOptions(options, ['nome', 'email', 'nascimento']);

  const user = {
    nome: validateName(ensureRequiredOption(options, 'nome')),
    email: validateEmail(ensureRequiredOption(options, 'email')),
    dataNascimento: validateBirthDate(
      ensureRequiredOption(options, 'nascimento')
    )
  };

  const createdUser = createUser(database, user);

  console.log('Usuário cadastrado com sucesso.');
  displayUser(createdUser);
}

function handleList(database, args) {
  const { positional, options } = parseArguments(args);

  assertNoExtraPositionals(positional, 0);
  assertAllowedOptions(options, []);

  const users = listUsers(database);

  if (users.length === 0) {
    console.log('Nenhum usuário cadastrado.');
    return;
  }

  console.table(
    users.map((user) => ({
      ID: user.id,
      Nome: user.nome,
      'E-mail': user.email,
      Nascimento: user.dataNascimento,
      Criado: user.criadoEm,
      Atualizado: user.atualizadoEm
    }))
  );
}

function handleUpdate(database, args) {
  const { positional, options } = parseArguments(args);

  assertNoExtraPositionals(positional, 1);
  assertAllowedOptions(options, ['nome', 'email', 'nascimento']);

  const id = validateId(positional[0]);

  if (Object.keys(options).length === 0) {
    throw new InputError(
      'Informe pelo menos um campo para atualizar: --nome, --email ou --nascimento.'
    );
  }

  const fields = {};

  if (Object.prototype.hasOwnProperty.call(options, 'nome')) {
    fields.nome = validateName(options.nome);
  }

  if (Object.prototype.hasOwnProperty.call(options, 'email')) {
    fields.email = validateEmail(options.email);
  }

  if (Object.prototype.hasOwnProperty.call(options, 'nascimento')) {
    fields.dataNascimento = validateBirthDate(options.nascimento);
  }

  const updatedUser = updateUser(database, id, fields);

  if (!updatedUser) {
    throw new InputError(`Usuário com ID ${id} não encontrado.`);
  }

  console.log('Usuário atualizado com sucesso.');
  displayUser(updatedUser);
}

function handleRemove(database, args) {
  const { positional, options } = parseArguments(args);

  assertNoExtraPositionals(positional, 1);
  assertAllowedOptions(options, []);

  const id = validateId(positional[0]);
  const removedUser = removeUser(database, id);

  if (!removedUser) {
    throw new InputError(`Usuário com ID ${id} não encontrado.`);
  }

  console.log(
    `Usuário removido com sucesso: ${removedUser.nome} <${removedUser.email}>.`
  );
}

function isUniqueEmailError(error) {
  return (
    error &&
    typeof error === 'object' &&
    (
      error.code === 'SQLITE_CONSTRAINT_UNIQUE' ||
      error.code === 'SQLITE_CONSTRAINT_PRIMARYKEY' ||
      (
        error.code === 'SQLITE_CONSTRAINT' &&
        String(error.message).toLowerCase().includes('email')
      )
    )
  );
}

function main() {
  const [command, ...args] = process.argv.slice(2);

  if (!command || command === 'ajuda' || command === 'help' || command === '--help') {
    console.log(HELP_TEXT);
    return;
  }

  let database;

  try {
    /*
     * O schema é executado automaticamente ao abrir o banco.
     * Como ele usa IF NOT EXISTS, a operação é segura em execuções repetidas.
     */
    database = openDatabase();

    switch (command) {
      case 'inicializar':
        if (args.length > 0) {
          throw new InputError('O comando inicializar não recebe argumentos.');
        }

        console.log('Banco de dados inicializado com sucesso.');
        console.log(`Arquivo: ${getDatabasePath()}`);
        break;

      case 'cadastrar':
        handleCreate(database, args);
        break;

      case 'listar':
        handleList(database, args);
        break;

      case 'atualizar':
        handleUpdate(database, args);
        break;

      case 'remover':
        handleRemove(database, args);
        break;

      default:
        throw new InputError(
          `Comando desconhecido: ${command}. Use "node src/index.js ajuda".`
        );
    }
  } catch (error) {
    if (isUniqueEmailError(error)) {
      console.error('Erro: já existe um usuário cadastrado com esse e-mail.');
      process.exitCode = 1;
      return;
    }

    if (error instanceof InputError) {
      console.error(`Erro: ${error.message}`);
      process.exitCode = 1;
      return;
    }

    console.error('Erro inesperado ao executar a operação.');

    if (process.env.DEBUG === '1') {
      console.error(error);
    } else {
      console.error('Use DEBUG=1 para exibir detalhes técnicos.');
    }

    process.exitCode = 1;
  } finally {
    if (database) {
      database.close();
    }
  }
}

main();
```

---

### `.gitignore`

```gitignore
node_modules/
data/*.db
data/*.db-shm
data/*.db-wal
npm-debug.log*
.DS_Store
```

---

### `data/.gitkeep`

Arquivo vazio:

```text
```

---

### `README.md`

```markdown
# Gerenciador de usuários CLI

Aplicação de linha de comando para cadastrar, listar, atualizar e remover
usuários, persistindo os dados em SQLite.

## Requisitos

- Node.js 18 ou superior
- npm

## Instalação

Na raiz do projeto, execute:

```bash
npm install
```

## Inicializar o banco

O banco é inicializado automaticamente na primeira execução. Também é possível
inicializá-lo explicitamente:

```bash
npm run init-db
```

Por padrão, o banco será criado em:

```text
data/usuarios.db
```

## Comandos

### Exibir ajuda

```bash
npm start
```

Ou:

```bash
node src/index.js ajuda
```

### Cadastrar usuário

```bash
node src/index.js cadastrar \
  --nome "Ana Silva" \
  --email "ana@example.com" \
  --nascimento "1992-08-15"
```

A data deve estar no formato `YYYY-MM-DD`.

### Listar usuários

```bash
node src/index.js listar
```

### Atualizar usuário

É possível atualizar um ou mais campos:

```bash
node src/index.js atualizar 1 --nome "Ana Souza"
```

```bash
node src/index.js atualizar 1 \
  --email "ana.souza@example.com" \
  --nascimento "1992-09-20"
```

### Remover usuário

```bash
node src/index.js remover 1
```

## Banco em outro local

Defina a variável de ambiente `USERS_DB`:

```bash
USERS_DB=/tmp/meus-usuarios.db node src/index.js listar
```

No Windows PowerShell:

```powershell
$env:USERS_DB="C:\dados\usuarios.db"
node src/index.js listar
```

## Validações

A aplicação:

- exige nome com pelo menos 2 caracteres;
- valida o formato básico do e-mail;
- normaliza e-mails para letras minúsculas;
- impede e-mails duplicados sem diferenciar maiúsculas e minúsculas;
- exige data no formato `YYYY-MM-DD`;
- verifica se a data realmente existe;
- impede datas de nascimento futuras;
- valida identificadores antes de consultar o banco;
- utiliza queries parametrizadas para evitar injeção de SQL.

## Detalhes de erros

Erros comuns são apresentados de forma amigável. Para visualizar detalhes
técnicos de erros inesperados:

```bash
DEBUG=1 node src/index.js listar
```
```

## Execução rápida

Depois de criar os arquivos:

```bash
npm install
npm run init-db
```

Cadastre um usuário:

```bash
node src/index.js cadastrar \
  --nome "Maria Oliveira" \
  --email "maria@example.com" \
  --nascimento "1988-04-12"
```

Liste os usuários:

```bash
node src/index.js listar
```

Atualize:

```bash
node src/index.js atualizar 1 --nome "Maria da Silva Oliveira"
```

Remova:

```bash
node src/index.js remover 1
```