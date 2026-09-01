<!--
nivel: 3 - Sistema web full-stack
provider: groq
model: openai/gpt-oss-120b
tentativa: 1
temperature: 0.2
timestamp: 2026-08-27T18:59:41.944Z
metadata: {"model":"openai/gpt-oss-120b","usage":{"queue_time":0.245314287,"prompt_tokens":251,"prompt_time":0.011237536,"completion_tokens":3950,"completion_time":8.263513325,"total_tokens":4201,"total_time":8.274750861,"completion_tokens_details":{"reasoning_tokens":60}},"finish_reason":"stop"}
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
**Linguagem:** Node.js (JavaScript)  
**Banco:** SQLite (arquivo `data.db`)  
**Web server:** Express (mínimo necessário)  
**Frontend:** HTML + CSS + Vanilla JS (usa `fetch` para chamar a API REST)  

---  

## 1. Estrutura de diretórios

```
user-registry/
│
├─ package.json
├─ server.js
├─ db.js
│
├─ public/
│   ├─ index.html
│   ├─ app.js
│   └─ style.css
│
└─ data.db            (gerado automaticamente na primeira execução)
```

---  

## 2. Arquivo **package.json**

```json
{
  "name": "user-registry",
  "version": "1.0.0",
  "description": "Sistema web completo (frontend + backend) para cadastro de usuários com persistência em SQLite.",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "author": "Seu Nome",
  "license": "MIT",
  "dependencies": {
    "express": "^4.18.2",
    "sqlite3": "^5.1.6"
  }
}
```

> **Observação:** Apenas `express` e `sqlite3` são usados, que são os frameworks estritamente necessários.

---  

## 3. Arquivo **db.js** – camada de acesso ao SQLite

```js
// db.js
// ----------
// Responsável por criar a conexão com o SQLite, garantir que a tabela
// "users" exista e expor funções CRUD usadas pelo servidor HTTP.

const sqlite3 = require('sqlite3').verbose();
const path = require('path');

// O banco será criado (ou aberto) no mesmo diretório do projeto.
const DB_PATH = path.join(__dirname, 'data.db');
const db = new sqlite3.Database(DB_PATH, (err) => {
  if (err) {
    console.error('Erro ao abrir o banco de dados:', err.message);
    process.exit(1);
  }
  console.log('Conectado ao SQLite em', DB_PATH);
});

// Cria a tabela se ainda não existir.
const init = () => {
  const sql = `
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      email TEXT NOT NULL UNIQUE,
      age INTEGER
    )
  `;
  db.run(sql, (err) => {
    if (err) {
      console.error('Erro ao criar tabela "users":', err.message);
    } else {
      console.log('Tabela "users" pronta.');
    }
  });
};

// --------- CRUD ----------
const getAll = (callback) => {
  db.all('SELECT * FROM users ORDER BY id DESC', [], callback);
};

const getById = (id, callback) => {
  db.get('SELECT * FROM users WHERE id = ?', [id], callback);
};

const create = (user, callback) => {
  const { name, email, age } = user;
  const sql = 'INSERT INTO users (name, email, age) VALUES (?, ?, ?)';
  db.run(sql, [name, email, age], function (err) {
    callback(err, this ? this.lastID : null);
  });
};

const update = (id, user, callback) => {
  const { name, email, age } = user;
  const sql = 'UPDATE users SET name = ?, email = ?, age = ? WHERE id = ?';
  db.run(sql, [name, email, age, id], function (err) {
    callback(err, this ? this.changes : null);
  });
};

const remove = (id, callback) => {
  const sql = 'DELETE FROM users WHERE id = ?';
  db.run(sql, [id], function (err) {
    callback(err, this ? this.changes : null);
  });
};

module.exports = {
  init,
  getAll,
  getById,
  create,
  update,
  remove,
};
```

---  

## 4. Arquivo **server.js** – API REST + serviço estático

