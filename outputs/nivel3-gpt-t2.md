<!--
nivel: 3 - Sistema web full-stack
provider: gpt
model: gpt-5.6
tentativa: 2
temperature: 0.2
timestamp: 2026-08-18T21:39:54.761Z
metadata: {"model":"gpt-5.6-sol","usage":{"prompt_tokens":186,"completion_tokens":8442,"total_tokens":8628,"prompt_tokens_details":{"cached_tokens":0,"cache_write_tokens":0,"audio_tokens":0},"completion_tokens_details":{"reasoning_tokens":512,"audio_tokens":0,"accepted_prediction_tokens":0,"rejected_prediction_tokens":0}},"finish_reason":"stop"}
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

Abaixo está uma implementação completa usando:

- **Node.js**
- **Express** para servidor HTTP e API REST
- **better-sqlite3** para persistência SQLite
- **HTML, CSS e JavaScript puros** no frontend

A aplicação permite listar, cadastrar, editar e remover usuários. Foram assumidos os campos **nome** e **e-mail**, com e-mail único.

## Estrutura do projeto

```text
cadastro-usuarios/
├── package.json
├── server.js
├── .gitignore
└── public/
    ├── index.html
    ├── styles.css
    └── app.js
```

O diretório `data/` e o banco SQLite serão criados automaticamente na primeira execução.

---

### Arquivo: `package.json`

```json
{
  "name": "cadastro-usuarios",
  "version": "1.0.0",
  "description": "Sistema web completo para cadastro de usuários com Node.js, Express e SQLite.",
  "main": "server.js",
  "type": "commonjs",
  "scripts": {
    "start": "node server.js",
    "dev": "node --watch server.js"
  },
  "engines": {
    "node": ">=20"
  },
  "dependencies": {
    "better-sqlite3": "^12.2.0",
    "express": "^5.1.0"
  }
}
```

---

### Arquivo: `.gitignore`

```gitignore
node_modules/
data/
.env
npm-debug.log*
.DS_Store
```

---

### Arquivo: `server.js`

```javascript
'use strict';

const express = require('express');
const Database = require('better-sqlite3');
const path = require('node:path');
const fs = require('node:fs');

const app = express();

const PORT = Number.parseInt(process.env.PORT, 10) || 3000;
const HOST = process.env.HOST || '0.0.0.0';

const publicDirectory = path.join(__dirname, 'public');
const dataDirectory = path.join(__dirname, 'data');
const databasePath = path.join(dataDirectory, 'usuarios.db');

fs.mkdirSync(dataDirectory, { recursive: true });

const database = new Database(databasePath);

// WAL melhora a concorrência entre leituras e escritas.
database.pragma('journal_mode = WAL');
database.pragma('foreign_keys = ON');

database.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL CHECK(length(name) BETWEEN 2 AND 100),
    email TEXT NOT NULL COLLATE NOCASE UNIQUE,
    created_at TEXT NOT NULL DEFAULT (
      strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
    ),
    updated_at TEXT NOT NULL DEFAULT (
      strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
    )
  );
`);

const statements = {
  listUsers: database.prepare(`
    SELECT
      id,
      name,
      email,
      created_at AS createdAt,
      updated_at AS updatedAt
    FROM users
    ORDER BY name COLLATE NOCASE ASC, id ASC
  `),

  getUser: database.prepare(`
    SELECT
      id,
      name,
      email,
      created_at AS createdAt,
      updated_at AS updatedAt
    FROM users
    WHERE id = ?
  `),

  createUser: database.prepare(`
    INSERT INTO users (name, email)
    VALUES (?, ?)
  `),

  updateUser: database.prepare(`
    UPDATE users
    SET
      name = ?,
      email = ?,
      updated_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
    WHERE id = ?
  `),

  deleteUser: database.prepare(`
    DELETE FROM users
    WHERE id = ?
  `)
};

app.disable('x-powered-by');

app.use(express.json({ limit: '100kb' }));

function parseUserId(rawId) {
  const id = Number(rawId);

  if (!Number.isSafeInteger(id) || id <= 0) {
    return null;
  }

  return id;
}

