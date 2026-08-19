<!--
nivel: 4 - Seguranca (autenticacao e autorizacao)
provider: gpt
model: gpt-5.6
tentativa: 1
temperature: 0.2
timestamp: 2026-08-18T21:51:29.214Z
metadata: {"model":"gpt-5.6-sol","usage":{"prompt_tokens":210,"completion_tokens":12525,"total_tokens":12735,"prompt_tokens_details":{"cached_tokens":0,"cache_write_tokens":0,"audio_tokens":0},"completion_tokens_details":{"reasoning_tokens":1485,"audio_tokens":0,"accepted_prediction_tokens":0,"rejected_prediction_tokens":0}},"finish_reason":"stop"}
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

Abaixo está uma implementação completa em Node.js, Express e SQLite.

Decisões adotadas:

- Senhas protegidas com `scrypt`, salt aleatório individual e comparação em tempo constante.
- Sessões armazenadas no SQLite.
- O cookie contém somente um token aleatório; no banco é armazenado apenas o hash SHA-256 do token.
- Cookies `HttpOnly`, `SameSite=Lax` e `Secure` em produção.
- Operações de escrita exigem autenticação e token CSRF.
- A listagem de usuários é pública.
- O usuário autenticado não pode excluir a própria conta, evitando a invalidação acidental da sessão.
- O primeiro usuário é criado por um script administrativo local, pois ainda não existe usuário autenticado para cadastrá-lo.

## Estrutura

```text
cadastro-usuarios/
├── package.json
├── .gitignore
├── .env.example
├── README.md
├── public/
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── scripts/
│   └── create-admin.js
└── src/
    ├── db.js
    ├── security.js
    └── server.js
```

---

### `package.json`

```json
{
  "name": "cadastro-usuarios-seguro",
  "version": "1.0.0",
  "private": true,
  "description": "Sistema web de cadastro de usuários com autenticação, sessões e SQLite",
  "main": "src/server.js",
  "scripts": {
    "start": "node src/server.js",
    "dev": "node --watch src/server.js",
    "create-admin": "node scripts/create-admin.js"
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
# Este projeto não carrega automaticamente arquivos .env.
# Estas variáveis devem ser definidas no ambiente do processo.

PORT=3000
HOST=127.0.0.1

# Caminho opcional para o banco.
DB_FILE=./data/app.db

# Use production ao executar atrás de HTTPS.
NODE_ENV=development

# Defina como true quando a aplicação for acessada exclusivamente por HTTPS.
COOKIE_SECURE=false

# Origem pública opcional usada na validação de requisições do navegador.
# Exemplo:
# APP_ORIGIN=https://usuarios.exemplo.com

# Usadas somente pelo script de criação do primeiro usuário:
# ADMIN_USERNAME=admin
# ADMIN_PASSWORD=uma-senha-longa-e-segura
```

---

### `src/db.js`

```javascript
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const Database = require('better-sqlite3');

const defaultDatabasePath = path.join(process.cwd(), 'data', 'app.db');
const databasePath = path.resolve(process.env.DB_FILE || defaultDatabasePath);

fs.mkdirSync(path.dirname(databasePath), { recursive: true });

const db = new Database(databasePath);

db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');
db.pragma('busy_timeout = 5000');

db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL COLLATE NOCASE UNIQUE,
    password_hash TEXT NOT NULL,
    password_salt TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
  );

  CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token_hash TEXT NOT NULL UNIQUE,
    csrf_token TEXT NOT NULL,
    expires_at INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
  );

  CREATE INDEX IF NOT EXISTS idx_sessions_token_hash
    ON sessions(token_hash);

  CREATE INDEX IF NOT EXISTS idx_sessions_expires_at
    ON sessions(expires_at);

  CREATE INDEX IF NOT EXISTS idx_sessions_user_id
    ON sessions(user_id);
`);

module.exports = {
  db,
  databasePath
};
```

---

### `src/security.js`

```javascript
'use strict';

const crypto = require('node:crypto');
const { promisify } = require('node:util');

const scryptAsync = promisify(crypto.scrypt);

const SCRYPT_OPTIONS = Object.freeze({
  N: 16384,
  r: 8,
  p: 1,
  maxmem: 64 * 1024 * 1024
});

const HASH_LENGTH = 64;

function randomToken(bytes = 32) {
  return crypto.randomBytes(bytes).toString('base64url');
}

function hashToken(token) {
  return crypto.createHash('sha256').update(token, 'utf8').digest('hex');
}

async function hashPassword(password) {
  const salt = crypto.randomBytes(16).toString('base64');

  const derivedKey = await scryptAsync(
    password,
    Buffer.from(salt, 'base64'),
    HASH_LENGTH,
    SCRYPT_OPTIONS
  );

  return {
    salt,
    hash: derivedKey.toString('base64')
  };
}

async function verifyPassword(password, storedSalt, storedHash) {
  try {
    const expectedHash = Buffer.from(storedHash, 'base64');

    const actualHash = await scryptAsync(
      password,
      Buffer.from(storedSalt, 'base64'),
      expectedHash.length || HASH_LENGTH,
      SCRYPT_OPTIONS
    );

    if (expectedHash.length !== actualHash.length) {
      return false;
    }

    return crypto.timingSafeEqual(expectedHash, actualHash);
  } catch {
    return false;
  }
}

