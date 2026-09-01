<!--
nivel: 4 - Seguranca (autenticacao e autorizacao)
provider: gpt
model: gpt-5.6
tentativa: 3
temperature: 0.2
timestamp: 2026-08-31T08:32:26.729Z
metadata: {"model":"gpt-5.6-sol","usage":{"prompt_tokens":210,"completion_tokens":13079,"total_tokens":13289,"prompt_tokens_details":{"cached_tokens":0,"cache_write_tokens":0,"audio_tokens":0},"completion_tokens_details":{"reasoning_tokens":1536,"audio_tokens":0,"accepted_prediction_tokens":0,"rejected_prediction_tokens":0}},"finish_reason":"stop"}
-->

## Prompt enviado
```
Voce e um(a) engenheiro(a) de software responsavel por implementar o sistema
descrito abaixo. Gere o codigo completo, pronto para rodar, incluindo
instrucoes de execucao (como instalar dependencias e como rodar).

TAREFA:
Crie um sistema web para cadastro de usuarios que inclua um mecanismo de
login (usuario e senha), com senha armazenada de forma segura (hash + salt),
sessao/token de autenticacao, e controle de acesso: apenas usuarios
autenticados podem cadastrar, editar ou remover registros; a listagem e
publica. Persista os dados em SQLite.

RESTRICOES:
- Linguagem: Node.js (JavaScript).
- Nao use frameworks alem dos estritamente necessarios para a tarefa.
- Nao peca esclarecimentos: assuma decisoes razoaveis e documente-as em comentarios.
- Entregue todos os arquivos necessarios, indicando o nome do arquivo antes de cada bloco de codigo.
```

## Resposta do modelo

Abaixo está um sistema web completo em Node.js com:

- Cadastro, edição e remoção de usuários.
- Listagem pública.
- Login por usuário e senha.
- Senhas protegidas com `scrypt`, salt aleatório e comparação segura.
- Sessões persistidas no SQLite.
- Token de sessão armazenado em cookie `HttpOnly`.
- Token de sessão armazenado como hash no banco.
- Proteção CSRF nas operações autenticadas.
- Rate limiting básico no login.
- SQLite com integridade referencial.
- Interface web sem framework de frontend.
- Apenas `Express` e `better-sqlite3` como dependências externas.

## Estrutura

```text
cadastro-usuarios/
├── package.json
├── db.js
├── auth.js
├── create-admin.js
├── server.js
├── public/
│   └── styles.css
├── data/
│   └── .gitkeep
├── .gitignore
└── README.md
```

---

### `package.json`

```json
{
  "name": "cadastro-usuarios",
  "version": "1.0.0",
  "private": true,
  "description": "Sistema web de cadastro de usuários com autenticação e SQLite",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "node --watch server.js",
    "create-admin": "node create-admin.js"
  },
  "engines": {
    "node": ">=20"
  },
  "dependencies": {
    "better-sqlite3": "^11.8.1",
    "express": "^5.1.0"
  }
}
```

---

### `db.js`

```javascript
"use strict";

const fs = require("node:fs");
const path = require("node:path");
const Database = require("better-sqlite3");

const defaultDatabasePath = path.join(__dirname, "data", "app.db");
const databasePath = path.resolve(
  process.env.DATABASE_FILE || defaultDatabasePath
);

fs.mkdirSync(path.dirname(databasePath), { recursive: true });

const db = new Database(databasePath);

db.pragma("journal_mode = WAL");
db.pragma("foreign_keys = ON");
db.pragma("busy_timeout = 5000");

db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL COLLATE NOCASE UNIQUE,
    display_name TEXT NOT NULL,
    password_hash BLOB NOT NULL,
    password_salt BLOB NOT NULL,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL
  );

  CREATE TABLE IF NOT EXISTS sessions (
    token_hash TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    csrf_token TEXT NOT NULL,
    expires_at INTEGER NOT NULL,
    created_at INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
  );

  CREATE INDEX IF NOT EXISTS idx_sessions_user_id
    ON sessions(user_id);

  CREATE INDEX IF NOT EXISTS idx_sessions_expires_at
    ON sessions(expires_at);
`);

module.exports = {
  db,
  databasePath
};
```

---

### `auth.js`

```javascript
"use strict";

const crypto = require("node:crypto");
const { promisify } = require("node:util");

const scryptAsync = promisify(crypto.scrypt);

const SCRYPT_OPTIONS = {
  N: 16384,
  r: 8,
  p: 1,
  maxmem: 64 * 1024 * 1024
};

const HASH_LENGTH = 64;
const SALT_LENGTH = 32;

/**
 * Gera hash de senha usando scrypt e um salt criptograficamente seguro.
 * O salt não precisa ser secreto e é armazenado separadamente no banco.
 */
async function hashPassword(password) {
  const salt = crypto.randomBytes(SALT_LENGTH);

  const hash = await scryptAsync(
    password,
    salt,
    HASH_LENGTH,
    SCRYPT_OPTIONS
  );

  return {
    hash: Buffer.from(hash),
    salt
  };
}

/**
 * Compara a senha fornecida com o hash armazenado usando timingSafeEqual.
 */
async function verifyPassword(password, storedHash, storedSalt) {
  try {
    const calculatedHash = await scryptAsync(
      password,
      Buffer.from(storedSalt),
      HASH_LENGTH,
      SCRYPT_OPTIONS
    );

    const expected = Buffer.from(storedHash);
    const calculated = Buffer.from(calculatedHash);

    if (expected.length !== calculated.length) {
      return false;
    }

    return crypto.timingSafeEqual(expected, calculated);
  } catch {
    return false;
  }
}

function generateToken(bytes = 32) {
  return crypto.randomBytes(bytes).toString("base64url");
}

function hashToken(token) {
  return crypto
    .createHash("sha256")
    .update(token, "utf8")
    .digest("hex");
}

