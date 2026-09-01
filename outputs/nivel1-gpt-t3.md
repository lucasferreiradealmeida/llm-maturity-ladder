<!--
nivel: 1 - CRUD com persistencia em banco
provider: gpt
model: gpt-5.6
tentativa: 3
temperature: 0.2
timestamp: 2026-08-31T08:20:02.171Z
metadata: {"model":"gpt-5.6-sol","usage":{"prompt_tokens":221,"completion_tokens":7543,"total_tokens":7764,"prompt_tokens_details":{"cached_tokens":0,"cache_write_tokens":0,"audio_tokens":0},"completion_tokens_details":{"reasoning_tokens":1537,"audio_tokens":0,"accepted_prediction_tokens":0,"rejected_prediction_tokens":0}},"finish_reason":"stop"}
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

Abaixo está uma implementação completa em Node.js com SQLite. A aplicação usa comandos em português, inicializa automaticamente o banco e também inclui um comando explícito para criação do schema.

## Estrutura do projeto

```text
usuarios-cli/
├── package.json
├── schema.sql
├── .gitignore
├── README.md
└── src/
    ├── cli.js
    ├── database.js
    └── validation.js
```

---

### Arquivo: `package.json`

```json
{
  "name": "usuarios-cli",
  "version": "1.0.0",
  "description": "Aplicação CLI para gerenciamento de usuários com Node.js e SQLite",
  "main": "src/cli.js",
  "type": "commonjs",
  "bin": {
    "usuarios": "src/cli.js"
  },
  "scripts": {
    "start": "node src/cli.js",
    "init": "node src/cli.js inicializar"
  },
  "engines": {
    "node": ">=20"
  },
  "dependencies": {
    "better-sqlite3": "^11.8.1"
  }
}
```

---

### Arquivo: `schema.sql`

```sql
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    nome TEXT NOT NULL
        CHECK (length(trim(nome)) BETWEEN 1 AND 150),

    email TEXT NOT NULL COLLATE NOCASE
        CHECK (length(trim(email)) BETWEEN 3 AND 254),

    data_nascimento TEXT NOT NULL
        CHECK (
            length(data_nascimento) = 10
            AND data_nascimento GLOB
                '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
        ),

    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT usuarios_email_unico UNIQUE (email)
);

CREATE INDEX IF NOT EXISTS idx_usuarios_nome
    ON usuarios(nome);

CREATE TRIGGER IF NOT EXISTS trg_usuarios_atualizado_em
AFTER UPDATE ON usuarios
FOR EACH ROW
BEGIN
    UPDATE usuarios
    SET atualizado_em = CURRENT_TIMESTAMP
    WHERE id = OLD.id;
END;
```

---

### Arquivo: `src/validation.js`

