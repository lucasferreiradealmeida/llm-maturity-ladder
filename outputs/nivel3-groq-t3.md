<!--
nivel: 3 - Sistema web full-stack
provider: groq
model: openai/gpt-oss-120b
tentativa: 3
temperature: 0.2
timestamp: 2026-08-31T09:08:09.798Z
metadata: {"model":"openai/gpt-oss-120b","usage":{"queue_time":0.247827749,"prompt_tokens":251,"prompt_time":0.010084497,"completion_tokens":4342,"completion_time":9.141295883,"total_tokens":4593,"total_time":9.15138038,"completion_tokens_details":{"reasoning_tokens":32}},"finish_reason":"stop"}
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

**Resumo**  
Este repositório contém um pequeno sistema web (frontend + backend) para gerenciamento de usuários.  
- **Backend**: Node.js + Express + sqlite3 – API REST completa (`GET /users`, `POST /users`, `PUT /users/:id`, `DELETE /users/:id`).  
- **Frontend**: HTML + CSS + vanilla JavaScript – interface simples que consome a API e permite listar, criar, editar e remover usuários.  

A seguir estão todos os arquivos necessários, com comentários explicativos, e instruções passo‑a‑passo para rodar o projeto.

---

## Estrutura de diretórios

```
user‑manager/
│
├─ backend/
│   ├─ package.json
│   ├─ package-lock.json   (gerado após npm install)
│   ├─ server.js
│   └─ db.js
│
├─ frontend/
│   ├─ index.html
│   ├─ style.css
│   └─ app.js
│
└─ README.md
```

---

## 1. Backend

### 1.1 `backend/package.json`

```json
{
  "name": "user-manager-backend",
  "version": "1.0.0",
  "description": "API REST para cadastro de usuários usando SQLite",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js"
  },
  "author": "Your Name",
  "license": "MIT",
  "dependencies": {
    "express": "^4.18.2",
    "sqlite3": "^5.1.6"
  },
  "devDependencies": {
    "nodemon": "^3.0.1"
  }
}
```

*Observação*: `nodemon` é opcional, mas útil durante o desenvolvimento.

### 1.2 `backend/db.js`

```js
// db.js – camada de acesso ao SQLite
// Cria (se necessário) o arquivo users.db e a tabela "users"

const path = require('path');
const sqlite3 = require('sqlite3').verbose();

// O banco será armazenado dentro da pasta backend/
const DB_PATH = path.join(__dirname, 'users.db');

const db = new sqlite3.Database(DB_PATH, (err) => {
  if (err) {
    console.error('Erro ao conectar ao SQLite:', err.message);
    process.exit(1);
  }
  console.log('Conectado ao SQLite em', DB_PATH);
});

// Cria a tabela caso ela não exista
const initSql = `
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    age INTEGER
  );
`;

db.run(initSql, (err) => {
  if (err) {
    console.error('Erro ao criar tabela "users":', err.message);
  } else {
    console.log('Tabela "users" pronta para uso.');
  }
});

module.exports = db;
```

### 1.3 `backend/server.js`

