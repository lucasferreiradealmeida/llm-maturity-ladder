<!--
nivel: 3 - Sistema web full-stack
provider: gemini
model: gemini-3.1-pro-preview
tentativa: 3
temperature: 0.2
timestamp: 2026-08-31T08:50:25.179Z
metadata: {"model":"gemini-3.1-pro-preview","usage":{"promptTokenCount":195,"candidatesTokenCount":3198,"totalTokenCount":4420,"promptTokensDetails":[{"modality":"TEXT","tokenCount":195}],"thoughtsTokenCount":1027,"serviceTier":"standard"},"finish_reason":"STOP"}
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

Como engenheiro de software, projetei uma solução simples, eficiente e direta ao ponto. 

**Decisões de Arquitetura:**
1. **Backend:** Utilizei `express` para facilitar a criação da API REST e o roteamento, e `sqlite3` para a persistência de dados.
2. **Frontend:** Utilizei HTML, CSS e JavaScript puro (Vanilla JS). Isso elimina a necessidade de ferramentas de build (como Webpack ou Vite) e frameworks pesados (como React ou Vue), mantendo o projeto estritamente dentro da regra de "mínimo de frameworks necessários".
3. **Estrutura:** O backend servirá os arquivos estáticos do frontend a partir de uma pasta chamada `public`.

Abaixo estão todos os arquivos necessários e as instruções de execução.

### Estrutura de Arquivos
Crie uma pasta para o projeto e adicione os seguintes arquivos exatamente com estes nomes:

---

**`package.json`**
```json
{
  "name": "sistema-usuarios",
  "version": "1.0.0",
  "description": "CRUD de usuarios com Node.js e SQLite",
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

**`server.js`**
```javascript
// server.js - Ponto de entrada do Backend
const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const app = express();
const PORT = 3000;

// Middleware para fazer o parse de JSON no corpo das requisições
app.use(express.json());

// Servir arquivos estáticos da pasta 'public' (Frontend)
app.use(express.static(path.join(__dirname, 'public')));

// Inicialização do banco de dados SQLite (cria um arquivo local)
const db = new sqlite3.Database('./database.sqlite', (err) => {
    if (err) {
        console.error('Erro ao conectar ao banco de dados:', err.message);
    } else {
        console.log('Conectado ao banco de dados SQLite.');
        // Criação da tabela de usuários caso não exista
        db.run(`CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )`);
    }
});

// ==========================================
// API REST - Rotas de Usuários
// ==========================================

// CREATE - Cadastrar usuário
app.post('/api/users', (req, res) => {
    const { name, email } = req.body;
    if (!name || !email) return res.status(400).json({ error: 'Nome e email são obrigatórios.' });

    const sql = 'INSERT INTO users (name, email) VALUES (?, ?)';
    db.run(sql, [name, email], function(err) {
        if (err) return res.status(400).json({ error: err.message });
        res.status(201).json({ id: this.lastID, name, email });
    });
});

// READ - Listar todos os usuários
app.get('/api/users', (req, res) => {
    const sql = 'SELECT * FROM users';
    db.all(sql, [], (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        res.json(rows);
    });
});

// UPDATE - Editar usuário
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

// DELETE - Remover usuário
app.delete('/api/users/:id', (req, res) => {
    const { id } = req.params;
    const sql = 'DELETE FROM users WHERE id = ?';
    
    db.run(sql, id, function(err) {
        if (err) return res.status(500).json({ error: err.message });
        if (this.changes === 0) return res.status(404).json({ error: 'Usuário não encontrado.' });
        res.json({ message: 'Usuário removido com sucesso.' });
    });
});

// Iniciar o servidor
app.listen(PORT, () => {
    console.log(`Servidor rodando em http://localhost:${PORT}`);
});
```

---

Crie uma pasta chamada **`public`** na raiz do projeto. Dentro dela, crie os próximos 3 arquivos:

**`public/index.html`**
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
        
        <!-- Formulário de Cadastro/Edição -->
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
            <button type="submit" id="submitBtn">Salvar Usuário</button>
            <button type="button" id="cancelBtn" style="display: none;" onclick="resetForm()">Cancelar</button>
        </form>

        <!-- Lista de Usuários -->
        <h2>Lista de Usuários</h2>
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

**`public/style.css`**
```css
body {
    font-family: Arial, sans-serif;
    background-color: #f4f4f9;
    margin: 0;
    padding: 20px;
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
    color: #333;
}