function safeStringEqual(left, right) {
  if (typeof left !== 'string' || typeof right !== 'string') {
    return false;
  }

  const leftBuffer = Buffer.from(left, 'utf8');
  const rightBuffer = Buffer.from(right, 'utf8');

  if (leftBuffer.length !== rightBuffer.length) {
    return false;
  }

  return crypto.timingSafeEqual(leftBuffer, rightBuffer);
}

function validateUsername(username) {
  if (typeof username !== 'string') {
    return 'O nome de usuário é obrigatório.';
  }

  const normalized = username.trim();

  if (normalized.length < 3 || normalized.length > 50) {
    return 'O nome de usuário deve ter entre 3 e 50 caracteres.';
  }

  if (!/^[A-Za-z0-9._-]+$/.test(normalized)) {
    return 'O nome de usuário só pode conter letras, números, ponto, hífen e sublinhado.';
  }

  return null;
}

function validatePassword(password) {
  if (typeof password !== 'string') {
    return 'A senha é obrigatória.';
  }

  if (password.length < 10) {
    return 'A senha deve ter no mínimo 10 caracteres.';
  }

  if (Buffer.byteLength(password, 'utf8') > 200) {
    return 'A senha é muito longa.';
  }

  return null;
}

module.exports = {
  hashPassword,
  verifyPassword,
  randomToken,
  hashToken,
  safeStringEqual,
  validateUsername,
  validatePassword
};
```

---

### `src/server.js`

```javascript
'use strict';

const path = require('node:path');
const express = require('express');

const { db, databasePath } = require('./db');
const {
  hashPassword,
  verifyPassword,
  randomToken,
  hashToken,
  safeStringEqual,
  validateUsername,
  validatePassword
} = require('./security');

const app = express();

const port = Number.parseInt(process.env.PORT || '3000', 10);
const host = process.env.HOST || '127.0.0.1';
const isProduction = process.env.NODE_ENV === 'production';
const cookieSecure =
  process.env.COOKIE_SECURE === 'true' ||
  (isProduction && process.env.COOKIE_SECURE !== 'false');

const configuredOrigin = process.env.APP_ORIGIN
  ? process.env.APP_ORIGIN.replace(/\/+$/, '')
  : null;

const sessionDurationSeconds = 8 * 60 * 60;
const sessionCookieName = 'session_token';

const publicDirectory = path.join(__dirname, '..', 'public');

/*
 * Limitador simples em memória para tentativas de login.
 * Em uma implantação com múltiplas instâncias, ele deve ser substituído
 * por um armazenamento compartilhado.
 */
const loginAttempts = new Map();
const loginWindowMs = 15 * 60 * 1000;
const maximumLoginAttempts = 10;

app.disable('x-powered-by');

app.use((req, res, next) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('Referrer-Policy', 'no-referrer');
  res.setHeader('Permissions-Policy', 'camera=(), microphone=(), geolocation=()');
  res.setHeader(
    'Content-Security-Policy',
    [
      "default-src 'self'",
      "script-src 'self'",
      "style-src 'self'",
      "img-src 'self' data:",
      "object-src 'none'",
      "base-uri 'self'",
      "frame-ancestors 'none'",
      "form-action 'self'"
    ].join('; ')
  );

  if (cookieSecure) {
    res.setHeader(
      'Strict-Transport-Security',
      'max-age=31536000; includeSubDomains'
    );
  }

  next();
});

app.use(express.json({ limit: '20kb' }));

function parseCookies(cookieHeader) {
  const cookies = {};

  if (!cookieHeader) {
    return cookies;
  }

  for (const part of cookieHeader.split(';')) {
    const separatorIndex = part.indexOf('=');

    if (separatorIndex === -1) {
      continue;
    }

    const name = part.slice(0, separatorIndex).trim();
    const value = part.slice(separatorIndex + 1).trim();

    try {
      cookies[name] = decodeURIComponent(value);
    } catch {
      // Cookies malformados são ignorados.
    }
  }

  return cookies;
}

function setSessionCookie(res, token) {
  res.cookie(sessionCookieName, token, {
    httpOnly: true,
    sameSite: 'lax',
    secure: cookieSecure,
    maxAge: sessionDurationSeconds * 1000,
    path: '/'
  });
}

function clearSessionCookie(res) {
  res.clearCookie(sessionCookieName, {
    httpOnly: true,
    sameSite: 'lax',
    secure: cookieSecure,
    path: '/'
  });
}

function getExpectedOrigin(req) {
  if (configuredOrigin) {
    return configuredOrigin;
  }

  const protocol = cookieSecure ? 'https' : req.protocol;
  return `${protocol}://${req.get('host')}`;
}

/*
 * Rejeita mutações originadas por outro site.
 * Requisições sem Origin continuam permitidas para clientes não navegadores;
 * endpoints autenticados ainda exigem o token CSRF.
 */
app.use('/api', (req, res, next) => {
  if (['GET', 'HEAD', 'OPTIONS'].includes(req.method)) {
    return next();
  }

  const origin = req.get('origin');
  const fetchSite = req.get('sec-fetch-site');

  if (fetchSite === 'cross-site') {
    return res.status(403).json({
      error: 'Requisição entre sites não permitida.'
    });
  }

  if (origin && origin.replace(/\/+$/, '') !== getExpectedOrigin(req)) {
    return res.status(403).json({
      error: 'Origem da requisição não permitida.'
    });
  }

  return next();
});

