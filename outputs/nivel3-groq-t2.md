<!--
nivel: 3 - Sistema web full-stack
provider: groq
model: openai/gpt-oss-120b
tentativa: 2
temperature: 0.2
timestamp: 2026-08-27T19:00:20.086Z
metadata: {"model":"openai/gpt-oss-120b","usage":{"queue_time":0.224163602,"prompt_tokens":251,"prompt_time":0.012537141,"completion_tokens":3996,"completion_time":8.810275888,"total_tokens":4247,"total_time":8.822813029,"completion_tokens_details":{"reasoning_tokens":58}},"finish_reason":"stop"}
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

**Projeto:** `user‑registry`  
**Descrição:** Sistema web completo (frontend + backend) para cadastro de usuários. O backend expõe uma API REST que persiste os dados em SQLite e o frontend (HTML + JS) consome essa API para listar, criar, editar e remover usuários.

---

## Estrutura de pastas

```
user-registry/
├─ package.json
├─ server.js
├─ db.js
├─ public/
│  ├─ index.html
│  ├─ app.js
│  └─ style.css
```

---

## 1. `package.json`  
Define as dependências e o script de inicialização.

```json
{
  "name": "user-registry",
  "version": "1.0.0",
  "description": "Sistema web completo (frontend + backend) para cadastro de usuários com SQLite",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "author": "Seu Nome",
  "license": "MIT",
  "dependencies": {
    "express": "^4.18.2",
    "sqlite3": "^5.1.6",
    "cors": "^2.8.5",
    "body-parser": "^1.20.2"
  }
}
```

---

## 2. `db.js`  
Módulo responsável por criar a conexão SQLite e prover funções CRUD.

```javascript
// db.js
// ----------
// Conexão com SQLite e funções de acesso ao banco.
// Não usamos nenhum ORM para manter o projeto o mais simples possível.

const path = require('path');
const sqlite3 = require('sqlite3').verbose();

// O arquivo DB será criado na raiz do projeto.
const DB_PATH = path.resolve(__dirname, 'users.db');

const db = new sqlite3.Database(DB_PATH, (err) => {
  if (err) {
    console.error('Erro ao conectar ao SQLite:', err.message);
    process.exit(1);
  }
  console.log('Conectado ao SQLite em', DB_PATH);
});

// Cria a tabela "users" caso ainda não exista.
db.serialize(() => {
  db.run(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      email TEXT NOT NULL UNIQUE,
      age INTEGER
    )
  `);
});

/**
 * Lista todos os usuários.
 * @returns {Promise<Array>}
 */
function listUsers() {
  return new Promise((resolve, reject) => {
    db.all('SELECT * FROM users ORDER BY id DESC', [], (err, rows) => {
      if (err) reject(err);
      else resolve(rows);
    });
  });
}

/**
 * Busca um usuário por ID.
 * @param {number} id
 * @returns {Promise<Object>}
 */
function getUser(id) {
  return new Promise((resolve, reject) => {
    db.get('SELECT * FROM users WHERE id = ?', [id], (err, row) => {
      if (err) reject(err);
      else resolve(row);
    });
  });
}

/**
 * Cria um novo usuário.
 * @param {{name:string,email:string,age:number}} user
 * @returns {Promise<Object>} usuário criado (com id)
 */
function createUser(user) {
  const { name, email, age } = user;
  return new Promise((resolve, reject) => {
    const stmt = db.prepare(
      'INSERT INTO users (name, email, age) VALUES (?, ?, ?)'
    );
    stmt.run([name, email, age || null], function (err) {
      if (err) reject(err);
      else resolve({ id: this.lastID, name, email, age });
    });
    stmt.finalize();
  });
}

/**
 * Atualiza um usuário existente.
 * @param {number} id
 * @param {{name:string,email:string,age:number}} user
 * @returns {Promise<void>}
 */
function updateUser(id, user) {
  const { name, email, age } = user;
  return new Promise((resolve, reject) => {
    const stmt = db.prepare(
      'UPDATE users SET name = ?, email = ?, age = ? WHERE id = ?'
    );
    stmt.run([name, email, age || null, id], function (err) {
      if (err) reject(err);
      else resolve();
    });
    stmt.finalize();
  });
}

/**
 * Remove um usuário.
 * @param {number} id
 * @returns {Promise<void>}
 */
function deleteUser(id) {
  return new Promise((resolve, reject) => {
    db.run('DELETE FROM users WHERE id = ?', [id], function (err) {
      if (err) reject(err);
      else resolve();
    });
  });
}

// Exporta as funções para uso no server.
module.exports = {
  listUsers,
  getUser,
  createUser,
  updateUser,
  deleteUser,
};
```

---

## 3. `server.js`  
API REST + servidor estático que serve a pasta `public`.

```javascript
// server.js
// ----------
// Entrypoint da aplicação. Configura o Express, CORS, body‑parser
// e define as rotas da API.

const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');

const db = require('./db');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());                     // Permite chamadas do frontend
app.use(bodyParser.json());          // Parseia JSON no body das requisições
app.use(express.static(path.join(__dirname, 'public'))); // Arquivos estáticos