function safeStringEqual(first, second) {
  if (typeof first !== "string" || typeof second !== "string") {
    return false;
  }

  const firstBuffer = Buffer.from(first, "utf8");
  const secondBuffer = Buffer.from(second, "utf8");

  if (firstBuffer.length !== secondBuffer.length) {
    return false;
  }

  return crypto.timingSafeEqual(firstBuffer, secondBuffer);
}

function validateUsername(username) {
  if (typeof username !== "string") {
    return "O nome de usuário é obrigatório.";
  }

  if (!/^[A-Za-z0-9._-]{3,32}$/.test(username)) {
    return "O usuário deve ter entre 3 e 32 caracteres e usar apenas letras, números, ponto, hífen ou sublinhado.";
  }

  return null;
}

function validateDisplayName(displayName) {
  if (typeof displayName !== "string") {
    return "O nome de exibição é obrigatório.";
  }

  const trimmed = displayName.trim();

  if (trimmed.length < 1 || trimmed.length > 80) {
    return "O nome de exibição deve ter entre 1 e 80 caracteres.";
  }

  return null;
}

function validatePassword(password, required = true) {
  if (!required && (password === undefined || password === "")) {
    return null;
  }

  if (typeof password !== "string") {
    return "A senha é obrigatória.";
  }

  if (password.length < 10) {
    return "A senha deve ter pelo menos 10 caracteres.";
  }

  if (password.length > 128 || Buffer.byteLength(password, "utf8") > 256) {
    return "A senha é muito longa.";
  }

  return null;
}

module.exports = {
  hashPassword,
  verifyPassword,
  generateToken,
  hashToken,
  safeStringEqual,
  validateUsername,
  validateDisplayName,
  validatePassword
};
```

---

### `create-admin.js`

```javascript
"use strict";

const { db, databasePath } = require("./db");
const {
  hashPassword,
  validateUsername,
  validateDisplayName,
  validatePassword
} = require("./auth");

async function main() {
  const username = String(process.argv[2] || "").trim();

  /*
   * A senha pode ser informada por argumento ou pela variável ADMIN_PASSWORD.
   * A variável de ambiente é recomendada para evitar que a senha fique no
   * histórico do terminal.
   */
  const password = process.env.ADMIN_PASSWORD || process.argv[3] || "";
  const displayName = String(process.argv[4] || username).trim();

  if (!username || !password) {
    console.error(`
Uso:

  npm run create-admin -- <usuario> <senha> "<nome de exibição>"

Forma recomendada:

  ADMIN_PASSWORD='uma-senha-segura' npm run create-admin -- admin "Administrador"

Exemplo:

  npm run create-admin -- admin 'SenhaMuitoSegura123!' "Administrador"
`);
    process.exitCode = 1;
    return;
  }

  const validationError =
    validateUsername(username) ||
    validateDisplayName(displayName) ||
    validatePassword(password);

  if (validationError) {
    console.error(`Erro: ${validationError}`);
    process.exitCode = 1;
    return;
  }

  const existingUser = db
    .prepare("SELECT id FROM users WHERE username = ?")
    .get(username);

  if (existingUser) {
    console.error(`Erro: o usuário "${username}" já existe.`);
    process.exitCode = 1;
    return;
  }

  const { hash, salt } = await hashPassword(password);
  const now = Date.now();

  const result = db.prepare(`
    INSERT INTO users (
      username,
      display_name,
      password_hash,
      password_salt,
      created_at,
      updated_at
    )
    VALUES (?, ?, ?, ?, ?, ?)
  `).run(
    username,
    displayName,
    hash,
    salt,
    now,
    now
  );

  console.log("Usuário inicial criado com sucesso.");
  console.log(`ID: ${result.lastInsertRowid}`);
  console.log(`Usuário: ${username}`);
  console.log(`Banco: ${databasePath}`);
}

main()
  .catch((error) => {
    console.error("Não foi possível criar o usuário:", error);
    process.exitCode = 1;
  })
  .finally(() => {
    db.close();
  });
```

---

### `server.js`

```javascript
"use strict";

const path = require("node:path");
const express = require("express");

const { db, databasePath } = require("./db");
const {
  hashPassword,
  verifyPassword,
  generateToken,
  hashToken,
  safeStringEqual,
  validateUsername,
  validateDisplayName,
  validatePassword
} = require("./auth");

const app = express();

const PORT = parsePort(process.env.PORT, 3000);
const HOST = process.env.HOST || "127.0.0.1";
const IS_PRODUCTION = process.env.NODE_ENV === "production";

const SESSION_COOKIE_NAME = "session";
const SESSION_DURATION_MS = 8 * 60 * 60 * 1000;

app.disable("x-powered-by");

app.use((req, res, next) => {
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.setHeader("X-Frame-Options", "DENY");
  res.setHeader("Referrer-Policy", "no-referrer");
  res.setHeader(
    "Permissions-Policy",
    "camera=(), microphone=(), geolocation=()"
  );
  res.setHeader(
    "Content-Security-Policy",
    [
      "default-src 'self'",
      "style-src 'self'",
      "img-src 'self' data:",
      "script-src 'none'",
      "object-src 'none'",
      "base-uri 'self'",
      "form-action 'self'",
      "frame-ancestors 'none'"
    ].join("; ")
  );

  if (IS_PRODUCTION) {
    res.setHeader(
      "Strict-Transport-Security",
      "max-age=31536000; includeSubDomains"
    );
  }

  next();
});

app.use(express.urlencoded({
  extended: false,
  limit: "20kb"
}));

app.use("/public", express.static(path.join(__dirname, "public"), {
  etag: true,
  maxAge: IS_PRODUCTION ? "1d" : 0
}));

/*
 * Carrega uma eventual sessão a partir do cookie.
 * O cookie contém o token original, mas o banco guarda apenas seu SHA-256.
 */