function normalizeUserInput(body) {
  const source = body && typeof body === 'object' ? body : {};

  return {
    name: typeof source.name === 'string' ? source.name.trim() : '',
    email:
      typeof source.email === 'string'
        ? source.email.trim().toLowerCase()
        : ''
  };
}

function validateUser(user) {
  const errors = {};

  if (!user.name) {
    errors.name = 'O nome é obrigatório.';
  } else if (user.name.length < 2) {
    errors.name = 'O nome deve possuir pelo menos 2 caracteres.';
  } else if (user.name.length > 100) {
    errors.name = 'O nome deve possuir no máximo 100 caracteres.';
  }

  if (!user.email) {
    errors.email = 'O e-mail é obrigatório.';
  } else if (user.email.length > 254) {
    errors.email = 'O e-mail deve possuir no máximo 254 caracteres.';
  } else {
    // Validação intencionalmente simples e adequada para formulário web.
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailPattern.test(user.email)) {
      errors.email = 'Informe um endereço de e-mail válido.';
    }
  }

  return errors;
}

function isUniqueConstraintError(error) {
  return (
    error &&
    typeof error.code === 'string' &&
    error.code.startsWith('SQLITE_CONSTRAINT_UNIQUE')
  );
}

function sendNotFound(response) {
  return response.status(404).json({
    error: 'Usuário não encontrado.'
  });
}

app.get('/api/health', (request, response) => {
  response.json({
    status: 'ok'
  });
});

app.get('/api/users', (request, response) => {
  const users = statements.listUsers.all();
  response.json(users);
});

app.get('/api/users/:id', (request, response) => {
  const id = parseUserId(request.params.id);

  if (id === null) {
    return response.status(400).json({
      error: 'Identificador de usuário inválido.'
    });
  }

  const user = statements.getUser.get(id);

  if (!user) {
    return sendNotFound(response);
  }

  return response.json(user);
});

app.post('/api/users', (request, response, next) => {
  const userInput = normalizeUserInput(request.body);
  const validationErrors = validateUser(userInput);

  if (Object.keys(validationErrors).length > 0) {
    return response.status(400).json({
      error: 'Dados inválidos.',
      fields: validationErrors
    });
  }

  try {
    const result = statements.createUser.run(
      userInput.name,
      userInput.email
    );

    const createdUser = statements.getUser.get(result.lastInsertRowid);

    return response.status(201).json(createdUser);
  } catch (error) {
    if (isUniqueConstraintError(error)) {
      return response.status(409).json({
        error: 'Já existe um usuário cadastrado com este e-mail.',
        fields: {
          email: 'Este e-mail já está cadastrado.'
        }
      });
    }

    return next(error);
  }
});

app.put('/api/users/:id', (request, response, next) => {
  const id = parseUserId(request.params.id);

  if (id === null) {
    return response.status(400).json({
      error: 'Identificador de usuário inválido.'
    });
  }

  if (!statements.getUser.get(id)) {
    return sendNotFound(response);
  }

  const userInput = normalizeUserInput(request.body);
  const validationErrors = validateUser(userInput);

  if (Object.keys(validationErrors).length > 0) {
    return response.status(400).json({
      error: 'Dados inválidos.',
      fields: validationErrors
    });
  }

  try {
    statements.updateUser.run(userInput.name, userInput.email, id);

    const updatedUser = statements.getUser.get(id);
    return response.json(updatedUser);
  } catch (error) {
    if (isUniqueConstraintError(error)) {
      return response.status(409).json({
        error: 'Já existe um usuário cadastrado com este e-mail.',
        fields: {
          email: 'Este e-mail já está cadastrado.'
        }
      });
    }

    return next(error);
  }
});

app.delete('/api/users/:id', (request, response) => {
  const id = parseUserId(request.params.id);

  if (id === null) {
    return response.status(400).json({
      error: 'Identificador de usuário inválido.'
    });
  }

  const result = statements.deleteUser.run(id);

  if (result.changes === 0) {
    return sendNotFound(response);
  }

  return response.status(204).send();
});

// O frontend é servido pelo mesmo servidor para evitar configuração de CORS.
app.use(express.static(publicDirectory));

app.use('/api', (request, response) => {
  response.status(404).json({
    error: 'Endpoint não encontrado.'
  });
});