function loadAuthentication(req, res, next) {
  const cookies = parseCookies(req.headers.cookie);
  const token = cookies[sessionCookieName];

  req.auth = null;

  if (!token) {
    return next();
  }

  const tokenDigest = hashToken(token);
  const currentTime = Math.floor(Date.now() / 1000);

  const session = db.prepare(`
    SELECT
      sessions.id AS session_id,
      sessions.user_id,
      sessions.csrf_token,
      sessions.expires_at,
      users.username
    FROM sessions
    INNER JOIN users ON users.id = sessions.user_id
    WHERE sessions.token_hash = ?
      AND sessions.expires_at > ?
  `).get(tokenDigest, currentTime);

  if (!session) {
    clearSessionCookie(res);
    return next();
  }

  req.auth = {
    sessionId: session.session_id,
    userId: session.user_id,
    username: session.username,
    csrfToken: session.csrf_token,
    expiresAt: session.expires_at,
    rawToken: token
  };

  return next();
}

app.use(loadAuthentication);

function requireAuthentication(req, res, next) {
  if (!req.auth) {
    return res.status(401).json({
      error: 'Autenticação necessária.'
    });
  }

  return next();
}

function requireCsrf(req, res, next) {
  const csrfToken = req.get('x-csrf-token');

  if (!req.auth || !safeStringEqual(csrfToken, req.auth.csrfToken)) {
    return res.status(403).json({
      error: 'Token CSRF inválido ou ausente.'
    });
  }

  return next();
}

function isUniqueConstraintError(error) {
  return (
    error &&
    typeof error.code === 'string' &&
    error.code.startsWith('SQLITE_CONSTRAINT')
  );
}

function getLoginAttemptKey(req, username) {
  return `${req.ip}|${String(username || '').toLowerCase()}`;
}

function isLoginRateLimited(key) {
  const now = Date.now();
  const record = loginAttempts.get(key);

  if (!record) {
    return false;
  }

  if (now - record.startedAt >= loginWindowMs) {
    loginAttempts.delete(key);
    return false;
  }

  return record.count >= maximumLoginAttempts;
}

function registerFailedLogin(key) {
  const now = Date.now();
  const record = loginAttempts.get(key);

  if (!record || now - record.startedAt >= loginWindowMs) {
    loginAttempts.set(key, {
      count: 1,
      startedAt: now
    });
    return;
  }

  record.count += 1;
}

function clearFailedLogins(key) {
  loginAttempts.delete(key);
}

function cleanupExpiredSessions() {
  const now = Math.floor(Date.now() / 1000);
  db.prepare('DELETE FROM sessions WHERE expires_at <= ?').run(now);
}

cleanupExpiredSessions();

const cleanupInterval = setInterval(cleanupExpiredSessions, 30 * 60 * 1000);
cleanupInterval.unref();

app.get('/api/session', (req, res) => {
  res.setHeader('Cache-Control', 'no-store');

  if (!req.auth) {
    return res.json({
      authenticated: false
    });
  }

  return res.json({
    authenticated: true,
    user: {
      id: req.auth.userId,
      username: req.auth.username
    },
    csrfToken: req.auth.csrfToken,
    expiresAt: req.auth.expiresAt
  });
});

app.post('/api/login', async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');

  const username =
    typeof req.body?.username === 'string' ? req.body.username.trim() : '';
  const password =
    typeof req.body?.password === 'string' ? req.body.password : '';

  const attemptKey = getLoginAttemptKey(req, username);

  if (isLoginRateLimited(attemptKey)) {
    return res.status(429).json({
      error: 'Muitas tentativas de login. Aguarde alguns minutos.'
    });
  }

  const user = db.prepare(`
    SELECT id, username, password_hash, password_salt
    FROM users
    WHERE username = ?
  `).get(username);

  /*
   * Mesmo quando o usuário não existe, uma verificação scrypt é executada
   * para reduzir diferenças de tempo que poderiam revelar usuários válidos.
   */
  const passwordValid = user
    ? await verifyPassword(password, user.password_salt, user.password_hash)
    : await verifyPassword(
        password,
        'AAAAAAAAAAAAAAAAAAAAAA==',
        'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=='
      );

  if (!user || !passwordValid) {
    registerFailedLogin(attemptKey);

    return res.status(401).json({
      error: 'Usuário ou senha inválidos.'
    });
  }

  clearFailedLogins(attemptKey);
  cleanupExpiredSessions();

  const rawToken = randomToken(32);
  const csrfToken = randomToken(32);
  const tokenDigest = hashToken(rawToken);
  const expiresAt =
    Math.floor(Date.now() / 1000) + sessionDurationSeconds;

  db.prepare(`
    INSERT INTO sessions (user_id, token_hash, csrf_token, expires_at)
    VALUES (?, ?, ?, ?)
  `).run(user.id, tokenDigest, csrfToken, expiresAt);

  setSessionCookie(res, rawToken);

  return res.json({
    authenticated: true,
    user: {
      id: user.id,
      username: user.username
    },
    csrfToken,
    expiresAt
  });
});

app.post(
  '/api/logout',
  requireAuthentication,
  requireCsrf,
  (req, res) => {
    db.prepare('DELETE FROM sessions WHERE id = ?').run(req.auth.sessionId);
    clearSessionCookie(res);

    return res.json({
      message: 'Sessão encerrada.'
    });
  }
);

