<!--
nivel: 4 - Seguranca (autenticacao e autorizacao)
provider: claude
model: claude-sonnet-5
tentativa: 1
temperature: 0.2
timestamp: 2026-08-18T21:34:55.750Z
metadata: {"model":"claude-sonnet-5","usage":{"input_tokens":366,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"cache_creation":{"ephemeral_5m_input_tokens":0,"ephemeral_1h_input_tokens":0},"output_tokens":11939,"output_tokens_details":{"thinking_tokens":1752},"service_tier":"standard","inference_geo":"global"},"stop_reason":"end_turn"}
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

# Sistema de Cadastro com Autenticação (Node.js + SQLite)

## Decisões de projeto (documentadas)

- **Framework HTTP:** `express` — é o mínimo necessário para roteamento, parsing de JSON e servir arquivos estáticos sem reinventar a roda.
- **Banco de dados:** `better-sqlite3` — driver SQLite síncrono, rápido, sem necessidade de ORM.
- **Hash de senha:** `crypto.scrypt` (nativo do Node, **sem dependência externa**) com salt aleatório de 16 bytes por usuário. Formato armazenado: `salt:hash` (hex).
- **Token de autenticação:** JWT (`jsonwebtoken`) assinado com segredo do servidor, guardado em **cookie httpOnly** (mitiga XSS) e `SameSite=Lax` (mitiga CSRF básico). Expira em 2 horas.
- **Cookies:** `cookie-parser` para ler o cookie do token.
- **Controle de acesso:** listagem de registros (`GET /api/records`) é pública; criação/edição/remoção exigem middleware de autenticação (`requireAuth`).
- **Ownership:** qualquer usuário autenticado pode editar/remover qualquer registro (o enunciado não pede restrição por dono). Isso está isolado no middleware, fácil de restringir depois.
- **Front-end:** HTML/CSS/JS puro (sem framework front-end), consumindo a API via `fetch` com `credentials: 'include'`.
- **Entidades:** `users` (autenticação) e `records` (os "registros" cadastráveis: título + descrição).

Estrutura de arquivos:

```
.
├── package.json
├── .env.example
├── db.js
├── utils/
│   ├── password.js
│   └── auth.js
├── routes/
│   ├── auth.routes.js
│   └── records.routes.js
├── server.js
└── public/
    ├── index.html
    ├── style.css
    └── app.js
```

---

### `package.json`

```json
{
  "name": "cadastro-auth-sqlite",
  "version": "1.0.0",
  "description": "Sistema de cadastro de usuarios com login, senha hasheada, JWT em cookie e CRUD de registros com controle de acesso.",
  "main": "server.js",
  "type": "commonjs",
  "scripts": {
    "start": "node server.js",
    "dev": "node server.js"
  },
  "dependencies": {
    "better-sqlite3": "^11.3.0",
    "cookie-parser": "^1.4.6",
    "dotenv": "^16.4.5",
    "express": "^4.19.2",
    "jsonwebtoken": "^9.0.2"
  }
}
```

---

### `.env.example`

```
# Copie este arquivo para .env e ajuste os valores em producao
PORT=3000
JWT_SECRET=troque-este-segredo-por-um-valor-aleatorio-grande
NODE_ENV=development
```

---

### `db.js`

```js
// db.js
// Inicializa o banco SQLite e garante a existencia das tabelas necessarias.
const Database = require('better-sqlite3');
const path = require('path');

const DB_PATH = path.join(__dirname, 'data.sqlite');
const db = new Database(DB_PATH);

// Ativa chaves estrangeiras (desligado por padrao no SQLite)
db.pragma('foreign_keys = ON');

// Tabela de usuarios: senha nunca armazenada em texto puro.
db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL, -- formato: salt:hash (hex)
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
  );
`);

// Tabela de registros publicos (listagem publica, escrita restrita a autenticados).
db.exec(`
  CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    owner_id INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
  );
`);

