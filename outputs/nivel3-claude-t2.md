<!--
nivel: 3 - Sistema web full-stack
provider: claude
model: claude-sonnet-5
tentativa: 2
temperature: 0.2
timestamp: 2026-08-18T21:33:57.226Z
metadata: {"model":"claude-sonnet-5","usage":{"input_tokens":331,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"cache_creation":{"ephemeral_5m_input_tokens":0,"ephemeral_1h_input_tokens":0},"output_tokens":7777,"output_tokens_details":{"thinking_tokens":416},"service_tier":"standard","inference_geo":"global"},"stop_reason":"end_turn"}
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

# Sistema de Cadastro de Usuários

Abaixo está o sistema completo: backend em **Node.js + Express** (único framework usado, pois é o mínimo necessário para expor uma API REST de forma organizada) com persistência em **SQLite** (via pacote `sqlite3`), e um frontend em **HTML/CSS/JS puro** (sem frameworks de frontend), servido como arquivos estáticos pelo próprio Express.

## Decisões de projeto (documentadas)

- **Express**: usado apenas para roteamento HTTP e servir arquivos estáticos — evita reescrever parser de rotas/HTTP manualmente, mas não traz nada além disso (sem ORM, sem template engine).
- **sqlite3**: driver oficial simples para SQLite, sem ORM, para manter o código explícito (SQL puro).
- **express.json()** nativo do Express é usado no lugar de `body-parser` (já incluso no Express 4.16+).
- Banco de dados é criado automaticamente em `data/database.sqlite` na primeira execução.
- Validação básica de campos (nome obrigatório, email obrigatório com formato válido e único) é feita no backend.
- Frontend é uma SPA simples (uma página) que consome a API via `fetch`.
- Frontend e backend rodam no mesmo servidor/porta (sem necessidade de CORS).

## Estrutura de arquivos

```
projeto/
├── package.json
├── server.js
├── db.js
└── public/
    ├── index.html
    ├── style.css
    └── app.js
```

---

### `package.json`

```json
{
  "name": "cadastro-usuarios",
  "version": "1.0.0",
  "description": "Sistema de cadastro de usuarios (Node.js + Express + SQLite)",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "^4.19.2",
    "sqlite3": "^5.1.7"
  }
}
```

---

### `db.js`

```javascript
// db.js
// Responsavel por criar/conectar o banco SQLite e garantir a existencia da tabela "users".

const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

// Garante que a pasta "data" exista, para armazenar o arquivo do banco.
const dataDir = path.join(__dirname, 'data');
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir);
}

const dbPath = path.join(dataDir, 'database.sqlite');

const db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error('Erro ao conectar ao banco de dados:', err.message);
  } else {
    console.log('Conectado ao banco SQLite em:', dbPath);
  }
});

// Cria a tabela de usuarios caso nao exista.
db.run(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
  )
`, (err) => {
  if (err) {
    console.error('Erro ao criar tabela users:', err.message);
  }
});

module.exports = db;
```

---

### `server.js`

```javascript
// server.js
// Servidor Express que expoe a API REST de usuarios e serve o frontend estatico.

const express = require('express');
const path = require('path');
const db = require('./db');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware nativo do Express para parsear JSON no corpo das requisicoes.
app.use(express.json());

// Serve os arquivos estaticos do frontend (public/).
app.use(express.static(path.join(__dirname, 'public')));

// Regex simples para validacao de email.
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function validateUserPayload(body) {
  const errors = [];
  const name = (body.name || '').trim();
  const email = (body.email || '').trim();

  if (!name) {
    errors.push('O campo "name" e obrigatorio.');
  }
  if (!email) {
    errors.push('O campo "email" e obrigatorio.');
  } else if (!EMAIL_REGEX.test(email)) {
    errors.push('O campo "email" possui formato invalido.');
  }

  return { errors, name, email };
}

// GET /api/users -> lista todos os usuarios
app.get('/api/users', (req, res) => {
  db.all('SELECT * FROM users ORDER BY id DESC', [], (err, rows) => {
    if (err) {
      return res.status(500).json({ error: 'Erro ao buscar usuarios.' });
    }
    res.json(rows);
  });
});

