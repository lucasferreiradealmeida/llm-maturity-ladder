<!--
nivel: 4 - Seguranca (autenticacao e autorizacao)
provider: gpt
model: gpt-5.6
tentativa: 2
temperature: 0.2
timestamp: 2026-08-18T21:53:43.730Z
metadata: {"model":"gpt-5.6-sol","usage":{"prompt_tokens":210,"completion_tokens":13323,"total_tokens":13533,"prompt_tokens_details":{"cached_tokens":0,"cache_write_tokens":0,"audio_tokens":0},"completion_tokens_details":{"reasoning_tokens":1536,"audio_tokens":0,"accepted_prediction_tokens":0,"rejected_prediction_tokens":0}},"finish_reason":"stop"}
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

Abaixo está um projeto completo em Node.js com:

- Cadastro, edição e remoção de usuários somente para autenticados.
- Listagem pública.
- Senhas protegidas com `scrypt`, salt individual e comparação segura.
- Sessões persistidas no SQLite, usando token aleatório armazenado no banco apenas como hash.
- Cookie `HttpOnly`, `SameSite=Strict` e `Secure` em produção.
- Proteção CSRF para operações autenticadas.
- Controle básico contra tentativas repetidas de login.
- Interface web sem framework frontend.
- Usuário administrador inicial criado por variáveis de ambiente.

## Estrutura

```text
cadastro-usuarios/
├── package.json
├── server.js
├── .env.example
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
  "name": "cadastro-usuarios-seguro",
  "version": "1.0.0",
  "private": true,
  "description": "Sistema web de cadastro de usuários com autenticação e SQLite",
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
    "better-sqlite3": "^11.8.1",
    "express": "^4.21.2"
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
.env
npm-debug.log*
.DS_Store
```

---

### `.env.example`

```dotenv
# Este arquivo é apenas uma referência.
# O projeto não usa dotenv para evitar uma dependência adicional.
# Defina estas variáveis diretamente no ambiente antes de iniciar.

PORT=3000
HOST=127.0.0.1
NODE_ENV=development

# Local opcional do banco de dados.
DB_PATH=./data/app.db

# Duração da sessão em segundos. Padrão: 28800 (8 horas).
SESSION_TTL_SECONDS=28800

# Necessários apenas na primeira execução, quando ainda não existem usuários.
ADMIN_USERNAME=admin
ADMIN_PASSWORD=troque-por-uma-senha-forte
ADMIN_DISPLAY_NAME=Administrador
```

---

### `server.js`

