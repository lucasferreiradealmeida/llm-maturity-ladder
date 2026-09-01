<!--
nivel: 3 - Sistema web full-stack
provider: gpt
model: gpt-5.6
tentativa: 3
temperature: 0.2
timestamp: 2026-08-31T08:30:40.780Z
metadata: {"model":"gpt-5.6-sol","usage":{"prompt_tokens":186,"completion_tokens":10341,"total_tokens":10527,"prompt_tokens_details":{"cached_tokens":0,"cache_write_tokens":0,"audio_tokens":0},"completion_tokens_details":{"reasoning_tokens":1024,"audio_tokens":0,"accepted_prediction_tokens":0,"rejected_prediction_tokens":0}},"finish_reason":"stop"}
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

Abaixo está um projeto completo usando apenas APIs nativas do Node.js e o módulo `node:sqlite`. O frontend utiliza HTML, CSS e JavaScript puros, sem frameworks.

> **Requisito:** Node.js **22.13 ou superior**, devido ao uso de `node:sqlite`.

## Estrutura do projeto

```text
cadastro-usuarios/
├── data/
│   └── .gitkeep
├── public/
│   ├── app.js
│   ├── index.html
│   └── styles.css
├── .gitignore
├── package.json
├── README.md
└── server.js
```

---

### `package.json`

```json
{
  "name": "cadastro-usuarios",
  "version": "1.0.0",
  "private": true,
  "description": "Sistema web completo para cadastro de usuários com Node.js, JavaScript e SQLite.",
  "type": "module",
  "scripts": {
    "start": "node server.js",
    "dev": "node --watch server.js"
  },
  "engines": {
    "node": ">=22.13.0"
  }
}
```

---

### `.gitignore`

```gitignore
node_modules/
data/*.db
data/*.db-shm
data/*.db-wal
.env
.DS_Store
npm-debug.log*
```

---

### `data/.gitkeep`

```text
```

---

### `server.js`

```javascript
import { createServer } from 'node:http';
import { DatabaseSync } from 'node:sqlite';
import {
  dirname,
  extname,
  join,
  resolve,
  sep
} from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  existsSync,
  mkdirSync,
  readFileSync
} from 'node:fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const PORT = normalizePort(process.env.PORT) ?? 3000;
const HOST = process.env.HOST || '0.0.0.0';

const PUBLIC_DIR = join(__dirname, 'public');
const DATA_DIR = join(__dirname, 'data');
const DATABASE_PATH = join(DATA_DIR, 'users.db');
const MAX_BODY_SIZE = 1_000_000;

mkdirSync(DATA_DIR, { recursive: true });

/*
 * Decisão de implementação:
 * - O projeto utiliza node:sqlite, disponível nas versões modernas do Node.js.
 * - Isso elimina dependências externas e mantém a aplicação simples.
 * - DatabaseSync é adequado para esta aplicação pequena de cadastro.
 */
const database = new DatabaseSync(DATABASE_PATH);

database.exec(`
  PRAGMA journal_mode = WAL;
  PRAGMA foreign_keys = ON;

  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL CHECK(length(nome) BETWEEN 2 AND 100),
    email TEXT NOT NULL COLLATE NOCASE UNIQUE,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
  );
`);

const statements = {
  listUsers: database.prepare(`
    SELECT
      id,
      nome,
      email,
      created_at AS createdAt,
      updated_at AS updatedAt
    FROM users
    ORDER BY nome COLLATE NOCASE ASC, id ASC
  `),

  findUserById: database.prepare(`
    SELECT
      id,
      nome,
      email,
      created_at AS createdAt,
      updated_at AS updatedAt
    FROM users
    WHERE id = ?
  `),

  insertUser: database.prepare(`
    INSERT INTO users (nome, email)
    VALUES (?, ?)
  `),

  updateUser: database.prepare(`
    UPDATE users
    SET
      nome = ?,
      email = ?,
      updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
  `),

  deleteUser: database.prepare(`
    DELETE FROM users
    WHERE id = ?
  `)
};

const mimeTypes = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon'
};

const server = createServer(async (request, response) => {
  setSecurityHeaders(response);

  try {
    const requestUrl = new URL(
      request.url ?? '/',
      `http://${request.headers.host || 'localhost'}`
    );

    if (requestUrl.pathname.startsWith('/api/')) {
      await handleApiRequest(request, response, requestUrl);
      return;
    }

    serveStaticFile(request, response, requestUrl);
  } catch (error) {
    console.error('Erro não tratado:', error);

    if (!response.headersSent) {
      sendJson(response, 500, {
        erro: 'Ocorreu um erro interno no servidor.'
      });
    } else {
      response.end();
    }
  }
});