```javascript
"use strict";

class ValidationError extends Error {
  constructor(message) {
    super(message);
    this.name = "ValidationError";
  }
}

/*
 * A validação de e-mail é intencionalmente pragmática:
 * verifica a estrutura básica "algo@dominio.extensao", espaços e limites
 * de tamanho, sem tentar implementar integralmente todas as regras da RFC.
 */
function validateEmail(value) {
  if (typeof value !== "string") {
    throw new ValidationError("O e-mail deve ser informado.");
  }

  const email = value.trim().toLowerCase();

  if (email.length === 0) {
    throw new ValidationError("O e-mail não pode estar vazio.");
  }

  if (email.length > 254) {
    throw new ValidationError("O e-mail deve possuir no máximo 254 caracteres.");
  }

  const basicEmailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (!basicEmailPattern.test(email)) {
    throw new ValidationError(
      "Formato de e-mail inválido. Exemplo esperado: usuario@dominio.com."
    );
  }

  return email;
}

function validateName(value) {
  if (typeof value !== "string") {
    throw new ValidationError("O nome deve ser informado.");
  }

  const name = value.trim();

  if (name.length === 0) {
    throw new ValidationError("O nome não pode estar vazio.");
  }

  if (name.length > 150) {
    throw new ValidationError("O nome deve possuir no máximo 150 caracteres.");
  }

  return name;
}

function isLeapYear(year) {
  return year % 400 === 0 || (year % 4 === 0 && year % 100 !== 0);
}

function daysInMonth(year, month) {
  const days = [
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

  return days[month - 1];
}

function getTodayAsIsoDate() {
  const now = new Date();
  const year = String(now.getFullYear()).padStart(4, "0");
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");

  return `${year}-${month}-${day}`;
}

/*
 * A data é armazenada no SQLite como texto no formato ISO YYYY-MM-DD.
 * Essa representação mantém a ordenação cronológica e evita problemas de
 * fuso horário para uma data que não possui componente de hora.
 */
function validateBirthDate(value) {
  if (typeof value !== "string") {
    throw new ValidationError("A data de nascimento deve ser informada.");
  }

  const birthDate = value.trim();
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(birthDate);

  if (!match) {
    throw new ValidationError(
      "Data de nascimento inválida. Use o formato YYYY-MM-DD, por exemplo 1990-05-21."
    );
  }

  const year = Number(match[1]);
  const month = Number(match[2]);
  const day = Number(match[3]);

  if (year < 1) {
    throw new ValidationError("O ano da data de nascimento é inválido.");
  }

  if (month < 1 || month > 12) {
    throw new ValidationError("O mês da data de nascimento é inválido.");
  }

  if (day < 1 || day > daysInMonth(year, month)) {
    throw new ValidationError("O dia da data de nascimento é inválido.");
  }

  // Como se trata de nascimento, datas futuras não são aceitas.
  if (birthDate > getTodayAsIsoDate()) {
    throw new ValidationError(
      "A data de nascimento não pode estar no futuro."
    );
  }

  return birthDate;
}

function validateId(value) {
  const text = String(value ?? "").trim();

  if (!/^\d+$/.test(text)) {
    throw new ValidationError("O ID deve ser um número inteiro positivo.");
  }

  const id = Number(text);

  if (!Number.isSafeInteger(id) || id <= 0) {
    throw new ValidationError("O ID deve ser um número inteiro positivo.");
  }

  return id;
}

module.exports = {
  ValidationError,
  validateEmail,
  validateName,
  validateBirthDate,
  validateId
};
```

---

### Arquivo: `src/database.js`