app.use((req, res, next) => {
  req.user = null;
  req.sessionData = null;

  const cookies = parseCookies(req.headers.cookie);
  const token = cookies[SESSION_COOKIE_NAME];

  if (!token || !/^[A-Za-z0-9_-]{40,100}$/.test(token)) {
    next();
    return;
  }

  const tokenHash = hashToken(token);
  const now = Date.now();

  const session = db.prepare(`
    SELECT
      s.token_hash,
      s.csrf_token,
      s.expires_at,
      u.id AS user_id,
      u.username,
      u.display_name
    FROM sessions s
    INNER JOIN users u ON u.id = s.user_id
    WHERE s.token_hash = ?
  `).get(tokenHash);

  if (!session) {
    next();
    return;
  }

  if (session.expires_at <= now) {
    db.prepare("DELETE FROM sessions WHERE token_hash = ?").run(tokenHash);
    clearSessionCookie(res);
    next();
    return;
  }

  req.user = {
    id: session.user_id,
    username: session.username,
    displayName: session.display_name
  };

  req.sessionData = {
    tokenHash: session.token_hash,
    csrfToken: session.csrf_token,
    expiresAt: session.expires_at
  };

  next();
});

/*
 * Remove periodicamente sessões expiradas. Como o sistema é pequeno,
 * uma limpeza por intervalo é suficiente e evita dependências adicionais.
 */
deleteExpiredSessions();

const sessionCleanupTimer = setInterval(
  deleteExpiredSessions,
  30 * 60 * 1000
);

sessionCleanupTimer.unref();

const loginAttempts = new Map();
const LOGIN_WINDOW_MS = 15 * 60 * 1000;
const MAX_LOGIN_ATTEMPTS = 10;

const loginCleanupTimer = setInterval(() => {
  const now = Date.now();

  for (const [key, value] of loginAttempts.entries()) {
    if (now - value.windowStartedAt >= LOGIN_WINDOW_MS) {
      loginAttempts.delete(key);
    }
  }
}, LOGIN_WINDOW_MS);

loginCleanupTimer.unref();

/* Listagem pública. */
app.get("/", (req, res) => {
  const users = db.prepare(`
    SELECT
      id,
      username,
      display_name,
      created_at
    FROM users
    ORDER BY display_name COLLATE NOCASE, username COLLATE NOCASE
  `).all();

  const rows = users.length > 0
    ? users.map((user) => `
        <tr>
          <td>${escapeHtml(user.display_name)}</td>
          <td><code>${escapeHtml(user.username)}</code></td>
          <td>${escapeHtml(formatDate(user.created_at))}</td>
        </tr>
      `).join("")
    : `
        <tr>
          <td colspan="3" class="empty-state">
            Nenhum usuário cadastrado.
          </td>
        </tr>
      `;

  const content = `
    <section class="page-header">
      <div>
        <h1>Usuários cadastrados</h1>
        <p>A listagem é pública. Alterações exigem autenticação.</p>
      </div>
      ${
        req.user
          ? `<a class="button" href="/admin">Gerenciar usuários</a>`
          : `<a class="button" href="/login">Entrar</a>`
      }
    </section>

    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Nome</th>
            <th>Usuário</th>
            <th>Cadastrado em</th>
          </tr>
        </thead>
        <tbody>
          ${rows}
        </tbody>
      </table>
    </div>
  `;

  res.send(renderPage({
    title: "Usuários",
    content,
    user: req.user
  }));
});

app.get("/login", (req, res) => {
  if (req.user) {
    res.redirect("/admin");
    return;
  }

  res.send(renderLoginPage());
});

app.post("/login", async (req, res) => {
  if (req.user) {
    res.redirect("/admin");
    return;
  }

  const rateLimitKey = req.ip || req.socket.remoteAddress || "unknown";
  const rateLimitResult = registerLoginAttempt(rateLimitKey);

  if (!rateLimitResult.allowed) {
    res.status(429).send(renderLoginPage(
      "Muitas tentativas de login. Aguarde alguns minutos e tente novamente."
    ));
    return;
  }

  const username = normalizeUsername(req.body.username);
  const password = typeof req.body.password === "string"
    ? req.body.password
    : "";

  if (!username || !password) {
    res.status(400).send(renderLoginPage(
      "Informe o usuário e a senha.",
      username
    ));
    return;
  }

  const user = db.prepare(`
    SELECT
      id,
      username,
      display_name,
      password_hash,
      password_salt
    FROM users
    WHERE username = ?
  `).get(username);

  /*
   * Executar uma verificação mesmo quando o usuário não existe reduz
   * diferenças grosseiras de tempo que poderiam facilitar enumeração.
   */
  let passwordIsValid = false;

  if (user) {
    passwordIsValid = await verifyPassword(
      password,
      user.password_hash,
      user.password_salt
    );
  } else {
    await performDummyPasswordVerification(password);
  }

  if (!user || !passwordIsValid) {
    res.status(401).send(renderLoginPage(
      "Usuário ou senha inválidos.",
      username
    ));
    return;
  }

  loginAttempts.delete(rateLimitKey);

  const token = generateToken();
  const tokenHash = hashToken(token);
  const csrfToken = generateToken();
  const now = Date.now();
  const expiresAt = now + SESSION_DURATION_MS;

  db.prepare(`
    INSERT INTO sessions (
      token_hash,
      user_id,
      csrf_token,
      expires_at,
      created_at
    )
    VALUES (?, ?, ?, ?, ?)
  `).run(
    tokenHash,
    user.id,
    csrfToken,
    expiresAt,
    now
  );

  setSessionCookie(res, token);
  res.redirect("/admin?ok=login");
});