// GET /api/users/:id -> busca um usuario especifico
app.get('/api/users/:id', (req, res) => {
  const { id } = req.params;
  db.get('SELECT * FROM users WHERE id = ?', [id], (err, row) => {
    if (err) {
      return res.status(500).json({ error: 'Erro ao buscar usuario.' });
    }
    if (!row) {
      return res.status(404).json({ error: 'Usuario nao encontrado.' });
    }
    res.json(row);
  });
});

// POST /api/users -> cria um novo usuario
app.post('/api/users', (req, res) => {
  const { errors, name, email } = validateUserPayload(req.body);
  if (errors.length > 0) {
    return res.status(400).json({ error: errors.join(' ') });
  }

  const sql = 'INSERT INTO users (name, email) VALUES (?, ?)';
  db.run(sql, [name, email], function (err) {
    if (err) {
      if (err.message.includes('UNIQUE constraint failed')) {
        return res.status(409).json({ error: 'Ja existe um usuario com este email.' });
      }
      return res.status(500).json({ error: 'Erro ao criar usuario.' });
    }
    db.get('SELECT * FROM users WHERE id = ?', [this.lastID], (err2, row) => {
      if (err2) {
        return res.status(500).json({ error: 'Usuario criado, mas houve erro ao recupera-lo.' });
      }
      res.status(201).json(row);
    });
  });
});

// PUT /api/users/:id -> atualiza um usuario existente
app.put('/api/users/:id', (req, res) => {
  const { id } = req.params;
  const { errors, name, email } = validateUserPayload(req.body);
  if (errors.length > 0) {
    return res.status(400).json({ error: errors.join(' ') });
  }

  db.get('SELECT * FROM users WHERE id = ?', [id], (err, row) => {
    if (err) {
      return res.status(500).json({ error: 'Erro ao buscar usuario.' });
    }
    if (!row) {
      return res.status(404).json({ error: 'Usuario nao encontrado.' });
    }

    const sql = 'UPDATE users SET name = ?, email = ? WHERE id = ?';
    db.run(sql, [name, email, id], function (err2) {
      if (err2) {
        if (err2.message.includes('UNIQUE constraint failed')) {
          return res.status(409).json({ error: 'Ja existe um usuario com este email.' });
        }
        return res.status(500).json({ error: 'Erro ao atualizar usuario.' });
      }
      db.get('SELECT * FROM users WHERE id = ?', [id], (err3, updatedRow) => {
        if (err3) {
          return res.status(500).json({ error: 'Usuario atualizado, mas houve erro ao recupera-lo.' });
        }
        res.json(updatedRow);
      });
    });
  });
});

// DELETE /api/users/:id -> remove um usuario
app.delete('/api/users/:id', (req, res) => {
  const { id } = req.params;
  db.get('SELECT * FROM users WHERE id = ?', [id], (err, row) => {
    if (err) {
      return res.status(500).json({ error: 'Erro ao buscar usuario.' });
    }
    if (!row) {
      return res.status(404).json({ error: 'Usuario nao encontrado.' });
    }
    db.run('DELETE FROM users WHERE id = ?', [id], (err2) => {
      if (err2) {
        return res.status(500).json({ error: 'Erro ao remover usuario.' });
      }
      res.status(204).send();
    });
  });
});

// Fallback: qualquer rota nao reconhecida da API retorna 404 em JSON.
app.use('/api', (req, res) => {
  res.status(404).json({ error: 'Rota de API nao encontrada.' });
});

app.listen(PORT, () => {
  console.log(`Servidor rodando em http://localhost:${PORT}`);
});
```

---

### `public/index.html`

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Cadastro de Usuarios</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="container">
    <h1>Cadastro de Usuarios</h1>

    <section class="form-section">
      <h2 id="form-title">Novo Usuario</h2>
      <form id="user-form">
        <input type="hidden" id="user-id">

        <div class="field">
          <label for="name">Nome</label>
          <input type="text" id="name" placeholder="Digite o nome" required>
        </div>

        <div class="field">
          <label for="email">Email</label>
          <input type="email" id="email" placeholder="Digite o email" required>
        </div>

        <div class="actions">
          <button type="submit" id="submit-btn">Cadastrar</button>
          <button type="button" id="cancel-btn" class="secondary" hidden>Cancelar</button>
        </div>

        <p id="form-message" class="message"></p>
      </form>
    </section>

    <section class="list-section">
      <h2>Usuarios cadastrados</h2>
      <table id="users-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nome</th>
            <th>Email</th>
            <th>Criado em</th>
            <th>Acoes</th>
          </tr>
        </thead>
        <tbody id="users-tbody">
          <!-- Preenchido dinamicamente via JS -->
        </tbody>
      </table>
      <p id="empty-message" class="empty" hidden>Nenhum usuario cadastrado.</p>
    </section>
  </div>

  <script src="app.js"></script>
</body>
</html>
```

