<!--
nivel: 3 - Sistema web full-stack
provider: gemini
model: gemini-3.1-pro-preview
modelo_resolvido: gemini-3.1-pro-preview
tentativa: 1
temperature: 0.2
timestamp: 2026-09-28T18:33:42.286Z
metadata: {"model":"gemini-3.1-pro-preview","modelVersion":"gemini-3.1-pro-preview","responseId":"BrO6aoSAG46sz7IPj4aN8Qw","usage":{"promptTokenCount":195,"candidatesTokenCount":3428,"totalTokenCount":4696,"promptTokensDetails":[{"modality":"TEXT","tokenCount":195}],"thoughtsTokenCount":1073,"serviceTier":"standard"},"finish_reason":"STOP","parametros":{"maxOutputTokens":16000,"temperature":0.2,"thinkingConfig":{"thinkingBudget":2048}}}
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

Como engenheiro de software, projetei uma solução minimalista e eficiente. Para o backend, utilizarei o **Node.js** com o micro-framework **Express** (estritamente necessário para lidar com rotas HTTP de forma limpa) e o driver **sqlite3** para o banco de dados. Para o frontend, utilizarei **HTML, CSS e JavaScript puro (Vanilla JS)**, sem frameworks como React ou Vue, garantindo leveza e cumprindo a restrição. O frontend será servido pelo próprio backend para evitar problemas de CORS e simplificar a execução.

Abaixo estão as instruções de execução e os arquivos do projeto.

### Instruções de Execução

1. Certifique-se de ter o **Node.js** instalado em sua máquina.
2. Crie uma pasta para o projeto e salve os arquivos abaixo com seus respectivos nomes e estruturas de diretório (crie uma pasta chamada `public` para os arquivos do frontend).
3. Abra o terminal na raiz do projeto e execute o comando para instalar as dependências:
   ```bash
   npm install
   ```
4. Inicie o servidor com o comando:
   ```bash
   npm start
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
Arquivo de configuração do Node.js e dependências.

```json
{
  "name": "crud-usuarios-node-sqlite",
  "version": "1.0.0",
  "description": "Sistema CRUD de usuários com Node.js, Express e SQLite",
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
Backend da aplicação. Gerencia a API REST e a conexão com o SQLite.
*Decisão de design: O banco de dados será criado em um arquivo local `database.sqlite`. A tabela será criada automaticamente ao iniciar o servidor.*

```javascript
const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const app = express();
const PORT = 3000;

// Middleware para fazer o parse do corpo das requisições em JSON
app.use(express.json());

// Serve os arquivos estáticos do frontend (HTML, CSS, JS)
app.use(express.static(path.join(__dirname, 'public')));

// Inicialização do Banco de Dados SQLite
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

// ==========================================
// ROTAS DA API REST
// ==========================================

// Listar todos os usuários (Read)
app.get('/api/users', (req, res) => {
    db.all('SELECT * FROM users', [], (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        res.json(rows);
    });
});

// Cadastrar um novo usuário (Create)
app.post('/api/users', (req, res) => {
    const { name, email } = req.body;
    if (!name || !email) return res.status(400).json({ error: 'Nome e email são obrigatórios.' });

    const sql = 'INSERT INTO users (name, email) VALUES (?, ?)';
    db.run(sql, [name, email], function(err) {
        if (err) return res.status(400).json({ error: 'Erro ao cadastrar. Email pode já estar em uso.' });
        res.status(201).json({ id: this.lastID, name, email });
    });
});

// Editar um usuário (Update)
app.put('/api/users/:id', (req, res) => {
    const { name, email } = req.body;
    const { id } = req.params;

    const sql = 'UPDATE users SET name = ?, email = ? WHERE id = ?';
    db.run(sql, [name, email, id], function(err) {
        if (err) return res.status(400).json({ error: err.message });
        if (this.changes === 0) return res.status(404).json({ error: 'Usuário não encontrado.' });
        res.json({ message: 'Usuário atualizado com sucesso.' });
    });
});

// Remover um usuário (Delete)
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
Estrutura da interface do usuário.

```html
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
        <div class="form-container">
            <h2 id="form-title">Novo Usuário</h2>
            <form id="user-form">
                <input type="hidden" id="user-id">
                <div class="input-group">
                    <label for="name">Nome:</label>
                    <input type="text" id="name" required placeholder="Digite o nome">
                </div>
                <div class="input-group">
                    <label for="email">E-mail:</label>
                    <input type="email" id="email" required placeholder="Digite o e-mail">
                </div>
                <div class="form-actions">
                    <button type="submit" id="btn-save">Salvar</button>
                    <button type="button" id="btn-cancel" class="btn-secondary" style="display: none;">Cancelar</button>
                </div>
            </form>
        </div>

        <!-- Lista de Usuários -->
        <div class="list-container">
            <h2>Usuários Cadastrados</h2>
            <table id="users-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nome</th>
                        <th>E-mail</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody id="users-list">
                    <!-- Usuários serão injetados aqui via JavaScript -->
                </tbody>
            </table>
        </div>
    </div>

    <script src="app.js"></script>
</body>
</html>
```

---

### `public/style.css`
Estilização básica para tornar a interface limpa e amigável.

```css
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    font-family: Arial, sans-serif;
}

