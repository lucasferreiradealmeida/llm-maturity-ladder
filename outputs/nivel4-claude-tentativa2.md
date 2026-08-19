<!--
nivel: 4 - Seguranca (autenticacao e autorizacao)
provider: claude
model: claude-sonnet-5
tentativa: 2
temperature: 0.2
timestamp: 2026-08-18T21:36:29.662Z
metadata: {"model":"claude-sonnet-5","usage":{"input_tokens":366,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"cache_creation":{"ephemeral_5m_input_tokens":0,"ephemeral_1h_input_tokens":0},"output_tokens":11203,"output_tokens_details":{"thinking_tokens":1427},"service_tier":"standard","inference_geo":"global"},"stop_reason":"end_turn"}
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

## Decisões de projeto (documentadas conforme pedido)

- **Framework HTTP**: `express` — é o mínimo necessário para rotear requisições HTTP, parsear JSON e servir arquivos estáticos sem reescrever tudo isso manualmente.
- **Banco de dados**: `better-sqlite3` — driver SQLite síncrono, rápido, sem necessidade de servidor externo, com *prepared statements* (proteção contra SQL Injection).
- **Hash de senha**: `bcryptjs` (implementação em JS pura, evita problemas de compilação nativa) — gera salt automaticamente e faz hash com custo configurável (10 rounds).
- **Sessão/token**: `JWT` (jsonwebtoken) armazenado em **cookie httpOnly** (não acessível via JS no browser, mitigando XSS) — abordagem stateless, simples e sem necessidade de tabela de sessões.
- **Entidades**: 
  - `users`: usados exclusivamente para autenticação (cadastro/login).
  - `records`: um cadastro genérico (ex.: "contatos"/"itens") que representa "os registros" citados no enunciado. Listagem é pública; criar/editar/remover exige autenticação.
- **CSRF**: como o cookie é `SameSite=Lax` e a API só aceita `application/json` (não formulários simples), o risco de CSRF clássico é reduzido. Para produção real, recomenda-se token CSRF adicional (fora do escopo mínimo pedido).
- **Front-end**: HTML/CSS/JS puro (sem framework front-end), consumindo a API via `fetch`.

---

## Estrutura de arquivos

```
projeto/
├── package.json
├── .env.example
├── src/
│   ├── server.js
│   ├── db.js
│   ├── middleware/
│   │   └── auth.js
│   └── routes/
│       ├── authRoutes.js
│       └── recordRoutes.js
└── public/
    ├── index.html
    ├── app.js
    └── style.css
```

---

### `package.json`

```json
{
  "name": "cadastro-auth-sqlite",
  "version": "1.0.0",
  "description": "Sistema web de cadastro com login, senha hasheada, JWT e SQLite",
  "main": "src/server.js",
  "type": "commonjs",
  "scripts": {
    "start": "node src/server.js",
    "dev": "node --watch src/server.js"
  },
  "dependencies": {
    "better-sqlite3": "^11.3.0",
    "bcryptjs": "^2.4.3",
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
# Copie este arquivo para ".env" e ajuste os valores
PORT=3000
JWT_SECRET=troque-este-segredo-por-um-valor-aleatorio-longo
NODE_ENV=development
```

---

### `src/db.js`

```javascript
// src/db.js
// Responsável por inicializar a conexão SQLite e criar as tabelas necessárias.
const path = require('path');
const Database = require('better-sqlite3');

const DB_PATH = path.join(__dirname, '..', 'data.sqlite');
const db = new Database(DB_PATH);

// Habilita chaves estrangeiras
db.pragma('foreign_keys = ON');

// Tabela de usuários (autenticação)
db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
  )
`);

// Tabela de registros (o "cadastro" público para leitura, protegido para escrita)
db.exec(`
  CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    created_by INTEGER,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
  )
`);

module.exports = db;
```

---

### `src/middleware/auth.js`

```javascript
// src/middleware/auth.js
// Middleware de autenticação baseado em JWT armazenado em cookie httpOnly.
const jwt = require('jsonwebtoken');

const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret-nao-use-em-producao';

function requireAuth(req, res, next) {
  const token = req.cookies && req.cookies.token;

  if (!token) {
    return res.status(401).json({ error: 'Autenticação necessária. Faça login.' });
  }

  try {
    const payload = jwt.verify(token, JWT_SECRET);
    req.user = { id: payload.sub, username: payload.username };
    next();
  } catch (err) {
    return res.status(401).json({ error: 'Token inválido ou expirado.' });
  }
}