---

### `public/style.css`

```css
/* style.css - estilo simples e limpo, sem framework de CSS */

* {
  box-sizing: border-box;
}

body {
  font-family: Arial, Helvetica, sans-serif;
  background: #f4f6f8;
  margin: 0;
  padding: 20px;
  color: #333;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  background: #fff;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

h1 {
  text-align: center;
  color: #2c3e50;
}

h2 {
  color: #2c3e50;
  border-bottom: 2px solid #eee;
  padding-bottom: 8px;
}

.form-section {
  margin-bottom: 32px;
}

.field {
  margin-bottom: 12px;
  display: flex;
  flex-direction: column;
}

.field label {
  font-weight: bold;
  margin-bottom: 4px;
}

.field input {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
}

.actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

button {
  padding: 10px 16px;
  border: none;
  border-radius: 4px;
  background: #2980b9;
  color: #fff;
  cursor: pointer;
  font-size: 14px;
}

button:hover {
  background: #206090;
}

button.secondary {
  background: #95a5a6;
}

button.secondary:hover {
  background: #7f8c8d;
}

button.danger {
  background: #e74c3c;
  padding: 6px 10px;
}

button.danger:hover {
  background: #c0392b;
}

button.edit {
  background: #f39c12;
  padding: 6px 10px;
  margin-right: 6px;
}

button.edit:hover {
  background: #d68910;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 12px;
}

th, td {
  text-align: left;
  padding: 10px;
  border-bottom: 1px solid #eee;
}

th {
  background: #f0f2f5;
}

.message {
  margin-top: 8px;
  font-size: 14px;
}

.message.success {
  color: #27ae60;
}

.message.error {
  color: #e74c3c;
}

.empty {
  text-align: center;
  color: #888;
  margin-top: 16px;
}
```

---

### `public/app.js`

```javascript
// app.js - logica do frontend: consome a API REST via fetch
// e manipula o DOM para listar, cadastrar, editar e remover usuarios.

const API_URL = '/api/users';

const form = document.getElementById('user-form');
const formTitle = document.getElementById('form-title');
const userIdInput = document.getElementById('user-id');
const nameInput = document.getElementById('name');
const emailInput = document.getElementById('email');
const submitBtn = document.getElementById('submit-btn');
const cancelBtn = document.getElementById('cancel-btn');
const formMessage = document.getElementById('form-message');
const usersTbody = document.getElementById('users-tbody');
const emptyMessage = document.getElementById('empty-message');

// Formata data ISO retornada pelo SQLite (UTC) para formato legivel pt-BR.
function formatDate(isoString) {
  try {
    const date = new Date(isoString.replace(' ', 'T') + 'Z');
    return date.toLocaleString('pt-BR');
  } catch {
    return isoString;
  }
}

function showMessage(text, type) {
  formMessage.textContent = text;
  formMessage.className = `message ${type}`;
}

function clearMessage() {
  formMessage.textContent = '';
  formMessage.className = 'message';
}

function resetForm() {
  form.reset();
  userIdInput.value = '';
  formTitle.textContent = 'Novo Usuario';
  submitBtn.textContent = 'Cadastrar';
  cancelBtn.hidden = true;
  clearMessage();
}

function fillFormForEdit(user) {
  userIdInput.value = user.id;
  nameInput.value = user.name;
  emailInput.value = user.email;
  formTitle.textContent = `Editar Usuario #${user.id}`;
  submitBtn.textContent = 'Salvar alteracoes';
  cancelBtn.hidden = false;
  clearMessage();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function fetchUsers() {
  try {
    const res = await fetch(API_URL);
    if (!res.ok) throw new Error('Erro ao carregar usuarios.');
    const users = await res.json();
    renderUsers(users);
  } catch (err) {
    usersTbody.innerHTML = '';
    emptyMessage.hidden = false;
    emptyMessage.textContent = 'Erro ao carregar usuarios: ' + err.message;
  }
}

