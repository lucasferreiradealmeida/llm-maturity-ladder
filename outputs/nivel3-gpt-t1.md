<!--
nivel: 3 - Sistema web full-stack
provider: gpt
model: gpt-5.6
tentativa: 1
temperature: 0.2
timestamp: 2026-08-18T21:38:31.158Z
metadata: {"model":"gpt-5.6-sol","usage":{"prompt_tokens":186,"completion_tokens":8433,"total_tokens":8619,"prompt_tokens_details":{"cached_tokens":0,"cache_write_tokens":0,"audio_tokens":0},"completion_tokens_details":{"reasoning_tokens":512,"audio_tokens":0,"accepted_prediction_tokens":0,"rejected_prediction_tokens":0}},"finish_reason":"stop"}
-->

## Prompt enviado
```
Voce e um(a) engenheiro(a) de software responsavel por implementar o sistema
descrito abaixo. Gere o codigo completo, pronto para rodar, incluindo
instrucoes de execucao (como instalar dependencias e como rodar).

TAREFA:
Crie um sistema web completo (frontend + backend) para cadastro de
usuarios. O frontend deve permitir listar, cadastrar, editar e remover
usuarios atraves de uma interface no navegador, consumindo uma API REST
que persiste os dados em SQLite.

RESTRICOES:
- Linguagem: Node.js (JavaScript).
- Nao use frameworks alem dos estritamente necessarios para a tarefa.
- Nao peca esclarecimentos: assuma decisoes razoaveis e documente-as em comentarios.
- Entregue todos os arquivos necessarios, indicando o nome do arquivo antes de cada bloco de codigo.
```

## Resposta do modelo

Abaixo está um sistema completo de cadastro de usuários com:

- Backend em Node.js e Express.
- API REST.
- Persistência em SQLite.
- Frontend em HTML, CSS e JavaScript puro.
- Listagem, cadastro, edição e exclusão.
- Validação no frontend e backend.
- Tratamento de e-mail duplicado.
- Criação automática do banco e da tabela.

## Estrutura do projeto

```text
cadastro-usuarios/
├── package.json
├── server.js
├── database.js
├── .gitignore
├── README.md
└── public/
    ├── index.html
    ├── styles.css
    └── app.js
```

---

### `package.json`

```json
{
  "name": "cadastro-usuarios",
  "version": "1.0.0",
  "description": "Sistema web completo para cadastro de usuários com Node.js, Express e SQLite",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "node --watch server.js"
  },
  "engines": {
    "node": ">=18"
  },
  "dependencies": {
    "express": "^5.1.0",
    "sqlite3": "^5.1.7"
  }
}
```

---

### `database.js`