server.listen(PORT, HOST, () => {
  console.log(`Servidor iniciado em http://localhost:${PORT}`);
  console.log(`Banco de dados: ${DATABASE_PATH}`);
});

async function handleApiRequest(request, response, requestUrl) {
  response.setHeader('Cache-Control', 'no-store');

  const pathname = requestUrl.pathname;
  const method = request.method ?? 'GET';

  if ((pathname === '/api/users' || pathname === '/api/users/') && method === 'GET') {
    const users = statements.listUsers.all();

    sendJson(response, 200, {
      dados: users
    });
    return;
  }

  if ((pathname === '/api/users' || pathname === '/api/users/') && method === 'POST') {
    ensureJsonContentType(request);

    const body = await readJsonBody(request);
    const validation = validateUser(body);

    if (!validation.valid) {
      sendJson(response, 400, {
        erro: 'Dados de usuário inválidos.',
        detalhes: validation.errors
      });
      return;
    }

    try {
      const result = statements.insertUser.run(
        validation.user.nome,
        validation.user.email
      );

      const userId = Number(result.lastInsertRowid);
      const createdUser = statements.findUserById.get(userId);

      sendJson(response, 201, {
        dados: createdUser
      });
    } catch (error) {
      handleDatabaseError(error, response);
    }

    return;
  }

  const userRouteMatch = pathname.match(/^\/api\/users\/(\d+)\/?$/);

  if (userRouteMatch) {
    const userId = Number(userRouteMatch[1]);

    if (!Number.isSafeInteger(userId) || userId <= 0) {
      sendJson(response, 400, {
        erro: 'Identificador de usuário inválido.'
      });
      return;
    }

    if (method === 'GET') {
      const user = statements.findUserById.get(userId);

      if (!user) {
        sendJson(response, 404, {
          erro: 'Usuário não encontrado.'
        });
        return;
      }

      sendJson(response, 200, {
        dados: user
      });
      return;
    }

    if (method === 'PUT') {
      ensureJsonContentType(request);

      const currentUser = statements.findUserById.get(userId);

      if (!currentUser) {
        sendJson(response, 404, {
          erro: 'Usuário não encontrado.'
        });
        return;
      }

      const body = await readJsonBody(request);
      const validation = validateUser(body);

      if (!validation.valid) {
        sendJson(response, 400, {
          erro: 'Dados de usuário inválidos.',
          detalhes: validation.errors
        });
        return;
      }

      try {
        statements.updateUser.run(
          validation.user.nome,
          validation.user.email,
          userId
        );

        const updatedUser = statements.findUserById.get(userId);

        sendJson(response, 200, {
          dados: updatedUser
        });
      } catch (error) {
        handleDatabaseError(error, response);
      }

      return;
    }

    if (method === 'DELETE') {
      const result = statements.deleteUser.run(userId);

      if (result.changes === 0) {
        sendJson(response, 404, {
          erro: 'Usuário não encontrado.'
        });
        return;
      }

      response.writeHead(204);
      response.end();
      return;
    }

    sendJson(response, 405, {
      erro: 'Método não permitido.'
    });
    return;
  }

  sendJson(response, 404, {
    erro: 'Rota da API não encontrada.'
  });
}

function serveStaticFile(request, response, requestUrl) {
  const method = request.method ?? 'GET';

  if (method !== 'GET' && method !== 'HEAD') {
    sendJson(response, 405, {
      erro: 'Método não permitido.'
    });
    return;
  }

  let pathname;

  try {
    pathname = decodeURIComponent(requestUrl.pathname);
  } catch {
    sendJson(response, 400, {
      erro: 'Endereço inválido.'
    });
    return;
  }

  if (pathname === '/') {
    pathname = '/index.html';
  }

  const publicRoot = resolve(PUBLIC_DIR);
  const requestedFile = resolve(PUBLIC_DIR, `.${pathname}`);

  /*
   * Evita acesso a arquivos fora da pasta public por meio de caminhos
   * como ../../server.js.
   */
  if (
    requestedFile !== publicRoot &&
    !requestedFile.startsWith(`${publicRoot}${sep}`)
  ) {
    sendJson(response, 403, {
      erro: 'Acesso negado.'
    });
    return;
  }

  if (!existsSync(requestedFile)) {
    sendJson(response, 404, {
      erro: 'Arquivo não encontrado.'
    });
    return;
  }

  try {
    const content = readFileSync(requestedFile);
    const contentType =
      mimeTypes[extname(requestedFile).toLowerCase()] ??
      'application/octet-stream';

    response.writeHead(200, {
      'Content-Type': contentType,
      'Content-Length': content.length,
      'Cache-Control': 'no-cache'
    });

    if (method === 'HEAD') {
      response.end();
      return;
    }

    response.end(content);
  } catch (error) {
    console.error('Erro ao servir arquivo estático:', error);

    sendJson(response, 500, {
      erro: 'Não foi possível carregar o arquivo solicitado.'
    });
  }
}