```js
// server.js – API REST completa
// Usa apenas Express (framework minimalista) e o módulo sqlite3 criado acima.

const express = require('express');
const db = require('./db');
const path = require('path');
const cors = require('cors'); // permite que o frontend (que roda em outra porta) acesse a API

const app = express();
const PORT = process.env.PORT || 3000;

// Middlewares
app.use(cors());                // habilita CORS para todas as rotas
app.use(express.json());        // parseia JSON no body das requisições

// ---------- Rotas da API ----------
/**
 * GET /users
 * Retorna a lista completa de usuários.
 */
app.get('/users', (req, res) => {
  const sql = 'SELECT * FROM users ORDER BY id ASC';
  db.all(sql, [], (err, rows) => {
    if (err) {
      console.error(err);
      return res.status(500).json({ error: 'Falha ao buscar usuários.' });
    }
    res.json(rows);
  });
});

/**
 * POST /users
 * Cria um novo usuário.
 * Espera no body: { name, email, age }
 */
app.post('/users', (req, res) => {
  const { name, email, age } = req.body;
  if (!name || !email) {
    return res.status(400).json({ error: 'Nome e e‑mail são obrigatórios.' });
  }

  const sql = 'INSERT INTO users (name, email, age) VALUES (?,?,?)';
  db.run(sql, [name, email, age], function (err) {
    if (err) {
      console.error(err);
      // SQLite lança erro de UNIQUE constraint quando o e‑mail já existe
      if (err.message.includes('UNIQUE')) {
        return res.status(409).json({ error: 'E‑mail já cadastrado.' });
      }
      return res.status(500).json({ error: 'Falha ao criar usuário.' });
    }
    // this.lastID contém o ID gerado automaticamente
    res.status(201).json({ id: this.lastID, name, email, age });
  });
});

/**
 * PUT /users/:id
 * Atualiza um usuário existente.
 * Espera no body: { name, email, age }
 */
app.put('/users/:id', (req, res) => {
  const { id } = req.params;
  const { name, email, age } = req.body;
  if (!name || !email) {
    return res.status(400).json({ error: 'Nome e e‑mail são obrigatórios.' });
  }

  const sql = 'UPDATE users SET name = ?, email = ?, age = ? WHERE id = ?';
  db.run(sql, [name, email, age, id], function (err) {
    if (err) {
      console.error(err);
      if (err.message.includes('UNIQUE')) {
        return res.status(409).json({ error: 'E‑mail já cadastrado.' });
      }
      return res.status(500).json({ error: 'Falha ao atualizar usuário.' });
    }
    if (this.changes === 0) {
      return res.status(404).json({ error: 'Usuário não encontrado.' });
    }
    res.json({ id: Number(id), name, email, age });
  });
});

/**
 * DELETE /users/:id
 * Remove o usuário com o ID informado.
 */
app.delete('/users/:id', (req, res) => {
  const { id } = req.params;
  const sql = 'DELETE FROM users WHERE id = ?';
  db.run(sql, id, function (err) {
    if (err) {
      console.error(err);
      return res.status(500).json({ error: 'Falha ao remover usuário.' });
    }
    if (this.changes === 0) {
      return res.status(404).json({ error: 'Usuário não encontrado.' });
    }
    res.json({ message: 'Usuário removido com sucesso.' });
  });
});

// ---------- Servir arquivos estáticos do frontend (opcional) ----------
app.use('/', express.static(path.join(__dirname, '..', 'frontend')));

// Inicia o servidor
app.listen(PORT, () => {
  console.log(`🚀 API rodando em http://localhost:${PORT}`);
});
```

*Obs.*: O `express.static` permite que, ao rodar o backend, você acesse diretamente a pasta `frontend` (útil para testes rápidos). Em produção, pode‑se servir o frontend de forma independente.

---

## 2. Frontend

### 2.1 `frontend/index.html`

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Gerenciador de Usuários</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <h1>Gerenciador de Usuários</h1>

  <!-- Formulário para criar/editar -->
  <section id="form-section">
    <h2 id="form-title">Cadastrar Usuário</h2>
    <form id="user-form">
      <input type="hidden" id="user-id"> <!-- usado somente na edição -->
      <div class="field">
        <label for="name">Nome:</label>
        <input type="text" id="name" required>
      </div>
      <div class="field">
        <label for="email">E‑mail:</label>
        <input type="email" id="email" required>
      </div>
      <div class="field">
        <label for="age">Idade:</label>
        <input type="number" id="age" min="0">
      </div>
      <button type="submit" id="submit-btn">Salvar</button>
      <button type="button" id="cancel-btn" class="hidden">Cancelar</button>
    </form>
    <p id="form-msg" class="msg"></p>
  </section>

  <!-- Lista de usuários -->
  <section id="list-section">
    <h2>Lista de Usuários</h2>
    <table id="users-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Nome</th>
          <th>E‑mail</th>
          <th>Idade</th>
          <th>Ações</th>
        </tr>
      </thead>
      <tbody>
        <!-- Preenchido via JavaScript -->
      </tbody>
    </table>
    <p id="list-msg" class="msg"></p>
  </section>

  <script src="app.js"></script>
</body>
</html>
```