```javascript
const path = require("node:path");
const sqlite3 = require("sqlite3").verbose();

const databasePath = path.join(__dirname, "usuarios.sqlite");

const db = new sqlite3.Database(databasePath, (error) => {
  if (error) {
    console.error("Não foi possível abrir o banco de dados:", error);
  }
});

/**
 * Pequenas funções auxiliares convertem a API baseada em callbacks do sqlite3
 * para Promises, permitindo o uso de async/await no restante da aplicação.
 */
function run(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.run(sql, params, function onRun(error) {
      if (error) {
        reject(error);
        return;
      }

      resolve({
        lastID: this.lastID,
        changes: this.changes
      });
    });
  });
}

function get(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.get(sql, params, (error, row) => {
      if (error) {
        reject(error);
        return;
      }

      resolve(row);
    });
  });
}

function all(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.all(sql, params, (error, rows) => {
      if (error) {
        reject(error);
        return;
      }

      resolve(rows);
    });
  });
}

function close() {
  return new Promise((resolve, reject) => {
    db.close((error) => {
      if (error) {
        reject(error);
        return;
      }

      resolve();
    });
  });
}

async function initializeDatabase() {
  await run("PRAGMA foreign_keys = ON");
  await run("PRAGMA journal_mode = WAL");

  /*
   * Decisões assumidas:
   * - Um usuário possui nome e e-mail.
   * - O e-mail identifica o usuário e, por isso, deve ser único.
   * - COLLATE NOCASE faz a comparação de e-mails ignorar maiúsculas/minúsculas.
   * - As datas são armazenadas pelo SQLite em UTC.
   */
  await run(`
    CREATE TABLE IF NOT EXISTS usuarios (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      nome TEXT NOT NULL,
      email TEXT NOT NULL COLLATE NOCASE UNIQUE,
      criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      atualizado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
  `);
}

module.exports = {
  initializeDatabase,
  run,
  get,
  all,
  close
};
```

---

### `server.js`

```javascript
const path = require("node:path");
const express = require("express");
const database = require("./database");

const app = express();
const PORT = Number(process.env.PORT) || 3000;
const publicDirectory = path.join(__dirname, "public");

let httpServer;

app.disable("x-powered-by");

app.use((request, response, next) => {
  // Cabeçalhos de segurança básicos, sem adicionar outro framework.
  response.setHeader("X-Content-Type-Options", "nosniff");
  response.setHeader("X-Frame-Options", "DENY");
  response.setHeader("Referrer-Policy", "no-referrer");
  response.setHeader(
    "Content-Security-Policy",
    "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
  );

  next();
});

app.use(express.json({ limit: "20kb" }));
app.use(express.static(publicDirectory));

function validateUser(body) {
  const errors = [];

  if (!body || typeof body !== "object" || Array.isArray(body)) {
    return {
      errors: ["O corpo da requisição deve ser um objeto JSON."]
    };
  }

  const nome = typeof body.nome === "string" ? body.nome.trim() : "";
  const email =
    typeof body.email === "string" ? body.email.trim().toLowerCase() : "";

  if (!nome) {
    errors.push("O nome é obrigatório.");
  } else if (nome.length < 2) {
    errors.push("O nome deve possuir pelo menos 2 caracteres.");
  } else if (nome.length > 120) {
    errors.push("O nome deve possuir no máximo 120 caracteres.");
  }

  if (!email) {
    errors.push("O e-mail é obrigatório.");
  } else if (email.length > 254) {
    errors.push("O e-mail deve possuir no máximo 254 caracteres.");
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    errors.push("Informe um endereço de e-mail válido.");
  }

  return {
    errors,
    data: { nome, email }
  };
}

function parseId(rawId) {
  if (!/^\d+$/.test(rawId)) {
    return null;
  }

  const id = Number(rawId);

  if (!Number.isSafeInteger(id) || id <= 0) {
    return null;
  }

  return id;
}

function isUniqueConstraintError(error) {
  return (
    error &&
    (error.code === "SQLITE_CONSTRAINT" ||
      error.code === "SQLITE_CONSTRAINT_UNIQUE") &&
    String(error.message).includes("usuarios.email")
  );
}

function serializeUser(row) {
  return {
    id: row.id,
    nome: row.nome,
    email: row.email,
    criadoEm: row.criado_em,
    atualizadoEm: row.atualizado_em
  };
}

/**
 * GET /api/usuarios
 * Retorna todos os usuários, ordenados pelo nome.
 */
app.get("/api/usuarios", async (request, response, next) => {
  try {
    const rows = await database.all(`
      SELECT id, nome, email, criado_em, atualizado_em
      FROM usuarios
      ORDER BY nome COLLATE NOCASE ASC, id ASC
    `);

    response.json(rows.map(serializeUser));
  } catch (error) {
    next(error);
  }
});

/**
 * GET /api/usuarios/:id
 * Retorna um usuário específico.
 */
app.get("/api/usuarios/:id", async (request, response, next) => {
  const id = parseId(request.params.id);

  if (id === null) {
    return response.status(400).json({
      mensagem: "O identificador do usuário é inválido."
    });
  }

  try {
    const row = await database.get(
      `
        SELECT id, nome, email, criado_em, atualizado_em
        FROM usuarios
        WHERE id = ?
      `,
      [id]
    );

    if (!row) {
      return response.status(404).json({
        mensagem: "Usuário não encontrado."
      });
    }

    return response.json(serializeUser(row));
  } catch (error) {
    return next(error);
  }
});

/**
 * POST /api/usuarios
 * Cria um usuário.
 */
app.post("/api/usuarios", async (request, response, next) => {
  const validation = validateUser(request.body);

  if (validation.errors.length > 0) {
    return response.status(400).json({
      mensagem: "Os dados informados são inválidos.",
      erros: validation.errors
    });
  }

  const { nome, email } = validation.data;

  try {
    const result = await database.run(
      `
        INSERT INTO usuarios (nome, email)
        VALUES (?, ?)
      `,
      [nome, email]
    );

    const createdUser = await database.get(
      `
        SELECT id, nome, email, criado_em, atualizado_em
        FROM usuarios
        WHERE id = ?
      `,
      [result.lastID]
    );

    return response.status(201).json(serializeUser(createdUser));
  } catch (error) {
    if (isUniqueConstraintError(error)) {
      return response.status(409).json({
        mensagem: "Já existe um usuário cadastrado com este e-mail."
      });
    }

    return next(error);
  }
});

/**
 * PUT /api/usuarios/:id
 * Atualiza todos os dados editáveis de um usuário.
 */
app.put("/api/usuarios/:id", async (request, response, next) => {
  const id = parseId(request.params.id);

  if (id === null) {
    return response.status(400).json({
      mensagem: "O identificador do usuário é inválido."
    });
  }

  const validation = validateUser(request.body);

  if (validation.errors.length > 0) {
    return response.status(400).json({
      mensagem: "Os dados informados são inválidos.",
      erros: validation.errors
    });
  }

  const { nome, email } = validation.data;

  try {
    const result = await database.run(
      `
        UPDATE usuarios
        SET
          nome = ?,
          email = ?,
          atualizado_em = CURRENT_TIMESTAMP
        WHERE id = ?
      `,
      [nome, email, id]
    );

    if (result.changes === 0) {
      return response.status(404).json({
        mensagem: "Usuário não encontrado."
      });
    }

    const updatedUser = await database.get(
      `
        SELECT id, nome, email, criado_em, atualizado_em
        FROM usuarios
        WHERE id = ?
      `,
      [id]
    );

    return response.json(serializeUser(updatedUser));
  } catch (error) {
    if (isUniqueConstraintError(error)) {
      return response.status(409).json({
        mensagem: "Já existe um usuário cadastrado com este e-mail."
      });
    }

    return next(error);
  }
});

/**
 * DELETE /api/usuarios/:id
 * Exclui um usuário.
 */
app.delete("/api/usuarios/:id", async (request, response, next) => {
  const id = parseId(request.params.id);

  if (id === null) {
    return response.status(400).json({
      mensagem: "O identificador do usuário é inválido."
    });
  }

  try {
    const result = await database.run(
      "DELETE FROM usuarios WHERE id = ?",
      [id]
    );

    if (result.changes === 0) {
      return response.status(404).json({
        mensagem: "Usuário não encontrado."
      });
    }

    return response.status(204).send();
  } catch (error) {
    return next(error);
  }
});

app.use("/api", (request, response) => {
  response.status(404).json({
    mensagem: "Rota da API não encontrada."
  });
});

app.use((error, request, response, next) => {
  if (response.headersSent) {
    return next(error);
  }

  if (
    error instanceof SyntaxError &&
    error.status === 400 &&
    Object.prototype.hasOwnProperty.call(error, "body")
  ) {
    return response.status(400).json({
      mensagem: "O corpo da requisição contém um JSON inválido."
    });
  }

  console.error("Erro interno:", error);

  return response.status(500).json({
    mensagem: "Ocorreu um erro interno no servidor."
  });
});

async function startServer() {
  try {
    await database.initializeDatabase();

    httpServer = app.listen(PORT, () => {
      console.log(`Servidor disponível em http://localhost:${PORT}`);
    });
  } catch (error) {
    console.error("Não foi possível iniciar a aplicação:", error);
    process.exit(1);
  }
}