// Middleware opcional: se houver token válido, popula req.user, mas não bloqueia.
function attachUserIfPresent(req, _res, next) {
  const token = req.cookies && req.cookies.token;
  if (token) {
    try {
      const payload = jwt.verify(token, JWT_SECRET);
      req.user = { id: payload.sub, username: payload.username };
    } catch (_err) {
      // token inválido: ignora silenciosamente
    }
  }
  next();
}

module.exports = { requireAuth, attachUserIfPresent, JWT_SECRET };
```

---

### `src/routes/authRoutes.js`

```javascript
// src/routes/authRoutes.js
// Rotas de cadastro de usuário, login, logout e verificação da sessão atual.
const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const db = require('../db');
const { requireAuth, JWT_SECRET } = require('../middleware/auth');

const router = express.Router();

const SALT_ROUNDS = 10;
const TOKEN_EXPIRES_IN = '2h';

// Validação simples de entrada
function validateCredentials(username, password) {
  if (typeof username !== 'string' || typeof password !== 'string') {
    return 'Usuário e senha são obrigatórios.';
  }
  if (username.trim().length < 3) {
    return 'Usuário deve ter ao menos 3 caracteres.';
  }
  if (password.length < 6) {
    return 'Senha deve ter ao menos 6 caracteres.';
  }
  return null;
}

// POST /api/auth/register — cria um novo usuário com senha hasheada (hash + salt)
router.post('/register', (req, res) => {
  const { username, password } = req.body || {};

  const validationError = validateCredentials(username, password);
  if (validationError) {
    return res.status(400).json({ error: validationError });
  }

  const cleanUsername = username.trim();

  const existing = db.prepare('SELECT id FROM users WHERE username = ?').get(cleanUsername);
  if (existing) {
    return res.status(409).json({ error: 'Usuário já existe.' });
  }

  // bcrypt gera o salt automaticamente e o embute no hash resultante.
  const passwordHash = bcrypt.hashSync(password, SALT_ROUNDS);

  const info = db
    .prepare('INSERT INTO users (username, password_hash) VALUES (?, ?)')
    .run(cleanUsername, passwordHash);

  return res.status(201).json({ id: info.lastInsertRowid, username: cleanUsername });
});

// POST /api/auth/login — verifica credenciais e emite cookie com JWT
router.post('/login', (req, res) => {
  const { username, password } = req.body || {};

  if (typeof username !== 'string' || typeof password !== 'string') {
    return res.status(400).json({ error: 'Usuário e senha são obrigatórios.' });
  }

  const user = db.prepare('SELECT * FROM users WHERE username = ?').get(username.trim());
  if (!user) {
    // Mensagem genérica para não revelar se o usuário existe ou não
    return res.status(401).json({ error: 'Credenciais inválidas.' });
  }

  const passwordMatches = bcrypt.compareSync(password, user.password_hash);
  if (!passwordMatches) {
    return res.status(401).json({ error: 'Credenciais inválidas.' });
  }

  const token = jwt.sign(
    { sub: user.id, username: user.username },
    JWT_SECRET,
    { expiresIn: TOKEN_EXPIRES_IN }
  );

  res.cookie('token', token, {
    httpOnly: true,               // não acessível via JavaScript no browser (mitiga XSS)
    sameSite: 'lax',               // mitigação básica contra CSRF
    secure: process.env.NODE_ENV === 'production', // exige HTTPS em produção
    maxAge: 2 * 60 * 60 * 1000    // 2 horas, em ms
  });

  return res.json({ id: user.id, username: user.username });
});

// POST /api/auth/logout — remove o cookie de sessão
router.post('/logout', (_req, res) => {
  res.clearCookie('token');
  return res.json({ message: 'Logout realizado com sucesso.' });
});

// GET /api/auth/me — retorna o usuário autenticado atual (se houver)
router.get('/me', requireAuth, (req, res) => {
  return res.json({ id: req.user.id, username: req.user.username });
});

module.exports = router;
```

---

### `src/routes/recordRoutes.js`

```javascript
// src/routes/recordRoutes.js
// CRUD de "registros". Listagem é pública; criação/edição/remoção exigem autenticação.
const express = require('express');
const db = require('../db');
const { requireAuth } = require('../middleware/auth');

const router = express.Router();