module.exports = db;
```

---

### `utils/password.js`

```js
// utils/password.js
// Hash de senha usando scrypt (nativo do Node) + salt aleatorio.
// Evita dependencia externa (ex: bcrypt) mantendo seguranca adequada.
const crypto = require('crypto');

const KEY_LEN = 64;

function hashPassword(plainPassword) {
  const salt = crypto.randomBytes(16).toString('hex');
  const derivedKey = crypto.scryptSync(plainPassword, salt, KEY_LEN);
  return `${salt}:${derivedKey.toString('hex')}`;
}

function verifyPassword(plainPassword, storedHash) {
  const [salt, keyHex] = storedHash.split(':');
  if (!salt || !keyHex) return false;
  const derivedKey = crypto.scryptSync(plainPassword, salt, KEY_LEN);
  const storedKey = Buffer.from(keyHex, 'hex');
  // Comparacao em tempo constante para evitar timing attacks
  if (storedKey.length !== derivedKey.length) return false;
  return crypto.timingSafeEqual(storedKey, derivedKey);
}

module.exports = { hashPassword, verifyPassword };
```

---

### `utils/auth.js`

```js
// utils/auth.js
// Geracao/verificacao de token JWT e middleware de controle de acesso.
const jwt = require('jsonwebtoken');

const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret-nao-use-em-producao';
const TOKEN_EXPIRES_IN = '2h';
const COOKIE_NAME = 'auth_token';

function generateToken(user) {
  return jwt.sign(
    { id: user.id, username: user.username },
    JWT_SECRET,
    { expiresIn: TOKEN_EXPIRES_IN }
  );
}

function setAuthCookie(res, token) {
  res.cookie(COOKIE_NAME, token, {
    httpOnly: true, // impede acesso via JS no browser (mitiga XSS)
    sameSite: 'lax', // mitigacao basica de CSRF
    secure: process.env.NODE_ENV === 'production', // exige HTTPS em producao
    maxAge: 2 * 60 * 60 * 1000, // 2h em ms
  });
}

function clearAuthCookie(res) {
  res.clearCookie(COOKIE_NAME);
}

// Middleware: exige usuario autenticado. Popula req.user.
function requireAuth(req, res, next) {
  const token = req.cookies[COOKIE_NAME];
  if (!token) {
    return res.status(401).json({ error: 'Autenticacao necessaria.' });
  }
  try {
    const payload = jwt.verify(token, JWT_SECRET);
    req.user = payload;
    next();
  } catch (err) {
    return res.status(401).json({ error: 'Token invalido ou expirado.' });
  }
}

// Middleware opcional: nao bloqueia, mas popula req.user se houver token valido.
function attachUserIfPresent(req, res, next) {
  const token = req.cookies[COOKIE_NAME];
  if (token) {
    try {
      req.user = jwt.verify(token, JWT_SECRET);
    } catch (err) {
      // token invalido: ignora, segue como anonimo
    }
  }
  next();
}

module.exports = {
  generateToken,
  setAuthCookie,
  clearAuthCookie,
  requireAuth,
  attachUserIfPresent,
  COOKIE_NAME,
};
```

---

### `routes/auth.routes.js`

```js
// routes/auth.routes.js
// Rotas de cadastro/login/logout de usuarios do sistema.
const express = require('express');
const db = require('../db');
const { hashPassword, verifyPassword } = require('../utils/password');
const {
  generateToken,
  setAuthCookie,
  clearAuthCookie,
  requireAuth,
} = require('../utils/auth');

const router = express.Router();

function isValidUsername(username) {
  return typeof username === 'string' && /^[a-zA-Z0-9_.-]{3,30}$/.test(username);
}

function isValidPassword(password) {
  return typeof password === 'string' && password.length >= 6 && password.length <= 200;
}

