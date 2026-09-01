<!--
nivel: 4 - Seguranca (autenticacao e autorizacao)
provider: claude
model: claude-sonnet-5
tentativa: 3
temperature: 0.2
timestamp: 2026-08-31T09:13:28.246Z
metadata: {"model":"claude-sonnet-5","usage":{"input_tokens":366,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"cache_creation":{"ephemeral_5m_input_tokens":0,"ephemeral_1h_input_tokens":0},"output_tokens":8073,"service_tier":"standard","inference_geo":"global","output_tokens_details":{"thinking_tokens":385}},"stop_reason":"end_turn"}
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

- **Express**: único framework usado, pois é o mínimo necessário para roteamento HTTP em Node (a tarefa não pede implementação de servidor HTTP cru).
- **better-sqlite3**: driver SQLite síncrono, simples, sem necessidade de ORM.
- **bcrypt**: gera hash + salt automaticamente (salt embutido no hash, custo configurável).
- **jsonwebtoken (JWT)**: usado como token de sessão stateless enviado via header `Authorization: Bearer <token>`. Expira em 2h.
- **Entidade de exemplo `records`**: como a tarefa fala genericamente em "cadastrar, editar, remover registros" e "listagem pública", criei uma entidade genérica `records` (título/descrição) vinculada ao usuário que criou. Listagem (`GET`) é pública; criação/edição/remoção exigem autenticação.
- **Senhas**: nunca armazenadas em texto puro, apenas o hash bcrypt.
- **Validações básicas**: campos obrigatórios, usuário único, senha mínima de 6 caracteres.
- **CORS liberado** apenas para simplificar testes locais do frontend estático.

---

## Estrutura de arquivos

```
projeto/
├── package.json
├── .env.example
├── db.js
├── auth.js
├── server.js
├── routes/
│   ├── users.js
│   └── records.js
└── public/
    ├── index.html
    └── app.js
```

---

### `package.json`

```json
{
  "name": "cadastro-auth-sqlite",
  "version": "1.0.0",
  "description": "Sistema de cadastro de usuarios com login, hash de senha, JWT e SQLite",
  "main": "server.js",
  "type": "commonjs",
  "scripts": {
    "start": "node server.js",
    "dev": "node server.js"
  },
  "dependencies": {
    "better-sqlite3": "^11.3.0",
    "bcrypt": "^5.1.1",
    "cors": "^2.8.5",
    "dotenv": "^16.4.5",
    "express": "^4.19.2",
    "jsonwebtoken": "^9.0.2"
  }
}
```

---

### `.env.example`

```env
# Copie este arquivo para ".env" e ajuste se necessario
PORT=3000
JWT_SECRET=troque-esta-chave-por-uma-bem-secreta-e-longa
JWT_EXPIRES_IN=2h
BCRYPT_SALT_ROUNDS=10
```

---

### `db.js`

```js
// db.js
// Responsavel por inicializar o banco SQLite e criar as tabelas necessarias.
// Usamos better-sqlite3: driver sincrono, simples e rapido para apps pequenas/medias.

const Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, 'data.sqlite');
const db = new Database(dbPath);

// Ativa chaves estrangeiras (desligado por padrao no SQLite)
db.pragma('foreign_keys = ON');

// Tabela de usuarios
db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
  );
`);

// Tabela de registros (entidade generica de exemplo, ligada ao usuario que criou)
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

### `auth.js`

```js
// auth.js
// Middleware e utilitarios de autenticacao baseados em JWT.
// Decisao: JWT (stateless) evita a necessidade de tabela de sessoes no banco,
// simplificando a implementacao mantendo seguranca adequada.

const jwt = require('jsonwebtoken');
require('dotenv').config();

const JWT_SECRET = process.env.JWT_SECRET || 'chave-padrao-insegura-trocar-em-producao';
const JWT_EXPIRES_IN = process.env.JWT_EXPIRES_IN || '2h';

function generateToken(user) {
  // Payload minimo: id e username. Nunca incluir senha/hash no token.
  return jwt.sign(
    { id: user.id, username: user.username },
    JWT_SECRET,
    { expiresIn: JWT_EXPIRES_IN }
  );
}

function authMiddleware(req, res, next) {
  const authHeader = req.headers['authorization'];

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Token de autenticacao ausente.' });
  }

  const token = authHeader.split(' ')[1];

  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    req.user = decoded; // { id, username, iat, exp }
    next();
  } catch (err) {
    return res.status(401).json({ error: 'Token invalido ou expirado.' });
  }
}

module.exports = { generateToken, authMiddleware, JWT_SECRET };
```