app.get('/api/users', (req, res) => {
  const users = db.prepare(`
    SELECT id, username, created_at, updated_at
    FROM users
    ORDER BY username COLLATE NOCASE ASC
  `).all();

  return res.json({ users });
});

app.post(
  '/api/users',
  requireAuthentication,
  requireCsrf,
  async (req, res) => {
    const username =
      typeof req.body?.username === 'string' ? req.body.username.trim() : '';
    const password = req.body?.password;

    const usernameError = validateUsername(username);
    const passwordError = validatePassword(password);

    if (usernameError || passwordError) {
      return res.status(400).json({
        error: usernameError || passwordError
      });
    }

    const passwordData = await hashPassword(password);

    try {
      const result = db.prepare(`
        INSERT INTO users (username, password_hash, password_salt)
        VALUES (?, ?, ?)
      `).run(username, passwordData.hash, passwordData.salt);

      const createdUser = db.prepare(`
        SELECT id, username, created_at, updated_at
        FROM users
        WHERE id = ?
      `).get(result.lastInsertRowid);

      return res.status(201).json({
        message: 'Usuário cadastrado.',
        user: createdUser
      });
    } catch (error) {
      if (isUniqueConstraintError(error)) {
        return res.status(409).json({
          error: 'Já existe um usuário com esse nome.'
        });
      }

      throw error;
    }
  }
);

app.put(
  '/api/users/:id',
  requireAuthentication,
  requireCsrf,
  async (req, res) => {
    const userId = Number.parseInt(req.params.id, 10);

    if (!Number.isSafeInteger(userId) || userId <= 0) {
      return res.status(400).json({
        error: 'Identificador de usuário inválido.'
      });
    }

    const existingUser = db.prepare(`
      SELECT id, username
      FROM users
      WHERE id = ?
    `).get(userId);

    if (!existingUser) {
      return res.status(404).json({
        error: 'Usuário não encontrado.'
      });
    }

    const username =
      typeof req.body?.username === 'string' ? req.body.username.trim() : '';
    const password =
      typeof req.body?.password === 'string' ? req.body.password : undefined;

    const usernameError = validateUsername(username);

    if (usernameError) {
      return res.status(400).json({
        error: usernameError
      });
    }

    const changePassword = password !== undefined && password !== '';

    if (changePassword) {
      const passwordError = validatePassword(password);

      if (passwordError) {
        return res.status(400).json({
          error: passwordError
        });
      }
    }

    const passwordData = changePassword
      ? await hashPassword(password)
      : null;

    const updateUser = db.transaction(() => {
      if (passwordData) {
        db.prepare(`
          UPDATE users
          SET
            username = ?,
            password_hash = ?,
            password_salt = ?,
            updated_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
          WHERE id = ?
        `).run(
          username,
          passwordData.hash,
          passwordData.salt,
          userId
        );

        /*
         * Ao trocar uma senha, sessões anteriores são revogadas.
         * Se o usuário estiver alterando a própria conta, a sessão atual
         * é preservada para não desconectá-lo no meio da operação.
         */
        if (userId === req.auth.userId) {
          db.prepare(`
            DELETE FROM sessions
            WHERE user_id = ? AND id <> ?
          `).run(userId, req.auth.sessionId);
        } else {
          db.prepare(`
            DELETE FROM sessions
            WHERE user_id = ?
          `).run(userId);
        }
      } else {
        db.prepare(`
          UPDATE users
          SET
            username = ?,
            updated_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
          WHERE id = ?
        `).run(username, userId);
      }
    });

    try {
      updateUser();

      const updatedUser = db.prepare(`
        SELECT id, username, created_at, updated_at
        FROM users
        WHERE id = ?
      `).get(userId);

      return res.json({
        message: 'Usuário atualizado.',
        user: updatedUser
      });
    } catch (error) {
      if (isUniqueConstraintError(error)) {
        return res.status(409).json({
          error: 'Já existe um usuário com esse nome.'
        });
      }

      throw error;
    }
  }
);

app.delete(
  '/api/users/:id',
  requireAuthentication,
  requireCsrf,
  (req, res) => {
    const userId = Number.parseInt(req.params.id, 10);

    if (!Number.isSafeInteger(userId) || userId <= 0) {
      return res.status(400).json({
        error: 'Identificador de usuário inválido.'
      });
    }

    if (userId === req.auth.userId) {
      return res.status(400).json({
        error: 'Não é permitido excluir a conta usada na sessão atual.'
      });
    }

    const result = db.prepare(`
      DELETE FROM users
      WHERE id = ?
    `).run(userId);

    if (result.changes === 0) {
      return res.status(404).json({
        error: 'Usuário não encontrado.'
      });
    }

    return res.json({
      message: 'Usuário removido.'
    });
  }
);

app.use('/api', (req, res) => {
  res.status(404).json({
    error: 'Endpoint não encontrado.'
  });
});

app.use(express.static(publicDirectory, {
  index: 'index.html',
  etag: true,
  maxAge: isProduction ? '1h' : 0
}));

app.use((error, req, res, next) => {
  if (res.headersSent) {
    return next(error);
  }

  if (
    error instanceof SyntaxError &&
    error.status === 400 &&
    Object.prototype.hasOwnProperty.call(error, 'body')
  ) {
    return res.status(400).json({
      error: 'JSON inválido.'
    });
  }

  console.error(error);

  return res.status(500).json({
    error: 'Erro interno do servidor.'
  });
});