// POST /api/auth/register - cria um novo usuario (endpoint publico, e o "cadastro")
router.post('/register', (req, res) => {
  const { username, password } = req.body || {};

  if (!isValidUsername(username)) {
    return res.status(400).json({
      error: 'Usuario invalido. Use 3-30 caracteres: letras, numeros, ".", "_" ou "-".',
    });
  }
  if (!isValidPassword(password)) {
    return res.status(400).json({ error: 'Senha invalida. Minimo 6 caracteres.' });
  }

  const existing = db.prepare('SELECT id FROM users WHERE username = ?').get(username);
  if (existing) {
    return res.status(409).json({ error: 'Usuario ja existe.' });
  }

  const passwordHash = hashPassword(password);
  const info = db
    .prepare('INSERT INTO users (username, password_hash) VALUES (?, ?)')
    .run(username, passwordHash);

  return res.status(201).json({ id: info.lastInsertRowid, username });
});

// POST /api/auth/login - autentica e emite cookie com JWT
router.post('/login', (req, res) => {
  const { username, password } = req.body || {};

  if (!isValidUsername(username) || !isValidPassword(password)) {
    return res.status(400).json({ error: 'Credenciais invalidas.' });
  }

  const user = db.prepare('SELECT * FROM users WHERE username = ?').get(username);
  if (!user || !verifyPassword(password, user.password_hash)) {
    // mensagem generica para nao revelar se o usuario existe
    return res.status(401).json({ error: 'Usuario ou senha incorretos.' });
  }

  const token = generateToken(user);
  setAuthCookie(res, token);
  return res.json({ id: user.id, username: user.username });
});

// POST /api/auth/logout - limpa o cookie de sessao
router.post('/logout', (req, res) => {
  clearAuthCookie(res);
  return res.status(204).send();
});

// GET /api/auth/me - retorna dados do usuario logado (uso pelo front-end)
router.get('/me', requireAuth, (req, res) => {
  return res.json({ id: req.user.id, username: req.user.username });
});

module.exports = router;
```

---

### `routes/records.routes.js`

```js
// routes/records.routes.js
// CRUD de "registros". Listagem publica; criacao/edicao/remocao exigem autenticacao.
const express = require('express');
const db = require('../db');
const { requireAuth } = require('../utils/auth');

const router = express.Router();

function isValidTitle(title) {
  return typeof title === 'string' && title.trim().length >= 1 && title.trim().length <= 200;
}

// GET /api/records - PUBLICO
router.get('/', (req, res) => {
  const records = db
    .prepare(
      `SELECT records.id, records.title, records.description,
              records.created_at, records.updated_at,
              users.username AS owner
       FROM records
       JOIN users ON users.id = records.owner_id
       ORDER BY records.created_at DESC`
    )
    .all();
  res.json(records);
});

// GET /api/records/:id - PUBLICO (detalhe individual)
router.get('/:id', (req, res) => {
  const record = db
    .prepare(
      `SELECT records.id, records.title, records.description,
              records.created_at, records.updated_at,
              users.username AS owner
       FROM records
       JOIN users ON users.id = records.owner_id
       WHERE records.id = ?`
    )
    .get(req.params.id);

  if (!record) return res.status(404).json({ error: 'Registro nao encontrado.' });
  res.json(record);
});

// POST /api/records - AUTENTICADO
router.post('/', requireAuth, (req, res) => {
  const { title, description } = req.body || {};
  if (!isValidTitle(title)) {
    return res.status(400).json({ error: 'Titulo invalido (1-200 caracteres).' });
  }

  const info = db
    .prepare('INSERT INTO records (title, description, owner_id) VALUES (?, ?, ?)')
    .run(title.trim(), description || null, req.user.id);

  const created = db.prepare('SELECT * FROM records WHERE id = ?').get(info.lastInsertRowid);
  res.status(201).json(created);
});

// PUT /api/records/:id - AUTENTICADO
router.put('/:id', requireAuth, (req, res) => {
  const { title, description } = req.body || {};
  const existing = db.prepare('SELECT * FROM records WHERE id = ?').get(req.params.id);
  if (!existing) return res.status(404).json({ error: 'Registro nao encontrado.' });

  if (!isValidTitle(title)) {
    return res.status(400).json({ error: 'Titulo invalido (1-200 caracteres).' });
  }

  db.prepare(
    `UPDATE records SET title = ?, description = ?, updated_at = datetime('now') WHERE id = ?`
  ).run(title.trim(), description || null, req.params.id);

  const updated = db.prepare('SELECT * FROM records WHERE id = ?').get(req.params.id);
  res.json(updated);
});