// ---------- API REST ----------

// GET /api/users      -> lista todos
app.get('/api/users', async (req, res) => {
  try {
    const users = await db.listUsers();
    res.json(users);
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: 'Erro ao listar usuários' });
  }
});

// GET /api/users/:id  -> busca por ID
app.get('/api/users/:id', async (req, res) => {
  try {
    const user = await db.getUser(req.params.id);
    if (!user) return res.status(404).json({ error: 'Usuário não encontrado' });
    res.json(user);
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: 'Erro ao buscar usuário' });
  }
});

// POST /api/users    -> cria novo
app.post('/api/users', async (req, res) => {
  const { name, email, age } = req.body;
  if (!name || !email) {
    return res.status(400).json({ error: 'Nome e e‑mail são obrigatórios' });
  }
  try {
    const user = await db.createUser({ name, email, age });
    res.status(201).json(user);
  } catch (e) {
    console.error(e);
    // Erro de UNIQUE constraint (email duplicado)
    if (e.code === 'SQLITE_CONSTRAINT') {
      return res.status(409).json({ error: 'E‑mail já cadastrado' });
    }
    res.status(500).json({ error: 'Erro ao criar usuário' });
  }
});

// PUT /api/users/:id -> atualiza
app.put('/api/users/:id', async (req, res) => {
  const { name, email, age } = req.body;
  if (!name || !email) {
    return res.status(400).json({ error: 'Nome e e‑mail são obrigatórios' });
  }
  try {
    const existing = await db.getUser(req.params.id);
    if (!existing) return res.status(404).json({ error: 'Usuário não encontrado' });

    await db.updateUser(req.params.id, { name, email, age });
    const updated = await db.getUser(req.params.id);
    res.json(updated);
  } catch (e) {
    console.error(e);
    if (e.code === 'SQLITE_CONSTRAINT') {
      return res.status(409).json({ error: 'E‑mail já cadastrado' });
    }
    res.status(500).json({ error: 'Erro ao atualizar usuário' });
  }
});

// DELETE /api/users/:id -> remove
app.delete('/api/users/:id', async (req, res) => {
  try {
    const existing = await db.getUser(req.params.id);
    if (!existing) return res.status(404).json({ error: 'Usuário não encontrado' });

    await db.deleteUser(req.params.id);
    res.status(204).end(); // No Content
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: 'Erro ao remover usuário' });
  }
});

// Fallback: serve index.html para rotas não encontradas (SPA)
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Inicia o servidor
app.listen(PORT, () => {
  console.log(`Servidor rodando em http://localhost:${PORT}`);
});
```

---

## 4. Frontend

### 4.1 `public/index.html`

```html
<!-- public/index.html -->
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Cadastro de Usuários</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <h1>Cadastro de Usuários</h1>

  <section id="form-section">
    <h2 id="form-title">Novo Usuário</h2>
    <form id="user-form">
      <input type="hidden" id="user-id" />
      <div class="field">
        <label for="name">Nome:</label>
        <input type="text" id="name" required />
      </div>
      <div class="field">
        <label for="email">E‑mail:</label>
        <input type="email" id="email" required />
      </div>
      <div class="field">
        <label for="age">Idade:</label>
        <input type="number" id="age" min="0" />
      </div>
      <button type="submit" id="submit-btn">Salvar</button>
      <button type="button" id="cancel-btn" class="hidden">Cancelar</button>
    </form>
  </section>

  <section id="list-section">
    <h2>Lista de Usuários</h2>
    <table id="users-table">
      <thead>
        <tr>
          <th>ID</th><th>Nome</th><th>E‑mail</th><th>Idade</th><th>Ações</th>
        </tr>
      </thead>
      <tbody></tbody>
    </table>
  </section>

  <script src="app.js"></script>
</body>
</html>
```

### 4.2 `public/style.css`

```css
/* public/style.css */
body {
  font-family: Arial, Helvetica, sans-serif;
  margin: 20px;
  background: #f7f7f7;
}
h1, h2 {
  color: #333;
}
section {
  margin-bottom: 30px;
  background: #fff;
  padding: 15px;
  border-radius: 5px;
  box-shadow: 0 0 5px rgba(0,0,0,0.1);
}
.field {
  margin-bottom: 10px;
}
label {
  display: inline-block;
  width: 80px;
}
input[type="text"],
input[type="email"],
input[type="number"] {
  width: 200px;
  padding: 5px;
}
button {
  padding: 6px 12px;
  margin-right: 5px;
  cursor: pointer;
}
button.hidden {
  display: none;
}
table {
  width: 100%;
  border-collapse: collapse;
}
th, td {
  padding: 8px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}
tr:hover {
  background: #f1f1f1;
}
.action-btn {
  margin-right: 5px;
}
```

### 4.3 `public/app.js`

```javascript
// public/app.js
// ----------
// Código cliente que consome a API REST.
// Usa fetch() nativo do navegador; não depende de bibliotecas externas.