```javascript
"use strict";

const fs = require("fs");
const path = require("path");
const Database = require("better-sqlite3");

class DatabaseError extends Error {
  constructor(message, cause) {
    super(message);
    this.name = "DatabaseError";
    this.cause = cause;
  }
}

class DuplicateEmailError extends Error {
  constructor(email) {
    super(`Já existe um usuário cadastrado com o e-mail "${email}".`);
    this.name = "DuplicateEmailError";
  }
}

class UserNotFoundError extends Error {
  constructor(id) {
    super(`Usuário com ID ${id} não encontrado.`);
    this.name = "UserNotFoundError";
  }
}

function resolveDatabasePath() {
  /*
   * Por padrão, o banco fica em data/usuarios.db, relativamente ao diretório
   * no qual o comando foi executado. O caminho pode ser alterado com a
   * variável de ambiente USERS_DB_PATH.
   */
  const configuredPath =
    process.env.USERS_DB_PATH || path.join("data", "usuarios.db");

  return path.resolve(configuredPath);
}

function isUniqueConstraintError(error) {
  return (
    error &&
    typeof error.code === "string" &&
    error.code.startsWith("SQLITE_CONSTRAINT") &&
    /unique/i.test(error.message)
  );
}

class UserDatabase {
  constructor(databasePath = resolveDatabasePath()) {
    this.databasePath = databasePath;

    fs.mkdirSync(path.dirname(databasePath), { recursive: true });

    this.db = new Database(databasePath);

    this.db.pragma("foreign_keys = ON");
    this.db.pragma("journal_mode = WAL");
    this.db.pragma("busy_timeout = 5000");
  }

  initialize() {
    const schemaPath = path.resolve(__dirname, "..", "schema.sql");

    try {
      const schema = fs.readFileSync(schemaPath, "utf8");
      this.db.exec(schema);
    } catch (error) {
      throw new DatabaseError(
        `Não foi possível inicializar o banco de dados: ${error.message}`,
        error
      );
    }
  }

  createUser({ nome, email, dataNascimento }) {
    const statement = this.db.prepare(`
      INSERT INTO usuarios (nome, email, data_nascimento)
      VALUES (@nome, @email, @dataNascimento)
    `);

    try {
      const result = statement.run({
        nome,
        email,
        dataNascimento
      });

      return this.findUserById(Number(result.lastInsertRowid));
    } catch (error) {
      if (isUniqueConstraintError(error)) {
        throw new DuplicateEmailError(email);
      }

      throw new DatabaseError(
        `Não foi possível cadastrar o usuário: ${error.message}`,
        error
      );
    }
  }

  listUsers() {
    try {
      return this.db
        .prepare(`
          SELECT
            id,
            nome,
            email,
            data_nascimento AS dataNascimento,
            criado_em AS criadoEm,
            atualizado_em AS atualizadoEm
          FROM usuarios
          ORDER BY nome COLLATE NOCASE ASC, id ASC
        `)
        .all();
    } catch (error) {
      throw new DatabaseError(
        `Não foi possível listar os usuários: ${error.message}`,
        error
      );
    }
  }

  findUserById(id) {
    try {
      return (
        this.db
          .prepare(`
            SELECT
              id,
              nome,
              email,
              data_nascimento AS dataNascimento,
              criado_em AS criadoEm,
              atualizado_em AS atualizadoEm
            FROM usuarios
            WHERE id = ?
          `)
          .get(id) || null
      );
    } catch (error) {
      throw new DatabaseError(
        `Não foi possível consultar o usuário: ${error.message}`,
        error
      );
    }
  }

  updateUser(id, changes) {
    const currentUser = this.findUserById(id);

    if (!currentUser) {
      throw new UserNotFoundError(id);
    }

    const columnMapping = {
      nome: "nome",
      email: "email",
      dataNascimento: "data_nascimento"
    };

    const entries = Object.entries(changes).filter(
      ([key, value]) =>
        Object.prototype.hasOwnProperty.call(columnMapping, key) &&
        value !== undefined
    );

    if (entries.length === 0) {
      return currentUser;
    }

    const assignments = entries
      .map(([key]) => `${columnMapping[key]} = @${key}`)
      .join(", ");

    const params = { id };

    for (const [key, value] of entries) {
      params[key] = value;
    }

    try {
      this.db
        .prepare(`
          UPDATE usuarios
          SET ${assignments}
          WHERE id = @id
        `)
        .run(params);

      return this.findUserById(id);
    } catch (error) {
      if (isUniqueConstraintError(error)) {
        throw new DuplicateEmailError(changes.email);
      }

      throw new DatabaseError(
        `Não foi possível atualizar o usuário: ${error.message}`,
        error
      );
    }
  }

  deleteUser(id) {
    try {
      const result = this.db
        .prepare("DELETE FROM usuarios WHERE id = ?")
        .run(id);

      if (result.changes === 0) {
        throw new UserNotFoundError(id);
      }

      return true;
    } catch (error) {
      if (error instanceof UserNotFoundError) {
        throw error;
      }

      throw new DatabaseError(
        `Não foi possível remover o usuário: ${error.message}`,
        error
      );
    }
  }

  close() {
    if (this.db && this.db.open) {
      this.db.close();
    }
  }
}

module.exports = {
  UserDatabase,
  DatabaseError,
  DuplicateEmailError,
  UserNotFoundError,
  resolveDatabasePath
};
```

---

### Arquivo: `src/cli.js`

```javascript
#!/usr/bin/env node
"use strict";

const readline = require("readline/promises");
const { stdin, stdout } = require("process");

const {
  UserDatabase,
  DatabaseError,
  DuplicateEmailError,
  UserNotFoundError,
  resolveDatabasePath
} = require("./database");

const {
  ValidationError,
  validateEmail,
  validateName,
  validateBirthDate,
  validateId
} = require("./validation");

class CliError extends Error {
  constructor(message) {
    super(message);
    this.name = "CliError";
  }
}

const COMMAND_ALIASES = {
  inicializar: "inicializar",
  init: "inicializar",

  cadastrar: "cadastrar",
  adicionar: "cadastrar",
  add: "cadastrar",

  listar: "listar",
  list: "listar",

  atualizar: "atualizar",
  update: "atualizar",

  remover: "remover",
  remove: "remover",
  delete: "remover",

  ajuda: "ajuda",
  help: "ajuda"
};

const BOOLEAN_OPTIONS = new Set(["sim", "ajuda", "help"]);

function printHelp() {
  console.log(`