function validateUser(input) {
  const errors = [];

  if (
    input === null ||
    typeof input !== 'object' ||
    Array.isArray(input)
  ) {
    return {
      valid: false,
      errors: ['O corpo da requisição deve ser um objeto JSON.']
    };
  }

  const nome = typeof input.nome === 'string'
    ? input.nome.trim().replace(/\s+/g, ' ')
    : '';

  const email = typeof input.email === 'string'
    ? input.email.trim().toLowerCase()
    : '';

  if (nome.length < 2) {
    errors.push('O nome deve possuir pelo menos 2 caracteres.');
  }

  if (nome.length > 100) {
    errors.push('O nome deve possuir no máximo 100 caracteres.');
  }

  if (email.length === 0) {
    errors.push('O e-mail é obrigatório.');
  } else if (email.length > 254) {
    errors.push('O e-mail deve possuir no máximo 254 caracteres.');
  } else if (!isValidEmail(email)) {
    errors.push('Informe um endereço de e-mail válido.');
  }

  return {
    valid: errors.length === 0,
    errors,
    user: {
      nome,
      email
    }
  };
}

function isValidEmail(email) {
  /*
   * Validação deliberadamente simples. A validação completa da RFC de
   * e-mails seria excessiva para um cadastro comum.
   */
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function ensureJsonContentType(request) {
  const contentType = request.headers['content-type'] ?? '';

  if (!contentType.toLowerCase().startsWith('application/json')) {
    const error = new Error(
      'O cabeçalho Content-Type deve ser application/json.'
    );

    error.statusCode = 415;
    throw error;
  }
}

function readJsonBody(request) {
  return new Promise((resolveBody, rejectBody) => {
    let body = '';
    let bodySize = 0;
    let rejected = false;

    request.setEncoding('utf8');

    request.on('data', (chunk) => {
      if (rejected) {
        return;
      }

      bodySize += Buffer.byteLength(chunk, 'utf8');

      if (bodySize > MAX_BODY_SIZE) {
        rejected = true;

        const error = new Error(
          'O corpo da requisição excede o limite permitido.'
        );

        error.statusCode = 413;
        rejectBody(error);
        return;
      }

      body += chunk;
    });

    request.on('end', () => {
      if (rejected) {
        return;
      }

      if (!body.trim()) {
        const error = new Error('O corpo da requisição não pode estar vazio.');
        error.statusCode = 400;
        rejectBody(error);
        return;
      }

      try {
        resolveBody(JSON.parse(body));
      } catch {
        const error = new Error('O corpo da requisição contém JSON inválido.');
        error.statusCode = 400;
        rejectBody(error);
      }
    });

    request.on('error', (error) => {
      rejectBody(error);
    });
  });
}

function handleDatabaseError(error, response) {
  console.error('Erro no banco de dados:', error);

  const message = String(error?.message ?? '');

  if (
    message.includes('UNIQUE constraint failed') ||
    message.includes('users.email')
  ) {
    sendJson(response, 409, {
      erro: 'Já existe um usuário cadastrado com este e-mail.'
    });
    return;
  }

  if (message.includes('CHECK constraint failed')) {
    sendJson(response, 400, {
      erro: 'Os dados informados não atendem às regras de validação.'
    });
    return;
  }

  sendJson(response, 500, {
    erro: 'Não foi possível executar a operação no banco de dados.'
  });
}

function sendJson(response, statusCode, payload) {
  if (response.headersSent) {
    return;
  }

  const content = JSON.stringify(payload);

  response.writeHead(statusCode, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': Buffer.byteLength(content)
  });

  response.end(content);
}