// GET /api/records — pública, qualquer visitante pode listar
router.get('/', (_req, res) => {
  const records = db
    .prepare(
      `SELECT records.id, records.title, records.description,
              records.created_at, records.updated_at,
              users.username AS created_by
       FROM records
       LEFT JOIN users ON users.id = records.created_by
       ORDER BY records.id DESC`
    )
    .all();
  res.json(records);
});

// GET /api/records/:id — pública, detalhe de um registro
router.get('/:id', (req, res) => {
  const record = db
    .prepare(
      `SELECT records.id, records.title, records.description,
              records.created_at, records.updated_at,
              users.username AS created_by
       FROM records
       LEFT JOIN users ON users.id = records.created_by
       WHERE records.id = ?`
    )
    .get(req.params.id);

  if (!record) {
    return res.status(404).json({ error: 'Registro não encontrado.' });
  }
  res.json(record);
});

// POST /api/records — protegida
router.post('/', requireAuth, (req, res) => {
  const { title, description } = req.body || {};

  if (typeof title !== 'string' || title.trim().length === 0) {
    return res.status(400).json({ error: 'O campo "title" é obrigatório.' });
  }

  const info = db
    .prepare('INSERT INTO records (title, description, created_by) VALUES (?, ?, ?)')
    .run(title.trim(), description || null, req.user.id);

  const created = db.prepare('SELECT * FROM records WHERE id = ?').get(info.lastInsertRowid);
  res.status(201).json(created);
});

// PUT /api/records/:id — protegida
router.put('/:id', requireAuth, (req, res) => {
  const { title, description } = req.body || {};
  const record = db.prepare('SELECT * FROM records WHERE id = ?').get(req.params.id);

  if (!record) {
    return res.status(404).json({ error: 'Registro não encontrado.' });
  }

  if (typeof title !== 'string' || title.trim().length === 0) {
    return res.status(400).json({ error: 'O campo "title" é obrigatório.' });
  }

  db.prepare(
    `UPDATE records
     SET title = ?, description = ?, updated_at = datetime('now')
     WHERE id = ?`
  ).run(title.trim(), description || null, req.params.id);

  const updated = db.prepare('SELECT * FROM records WHERE id = ?').get(req.params.id);
  res.json(updated);
});

// DELETE /api/records/:id — protegida
router.delete('/:id', requireAuth, (req, res) => {
  const record = db.prepare('SELECT * FROM records WHERE id = ?').get(req.params.id);

  if (!record) {
    return res.status(404).json({ error: 'Registro não encontrado.' });
  }

  db.prepare('DELETE FROM records WHERE id = ?').run(req.params.id);
  res.json({ message: 'Registro removido com sucesso.' });
});

module.exports = router;
```

---

### `src/server.js`

```javascript
// src/server.js
// Ponto de entrada da aplicação.
require('dotenv').config();

const path = require('path');
const express = require('express');
const cookieParser = require('cookie-parser');

const authRoutes = require('./routes/authRoutes');
const recordRoutes = require('./routes/recordRoutes');

// Garante que o banco/tabelas sejam inicializados ao subir o servidor
require('./db');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(cookieParser());

// Arquivos estáticos do front-end
app.use(express.static(path.join(__dirname, '..', 'public')));

// Rotas da API
app.use('/api/auth', authRoutes);
app.use('/api/records', recordRoutes);