async function shutdown(signal) {
  console.log(`\nSinal ${signal} recebido. Encerrando a aplicação...`);

  if (httpServer) {
    await new Promise((resolve) => httpServer.close(resolve));
  }

  try {
    await database.close();
  } catch (error) {
    console.error("Erro ao fechar o banco de dados:", error);
  }

  process.exit(0);
}

process.on("SIGINT", () => {
  shutdown("SIGINT");
});

process.on("SIGTERM", () => {
  shutdown("SIGTERM");
});

startServer();
```

---

### `public/index.html`

```html
<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta
      name="description"
      content="Sistema de cadastro e gerenciamento de usuários"
    />
    <title>Cadastro de usuários</title>
    <link rel="stylesheet" href="/styles.css" />
    <script src="/app.js" defer></script>
  </head>

  <body>
    <header class="page-header">
      <div class="container">
        <p class="eyebrow">Administração</p>
        <h1>Cadastro de usuários</h1>
        <p class="subtitle">
          Cadastre, edite e remova usuários do sistema.
        </p>
      </div>
    </header>

    <main class="container page-content">
      <section class="card form-card" aria-labelledby="form-title">
        <div class="section-header">
          <div>
            <h2 id="form-title">Novo usuário</h2>
            <p id="form-description">Preencha os dados abaixo para cadastrar.</p>
          </div>
        </div>

        <form id="user-form">
          <input type="hidden" id="user-id" />

          <div class="form-grid">
            <div class="field">
              <label for="name">Nome</label>
              <input
                id="name"
                name="nome"
                type="text"
                minlength="2"
                maxlength="120"
                autocomplete="name"
                placeholder="Ex.: Maria da Silva"
                required
              />
            </div>

            <div class="field">
              <label for="email">E-mail</label>
              <input
                id="email"
                name="email"
                type="email"
                maxlength="254"
                autocomplete="email"
                placeholder="Ex.: maria@exemplo.com"
                required
              />
            </div>
          </div>

          <div class="form-actions">
            <button id="submit-button" class="button primary" type="submit">
              Cadastrar usuário
            </button>

            <button
              id="cancel-button"
              class="button secondary"
              type="button"
              hidden
            >
              Cancelar edição
            </button>
          </div>
        </form>
      </section>

      <div
        id="message"
        class="message"
        role="status"
        aria-live="polite"
        hidden
      ></div>

      <section class="card" aria-labelledby="list-title">
        <div class="section-header list-header">
          <div>
            <h2 id="list-title">Usuários cadastrados</h2>
            <p id="user-count">Carregando usuários...</p>
          </div>

          <button id="refresh-button" class="button secondary" type="button">
            Atualizar lista
          </button>
        </div>

        <div id="loading-state" class="state">
          Carregando usuários...
        </div>

        <div id="empty-state" class="state" hidden>
          <strong>Nenhum usuário cadastrado.</strong>
          <span>Use o formulário acima para adicionar o primeiro usuário.</span>
        </div>

        <div id="table-container" class="table-container" hidden>
          <table>
            <thead>
              <tr>
                <th scope="col">Nome</th>
                <th scope="col">E-mail</th>
                <th scope="col">Cadastro</th>
                <th scope="col" class="actions-column">Ações</th>
              </tr>
            </thead>
            <tbody id="users-table-body"></tbody>
          </table>
        </div>
      </section>
    </main>

    <footer class="footer">
      <div class="container">
        Sistema de cadastro de usuários
      </div>
    </footer>
  </body>