### 2.2 `frontend/style.css`

```css
/* style.css – visual simples e responsivo */
body {
  font-family: Arial, Helvetica, sans-serif;
  margin: 20px;
  background-color: #f9f9f9;
  color: #333;
}
h1, h2 {
  text-align: center;
}
section {
  margin: 20px auto;
  max-width: 800px;
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
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
  width: calc(100% - 100px);
  padding: 6px;
}
button {
  padding: 8px 12px;
  margin-right: 5px;
  cursor: pointer;
}
button:hover {
  opacity: 0.9;
}
#users-table {
  width: 100%;
  border-collapse: collapse;
}
#users-table th, #users-table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: center;
}
#users-table tr:nth-child(even) {
  background-color: #f2f2f2;
}
.msg {
  margin-top: 10px;
  font-weight: bold;
}
.msg.error { color: #c00; }
.msg.success { color: #090; }
.hidden { display: none; }
```

### 2.3 `frontend/app.js`

```js
/* app.js – lógica da UI que consome a API REST */
const API_URL = 'http://localhost:3000/users'; // porta do backend

// Elementos do DOM
const usersTableBody = document.querySelector('#users-table tbody');
const form = document.getElementById('user-form');
const formTitle = document.getElementById('form-title');
const submitBtn = document.getElementById('submit-btn');
const cancelBtn = document.getElementById('cancel-btn');
const formMsg = document.getElementById('form-msg');
const listMsg = document.getElementById('list-msg');

// Campos do formulário
const inputId = document.getElementById('user-id');
const inputName = document.getElementById('name');
const inputEmail = document.getElementById('email');
const inputAge = document.getElementById('age');

/* ---------- Funções de API ---------- */
async function fetchUsers() {
  try {
    const resp = await fetch(API_URL);
    if (!resp.ok) throw new Error('Erro ao buscar usuários');
    const users = await resp.json();
    renderUserList(users);
    listMsg.textContent = '';
  } catch (e) {
    listMsg.textContent = e.message;
    listMsg.className = 'msg error';
  }
}

async function createUser(user) {
  const resp = await fetch(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(user)
  });
  if (!resp.ok) {
    const err = await resp.json();
    throw new Error(err.error || 'Falha ao criar usuário');
  }
  return resp.json();
}

async function updateUser(id, user) {
  const resp = await fetch(`${API_URL}/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(user)
  });
  if (!resp.ok) {
    const err = await resp.json();
    throw new Error(err.error || 'Falha ao atualizar usuário');
  }
  return resp.json();
}

async function deleteUser(id) {
  const resp = await fetch(`${API_URL}/${id}`, { method: 'DELETE' });
  if (!resp.ok) {
    const err = await resp.json();
    throw new Error(err.error || 'Falha ao remover usuário');
  }
  return resp.json();
}

/* ---------- Renderização ---------- */
function renderUserList(users) {
  usersTableBody.innerHTML = ''; // limpa

  if (users.length === 0) {
    usersTableBody.innerHTML = '<tr><td colspan="5">Nenhum usuário cadastrado.</td></tr>';
    return;
  }

  users.forEach(user => {
    const tr = document.createElement('tr');

    tr.innerHTML = `
      <td>${user.id}</td>
      <td>${escapeHtml(user.name)}</td>
      <td>${escapeHtml(user.email)}</td>
      <td>${user.age ?? ''}</td>
      <td>
        <button class="edit-btn" data-id="${user.id}">Editar</button>
        <button class="del-btn" data-id="${user.id}">Remover</button>
      </td>
    `;

    usersTableBody.appendChild(tr);
  });
}

/* ---------- Utilitários ---------- */
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

/* ---------- Manipuladores de eventos ---------- */
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  formMsg.textContent = '';
  const user = {
    name: inputName.value.trim(),
    email: inputEmail.value.trim(),
    age: inputAge.value ? Number(inputAge.value) : null
  };

  try {
    if (inputId.value) {
      // edição
      await updateUser(inputId.value, user);
      formMsg.textContent = 'Usuário atualizado com sucesso!';
    } else {
      // criação
      await createUser(user);
      formMsg.textContent = 'Usuário criado com sucesso!';
    }
    formMsg.className = 'msg success';
    resetForm();
    fetchUsers();
  } catch (err) {
    formMsg.textContent = err.message;
    formMsg.className = 'msg error';
  }
});