```js
// server.js
// ----------
// Entrada da aplicação. Configura o Express, serve arquivos estáticos
// (frontend) e expõe a API REST para gerenciamento de usuários.

const express = require('express');
const path = require('path');
const db = require('./db');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware para receber JSON no body
app.use(express.json());

// Servir arquivos estáticos da pasta "public"
app.use(express.static(path.join(__dirname, 'public')));

// ---------- API REST ----------
const apiRouter = express.Router();

// Lista todos os usuários
apiRouter.get('/users', (req, res) => {
  db.getAll((err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(rows);
  });
});

// Busca usuário por ID
apiRouter.get('/users/:id', (req, res) => {
  const id = Number(req.params.id);
  db.getById(id, (err, row) => {
    if (err) return res.status(500).json({ error: err.message });
    if (!row) return res.status(404).json({ error: 'Usuário não encontrado' });
    res.json(row);
  });
});

// Cria novo usuário
apiRouter.post('/users', (req, res) => {
  const { name, email, age } = req.body;
  if (!name || !email) {
    return res.status(400).json({ error: 'Nome e email são obrigatórios' });
  }
  db.create({ name, email, age }, (err, id) => {
    if (err) {
      // Erro de UNIQUE (email já existente)
      if (err.code === 'SQLITE_CONSTRAINT') {
        return res.status(409).json({ error: 'Email já cadastrado' });
      }
      return res.status(500).json({ error: err.message });
    }
    res.status(201).json({ id });
  });
});

// Atualiza usuário existente
apiRouter.put('/users/:id', (req, res) => {
  const id = Number(req.params.id);
  const { name, email, age } = req.body;
  if (!name || !email) {
    return res.status(400).json({ error: 'Nome e email são obrigatórios' });
  }
  db.update(id, { name, email, age }, (err, changes) => {
    if (err) {
      if (err.code === 'SQLITE_CONSTRAINT') {
        return res.status(409).json({ error: 'Email já cadastrado' });
      }
      return res.status(500).json({ error: err.message });
    }
    if (changes === 0) {
      return res.status(404).json({ error: 'Usuário não encontrado' });
    }
    res.json({ message: 'Usuário atualizado' });
  });
});

// Remove usuário
apiRouter.delete('/users/:id', (req, res) => {
  const id = Number(req.params.id);
  db.remove(id, (err, changes) => {
    if (err) return res.status(500).json({ error: err.message });
    if (changes === 0) {
      return res.status(404).json({ error: 'Usuário não encontrado' });
    }
    res.json({ message: 'Usuário removido' });
  });
});

// Prefixa todas as rotas da API com /api
app.use('/api', apiRouter);

// ---------- Inicialização ----------
db.init();

app.listen(PORT, () => {
  console.log(`Servidor rodando em http://localhost:${PORT}`);
});
```

---  

## 5. Arquivo **public/index.html** – Interface do usuário

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
      <div class="form-group">
        <label for="name">Nome:</label>
        <input type="text" id="name" required />
      </div>
      <div class="form-group">
        <label for="email">E‑mail:</label>
        <input type="email" id="email" required />
      </div>
      <div class="form-group">
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
    <p id="empty-msg" class="hidden">Nenhum usuário cadastrado.</p>
  </section>

  <script src="app.js"></script>
</body>
</html>
```

---  

## 6. Arquivo **public/style.css** – Estilo básico

```css
/* public/style.css */
body {
  font-family: Arial, sans-serif;
  margin: 2rem;
  background: #f7f7f7;
  color: #333;
}
h1, h2 {
  color: #2c3e50;
}
#form-section, #list-section {
  background: #fff;
  padding: 1.5rem;
  margin-bottom: 2rem;
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0,0,0,.1);
}
.form-group {
  margin-bottom: 1rem;
}
label {
  display: inline-block;
  width: 80px;
}
input[type="text"], input[type="email"], input[type="number"] {
  width: 200px;
  padding: .4rem;
}
button {
  padding: .5rem 1rem;
  margin-right: .5rem;
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
  border: 1px solid #ddd;
  padding: .5rem;
  text-align: left;
}
tr:nth-child(even) {
  background: #f2f2f2;
}
.action-btn {
  margin-right: .3rem;
  padding: .3rem .6rem;
}
#empty-msg {
  font-style: italic;
}
```

---  

## 7. Arquivo **public/app.js** – Lógica do frontend

```js
// public/app.js
// ----------
// Manipula o DOM, faz chamadas à API REST e mantém a UI sincronizada.

const API_BASE = '/api/users';

const form = document.getElementById('user-form');
const userIdInput = document.getElementById('user-id');
const nameInput = document.getElementById('name');
const emailInput = document.getElementById('email');
const ageInput = document.getElementById('age');
const formTitle = document.getElementById('form-title');
const submitBtn = document.getElementById('submit-btn');
const cancelBtn = document.getElementById('cancel-btn');

const tableBody = document.querySelector('#users-table tbody');
const emptyMsg = document.getElementById('empty-msg');

/* ------------------- Helpers ------------------- */
function clearForm() {
  userIdInput.value = '';
  nameInput.value = '';
  emailInput.value = '';
  ageInput.value = '';
  formTitle.textContent = 'Novo Usuário';
  submitBtn.textContent = 'Salvar';
  cancelBtn.classList.add('hidden');
}

function fillForm(user) {
  userIdInput.value = user.id;
  nameInput.value = user.name;
  emailInput.value = user.email;
  ageInput.value = user.age ?? '';
  formTitle.textContent = 'Editar Usuário';
  submitBtn.textContent = 'Atualizar';
  cancelBtn.classList.remove('hidden');
}

/* ------------------- API Calls ------------------- */
async function fetchUsers() {
  const resp = await fetch(API_BASE);
  if (!resp.ok) throw new Error('Falha ao obter usuários');
  return resp.json();
}

async function createUser(user) {
  const resp = await fetch(API_BASE, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(user),
  });
  if (!resp.ok) {
    const err = await resp.json();
    throw new Error(err.error || 'Erro ao criar usuário');
  }
  return resp.json();
}

async function updateUser(id, user) {
  const resp = await fetch(`${API_BASE}/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(user),
  });
  if (!resp.ok) {
    const err = await resp.json();
    throw new Error(err.error || 'Erro ao atualizar usuário');
  }
  return resp.json();
}

