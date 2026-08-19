<!--
nivel: 1 - CRUD com persistencia em banco
provider: gpt
model: gpt-5.6
tentativa: 1
temperature: 0.2
timestamp: 2026-08-18T16:58:13.666Z
metadata: {"model":"gpt-5.6-sol","usage":{"prompt_tokens":221,"completion_tokens":6899,"total_tokens":7120,"prompt_tokens_details":{"cached_tokens":0,"cache_write_tokens":0,"audio_tokens":0},"completion_tokens_details":{"reasoning_tokens":1536,"audio_tokens":0,"accepted_prediction_tokens":0,"rejected_prediction_tokens":0}},"finish_reason":"stop"}
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

Abaixo está uma implementação completa em Node.js com SQLite, sem framework de CLI. A aplicação oferece os comandos `cadastrar`, `listar`, `atualizar` e `remover`, com aliases em inglês.

## Estrutura do projeto

```text
usuarios-cli/
├── package.json
├── schema.sql
├── src/
│   ├── cli.js
│   ├── database.js
│   ├── errors.js
│   └── validators.js
├── .gitignore
└── README.md
```

---

### `package.json`

```json
{
  "name": "usuarios-cli",
  "version": "1.0.0",
  "description": "Aplicação CLI para gerenciamento de usuários com SQLite",
  "main": "src/cli.js",
  "type": "commonjs",
  "scripts": {
    "start": "node src/cli.js",
    "init-db": "node src/cli.js init",
    "test": "node src/cli.js ajuda"
  },
  "engines": {
    "node": ">=20"
  },
  "dependencies": {
    "better-sqlite3": "^12.2.0"
  },
  "license": "MIT"
}
```

---

### `schema.sql`

```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL
        CHECK (length(trim(name)) > 0),

    -- COLLATE NOCASE faz com que a restrição UNIQUE trate
    -- exemplo@email.com e EXEMPLO@EMAIL.COM como duplicados.
    email TEXT NOT NULL COLLATE NOCASE UNIQUE
        CHECK (length(trim(email)) > 0),

    -- Datas são armazenadas em ISO 8601: YYYY-MM-DD.
    -- A validação completa da existência da data é feita pela aplicação.
    birth_date TEXT NOT NULL
        CHECK (
            length(birth_date) = 10
            AND birth_date GLOB
                '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
        ),

    created_at TEXT NOT NULL DEFAULT (
        strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
    ),

    updated_at TEXT NOT NULL DEFAULT (
        strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
    )
);
```

---

### `src/errors.js`

```javascript
class AppError extends Error {
  constructor(message, exitCode = 1) {
    super(message);
    this.name = "AppError";
    this.exitCode = exitCode;
  }
}

module.exports = {
  AppError
};
```

---

### `src/validators.js`

```javascript
const { AppError } = require("./errors");

/**
 * As validações são executadas também nas atualizações.
 * Os valores são normalizados antes de serem persistidos:
 * - nome: espaços externos removidos;
 * - e-mail: espaços removidos e convertido para minúsculas;
 * - nascimento: preservado no formato ISO YYYY-MM-DD.
 */

function validateName(value) {
  if (typeof value !== "string") {
    throw new AppError("O nome é obrigatório.");
  }

  const name = value.trim();

  if (name.length === 0) {
    throw new AppError("O nome não pode estar vazio.");
  }

  if (name.length > 200) {
    throw new AppError("O nome deve ter no máximo 200 caracteres.");
  }

  return name;
}

function validateEmail(value) {
  if (typeof value !== "string") {
    throw new AppError("O e-mail é obrigatório.");
  }

  const email = value.trim().toLowerCase();

  if (email.length === 0) {
    throw new AppError("O e-mail não pode estar vazio.");
  }

  if (email.length > 254) {
    throw new AppError("O e-mail deve ter no máximo 254 caracteres.");
  }

  /*
   * Validação prática para uma aplicação de cadastro:
   * - deve haver exatamente uma separação principal por @;
   * - não permite espaços;
   * - exige domínio com pelo menos um ponto.
   *
   * A expressão não tenta implementar integralmente toda a RFC 5322,
   * pois formatos extremamente incomuns não são apropriados para esta CLI.
   */
  const emailPattern = /^[^\s@]+@[^\s@.]+(?:\.[^\s@.]+)+$/;

  if (!emailPattern.test(email)) {
    throw new AppError(
      "Formato de e-mail inválido. Exemplo esperado: usuario@dominio.com"
    );
  }

  return email;
}

function validateBirthDate(value) {
  if (typeof value !== "string") {
    throw new AppError("A data de nascimento é obrigatória.");
  }

  const birthDate = value.trim();
  const formatPattern = /^\d{4}-\d{2}-\d{2}$/;

  if (!formatPattern.test(birthDate)) {
    throw new AppError(
      "Data de nascimento inválida. Use o formato YYYY-MM-DD."
    );
  }

  const parsedDate = new Date(`${birthDate}T00:00:00.000Z`);

  if (
    Number.isNaN(parsedDate.getTime()) ||
    parsedDate.toISOString().slice(0, 10) !== birthDate
  ) {
    throw new AppError(
      "A data de nascimento informada não existe. Use YYYY-MM-DD."
    );
  }

  const today = new Date().toISOString().slice(0, 10);

  if (birthDate > today) {
    throw new AppError(
      "A data de nascimento não pode estar no futuro."
    );
  }

  return birthDate;
}

function validateId(value) {
  const text = String(value ?? "").trim();

  if (!/^[1-9]\d*$/.test(text)) {
    throw new AppError("O ID deve ser um número inteiro positivo.");
  }

  const id = Number(text);

  if (!Number.isSafeInteger(id)) {
    throw new AppError("O ID informado é maior do que o limite suportado.");
  }

  return id;
}

module.exports = {
  validateName,
  validateEmail,
  validateBirthDate,
  validateId
};
```