```javascript
'use strict';

const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const { promisify } = require('util');

const scryptAsync = promisify(crypto.scrypt);

const PORT = parsePositiveInteger(process.env.PORT, 3000);
const HOST = process.env.HOST || '127.0.0.1';
const IS_PRODUCTION = process.env.NODE_ENV === 'production';
const SESSION_TTL_SECONDS = parsePositiveInteger(
  process.env.SESSION_TTL_SECONDS,
  8 * 60 * 60
);
const SESSION_TTL_MS = SESSION_TTL_SECONDS * 1000;

const DB_PATH = path.resolve(
  process.env.DB_PATH || path.join(__dirname, 'data', 'app.db')
);
const PUBLIC_DIRECTORY = path.join(__dirname, 'public');

const COOKIE_NAME = 'session_token';
const MAX_LOGIN_ATTEMPTS = 5;
const LOGIN_WINDOW_MS = 15 * 60 * 1000;

const PASSWORD_MIN_LENGTH = 10;
const PASSWORD_MAX_LENGTH = 128;
const USERNAME_REGEX = /^[A-Za-z0-9_.-]{3,32}$/;

// Parâmetros explícitos do scrypt.
// Cada senha possui um salt criptograficamente aleatório próprio.
const SCRYPT_OPTIONS = {
  N: 32768,
  r: 8,
  p: 1,
  maxmem: 64 * 1024 * 1024
};
const SCRYPT_KEY_LENGTH = 64;

fs.mkdirSync(path.dirname(DB_PATH), { recursive: true });

const db = new Database(DB_PATH);
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');
db.pragma('busy_timeout = 5000');

createSchema();

const app = express();
const loginAttempts = new Map();

app.disable('x-powered-by');

app.use((req, res, next) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('Referrer-Policy', 'no-referrer');
  res.setHeader(
    'Permissions-Policy',
    'camera=(), microphone=(), geolocation=()'
  );
  res.setHeader(
    'Content-Security-Policy',
    [
      "default-src 'self'",
      "base-uri 'self'",
      "form-action 'self'",
      "frame-ancestors 'none'",
      "object-src 'none'",
      "script-src 'self'",
      "style-src 'self'",
      "connect-src 'self'",
      "img-src 'self' data:"
    ].join('; ')
  );

  if (IS_PRODUCTION) {
    res.setHeader(
      'Strict-Transport-Security',
      'max-age=31536000; includeSubDomains'
    );
  }

  next();
});

app.use(express.json({ limit: '20kb', strict: true }));

// Respostas da API não devem ser armazenadas por navegadores ou proxies.
app.use('/api', (req, res, next) => {
  res.setHeader('Cache-Control', 'no-store');
  next();
});

/**
 * Lista pública de usuários.
 * Nunca são retornados hash, salt ou informações de sessão.
 */
app.get('/api/users', (req, res) => {
  const users = db
    .prepare(`
      SELECT
        id,
        username,
        display_name AS displayName,
        created_at AS createdAt,
        updated_at AS updatedAt
      FROM users
      ORDER BY username COLLATE NOCASE ASC
    `)
    .all();

  res.json({ users });
});

/**
 * Retorna a sessão atual.
 */
app.get('/api/auth/me', requireAuthentication, (req, res) => {
  res.json({
    authenticated: true,
    user: publicUser(req.auth.user),
    csrfToken: req.auth.csrfToken,
    expiresAt: new Date(req.auth.expiresAt).toISOString()
  });
});

/**
 * Login.
 *
 * O token entregue ao navegador não é salvo diretamente no banco.
 * Apenas SHA-256(token) é persistido.
 */
app.post('/api/auth/login', asyncRoute(async (req, res) => {
  const clientKey = getLoginClientKey(req);

  if (isLoginBlocked(clientKey)) {
    return res.status(429).json({
      error: 'Muitas tentativas de login. Tente novamente mais tarde.'
    });
  }

  const username =
    typeof req.body?.username === 'string' ? req.body.username.trim() : '';
  const password =
    typeof req.body?.password === 'string' ? req.body.password : '';

  if (!username || !password || password.length > PASSWORD_MAX_LENGTH) {
    registerFailedLogin(clientKey);
    return res.status(401).json({
      error: 'Usuário ou senha inválidos.'
    });
  }

  const user = db
    .prepare(`
      SELECT
        id,
        username,
        display_name,
        password_hash,
        password_salt,
        created_at,
        updated_at
      FROM users
      WHERE username = ? COLLATE NOCASE
    `)
    .get(username);

  let validPassword = false;

  if (user) {
    validPassword = await verifyPassword(
      password,
      user.password_hash,
      user.password_salt
    );
  } else {
    // Executa scrypt mesmo quando o usuário não existe, reduzindo diferenças
    // de tempo que poderiam facilitar a enumeração de nomes de usuário.
    await derivePasswordHash(
      password,
      '00000000000000000000000000000000'
    );
  }

  if (!user || !validPassword) {
    registerFailedLogin(clientKey);
    return res.status(401).json({
      error: 'Usuário ou senha inválidos.'
    });
  }

  loginAttempts.delete(clientKey);
  deleteExpiredSessions();

  const sessionToken = randomToken(32);
  const sessionTokenHash = hashSessionToken(sessionToken);
  const csrfToken = randomToken(32);
  const now = Date.now();
  const expiresAt = now + SESSION_TTL_MS;

  db.prepare(`
    INSERT INTO sessions (
      token_hash,
      user_id,
      csrf_token,
      created_at,
      expires_at
    )
    VALUES (?, ?, ?, ?, ?)
  `).run(
    sessionTokenHash,
    user.id,
    csrfToken,
    new Date(now).toISOString(),
    expiresAt
  );

  setSessionCookie(res, sessionToken);

  res.json({
    authenticated: true,
    user: publicUser(user),
    csrfToken,
    expiresAt: new Date(expiresAt).toISOString()
  });
}));

app.post(
  '/api/auth/logout',
  requireAuthentication,
  requireCsrf,
  (req, res) => {
    db.prepare('DELETE FROM sessions WHERE token_hash = ?').run(
      req.auth.tokenHash
    );

    clearSessionCookie(res);
    res.status(204).end();
  }
);

/**
 * Criação de usuário.
 *
 * Há uma única exceção à regra "somente autenticados podem cadastrar":
 * o primeiro usuário é criado no início da aplicação por variáveis de
 * ambiente. Isso resolve o problema de inicialização sem expor uma rota
 * pública de cadastro.
 */
app.post(
  '/api/users',
  requireAuthentication,
  requireCsrf,
  asyncRoute(async (req, res) => {
    const validation = validateUserInput(req.body, { passwordRequired: true });

    if (!validation.ok) {
      return res.status(400).json({ error: validation.error });
    }

    const { username, displayName, password } = validation.value;
    const passwordData = await hashPassword(password);
    const now = new Date().toISOString();

    try {
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
        passwordData.hash,
        passwordData.salt,
        now,
        now
      );

      const createdUser = getUserById(result.lastInsertRowid);

      res.status(201).json({
        user: publicUser(createdUser)
      });
    } catch (error) {
      if (isUniqueConstraintError(error)) {
        return res.status(409).json({
          error: 'Já existe um usuário com esse nome.'
        });
      }

      throw error;
    }
  })
);

app.put(
  '/api/users/:id',
  requireAuthentication,
  requireCsrf,
  asyncRoute(async (req, res) => {
    const userId = parseId(req.params.id);

    if (!userId) {
      return res.status(400).json({ error: 'Identificador inválido.' });
    }

    const existingUser = getUserById(userId);

    if (!existingUser) {
      return res.status(404).json({ error: 'Usuário não encontrado.' });
    }

    const validation = validateUserInput(req.body, {
      passwordRequired: false
    });

    if (!validation.ok) {
      return res.status(400).json({ error: validation.error });
    }

    const { username, displayName, password } = validation.value;
    const now = new Date().toISOString();

    let passwordData = null;

    if (password) {
      passwordData = await hashPassword(password);
    }

    try {
      if (passwordData) {
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
          passwordData.hash,
          passwordData.salt,
          now,
          userId
        );
      } else {
        db.prepare(`
          UPDATE users
          SET
            username = ?,
            display_name = ?,
            updated_at = ?
          WHERE id = ?
        `).run(username, displayName, now, userId);
      }

      const updatedUser = getUserById(userId);

      res.json({
        user: publicUser(updatedUser)
      });
    } catch (error) {
      if (isUniqueConstraintError(error)) {
        return res.status(409).json({
          error: 'Já existe um usuário com esse nome.'
        });
      }

      throw error;
    }
  })
);

app.delete(
  '/api/users/:id',
  requireAuthentication,
  requireCsrf,
  (req, res) => {
    const userId = parseId(req.params.id);

    if (!userId) {
      return res.status(400).json({ error: 'Identificador inválido.' });
    }

    const result = deleteUserTransaction(userId);

    if (result === 'not-found') {
      return res.status(404).json({ error: 'Usuário não encontrado.' });
    }

    // Impede que o sistema fique sem qualquer conta capaz de autenticar.
    if (result === 'last-user') {
      return res.status(409).json({
        error: 'Não é possível remover o último usuário do sistema.'
      });
    }

    const deletedCurrentUser = req.auth.user.id === userId;

    if (deletedCurrentUser) {
      // As sessões já foram apagadas automaticamente por ON DELETE CASCADE.
      clearSessionCookie(res);
    }

    res.json({
      deleted: true,
      loggedOut: deletedCurrentUser
    });
  }
);

app.use('/api', (req, res) => {
  res.status(404).json({ error: 'Rota da API não encontrada.' });
});

app.use(
  express.static(PUBLIC_DIRECTORY, {
    index: 'index.html',
    etag: true,
    maxAge: IS_PRODUCTION ? '1h' : 0
  })
);

app.use((error, req, res, next) => {
  console.error(error);

  if (res.headersSent) {
    return next(error);
  }

  if (error instanceof SyntaxError && error.status === 400 && 'body' in error) {
    return res.status(400).json({ error: 'JSON inválido.' });
  }

  res.status(500).json({
    error: 'Erro interno do servidor.'
  });
});

async function start() {
  await createInitialAdministratorIfNecessary();

  deleteExpiredSessions();

  const cleanupTimer = setInterval(deleteExpiredSessions, 60 * 60 * 1000);
  cleanupTimer.unref();

  const server = app.listen(PORT, HOST, () => {
    console.log(`Servidor disponível em http://${HOST}:${PORT}`);
    console.log(`Banco SQLite: ${DB_PATH}`);

    if (IS_PRODUCTION) {
      console.log(
        'Modo de produção ativo: o cookie de sessão exige conexão HTTPS.'
      );
    }
  });

  function shutdown(signal) {
    console.log(`\nRecebido ${signal}. Encerrando...`);

    server.close(() => {
      db.close();
      process.exit(0);
    });

    setTimeout(() => process.exit(1), 10_000).unref();
  }

  process.on('SIGINT', () => shutdown('SIGINT'));
  process.on('SIGTERM', () => shutdown('SIGTERM'));
}