const server = app.listen(port, host, () => {
  console.log(`Servidor disponível em http://${host}:${port}`);
  console.log(`Banco SQLite: ${databasePath}`);

  if (isProduction && !cookieSecure) {
    console.warn(
      'AVISO: COOKIE_SECURE está desabilitado em produção. Use HTTPS e COOKIE_SECURE=true.'
    );
  }
});

function shutdown(signal) {
  console.log(`\nRecebido ${signal}. Encerrando...`);

  server.close(() => {
    db.close();
    process.exit(0);
  });

  setTimeout(() => {
    process.exit(1);
  }, 5000).unref();
}

process.on('SIGINT', () => shutdown('SIGINT'));
process.on('SIGTERM', () => shutdown('SIGTERM'));
```

---

### `scripts/create-admin.js`

```javascript
'use strict';

const { db, databasePath } = require('../src/db');
const {
  hashPassword,
  validateUsername,
  validatePassword
} = require('../src/security');

async function main() {
  /*
   * A criação local do primeiro usuário é a exceção necessária à regra
   * de que somente usuários autenticados podem cadastrar outros usuários.
   *
   * A senha é recebida por variável de ambiente para não ser incluída
   * diretamente nos argumentos da linha de comando.
   */
  const username = (
    process.env.ADMIN_USERNAME ||
    process.argv[2] ||
    ''
  ).trim();

  const password = process.env.ADMIN_PASSWORD || '';

  const usernameError = validateUsername(username);
  const passwordError = validatePassword(password);

  if (usernameError || passwordError) {
    console.error(usernameError || passwordError);
    console.error('');
    console.error('Uso:');
    console.error(
      '  ADMIN_USERNAME=admin ADMIN_PASSWORD="senha-segura" npm run create-admin'
    );
    console.error('');
    console.error('Ou informe apenas o usuário como argumento:');
    console.error(
      '  ADMIN_PASSWORD="senha-segura" npm run create-admin -- admin'
    );
    process.exitCode = 1;
    return;
  }

  const existingUser = db.prepare(`
    SELECT id
    FROM users
    WHERE username = ?
  `).get(username);

  if (existingUser) {
    console.error(`O usuário "${username}" já existe.`);
    process.exitCode = 1;
    return;
  }

  const passwordData = await hashPassword(password);

  db.prepare(`
    INSERT INTO users (username, password_hash, password_salt)
    VALUES (?, ?, ?)
  `).run(username, passwordData.hash, passwordData.salt);

  console.log(`Usuário inicial "${username}" criado com sucesso.`);
  console.log(`Banco SQLite: ${databasePath}`);
}