// Retorna a página principal para rotas não pertencentes à API.
app.get(/.*/, (request, response) => {
  response.sendFile(path.join(publicDirectory, 'index.html'));
});

// Tratamento específico para JSON inválido enviado pelo cliente.
app.use((error, request, response, next) => {
  if (error instanceof SyntaxError && error.status === 400 && 'body' in error) {
    return response.status(400).json({
      error: 'O corpo da requisição contém JSON inválido.'
    });
  }

  return next(error);
});

// Tratamento centralizado de erros inesperados.
app.use((error, request, response, next) => {
  console.error(error);

  if (response.headersSent) {
    return next(error);
  }

  return response.status(500).json({
    error: 'Ocorreu um erro interno no servidor.'
  });
});

const server = app.listen(PORT, HOST, () => {
  console.log(`Servidor disponível em http://localhost:${PORT}`);
  console.log(`Banco de dados: ${databasePath}`);
});

function shutdown(signal) {
  console.log(`\nSinal ${signal} recebido. Encerrando servidor...`);

  server.close(() => {
    database.close();
    console.log('Servidor e banco de dados encerrados.');
    process.exit(0);
  });

  setTimeout(() => {
    console.error('Encerramento forçado após tempo limite.');
    process.exit(1);
  }, 10_000).unref();
}

process.on('SIGINT', () => shutdown('SIGINT'));
process.on('SIGTERM', () => shutdown('SIGTERM'));
```

---

### Arquivo: `public/index.html`

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta
    name="viewport"
    content="width=device-width, initial-scale=1"
  >
  <meta
    name="description"
    content="Sistema para cadastro e gerenciamento de usuários."
  >
  <title>Cadastro de Usuários</title>
  <link rel="stylesheet" href="/styles.css">
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

  <main class="container main-content">
    <section class="card form-card" aria-labelledby="form-title">
      <div class="section-heading">
        <div>
          <h2 id="form-title">Novo usuário</h2>
          <p id="form-description">
            Preencha os dados abaixo para realizar o cadastro.
          </p>
        </div>
      </div>

      <form id="user-form" novalidate>
        <input id="user-id" type="hidden">

        <div class="form-grid">
          <div class="field">
            <label for="name">Nome</label>
            <input
              id="name"
              name="name"
              type="text"
              minlength="2"
              maxlength="100"
              autocomplete="name"
              placeholder="Ex.: Maria da Silva"
              required
            >
            <small id="name-error" class="field-error"></small>
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
            >
            <small id="email-error" class="field-error"></small>
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

    <section class="card users-card" aria-labelledby="users-title">
      <div class="section-heading users-heading">
        <div>
          <h2 id="users-title">Usuários cadastrados</h2>
          <p id="user-count">Carregando usuários...</p>
        </div>

        <button
          id="refresh-button"
          class="button secondary"
          type="button"
        >
          Atualizar lista
        </button>
      </div>

      <div
        id="status-message"
        class="status-message"
        role="status"
        aria-live="polite"
        hidden
      ></div>

      <div id="loading-state" class="state-box">
        Carregando usuários...
      </div>

      <div id="empty-state" class="state-box" hidden>
        <strong>Nenhum usuário cadastrado.</strong>
        <span>Utilize o formulário acima para criar o primeiro cadastro.</span>
      </div>

      <div id="table-wrapper" class="table-wrapper" hidden>
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

  <footer class="page-footer">
    <div class="container">
      Sistema de cadastro de usuários
    </div>
  </footer>

  <script src="/app.js" defer></script>
</body>
</html>
```

---

### Arquivo: `public/styles.css`