// DELETE /api/records/:id - AUTENTICADO
router.delete('/:id', requireAuth, (req, res) => {
  const existing = db.prepare('SELECT * FROM records WHERE id = ?').get(req.params.id);
  if (!existing) return res.status(404).json({ error: 'Registro nao encontrado.' });

  db.prepare('DELETE FROM records WHERE id = ?').run(req.params.id);
  res.status(204).send();
});

module.exports = router;
```

---

### `server.js`

```js
// server.js
// Ponto de entrada da aplicacao.
require('dotenv').config();

const express = require('express');
const cookieParser = require('cookie-parser');
const path = require('path');

const authRoutes = require('./routes/auth.routes');
const recordsRoutes = require('./routes/records.routes');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(cookieParser());

// Front-end estatico (HTML/CSS/JS puros)
app.use(express.static(path.join(__dirname, 'public')));

// Rotas da API
app.use('/api/auth', authRoutes);
app.use('/api/records', recordsRoutes);

// Handler de erro generico (evita vazar stack trace)
app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ error: 'Erro interno do servidor.' });
});

app.listen(PORT, () => {
  console.log(`Servidor rodando em http://localhost:${PORT}`);
});
```

---

### `public/index.html`

```html
<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Cadastro de Registros</title>
<link rel="stylesheet" href="style.css" />
</head>
<body>
  <header>
    <h1>Sistema de Cadastro</h1>
    <div id="user-info">
      <span id="user-label">Nao autenticado</span>
      <button id="btn-logout" style="display:none;">Sair</button>
    </div>
  </header>

  <main>
    <section id="auth-section">
      <div class="card">
        <h2>Login</h2>
        <form id="login-form">
          <input type="text" name="username" placeholder="Usuario" required />
          <input type="password" name="password" placeholder="Senha" required />
          <button type="submit">Entrar</button>
        </form>
        <p id="login-msg" class="msg"></p>
      </div>

      <div class="card">
        <h2>Cadastrar usuario</h2>
        <form id="register-form">
          <input type="text" name="username" placeholder="Usuario" required />
          <input type="password" name="password" placeholder="Senha (min. 6 caracteres)" required />
          <button type="submit">Cadastrar</button>
        </form>
        <p id="register-msg" class="msg"></p>
      </div>
    </section>

    <section id="record-form-section" style="display:none;">
      <div class="card">
        <h2 id="record-form-title">Novo Registro</h2>
        <form id="record-form">
          <input type="hidden" name="id" />
          <input type="text" name="title" placeholder="Titulo" required />
          <textarea name="description" placeholder="Descricao"></textarea>
          <button type="submit">Salvar</button>
          <button type="button" id="btn-cancel-edit" style="display:none;">Cancelar edicao</button>
        </form>
        <p id="record-msg" class="msg"></p>
      </div>
    </section>

    <section>
      <h2>Registros (listagem publica)</h2>
      <ul id="records-list"></ul>
    </section>
  </main>

  <script src="app.js"></script>