---

### `routes/users.js`

```js
// routes/users.js
// Rotas de cadastro de usuario e login.

const express = require('express');
const bcrypt = require('bcrypt');
const db = require('../db');
const { generateToken } = require('../auth');

require('dotenv').config();

const router = express.Router();
const SALT_ROUNDS = parseInt(process.env.BCRYPT_SALT_ROUNDS || '10', 10);

// Cadastro de novo usuario (rota publica: qualquer um pode criar sua conta)
router.post('/register', async (req, res) => {
  const { username, password } = req.body;

  if (!username || !password) {
    return res.status(400).json({ error: 'Usuario e senha sao obrigatorios.' });
  }

  if (typeof password !== 'string' || password.length < 6) {
    return res.status(400).json({ error: 'A senha deve ter no minimo 6 caracteres.' });
  }

  const existing = db.prepare('SELECT id FROM users WHERE username = ?').get(username);
  if (existing) {
    return res.status(409).json({ error: 'Nome de usuario ja esta em uso.' });
  }

  try {
    // bcrypt.hash gera o salt automaticamente e o embute no hash resultante
    const passwordHash = await bcrypt.hash(password, SALT_ROUNDS);

    const info = db
      .prepare('INSERT INTO users (username, password_hash) VALUES (?, ?)')
      .run(username, passwordHash);

    const user = { id: info.lastInsertRowid, username };
    const token = generateToken(user);

    return res.status(201).json({ user, token });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: 'Erro interno ao criar usuario.' });
  }
});

// Login
router.post('/login', async (req, res) => {
  const { username, password } = req.body;

  if (!username || !password) {
    return res.status(400).json({ error: 'Usuario e senha sao obrigatorios.' });
  }

  const user = db.prepare('SELECT * FROM users WHERE username = ?').get(username);

  // Mensagem generica para nao revelar se o usuario existe ou nao
  if (!user) {
    return res.status(401).json({ error: 'Credenciais invalidas.' });
  }

  const passwordMatches = await bcrypt.compare(password, user.password_hash);
  if (!passwordMatches) {
    return res.status(401).json({ error: 'Credenciais invalidas.' });
  }

  const token = generateToken(user);
  return res.json({ user: { id: user.id, username: user.username }, token });
});

module.exports = router;
```

---

### `routes/records.js`