```css
:root {
  color-scheme: light;
  font-family:
    Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
    "Segoe UI", sans-serif;
  font-synthesis: none;
  --background: #f3f6fb;
  --surface: #ffffff;
  --text: #172033;
  --muted: #667085;
  --border: #d9e0eb;
  --primary: #3157d5;
  --primary-hover: #2748b3;
  --danger: #c72d3b;
  --danger-hover: #a92330;
  --success-background: #e9f9ef;
  --success-text: #176536;
  --error-background: #fdeced;
  --error-text: #992431;
  --info-background: #eaf1ff;
  --info-text: #244b9c;
  --shadow: 0 12px 35px rgba(21, 38, 73, 0.08);
}

* {
  box-sizing: border-box;
}

html {
  min-width: 320px;
}

body {
  min-height: 100vh;
  margin: 0;
  background: var(--background);
  color: var(--text);
}

button,
input {
  font: inherit;
}

button {
  cursor: pointer;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.65;
}

.container {
  width: min(1120px, calc(100% - 32px));
  margin-inline: auto;
}

.page-header {
  padding: 52px 0 76px;
  background:
    radial-gradient(circle at top right, rgba(255, 255, 255, 0.22), transparent 30%),
    linear-gradient(135deg, #2746b4, #4068e8);
  color: #ffffff;
}

.eyebrow {
  margin: 0 0 8px;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  opacity: 0.85;
}

h1 {
  margin: 0;
  font-size: clamp(2rem, 5vw, 3.2rem);
  line-height: 1.1;
}

.subtitle {
  max-width: 600px;
  margin: 14px 0 0;
  color: rgba(255, 255, 255, 0.85);
  font-size: 1.05rem;
}

.main-content {
  display: grid;
  gap: 24px;
  margin-top: -38px;
  padding-bottom: 48px;
}

.card {
  padding: 28px;
  border: 1px solid rgba(217, 224, 235, 0.85);
  border-radius: 16px;
  background: var(--surface);
  box-shadow: var(--shadow);
}

.section-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 24px;
}

.section-heading h2 {
  margin: 0;
  font-size: 1.3rem;
}

.section-heading p {
  margin: 6px 0 0;
  color: var(--muted);
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.field {
  display: flex;
  flex-direction: column;
}

.field label {
  margin-bottom: 8px;
  font-weight: 700;
}

.field input {
  width: 100%;
  min-height: 44px;
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: 9px;
  outline: none;
  background: #ffffff;
  color: var(--text);
  transition:
    border-color 150ms ease,
    box-shadow 150ms ease;
}

.field input:hover {
  border-color: #aab5c5;
}

.field input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(49, 87, 213, 0.15);
}

.field input.invalid {
  border-color: var(--danger);
}

.field input.invalid:focus {
  box-shadow: 0 0 0 3px rgba(199, 45, 59, 0.13);
}

.field-error {
  min-height: 20px;
  margin-top: 6px;
  color: var(--danger);
  font-size: 0.85rem;
}

.form-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 8px;
}

.button {
  min-height: 42px;
  padding: 9px 16px;
  border: 1px solid transparent;
  border-radius: 9px;
  font-weight: 750;
  transition:
    background-color 150ms ease,
    border-color 150ms ease,
    transform 100ms ease;
}

.button:active:not(:disabled) {
  transform: translateY(1px);
}

.button:focus-visible {
  outline: 3px solid rgba(49, 87, 213, 0.28);
  outline-offset: 2px;
}

.button.primary {
  background: var(--primary);
  color: #ffffff;
}

.button.primary:hover:not(:disabled) {
  background: var(--primary-hover);
}

.button.secondary {
  border-color: var(--border);
  background: #ffffff;
  color: #344054;
}

.button.secondary:hover:not(:disabled) {
  border-color: #aeb8c8;
  background: #f7f9fc;
}

.button.danger {
  border-color: #f1c5ca;
  background: #fff5f6;
  color: var(--danger);
}

.button.danger:hover:not(:disabled) {
  border-color: var(--danger);
  background: var(--danger);
  color: #ffffff;
}

.button.small {
  min-height: 36px;
  padding: 7px 11px;
  font-size: 0.88rem;
}

.status-message {
  margin-bottom: 18px;
  padding: 12px 14px;
  border-radius: 9px;
  font-weight: 650;
}

.status-message.success {
  background: var(--success-background);
  color: var(--success-text);
}

.status-message.error {
  background: var(--error-background);
  color: var(--error-text);
}

.status-message.info {
  background: var(--info-background);
  color: var(--info-text);
}

.state-box {
  display: flex;
  min-height: 130px;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 24px;
  border: 1px dashed var(--border);
  border-radius: 12px;
  color: var(--muted);
  text-align: center;
}

.table-wrapper {
  overflow-x: auto;
  border: 1px solid var(--border);
  border-radius: 12px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 15px 16px;
  border-bottom: 1px solid var(--border);
  text-align: left;
  vertical-align: middle;
}

th {
  background: #f7f9fc;
  color: #4b5565;
  font-size: 0.82rem;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}

tbody tr:last-child td {
  border-bottom: 0;
}

tbody tr:hover {
  background: #fbfcfe;
}

.user-name {
  font-weight: 750;
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
  justify-content: flex-end;
}

.page-footer {
  padding: 20px 0 30px;
  color: var(--muted);
  text-align: center;
  font-size: 0.9rem;
}

[hidden] {
  display: none !important;
}

@media (max-width: 760px) {
  .page-header {
    padding-top: 38px;
  }

  .card {
    padding: 20px;
  }

  .form-grid {
    grid-template-columns: 1fr;
    gap: 4px;
  }

  .users-heading {
    align-items: flex-start;
    flex-direction: column;
  }

  .users-heading .button {
    width: 100%;
  }

  th,
  td {
    padding: 12px;
  }

  .row-actions {
    flex-direction: column;
  }
}

@media (max-width: 520px) {
  .container {
    width: min(100% - 20px, 1120px);
  }

  .form-actions {
    flex-direction: column;
  }

  .form-actions .button {
    width: 100%;
  }

  .card {
    border-radius: 12px;
  }
}
```