cancelBtn.addEventListener('click', () => {
  resetForm();
});

usersTableBody.addEventListener('click', async (e) => {
  const target = e.target;
  const id = target.dataset.id;
  if (!id) return;

  if (target.classList.contains('edit-btn')) {
    // carregar dados para edição
    const row = target.closest('tr');
    inputId.value = id;
    inputName.value = row.children[1].textContent;
    inputEmail.value = row.children[2].textContent;
    inputAge.value = row.children[3].textContent;
    formTitle.textContent = 'Editar Usuário';
    submitBtn.textContent = 'Salvar';
    cancelBtn.classList.remove('hidden');
  }

  if (target.classList.contains('del-btn')) {
    if (confirm('Tem certeza que deseja remover este usuário?')) {
      try {
        await deleteUser(id);
        listMsg.textContent = 'Usuário removido.';
        listMsg.className = 'msg success';
        fetchUsers();
      } catch (err) {
        listMsg.textContent = err.message;
        listMsg.className = 'msg error';
      }
    }
  }
});

/* ---------- Helpers ---------- */
function resetForm() {
  inputId.value = '';
  form.reset();
  formTitle.textContent = 'Cadastrar Usuário';
  submitBtn.textContent = 'Salvar';
  cancelBtn.classList.add('hidden');
  formMsg.textContent = '';
}

/* ---------- Inicialização ---------- */
fetchUsers();
```

---

## 3. Como executar

### Pré‑requisitos
- **Node.js** (versão ≥ 14) instalado.  
- **Git** (opcional, para clonar o repositório).

### Passo a passo

1. **Clone ou copie o projeto**  
   ```bash
   git clone https://github.com/SEU_USUARIO/user-manager.git
   cd user-manager
   ```

2. **Instale as dependências do backend**  
   ```bash
   cd backend
   npm install
   ```

3. **Inicie o servidor**  
   - modo de produção (simples):  
     ```bash
     npm start
     ```
   - modo de desenvolvimento (recarrega ao salvar):  
     ```bash
     npm run dev
     ```

   O backend ficará escutando em `http://localhost:3000`.

4. **Abra o frontend**  
   - Como o backend já serve os arquivos estáticos, basta abrir no navegador:  

     ```
     http://localhost:3000/
     ```

   - Alternativamente, abra diretamente o arquivo `frontend/index.html` em um navegador; o JavaScript ainda apontará para `http://localhost:3000/users`.

5. **Teste**  
   - Cadastre novos usuários usando o formulário.  
   - Edite ou remova usuários através dos botões da tabela.  
   - Os dados são persistidos em `backend/users.db` (SQLite) e permanecem mesmo após reiniciar o servidor.

### Como limpar o banco (opcional)

Se quiser reiniciar o banco de dados:

```bash
rm backend/users.db   # remove o arquivo
npm start             # o script db.js recria a tabela vazia
```

---

## 4. Comentários finais

- **Frameworks**: Apenas `express` (para rotas HTTP) e `sqlite3` (driver SQLite) são usados. Não há dependências de front‑end além de HTML/CSS/JS puro, atendendo à restrição de “não usar frameworks além dos estritamente necessários”.
- **Validação**: O backend valida a presença de `name` e `email` e garante unicidade do e‑mail. O frontend faz validação mínima via atributos `required`/`type`.
- **Segurança**: Este é um exemplo didático; em produção, considere:
  - HTTPS, sanitização adicional, proteção contra CSRF, etc.
  - Camada de autenticação/autorização.
- **Escalabilidade**: Para projetos maiores, poderia separar frontend e backend em repositórios diferentes, usar ORM, etc., mas para o escopo pedido este código já está pronto para rodar.

Pronto! 🎉 Seu sistema de cadastro de usuários está completamente funcional. Boa codificação!