Gerenciador de usuários

Uso:
  node src/cli.js <comando> [argumentos] [opções]

Comandos:
  inicializar
      Cria o arquivo do banco e aplica o schema.

  cadastrar --nome <nome> --email <email> --nascimento <YYYY-MM-DD>
      Cadastra um novo usuário.

  listar
      Lista todos os usuários cadastrados.

  atualizar <id> [--nome <nome>] [--email <email>] [--nascimento <YYYY-MM-DD>]
      Atualiza um ou mais campos de um usuário.

  remover <id> [--sim]
      Remove um usuário. Sem --sim, solicita confirmação.

  ajuda
      Exibe esta mensagem.

Exemplos:
  node src/cli.js inicializar

  node src/cli.js cadastrar \\
    --nome "Maria da Silva" \\
    --email "maria@example.com" \\
    --nascimento "1990-05-21"

  node src/cli.js listar

  node src/cli.js atualizar 1 --nome "Maria Souza"

  node src/cli.js atualizar 1 \\
    --email "maria.souza@example.com" \\
    --nascimento "1990-05-22"

  node src/cli.js remover 1
  node src/cli.js remover 1 --sim

Também é possível instalar o comando globalmente no projeto:
  npm link
  usuarios listar

Banco padrão:
  ${resolveDatabasePath()}

Para usar outro arquivo:
  USERS_DB_PATH=/caminho/usuarios.db node src/cli.js listar
