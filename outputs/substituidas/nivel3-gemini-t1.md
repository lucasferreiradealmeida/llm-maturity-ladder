<!--
nivel: 3 - Sistema web full-stack
provider: gemini
model: gemini-pro-latest
tentativa: 1
temperature: 0.2
timestamp: 2026-08-18T17:13:27.332Z
-->

## Resposta do modelo

### `package.json`
```json
{
  "name": "sistema-usuarios",
  "version": "1.0.0",
  "main": "server.js",
  "scripts": { "start": "node server.js" },
  "dependencies": { "express": "^4.18.2", "sqlite3": "^5.1.6" }
}
```

### `server.js`
```javascript
const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const app = express();
const PORT = 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

const db = new sqlite3.Database('./database.sqlite', (err) => {
    if (err) {
        console.error('Erro ao conectar ao banco de dados:', err.message);
    } else {
        console.log('Conectado ao banco de dados SQLite.');
        db.run(`CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )`);
    }
});

app.get('/api/users', (req, res) => {
    db.all('SELECT * FROM users', [], (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        res.json(rows);
    });
});

app.post('/api/users', (req, res) => {
    const { name, email } = req.body;
    if (!name || !email) return res.status(400).json({ error: 'Nome e email são obrigatórios.' });

    const sql = 'INSERT INTO users (name, email) VALUES (?, ?)';
    db.run(sql, [name, email], function(err) {
        if (err) return res.status(400).json({ error: err.message });
        res.status(201).json({ id: this.lastID, name, email });
    });
});

app.put('/api/users/:id', (req, res) => {
    const { name, email } = req.body;
    const { id } = req.params;

    if (!name || !email) return res.status(400).json({ error: 'Nome e email são obrigatórios.' });

    const sql = 'UPDATE users SET name = ?, email = ? WHERE id = ?';
    db.run(sql, [name, email, id], function(err) {
        if (err) return res.status(400).json({ error: err.message });
        if (this.changes === 0) return res.status(404).json({ error: 'Usuário não encontrado.' });
        res.json({ id, name, email });
    });
});

app.delete('/api/users/:id', (req, res) => {
    const { id } = req.params;
    const sql = 'DELETE FROM users WHERE id = ?';
    db.run(sql, id, function(err) {
        if (err) return res.status(500).json({ error: err.message });
        if (this.changes === 0) return res.status(404).json({ error: 'Usuário não encontrado.' });
        res.json({ message: 'Usuário removido com sucesso.' });
    });
});

app.listen(PORT, () => {
    console.log(`Servidor rodando em http://localhost:${PORT}`);
});
```

### `public/index.html`
```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Cadastro de Usuários</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <h1>Gerenciamento de Usuários</h1>
        <div class="card">
            <h2 id="form-title">Novo Usuário</h2>
            <form id="user-form">
                <input type="hidden" id="user-id">
                <div class="form-group">
                    <label for="name">Nome:</label>
                    <input type="text" id="name" required>
                </div>
                <div class="form-group">
                    <label for="email">E-mail:</label>
                    <input type="email" id="email" required>
                </div>
                <button type="submit" id="btn-save">Salvar</button>
                <button type="button" id="btn-cancel" style="display: none;">Cancelar</button>
            </form>
        </div>
        <div class="card">
            <h2>Lista de Usuários</h2>
            <table>
                <thead><tr><th>ID</th><th>Nome</th><th>E-mail</th><th>Ações</th></tr></thead>
                <tbody id="user-list"></tbody>
            </table>
        </div>
    </div>
    <script src="app.js"></script>
</body>
</html>
```

### `public/style.css`
```css
body { font-family: Arial, sans-serif; padding: 20px; }
.container { max-width: 800px; margin: 0 auto; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
```

### `public/app.js`
```javascript
const API_URL = '/api/users';
const userForm = document.getElementById('user-form');
const userIdInput = document.getElementById('user-id');
const nameInput = document.getElementById('name');
const emailInput = document.getElementById('email');
const userList = document.getElementById('user-list');
const formTitle = document.getElementById('form-title');
const btnCancel = document.getElementById('btn-cancel');

document.addEventListener('DOMContentLoaded', fetchUsers);

async function fetchUsers() {
    try {
        const response = await fetch(API_URL);
        const users = await response.json();
        renderUsers(users);
    } catch (error) {
        console.error('Erro ao buscar usuários:', error);
    }
}

function renderUsers(users) {
    userList.innerHTML = '';
    users.forEach(user => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${user.id}</td>
            <td>${user.name}</td>
            <td>${user.email}</td>
            <td>
                <button onclick="editUser(${user.id}, '${user.name}', '${user.email}')">Editar</button>
                <button onclick="deleteUser(${user.id})">Remover</button>
            </td>
        `;
        userList.appendChild(tr);
    });
}

userForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = userIdInput.value;
    const user = { name: nameInput.value, email: emailInput.value };

    try {
        if (id) {
            await fetch(`${API_URL}/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(user)
            });
        } else {
            await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(user)
            });
        }
        resetForm();
        fetchUsers();
    } catch (error) {
        console.error('Erro ao salvar usuário:', error);
        alert('Erro ao salvar usuário. Verifique se o email já existe.');
    }
});

window.editUser = (id, name, email) => {
    userIdInput.value = id;
    nameInput.value = name;
    emailInput.value = email;
    formTitle.textContent = 'Editar Usuário';
    btnCancel.style.display = 'inline-block';
};

window.deleteUser = async (id) => {
    if (confirm('Tem certeza que deseja remover este usuário?')) {
        try {
            await fetch(`${API_URL}/${id}`, { method: 'DELETE' });
            fetchUsers();
        } catch (error) {
            console.error('Erro ao remover usuário:', error);
        }
    }
};

btnCancel.addEventListener('click', resetForm);

function resetForm() {
    userForm.reset();
    userIdInput.value = '';
    formTitle.textContent = 'Novo Usuário';
    btnCancel.style.display = 'none';
}
```