const API_URL = '/api/users';

// Elements
const usersTableBody = document.querySelector('#users-table tbody');
const form = document.getElementById('user-form');
const formTitle = document.getElementById('form-title');
const submitBtn = document.getElementById('submit-btn');
const cancelBtn = document.getElementById('cancel-btn');

const inputId = document.getElementById('user-id');
const inputName = document.getElementById('name');
const inputEmail = document.getElementById('email');
const inputAge = document.getElementById('age');

// ---------- Helpers ----------
function clearForm() {
  inputId.value = '';
  inputName.value = '';
  inputEmail.value = '';
  inputAge.value = '';
  formTitle.textContent = 'Novo Usuário';
  submitBtn.textContent = 'Salvar';
  cancelBtn.classList.add('hidden');
}

function populateForm(user) {
  inputId.value = user.id;
  inputName.value = user.name;
  inputEmail.value = user.email;
  inputAge.value = user.age ?? '';
  formTitle.textContent = `Editar Usuário #${user.id}`;
  submitBtn.textContent = 'Atualizar';
  cancelBtn.classList.remove('hidden');
}

// ---------- API Calls ----------
async function fetchUsers() {
  const resp = await fetch(API_URL);
  const data = await resp.json();
  return data;
}

async function createUser(user) {
  const resp = await fetch(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(user),
  });
  if (!resp.ok) throw await resp.json();
  return await resp.json();
}

async function updateUser(id, user) {
  const resp = await fetch(`${API_URL}/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(user),
  });
  if (!resp.ok) throw await resp.json();
  return await resp.json();
}

async function deleteUser(id) {
  const resp = await fetch(`${API_URL}/${id}`, { method: 'DELETE' });
  if (!resp.ok) throw await resp.json();
}

// ---------- UI ----------
function renderTable(users) {
  usersTableBody.innerHTML = '';
  users.forEach((u) => {
    const tr = document.createElement('tr');

    tr.innerHTML = `
      <td>${u.id}</td>
      <td>${u.name}</td>
      <td>${u.email}</td>
      <td>${u.age ?? ''}</td>
      <td>
        <button class="action-btn edit-btn" data-id="${u.id}">Editar</button>
        <button class="action-btn del-btn" data-id="${u.id}">Remover</button>
      </td>
    `;
    usersTableBody.appendChild(tr);
  });
}

// Load and render list on page load
async function loadAndRender() {
  try {
    const users = await fetchUsers();
    renderTable(users);
  } catch (e) {
    alert('Erro ao carregar usuários');
    console.error(e);
  }
}

// ---------- Event Listeners ----------
form.addEventListener('submit', async (e) => {
  e.preventDefault();

  const user = {
    name: inputName.value.trim(),
    email: inputEmail.value.trim(),
    age: inputAge.value ? Number(inputAge.value) : null,
  };

  try {
    if (inputId.value) {
      // Update
      await updateUser(inputId.value, user);
    } else {
      // Create
      await createUser(user);
    }
    clearForm();
    await loadAndRender();
  } catch (err) {
    alert(err.error || 'Erro na operação');
    console.error(err);
  }
});

cancelBtn.addEventListener('click', (e) => {
  clearForm();
});

usersTableBody.addEventListener('click', async (e) => {
  const target = e.target;
  if (target.classList.contains('edit-btn')) {
    const id = target.dataset.id;
    const resp = await fetch(`${API_URL}/${id}`);
    const user = await resp.json();
    populateForm(user);
  } else if (target.classList.contains('del-btn')) {
    if (confirm('Tem certeza que deseja remover este usuário?')) {
      const id = target.dataset.id;
      try {
        await deleteUser(id);
        await loadAndRender();
      } catch (err) {
        alert(err.error || 'Erro ao remover');
        console.error(err);
      }
    }
  }
});

// Inicializa
loadAndRender();
```

---

## 5. Instruções de execução

### Pré‑requisitos
- **Node.js** (versão 14 ou superior) e **npm** instalados.

### Passos

```bash
# 1. Clonar ou copiar o projeto para uma pasta
git clone <repo‑url> user-registry   # (ou simplesmente criar a pasta)

# 2. Entrar no diretório
cd user-registry

# 3. Instalar as dependências
npm install

# 4. Iniciar o servidor
npm start
```

O servidor iniciará em **http://localhost:3000**.  
Ao abrir essa URL no navegador você verá a interface para listar, cadastrar, editar e remover usuários. Todos os dados são armazenados no arquivo SQLite `users.db` criado automaticamente na raiz do projeto.

### Desenvolvimento

- Para reiniciar o servidor automaticamente ao mudar código, instale `nodemon` globalmente (`npm i -g nodemon`) e rode `nodemon server.js`.
- O banco pode ser inspecionado com qualquer cliente SQLite, pois o arquivo `users.db` está na raiz.

---

**Pronto!** 🎉  
Todo o código necessário está acima e pode ser colocado nos respectivos arquivos. Basta seguir as instruções de instalação e o sistema estará operacional.