</body>
</html>
```

---

### `public/style.css`

```css
* { box-sizing: border-box; }
body {
  font-family: system-ui, Arial, sans-serif;
  max-width: 800px;
  margin: 0 auto;
  padding: 1rem;
  background: #f5f5f7;
  color: #222;
}
header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
.card {
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
}
#auth-section {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}
#auth-section .card { flex: 1; min-width: 250px; }
form { display: flex; flex-direction: column; gap: 0.5rem; }
input, textarea, button {
  padding: 0.5rem;
  font-size: 1rem;
  border-radius: 4px;
  border: 1px solid #ccc;
}
button {
  cursor: pointer;
  background: #2563eb;
  color: #fff;
  border: none;
}
button:hover { background: #1d4ed8; }
#btn-logout, #btn-cancel-edit {
  background: #999;
}
.msg { font-size: 0.9rem; color: #b00020; min-height: 1.2em; }
ul#records-list { list-style: none; padding: 0; }
ul#records-list li {
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 0.75rem;
  margin-bottom: 0.5rem;
}
.record-meta { font-size: 0.8rem; color: #666; }
.record-actions { margin-top: 0.5rem; display: flex; gap: 0.5rem; }
.record-actions button { font-size: 0.85rem; padding: 0.3rem 0.6rem; }
.btn-delete { background: #dc2626; }
.btn-delete:hover { background: #b91c1c; }
```

---

### `public/app.js`

```js
// public/app.js
// Front-end simples (sem framework) consumindo a API via fetch.
// credentials: 'include' garante envio do cookie httpOnly de autenticacao.

const API = '/api';
let currentUser = null;
let editingId = null;

const el = (id) => document.getElementById(id);

async function api(path, options = {}) {
  const res = await fetch(`${API}${path}`, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  const isJson = res.headers.get('content-type')?.includes('application/json');
  const data = isJson ? await res.json() : null;
  if (!res.ok) {
    throw new Error(data?.error || `Erro HTTP ${res.status}`);
  }
  return data;
}

async function checkSession() {
  try {
    currentUser = await api('/auth/me');
  } catch {
    currentUser = null;
  }
  renderAuthState();
}

function renderAuthState() {
  const label = el('user-label');
  const logoutBtn = el('btn-logout');
  const authSection = el('auth-section');
  const recordFormSection = el('record-form-section');

  if (currentUser) {
    label.textContent = `Logado como: ${currentUser.username}`;
    logoutBtn.style.display = 'inline-block';
    authSection.style.display = 'none';
    recordFormSection.style.display = 'block';
  } else {
    label.textContent = 'Nao autenticado';
    logoutBtn.style.display = 'none';
    authSection.style.display = 'flex';
    recordFormSection.style.display = 'none';
  }
}

async function loadRecords() {
  const list = el('records-list');
  list.innerHTML = '<li>Carregando...</li>';
  try {
    const records = await api('/records');
    list.innerHTML = '';
    if (records.length === 0) {
      list.innerHTML = '<li>Nenhum registro cadastrado ainda.</li>';
      return;
    }
    records.forEach((r) => {
      const li = document.createElement('li');
      li.innerHTML = `
        <strong>${escapeHtml(r.title)}</strong>
        <p>${escapeHtml(r.description || '')}</p>
        <div class="record-meta">Por ${escapeHtml(r.owner)} em ${new Date(r.created_at).toLocaleString()}</div>
        ${currentUser ? `
          <div class="record-actions">
            <button class="btn-edit" data-id="${r.id}" data-title="${encodeURIComponent(r.title)}" data-description="${encodeURIComponent(r.description || '')}">Editar</button>
            <button class="btn-delete" data-id="${r.id}">Remover</button>
          </div>` : ''}
      `;
      list.appendChild(li);
    });
  } catch (err) {
    list.innerHTML = `<li>Erro ao carregar registros: ${err.message}</li>`;
  }
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// --- Handlers de formularios ---

el('login-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const form = new FormData(e.target);
  const msg = el('login-msg');
  msg.textContent = '';
  try {
    await api('/auth/login', {
      method: 'POST',
      body: JSON.stringify({
        username: form.get('username'),
        password: form.get('password'),
      }),
    });
    e.target.reset();
    await checkSession();
    await loadRecords();
  } catch (err) {
    msg.textContent = err.message;
  }
});

el('register-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const form = new FormData(e.target);
  const msg = el('register-msg');
  msg.textContent = '';
  try {
    await api('/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        username: form.get('username'),
        password: form.get('password'),
      }),
    });
    msg.style.color = 'green';
    msg.textContent = 'Usuario criado! Faca login.';
    e.target.reset();
  } catch (err) {
    msg.style.color = '#b00020';
    msg.textContent = err.message;
  }
});