.form-group {
    margin-bottom: 15px;
}

label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
}

input[type="text"], input[type="email"] {
    width: 100%;
    padding: 8px;
    box-sizing: border-box;
    border: 1px solid #ccc;
    border-radius: 4px;
}

button {
    padding: 10px 15px;
    background-color: #28a745;
    color: white;
    border: none;
    border-radius: 4px;
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
    margin-top: 20px;
}

th, td {
    padding: 12px;
    border: 1px solid #ddd;
    text-align: left;
}

th {
    background-color: #f8f9fa;
}

.btn-edit {
    background-color: #007bff;
    padding: 5px 10px;
}

.btn-edit:hover {
    background-color: #0056b3;
}

.btn-delete {
    background-color: #dc3545;
    padding: 5px 10px;
}

.btn-delete:hover {
    background-color: #c82333;
}
```

---

**`public/app.js`**
```javascript
const API_URL = '/api/users';
const userForm = document.getElementById('userForm');
const userTableBody = document.getElementById('userTableBody');
const submitBtn = document.getElementById('submitBtn');
const cancelBtn = document.getElementById('cancelBtn');

// Carregar usuários ao iniciar
document.addEventListener('DOMContentLoaded', fetchUsers);

// Lidar com o envio do formulário (Criar ou Atualizar)
userForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const id = document.getElementById('userId').value;
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;

    const method = id ? 'PUT' : 'POST';
    const url = id ? `${API_URL}/${id}` : API_URL;

    try {
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Erro ao salvar usuário');
        }

        resetForm();
        fetchUsers();
    } catch (error) {
        alert(error.message);
    }
});

// Buscar e renderizar usuários
async function fetchUsers() {
    try {
        const response = await fetch(API_URL);
        const users = await response.json();
        
        userTableBody.innerHTML = '';
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
            userTableBody.appendChild(tr);
        });
    } catch (error) {
        console.error('Erro ao buscar usuários:', error);
    }
}

// Preparar formulário para edição
function editUser(id, name, email) {
    document.getElementById('userId').value = id;
    document.getElementById('name').value = name;
    document.getElementById('email').value = email;
    
    submitBtn.textContent = 'Atualizar Usuário';
    cancelBtn.style.display = 'inline-block';
}

// Excluir usuário
async function deleteUser(id) {
    if (!confirm('Tem certeza que deseja excluir este usuário?')) return;

    try {
        const response = await fetch(`${API_URL}/${id}`, { method: 'DELETE' });
        if (!response.ok) throw new Error('Erro ao excluir usuário');
        fetchUsers();
    } catch (error) {
        alert(error.message);
    }
}

// Resetar formulário
function resetForm() {
    document.getElementById('userId').value = '';
    document.getElementById('name').value = '';
    document.getElementById('email').value = '';
    
    submitBtn.textContent = 'Salvar Usuário';
    cancelBtn.style.display = 'none';
}
```

---

### Instruções de Execução

1. **Pré-requisitos:** Certifique-se de ter o [Node.js](https://nodejs.org/) instalado em sua máquina.
2. **Preparação:** Abra o terminal, navegue até a pasta raiz do projeto (onde está o `package.json`).
3. **Instalar Dependências:** Execute o comando abaixo para instalar o Express e o SQLite3:
   ```bash
   npm install
   ```
4. **Rodar o Servidor:** Inicie a aplicação com o comando:
   ```bash
   npm start
   ```
5. **Acessar o Sistema:** Abra o seu navegador e acesse:
   **http://localhost:3000**

O banco de dados (`database.sqlite`) será criado automaticamente na raiz do projeto assim que o servidor for iniciado pela primeira vez.