function setSecurityHeaders(response) {
  response.setHeader('X-Content-Type-Options', 'nosniff');
  response.setHeader('X-Frame-Options', 'DENY');
  response.setHeader('Referrer-Policy', 'no-referrer');
  response.setHeader(
    'Content-Security-Policy',
    "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'"
  );
}

function normalizePort(value) {
  if (value === undefined || value === null || value === '') {
    return null;
  }

  const port = Number(value);

  if (!Number.isInteger(port) || port < 1 || port > 65535) {
    throw new Error(`Porta inválida: ${value}`);
  }

  return port;
}

function shutdown(signal) {
  console.log(`\nSinal ${signal} recebido. Encerrando aplicação...`);

  server.close(() => {
    try {
      database.close();
    } finally {
      process.exit(0);
    }
  });

  setTimeout(() => {
    console.error('Encerramento forçado após tempo limite.');
    process.exit(1);
  }, 5_000).unref();
}

process.on('SIGINT', () => shutdown('SIGINT'));
process.on('SIGTERM', () => shutdown('SIGTERM'));

process.on('uncaughtException', (error) => {
  console.error('Exceção não capturada:', error);
  shutdown('uncaughtException');
});

process.on('unhandledRejection', (reason) => {
  console.error('Promise rejeitada sem tratamento:', reason);
});
```

---

### `public/index.html`

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
  >
  <meta
    name="description"
    content="Sistema de cadastro e gerenciamento de usuários"
  >
  <title>Cadastro de usuários</title>
  <link rel="stylesheet" href="/styles.css">
  <script src="/app.js" defer></script>
</head>
<body>
  <header class="topbar">
    <div class="container topbar-content">
      <div>
        <p class="eyebrow">Administração</p>
        <h1>Cadastro de usuários</h1>
      </div>

      <button id="new-user-button" class="button button-primary" type="button">
        Novo usuário
      </button>
    </div>
  </header>

  <main class="container">
    <section
      id="user-form-section"
      class="card form-card"
      aria-labelledby="form-title"
      hidden
    >
      <div class="section-header">
        <div>
          <h2 id="form-title">Cadastrar usuário</h2>
          <p>Preencha o nome e o endereço de e-mail.</p>
        </div>

        <button
          id="close-form-button"
          class="icon-button"
          type="button"
          aria-label="Fechar formulário"
          title="Fechar formulário"
        >
          ×
        </button>
      </div>

      <form id="user-form">
        <input id="user-id" type="hidden">

        <div class="form-grid">
          <div class="field">
            <label for="name">Nome</label>
            <input
              id="name"
              name="nome"
              type="text"
              minlength="2"
              maxlength="100"
              autocomplete="name"
              placeholder="Ex.: Maria da Silva"
              required
            >
          </div>

          <div class="field">
            <label for="email">E-mail</label>
            <input
              id="email"
              name="email"
              type="email"
              maxlength="254"
              autocomplete="email"
              placeholder="Ex.: maria@empresa.com"
              required
            >
          </div>
        </div>

        <div class="form-actions">
          <button
            id="cancel-button"
            class="button button-secondary"
            type="button"
          >
            Cancelar
          </button>

          <button
            id="save-button"
            class="button button-primary"
            type="submit"
          >
            Salvar usuário
          </button>
        </div>
      </form>
    </section>

    <section class="card" aria-labelledby="users-title">
      <div class="section-header users-header">
        <div>
          <h2 id="users-title">Usuários cadastrados</h2>
          <p id="users-summary">Carregando usuários...</p>
        </div>

        <button
          id="refresh-button"
          class="button button-secondary"
          type="button"
        >
          Atualizar
        </button>
      </div>

      <div id="loading-state" class="state-message">
        Carregando usuários...
      </div>

      <div id="error-state" class="state-message state-error" hidden>
        <p id="error-message">Não foi possível carregar os usuários.</p>
        <button
          id="retry-button"
          class="button button-secondary"
          type="button"
        >
          Tentar novamente
        </button>
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

      <div id="empty-state" class="state-message" hidden>
        <p>Nenhum usuário foi cadastrado.</p>
        <button
          id="empty-new-user-button"
          class="button button-primary"
          type="button"
        >
          Cadastrar primeiro usuário
        </button>
      </div>
    </section>
  </main>

  <div
    id="notification"
    class="notification"
    role="status"
    aria-live="polite"
    hidden
  ></div>
</body>
</html>
```