</html>
```

---

### `public/styles.css`

```css
:root {
  color-scheme: light;
  font-family:
    Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
    sans-serif;
  font-synthesis: none;

  --background: #f3f5f9;
  --surface: #ffffff;
  --surface-subtle: #f8fafc;
  --text: #182033;
  --muted: #64748b;
  --border: #dce2ea;
  --primary: #2563eb;
  --primary-hover: #1d4ed8;
  --danger: #dc2626;
  --danger-hover: #b91c1c;
  --success-bg: #ecfdf3;
  --success-text: #166534;
  --success-border: #bbf7d0;
  --error-bg: #fef2f2;
  --error-text: #991b1b;
  --error-border: #fecaca;
  --shadow: 0 12px 35px rgb(15 23 42 / 8%);
  --radius: 14px;
}

* {
  box-sizing: border-box;
}

body {
  min-width: 320px;
  min-height: 100vh;
  margin: 0;
  color: var(--text);
  background: var(--background);
}

button,
input {
  font: inherit;
}

button {
  cursor: pointer;
}

button:disabled,
input:disabled {
  cursor: not-allowed;
  opacity: 0.65;
}

.container {
  width: min(1120px, calc(100% - 32px));
  margin: 0 auto;
}

.page-header {
  padding: 52px 0 86px;
  color: white;
  background:
    radial-gradient(circle at 80% 20%, rgb(255 255 255 / 15%), transparent 25%),
    linear-gradient(135deg, #1d4ed8, #4338ca);
}

.page-header h1 {
  margin: 4px 0 8px;
  font-size: clamp(2rem, 5vw, 3rem);
  letter-spacing: -0.04em;
}

.eyebrow {
  margin: 0;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  opacity: 0.85;
}

.subtitle {
  max-width: 620px;
  margin: 0;
  color: rgb(255 255 255 / 82%);
  font-size: 1.05rem;
}

.page-content {
  display: grid;
  gap: 22px;
  margin-top: -48px;
  padding-bottom: 48px;
}

.card {
  overflow: hidden;
  padding: 28px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface);
  box-shadow: var(--shadow);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 24px;
}