---

### `src/database.js`

```javascript
const fs = require("node:fs");
const path = require("node:path");
const Database = require("better-sqlite3");

function getDatabasePath() {
  /*
   * Por padrão, o banco fica em data/users.db.
   * A variável DATABASE_PATH pode ser usada para escolher outro local.
   */
  const configuredPath = process.env.DATABASE_PATH;

  if (configuredPath) {
    return path.resolve(process.cwd(), configuredPath);
  }

  return path.resolve(__dirname, "..", "data", "users.db");
}

function openDatabase() {
  const databasePath = getDatabasePath();
  const directory = path.dirname(databasePath);

  fs.mkdirSync(directory, { recursive: true });

  const database = new Database(databasePath);

  database.pragma("journal_mode = WAL");
  database.pragma("foreign_keys = ON");
  database.pragma("busy_timeout = 5000");

  const schemaPath = path.resolve(__dirname, "..", "schema.sql");
  const schema = fs.readFileSync(schemaPath, "utf8");

  /*
   * O schema é aplicado em toda abertura. CREATE TABLE IF NOT EXISTS
   * torna a operação segura e idempotente.
   */
  database.exec(schema);

  return {
    database,
    databasePath
  };
}

function createUser(database, user) {
  const statement = database.prepare(`
    INSERT INTO users (name, email, birth_date)
    VALUES (@name, @email, @birthDate)
  `);

  const result = statement.run(user);

  return findUserById(database, Number(result.lastInsertRowid));
}

function listUsers(database) {
  return database
    .prepare(`
      SELECT
        id,
        name,
        email,
        birth_date AS birthDate,
        created_at AS createdAt,
        updated_at AS updatedAt
      FROM users
      ORDER BY id ASC
    `)
    .all();
}

function findUserById(database, id) {
  return database
    .prepare(`
      SELECT
        id,
        name,
        email,
        birth_date AS birthDate,
        created_at AS createdAt,
        updated_at AS updatedAt
      FROM users
      WHERE id = ?
    `)
    .get(id);
}

function updateUser(database, id, fields) {
  /*
   * As colunas não são recebidas diretamente do usuário.
   * O mapeamento explícito evita injeção em identificadores SQL.
   */
  const columnMapping = {
    name: "name",
    email: "email",
    birthDate: "birth_date"
  };

  const assignments = [];
  const parameters = { id };

  for (const [field, value] of Object.entries(fields)) {
    const column = columnMapping[field];

    if (!column) {
      continue;
    }

    assignments.push(`${column} = @${field}`);
    parameters[field] = value;
  }

  if (assignments.length === 0) {
    return findUserById(database, id);
  }

  assignments.push(
    "updated_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')"
  );

  const statement = database.prepare(`
    UPDATE users
    SET ${assignments.join(", ")}
    WHERE id = @id
  `);

  const result = statement.run(parameters);

  if (result.changes === 0) {
    return undefined;
  }

  return findUserById(database, id);
}

function removeUser(database, id) {
  const existingUser = findUserById(database, id);

  if (!existingUser) {
    return undefined;
  }

  database
    .prepare("DELETE FROM users WHERE id = ?")
    .run(id);

  return existingUser;
}

module.exports = {
  getDatabasePath,
  openDatabase,
  createUser,
  listUsers,
  findUserById,
  updateUser,
  removeUser
};
```