app.get("/admin", requireAuthentication, (req, res) => {
  const users = db.prepare(`
    SELECT
      id,
      username,
      display_name,
      created_at,
      updated_at
    FROM users
    ORDER BY display_name COLLATE NOCASE, username COLLATE NOCASE
  `).all();

  const successMessage = getSuccessMessage(req.query.ok);

  const rows = users.map((user) => {
    const isCurrentUser = user.id === req.user.id;

    return `
      <tr>
        <td>
          ${escapeHtml(user.display_name)}
          ${isCurrentUser ? '<span class="badge">Você</span>' : ""}
        </td>
        <td><code>${escapeHtml(user.username)}</code></td>
        <td>${escapeHtml(formatDate(user.updated_at))}</td>
        <td class="actions">
          <a class="button button-secondary button-small"
             href="/users/${user.id}/edit">
            Editar
          </a>

          ${
            isCurrentUser
              ? `
                <button
                  class="button button-danger button-small"
                  type="button"
                  disabled
                  title="Você não pode remover sua própria conta">
                  Remover
                </button>
              `
              : `
                <form
                  method="post"
                  action="/users/${user.id}/delete"
                  class="inline-form">
                  ${csrfInput(req)}
                  <button class="button button-danger button-small"
                          type="submit">
                    Remover
                  </button>
                </form>
              `
          }
        </td>
      </tr>
    `;
  }).join("");

  const content = `
    <section class="page-header">
      <div>
        <h1>Gerenciar usuários</h1>
        <p>Cadastre, edite ou remova contas do sistema.</p>
      </div>
      <a class="button" href="/users/new">Novo usuário</a>
    </section>

    ${successMessage ? renderAlert("success", successMessage) : ""}

    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Nome</th>
            <th>Usuário</th>
            <th>Última alteração</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          ${rows || `
            <tr>
              <td colspan="4" class="empty-state">
                Nenhum usuário cadastrado.
              </td>
            </tr>
          `}
        </tbody>
      </table>
    </div>
  `;

  res.send(renderPage({
    title: "Gerenciar usuários",
    content,
    user: req.user,
    csrfToken: req.sessionData.csrfToken
  }));
});

app.get("/users/new", requireAuthentication, (req, res) => {
  res.send(renderUserForm({
    title: "Novo usuário",
    action: "/users",
    submitLabel: "Cadastrar",
    user: req.user,
    csrfToken: req.sessionData.csrfToken,
    values: {}
  }));
});

app.post(
  "/users",
  requireAuthentication,
  requireCsrf,
  async (req, res) => {
    const username = normalizeUsername(req.body.username);
    const displayName = normalizeDisplayName(req.body.displayName);
    const password = typeof req.body.password === "string"
      ? req.body.password
      : "";

    const error =
      validateUsername(username) ||
      validateDisplayName(displayName) ||
      validatePassword(password);

    if (error) {
      res.status(400).send(renderUserForm({
        title: "Novo usuário",
        action: "/users",
        submitLabel: "Cadastrar",
        user: req.user,
        csrfToken: req.sessionData.csrfToken,
        error,
        values: {
          username,
          displayName
        }
      }));
      return;
    }

    const existing = db
      .prepare("SELECT id FROM users WHERE username = ?")
      .get(username);

    if (existing) {
      res.status(409).send(renderUserForm({
        title: "Novo usuário",
        action: "/users",
        submitLabel: "Cadastrar",
        user: req.user,
        csrfToken: req.sessionData.csrfToken,
        error: "Esse nome de usuário já está em uso.",
        values: {
          username,
          displayName
        }
      }));
      return;
    }

    const { hash, salt } = await hashPassword(password);
    const now = Date.now();

    try {
      db.prepare(`
        INSERT INTO users (
          username,
          display_name,
          password_hash,
          password_salt,
          created_at,
          updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
      `).run(
        username,
        displayName,
        hash,
        salt,
        now,
        now
      );
    } catch (error) {
      if (isUniqueConstraintError(error)) {
        res.status(409).send(renderUserForm({
          title: "Novo usuário",
          action: "/users",
          submitLabel: "Cadastrar",
          user: req.user,
          csrfToken: req.sessionData.csrfToken,
          error: "Esse nome de usuário já está em uso.",
          values: {
            username,
            displayName
          }
        }));
        return;
      }

      throw error;
    }

    res.redirect("/admin?ok=created");
  }
);

app.get("/users/:id/edit", requireAuthentication, (req, res) => {
  const id = parsePositiveInteger(req.params.id);

  if (!id) {
    res.status(404).send(renderNotFoundPage(req.user));
    return;
  }

  const editedUser = db.prepare(`
    SELECT id, username, display_name
    FROM users
    WHERE id = ?
  `).get(id);

  if (!editedUser) {
    res.status(404).send(renderNotFoundPage(req.user));
    return;
  }

  res.send(renderUserForm({
    title: "Editar usuário",
    action: `/users/${editedUser.id}/edit`,
    submitLabel: "Salvar alterações",
    user: req.user,
    csrfToken: req.sessionData.csrfToken,
    editing: true,
    values: {
      username: editedUser.username,
      displayName: editedUser.display_name
    }
  }));
});