.section-header h2 {
  margin: 0 0 5px;
  font-size: 1.3rem;
  letter-spacing: -0.02em;
}

.section-header p {
  margin: 0;
  color: var(--muted);
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}

.field {
  display: grid;
  gap: 8px;
}

.field label {
  font-size: 0.9rem;
  font-weight: 700;
}

.field input {
  width: 100%;
  min-height: 46px;
  padding: 10px 13px;
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 9px;
  outline: none;
  background: var(--surface);
  transition:
    border-color 150ms,
    box-shadow 150ms;
}

.field input::placeholder {
  color: #94a3b8;
}

.field input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgb(37 99 235 / 14%);
}

.form-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 22px;
}

.button {
  min-height: 42px;
  padding: 9px 16px;
  border: 1px solid transparent;
  border-radius: 9px;
  font-weight: 700;
  transition:
    background-color 150ms,
    border-color 150ms,
    transform 80ms;
}

.button:active:not(:disabled) {
  transform: translateY(1px);
}

.button.primary {
  color: white;
  background: var(--primary);
}

.button.primary:hover:not(:disabled) {
  background: var(--primary-hover);
}

.button.secondary {
  color: #334155;
  border-color: var(--border);
  background: var(--surface);
}

.button.secondary:hover:not(:disabled) {
  border-color: #aeb8c6;
  background: var(--surface-subtle);
}

.button.danger {
  color: var(--danger);
  border-color: #fecaca;
  background: white;
}

.button.danger:hover:not(:disabled) {
  color: white;
  border-color: var(--danger-hover);
  background: var(--danger-hover);
}

.button.small {
  min-height: 34px;
  padding: 6px 10px;
  font-size: 0.84rem;
}

.message {
  padding: 14px 16px;
  border: 1px solid;
  border-radius: 10px;
  font-weight: 600;
}

.message.success {
  color: var(--success-text);
  border-color: var(--success-border);
  background: var(--success-bg);
}

.message.error {
  color: var(--error-text);
  border-color: var(--error-border);
  background: var(--error-bg);
}

.state {
  display: grid;
  justify-items: center;
  gap: 7px;
  padding: 48px 16px;
  color: var(--muted);
  text-align: center;
  border: 1px dashed var(--border);
  border-radius: 10px;
  background: var(--surface-subtle);
}

.table-container {
  overflow-x: auto;
  margin: 0 -28px -28px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 15px 18px;
  text-align: left;
  border-top: 1px solid var(--border);
}

th {
  color: #475569;
  background: var(--surface-subtle);
  font-size: 0.78rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

td {
  vertical-align: middle;
}

.user-name {
  font-weight: 700;
}

.user-email,
.user-date {
  color: var(--muted);
}

.actions-column {
  width: 1%;
  white-space: nowrap;
}

.row-actions {
  display: flex;
  gap: 8px;
}

.footer {
  padding: 22px 0;
  color: var(--muted);
  text-align: center;
  border-top: 1px solid var(--border);
  background: var(--surface);
  font-size: 0.88rem;
}

[hidden] {
  display: none !important;
}

@media (max-width: 720px) {
  .page-header {
    padding-top: 38px;
  }

  .card {
    padding: 20px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .section-header.list-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .table-container {
    margin: 0 -20px -20px;
  }

  th,
  td {
    padding: 13px;
  }

  .row-actions {
    align-items: stretch;
    flex-direction: column;
  }
}
```

---

### `public/app.js`

```javascript
const API_URL = "/api/usuarios";

const form = document.querySelector("#user-form");
const userIdInput = document.querySelector("#user-id");
const nameInput = document.querySelector("#name");
const emailInput = document.querySelector("#email");
const submitButton = document.querySelector("#submit-button");
const cancelButton = document.querySelector("#cancel-button");
const refreshButton = document.querySelector("#refresh-button");
const formTitle = document.querySelector("#form-title");
const formDescription = document.querySelector("#form-description");
const message = document.querySelector("#message");
const loadingState = document.querySelector("#loading-state");
const emptyState = document.querySelector("#empty-state");
const tableContainer = document.querySelector("#table-container");
const tableBody = document.querySelector("#users-table-body");
const userCount = document.querySelector("#user-count");

let users = [];
let messageTimer = null;

function setFormLoading(isLoading) {
  submitButton.disabled = isLoading;
  cancelButton.disabled = isLoading;
  nameInput.disabled = isLoading;
  emailInput.disabled = isLoading;

  if (isLoading) {
    submitButton.textContent = userIdInput.value
      ? "Salvando..."
      : "Cadastrando...";
  } else {
    submitButton.textContent = userIdInput.value
      ? "Salvar alterações"
      : "Cadastrar usuário";
  }
}

function showMessage(text, type = "success") {
  window.clearTimeout(messageTimer);

  message.textContent = text;
  message.className = `message ${type}`;
  message.hidden = false;

  messageTimer = window.setTimeout(() => {
    message.hidden = true;
  }, 5000);
}

function hideMessage() {
  window.clearTimeout(messageTimer);
  message.hidden = true;
  message.textContent = "";
}

function formatDate(sqliteDate) {
  if (!sqliteDate) {
    return "—";
  }

  /*
   * CURRENT_TIMESTAMP do SQLite produz "AAAA-MM-DD HH:MM:SS" em UTC.
   * A substituição deixa o formato compatível com o construtor Date.
   */
  const parsedDate = new Date(`${sqliteDate.replace(" ", "T")}Z`);

  if (Number.isNaN(parsedDate.getTime())) {
    return sqliteDate;
  }

  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short"
  }).format(parsedDate);
}