---

### `src/cli.js`

```javascript
#!/usr/bin/env node

const { AppError } = require("./errors");
const {
  validateName,
  validateEmail,
  validateBirthDate,
  validateId
} = require("./validators");
const {
  openDatabase,
  createUser,
  listUsers,
  updateUser,
  removeUser
} = require("./database");

const HELP_TEXT = `
Gerenciador de usuários

Uso:
  npm start -- <comando> [argumentos] [opções]

Comandos:
  init
      Cria ou inicializa o banco de dados.

  cadastrar --nome <nome> --email <email> --nascimento <YYYY-MM-DD>
      Cadastra um novo usuário.

  listar
      Lista todos os usuários.

  atualizar <id> [--nome <nome>] [--email <email>] [--nascimento <YYYY-MM-DD>]
      Atualiza um ou mais campos de um usuário.

  remover <id>
      Remove um usuário.

Aliases em inglês:
  add      -> cadastrar
  list     -> listar
  update   -> atualizar
  remove   -> remover
  help     -> ajuda

Exemplos:
  npm start -- init

  npm start -- cadastrar \\
    --nome "Maria Silva" \\
    --email "maria@example.com" \\
    --nascimento "1990-05-20"

  npm start -- listar

  npm start -- atualizar 1 --email "novo-email@example.com"

  npm start -- remover 1

Banco alternativo:
  DATABASE_PATH=/caminho/usuarios.db npm start -- listar