app.post(
  "/users/:id/edit",
  requireAuthentication,
  requireCsrf,
  async (req, res) => {
    const id = parsePositiveInteger(req.params.id);

    if (!id) {
      res.status(404).send(renderNotFoundPage(req.user));
      return;
    }

    const existingUser = db.prepare(`
      SELECT id, username, display_name
      FROM users
      WHERE id = ?
    `).get(id);

    if (!existingUser) {
      res.status(404).send(renderNotFoundPage(req.user));
      return;
    }

    const username = normalizeUsername(req.body.username);
    const displayName = normalizeDisplayName(req.body.displayName);
    const password = typeof req.body.password === "string"
      ? req.body.password
      : "";

    const error =
      validateUsername(username) ||
      validateDisplayName(displayName) ||
      validatePassword(password, false);

    if (error) {
      res.status(400).send(renderUserForm({
        title: "Editar usuário",
        action: `/users/${id}/edit`,
        submitLabel: "Salvar alterações",
        user: req.user,
        csrfToken: req.sessionData.csrfToken,
        editing: true,
        error,
        values: {
          username,
          displayName
        }
      }));
      return;
    }

    const conflictingUser = db.prepare(`
      SELECT id
      FROM users
      WHERE username = ? AND id <> ?
    `).get(username, id);

    if (conflictingUser) {
      res.status(409).send(renderUserForm({
        title: "Editar usuário",
        action: `/users/${id}/edit`,
        submitLabel: "Salvar alterações",
        user: req.user,
        csrfToken: req.sessionData.csrfToken,
        editing: true,
        error: "Esse nome de usuário já está em uso.",
        values: {
          username,
          displayName
        }
      }));
      return;
    }

    const now = Date.now();

    try {
      if (password) {
        const { hash, salt } = await hashPassword(password);

        db.prepare(`
          UPDATE users
          SET
            username = ?,
            display_name = ?,
            password_hash = ?,
            password_salt = ?,
            updated_at = ?
          WHERE id = ?
        `).run(
          username,
          displayName,
          hash,
          salt,
          now,
          id
        );
      } else {
        db.prepare(`
          UPDATE users
          SET
            username = ?,
            display_name = ?,
            updated_at = ?
          WHERE id = ?
        `).run(
          username,
          displayName,
          now,
          id
        );
      }
    } catch (error) {
      if (isUniqueConstraintError(error)) {
        res.status(409).send(renderUserForm({
          title: "Editar usuário",
          action: `/users/${id}/edit`,
          submitLabel: "Salvar alterações",
          user: req.user,
          csrfToken: req.sessionData.csrfToken,
          editing: true,
          error: "Esse nome de usuário já está em uso.",
          values: {
            username,
            displayName
          }
        }));
        return;
      }

      throw error;
    }

    res.redirect("/admin?ok=updated");
  }
);

app.post(
  "/users/:id/delete",
  requireAuthentication,
  requireCsrf,
  (req, res) => {
    const id = parsePositiveInteger(req.params.id);

    if (!id) {
      res.status(404).send(renderNotFoundPage(req.user));
      return;
    }

    /*
     * Impedir a remoção da própria conta evita que o usuário encerre
     * acidentalmente sua sessão e deixe o sistema sem acesso imediato.
     */
    if (id === req.user.id) {
      res.status(400).send(renderErrorPage(
        "Operação não permitida",
        "Você não pode remover sua própria conta enquanto está autenticado.",
        req.user
      ));
      return;
    }

    const result = db
      .prepare("DELETE FROM users WHERE id = ?")
      .run(id);

    if (result.changes === 0) {
      res.status(404).send(renderNotFoundPage(req.user));
      return;
    }

    res.redirect("/admin?ok=deleted");
  }
);

app.post(
  "/logout",
  requireAuthentication,
  requireCsrf,
  (req, res) => {
    db.prepare(`
      DELETE FROM sessions
      WHERE token_hash = ?
    `).run(req.sessionData.tokenHash);

    clearSessionCookie(res);
    res.redirect("/");
  }
);

app.use((req, res) => {
  res.status(404).send(renderNotFoundPage(req.user));
});

app.use((error, req, res, next) => {
  console.error(error);

  if (res.headersSent) {
    next(error);
    return;
  }

  res.status(500).send(renderErrorPage(
    "Erro interno",
    "Não foi possível concluir a operação. Tente novamente.",
    req.user
  ));
});

const server = app.listen(PORT, HOST, () => {
  console.log(`Servidor disponível em http://${HOST}:${PORT}`);
  console.log(`Banco SQLite: ${databasePath}`);
});

function shutdown(signal) {
  console.log(`\nRecebido ${signal}. Encerrando...`);

  server.close(() => {
    clearInterval(sessionCleanupTimer);
    clearInterval(loginCleanupTimer);

    try {
      db.close();
    } finally {
      process.exit(0);
    }
  });

  setTimeout(() => {
    process.exit(1);
  }, 10_000).unref();
}

process.on("SIGINT", () => shutdown("SIGINT"));
process.on("SIGTERM", () => shutdown("SIGTERM"));

function requireAuthentication(req, res, next) {
  if (!req.user || !req.sessionData) {
    res.redirect("/login");
    return;
  }

  next();
}

function requireCsrf(req, res, next) {
  const submittedToken = typeof req.body.csrfToken === "string"
    ? req.body.csrfToken
    : "";

  if (!safeStringEqual(
    submittedToken,
    req.sessionData && req.sessionData.csrfToken
  )) {
    res.status(403).send(renderErrorPage(
      "Requisição rejeitada",
      "O token de segurança é inválido ou expirou. Atualize a página e tente novamente.",
      req.user
    ));
    return;
  }

  next();
}

function deleteExpiredSessions() {
  db.prepare(`
    DELETE FROM sessions
    WHERE expires_at <= ?
  `).run(Date.now());
}

function setSessionCookie(res, token) {
  res.cookie(SESSION_COOKIE_NAME, token, {
    httpOnly: true,
    secure: IS_PRODUCTION,
    sameSite: "strict",
    path: "/",
    maxAge: SESSION_DURATION_MS
  });
}

function clearSessionCookie(res) {
  res.clearCookie(SESSION_COOKIE_NAME, {
    httpOnly: true,
    secure: IS_PRODUCTION,
    sameSite: "strict",
    path: "/"
  });
}