---

### `public/styles.css`

```css
:root {
  color-scheme: light;
  --background: #f4f6f8;
  --surface: #ffffff;
  --surface-muted: #f8fafc;
  --border: #dbe1e8;
  --text: #172033;
  --text-muted: #5f6b7a;
  --primary: #2457d6;
  --primary-hover: #1945b5;
  --danger: #bf2c2c;
  --danger-hover: #9f2020;
  --success: #176b41;
  --shadow: 0 12px 35px rgb(23 32 51 / 8%);
  --radius: 12px;
}

* {
  box-sizing: border-box;
}

html {
  min-width: 320px;
  background: var(--background);
}

body {
  min-height: 100vh;
  margin: 0;
  color: var(--text);
  background: var(--background);
  font-family:
    Inter,
    ui-sans-serif,
    system-ui,
    -apple-system,
    BlinkMacSystemFont,
    "Segoe UI",
    sans-serif;
  line-height: 1.5;
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

[hidden] {
  display: none !important;
}

.container {
  width: min(1120px, calc(100% - 32px));
  margin-inline: auto;
}

.topbar {
  padding: 28px 0;
  color: #ffffff;
  background:
    linear-gradient(135deg, #173d9e, #2a65e8);
  box-shadow: 0 4px 20px rgb(23 61 158 / 20%);
}

.topbar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.eyebrow {
  margin: 0 0 4px;
  color: #cedaff;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

h1,
h2,
p {
  margin-top: 0;
}

h1 {
  margin-bottom: 0;
  font-size: clamp(1.6rem, 4vw, 2.2rem);
}

h2 {
  margin-bottom: 5px;
  font-size: 1.25rem;
}

main {
  display: grid;
  gap: 22px;
  padding-top: 28px;
  padding-bottom: 48px;
}

.card {
  overflow: hidden;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface);
  box-shadow: var(--shadow);
}

.form-card {
  padding: 24px;
}

.section-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
}

.section-header p {
  margin-bottom: 0;
  color: var(--text-muted);
}

.users-header {
  align-items: center;
  padding: 22px 24px;
  border-bottom: 1px solid var(--border);
}

.icon-button {
  display: inline-grid;
  width: 38px;
  height: 38px;
  place-items: center;
  border: 0;
  border-radius: 50%;
  color: var(--text-muted);
  background: transparent;
  font-size: 1.8rem;
  line-height: 1;
}

.icon-button:hover {
  color: var(--text);
  background: var(--surface-muted);
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
  margin-top: 24px;
}

.field {
  display: grid;
  gap: 7px;
}

.field label {
  font-size: 0.9rem;
  font-weight: 700;
}

.field input {
  width: 100%;
  height: 44px;
  padding: 0 13px;
  border: 1px solid #bec7d2;
  border-radius: 8px;
  outline: none;
  color: var(--text);
  background: #ffffff;
  transition:
    border-color 150ms ease,
    box-shadow 150ms ease;
}

.field input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgb(36 87 214 / 14%);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 22px;
}

.button {
  min-height: 40px;
  padding: 8px 16px;
  border: 1px solid transparent;
  border-radius: 8px;
  font-weight: 700;
  transition:
    background 150ms ease,
    border-color 150ms ease,
    transform 100ms ease;
}

.button:active:not(:disabled) {
  transform: translateY(1px);
}

.button-primary {
  color: #ffffff;
  background: var(--primary);
}

.button-primary:hover:not(:disabled) {
  background: var(--primary-hover);
}

.button-secondary {
  border-color: #c9d1db;
  color: var(--text);
  background: #ffffff;
}

.button-secondary:hover:not(:disabled) {
  background: var(--surface-muted);
}

.button-danger {
  border-color: #f0b7b7;
  color: var(--danger);
  background: #fff7f7;
}

.button-danger:hover:not(:disabled) {
  border-color: var(--danger);
  color: #ffffff;
  background: var(--danger-hover);
}

.button-small {
  min-height: 34px;
  padding: 5px 10px;
  font-size: 0.85rem;
}

.table-wrapper {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 15px 24px;
  border-bottom: 1px solid var(--border);
  text-align: left;
  vertical-align: middle;
}

th {
  color: var(--text-muted);
  background: var(--surface-muted);
  font-size: 0.78rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

tbody tr:last-child td {
  border-bottom: 0;
}

tbody tr:hover {
  background: #fafbfc;
}

.actions-column {
  width: 190px;
  text-align: right;
}

.row-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.user-name {
  font-weight: 700;
}

.user-email,
.user-date {
  color: var(--text-muted);
}

.state-message {
  padding: 42px 24px;
  text-align: center;
  color: var(--text-muted);
}

.state-message p {
  margin-bottom: 16px;
}

.state-error {
  color: var(--danger);
}

.notification {
  position: fixed;
  right: 22px;
  bottom: 22px;
  z-index: 100;
  width: min(420px, calc(100% - 44px));
  padding: 14px 18px;
  border-radius: 9px;
  color: #ffffff;
  background: var(--success);
  box-shadow: 0 12px 30px rgb(0 0 0 / 20%);
  font-weight: 650;
}

.notification.error {
  background: var(--danger);
}

@media (max-width: 760px) {
  .topbar-content,
  .section-header {
    align-items: stretch;
    flex-direction: column;
  }

  .topbar-content .button {
    width: 100%;
  }

  .users-header {
    align-items: stretch;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .section-header .icon-button {
    position: absolute;
    align-self: flex-end;
  }

  th,
  td {
    padding: 13px 16px;
  }

  .actions-column {
    width: auto;
  }

  .row-actions {
    min-width: 160px;
  }
}

@media (max-width: 520px) {
  .container {
    width: min(100% - 20px, 1120px);
  }

  .topbar {
    padding: 22px 0;
  }

  main {
    padding-top: 18px;
  }

  .form-card,
  .users-header {
    padding: 18px;
  }

  .form-actions {
    flex-direction: column-reverse;
  }

  .form-actions .button {
    width: 100%;
  }
}
```