main()
  .catch((error) => {
    console.error('Não foi possível criar o usuário inicial.');
    console.error(error);
    process.exitCode = 1;
  })
  .finally(() => {
    db.close();
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
</head>
<body>
  <header class="page-header">
    <div class="container header-content">
      <div>
        <h1>Cadastro de usuários</h1>
        <p>Listagem pública com gerenciamento autenticado.</p>
      </div>

      <div id="session-summary" class="session-summary">
        Verificando sessão...
      </div>
    </div>
  </header>

  <main class="container layout">
    <section id="login-section" class="card">
      <h2>Entrar</h2>

      <form id="login-form">
        <label for="login-username">Usuário</label>
        <input
          id="login-username"
          name="username"
          type="text"
          autocomplete="username"
          required
        >

        <label for="login-password">Senha</label>
        <input
          id="login-password"
          name="password"
          type="password"
          autocomplete="current-password"
          required
        >

        <button type="submit">Entrar</button>
      </form>
    </section>

    <section id="management-section" class="card" hidden>
      <div class="section-heading">
        <h2 id="user-form-title">Cadastrar usuário</h2>
        <button id="logout-button" type="button" class="secondary">
          Sair
        </button>
      </div>

      <form id="user-form">
        <input id="editing-user-id" type="hidden">

        <label for="user-username">Usuário</label>
        <input
          id="user-username"
          name="username"
          type="text"
          minlength="3"
          maxlength="50"
          pattern="[A-Za-z0-9._-]+"
          autocomplete="off"
          required
        >
        <small>
          Use de 3 a 50 letras, números, ponto, hífen ou sublinhado.
        </small>

        <label for="user-password">Senha</label>
        <input
          id="user-password"
          name="password"
          type="password"
          minlength="10"
          maxlength="200"
          autocomplete="new-password"
        >
        <small id="password-help">
          Mínimo de 10 caracteres.
        </small>

        <div class="form-actions">
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

    <section class="card users-card">
      <div class="section-heading">
        <div>
          <h2>Usuários</h2>
          <p class="muted">Esta listagem é pública.</p>
        </div>

        <button id="refresh-button" type="button" class="secondary">
          Atualizar
        </button>
      </div>

      <div id="message" class="message" role="status" hidden></div>

      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Usuário</th>
              <th>Cadastrado em</th>
              <th>Atualizado em</th>
              <th id="actions-heading" hidden>Ações</th>
            </tr>
          </thead>
          <tbody id="users-table-body">
            <tr>
              <td colspan="4">Carregando...</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </main>

  <script src="/app.js" defer></script>
</body>
</html>
```

---

### `public/app.js`

```javascript
'use strict';

const state = {
  authenticated: false,
  currentUser: null,
  csrfToken: null,
  users: []
};

const loginSection = document.querySelector('#login-section');
const managementSection = document.querySelector('#management-section');
const sessionSummary = document.querySelector('#session-summary');

const loginForm = document.querySelector('#login-form');
const logoutButton = document.querySelector('#logout-button');

const userForm = document.querySelector('#user-form');
const userFormTitle = document.querySelector('#user-form-title');
const editingUserId = document.querySelector('#editing-user-id');
const userUsername = document.querySelector('#user-username');
const userPassword = document.querySelector('#user-password');
const passwordHelp = document.querySelector('#password-help');
const saveUserButton = document.querySelector('#save-user-button');
const cancelEditButton = document.querySelector('#cancel-edit-button');

const usersTableBody = document.querySelector('#users-table-body');
const actionsHeading = document.querySelector('#actions-heading');
const refreshButton = document.querySelector('#refresh-button');
const messageElement = document.querySelector('#message');

async function request(url, options = {}) {
  const headers = new Headers(options.headers || {});

  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  if (
    state.authenticated &&
    state.csrfToken &&
    options.method &&
    !['GET', 'HEAD'].includes(options.method.toUpperCase())
  ) {
    headers.set('X-CSRF-Token', state.csrfToken);
  }

  const response = await fetch(url, {
    credentials: 'same-origin',
    ...options,
    headers
  });

  let body = {};

  try {
    body = await response.json();
  } catch {
    body = {};
  }

  if (!response.ok) {
    const error = new Error(body.error || 'A operação não pôde ser concluída.');
    error.status = response.status;
    throw error;
  }

  return body;
}

function showMessage(text, type = 'success') {
  messageElement.textContent = text;
  messageElement.className = `message ${type}`;
  messageElement.hidden = false;
}

function hideMessage() {
  messageElement.hidden = true;
  messageElement.textContent = '';
}

function formatDate(value) {
  if (!value) {
    return '-';
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'short',
    timeStyle: 'short'
  }).format(date);
}

function updateSessionInterface() {
  loginSection.hidden = state.authenticated;
  managementSection.hidden = !state.authenticated;
  actionsHeading.hidden = !state.authenticated;

  if (state.authenticated) {
    sessionSummary.textContent = `Autenticado como ${state.currentUser.username}`;
  } else {
    sessionSummary.textContent = 'A listagem pode ser consultada sem login.';
    resetUserForm();
  }

  renderUsers();
}

function createCell(text) {
  const cell = document.createElement('td');
  cell.textContent = text;
  return cell;
}

function renderUsers() {
  usersTableBody.replaceChildren();

  if (state.users.length === 0) {
    const row = document.createElement('tr');
    const cell = document.createElement('td');

    cell.colSpan = state.authenticated ? 4 : 3;
    cell.textContent = 'Nenhum usuário cadastrado.';

    row.appendChild(cell);
    usersTableBody.appendChild(row);
    return;
  }

  for (const user of state.users) {
    const row = document.createElement('tr');

    row.appendChild(createCell(user.username));
    row.appendChild(createCell(formatDate(user.created_at)));
    row.appendChild(createCell(formatDate(user.updated_at)));

    if (state.authenticated) {
      const actionsCell = document.createElement('td');
      const actions = document.createElement('div');
      actions.className = 'row-actions';

      const editButton = document.createElement('button');
      editButton.type = 'button';
      editButton.className = 'small secondary';
      editButton.textContent = 'Editar';
      editButton.addEventListener('click', () => startEditing(user));

      const deleteButton = document.createElement('button');
      deleteButton.type = 'button';
      deleteButton.className = 'small danger';
      deleteButton.textContent = 'Excluir';
      deleteButton.disabled = user.id === state.currentUser.id;
      deleteButton.title = deleteButton.disabled
        ? 'Não é possível excluir a conta da sessão atual.'
        : 'Excluir usuário';
      deleteButton.addEventListener('click', () => deleteUser(user));

      actions.append(editButton, deleteButton);
      actionsCell.appendChild(actions);
      row.appendChild(actionsCell);
    }

    usersTableBody.appendChild(row);
  }
}

async function loadSession() {
  const result = await request('/api/session');

  state.authenticated = result.authenticated;
  state.currentUser = result.user || null;
  state.csrfToken = result.csrfToken || null;

  updateSessionInterface();
}

async function loadUsers() {
  const result = await request('/api/users');
  state.users = result.users;
  renderUsers();
}

function resetUserForm() {
  userForm.reset();
  editingUserId.value = '';
  userFormTitle.textContent = 'Cadastrar usuário';
  saveUserButton.textContent = 'Cadastrar';
  cancelEditButton.hidden = true;
  userPassword.required = state.authenticated;
  passwordHelp.textContent = 'Mínimo de 10 caracteres.';
}

function startEditing(user) {
  editingUserId.value = String(user.id);
  userUsername.value = user.username;
  userPassword.value = '';
  userPassword.required = false;

  userFormTitle.textContent = `Editar ${user.username}`;
  saveUserButton.textContent = 'Salvar alterações';
  cancelEditButton.hidden = false;
  passwordHelp.textContent =
    'Deixe em branco para manter a senha atual. Uma nova senha deve ter no mínimo 10 caracteres.';

  userUsername.focus();
  managementSection.scrollIntoView({
    behavior: 'smooth',
    block: 'start'
  });
}

async function deleteUser(user) {
  const confirmed = window.confirm(
    `Deseja realmente excluir o usuário "${user.username}"?`
  );

  if (!confirmed) {
    return;
  }

  hideMessage();

  try {
    await request(`/api/users/${user.id}`, {
      method: 'DELETE'
    });

    if (editingUserId.value === String(user.id)) {
      resetUserForm();
    }

    showMessage('Usuário removido.');
    await loadUsers();
  } catch (error) {
    await handleRequestError(error);
  }
}

async function handleRequestError(error) {
  if (error.status === 401) {
    await loadSession();
    showMessage('Sua sessão expirou. Entre novamente.', 'error');
    return;
  }

  showMessage(error.message, 'error');
}

loginForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  hideMessage();

  const formData = new FormData(loginForm);

  try {
    const result = await request('/api/login', {
      method: 'POST',
      body: JSON.stringify({
        username: formData.get('username'),
        password: formData.get('password')
      })
    });

    state.authenticated = true;
    state.currentUser = result.user;
    state.csrfToken = result.csrfToken;

    loginForm.reset();
    updateSessionInterface();
    resetUserForm();
    showMessage('Login realizado com sucesso.');
    await loadUsers();
  } catch (error) {
    showMessage(error.message, 'error');
  }
});

