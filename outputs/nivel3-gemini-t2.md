<!--
nivel: 3 - Sistema web full-stack
provider: gemini
model: gemini-3.1-pro-preview
modelo_resolvido: gemini-3.1-pro-preview
tentativa: 2
temperature: 0.2
timestamp: 2026-09-28T18:34:14.493Z
metadata: {"model":"gemini-3.1-pro-preview","modelVersion":"gemini-3.1-pro-preview","responseId":"JrO6aqmZKv6fz7IPzNH48A8","usage":{"promptTokenCount":195,"candidatesTokenCount":3254,"totalTokenCount":4521,"promptTokensDetails":[{"modality":"TEXT","tokenCount":195}],"thoughtsTokenCount":1072,"serviceTier":"standard"},"finish_reason":"STOP","parametros":{"maxOutputTokens":16000,"temperature":0.2,"thinkingConfig":{"thinkingBudget":2048}}}
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

Olá! Como engenheiro de software, projetei uma solução minimalista e eficiente para o seu problema. 

Para manter a simplicidade e atender à restrição de usar apenas os frameworks estritamente necessários, optei por:
1. **Backend:** Node.js com `express` (para roteamento e API REST) e `sqlite3` (para o banco de dados).
2. **Frontend:** HTML, CSS e JavaScript puros (Vanilla JS), servidos estaticamente pelo próprio Express. Nenhuma biblioteca externa (como React ou Angular) foi utilizada.
3. **Banco de Dados:** O SQLite criará um arquivo local chamado `database.sqlite` automaticamente na primeira execução.

Abaixo estão as instruções de execução e os códigos de todos os arquivos necessários.

### Instruções de Execução

1. Crie uma pasta para o projeto e entre nela.
2. Salve os arquivos abaixo com seus respectivos nomes e na estrutura de pastas indicada (crie a pasta `public`).
3. No terminal, dentro da pasta do projeto, instale as dependências executando:
   ```bash
   npm install express sqlite3
   ```
4. Inicie o servidor executando:
   ```bash
   node server.js
   ```
5. Abra o seu navegador e acesse: `http://localhost:3000`

---

### Estrutura de Arquivos
```text
/
├── package.json
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
  "name": "crud-usuarios-node-sqlite",
  "version": "1.0.0",
  "description": "Sistema de cadastro de usuários com Node.js e SQLite",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "sqlite3": "^5.1.6"
  }
}
```

---

### `server.js`
```javascript
// server.js
// Backend: API REST e inicialização do banco de dados SQLite

const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const app = express();
const PORT = 3000;

// Middleware para interpretar JSON e servir arquivos estáticos do frontend
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Inicialização do Banco de Dados SQLite
// Assumindo a criação de um arquivo local para persistência
const db = new sqlite3.Database('./database.sqlite', (err) => {
    if (err) {
        console.error('Erro ao conectar ao banco de dados:', err.message);
    } else {
        console.log('Conectado ao banco de dados SQLite.');
        // Cria a tabela de usuários se não existir
        db.run(`CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )`);
    }
});

// --- ROTAS DA API REST ---

// CREATE: Cadastrar usuário
app.post('/api/users', (req, res) => {
    const { name, email } = req.body;
    if (!name || !email) return res.status(400).json({ error: 'Nome e email são obrigatórios.' });

    const sql = 'INSERT INTO users (name, email) VALUES (?, ?)';
    db.run(sql, [name, email], function(err) {
        if (err) return res.status(500).json({ error: err.message });
        res.status(201).json({ id: this.lastID, name, email });
    });
});

// READ: Listar todos os usuários
app.get('/api/users', (req, res) => {
    const sql = 'SELECT * FROM users';
    db.all(sql, [], (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        res.json(rows);
    });
});

// UPDATE: Editar usuário
app.put('/api/users/:id', (req, res) => {
    const { name, email } = req.body;
    const { id } = req.params;
    
    if (!name || !email) return res.status(400).json({ error: 'Nome e email são obrigatórios.' });

    const sql = 'UPDATE users SET name = ?, email = ? WHERE id = ?';
    db.run(sql, [name, email, id], function(err) {
        if (err) return res.status(500).json({ error: err.message });
        if (this.changes === 0) return res.status(404).json({ error: 'Usuário não encontrado.' });
        res.json({ message: 'Usuário atualizado com sucesso.' });
    });
});

// DELETE: Remover usuário
app.delete('/api/users/:id', (req, res) => {
    const { id } = req.params;
    const sql = 'DELETE FROM users WHERE id = ?';
    
    db.run(sql, id, function(err) {
        if (err) return res.status(500).json({ error: err.message });
        if (this.changes === 0) return res.status(404).json({ error: 'Usuário não encontrado.' });
        res.json({ message: 'Usuário removido com sucesso.' });
    });
});

// Inicia o servidor
app.listen(PORT, () => {
    console.log(`Servidor rodando em http://localhost:${PORT}`);
});
```

---

### `public/index.html`
```html
<!-- public/index.html -->
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cadastro de Usuários</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <h1>Gerenciamento de Usuários</h1>
        
        <!-- Formulário para Cadastro e Edição -->
        <form id="userForm">
            <input type="hidden" id="userId">
            <div class="form-group">
                <label for="name">Nome:</label>
                <input type="text" id="name" required placeholder="Digite o nome">
            </div>
            <div class="form-group">
                <label for="email">E-mail:</label>
                <input type="email" id="email" required placeholder="Digite o e-mail">
            </div>
            <button type="submit" id="submitBtn">Cadastrar</button>
            <button type="button" id="cancelBtn" style="display: none;">Cancelar</button>
        </form>

        <!-- Lista de Usuários -->
        <h2>Usuários Cadastrados</h2>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Nome</th>
                    <th>E-mail</th>
                    <th>Ações</th>
                </tr>
            </thead>
            <tbody id="userTableBody">
                <!-- Linhas geradas via JavaScript -->
            </tbody>
        </table>
    </div>

    <script src="app.js"></script>