`.trim());
}

function parseArguments(tokens) {
  const options = {};
  const positionals = [];

  for (let index = 0; index < tokens.length; index += 1) {
    const token = tokens[index];

    if (!token.startsWith("--")) {
      positionals.push(token);
      continue;
    }

    const optionText = token.slice(2);

    if (!optionText) {
      throw new CliError("Foi encontrada uma opção vazia.");
    }

    const equalIndex = optionText.indexOf("=");
    let key;
    let value;

    if (equalIndex >= 0) {
      key = optionText.slice(0, equalIndex);
      value = optionText.slice(equalIndex + 1);
    } else {
      key = optionText;

      if (BOOLEAN_OPTIONS.has(key)) {
        value = true;
      } else {
        const nextToken = tokens[index + 1];

        if (nextToken === undefined || nextToken.startsWith("--")) {
          throw new CliError(`A opção --${key} precisa de um valor.`);
        }

        value = nextToken;
        index += 1;
      }
    }

    if (Object.prototype.hasOwnProperty.call(options, key)) {
      throw new CliError(`A opção --${key} foi informada mais de uma vez.`);
    }

    options[key] = value;
  }

  return { options, positionals };
}

function validateAllowedOptions(options, allowedOptions) {
  for (const option of Object.keys(options)) {
    if (!allowedOptions.includes(option)) {
      throw new CliError(`Opção desconhecida: --${option}.`);
    }
  }
}

function requireOption(options, optionName) {
  if (!Object.prototype.hasOwnProperty.call(options, optionName)) {
    throw new CliError(`A opção --${optionName} é obrigatória.`);
  }

  return options[optionName];
}

function ensureNoPositionals(positionals, command) {
  if (positionals.length > 0) {
    throw new CliError(
      `O comando "${command}" não aceita argumentos posicionais.`
    );
  }
}

function printUser(user) {
  console.log(`ID: ${user.id}`);
  console.log(`Nome: ${user.nome}`);
  console.log(`E-mail: ${user.email}`);
  console.log(`Data de nascimento: ${user.dataNascimento}`);
}

function handleInitialize(db, parsed) {
  validateAllowedOptions(parsed.options, []);
  ensureNoPositionals(parsed.positionals, "inicializar");

  console.log("Banco de dados inicializado com sucesso.");
  console.log(`Arquivo: ${db.databasePath}`);
}

function handleCreate(db, parsed) {
  validateAllowedOptions(parsed.options, [
    "nome",
    "email",
    "nascimento"
  ]);
  ensureNoPositionals(parsed.positionals, "cadastrar");

  const nome = validateName(requireOption(parsed.options, "nome"));
  const email = validateEmail(requireOption(parsed.options, "email"));
  const dataNascimento = validateBirthDate(
    requireOption(parsed.options, "nascimento")
  );

  const user = db.createUser({
    nome,
    email,
    dataNascimento
  });

  console.log("Usuário cadastrado com sucesso.");
  printUser(user);
}

function handleList(db, parsed) {
  validateAllowedOptions(parsed.options, []);
  ensureNoPositionals(parsed.positionals, "listar");

  const users = db.listUsers();

  if (users.length === 0) {
    console.log("Nenhum usuário cadastrado.");
    return;
  }

  console.table(
    users.map((user) => ({
      ID: user.id,
      Nome: user.nome,
      "E-mail": user.email,
      Nascimento: user.dataNascimento
    }))
  );

  console.log(
    `${users.length} usuário${users.length === 1 ? "" : "s"} encontrado${
      users.length === 1 ? "" : "s"
    }.`
  );
}

function handleUpdate(db, parsed) {
  validateAllowedOptions(parsed.options, [
    "nome",
    "email",
    "nascimento"
  ]);

  if (parsed.positionals.length !== 1) {
    throw new CliError(
      "Informe exatamente um ID. Exemplo: atualizar 1 --nome \"Novo nome\"."
    );
  }

  if (Object.keys(parsed.options).length === 0) {
    throw new CliError(
      "Informe pelo menos um campo para atualizar: --nome, --email ou --nascimento."
    );
  }

  const id = validateId(parsed.positionals[0]);
  const changes = {};

  if (Object.prototype.hasOwnProperty.call(parsed.options, "nome")) {
    changes.nome = validateName(parsed.options.nome);
  }

  if (Object.prototype.hasOwnProperty.call(parsed.options, "email")) {
    changes.email = validateEmail(parsed.options.email);
  }

  if (Object.prototype.hasOwnProperty.call(parsed.options, "nascimento")) {
    changes.dataNascimento = validateBirthDate(parsed.options.nascimento);
  }

  const user = db.updateUser(id, changes);

  console.log("Usuário atualizado com sucesso.");
  printUser(user);
}

async function askForDeleteConfirmation(user) {
  const prompt = readline.createInterface({
    input: stdin,
    output: stdout
  });

  try {
    console.log("Usuário que será removido:");
    printUser(user);

    const answer = await prompt.question(
      'Confirma a remoção? Digite "sim" para continuar: '
    );

    return ["sim", "s"].includes(answer.trim().toLowerCase());
  } finally {
    prompt.close();
  }
}

async function handleDelete(db, parsed) {
  validateAllowedOptions(parsed.options, ["sim"]);

  if (parsed.positionals.length !== 1) {
    throw new CliError(
      "Informe exatamente um ID. Exemplo: remover 1."
    );
  }

  const id = validateId(parsed.positionals[0]);
  const user = db.findUserById(id);

  if (!user) {
    throw new UserNotFoundError(id);
  }

  let confirmed = parsed.options.sim === true;

  if (!confirmed) {
    confirmed = await askForDeleteConfirmation(user);
  }

  if (!confirmed) {
    console.log("Remoção cancelada. Nenhuma alteração foi realizada.");
    return;
  }

  db.deleteUser(id);
  console.log(`Usuário com ID ${id} removido com sucesso.`);
}

function normalizeCommand(rawCommand) {
  if (!rawCommand) {
    return null;
  }

  return COMMAND_ALIASES[rawCommand.toLowerCase()] || null;
}

async function main() {
  const rawArguments = process.argv.slice(2);

  if (
    rawArguments.length === 0 ||
    rawArguments[0] === "--ajuda" ||
    rawArguments[0] === "--help"
  ) {
    printHelp();
    return;
  }

  const rawCommand = rawArguments[0];
  const command = normalizeCommand(rawCommand);

  if (!command) {
    throw new CliError(
      `Comando desconhecido: "${rawCommand}". Use "ajuda" para ver os comandos disponíveis.`
    );
  }

  if (command === "ajuda") {
    printHelp();
    return;
  }

  const parsed = parseArguments(rawArguments.slice(1));
  const db = new UserDatabase();

  try {
    /*
     * O schema é aplicado automaticamente em todos os comandos. Como o SQL
     * utiliza IF NOT EXISTS, a operação é idempotente e também permite usar a
     * aplicação sem executar manualmente o comando "inicializar".
     */
    db.initialize();

    switch (command) {
      case "inicializar":
        handleInitialize(db, parsed);
        break;

      case "cadastrar":
        handleCreate(db, parsed);
        break;

      case "listar":
        handleList(db, parsed);
        break;

      case "atualizar":
        handleUpdate(db, parsed);
        break;

      case "remover":
        await handleDelete(db, parsed);
        break;

      default:
        throw new CliError(`Comando não implementado: ${command}.`);
    }
  } finally {
    db.close();
  }
}

main().catch((error) => {
  const expectedErrors = [
    CliError,
    ValidationError,
    DuplicateEmailError,
    UserNotFoundError,
    DatabaseError
  ];

  const isExpected = expectedErrors.some(
    (ErrorClass) => error instanceof ErrorClass
  );

  if (isExpected) {
    console.error(`Erro: ${error.message}`);
  } else {
    console.error("Erro inesperado ao executar a aplicação.");

    if (process.env.DEBUG) {
      console.error(error.stack || error);
    }
  }

  process.exitCode = 1;
});
```