logoutButton.addEventListener('click', async () => {
  hideMessage();

  try {
    await request('/api/logout', {
      method: 'POST'
    });

    state.authenticated = false;
    state.currentUser = null;
    state.csrfToken = null;

    updateSessionInterface();
    showMessage('Sessão encerrada.');
  } catch (error) {
    await handleRequestError(error);
  }
});

userForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  hideMessage();

  const userId = editingUserId.value;
  const username = userUsername.value.trim();
  const password = userPassword.value;

  const isEditing = Boolean(userId);

  const payload = {
    username
  };

  if (!isEditing || password) {
    payload.password = password;
  }

  try {
    await request(
      isEditing ? `/api/users/${userId}` : '/api/users',
      {
        method: isEditing ? 'PUT' : 'POST',
        body: JSON.stringify(payload)
      }
    );

    showMessage(
      isEditing ? 'Usuário atualizado.' : 'Usuário cadastrado.'
    );

    resetUserForm();
    await loadSession();
    await loadUsers();
  } catch (error) {
    await handleRequestError(error);
  }
});

cancelEditButton.addEventListener('click', () => {
  resetUserForm();
});

refreshButton.addEventListener('click', async () => {
  hideMessage();

  try {
    await loadSession();
    await loadUsers();
  } catch (error) {
    showMessage(error.message, 'error');
  }
});

async function initialize() {
  try {
    await Promise.all([
      loadSession(),
      loadUsers()
    ]);
  } catch (error) {
    showMessage(
      'Não foi possível carregar os dados. Verifique se o servidor está disponível.',
      'error'
    );
  }
}

initialize();
```

---

### `public/styles.css`

```css
:root {
  color-scheme: light;
  font-family:
    Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
    "Segoe UI", sans-serif;
  color: #1f2937;
  background: #f3f4f6;
  line-height: 1.5;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-width: 320px;
}

button,
input {
  font: inherit;
}

button {
  border: 0;
  border-radius: 0.5rem;
  padding: 0.7rem 1rem;
  color: #fff;
  background: #2563eb;
  cursor: pointer;
  font-weight: 600;
}

button:hover:not(:disabled) {
  background: #1d4ed8;
}

button:focus-visible,
input:focus-visible {
  outline: 3px solid rgba(37, 99, 235, 0.35);
  outline-offset: 2px;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

button.secondary {
  color: #1f2937;
  background: #e5e7eb;
}

button.secondary:hover:not(:disabled) {
  background: #d1d5db;
}

button.danger {
  background: #dc2626;
}

button.danger:hover:not(:disabled) {
  background: #b91c1c;
}

button.small {
  padding: 0.45rem 0.7rem;
  font-size: 0.875rem;
}

.container {
  width: min(1100px, calc(100% - 2rem));
  margin-inline: auto;
}

.page-header {
  padding: 2rem 0;
  color: #fff;
  background: #111827;
}

.page-header h1,
.page-header p {
  margin: 0;
}

.page-header p {
  margin-top: 0.4rem;
  color: #d1d5db;
}

.header-content,
.section-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.session-summary {
  padding: 0.7rem 1rem;
  border: 1px solid #374151;
  border-radius: 0.5rem;
  background: #1f2937;
}

.layout {
  display: grid;
  gap: 1.25rem;
  padding-block: 1.5rem 3rem;
}

.card {
  padding: 1.25rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.8rem;
  background: #fff;
  box-shadow: 0 3px 12px rgba(17, 24, 39, 0.05);
}

.card h2 {
  margin-top: 0;
}

.users-card {
  overflow: hidden;
}

form {
  display: grid;
  gap: 0.65rem;
}

form label {
  margin-top: 0.4rem;
  font-weight: 600;
}

input {
  width: 100%;
  border: 1px solid #9ca3af;
  border-radius: 0.5rem;
  padding: 0.7rem 0.8rem;
  color: #111827;
  background: #fff;
}

small,
.muted {
  color: #6b7280;
}

.form-actions,
.row-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
}

.form-actions {
  margin-top: 0.7rem;
}