```js
// routes/records.js
// CRUD de "registros" - entidade generica de exemplo.
// Regra de negocio exigida:
//  - Listagem (GET) e publica, nao exige autenticacao.
//  - Criar (POST), editar (PUT) e remover (DELETE) exigem usuario autenticado.

const express = require('express');
const db = require('../db');
const { authMiddleware } = require('../auth');

const router = express.Router();

// Listagem publica
router.get('/', (req, res) => {
  const records = db
    .prepare(
      `SELECT records.id, records.title, records.description,
              records.created_at, records.updated_at,
              users.username AS owner
       FROM records
       JOIN users ON users.id = records.owner_id
       ORDER BY records.id DESC`
    )
    .all();

  res.json(records);
});

// Detalhe publico (util para telas de edicao tambem)
router.get('/:id', (req, res) => {
  const record = db
    .prepare(
      `SELECT records.id, records.title, records.description,
              records.created_at, records.updated_at,
              users.username AS owner, records.owner_id
       FROM records
       JOIN users ON users.id = records.owner_id
       WHERE records.id = ?`
    )
    .get(req.params.id);

  if (!record) {
    return res.status(404).json({ error: 'Registro nao encontrado.' });
  }

  res.json(record);
});

// A partir daqui, todas as rotas exigem autenticacao
router.use(authMiddleware);

// Criar registro
router.post('/', (req, res) => {
  const { title, description } = req.body;

  if (!title) {
    return res.status(400).json({ error: 'O campo "title" e obrigatorio.' });
  }

  const info = db
    .prepare('INSERT INTO records (title, description, owner_id) VALUES (?, ?, ?)')
    .run(title, description || null, req.user.id);

  const created = db.prepare('SELECT * FROM records WHERE id = ?').get(info.lastInsertRowid);
  res.status(201).json(created);
});

// Editar registro
// Decisao: apenas o dono do registro pode editar/remover (autorizacao adicional razoavel).
router.put('/:id', (req, res) => {
  const { title, description } = req.body;
  const record = db.prepare('SELECT * FROM records WHERE id = ?').get(req.params.id);

  if (!record) {
    return res.status(404).json({ error: 'Registro nao encontrado.' });
  }

  if (record.owner_id !== req.user.id) {
    return res.status(403).json({ error: 'Voce nao tem permissao para editar este registro.' });
  }

  const newTitle = title !== undefined ? title : record.title;
  const newDescription = description !== undefined ? description : record.description;

  db.prepare(
    `UPDATE records
     SET title = ?, description = ?, updated_at = datetime('now')
     WHERE id = ?`
  ).run(newTitle, newDescription, req.params.id);

  const updated = db.prepare('SELECT * FROM records WHERE id = ?').get(req.params.id);
  res.json(updated);
});

// Remover registro
router.delete('/:id', (req, res) => {
  const record = db.prepare('SELECT * FROM records WHERE id = ?').get(req.params.id);

  if (!record) {
    return res.status(404).json({ error: 'Registro nao encontrado.' });
  }

  if (record.owner_id !== req.user.id) {
    return res.status(403).json({ error: 'Voce nao tem permissao para remover este registro.' });
  }

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
const cors = require('cors');
const path = require('path');

const usersRoutes = require('./routes/users');
const recordsRoutes = require('./routes/records');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors()); // liberado para facilitar testes locais do frontend estatico
app.use(express.json());

// Frontend estatico simples para testar o fluxo (login/cadastro/listagem)
app.use(express.static(path.join(__dirname, 'public')));

// Rotas da API
app.use('/api/auth', usersRoutes);       // /api/auth/register  /api/auth/login
app.use('/api/records', recordsRoutes);  // CRUD dos registros

// Tratamento simples de rota nao encontrada
app.use((req, res) => {
  res.status(404).json({ error: 'Rota nao encontrada.' });
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
<title>Cadastro com Autenticacao</title>
<style>
  body { font-family: Arial, sans-serif; max-width: 700px; margin: 40px auto; }
  fieldset { margin-bottom: 20px; }
  input { display: block; margin: 5px 0; padding: 5px; width: 100%; box-sizing: border-box; }
  button { margin-top: 8px; padding: 6px 12px; }
  #records li { margin-bottom: 8px; border-bottom: 1px solid #ccc; padding-bottom: 8px; }
  .msg { color: red; }
  .ok { color: green; }
</style>
</head>
<body>
  <h1>Sistema de Cadastro</h1>

  <fieldset>
    <legend>Registrar novo usuario</legend>
    <input id="reg-username" placeholder="Usuario" />
    <input id="reg-password" type="password" placeholder="Senha (min 6 caracteres)" />
    <button onclick="register()">Registrar</button>
  </fieldset>

  <fieldset>
    <legend>Login</legend>
    <input id="login-username" placeholder="Usuario" />
    <input id="login-password" type="password" placeholder="Senha" />
    <button onclick="login()">Entrar</button>
    <button onclick="logout()">Sair</button>
    <p id="session-info"></p>
  </fieldset>

  <fieldset>
    <legend>Novo registro (requer login)</legend>
    <input id="rec-title" placeholder="Titulo" />
    <input id="rec-description" placeholder="Descricao" />
    <button onclick="createRecord()">Cadastrar registro</button>
  </fieldset>

  <h2>Registros (listagem publica)</h2>
  <button onclick="loadRecords()">Atualizar lista</button>
  <ul id="records"></ul>

  <p id="feedback"></p>

  <script src="app.js"></script>
</body>
</html>
```

---

### `public/app.js`