`.trim();

const COMMAND_ALIASES = {
  init: "init",
  cadastrar: "cadastrar",
  add: "cadastrar",
  listar: "listar",
  list: "listar",
  atualizar: "atualizar",
  update: "atualizar",
  remover: "remover",
  remove: "remover",
  ajuda: "ajuda",
  help: "ajuda"
};

function parseArguments(tokens) {
  const options = {};
  const positionals = [];

  for (let index = 0; index < tokens.length; index += 1) {
    const token = tokens[index];

    if (!token.startsWith("--")) {
      positionals.push(token);
      continue;
    }

    const equalsIndex = token.indexOf("=");
    let optionName;
    let optionValue;

    if (equalsIndex >= 0) {
      optionName = token.slice(2, equalsIndex);
      optionValue = token.slice(equalsIndex + 1);
    } else {
      optionName = token.slice(2);
      optionValue = tokens[index + 1];

      if (
        optionValue === undefined ||
        optionValue.startsWith("--")
      ) {
        throw new AppError(
          `A opção --${optionName} precisa de um valor.`
        );
      }

      index += 1;
    }

    if (!optionName) {
      throw new AppError("Foi informada uma opção inválida.");
    }

    if (Object.hasOwn(options, optionName)) {
      throw new AppError(
        `A opção --${optionName} foi informada mais de uma vez.`
      );
    }

    options[optionName] = optionValue;
  }

  return {
    options,
    positionals
  };
}

function ensureAllowedOptions(options, allowedOptions) {
  for (const optionName of Object.keys(options)) {
    if (!allowedOptions.includes(optionName)) {
      throw new AppError(`Opção desconhecida: --${optionName}`);
    }
  }
}

function ensureNoPositionals(positionals, command) {
  if (positionals.length > 0) {
    throw new AppError(
      `O comando "${command}" não aceita argumentos posicionais.`
    );
  }
}

function requireOption(options, optionName) {
  if (!Object.hasOwn(options, optionName)) {
    throw new AppError(
      `A opção obrigatória --${optionName} não foi informada.`
    );
  }

  return options[optionName];
}

function formatTable(rows) {
  const columns = [
    { key: "id", label: "ID" },
    { key: "name", label: "Nome" },
    { key: "email", label: "E-mail" },
    { key: "birthDate", label: "Nascimento" },
    { key: "createdAt", label: "Criado em" },
    { key: "updatedAt", label: "Atualizado em" }
  ];

  const widths = columns.map((column) => {
    const contentWidths = rows.map((row) =>
      String(row[column.key] ?? "").length
    );

    return Math.max(column.label.length, ...contentWidths);
  });

  const renderSeparator = () =>
    `+-${widths.map((width) => "-".repeat(width)).join("-+-")}-+`;

  const renderRow = (values) =>
    `| ${values
      .map((value, index) =>
        String(value ?? "").padEnd(widths[index], " ")
      )
      .join(" | ")} |`;

  const output = [
    renderSeparator(),
    renderRow(columns.map((column) => column.label)),
    renderSeparator()
  ];

  for (const row of rows) {
    output.push(
      renderRow(columns.map((column) => row[column.key]))
    );
  }

  output.push(renderSeparator());

  return output.join("\n");
}

function printUser(user) {
  console.log(`ID: ${user.id}`);
  console.log(`Nome: ${user.name}`);
  console.log(`E-mail: ${user.email}`);
  console.log(`Nascimento: ${user.birthDate}`);
  console.log(`Criado em: ${user.createdAt}`);
  console.log(`Atualizado em: ${user.updatedAt}`);
}

function handleInit(databasePath, positionals, options) {
  ensureNoPositionals(positionals, "init");
  ensureAllowedOptions(options, []);

  console.log("Banco de dados inicializado com sucesso.");
  console.log(`Arquivo: ${databasePath}`);
}

function handleCreate(database, positionals, options) {
  ensureNoPositionals(positionals, "cadastrar");
  ensureAllowedOptions(options, [
    "nome",
    "email",
    "nascimento"
  ]);

  const user = {
    name: validateName(requireOption(options, "nome")),
    email: validateEmail(requireOption(options, "email")),
    birthDate: validateBirthDate(
      requireOption(options, "nascimento")
    )
  };

  const createdUser = createUser(database, user);

  console.log("Usuário cadastrado com sucesso.");
  printUser(createdUser);
}

function handleList(database, positionals, options) {
  ensureNoPositionals(positionals, "listar");
  ensureAllowedOptions(options, []);

  const users = listUsers(database);

  if (users.length === 0) {
    console.log("Nenhum usuário cadastrado.");
    return;
  }

  console.log(formatTable(users));
  console.log(
    `\nTotal: ${users.length} usuário(s).`
  );
}

function handleUpdate(database, positionals, options) {
  ensureAllowedOptions(options, [
    "nome",
    "email",
    "nascimento"
  ]);

  if (positionals.length !== 1) {
    throw new AppError(
      "Uso esperado: atualizar <id> [opções]"
    );
  }

  if (Object.keys(options).length === 0) {
    throw new AppError(
      "Informe pelo menos um campo para atualizar: " +
        "--nome, --email ou --nascimento."
    );
  }

  const id = validateId(positionals[0]);
  const fields = {};

  if (Object.hasOwn(options, "nome")) {
    fields.name = validateName(options.nome);
  }

  if (Object.hasOwn(options, "email")) {
    fields.email = validateEmail(options.email);
  }

  if (Object.hasOwn(options, "nascimento")) {
    fields.birthDate = validateBirthDate(options.nascimento);
  }

  const updatedUser = updateUser(database, id, fields);

  if (!updatedUser) {
    throw new AppError(`Usuário com ID ${id} não encontrado.`);
  }

  console.log("Usuário atualizado com sucesso.");
  printUser(updatedUser);
}

function handleRemove(database, positionals, options) {
  ensureAllowedOptions(options, []);

  if (positionals.length !== 1) {
    throw new AppError("Uso esperado: remover <id>");
  }

  const id = validateId(positionals[0]);
  const removedUser = removeUser(database, id);

  if (!removedUser) {
    throw new AppError(`Usuário com ID ${id} não encontrado.`);
  }

  console.log("Usuário removido com sucesso.");
  console.log(`ID: ${removedUser.id}`);
  console.log(`Nome: ${removedUser.name}`);
  console.log(`E-mail: ${removedUser.email}`);
}

function isUniqueEmailError(error) {
  return (
    error &&
    (
      error.code === "SQLITE_CONSTRAINT_UNIQUE" ||
      error.code === "SQLITE_CONSTRAINT_PRIMARYKEY" ||
      (
        error.code === "SQLITE_CONSTRAINT" &&
        String(error.message).includes("users.email")
      )
    )
  );
}

function main() {
  const rawArguments = process.argv.slice(2);

  if (
    rawArguments.length === 0 ||
    rawArguments[0] === "--help" ||
    rawArguments[0] === "-h"
  ) {
    console.log(HELP_TEXT);
    return;
  }

  const requestedCommand = rawArguments[0].toLowerCase();
  const command = COMMAND_ALIASES[requestedCommand];

  if (!command) {
    throw new AppError(
      `Comando desconhecido: ${rawArguments[0]}\n\n${HELP_TEXT}`
    );
  }

  if (command === "ajuda") {
    console.log(HELP_TEXT);
    return;
  }

  const { options, positionals } = parseArguments(
    rawArguments.slice(1)
  );

  const { database, databasePath } = openDatabase();

  try {
    switch (command) {
      case "init":
        handleInit(databasePath, positionals, options);
        break;

      case "cadastrar":
        handleCreate(database, positionals, options);
        break;

      case "listar":
        handleList(database, positionals, options);
        break;

      case "atualizar":
        handleUpdate(database, positionals, options);
        break;

      case "remover":
        handleRemove(database, positionals, options);
        break;

      default:
        throw new AppError(`Comando não implementado: ${command}`);
    }
  } finally {
    database.close();
  }
}

try {
  main();
} catch (error) {
  if (isUniqueEmailError(error)) {
    console.error(
      "Erro: já existe um usuário cadastrado com este e-mail."
    );
    process.exitCode = 1;
  } else if (error instanceof AppError) {
    console.error(`Erro: ${error.message}`);
    process.exitCode = error.exitCode;
  } else {
    console.error(
      "Erro inesperado ao executar a operação."
    );

    if (process.env.DEBUG === "1") {
      console.error(error);
    }

    process.exitCode = 1;
  }
}
```