.message {
  margin-block: 1rem;
  border-radius: 0.5rem;
  padding: 0.8rem 1rem;
}

.message.success {
  color: #166534;
  background: #dcfce7;
}

.message.error {
  color: #991b1b;
  background: #fee2e2;
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
  border-bottom: 1px solid #e5e7eb;
  text-align: left;
  vertical-align: middle;
}

th {
  color: #374151;
  background: #f9fafb;
}

@media (min-width: 850px) {
  .layout {
    grid-template-columns: minmax(280px, 0.8fr) minmax(0, 2fr);
    align-items: start;
  }

  .users-card {
    grid-column: 2;
    grid-row: 1 / span 2;
  }
}

@media (max-width: 600px) {
  .header-content,
  .section-heading {
    align-items: stretch;
    flex-direction: column;
  }

  .session-summary {
    width: 100%;
  }

  th,
  td {
    padding: 0.65rem 0.5rem;
  }
}
```

---

### `README.md`

```markdown
# Cadastro de usuários seguro

Sistema web em Node.js com:

- Login por usuário e senha.
- Hash de senha com `scrypt` e salt individual.
- Sessões persistidas em SQLite.
- Cookie de autenticação `HttpOnly`.
- Proteção CSRF para operações autenticadas.
- Cadastro, edição e remoção somente para usuários autenticados.
- Listagem pública de usuários.
- Revogação de sessões após alterações de senha.
- Limitador básico de tentativas de login.

## Requisitos

- Node.js 20 ou mais recente.
- npm.
- Em alguns ambientes, ferramentas de compilação podem ser necessárias para
  instalar o `better-sqlite3`.

## Instalação

```bash
npm install
```

## Criar o primeiro usuário

Como apenas usuários autenticados podem cadastrar outros usuários, o primeiro
usuário deve ser criado localmente pelo script administrativo.

Linux/macOS:

```bash
ADMIN_USERNAME=admin \
ADMIN_PASSWORD='uma-senha-longa-e-segura' \
npm run create-admin
```

Também é possível passar o usuário como argumento:

```bash
ADMIN_PASSWORD='uma-senha-longa-e-segura' \
npm run create-admin -- admin
```

PowerShell:

```powershell
$env:ADMIN_USERNAME = "admin"
$env:ADMIN_PASSWORD = "uma-senha-longa-e-segura"
npm run create-admin
```

Prompt de comando do Windows:

```bat
set ADMIN_USERNAME=admin
set ADMIN_PASSWORD=uma-senha-longa-e-segura
npm run create-admin
```

Por segurança, remova as variáveis administrativas do ambiente após executar
o comando.

## Executar

```bash
npm start
```

Acesse:

```text
http://127.0.0.1:3000
```

Para desenvolvimento com reinicialização automática:

```bash
npm run dev
```

## Configuração

As variáveis são lidas diretamente do ambiente. O projeto não usa uma
dependência adicional para carregar arquivos `.env`.

Variáveis disponíveis:

- `PORT`: porta HTTP. Padrão: `3000`.
- `HOST`: endereço de escuta. Padrão: `127.0.0.1`.
- `DB_FILE`: caminho do SQLite. Padrão: `./data/app.db`.
- `NODE_ENV`: use `production` em produção.
- `COOKIE_SECURE`: use `true` quando o acesso for exclusivamente por HTTPS.
- `APP_ORIGIN`: origem pública exata, por exemplo
  `https://usuarios.exemplo.com`.

Exemplo:

```bash
PORT=8080 DB_FILE=/var/lib/usuarios/app.db npm start
```

## Produção

Execute atrás de HTTPS e configure:

```bash
NODE_ENV=production
COOKIE_SECURE=true
APP_ORIGIN=https://usuarios.exemplo.com
```

Exemplo:

```bash
NODE_ENV=production \
COOKIE_SECURE=true \
APP_ORIGIN=https://usuarios.exemplo.com \
HOST=127.0.0.1 \
PORT=3000 \
DB_FILE=/var/lib/usuarios/app.db \
npm start
```

O proxy reverso deve encaminhar apenas para o endereço local da aplicação.

## API

### Pública

- `GET /api/users`
- `GET /api/session`
- `POST /api/login`

### Autenticada

- `POST /api/logout`
- `POST /api/users`
- `PUT /api/users/:id`
- `DELETE /api/users/:id`

As operações autenticadas de escrita exigem o cabeçalho:

```text
X-CSRF-Token: token-retornado-por-/api/session
```

O navegador gerencia automaticamente o cookie de sessão pela interface web.

## Observações de segurança

- O token original da sessão não é salvo no banco; somente seu hash SHA-256.
- Senhas recebem um salt aleatório e são processadas com `scrypt`.
- As sessões expiram após 8 horas.
- A alteração de senha revoga outras sessões do usuário.
- A própria conta da sessão atual não pode ser excluída.
- A listagem pública não retorna hashes, salts nem dados de sessão.
- Em produção, use obrigatoriamente HTTPS e `COOKIE_SECURE=true`.
```

## Execução rápida

Depois de criar os arquivos:

```bash
npm install
```

Crie o primeiro usuário:

```bash
ADMIN_USERNAME=admin \
ADMIN_PASSWORD='uma-senha-com-pelo-menos-10-caracteres' \
npm run create-admin
```

Inicie o servidor:

```bash
npm start
```

Abra:

```text
http://127.0.0.1:3000
```