```js
// public/app.js
// Frontend minimo (sem framework) apenas para demonstrar/testar o fluxo da API.

const API = '/api';

function getToken() {
  return localStorage.getItem('token');
}

function setSession(token, username) {
  localStorage.setItem('token', token);
  localStorage.setItem('username', username);
  updateSessionInfo();
}

function clearSession() {
  localStorage.removeItem('token');
  localStorage.removeItem('username');
  updateSessionInfo();
}

function updateSessionInfo() {
  const username = localStorage.getItem('username');
  document.getElementById('session-info').innerText = username
    ? `Logado como: ${username}`
    : 'Nao autenticado.';
}

function showFeedback(msg, isError = true) {
  const el = document.getElementById('feedback');
  el.innerText = msg;
  el.className = isError ? 'msg' : 'ok';
}

async function register() {
  const username = document.getElementById('reg-username').value;
  const password = document.getElementById('reg-password').value;

  const res = await fetch(`${API}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  const data = await res.json();

  if (!res.ok) return showFeedback(data.error || 'Erro ao registrar.');

  setSession(data.token, data.user.username);
  showFeedback('Usuario registrado e logado com sucesso!', false);
}

async function login() {
  const username = document.getElementById('login-username').value;
  const password = document.getElementById('login-password').value;

  const res = await fetch(`${API}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  const data = await res.json();

  if (!res.ok) return showFeedback(data.error || 'Erro ao logar.');

  setSession(data.token, data.user.username);
  showFeedback('Login realizado com sucesso!', false);
}

function logout() {
  clearSession();
  showFeedback('Sessao encerrada.', false);
}

async function createRecord() {
  const title = document.getElementById('rec-title').value;
  const description = document.getElementById('rec-description').value;
  const token = getToken();

  if (!token) return showFeedback('Voce precisa estar logado para cadastrar.');

  const res = await fetch(`${API}/records`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ title, description })
  });
  const data = await res.json();

  if (!res.ok) return showFeedback(data.error || 'Erro ao criar registro.');

  showFeedback('Registro criado com sucesso!', false);
  loadRecords();
}

async function loadRecords() {
  const res = await fetch(`${API}/records`);
  const data = await res.json();

  const list = document.getElementById('records');
  list.innerHTML = '';

  data.forEach(r => {
    const li = document.createElement('li');
    li.innerHTML = `
      <strong>${r.title}</strong> (por ${r.owner})<br/>
      ${r.description || ''}
      <br/>
      <button onclick="deleteRecord(${r.id})">Remover</button>
    `;
    list.appendChild(li);
  });
}

async function deleteRecord(id) {
  const token = getToken();
  if (!token) return showFeedback('Voce precisa estar logado para remover.');

  const res = await fetch(`${API}/records/${id}`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` }
  });

  if (res.status === 204) {
    showFeedback('Registro removido.', false);
    loadRecords();
  } else {
    const data = await res.json();
    showFeedback(data.error || 'Erro ao remover.');
  }
}

updateSessionInfo();
loadRecords();
```

---

## Como executar

### 1. Pré-requisitos
- Node.js versão 18 ou superior instalado.

### 2. Instalar dependências
```bash
npm install
```

### 3. Configurar variáveis de ambiente
```bash
cp .env.example .env
# edite o .env e troque JWT_SECRET por um valor seguro
```

### 4. Rodar o servidor
```bash
npm start
```

O servidor iniciará em `http://localhost:3000` e criará automaticamente o arquivo `data.sqlite` na primeira execução.

### 5. Testar
Abra `http://localhost:3000` no navegador para usar a interface simples de teste, ou use `curl`/Postman:

```bash
# Registrar usuário
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"joao","password":"123456"}'

# Login
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"joao","password":"123456"}'

# Listar registros (publico, sem token)
curl http://localhost:3000/api/records

# Criar registro (autenticado)
curl -X POST http://localhost:3000/api/records \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -d '{"title":"Meu registro","description":"Teste"}'

# Editar registro
curl -X PUT http://localhost:3000/api/records/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -d '{"title":"Titulo atualizado"}'

# Remover registro
curl -X DELETE http://localhost:3000/api/records/1 \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

---

## Resumo de segurança implementada
- Senhas nunca armazenadas em texto puro (bcrypt com salt embutido, custo configurável).
- Autenticação via JWT assinado com segredo configurável e expiração.
- Autorização: apenas o dono de um registro pode editá-lo/removê-lo.
- Listagem e detalhe de registros são públicos, conforme especificado.
- Validações básicas de entrada em todas as rotas.