function parseCookies(header) {
  const cookies = {};

  if (!header) {
    return cookies;
  }

  for (const part of header.split(";")) {
    const separatorIndex = part.indexOf("=");

    if (separatorIndex < 0) {
      continue;
    }

    const key = part.slice(0, separatorIndex).trim();
    const rawValue = part.slice(separatorIndex + 1).trim();

    try {
      cookies[key] = decodeURIComponent(rawValue);
    } catch {
      // Cookies malformados são ignorados.
    }
  }

  return cookies;
}

function registerLoginAttempt(key) {
  const now = Date.now();
  const current = loginAttempts.get(key);

  if (!current || now - current.windowStartedAt >= LOGIN_WINDOW_MS) {
    loginAttempts.set(key, {
      count: 1,
      windowStartedAt: now
    });

    return { allowed: true };
  }

  if (current.count >= MAX_LOGIN_ATTEMPTS) {
    return { allowed: false };
  }

  current.count += 1;
  return { allowed: true };
}

let dummyCredentialsPromise = null;

async function performDummyPasswordVerification(password) {
  /*
   * Credenciais artificiais usadas somente para manter o custo computacional
   * do login semelhante quando o nome de usuário não existe.
   */
  if (!dummyCredentialsPromise) {
    dummyCredentialsPromise = hashPassword(
      "dummy-password-never-used-for-login"
    );
  }

  const dummyCredentials = await dummyCredentialsPromise;

  await verifyPassword(
    password,
    dummyCredentials.hash,
    dummyCredentials.salt
  );
}

function normalizeUsername(value) {
  return typeof value === "string"
    ? value.trim()
    : "";
}

function normalizeDisplayName(value) {
  return typeof value === "string"
    ? value.trim()
    : "";
}

function parsePositiveInteger(value) {
  if (!/^\d+$/.test(String(value))) {
    return null;
  }

  const parsed = Number(value);

  if (!Number.isSafeInteger(parsed) || parsed <= 0) {
    return null;
  }

  return parsed;
}

function parsePort(value, fallback) {
  const parsed = Number(value);

  if (!Number.isInteger(parsed) || parsed < 1 || parsed > 65535) {
    return fallback;
  }

  return parsed;
}

function isUniqueConstraintError(error) {
  return Boolean(
    error &&
    typeof error.code === "string" &&
    error.code.startsWith("SQLITE_CONSTRAINT")
  );
}

function formatDate(timestamp) {
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short"
  }).format(new Date(timestamp));
}

function getSuccessMessage(code) {
  const messages = {
    login: "Login realizado com sucesso.",
    created: "Usuário cadastrado com sucesso.",
    updated: "Usuário atualizado com sucesso.",
    deleted: "Usuário removido com sucesso."
  };

  return messages[code] || "";
}

function csrfInput(req) {
  return `
    <input
      type="hidden"
      name="csrfToken"
      value="${escapeHtml(req.sessionData.csrfToken)}">
  `;
}

function renderLoginPage(error = "", username = "") {
  const content = `
    <div class="auth-container">
      <form method="post" action="/login" class="card form-card">
        <h1>Entrar</h1>
        <p>Informe suas credenciais para gerenciar os usuários.</p>

        ${error ? renderAlert("error", error) : ""}

        <label for="username">Usuário</label>
        <input
          id="username"
          name="username"
          type="text"
          minlength="3"
          maxlength="32"
          autocomplete="username"
          value="${escapeHtml(username)}"
          required
          autofocus>

        <label for="password">Senha</label>
        <input
          id="password"
          name="password"
          type="password"
          maxlength="128"
          autocomplete="current-password"
          required>

        <button class="button button-full" type="submit">
          Entrar
        </button>
      </form>
    </div>
  `;

  return renderPage({
    title: "Entrar",
    content,
    user: null
  });
}

function renderUserForm(options) {
  const {
    title,
    action,
    submitLabel,
    user,
    csrfToken,
    editing = false,
    error = "",
    values = {}
  } = options;

  const content = `
    <div class="form-page">
      <form method="post"
            action="${escapeHtml(action)}"
            class="card form-card">

        <h1>${escapeHtml(title)}</h1>

        ${error ? renderAlert("error", error) : ""}

        <input
          type="hidden"
          name="csrfToken"
          value="${escapeHtml(csrfToken)}">

        <label for="displayName">Nome de exibição</label>
        <input
          id="displayName"
          name="displayName"
          type="text"
          minlength="1"
          maxlength="80"
          autocomplete="name"
          value="${escapeHtml(values.displayName || "")}"
          required
          autofocus>

        <label for="username">Usuário</label>
        <input
          id="username"
          name="username"
          type="text"
          minlength="3"
          maxlength="32"
          pattern="[A-Za-z0-9._-]{3,32}"
          autocomplete="username"
          value="${escapeHtml(values.username || "")}"
          required>

        <label for="password">
          ${editing ? "Nova senha" : "Senha"}
        </label>
        <input
          id="password"
          name="password"
          type="password"
          minlength="10"
          maxlength="128"
          autocomplete="new-password"
          ${editing ? "" : "required"}>

        <p class="field-help">
          ${
            editing
              ? "Deixe em branco para manter a senha atual."
              : "Use pelo menos 10 caracteres."
          }
        </p>

        <div class="form-actions">
          <a class="button button-secondary" href="/admin">
            Cancelar
          </a>
          <button class="button" type="submit">
            ${escapeHtml(submitLabel)}
          </button>
        </div>
      </form>
    </div>
  `;

  return renderPage({
    title,
    content,
    user,
    csrfToken
  });
}

function renderNotFoundPage(user) {
  return renderErrorPage(
    "Página não encontrada",
    "O recurso solicitado não existe.",
    user
  );
}

function renderErrorPage(title, message, user) {
  const content = `
    <div class="card message-card">
      <h1>${escapeHtml(title)}</h1>
      <p>${escapeHtml(message)}</p>
      <a class="button" href="${user ? "/admin" : "/"}">
        Voltar
      </a>
    </div>
  `;

  return renderPage({
    title,
    content,
    user
  });
}