async function deleteUser(id) {
  const resp = await fetch(`${API_BASE}/${id}`, { method: 'DELETE' });
  if (!resp.ok) {
    const err = await resp.json();
    throw new Error(err.error || 'Erro ao remover usuário');
  }
  return resp.json();
}

/* ------------------- UI Rendering ------------------- */
function renderTable(users) {
  tableBody.innerHTML = '';
  if (users.length === 0) {
    emptyMsg.classList.remove('hidden');
    return;
  }
  emptyMsg.classList.add('hidden');

  users.forEach(u => {
    const tr = document.createElement('tr');

    tr.innerHTML = `
      <td>${u.id}</td>
      <td>${u.name}</td>
      <td>${u.email}</td>
      <td>${u.age ?? ''}</td>
      <td>
        <button class="action-btn edit-btn" data-id="${u.id}">✎ Editar</button>
        <button class="action-btn del-btn" data-id="${u.id}">🗑️ Excluir</button>
      </td>
    `;
    tableBody.appendChild(tr);
  });
}

/* ------------------- Event Listeners ------------------- */
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const user = {
    name: nameInput.value.trim(),
    email: emailInput.value.trim(),
    age: ageInput.value ? Number(ageInput.value) : null,
  };
  try {
    if (userIdInput.value) {
      // edição
      await updateUser(userIdInput.value, user);
    } else {
      // criação
      await createUser(user);
    }
    await loadAndRender();
    clearForm();
  } catch (err) {
    alert(err.message);
  }
});

cancelBtn.addEventListener('click', (e) => {
  e.preventDefault();
  clearForm();
});

tableBody.addEventListener('click', async (e) => {
  if (e.target.matches('.edit-btn')) {
    const id = e.target.dataset.id;
    const users = await fetchUsers();
    const user = users.find(u => u.id == id);
    if (user) fillForm(user);
  } else if (e.target.matches('.del-btn')) {
    if (!confirm('Deseja realmente excluir este usuário?')) return;
    const id = e.target.dataset.id;
    try {
      await deleteUser(id);
      await loadAndRender();
    } catch (err) {
      alert(err.message);
    }
  }
});

/* ------------------- Init ------------------- */
async function loadAndRender() {
  try {
    const users = await fetchUsers();
    renderTable(users);
  } catch (err) {
    alert('Erro ao carregar usuários: ' + err.message);
  }
}

// Primeira carga
loadAndRender();
```

---  

## 8. Instruções de execução

### Pré‑requisitos
- **Node.js** (versão 14 ou superior) instalado e disponível no `PATH`.
- **Git** (opcional) se quiser clonar o repositório.

### Passos

```bash
# 1. Clone ou copie o projeto para sua máquina
git clone https://github.com/SEU_USUARIO/user-registry.git   # opcional
cd user-registry

# 2. Instalar dependências
npm install

# 3. Iniciar o servidor
npm start
```

O servidor iniciará em `http://localhost:3000`. Abra esse endereço em seu navegador; a página mostrará a lista de usuários (vazia na primeira execução) e permitirá **cadastrar**, **editar** e **remover** usuários.

### Onde os dados são armazenados?
O SQLite cria o arquivo `data.db` na raiz do projeto na primeira vez que o servidor for executado. Ele pode ser aberto com qualquer cliente SQLite para inspeção.

### Desenvolvimento
- Alterações em `public/*.js`, `public/*.html` ou `public/*.css` são refletidas imediatamente ao recarregar a página (sem necessidade de reiniciar o servidor).
- Caso queira mudar a porta, defina a variável de ambiente `PORT` antes de iniciar:

```bash
PORT=4000 npm start
```

---  

**Pronto!** 🎉  
Todo o código necessário para o sistema de cadastro de usuários está aqui, organizado em arquivos individuais e pronto para ser executado. Boa codificação!