---

### `.gitignore`

```gitignore
node_modules/
data/
*.db
*.db-shm
*.db-wal
npm-debug.log*
.DS_Store
```

---

### `README.md`

```markdown
# Gerenciador de usuários CLI

Aplicação de linha de comando em Node.js para cadastrar, listar, atualizar e
remover usuários, persistindo os dados em SQLite.

Cada usuário possui:

- nome;
- e-mail;
- data de nascimento.

## Requisitos

- Node.js 20 ou superior;
- npm.

## Instalação

Dentro da pasta do projeto, execute:

```bash
npm install
```

## Inicialização do banco

```bash
npm run init-db
```

O banco será criado por padrão em:

```text
data/users.db
```

O schema também é aplicado automaticamente sempre que a aplicação é iniciada.

## Comandos

### Exibir ajuda

```bash
npm start -- ajuda
```

### Cadastrar usuário

```bash
npm start -- cadastrar \
  --nome "Maria Silva" \
  --email "maria@example.com" \
  --nascimento "1990-05-20"
```

Também é possível usar opções com `=`:

```bash
npm start -- cadastrar \
  --nome="Maria Silva" \
  --email="maria@example.com" \
  --nascimento="1990-05-20"
```

### Listar usuários

```bash
npm start -- listar
```

### Atualizar usuário

Atualizar somente o nome:

```bash
npm start -- atualizar 1 --nome "Maria Souza"
```

Atualizar vários campos:

```bash
npm start -- atualizar 1 \
  --email "maria.souza@example.com" \
  --nascimento "1991-06-15"
```

### Remover usuário

```bash
npm start -- remover 1
```

## Aliases em inglês

Os seguintes aliases também são aceitos:

```text
add      -> cadastrar
list     -> listar
update   -> atualizar
remove   -> remover
help     -> ajuda
```

Exemplo:

```bash
npm start -- list
```

## Escolher outro arquivo de banco

Use a variável de ambiente `DATABASE_PATH`:

Linux/macOS:

```bash
DATABASE_PATH=/tmp/usuarios.db npm start -- listar
```

Windows PowerShell:

```powershell
$env:DATABASE_PATH="C:\temp\usuarios.db"
npm start -- listar
```

## Validações

A aplicação:

- impede nomes vazios;
- valida o formato do e-mail;
- normaliza e-mails para letras minúsculas;
- impede e-mails duplicados, inclusive com diferenças entre maiúsculas e
  minúsculas;
- exige datas no formato `YYYY-MM-DD`;
- verifica se a data realmente existe;
- impede datas de nascimento futuras;
- valida IDs como números inteiros positivos;
- informa quando um usuário não é encontrado.

## Diagnóstico

Erros internos não exibem detalhes técnicos por padrão. Para mostrar o erro
completo durante desenvolvimento, use:

```bash
DEBUG=1 npm start -- listar
```
```

## Execução rápida

Após criar os arquivos:

```bash
npm install
npm run init-db
npm start -- cadastrar --nome "Ana Lima" --email "ana@example.com" --nascimento "1988-10-12"
npm start -- listar
npm start -- atualizar 1 --nome "Ana Souza"
npm start -- remover 1
```