---

### Arquivo: `.gitignore`

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

### Arquivo: `README.md`

```markdown
# Gerenciador de usuários CLI

Aplicação de linha de comando para cadastrar, listar, atualizar e remover
usuários, com persistência em SQLite.

## Requisitos

- Node.js 20 ou superior
- npm

## Instalação

Na raiz do projeto:

```bash
npm install
```

## Inicialização do banco

O banco e o schema são inicializados automaticamente ao executar qualquer
comando. Também é possível inicializá-los explicitamente:

```bash
npm run init
```

Por padrão, o banco será criado em:

```text
data/usuarios.db
```

## Comandos

### Cadastrar usuário

```bash
node src/cli.js cadastrar \
  --nome "Maria da Silva" \
  --email "maria@example.com" \
  --nascimento "1990-05-21"
```

### Listar usuários

```bash
node src/cli.js listar
```

### Atualizar usuário

É possível atualizar um ou mais campos:

```bash
node src/cli.js atualizar 1 --nome "Maria Souza"
```

```bash
node src/cli.js atualizar 1 \
  --email "maria.souza@example.com" \
  --nascimento "1990-05-22"
```

### Remover usuário

Com confirmação interativa:

```bash
node src/cli.js remover 1
```

Sem confirmação interativa:

```bash
node src/cli.js remover 1 --sim
```

### Ajuda

```bash
node src/cli.js ajuda
```

## Instalação opcional como comando local/global

Para disponibilizar o comando `usuarios` por meio de um link npm:

```bash
npm link
```

Depois disso:

```bash
usuarios listar
```

```bash
usuarios cadastrar \
  --nome "João da Silva" \
  --email "joao@example.com" \
  --nascimento "1985-10-15"
```

## Caminho personalizado do banco

Defina a variável de ambiente `USERS_DB_PATH`:

```bash
USERS_DB_PATH=/tmp/meus-usuarios.db node src/cli.js listar
```

No Windows PowerShell:

```powershell
$env:USERS_DB_PATH="C:\dados\usuarios.db"
node src/cli.js listar
```

## Regras de validação

- O nome é obrigatório e possui limite de 150 caracteres.
- O e-mail é obrigatório, validado e armazenado em letras minúsculas.
- Não é permitido cadastrar e-mails duplicados.
- A comparação de e-mails não diferencia letras maiúsculas e minúsculas.
- A data de nascimento deve usar o formato `YYYY-MM-DD`.
- Datas inexistentes e datas futuras não são aceitas.
- O ID deve ser um número inteiro positivo.
```

## Como executar

```bash
mkdir usuarios-cli
cd usuarios-cli
```

Crie os arquivos conforme apresentados acima e execute:

```bash
npm install
npm run init
node src/cli.js ajuda
```

Exemplo completo:

```bash
node src/cli.js cadastrar \
  --nome "Ana Pereira" \
  --email "ana@example.com" \
  --nascimento "1992-08-14"

node src/cli.js listar
node src/cli.js atualizar 1 --nome "Ana Pereira da Silva"
node src/cli.js remover 1 --sim
```