function renderUsers(users) {
  usersTbody.innerHTML = '';

  if (users.length === 0) {
    emptyMessage.hidden = false;
    emptyMessage.textContent = 'Nenhum usuario cadastrado.';
    return;
  }

  emptyMessage.hidden = true;

  users.forEach((user) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${user.id}</td>
      <td>${escapeHtml(user.name)}</td>
      <td>${escapeHtml(user.email)}</td>
      <td>${formatDate(user.created_at)}</td>
      <td>
        <button class="edit" data-id="${user.id}">Editar</button>
        <button class="danger" data-id="${user.id}">Remover</button>
      </td>
    `;
    usersTbody.appendChild(tr);
  });

  // Liga eventos dos botoes de editar
  usersTbody.querySelectorAll('button.edit').forEach((btn) => {
    btn.addEventListener('click', () => handleEditClick(btn.dataset.id));
  });

  // Liga eventos dos botoes de remover
  usersTbody.querySelectorAll('button.danger').forEach((btn) => {
    btn.addEventListener('click', () => handleDeleteClick(btn.dataset.id));
  });
}

// Evita injecao de HTML simples ao renderizar dados vindos do usuario.
function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

async function handleEditClick(id) {
  try {
    const res = await fetch(`${API_URL}/${id}`);
    if (!res.ok) throw new Error('Usuario nao encontrado.');
    const user = await res.json();
    fillFormForEdit(user);
  } catch (err) {
    alert('Erro ao carregar usuario para edicao: ' + err.message);
  }
}

async function handleDeleteClick(id) {
  if (!confirm('Tem certeza que deseja remover este usuario?')) return;

  try {
    const res = await fetch(`${API_URL}/${id}`, { method: 'DELETE' });
    if (!res.ok && res.status !== 204) {
      const data = await res.json();
      throw new Error(data.error || 'Erro ao remover usuario.');
    }
    fetchUsers();
  } catch (err) {
    alert('Erro: ' + err.message);
  }
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  clearMessage();

  const id = userIdInput.value;
  const payload = {
    name: nameInput.value.trim(),
    email: emailInput.value.trim()
  };

  const isEdit = Boolean(id);
  const url = isEdit ? `${API_URL}/${id}` : API_URL;
  const method = isEdit ? 'PUT' : 'POST';

  try {
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      throw new Error(data.error || 'Erro ao salvar usuario.');
    }

    showMessage(
      isEdit ? 'Usuario atualizado com sucesso!' : 'Usuario cadastrado com sucesso!',
      'success'
    );
    resetForm();
    fetchUsers();
  } catch (err) {
    showMessage(err.message, 'error');
  }
});

cancelBtn.addEventListener('click', () => {
  resetForm();
});

// Carrega a lista de usuarios assim que a pagina abre.
fetchUsers();
```

---

## Instruções de execução

**Pré-requisitos:** Node.js instalado (versão 16 ou superior recomendada).

1. Crie a estrutura de pastas exatamente como mostrado acima e salve cada arquivo com o nome indicado.

2. No diretório do projeto, instale as dependências:

```bash
npm install
```

3. Inicie o servidor:

```bash
npm start
```

4. Abra o navegador em:

```
http://localhost:3000
```

O banco de dados SQLite será criado automaticamente em `data/database.sqlite` na primeira execução — não é necessário nenhum passo manual de configuração de banco.

### Testando a API diretamente (opcional, via curl)

```bash
# Listar usuarios
curl http://localhost:3000/api/users

# Criar usuario
curl -X POST http://localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Maria Silva","email":"maria@exemplo.com"}'

# Atualizar usuario (id=1)
curl -X PUT http://localhost:3000/api/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"Maria Souza","email":"maria@exemplo.com"}'

# Remover usuario (id=1)
curl -X DELETE http://localhost:3000/api/users/1
```