function createSchema() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT NOT NULL COLLATE NOCASE UNIQUE,
      display_name TEXT NOT NULL,
      password_hash TEXT NOT NULL,
      password_salt TEXT NOT NULL,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS sessions (
      token_hash TEXT PRIMARY KEY,
      user_id INTEGER NOT NULL,
      csrf_token TEXT NOT NULL,
      created_at TEXT NOT NULL,
      expires_at INTEGER NOT NULL,
      FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_sessions_user_id
      ON sessions(user_id);

    CREATE INDEX IF NOT EXISTS idx_sessions_expires_at
      ON sessions(expires_at);
  `);
}

async function createInitialAdministratorIfNecessary() {
  const row = db.prepare('SELECT COUNT(*) AS total FROM users').get();

  if (row.total > 0) {
    return;
  }

  const username = (process.env.ADMIN_USERNAME || '').trim();
  const displayName = (
    process.env.ADMIN_DISPLAY_NAME ||
    username ||
    'Administrador'
  ).trim();
  const password = process.env.ADMIN_PASSWORD || '';

  const validation = validateUserInput(
    { username, displayName, password },
    { passwordRequired: true }
  );

  if (!validation.ok) {
    console.error('');
    console.error('O banco ainda não possui usuários.');
    console.error(
      'Defina ADMIN_USERNAME, ADMIN_PASSWORD e, opcionalmente, ADMIN_DISPLAY_NAME.'
    );
    console.error(`Motivo: ${validation.error}`);
    console.error('');
    process.exit(1);
  }

  const passwordData = await hashPassword(validation.value.password);
  const now = new Date().toISOString();

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
    validation.value.username,
    validation.value.displayName,
    passwordData.hash,
    passwordData.salt,
    now,
    now
  );

  console.log(
    `Usuário inicial "${validation.value.username}" criado com sucesso.`
  );
}

function requireAuthentication(req, res, next) {
  const cookies = parseCookies(req.headers.cookie || '');
  const rawToken = cookies[COOKIE_NAME];

  if (!rawToken) {
    return res.status(401).json({
      error: 'Autenticação necessária.'
    });
  }

  const tokenHash = hashSessionToken(rawToken);

  const session = db.prepare(`
    SELECT
      s.token_hash,
      s.csrf_token,
      s.expires_at,
      u.id,
      u.username,
      u.display_name,
      u.created_at,
      u.updated_at
    FROM sessions s
    INNER JOIN users u ON u.id = s.user_id
    WHERE s.token_hash = ?
  `).get(tokenHash);

  if (!session) {
    clearSessionCookie(res);
    return res.status(401).json({
      error: 'Sessão inválida ou encerrada.'
    });
  }

  if (session.expires_at <= Date.now()) {
    db.prepare('DELETE FROM sessions WHERE token_hash = ?').run(tokenHash);
    clearSessionCookie(res);

    return res.status(401).json({
      error: 'Sessão expirada.'
    });
  }

  req.auth = {
    tokenHash,
    csrfToken: session.csrf_token,
    expiresAt: session.expires_at,
    user: {
      id: session.id,
      username: session.username,
      display_name: session.display_name,
      created_at: session.created_at,
      updated_at: session.updated_at
    }
  };

  next();
}

function requireCsrf(req, res, next) {
  const receivedToken = req.get('X-CSRF-Token') || '';

  if (!safeStringEqual(receivedToken, req.auth.csrfToken)) {
    return res.status(403).json({
      error: 'Token CSRF ausente ou inválido.'
    });
  }

  next();
}

function validateUserInput(body, options) {
  const username =
    typeof body?.username === 'string' ? body.username.trim() : '';
  const displayName =
    typeof body?.displayName === 'string' ? body.displayName.trim() : '';
  const password = typeof body?.password === 'string' ? body.password : '';

  if (!USERNAME_REGEX.test(username)) {
    return {
      ok: false,
      error:
        'O usuário deve ter entre 3 e 32 caracteres e usar apenas letras, números, ponto, hífen ou sublinhado.'
    };
  }

  if (displayName.length < 1 || displayName.length > 80) {
    return {
      ok: false,
      error: 'O nome de exibição deve ter entre 1 e 80 caracteres.'
    };
  }

  if (options.passwordRequired && !password) {
    return {
      ok: false,
      error: 'A senha é obrigatória.'
    };
  }

  if (
    password &&
    (password.length < PASSWORD_MIN_LENGTH ||
      password.length > PASSWORD_MAX_LENGTH)
  ) {
    return {
      ok: false,
      error: `A senha deve ter entre ${PASSWORD_MIN_LENGTH} e ${PASSWORD_MAX_LENGTH} caracteres.`
    };
  }

  return {
    ok: true,
    value: {
      username,
      displayName,
      password
    }
  };
}

async function hashPassword(password) {
  const salt = crypto.randomBytes(16).toString('hex');
  const hash = await derivePasswordHash(password, salt);

  return { salt, hash };
}

async function derivePasswordHash(password, salt) {
  const result = await scryptAsync(
    password,
    salt,
    SCRYPT_KEY_LENGTH,
    SCRYPT_OPTIONS
  );

  return result.toString('hex');
}

async function verifyPassword(password, storedHash, storedSalt) {
  const calculatedHash = await derivePasswordHash(password, storedSalt);

  const calculatedBuffer = Buffer.from(calculatedHash, 'hex');
  const storedBuffer = Buffer.from(storedHash, 'hex');

  if (calculatedBuffer.length !== storedBuffer.length) {
    return false;
  }

  return crypto.timingSafeEqual(calculatedBuffer, storedBuffer);
}

function hashSessionToken(token) {
  return crypto.createHash('sha256').update(token).digest('hex');
}

function randomToken(size) {
  return crypto.randomBytes(size).toString('base64url');
}

function safeStringEqual(first, second) {
  const firstBuffer = Buffer.from(String(first));
  const secondBuffer = Buffer.from(String(second));

  if (firstBuffer.length !== secondBuffer.length) {
    return false;
  }

  return crypto.timingSafeEqual(firstBuffer, secondBuffer);
}

function getUserById(id) {
  return db.prepare(`
    SELECT
      id,
      username,
      display_name,
      created_at,
      updated_at
    FROM users
    WHERE id = ?
  `).get(id);
}

function publicUser(user) {
  return {
    id: user.id,
    username: user.username,
    displayName: user.display_name,
    createdAt: user.created_at,
    updatedAt: user.updated_at
  };
}

function parseId(value) {
  const parsed = Number(value);

  if (!Number.isSafeInteger(parsed) || parsed <= 0) {
    return null;
  }

  return parsed;
}

const deleteUserTransaction = db.transaction((userId) => {
  const user = db.prepare('SELECT id FROM users WHERE id = ?').get(userId);

  if (!user) {
    return 'not-found';
  }

  const count = db.prepare('SELECT COUNT(*) AS total FROM users').get();

  if (count.total <= 1) {
    return 'last-user';
  }

  db.prepare('DELETE FROM users WHERE id = ?').run(userId);
  return 'deleted';
});

function setSessionCookie(res, token) {
  res.cookie(COOKIE_NAME, token, {
    httpOnly: true,
    sameSite: 'strict',
    secure: IS_PRODUCTION,
    path: '/',
    maxAge: SESSION_TTL_MS
  });
}

function clearSessionCookie(res) {
  res.clearCookie(COOKIE_NAME, {
    httpOnly: true,
    sameSite: 'strict',
    secure: IS_PRODUCTION,
    path: '/'
  });
}

function parseCookies(cookieHeader) {
  const cookies = {};

  for (const entry of cookieHeader.split(';')) {
    const separatorIndex = entry.indexOf('=');

    if (separatorIndex < 0) {
      continue;
    }

    const key = entry.slice(0, separatorIndex).trim();
    const value = entry.slice(separatorIndex + 1).trim();

    if (!key) {
      continue;
    }

    try {
      cookies[key] = decodeURIComponent(value);
    } catch {
      cookies[key] = value;
    }
  }

  return cookies;
}

function deleteExpiredSessions() {
  db.prepare('DELETE FROM sessions WHERE expires_at <= ?').run(Date.now());
}

function isUniqueConstraintError(error) {
  return (
    error &&
    typeof error.code === 'string' &&
    error.code.startsWith('SQLITE_CONSTRAINT_UNIQUE')
  );
}

function getLoginClientKey(req) {
  return `${req.ip}|${String(req.body?.username || '')
    .trim()
    .toLowerCase()}`;
}

function isLoginBlocked(key) {
  pruneLoginAttempts();

  const record = loginAttempts.get(key);

  if (!record) {
    return false;
  }

  return (
    record.count >= MAX_LOGIN_ATTEMPTS &&
    Date.now() - record.firstAttemptAt < LOGIN_WINDOW_MS
  );
}

function registerFailedLogin(key) {
  const now = Date.now();
  const record = loginAttempts.get(key);

  if (!record || now - record.firstAttemptAt >= LOGIN_WINDOW_MS) {
    loginAttempts.set(key, {
      count: 1,
      firstAttemptAt: now
    });
    return;
  }

  record.count += 1;
}

function pruneLoginAttempts() {
  const now = Date.now();

  for (const [key, record] of loginAttempts.entries()) {
    if (now - record.firstAttemptAt >= LOGIN_WINDOW_MS) {
      loginAttempts.delete(key);
    }
  }
}

function parsePositiveInteger(value, fallback) {
  const parsed = Number(value);

  if (!Number.isSafeInteger(parsed) || parsed <= 0) {
    return fallback;
  }

  return parsed;
}

function asyncRoute(handler) {
  return function wrappedAsyncRoute(req, res, next) {
    Promise.resolve(handler(req, res, next)).catch(next);
  };
}

start().catch((error) => {
  console.error('Não foi possível iniciar a aplicação:', error);
  db.close();
  process.exit(1);
});
```

---

### `public/index.html`

```html
<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="utf-8">
    <meta
      name="viewport"
      content="width=device-width, initial-scale=1"
    >
    <meta
      name="description"
      content="Sistema seguro de cadastro de usuários"
    >
    <title>Cadastro de usuários</title>
    <link rel="stylesheet" href="/styles.css">
    <script src="/app.js" defer></script>
  </head>

  <body>
    <header class="page-header">
      <div class="container header-content">
        <div>
          <h1>Cadastro de usuários</h1>
          <p>Listagem pública e gerenciamento autenticado.</p>
        </div>

        <div id="session-summary" class="session-summary" aria-live="polite">
          Não autenticado
        </div>
      </div>
    </header>

    <main class="container main-grid">
      <section class="card" aria-labelledby="authentication-title">
        <h2 id="authentication-title">Autenticação</h2>

        <form id="login-form">
          <div class="form-field">
            <label for="login-username">Usuário</label>
            <input
              id="login-username"
              name="username"
              type="text"
              autocomplete="username"
              required
            >
          </div>

          <div class="form-field">
            <label for="login-password">Senha</label>
            <input
              id="login-password"
              name="password"
              type="password"
              autocomplete="current-password"
              required
            >
          </div>

          <button type="submit">Entrar</button>
        </form>

        <div id="authenticated-panel" hidden>
          <p>
            Autenticado como
            <strong id="authenticated-user"></strong>.
          </p>

          <button id="logout-button" type="button" class="secondary">
            Sair
          </button>
        </div>
      </section>

      <section
        id="management-card"
        class="card"
        aria-labelledby="management-title"
        hidden
      >
        <h2 id="management-title">Cadastrar usuário</h2>

        <form id="user-form">
          <input id="editing-id" type="hidden">

          <div class="form-field">
            <label for="user-username">Usuário</label>
            <input
              id="user-username"
              type="text"
              minlength="3"
              maxlength="32"
              pattern="[A-Za-z0-9_.-]{3,32}"
              autocomplete="off"
              required
            >
            <small>
              Use de 3 a 32 letras, números, pontos, hífens ou sublinhados.
            </small>
          </div>

          <div class="form-field">
            <label for="display-name">Nome de exibição</label>
            <input
              id="display-name"
              type="text"
              maxlength="80"
              autocomplete="name"
              required
            >
          </div>

          <div class="form-field">
            <label for="user-password">Senha</label>
            <input
              id="user-password"
              type="password"
              minlength="10"
              maxlength="128"
              autocomplete="new-password"
            >
            <small id="password-help">
              Obrigatória no cadastro, com no mínimo 10 caracteres.
            </small>
          </div>

          <div class="button-row">
            <button id="save-user-button" type="submit">
              Cadastrar
            </button>

            <button
              id="cancel-edit-button"
              type="button"
              class="secondary"
              hidden
            >
              Cancelar edição
            </button>
          </div>
        </form>
      </section>

      <section class="card users-card" aria-labelledby="users-title">
        <div class="section-heading">
          <div>
            <h2 id="users-title">Usuários</h2>
            <p>A consulta desta lista é pública.</p>
          </div>

          <button id="reload-button" type="button" class="secondary">
            Atualizar
          </button>
        </div>

        <div class="table-wrapper">
          <table>
            <thead>
              <tr>
                <th scope="col">Usuário</th>
                <th scope="col">Nome</th>
                <th scope="col">Criado em</th>
                <th scope="col" id="actions-heading" hidden>Ações</th>
              </tr>
            </thead>
            <tbody id="users-table-body"></tbody>
          </table>
        </div>

        <p id="empty-users-message" hidden>
          Nenhum usuário cadastrado.
        </p>
      </section>
    </main>

    <div
      id="message"
      class="message"
      role="status"
      aria-live="polite"
      hidden
    ></div>

    <noscript>
      <p class="noscript-message">
        Esta aplicação precisa de JavaScript habilitado.
      </p>
    </noscript>
  </body>
</html>
```

---

### `public/styles.css`

```css
:root {
  color-scheme: light;
  font-family:
    Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
    "Segoe UI", sans-serif;
  line-height: 1.5;
  color: #172033;
  background: #f3f5f9;
  --primary: #2457d6;
  --primary-dark: #1942aa;
  --danger: #b42318;
  --danger-dark: #861e17;
  --border: #d8deea;
  --muted: #5c667a;
  --card: #ffffff;
}

* {
  box-sizing: border-box;
}

body {
  min-width: 320px;
  margin: 0;
}

button,
input {
  font: inherit;
}

button {
  min-height: 42px;
  padding: 0.65rem 1rem;
  border: 0;
  border-radius: 0.45rem;
  color: #fff;
  background: var(--primary);
  font-weight: 700;
  cursor: pointer;
}

button:hover {
  background: var(--primary-dark);
}

button:focus-visible,
input:focus-visible {
  outline: 3px solid rgba(36, 87, 214, 0.3);
  outline-offset: 2px;
}

button:disabled {
  cursor: wait;
  opacity: 0.65;
}

button.secondary {
  color: #25304a;
  background: #e8ecf4;
}

button.secondary:hover {
  background: #d9dfeb;
}

button.danger {
  background: var(--danger);
}

button.danger:hover {
  background: var(--danger-dark);
}

.container {
  width: min(1120px, calc(100% - 2rem));
  margin-inline: auto;
}

.page-header {
  padding: 1.5rem 0;
  color: #fff;
  background: #172b57;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.page-header h1 {
  margin: 0;
  font-size: clamp(1.55rem, 4vw, 2.2rem);
}

.page-header p {
  margin: 0.35rem 0 0;
  color: #dce5fb;
}

.session-summary {
  padding: 0.55rem 0.8rem;
  border: 1px solid rgba(255, 255, 255, 0.35);
  border-radius: 999px;
  white-space: nowrap;
}

.main-grid {
  display: grid;
  grid-template-columns: minmax(260px, 0.75fr) minmax(320px, 1.25fr);
  gap: 1rem;
  padding-block: 1.5rem 5rem;
}

.card {
  padding: 1.25rem;
  border: 1px solid var(--border);
  border-radius: 0.75rem;
  background: var(--card);
  box-shadow: 0 5px 20px rgba(30, 47, 83, 0.06);
}

.card h2 {
  margin-top: 0;
}

.users-card {
  grid-column: 1 / -1;
}

.form-field {
  margin-bottom: 1rem;
}

.form-field label {
  display: block;
  margin-bottom: 0.35rem;
  font-weight: 700;
}

.form-field input {
  width: 100%;
  min-height: 42px;
  padding: 0.65rem 0.75rem;
  border: 1px solid #adb7c9;
  border-radius: 0.45rem;
  color: #172033;
  background: #fff;
}

.form-field small {
  display: block;
  margin-top: 0.3rem;
  color: var(--muted);
}

.button-row,
.section-heading {
  display: flex;
  align-items: center;
  gap: 0.7rem;
}

.section-heading {
  justify-content: space-between;
  margin-bottom: 1rem;
}

.section-heading h2,
.section-heading p {
  margin: 0;
}

.section-heading p {
  color: var(--muted);
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
  padding: 0.8rem;
  border-bottom: 1px solid var(--border);
  text-align: left;
  vertical-align: middle;
}

th {
  color: #34405a;
  background: #f6f8fb;
}

.actions {
  display: flex;
  gap: 0.5rem;
  white-space: nowrap;
}

.actions button {
  min-height: 36px;
  padding: 0.45rem 0.7rem;
}

.message {
  position: fixed;
  right: 1rem;
  bottom: 1rem;
  max-width: min(420px, calc(100% - 2rem));
  padding: 0.9rem 1rem;
  border-radius: 0.55rem;
  color: #fff;
  background: #1d6b3d;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
}

.message.error {
  background: var(--danger);
}

.noscript-message {
  margin: 1rem;
  padding: 1rem;
  color: #fff;
  background: var(--danger);
}

[hidden] {
  display: none !important;
}

@media (max-width: 760px) {
  .header-content,
  .section-heading {
    align-items: flex-start;
    flex-direction: column;
  }

  .main-grid {
    grid-template-columns: 1fr;
  }

  .users-card {
    grid-column: auto;
  }

  .session-summary {
    white-space: normal;
  }

  th,
  td {
    padding: 0.65rem 0.5rem;
  }
}
```

---

### `public/app.js`

```javascript
'use strict';

const state = {
  currentUser: null,
  csrfToken: null,
  users: []
};

const elements = {
  loginForm: document.querySelector('#login-form'),
  loginUsername: document.querySelector('#login-username'),
  loginPassword: document.querySelector('#login-password'),
  authenticatedPanel: document.querySelector('#authenticated-panel'),
  authenticatedUser: document.querySelector('#authenticated-user'),
  logoutButton: document.querySelector('#logout-button'),
  sessionSummary: document.querySelector('#session-summary'),

  managementCard: document.querySelector('#management-card'),
  userForm: document.querySelector('#user-form'),
  managementTitle: document.querySelector('#management-title'),
  editingId: document.querySelector('#editing-id'),
  userUsername: document.querySelector('#user-username'),
  displayName: document.querySelector('#display-name'),
  userPassword: document.querySelector('#user-password'),
  passwordHelp: document.querySelector('#password-help'),
  saveUserButton: document.querySelector('#save-user-button'),
  cancelEditButton: document.querySelector('#cancel-edit-button'),

  usersTableBody: document.querySelector('#users-table-body'),
  emptyUsersMessage: document.querySelector('#empty-users-message'),
  actionsHeading: document.querySelector('#actions-heading'),
  reloadButton: document.querySelector('#reload-button'),
  message: document.querySelector('#message')
};

let messageTimer = null;

elements.loginForm.addEventListener('submit', handleLogin);
elements.logoutButton.addEventListener('click', handleLogout);
elements.userForm.addEventListener('submit', handleSaveUser);
elements.cancelEditButton.addEventListener('click', resetUserForm);
elements.reloadButton.addEventListener('click', loadUsers);

initialize();

async function initialize() {
  await Promise.all([loadSession(), loadUsers()]);
}

async function loadSession() {
  try {
    const response = await fetch('/api/auth/me', {
      headers: {
        Accept: 'application/json'
      }
    });

    if (response.status === 401) {
      setAuthenticatedState(null);
      return;
    }

    const data = await readResponse(response);
    setAuthenticatedState(data);
  } catch (error) {
    setAuthenticatedState(null);
    showMessage(error.message, true);
  }
}

async function loadUsers() {
  setButtonBusy(elements.reloadButton, true);

  try {
    const response = await fetch('/api/users', {
      headers: {
        Accept: 'application/json'
      }
    });
    const data = await readResponse(response);

    state.users = data.users;
    renderUsers();
  } catch (error) {
    showMessage(error.message, true);
  } finally {
    setButtonBusy(elements.reloadButton, false);
  }
}

async function handleLogin(event) {
  event.preventDefault();

  const submitButton = elements.loginForm.querySelector(
    'button[type="submit"]'
  );
  setButtonBusy(submitButton, true);

  try {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json'
      },
      body: JSON.stringify({
        username: elements.loginUsername.value,
        password: elements.loginPassword.value
      })
    });

    const data = await readResponse(response);

    elements.loginForm.reset();
    setAuthenticatedState(data);
    await loadUsers();
    showMessage('Login realizado com sucesso.');
  } catch (error) {
    showMessage(error.message, true);
  } finally {
    setButtonBusy(submitButton, false);
  }
}

async function handleLogout() {
  setButtonBusy(elements.logoutButton, true);

  try {
    const response = await fetch('/api/auth/logout', {
      method: 'POST',
      headers: authenticatedHeaders()
    });

    await readResponse(response);
    setAuthenticatedState(null);
    resetUserForm();
    renderUsers();
    showMessage('Sessão encerrada.');
  } catch (error) {
    if (error.status === 401) {
      setAuthenticatedState(null);
      renderUsers();
    }

    showMessage(error.message, true);
  } finally {
    setButtonBusy(elements.logoutButton, false);
  }
}

async function handleSaveUser(event) {
  event.preventDefault();

  const editingId = Number(elements.editingId.value) || null;
  const payload = {
    username: elements.userUsername.value,
    displayName: elements.displayName.value,
    password: elements.userPassword.value
  };

  setButtonBusy(elements.saveUserButton, true);

  try {
    const response = await fetch(
      editingId ? `/api/users/${editingId}` : '/api/users',
      {
        method: editingId ? 'PUT' : 'POST',
        headers: {
          ...authenticatedHeaders(),
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      }
    );

    await readResponse(response);

    const editedCurrentUser =
      editingId && state.currentUser?.id === editingId;

    resetUserForm();

    if (editedCurrentUser) {
      await loadSession();
    }

    await loadUsers();

    showMessage(
      editingId
        ? 'Usuário atualizado com sucesso.'
        : 'Usuário cadastrado com sucesso.'
    );
  } catch (error) {
    handlePossibleExpiredSession(error);
    showMessage(error.message, true);
  } finally {
    setButtonBusy(elements.saveUserButton, false);
  }
}

function startEditing(userId) {
  const user = state.users.find((item) => item.id === userId);

  if (!user) {
    return;
  }

  elements.editingId.value = String(user.id);
  elements.userUsername.value = user.username;
  elements.displayName.value = user.displayName;
  elements.userPassword.value = '';
  elements.userPassword.required = false;

  elements.managementTitle.textContent = 'Editar usuário';
  elements.saveUserButton.textContent = 'Salvar alterações';
  elements.cancelEditButton.hidden = false;
  elements.passwordHelp.textContent =
    'Deixe em branco para manter a senha atual.';

  elements.managementCard.scrollIntoView({
    behavior: 'smooth',
    block: 'start'
  });

  elements.userUsername.focus();
}

async function deleteUser(userId) {
  const user = state.users.find((item) => item.id === userId);

  if (!user) {
    return;
  }

  const confirmed = window.confirm(
    `Deseja realmente remover o usuário "${user.username}"?`
  );

  if (!confirmed) {
    return;
  }

  try {
    const response = await fetch(`/api/users/${userId}`, {
      method: 'DELETE',
      headers: authenticatedHeaders()
    });
    const data = await readResponse(response);

    if (data.loggedOut) {
      setAuthenticatedState(null);
      resetUserForm();
    }

    await loadUsers();
    showMessage('Usuário removido com sucesso.');
  } catch (error) {
    handlePossibleExpiredSession(error);
    showMessage(error.message, true);
  }
}

function setAuthenticatedState(sessionData) {
  if (!sessionData) {
    state.currentUser = null;
    state.csrfToken = null;

    elements.loginForm.hidden = false;
    elements.authenticatedPanel.hidden = true;
    elements.managementCard.hidden = true;
    elements.actionsHeading.hidden = true;
    elements.sessionSummary.textContent = 'Não autenticado';

    resetUserForm();
    renderUsers();
    return;
  }

  state.currentUser = sessionData.user;
  state.csrfToken = sessionData.csrfToken;

  elements.loginForm.hidden = true;
  elements.authenticatedPanel.hidden = false;
  elements.managementCard.hidden = false;
  elements.actionsHeading.hidden = false;

  elements.authenticatedUser.textContent =
    `${sessionData.user.displayName} (${sessionData.user.username})`;
  elements.sessionSummary.textContent =
    `Autenticado: ${sessionData.user.username}`;

  renderUsers();
}

function renderUsers() {
  elements.usersTableBody.replaceChildren();
  elements.emptyUsersMessage.hidden = state.users.length !== 0;

  for (const user of state.users) {
    const row = document.createElement('tr');

    row.appendChild(createTextCell(user.username));
    row.appendChild(createTextCell(user.displayName));
    row.appendChild(createTextCell(formatDate(user.createdAt)));

    if (state.currentUser) {
      const actionsCell = document.createElement('td');
      actionsCell.className = 'actions';

      const editButton = document.createElement('button');
      editButton.type = 'button';
      editButton.className = 'secondary';
      editButton.textContent = 'Editar';
      editButton.addEventListener('click', () => startEditing(user.id));

      const deleteButton = document.createElement('button');
      deleteButton.type = 'button';
      deleteButton.className = 'danger';
      deleteButton.textContent = 'Remover';
      deleteButton.addEventListener('click', () => deleteUser(user.id));

      actionsCell.append(editButton, deleteButton);
      row.appendChild(actionsCell);
    }

    elements.usersTableBody.appendChild(row);
  }
}

function resetUserForm() {
  elements.userForm.reset();
  elements.editingId.value = '';
  elements.userPassword.required = true;

  elements.managementTitle.textContent = 'Cadastrar usuário';
  elements.saveUserButton.textContent = 'Cadastrar';
  elements.cancelEditButton.hidden = true;
  elements.passwordHelp.textContent =
    'Obrigatória no cadastro, com no mínimo 10 caracteres.';
}

function createTextCell(value) {
  const cell = document.createElement('td');
  cell.textContent = value;
  return cell;
}

function authenticatedHeaders() {
  const headers = {
    Accept: 'application/json'
  };

  if (state.csrfToken) {
    headers['X-CSRF-Token'] = state.csrfToken;
  }

  return headers;
}

async function readResponse(response) {
  if (response.status === 204) {
    if (!response.ok) {
      throw createHttpError('A operação não pôde ser concluída.', response);
    }

    return null;
  }

  let data = null;

  try {
    data = await response.json();
  } catch {
    if (!response.ok) {
      throw createHttpError('Resposta inválida do servidor.', response);
    }

    return null;
  }

  if (!response.ok) {
    throw createHttpError(
      data?.error || 'A operação não pôde ser concluída.',
      response
    );
  }

  return data;
}

function createHttpError(message, response) {
  const error = new Error(message);
  error.status = response.status;
  return error;
}

function handlePossibleExpiredSession(error) {
  if (error.status === 401) {
    setAuthenticatedState(null);
    renderUsers();
  }
}

function setButtonBusy(button, busy) {
  if (!button) {
    return;
  }

  button.disabled = busy;
  button.setAttribute('aria-busy', String(busy));
}

function showMessage(text, isError = false) {
  window.clearTimeout(messageTimer);

  elements.message.textContent = text;
  elements.message.classList.toggle('error', isError);
  elements.message.hidden = false;

  messageTimer = window.setTimeout(() => {
    elements.message.hidden = true;
  }, 5000);
}

function formatDate(value) {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
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
# Cadastro de usuários seguro

Sistema web em Node.js para cadastro e autenticação de usuários, com
persistência em SQLite.

## Funcionalidades

- Listagem pública de usuários.
- Login com usuário e senha.
- Criação, edição e remoção somente para usuários autenticados.
- Senhas protegidas com:
  - `scrypt`;
  - salt aleatório individual;
  - comparação usando `crypto.timingSafeEqual`.
- Sessões persistidas em SQLite.
- Token de sessão aleatório.
- Apenas o hash SHA-256 do token de sessão é armazenado no banco.
- Cookie `HttpOnly`, `SameSite=Strict` e `Secure` em produção.
- Proteção CSRF nas operações autenticadas.
- Controle básico contra tentativas repetidas de login.
- Remoção automática de sessões expiradas.
- Impede a remoção do último usuário do sistema.
- Interface web sem framework frontend.

## Requisitos

- Node.js 20 ou superior.
- npm.

O pacote `better-sqlite3` normalmente oferece binários pré-compilados para
versões suportadas do Node.js. Em plataformas sem binário disponível, pode
ser necessário ter compilador C/C++ e Python instalados.

## Instalação

Na pasta do projeto:

```bash
npm install
```

## Primeira execução

Como apenas usuários autenticados podem criar outros usuários, a aplicação
precisa criar uma conta inicial quando o banco está vazio.

### Linux ou macOS

```bash
export ADMIN_USERNAME=admin
export ADMIN_PASSWORD='uma-senha-forte-com-10-ou-mais-caracteres'
export ADMIN_DISPLAY_NAME='Administrador'

npm start
```

Também é possível executar em uma única linha:

```bash
ADMIN_USERNAME=admin \
ADMIN_PASSWORD='uma-senha-forte-com-10-ou-mais-caracteres' \
ADMIN_DISPLAY_NAME='Administrador' \
npm start
```

### Windows PowerShell

```powershell
$env:ADMIN_USERNAME="admin"
$env:ADMIN_PASSWORD="uma-senha-forte-com-10-ou-mais-caracteres"
$env:ADMIN_DISPLAY_NAME="Administrador"

npm start
```

Depois, acesse:

```text
http://127.0.0.1:3000
```

As variáveis `ADMIN_USERNAME` e `ADMIN_PASSWORD` são necessárias somente
quando o banco ainda não possui usuários.

## Execuções posteriores

Depois que o primeiro usuário for criado:

```bash
npm start
```

## Modo de desenvolvimento

```bash
npm run dev
```

Esse comando usa o modo `--watch` do Node.js.

## Configurações opcionais

| Variável | Padrão | Descrição |
|---|---:|---|
| `PORT` | `3000` | Porta HTTP |
| `HOST` | `127.0.0.1` | Endereço de escuta |
| `DB_PATH` | `./data/app.db` | Caminho do SQLite |
| `SESSION_TTL_SECONDS` | `28800` | Duração da sessão em segundos |
| `NODE_ENV` | `development` | Use `production` em produção |
| `ADMIN_USERNAME` | - | Usuário inicial |
| `ADMIN_PASSWORD` | - | Senha inicial |
| `ADMIN_DISPLAY_NAME` | `Administrador` | Nome do usuário inicial |

## Exemplo usando banco em outro local

Linux/macOS:

```bash
DB_PATH=/var/lib/cadastro/app.db npm start
```

PowerShell:

```powershell
$env:DB_PATH="C:\dados\cadastro\app.db"
npm start
```

## Produção

Em produção, execute a aplicação atrás de um proxy reverso com HTTPS, como
Nginx, Caddy ou um balanceador de carga.

Exemplo:

```bash
NODE_ENV=production HOST=0.0.0.0 PORT=3000 npm start
```

Quando `NODE_ENV=production`, o cookie de sessão recebe a opção `Secure`.
Consequentemente, o navegador somente enviará o cookie através de HTTPS.

Nunca publique diretamente a aplicação em HTTP com
`NODE_ENV=production`, pois o login poderá ocorrer, mas o cookie seguro não
será enviado nas requisições HTTP seguintes.

## Banco de dados

Por padrão, o banco fica em:

```text
data/app.db
```

As tabelas são criadas automaticamente:

- `users`: usuários e hashes de senha.
- `sessions`: sessões autenticadas.

Os arquivos SQLite não devem ser versionados no Git.

## Regras de validação

### Usuário

- Entre 3 e 32 caracteres.
- Letras, números, ponto, hífen e sublinhado.
- Comparação sem distinção entre maiúsculas e minúsculas.

Por exemplo, `admin` e `ADMIN` são considerados o mesmo usuário.

### Senha

- Entre 10 e 128 caracteres.
- Nunca é retornada pela API.
- Nunca é salva em texto puro.

### Remoção

Um usuário autenticado pode remover outros usuários ou a própria conta.
Ao remover a própria conta, sua sessão é encerrada automaticamente.

O último usuário do sistema não pode ser removido, evitando que a aplicação
fique sem qualquer conta capaz de autenticar.
```

## Execução resumida

```bash
npm install

ADMIN_USERNAME=admin \
ADMIN_PASSWORD='minha-senha-segura-123' \
ADMIN_DISPLAY_NAME='Administrador' \
npm start
```

Abra:

```text
http://127.0.0.1:3000
```