body {
    background-color: #f4f4f9;
    color: #333;
    padding: 20px;
}

.container {
    max-width: 800px;
    margin: 0 auto;
}

h1 {
    text-align: center;
    margin-bottom: 20px;
}

.form-container, .list-container {
    background: #fff;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}

h2 {
    margin-bottom: 15px;
    font-size: 1.2rem;
    border-bottom: 2px solid #eee;
    padding-bottom: 5px;
}

.input-group {
    margin-bottom: 15px;
}

.input-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
}

.input-group input {
    width: 100%;
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
}

button {
    padding: 10px 15px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    background-color: #28a745;
    color: white;
    font-weight: bold;
}

button:hover {
    background-color: #218838;
}

.btn-secondary {
    background-color: #6c757d;
}

.btn-secondary:hover {
    background-color: #5a6268;
}

.btn-edit {
    background-color: #ffc107;
    color: #000;
    padding: 5px 10px;
}

.btn-delete {
    background-color: #dc3545;
    padding: 5px 10px;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th, td {
    padding: 10px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}

th {
    background-color: #f8f9fa;
}
```

---

### `public/app.js`
Lógica do frontend. Consome a API REST usando a `Fetch API` nativa do navegador.
*Decisão de design: O mesmo formulário é usado para criar e editar. A presença de um valor no campo oculto `user-id` determina se a requisição será POST (criar) ou PUT (atualizar).*

```javascript
const userForm = document.getElementById('user-form');
const userIdInput = document.getElementById('user-id');
const nameInput = document.getElementById('name');
const emailInput = document.getElementById('email');
const usersList = document.getElementById('users-list');
const formTitle = document.getElementById('form-title');
const btnCancel = document.getElementById('btn-cancel');

// Carrega os usuários ao abrir a página
document.addEventListener('DOMContentLoaded', fetchUsers);

// Gerencia o envio do formulário (Criar ou Editar)
userForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const id = userIdInput.value;
    const user = {
        name: nameInput.value,
        email: emailInput.value
    };

    try {
        if (id) {
            // Atualizar (PUT)
            await fetch(`/api/users/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(user)
            });
        } else {
            // Criar (POST)
            await fetch('/api/users', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(user)
            });
        }
        
        resetForm();
        fetchUsers();
    } catch (error) {
        alert('Erro ao salvar usuário.');
        console.error(error);
    }
});

// Botão cancelar edição
btnCancel.addEventListener('click', resetForm);

// Função para buscar e renderizar usuários (GET)
async function fetchUsers() {
    try {
        const response = await fetch('/api/users');
        const users = await response.json();
        
        usersList.innerHTML = '';
        users.forEach(user => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${user.id}</td>
                <td>${user.name}</td>
                <td>${user.email}</td>
                <td>
                    <button class="btn-edit" onclick="editUser(${user.id}, '${user.name}', '${user.email}')">Editar</button>
                    <button class="btn-delete" onclick="deleteUser(${user.id})">Excluir</button>
                </td>
            `;
            usersList.appendChild(tr);
        });
    } catch (error) {
        console.error('Erro ao buscar usuários:', error);
    }
}

// Prepara o formulário para edição
function editUser(id, name, email) {
    userIdInput.value = id;
    nameInput.value = name;
    emailInput.value = email;
    
    formTitle.textContent = 'Editar Usuário';
    btnCancel.style.display = 'inline-block';
}

// Função para deletar usuário (DELETE)
async function deleteUser(id) {
    if (!confirm('Tem certeza que deseja excluir este usuário?')) return;

    try {
        await fetch(`/api/users/${id}`, { method: 'DELETE' });
        fetchUsers();
    } catch (error) {
        alert('Erro ao excluir usuário.');
        console.error(error);
    }
}

// Reseta o formulário para o estado inicial de criação
function resetForm() {
    userIdInput.value = '';
    nameInput.value = '';
    emailInput.value = '';
    formTitle.textContent = 'Novo Usuário';
    btnCancel.style.display = 'none';
}
```