async function request(url, options = {}) {
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers
    },
    ...options
  });

  if (response.status === 204) {
    return null;
  }

  const contentType = response.headers.get("content-type") || "";
  const body = contentType.includes("application/json")
    ? await response.json()
    : null;

  if (!response.ok) {
    const details =
      Array.isArray(body?.erros) && body.erros.length > 0
        ? ` ${body.erros.join(" ")}`
        : "";

    throw new Error(
      `${body?.mensagem || "Não foi possível concluir a operação."}${details}`
    );
  }

  return body;
}

function createTextCell(text, className) {
  const cell = document.createElement("td");
  const element = document.createElement("span");

  element.textContent = text;
  element.className = className;

  cell.appendChild(element);
  return cell;
}

function createActionButton(text, className, action, id) {
  const button = document.createElement("button");

  button.type = "button";
  button.textContent = text;
  button.className = `button small ${className}`;
  button.dataset.action = action;
  button.dataset.id = String(id);

  return button;
}

function renderUsers() {
  tableBody.replaceChildren();

  const count = users.length;
  userCount.textContent =
    count === 1 ? "1 usuário cadastrado" : `${count} usuários cadastrados`;

  emptyState.hidden = count !== 0;
  tableContainer.hidden = count === 0;

  for (const user of users) {
    const row = document.createElement("tr");

    row.appendChild(createTextCell(user.nome, "user-name"));
    row.appendChild(createTextCell(user.email, "user-email"));
    row.appendChild(createTextCell(formatDate(user.criadoEm), "user-date"));

    const actionsCell = document.createElement("td");
    const actions = document.createElement("div");

    actions.className = "row-actions";
    actions.appendChild(
      createActionButton("Editar", "secondary", "edit", user.id)
    );
    actions.appendChild(
      createActionButton("Excluir", "danger", "delete", user.id)
    );

    actionsCell.appendChild(actions);
    row.appendChild(actionsCell);
    tableBody.appendChild(row);
  }
}

async function loadUsers() {
  refreshButton.disabled = true;
  loadingState.hidden = false;
  emptyState.hidden = true;
  tableContainer.hidden = true;
  userCount.textContent = "Carregando usuários...";

  try {
    users = await request(API_URL);
    renderUsers();
  } catch (error) {
    users = [];
    userCount.textContent = "Não foi possível carregar os usuários";
    showMessage(error.message, "error");
  } finally {
    loadingState.hidden = true;
    refreshButton.disabled = false;
  }
}

function resetForm() {
  form.reset();
  userIdInput.value = "";
  formTitle.textContent = "Novo usuário";
  formDescription.textContent = "Preencha os dados abaixo para cadastrar.";
  submitButton.textContent = "Cadastrar usuário";
  cancelButton.hidden = true;
}

function startEditing(user) {
  userIdInput.value = String(user.id);
  nameInput.value = user.nome;
  emailInput.value = user.email;

  formTitle.textContent = "Editar usuário";
  formDescription.textContent = `Alterando os dados de ${user.nome}.`;
  submitButton.textContent = "Salvar alterações";
  cancelButton.hidden = false;

  hideMessage();
  nameInput.focus();
  form.scrollIntoView({ behavior: "smooth", block: "center" });
}