---

### Arquivo: `public/app.js`

```javascript
'use strict';

const API_URL = '/api/users';

const elements = {
  form: document.querySelector('#user-form'),
  userId: document.querySelector('#user-id'),
  name: document.querySelector('#name'),
  email: document.querySelector('#email'),
  nameError: document.querySelector('#name-error'),
  emailError: document.querySelector('#email-error'),
  formTitle: document.querySelector('#form-title'),
  formDescription: document.querySelector('#form-description'),
  submitButton: document.querySelector('#submit-button'),
  cancelButton: document.querySelector('#cancel-button'),
  refreshButton: document.querySelector('#refresh-button'),
  userCount: document.querySelector('#user-count'),
  statusMessage: document.querySelector('#status-message'),
  loadingState: document.querySelector('#loading-state'),
  emptyState: document.querySelector('#empty-state'),
  tableWrapper: document.querySelector('#table-wrapper'),
  tableBody: document.querySelector('#users-table-body')
};

let users = [];
let isSaving = false;

async function apiRequest(url, options = {}) {
  const headers = new Headers(options.headers || {});

  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(url, {
    ...options,
    headers
  });

  let data = null;
  const contentType = response.headers.get('content-type') || '';

  if (contentType.includes('application/json')) {
    data = await response.json();
  }

  if (!response.ok) {
    const error = new Error(
      data?.error || `A requisição falhou com status ${response.status}.`
    );

    error.status = response.status;
    error.fields = data?.fields || {};
    throw error;
  }

  return data;
}

function setStatus(message, type = 'info') {
  elements.statusMessage.textContent = message;
  elements.statusMessage.className = `status-message ${type}`;
  elements.statusMessage.hidden = false;
}

function clearStatus() {
  elements.statusMessage.textContent = '';
  elements.statusMessage.className = 'status-message';
  elements.statusMessage.hidden = true;
}

function setFieldError(fieldName, message = '') {
  const input = elements[fieldName];
  const errorElement = elements[`${fieldName}Error`];

  input.classList.toggle('invalid', Boolean(message));
  input.setAttribute('aria-invalid', String(Boolean(message)));

  if (message) {
    input.setAttribute('aria-describedby', `${fieldName}-error`);
  } else {
    input.removeAttribute('aria-describedby');
  }

  errorElement.textContent = message;
}

function clearFieldErrors() {
  setFieldError('name');
  setFieldError('email');
}

function validateForm() {
  clearFieldErrors();

  const name = elements.name.value.trim();
  const email = elements.email.value.trim();
  let valid = true;

  if (!name) {
    setFieldError('name', 'O nome é obrigatório.');
    valid = false;
  } else if (name.length < 2) {
    setFieldError('name', 'O nome deve possuir pelo menos 2 caracteres.');
    valid = false;
  } else if (name.length > 100) {
    setFieldError('name', 'O nome deve possuir no máximo 100 caracteres.');
    valid = false;
  }

  if (!email) {
    setFieldError('email', 'O e-mail é obrigatório.');
    valid = false;
  } else if (!elements.email.validity.valid) {
    setFieldError('email', 'Informe um endereço de e-mail válido.');
    valid = false;
  }

  return valid;
}

function formatDate(dateValue) {
  const date = new Date(dateValue);

  if (Number.isNaN(date.getTime())) {
    return '-';
  }

  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'short',
    timeStyle: 'short'
  }).format(date);
}

function createButton(label, className, action, userId) {
  const button = document.createElement('button');

  button.type = 'button';
  button.className = `button small ${className}`;
  button.textContent = label;
  button.dataset.action = action;
  button.dataset.userId = String(userId);

  return button;
}

function renderUsers() {
  elements.tableBody.replaceChildren();

  const count = users.length;
  elements.userCount.textContent =
    count === 1 ? '1 usuário cadastrado' : `${count} usuários cadastrados`;

  elements.loadingState.hidden = true;
  elements.emptyState.hidden = count !== 0;
  elements.tableWrapper.hidden = count === 0;

  for (const user of users) {
    const row = document.createElement('tr');

    const nameCell = document.createElement('td');
    nameCell.className = 'user-name';
    nameCell.textContent = user.name;

    const emailCell = document.createElement('td');
    emailCell.className = 'user-email';
    emailCell.textContent = user.email;

    const dateCell = document.createElement('td');
    dateCell.className = 'user-date';
    dateCell.textContent = formatDate(user.createdAt);

    const actionsCell = document.createElement('td');
    actionsCell.className = 'actions-column';

    const actions = document.createElement('div');
    actions.className = 'row-actions';
    actions.append(
      createButton('Editar', 'secondary', 'edit', user.id),
      createButton('Remover', 'danger', 'delete', user.id)
    );

    actionsCell.append(actions);
    row.append(nameCell, emailCell, dateCell, actionsCell);
    elements.tableBody.append(row);
  }
}

function setLoading(isLoading) {
  elements.refreshButton.disabled = isLoading;

  if (isLoading) {
    elements.loadingState.hidden = false;
    elements.emptyState.hidden = true;
    elements.tableWrapper.hidden = true;
    elements.userCount.textContent = 'Carregando usuários...';
  }
}

async function loadUsers({ showMessage = false } = {}) {
  setLoading(true);

  try {
    users = await apiRequest(API_URL);
    renderUsers();

    if (showMessage) {
      setStatus('Lista de usuários atualizada.', 'success');
    }
  } catch (error) {
    elements.loadingState.hidden = true;
    elements.emptyState.hidden = true;
    elements.tableWrapper.hidden = true;
    elements.userCount.textContent = 'Não foi possível carregar os usuários.';
    setStatus(error.message, 'error');
  } finally {
    elements.refreshButton.disabled = false;
  }
}

function startEditing(user) {
  elements.userId.value = String(user.id);
  elements.name.value = user.name;
  elements.email.value = user.email;

  elements.formTitle.textContent = 'Editar usuário';
  elements.formDescription.textContent =
    'Altere os dados abaixo e salve as modificações.';
  elements.submitButton.textContent = 'Salvar alterações';
  elements.cancelButton.hidden = false;

  clearFieldErrors();
  clearStatus();

  document.querySelector('.form-card').scrollIntoView({
    behavior: 'smooth',
    block: 'start'
  });

  elements.name.focus();
}

function resetForm() {
  elements.form.reset();
  elements.userId.value = '';

  elements.formTitle.textContent = 'Novo usuário';
  elements.formDescription.textContent =
    'Preencha os dados abaixo para realizar o cadastro.';
  elements.submitButton.textContent = 'Cadastrar usuário';
  elements.cancelButton.hidden = true;

  clearFieldErrors();
}

function setSaving(saving) {
  isSaving = saving;

  elements.name.disabled = saving;
  elements.email.disabled = saving;
  elements.submitButton.disabled = saving;
  elements.cancelButton.disabled = saving;

  if (saving) {
    elements.submitButton.textContent = elements.userId.value
      ? 'Salvando...'
      : 'Cadastrando...';
  }
}

function applyApiFieldErrors(fields) {
  for (const fieldName of ['name', 'email']) {
    if (fields[fieldName]) {
      setFieldError(fieldName, fields[fieldName]);
    }
  }
}

async function handleSubmit(event) {
  event.preventDefault();

  if (isSaving || !validateForm()) {
    return;
  }

  clearStatus();

  const id = elements.userId.value;
  const isEditing = Boolean(id);

  const userData = {
    name: elements.name.value.trim(),
    email: elements.email.value.trim()
  };

  setSaving(true);

  try {
    await apiRequest(isEditing ? `${API_URL}/${id}` : API_URL, {
      method: isEditing ? 'PUT' : 'POST',
      body: JSON.stringify(userData)
    });

    resetForm();

    setStatus(
      isEditing
        ? 'Usuário atualizado com sucesso.'
        : 'Usuário cadastrado com sucesso.',
      'success'
    );

    await loadUsers();
    elements.name.focus();
  } catch (error) {
    applyApiFieldErrors(error.fields);
    setStatus(error.message, 'error');
  } finally {
    setSaving(false);

    if (elements.userId.value) {
      elements.submitButton.textContent = 'Salvar alterações';
    } else {
      elements.submitButton.textContent = 'Cadastrar usuário';
    }
  }
}

async function deleteUser(user) {
  const confirmed = window.confirm(
    `Deseja realmente remover o usuário "${user.name}"?`
  );

  if (!confirmed) {
    return;
  }

  clearStatus();

  try {
    await apiRequest(`${API_URL}/${user.id}`, {
      method: 'DELETE'
    });

    if (elements.userId.value === String(user.id)) {
      resetForm();
    }

    setStatus('Usuário removido com sucesso.', 'success');
    await loadUsers();
  } catch (error) {
    setStatus(error.message, 'error');
  }
}

function handleTableClick(event) {
  const button = event.target.closest('button[data-action]');

  if (!button) {
    return;
  }

  const userId = Number(button.dataset.userId);
  const user = users.find((item) => item.id === userId);

  if (!user) {
    setStatus('O usuário selecionado não foi encontrado.', 'error');
    return;
  }

  if (button.dataset.action === 'edit') {
    startEditing(user);
  }

  if (button.dataset.action === 'delete') {
    deleteUser(user);
  }
}

elements.form.addEventListener('submit', handleSubmit);

elements.cancelButton.addEventListener('click', () => {
  resetForm();
  clearStatus();
  elements.name.focus();
});

elements.refreshButton.addEventListener('click', () => {
  clearStatus();
  loadUsers({ showMessage: true });
});

elements.tableBody.addEventListener('click', handleTableClick);

elements.name.addEventListener('input', () => {
  setFieldError('name');
});

elements.email.addEventListener('input', () => {
  setFieldError('email');
});

loadUsers();
```

---

## Como executar

### 1. Pré-requisitos

Instale uma versão recente do Node.js:

```bash
node --version
```

É recomendado usar **Node.js 20 ou superior**.

### 2. Crie a estrutura de arquivos

Crie uma pasta para o projeto e salve os arquivos acima:

```bash
mkdir cadastro-usuarios
cd cadastro-usuarios
mkdir public
```

### 3. Instale as dependências

Na raiz do projeto, execute:

```bash
npm install
```

### 4. Inicie a aplicação

```bash
npm start
```

Para desenvolvimento com reinicialização automática ao alterar o backend:

```bash
npm run dev
```

### 5. Acesse no navegador

Abra:

```text
http://localhost:3000
```

O arquivo do banco será criado automaticamente em:

```text
data/usuarios.db
```

Para usar outra porta:

```bash
PORT=8080 npm start
```

No Windows PowerShell:

```powershell
$env:PORT=8080
npm start
```

## Endpoints da API

```text
GET    /api/users
GET    /api/users/:id
POST   /api/users
PUT    /api/users/:id
DELETE /api/users/:id
GET    /api/health
```

Exemplo de corpo para criação ou edição:

```json
{
  "name": "Maria da Silva",
  "email": "maria@exemplo.com"
}
```