// Tratamento de erro genérico (fallback)
app.use((err, _req, res, _next) => {
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
    <div id="auth-status">Carregando...</div>
  </header>

  <main>
    <!-- Seção de autenticação -->
    <section id="auth-section">
      <div class="cards">
        <div class="card">
          <h2>Login</h2>
          <form id="login-form">
            <input type="text" name="username" placeholder="Usuário" required />
            <input type="password" name="password" placeholder="Senha" required />
            <button type="submit">Entrar</button>
          </form>
        </div>

        <div class="card">
          <h2>Criar conta</h2>
          <form id="register-form">
            <input type="text" name="username" placeholder="Usuário (mín. 3 caracteres)" required />
            <input type="password" name="password" placeholder="Senha (mín. 6 caracteres)" required />
            <button type="submit">Cadastrar</button>
          </form>
        </div>
      </div>
      <p id="auth-message"></p>
    </section>

    <!-- Seção de criação/edição de registros (apenas autenticado) -->
    <section id="record-form-section" class="hidden">
      <h2 id="form-title">Novo Registro</h2>
      <form id="record-form">
        <input type="hidden" name="id" />
        <input type="text" name="title" placeholder="Título" required />
        <textarea name="description" placeholder="Descrição"></textarea>
        <button type="submit">Salvar</button>
        <button type="button" id="cancel-edit" class="hidden">Cancelar edição</button>
      </form>
      <p id="record-message"></p>
    </section>

    <!-- Listagem pública -->
    <section>
      <h2>Registros cadastrados</h2>
      <table id="records-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Título</th>
            <th>Descrição</th>
            <th>Criado por</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </section>
  </main>

  <script src="app.js"></script>
</body>
</html>
```

---

### `public/style.css`

```css
* { box-sizing: border-box; font-family: Arial, Helvetica, sans-serif; }
body { margin: 0; background: #f4f5f7; color: #222; }
header {
  background: #2b2d42;
  color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
main { padding: 2rem; max-width: 900px; margin: 0 auto; }
.cards { display: flex; gap: 1rem; flex-wrap: wrap; }
.card {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.15);
  flex: 1;
  min-width: 250px;
}
form { display: flex; flex-direction: column; gap: 0.5rem; }
input, textarea, button {
  padding: 0.5rem;
  border-radius: 4px;
  border: 1px solid #ccc;
  font-size: 1rem;
}
button {
  background: #2b2d42;
  color: white;
  border: none;
  cursor: pointer;
}
button:hover { background: #1b1d30; }
.hidden { display: none !important; }
table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  margin-top: 1rem;
}
th, td {
  border: 1px solid #ddd;
  padding: 0.5rem;
  text-align: left;
  font-size: 0.9rem;
}
th { background: #eee; }
#auth-message, #record-message { color: #b00020; font-weight: bold; }
```

---

### `public/app.js`

```javascript
// public/app.js
// Front-end simples (sem frameworks) consumindo a API via fetch.
// O cookie httpOnly de sessão é enviado automaticamente (credentials: 'include').

const authStatusEl = document.getElementById('auth-status');
const authSection = document.getElementById('auth-section');
const authMessageEl = document.getElementById('auth-message');
const recordFormSection = document.getElementById('record-form-section');
const recordMessageEl = document.getElementById('record-message');
const recordsTableBody = document.querySelector('#records-table tbody');
const recordForm = document.getElementById('record-form');
const formTitle = document.getElementById('form-title');
const cancelEditBtn = document.getElementById('cancel-edit');

let currentUser = null;

async function api(path, options = {}) {
  const res = await fetch(path, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    credentials: 'include'
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.error || 'Erro na requisição.');
  }
  return data;
}

// --- Autenticação ---

async function checkSession() {
  try {
    currentUser = await api('/api/auth/me');
  } catch (_e) {
    currentUser = null;
  }
  renderAuthState();
}

function renderAuthState() {
  if (currentUser) {
    authStatusEl.innerHTML = `Logado como <b>${currentUser.username}</b> <button id="logout-btn">Sair</button>`;
    authSection.classList.add('hidden');
    recordFormSection.classList.remove('hidden');
    document.getElementById('logout-btn').addEventListener('click', logout);
  } else {
    authStatusEl.textContent = 'Visitante (não autenticado)';
    authSection.classList.remove('hidden');
    recordFormSection.classList.add('hidden');
  }
  renderRecordsActions();
}

document.getElementById('login-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  authMessageEl.textContent = '';
  const formData = new FormData(e.target);
  try {
    currentUser = await api('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(Object.fromEntries(formData))
    });
    e.target.reset();
    renderAuthState();
  } catch (err) {
    authMessageEl.textContent = err.message;
  }
});

document.getElementById('register-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  authMessageEl.textContent = '';
  const formData = new FormData(e.target);
  try {
    await api('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(Object.fromEntries(formData))
    });
    authMessageEl.style.color = 'green';
    authMessageEl.textContent = 'Cadastro realizado! Agora faça login.';
    e.target.reset();
  } catch (err) {
    authMessageEl.style.color = '#b00020';
    authMessageEl.textContent = err.message;
  }
});

async function logout() {
  await api('/api/auth/logout', { method: 'POST' });
  currentUser = null;
  renderAuthState();
}

// --- Registros ---