</body>
</html>
```

---

### `public/style.css`
```css
/* public/style.css */
body {
    font-family: Arial, sans-serif;
    background-color: #f4f4f9;
    margin: 0;
    padding: 20px;
    color: #333;
}

.container {
    max-width: 800px;
    margin: 0 auto;
    background: #fff;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

h1, h2 {
    text-align: center;
}

form {
    display: flex;
    flex-direction: column;
    gap: 15px;
    margin-bottom: 30px;
    padding: 20px;
    background: #f9f9f9;
    border-radius: 5px;
}

.form-group {
    display: flex;
    flex-direction: column;
}

input {
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 16px;
}

button {
    padding: 10px;
    border: none;
    border-radius: 4px;
    background-color: #28a745;
    color: white;
    font-size: 16px;
    cursor: pointer;
}

button:hover {
    background-color: #218838;
}

#cancelBtn {
    background-color: #6c757d;
}

#cancelBtn:hover {
    background-color: #5a6268;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th, td {
    padding: 12px;
    border-bottom: 1px solid #ddd;
    text-align: left;
}

th {
    background-color: #007bff;
    color: white;
}

.action-btn {
    padding: 5px 10px;
    font-size: 14px;
    margin-right: 5px;
}

.edit-btn {
    background-color: #ffc107;
    color: #212529;
}

.delete-btn {
    background-color: #dc3545;
}
```

---

### `public/app.js`
```javascript
// public/app.js
// Frontend: Lógica de consumo da API REST e manipulação do DOM

const API_URL = '/api/users';

const userForm = document.getElementById('userForm');
const userIdInput = document.getElementById('userId');
const nameInput = document.getElementById('name');
const emailInput = document.getElementById('email');
const submitBtn = document.getElementById('submitBtn');
const cancelBtn = document.getElementById('cancelBtn');
const userTableBody = document.getElementById('userTableBody');

// Carregar usuários ao iniciar
document.addEventListener('DOMContentLoaded', fetchUsers);

// Lidar com o envio do formulário (Criar ou Atualizar)
userForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const id = userIdInput.value;
    const user = {
        name: nameInput.value,
        email: emailInput.value
    };

    try {
        if (id) {
            // Atualizar
            await fetch(`${API_URL}/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(user)
            });
        } else {
            // Criar
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
        alert('Erro ao salvar usuário.');
    }
});

// Cancelar edição
cancelBtn.addEventListener('click', resetForm);

// Buscar e renderizar usuários
async function fetchUsers() {
    try {
        const response = await fetch(API_URL);
        const users = await response.json();
        renderTable(users);
    } catch (error) {
        console.error('Erro ao buscar usuários:', error);
    }
}

// Renderizar tabela no HTML
function renderTable(users) {
    userTableBody.innerHTML = '';
    users.forEach(user => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${user.id}</td>
            <td>${user.name}</td>
            <td>${user.email}</td>
            <td>
                <button class="action-btn edit-btn" onclick="editUser(${user.id}, '${user.name}', '${user.email}')">Editar</button>
                <button class="action-btn delete-btn" onclick="deleteUser(${user.id})">Excluir</button>
            </td>
        `;
        userTableBody.appendChild(tr);
    });
}

// Preparar formulário para edição
function editUser(id, name, email) {
    userIdInput.value = id;
    nameInput.value = name;
    emailInput.value = email;
    
    submitBtn.textContent = 'Atualizar';
    cancelBtn.style.display = 'inline-block';
}

// Excluir usuário
async function deleteUser(id) {
    if (!confirm('Tem certeza que deseja excluir este usuário?')) return;

    try {
        await fetch(`${API_URL}/${id}`, { method: 'DELETE' });
        fetchUsers();
    } catch (error) {
        console.error('Erro ao excluir usuário:', error);
        alert('Erro ao excluir usuário.');
    }
}

// Resetar formulário para estado inicial
function resetForm() {
    userIdInput.value = '';
    nameInput.value = '';
    emailInput.value = '';
    submitBtn.textContent = 'Cadastrar';
    cancelBtn.style.display = 'none';
}
```