---

### `public/app.js`

```javascript
const elements = {
  newUserButton: document.querySelector('#new-user-button'),
  emptyNewUserButton: document.querySelector('#empty-new-user-button'),
  refreshButton: document.querySelector('#refresh-button'),
  retryButton: document.querySelector('#retry-button'),

  formSection: document.querySelector('#user-form-section'),
  formTitle: document.querySelector('#form-title'),
  form: document.querySelector('#user-form'),
  userId: document.querySelector('#user-id'),
  name: document.querySelector('#name'),
  email: document.querySelector('#email'),
  saveButton: document.querySelector('#save-button'),
  cancelButton: document.querySelector('#cancel-button'),
  closeFormButton: document.querySelector('#close-form-button'),

  usersSummary: document.querySelector('#users-summary'),
  loadingState: document.querySelector('#loading-state'),
  errorState: document.querySelector('#error-state'),
  errorMessage: document.querySelector('#error-message'),
  tableWrapper: document.querySelector('#table-wrapper'),
  tableBody: document.querySelector('#users-table-body'),
  emptyState: document.querySelector('#empty-state'),

  notification: document.querySelector('#notification')
};

let users = [];
let notificationTimer = null;

elements.newUserButton.addEventListener('click', openCreateForm);
elements.emptyNewUserButton.addEventListener('click', openCreateForm);
elements.cancelButton.addEventListener('click', closeForm);
elements.closeFormButton.addEventListener('click', closeForm);
elements.refreshButton.addEventListener('click', loadUsers);
elements.retryButton.addEventListener('click', loadUsers);
elements.form.addEventListener('submit', saveUser);
elements.tableBody.addEventListener('click', handleTableAction);

loadUsers();

async function loadUsers() {
  showListState('loading');
  elements.refreshButton.disabled = true;

  try {
    const response = await apiRequest('/api/users');
    users = response.dados ?? [];

    renderUsers();
  } catch (error) {
    console.error(error);
    elements.errorMessage.textContent =
      error.message || 'Não foi possível carregar os usuários.';

    showListState('error');
  } finally {
    elements.refreshButton.disabled = false;
  }
}

function renderUsers() {
  elements.tableBody.replaceChildren();

  const total = users.length;

  elements.usersSummary.textContent = total === 1
    ? '1 usuário cadastrado'
    : `${total} usuários cadastrados`;

  if (total === 0) {
    showListState('empty');
    return;
  }

  for (const user of users) {
    elements.tableBody.append(createUserRow(user));
  }

  showListState('table');
}

function createUserRow(user) {
  const row = document.createElement('tr');

  const nameCell = document.createElement('td');
  nameCell.className = 'user-name';
  nameCell.textContent = user.nome;

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

  const editButton = document.createElement('button');
  editButton.type = 'button';
  editButton.className = 'button button-secondary button-small';
  editButton.dataset.action = 'edit';
  editButton.dataset.id = String(user.id);
  editButton.textContent = 'Editar';
  editButton.setAttribute('aria-label', `Editar ${user.nome}`);

  const deleteButton = document.createElement('button');
  deleteButton.type = 'button';
  deleteButton.className = 'button button-danger button-small';
  deleteButton.dataset.action = 'delete';
  deleteButton.dataset.id = String(user.id);
  deleteButton.textContent = 'Remover';
  deleteButton.setAttribute('aria-label', `Remover ${user.nome}`);

  actions.append(editButton, deleteButton);
  actionsCell.append(actions);
  row.append(nameCell, emailCell, dateCell, actionsCell);

  return row;
}

function handleTableAction(event) {
  const button = event.target.closest('button[data-action]');

  if (!button) {
    return;
  }

  const userId = Number(button.dataset.id);
  const user = users.find((item) => item.id === userId);

  if (!user) {
    showNotification('O usuário selecionado não foi encontrado.', true);
    return;
  }

  if (button.dataset.action === 'edit') {
    openEditForm(user);
    return;
  }

  if (button.dataset.action === 'delete') {
    deleteUser(user, button);
  }
}

function openCreateForm() {
  elements.form.reset();
  elements.userId.value = '';
  elements.formTitle.textContent = 'Cadastrar usuário';
  elements.saveButton.textContent = 'Salvar usuário';
  elements.formSection.hidden = false;

  focusForm();
}

function openEditForm(user) {
  elements.form.reset();
  elements.userId.value = String(user.id);
  elements.name.value = user.nome;
  elements.email.value = user.email;
  elements.formTitle.textContent = 'Editar usuário';
  elements.saveButton.textContent = 'Salvar alterações';
  elements.formSection.hidden = false;

  focusForm();
}

function closeForm() {
  elements.form.reset();
  elements.userId.value = '';
  elements.formSection.hidden = true;
}

function focusForm() {
  elements.formSection.scrollIntoView({
    behavior: 'smooth',
    block: 'start'
  });

  window.setTimeout(() => {
    elements.name.focus();
  }, 250);
}

async function saveUser(event) {
  event.preventDefault();

  if (!elements.form.reportValidity()) {
    return;
  }

  const userId = elements.userId.value;
  const isEditing = userId !== '';

  const payload = {
    nome: elements.name.value,
    email: elements.email.value
  };

  setFormLoading(true);

  try {
    await apiRequest(
      isEditing ? `/api/users/${userId}` : '/api/users',
      {
        method: isEditing ? 'PUT' : 'POST',
        body: JSON.stringify(payload)
      }
    );

    closeForm();

    showNotification(
      isEditing
        ? 'Usuário atualizado com sucesso.'
        : 'Usuário cadastrado com sucesso.'
    );

    await loadUsers();
  } catch (error) {
    console.error(error);
    showNotification(error.message || 'Não foi possível salvar o usuário.', true);
  } finally {
    setFormLoading(false);
  }
}

async function deleteUser(user, button) {
  const confirmed = window.confirm(
    `Deseja realmente remover o usuário "${user.nome}"?`
  );

  if (!confirmed) {
    return;
  }

  button.disabled = true;
  button.textContent = 'Removendo...';

  try {
    await apiRequest(`/api/users/${user.id}`, {
      method: 'DELETE'
    });

    showNotification('Usuário removido com sucesso.');

    if (elements.userId.value === String(user.id)) {
      closeForm();
    }

    await loadUsers();
  } catch (error) {
    console.error(error);
    showNotification(error.message || 'Não foi possível remover o usuário.', true);

    button.disabled = false;
    button.textContent = 'Remover';
  }
}

async function apiRequest(url, options = {}) {
  const headers = {
    Accept: 'application/json',
    ...options.headers
  };

  if (options.body !== undefined) {
    headers['Content-Type'] = 'application/json';
  }

  let response;

  try {
    response = await fetch(url, {
      ...options,
      headers
    });
  } catch {
    throw new Error(
      'Não foi possível conectar ao servidor. Verifique sua conexão.'
    );
  }

  if (response.status === 204) {
    return null;
  }

  const contentType = response.headers.get('content-type') ?? '';
  let responseBody = null;

  if (contentType.includes('application/json')) {
    responseBody = await response.json();
  }

  if (!response.ok) {
    const details = Array.isArray(responseBody?.detalhes)
      ? ` ${responseBody.detalhes.join(' ')}`
      : '';

    throw new Error(
      `${responseBody?.erro || `Erro HTTP ${response.status}.`}${details}`
    );
  }

  return responseBody;
}

function showListState(state) {
  elements.loadingState.hidden = state !== 'loading';
  elements.errorState.hidden = state !== 'error';
  elements.tableWrapper.hidden = state !== 'table';
  elements.emptyState.hidden = state !== 'empty';

  if (state === 'loading') {
    elements.usersSummary.textContent = 'Carregando usuários...';
  }

  if (state === 'error') {
    elements.usersSummary.textContent = 'Falha ao carregar usuários';
  }
}

function setFormLoading(isLoading) {
  elements.saveButton.disabled = isLoading;
  elements.cancelButton.disabled = isLoading;
  elements.closeFormButton.disabled = isLoading;
  elements.name.disabled = isLoading;
  elements.email.disabled = isLoading;

  if (isLoading) {
    elements.saveButton.textContent = 'Salvando...';
    return;
  }

  elements.saveButton.textContent = elements.userId.value
    ? 'Salvar alterações'
    : 'Salvar usuário';
}

function showNotification(message, isError = false) {
  window.clearTimeout(notificationTimer);

  elements.notification.textContent = message;
  elements.notification.classList.toggle('error', isError);
  elements.notification.hidden = false;

  notificationTimer = window.setTimeout(() => {
    elements.notification.hidden = true;
  }, 4_500);
}

function formatDate(sqliteDate) {
  if (!sqliteDate) {
    return '—';
  }

  /*
   * O SQLite retorna CURRENT_TIMESTAMP como "YYYY-MM-DD HH:mm:ss" em UTC.
   * A conversão abaixo adiciona a indicação explícita de UTC.
   */
  const normalizedDate = sqliteDate.includes('T')
    ? sqliteDate
    : `${sqliteDate.replace(' ', 'T')}Z`;

  const date = new Date(normalizedDate);

  if (Number.isNaN(date.getTime())) {
    return sqliteDate;
  }

  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'short',
    timeStyle: 'short'
  }).format(date);
}
```