async function loadRecords() {
  const records = await api('/api/records');
  recordsTableBody.innerHTML = '';
  records.forEach((r) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${r.id}</td>
      <td>${escapeHtml(r.title)}</td>
      <td>${escapeHtml(r.description || '')}</td>
      <td>${escapeHtml(r.created_by || '-')}</td>
      <td class="actions" data-id="${r.id}"></td>
    `;
    recordsTableBody.appendChild(tr);
  });
  renderRecordsActions(records);
}

function renderRecordsActions(records) {
  if (!records) return;
  document.querySelectorAll('.actions').forEach((cell) => {
    const id = cell.dataset.id;
    const record = records.find((r) => String(r.id) === id);
    cell.innerHTML = '';
    if (currentUser && record) {
      const editBtn = document.createElement('button');
      editBtn.textContent = 'Editar';
      editBtn.onclick = () => startEdit(record);

      const delBtn = document.createElement('button');
      delBtn.textContent = 'Remover';
      delBtn.style.background = '#b00020';
      delBtn.onclick = () => removeRecord(record.id);

      cell.append(editBtn, delBtn);
    }
  });
}

function startEdit(record) {
  formTitle.textContent = `Editando registro #${record.id}`;
  recordForm.id.value = record.id;
  recordForm.title.value = record.title;
  recordForm.description.value = record.description || '';
  cancelEditBtn.classList.remove('hidden');
}

cancelEditBtn.addEventListener('click', () => {
  recordForm.reset();
  formTitle.textContent = 'Novo Registro';
  cancelEditBtn.classList.add('hidden');
});

recordForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  recordMessageEl.textContent = '';
  const formData = new FormData(recordForm);
  const payload = { title: formData.get('title'), description: formData.get('description') };
  const id = formData.get('id');

  try {
    if (id) {
      await api(`/api/records/${id}`, { method: 'PUT', body: JSON.stringify(payload) });
    } else {
      await api('/api/records', { method: 'POST', body: JSON.stringify(payload) });
    }
    recordForm.reset();
    formTitle.textContent = 'Novo Registro';
    cancelEditBtn.classList.add('hidden');
    await loadRecords();
  } catch (err) {
    recordMessageEl.textContent = err.message;
  }
});

async function removeRecord(id) {
  if (!confirm('Confirma remoção deste registro?')) return;
  try {
    await api(`/api/records/${id}`, { method: 'DELETE' });
    await loadRecords();
  } catch (err) {
    recordMessageEl.textContent = err.message;
  }
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// Inicialização
(async () => {
  await checkSession();
  await loadRecords();
})();
```

---

## Instruções de execução

### 1. Pré-requisitos
- Node.js 18+ instalado (recomendado, `better-sqlite3` compila binários nativos e funciona bem a partir dessa versão).

### 2. Instalação

```bash
# crie a pasta do projeto e coloque todos os arquivos acima na estrutura indicada
npm install
```

### 3. Configuração

```bash
cp .env.example .env
# edite o .env e defina um JWT_SECRET forte, por exemplo:
# JWT_SECRET=$(openssl rand -hex 32)
```

### 4. Rodando

```bash
npm start
# ou, para reiniciar automaticamente a cada alteração:
npm run dev
```

O servidor sobe em `http://localhost:3000`. O arquivo `data.sqlite` é criado automaticamente na raiz do projeto na primeira execução.

### 5. Uso

1. Abra `http://localhost:3000` no navegador.
2. Crie uma conta em "Criar conta".
3. Faça login em "Login" — um cookie `httpOnly` de sessão (JWT válido por 2h) será definido.
4. Com sessão ativa, use o formulário "Novo Registro" para criar, e os botões "Editar"/"Remover" na tabela para gerenciar registros.
5. Sem estar logado, a listagem de registros continua visível (rota pública), mas as ações de criar/editar/remover ficam indisponíveis e a API retorna `401` se forem chamadas diretamente.

### 6. Endpoints da API (referência)

| Método | Rota                  | Acesso        | Descrição                     |
|--------|-----------------------|---------------|--------------------------------|
| POST   | /api/auth/register    | Público       | Cria usuário (senha hasheada)  |
| POST   | /api/auth/login       | Público       | Autentica e define cookie JWT  |
| POST   | /api/auth/logout      | Público       | Remove cookie de sessão        |
| GET    | /api/auth/me          | Autenticado   | Retorna usuário logado         |
| GET    | /api/records          | Público       | Lista registros                |
| GET    | /api/records/:id      | Público       | Detalha um registro            |
| POST   | /api/records          | Autenticado   | Cria registro                  |
| PUT    | /api/records/:id      | Autenticado   | Edita registro                 |
| DELETE | /api/records/:id      | Autenticado   | Remove registro                |