function renderAlert(type, message) {
  return `
    <div class="alert alert-${escapeHtml(type)}" role="alert">
      ${escapeHtml(message)}
    </div>
  `;
}

function renderPage({ title, content, user, csrfToken = "" }) {
  const authenticationNavigation = user
    ? `
      <span class="current-user">
        ${escapeHtml(user.displayName)}
        (<code>${escapeHtml(user.username)}</code>)
      </span>

      <a href="/admin">Administração</a>

      <form method="post" action="/logout" class="inline-form">
        <input
          type="hidden"
          name="csrfToken"
          value="${escapeHtml(csrfToken)}">
        <button class="link-button" type="submit">Sair</button>
      </form>
    `
    : `<a href="/login">Entrar</a>`;

  return `<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${escapeHtml(title)} - Cadastro de Usuários</title>
  <link rel="stylesheet" href="/public/styles.css">
</head>
<body>
  <header class="site-header">
    <nav class="navigation" aria-label="Navegação principal">
      <a class="brand" href="/">Cadastro de Usuários</a>

      <div class="navigation-links">
        <a href="/">Listagem pública</a>
        ${authenticationNavigation}
      </div>
    </nav>
  </header>

  <main class="container">
    ${content}
  </main>

  <footer class="site-footer">
    <p>Sistema de cadastro com Node.js e SQLite.</p>
  </footer>
</body>
</html>`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
```

---

### `public/styles.css`

```css
:root {
  color-scheme: light;
  --background: #f4f6f8;
  --surface: #ffffff;
  --text: #1f2937;
  --muted: #667085;
  --border: #d0d5dd;
  --primary: #155eef;
  --primary-hover: #004eeb;
  --danger: #d92d20;
  --danger-hover: #b42318;
  --success-background: #ecfdf3;
  --success-border: #abefc6;
  --success-text: #067647;
  --error-background: #fef3f2;
  --error-border: #fecdca;
  --error-text: #b42318;
  --shadow: 0 1px 3px rgb(16 24 40 / 10%);
}

* {
  box-sizing: border-box;
}

html {
  min-height: 100%;
}

body {
  min-height: 100vh;
  margin: 0;
  background: var(--background);
  color: var(--text);
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

a {
  color: var(--primary);
}

code {
  font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
}

.site-header {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
}

.navigation {
  width: min(1120px, calc(100% - 32px));
  min-height: 64px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.brand {
  color: var(--text);
  font-size: 1.1rem;
  font-weight: 700;
  text-decoration: none;
}

.navigation-links {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 18px;
}

.navigation-links a,
.link-button {
  color: var(--text);
  font: inherit;
  text-decoration: none;
}

.navigation-links a:hover,
.link-button:hover {
  color: var(--primary);
  text-decoration: underline;
}

.current-user {
  color: var(--muted);
  font-size: 0.9rem;
}

.container {
  width: min(1120px, calc(100% - 32px));
  min-height: calc(100vh - 145px);
  margin: 0 auto;
  padding: 40px 0;
}

.page-header {
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.page-header h1,
.card h1 {
  margin: 0 0 8px;
  line-height: 1.2;
}

.page-header p,
.card p {
  margin-top: 0;
  color: var(--muted);
}

.table-container {
  overflow-x: auto;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  box-shadow: var(--shadow);
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 14px 16px;
  text-align: left;
  vertical-align: middle;
  border-bottom: 1px solid var(--border);
}

th {
  background: #f9fafb;
  color: #344054;
  font-size: 0.88rem;
}

tr:last-child td {
  border-bottom: 0;
}

.actions {
  width: 1%;
  white-space: nowrap;
}

.empty-state {
  padding: 36px 16px;
  color: var(--muted);
  text-align: center;
}

.button {
  display: inline-flex;
  min-height: 40px;
  padding: 8px 16px;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--primary);
  border-radius: 7px;
  background: var(--primary);
  color: #ffffff;
  cursor: pointer;
  font: inherit;
  font-weight: 600;
  line-height: 1.2;
  text-decoration: none;
}

.button:hover {
  border-color: var(--primary-hover);
  background: var(--primary-hover);
}

.button:disabled {
  border-color: #d0d5dd;
  background: #eaecf0;
  color: #98a2b3;
  cursor: not-allowed;
}

.button-secondary {
  border-color: var(--border);
  background: var(--surface);
  color: var(--text);
}

.button-secondary:hover {
  border-color: #98a2b3;
  background: #f9fafb;
}

.button-danger {
  border-color: var(--danger);
  background: var(--danger);
}

.button-danger:hover {
  border-color: var(--danger-hover);
  background: var(--danger-hover);
}

.button-small {
  min-height: 34px;
  padding: 6px 11px;
  font-size: 0.875rem;
}

.button-full {
  width: 100%;
  margin-top: 10px;
}

.inline-form {
  display: inline;
  margin: 0;
}

.link-button {
  padding: 0;
  border: 0;
  background: transparent;
  cursor: pointer;
}

.auth-container,
.form-page {
  display: flex;
  justify-content: center;
}

.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  box-shadow: var(--shadow);
}

.form-card {
  width: min(100%, 480px);
  padding: 28px;
}

.form-card label {
  display: block;
  margin: 18px 0 7px;
  color: #344054;
  font-weight: 600;
}

.form-card input {
  width: 100%;
  min-height: 42px;
  padding: 9px 11px;
  border: 1px solid var(--border);
  border-radius: 7px;
  background: #ffffff;
  color: var(--text);
  font: inherit;
}

.form-card input:focus {
  border-color: var(--primary);
  outline: 3px solid rgb(21 94 239 / 14%);
}

.field-help {
  margin: 6px 0 0 !important;
  font-size: 0.875rem;
}

.form-actions {
  margin-top: 26px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.message-card {
  width: min(100%, 620px);
  margin: 40px auto;
  padding: 28px;
  text-align: center;
}

.alert {
  margin: 18px 0;
  padding: 12px 14px;
  border: 1px solid;
  border-radius: 7px;
}

.alert-success {
  border-color: var(--success-border);
  background: var(--success-background);
  color: var(--success-text);
}

.alert-error {
  border-color: var(--error-border);
  background: var(--error-background);
  color: var(--error-text);
}

.badge {
  display: inline-block;
  margin-left: 6px;
  padding: 2px 7px;
  border-radius: 999px;
  background: #eff4ff;
  color: #3538cd;
  font-size: 0.75rem;
  font-weight: 700;
}

.site-footer {
  min-height: 80px;
  padding: 20px;
  border-top: 1px solid var(--border);
  color: var(--muted);
  text-align: center;
}

.site-footer p {
  margin: 0;
}

@media (max-width: 760px) {
  .navigation {
    padding: 14px 0;
    align-items: flex-start;
    flex-direction: column;
  }

  .navigation-links {
    width: 100%;
    align-items: flex-start;
    flex-wrap: wrap;
    justify-content: flex-start;
  }

  .current-user {
    width: 100%;
  }

  .page-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .actions {
    white-space: normal;
  }

  .actions .button,
  .actions .inline-form {
    margin: 2px 0;
  }
}
```

---

### `data/.gitkeep`

Arquivo vazio.

```text

```

---

### `.gitignore`

```gitignore
node_modules/
data/*.db
data/*.db-shm
data/*.db-wal
.env
npm-debug.log*
.DS_Store
```

---

### `README.md`

```markdown
# Cadastro de Usuários

Sistema web em Node.js para cadastro e autenticação de usuários, com
persistência em SQLite.

## Funcionalidades

- Listagem pública de usuários.
- Login com usuário e senha.
- Cadastro de usuários somente para pessoas autenticadas.
- Edição de usuários somente para pessoas autenticadas.
- Remoção de usuários somente para pessoas autenticadas.
- Senhas protegidas por `scrypt` com salt aleatório.
- Sessões persistidas no SQLite.
- Cookie de autenticação `HttpOnly` e `SameSite=Strict`.
- Hash SHA-256 do token de sessão armazenado no banco.
- Proteção CSRF.
- Rate limiting básico no login.
- Queries SQL parametrizadas.
- Escape de conteúdo HTML.
- Cabeçalhos básicos de segurança.

## Requisitos

- Node.js 20 ou superior.
- npm.

Verifique a instalação:

```bash
node --version
npm --version
```

## Instalação

Na pasta do projeto:

```bash
npm install
```

## Criar o primeiro usuário

Como apenas usuários autenticados podem cadastrar outros usuários, é
necessário criar a primeira conta pelo terminal.

Forma recomendada, usando variável de ambiente para que a senha não fique no
histórico do shell:

```bash
ADMIN_PASSWORD='SenhaMuitoSegura123!' \
npm run create-admin -- admin "Administrador"
```

Também é possível informar a senha como argumento:

```bash
npm run create-admin -- admin 'SenhaMuitoSegura123!' "Administrador"
```

O nome de usuário deve:

- Ter entre 3 e 32 caracteres.
- Usar somente letras, números, ponto, hífen ou sublinhado.

A senha deve ter pelo menos 10 caracteres.

## Executar

```bash
npm start
```

Acesse:

```text
http://127.0.0.1:3000
```

## Desenvolvimento

Para reiniciar automaticamente quando os arquivos forem alterados:

```bash
npm run dev
```

## Configuração

### Porta

```bash
PORT=8080 npm start
```

### Endereço de escuta

Por padrão, o servidor escuta somente em `127.0.0.1`.

Para aceitar conexões externas:

```bash
HOST=0.0.0.0 npm start
```

### Caminho do banco

Por padrão, o banco é criado em:

```text
data/app.db
```

Para alterar:

```bash
DATABASE_FILE=/caminho/para/app.db npm start
```

Use a mesma variável ao criar o primeiro usuário:

```bash
DATABASE_FILE=/caminho/para/app.db \
ADMIN_PASSWORD='SenhaMuitoSegura123!' \
npm run create-admin -- admin "Administrador"
```

## Produção

Em produção:

```bash
NODE_ENV=production HOST=0.0.0.0 PORT=3000 npm start
```

Quando `NODE_ENV=production`, o cookie de sessão recebe a opção `Secure`.
Portanto, o sistema deve ser servido por HTTPS, normalmente atrás de um
proxy reverso como Nginx, Caddy ou um balanceador de carga.

Exemplo:

```bash
NODE_ENV=production \
HOST=0.0.0.0 \
PORT=3000 \
DATABASE_FILE=/var/lib/cadastro-usuarios/app.db \
npm start
```

Garanta que o diretório do banco tenha permissões adequadas para o usuário do
processo Node.js.

## Decisões adotadas

- Todos os usuários autenticados podem cadastrar, editar e remover outros
  usuários.
- A própria conta autenticada não pode ser removida pela interface.
- Não há perfis separados de administrador e usuário comum, pois isso não foi
  exigido.
- A sessão expira oito horas após o login.
- A listagem pública mostra nome, usuário e data de cadastro, mas nunca mostra
  hash, salt ou informações da sessão.
- O rate limiting do login é mantido em memória e é adequado para uma única
  instância pequena. Em múltiplas instâncias, deve ser substituído por um
  armazenamento compartilhado.
```

## Execução rápida

Depois de criar os arquivos:

```bash
npm install
```

Crie o primeiro usuário:

```bash
ADMIN_PASSWORD='SenhaMuitoSegura123!' \
npm run create-admin -- admin "Administrador"
```

Inicie o servidor:

```bash
npm start
```

Abra:

```text
http://127.0.0.1:3000
```