---

### `README.md`

```markdown
# Cadastro de usuários

Sistema web completo para listar, cadastrar, editar e remover usuários.

## Tecnologias

- Node.js
- JavaScript
- SQLite por meio do módulo nativo `node:sqlite`
- HTML e CSS
- API REST sem frameworks externos

## Requisitos

- Node.js 22.13 ou superior
- npm

Confira a versão instalada:

```bash
node --version
```

## Instalação

Entre na pasta do projeto e execute:

```bash
npm install
```

O projeto não possui dependências externas. O comando é mantido para validar
o projeto e seguir o fluxo padrão de aplicações Node.js.

## Execução

Modo normal:

```bash
npm start
```

Modo de desenvolvimento, reiniciando o servidor quando um arquivo mudar:

```bash
npm run dev
```

Abra no navegador:

```text
http://localhost:3000
```

## Configuração opcional

É possível alterar a porta:

### Linux ou macOS

```bash
PORT=8080 npm start
```

### Windows PowerShell

```powershell
$env:PORT=8080
npm start
```

## Banco de dados

O arquivo SQLite é criado automaticamente em:

```text
data/users.db
```

Para apagar todos os dados, pare o servidor e remova esse arquivo.

## API REST

### Listar usuários

```http
GET /api/users
```

### Consultar usuário

```http
GET /api/users/:id
```

### Cadastrar usuário

```http
POST /api/users
Content-Type: application/json
```

Exemplo:

```json
{
  "nome": "Maria da Silva",
  "email": "maria@example.com"
}
```

### Editar usuário

```http
PUT /api/users/:id
Content-Type: application/json
```

Exemplo:

```json
{
  "nome": "Maria Souza",
  "email": "maria.souza@example.com"
}
```

### Remover usuário

```http
DELETE /api/users/:id
```

## Regras de validação

- O nome é obrigatório.
- O nome deve possuir entre 2 e 100 caracteres.
- O e-mail é obrigatório.
- O e-mail deve ser válido.
- O e-mail deve ser único, sem diferenciação entre letras maiúsculas e minúsculas.
```

## Como executar

Após criar os arquivos:

```bash
cd cadastro-usuarios
npm install
npm start
```

Depois, acesse:

```text
http://localhost:3000
```