async function deleteUser(user) {
  const confirmed = window.confirm(
    `Deseja realmente excluir o usuário "${user.nome}"?`
  );

  if (!confirmed) {
    return;
  }

  try {
    await request(`${API_URL}/${user.id}`, {
      method: "DELETE"
    });

    if (userIdInput.value === String(user.id)) {
      resetForm();
    }

    showMessage("Usuário excluído com sucesso.");
    await loadUsers();
  } catch (error) {
    showMessage(error.message, "error");
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  hideMessage();

  if (!form.reportValidity()) {
    return;
  }

  const id = userIdInput.value;
  const isEditing = Boolean(id);
  const data = {
    nome: nameInput.value.trim(),
    email: emailInput.value.trim()
  };

  setFormLoading(true);

  try {
    await request(isEditing ? `${API_URL}/${id}` : API_URL, {
      method: isEditing ? "PUT" : "POST",
      body: JSON.stringify(data)
    });

    resetForm();
    showMessage(
      isEditing
        ? "Usuário atualizado com sucesso."
        : "Usuário cadastrado com sucesso."
    );

    await loadUsers();
    nameInput.focus();
  } catch (error) {
    showMessage(error.message, "error");
  } finally {
    setFormLoading(false);
  }
});

cancelButton.addEventListener("click", () => {
  resetForm();
  hideMessage();
  nameInput.focus();
});

refreshButton.addEventListener("click", () => {
  loadUsers();
});

tableBody.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-action]");

  if (!button) {
    return;
  }

  const id = Number(button.dataset.id);
  const user = users.find((item) => item.id === id);

  if (!user) {
    showMessage("O usuário selecionado não foi encontrado.", "error");
    return;
  }

  if (button.dataset.action === "edit") {
    startEditing(user);
  }

  if (button.dataset.action === "delete") {
    deleteUser(user);
  }
});

loadUsers();
```

---

### `.gitignore`

```gitignore
node_modules/
usuarios.sqlite
usuarios.sqlite-shm
usuarios.sqlite-wal
npm-debug.log*
.DS_Store
.env
```

---

### `README.md`

```markdown
# Cadastro de usuários

Sistema web completo para listar, cadastrar, editar e excluir usuários.

## Tecnologias

- Node.js
- Express
- SQLite
- HTML, CSS e JavaScript puro

## Requisitos

- Node.js 18 ou superior
- npm

Para verificar as versões instaladas:

```bash
node --version
npm --version
```

## Instalação

Entre na pasta do projeto e instale as dependências:

```bash
npm install
```

## Execução

Inicie o servidor:

```bash
npm start
```

Depois, acesse no navegador:

```text
http://localhost:3000
```

O arquivo `usuarios.sqlite` será criado automaticamente na raiz do projeto.

## Modo de desenvolvimento

O Node.js reiniciará o servidor quando os arquivos forem alterados:

```bash
npm run dev
```

## Alteração da porta

Linux/macOS:

```bash
PORT=8080 npm start
```

PowerShell:

```powershell
$env:PORT=8080
npm start
```

## Endpoints da API

### Listar usuários

```http
GET /api/usuarios
```

### Consultar um usuário

```http
GET /api/usuarios/:id
```

### Cadastrar usuário

```http
POST /api/usuarios
Content-Type: application/json
```

Exemplo:

```json
{
  "nome": "Maria da Silva",
  "email": "maria@exemplo.com"
}
```

### Atualizar usuário

```http
PUT /api/usuarios/:id
Content-Type: application/json
```

Exemplo:

```json
{
  "nome": "Maria Souza",
  "email": "maria.souza@exemplo.com"
}
```

### Excluir usuário

```http
DELETE /api/usuarios/:id
```

## Decisões adotadas

- Cada usuário possui nome e e-mail.
- O e-mail é obrigatório e único.
- E-mails são normalizados para letras minúsculas.
- A API usa consultas parametrizadas para evitar injeção de SQL.
- O frontend é servido pelo próprio backend.
- O banco e a tabela são criados automaticamente.
- Não há autenticação, pois ela não faz parte do escopo solicitado.
```

## Como executar rapidamente

```bash
mkdir cadastro-usuarios
cd cadastro-usuarios
```

Crie os arquivos conforme a estrutura apresentada e execute:

```bash
npm install
npm start
```

Acesse:

```text
http://localhost:3000
```