el('btn-logout').addEventListener('click', async () => {
  await api('/auth/logout', { method: 'POST' });
  currentUser = null;
  renderAuthState();
  await loadRecords();
});

el('record-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const form = new FormData(e.target);
  const msg = el('record-msg');
  msg.textContent = '';
  const payload = {
    title: form.get('title'),
    description: form.get('description'),
  };
  try {
    if (editingId) {
      await api(`/records/${editingId}`, { method: 'PUT', body: JSON.stringify(payload) });
    } else {
      await api('/records', { method: 'POST', body: JSON.stringify(payload) });
    }
    e.target.reset();
    editingId = null;
    el('record-form-title').textContent = 'Novo Registro';
    el('btn-cancel-edit').style.display = 'none';
    await loadRecords();
  } catch (err) {
    msg.textContent = err.message;
  }
});

el('btn-cancel-edit').addEventListener('click', () => {
  editingId = null;
  el('record-form').reset();
  el('record-form-title').textContent = 'Novo Registro';
  el('btn-cancel-edit').style.display = 'none';
});

// Delegacao de eventos para botoes de editar/remover (criados dinamicamente)
el('records-list').addEventListener('click', async (e) => {
  if (e.target.classList.contains('btn-delete')) {
    const id = e.target.dataset.id;
    if (!confirm('Remover este registro?')) return;
    try {
      await api(`/records/${id}`, { method: 'DELETE' });
      await loadRecords();
    } catch (err) {
      alert(err.message);
    }
  }

  if (e.target.classList.contains('btn-edit')) {
    const { id, title, description } = e.target.dataset;
    editingId = id;
    const form = el('record-form');
    form.title.value = decodeURIComponent(title);
    form.description.value = decodeURIComponent(description);
    el('record-form-title').textContent = `Editando registro #${id}`;
    el('btn-cancel-edit').style.display = 'inline-block';
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
});

// Inicializacao
(async function init() {
  await checkSession();
  await loadRecords();
})();
```

---

## Instruções de execução

### 1. Pré-requisitos
- Node.js 18+ instalado.

### 2. Instalar dependências

```bash
npm install
```

> Isso instalará `express`, `better-sqlite3`, `cookie-parser`, `jsonwebtoken` e `dotenv`. O `better-sqlite3` compila um binário nativo — em máquinas Linux/Mac/Windows padrão isso funciona automaticamente via `npm install`.

### 3. Configurar variáveis de ambiente

```bash
cp .env.example .env
```

Edite `.env` e defina um `JWT_SECRET` forte (obrigatório em produção).

### 4. Rodar o servidor

```bash
npm start
```

O servidor sobe em `http://localhost:3000` (ou na porta definida em `PORT`).

O arquivo `data.sqlite` será criado automaticamente na primeira execução, com as tabelas `users` e `records`.

### 5. Usar o sistema

1. Abra `http://localhost:3000` no navegador.
2. Cadastre um usuário no formulário "Cadastrar usuario".
3. Faça login.
4. Após logado, o formulário de criação de registros aparece; você pode criar, editar e remover registros.
5. Sem estar logado (ou em aba anônima), a listagem de registros continua visível, mas os botões de criar/editar/remover ficam ocultos — e as rotas correspondentes retornam `401` se chamadas diretamente via API.

### 6. Testando a API diretamente (opcional, via curl)

```bash
# Cadastrar usuario
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"joao","password":"senha123"}'

# Login (salva cookie em cookies.txt)
curl -c cookies.txt -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"joao","password":"senha123"}'

# Criar registro autenticado (usa cookie salvo)
curl -b cookies.txt -X POST http://localhost:3000/api/records \
  -H "Content-Type: application/json" \
  -d '{"title":"Meu primeiro registro","description":"Teste"}'

# Listar registros (publico, sem cookie)
curl http://localhost:3000/api/records
```