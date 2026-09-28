<!--
nivel: 4 - Seguranca (autenticacao e autorizacao)
provider: gemini
model: gemini-3.1-pro-preview
modelo_resolvido: gemini-3.1-pro-preview
tentativa: 1
temperature: 0.2
timestamp: 2026-09-28T18:34:45.202Z
metadata: {"model":"gemini-3.1-pro-preview","modelVersion":"gemini-3.1-pro-preview","responseId":"RbO6arG1Fubxz7IP0v-t8A0","usage":{"promptTokenCount":224,"candidatesTokenCount":3643,"totalTokenCount":5124,"promptTokensDetails":[{"modality":"TEXT","tokenCount":224}],"thoughtsTokenCount":1257,"serviceTier":"standard"},"finish_reason":"STOP","parametros":{"maxOutputTokens":16000,"temperature":0.2,"thinkingConfig":{"thinkingBudget":2048}}}
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

Como engenheiro de software, projetei esta solução utilizando **Node.js** com o micro-framework **Express** (estritamente necessário para roteamento HTTP e middlewares de forma limpa). 

**Decisões de Arquitetura e Assunções:**
1. **Autenticação:** Utilizei **JWT (JSON Web Tokens)**. É stateless, ideal para APIs REST e dispensa a configuração de sessões no banco de dados ou em memória.
2. **Segurança de Senha:** Utilizei a biblioteca **bcrypt**, que é o padrão da indústria para Node.js. Ela aplica automaticamente o *salt* e o *hash* de forma segura.
3. **Problema do "Ovo e a Galinha":** Como apenas usuários autenticados podem criar novos usuários, o sistema cria automaticamente um usuário administrador padrão (`admin` / `admin123`) na inicialização do banco de dados para permitir o primeiro acesso.
4. **Frontend:** Criei uma interface simples em HTML/Vanilla JS (Single Page Application) servida pelo próprio Express para que você possa testar o sistema completo (API + Interface) pelo navegador.

Abaixo estão as instruções e os arquivos necessários.

### Instruções de Execução

1. Certifique-se de ter o **Node.js** instalado em sua máquina.
2. Crie uma pasta para o projeto e salve os arquivos abaixo com seus respectivos nomes.
3. Abra o terminal na pasta do projeto e instale as dependências executando:
   ```bash
   npm install express sqlite3 bcrypt jsonwebtoken
   ```
4. Inicie o servidor:
   ```bash
   node server.js
   ```
5. Abra o navegador e acesse: `http://localhost:3000`
6. **Credenciais iniciais:** Usuário: `admin` | Senha: `admin123`

---

### `package.json`
```json
{
  "name": "user-management-system",
  "version": "1.0.0",
  "description": "Sistema de cadastro de usuarios com autenticacao",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "bcrypt": "^5.1.1",
    "express": "^4.18.2",
    "jsonwebtoken": "^9.0.2",
    "sqlite3": "^5.1.7"
  }
}
```

---

### `db.js`
```javascript
// db.js - Responsável pela conexão e inicialização do SQLite
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');

const db = new sqlite3.Database('./database.sqlite', (err) => {
    if (err) {
        console.error('Erro ao conectar ao banco de dados:', err.message);
    } else {
        console.log('Conectado ao banco de dados SQLite.');
        initDb();
    }
});

function initDb() {
    // Cria a tabela de usuários se não existir
    db.run(`CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )`, async (err) => {
        if (!err) {
            // Assunção: Criar um usuário admin padrão para permitir o primeiro login
            const saltRounds = 10;
            const hashedPassword = await bcrypt.hash('admin123', saltRounds);
            
            const insert = 'INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)';
            db.run(insert, ['admin', hashedPassword]);
        }
    });
}

module.exports = db;
```

---

### `server.js`
```javascript
// server.js - API Backend e Servidor Web
const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const path = require('path');
const db = require('./db');

const app = express();
const PORT = 3000;
const JWT_SECRET = 'super_secret_key_change_in_production'; // Em prod, usar variáveis de ambiente

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public'))); // Serve o frontend

// Middleware de Autenticação
function authenticateToken(req, res, next) {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1]; // Formato: Bearer <token>

    if (!token) return res.status(401).json({ error: 'Acesso negado. Token não fornecido.' });

    jwt.verify(token, JWT_SECRET, (err, user) => {
        if (err) return res.status(403).json({ error: 'Token inválido ou expirado.' });
        req.user = user;
        next();
    });
}

// ROTA: Login (Gera o Token JWT)
app.post('/api/login', (req, res) => {
    const { username, password } = req.body;

    db.get('SELECT * FROM users WHERE username = ?', [username], async (err, user) => {
        if (err) return res.status(500).json({ error: 'Erro no servidor.' });
        if (!user) return res.status(401).json({ error: 'Usuário ou senha incorretos.' });

        const validPassword = await bcrypt.compare(password, user.password);
        if (!validPassword) return res.status(401).json({ error: 'Usuário ou senha incorretos.' });

        const token = jwt.sign({ id: user.id, username: user.username }, JWT_SECRET, { expiresIn: '1h' });
        res.json({ token });
    });
});

// ROTA: Listar Usuários (PÚBLICA)
app.get('/api/users', (req, res) => {
    // Não retornamos a senha por segurança
    db.all('SELECT id, username FROM users', [], (err, rows) => {
        if (err) return res.status(500).json({ error: 'Erro ao buscar usuários.' });
        res.json(rows);
    });
});

// ROTA: Criar Usuário (PROTEGIDA)
app.post('/api/users', authenticateToken, async (req, res) => {
    const { username, password } = req.body;
    if (!username || !password) return res.status(400).json({ error: 'Usuário e senha são obrigatórios.' });

    try {
        const hashedPassword = await bcrypt.hash(password, 10);
        db.run('INSERT INTO users (username, password) VALUES (?, ?)', [username, hashedPassword], function(err) {
            if (err) return res.status(400).json({ error: 'Erro ao criar usuário (talvez o nome já exista).' });
            res.status(201).json({ id: this.lastID, username });
        });
    } catch (error) {
        res.status(500).json({ error: 'Erro interno.' });
    }
});

// ROTA: Editar Usuário (PROTEGIDA)
app.put('/api/users/:id', authenticateToken, async (req, res) => {
    const { username, password } = req.body;
    const { id } = req.params;

    try {
        if (password) {
            const hashedPassword = await bcrypt.hash(password, 10);
            db.run('UPDATE users SET username = ?, password = ? WHERE id = ?', [username, hashedPassword, id], function(err) {
                if (err) return res.status(400).json({ error: 'Erro ao atualizar.' });
                res.json({ message: 'Usuário atualizado com sucesso.' });
            });
        } else {
            db.run('UPDATE users SET username = ? WHERE id = ?', [username, id], function(err) {
                if (err) return res.status(400).json({ error: 'Erro ao atualizar.' });
                res.json({ message: 'Usuário atualizado com sucesso.' });
            });
        }
    } catch (error) {
        res.status(500).json({ error: 'Erro interno.' });
    }
});

// ROTA: Remover Usuário (PROTEGIDA)
app.delete('/api/users/:id', authenticateToken, (req, res) => {
    const { id } = req.params;
    db.run('DELETE FROM users WHERE id = ?', [id], function(err) {
        if (err) return res.status(500).json({ error: 'Erro ao deletar usuário.' });
        res.json({ message: 'Usuário deletado com sucesso.' });
    });
});

app.listen(PORT, () => {
    console.log(`Servidor rodando em http://localhost:${PORT}`);
});
```

---

### `public/index.html`
*(Crie uma pasta chamada `public` e coloque este arquivo dentro)*
```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Sistema de Usuários</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 600px; margin: auto; }
        .panel { border: 1px solid #ccc; padding: 15px; margin-bottom: 20px; border-radius: 5px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        .hidden { display: none; }
        button { cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Gerenciamento de Usuários</h1>
        
        <!-- Painel de Login -->
        <div id="loginPanel" class="panel">
            <h3>Login (Para gerenciar)</h3>
            <input type="text" id="loginUser" placeholder="Usuário">
            <input type="password" id="loginPass" placeholder="Senha">
            <button onclick="login()">Entrar</button>
            <p id="loginMsg"></p>
        </div>

        <!-- Painel de Gerenciamento (Protegido) -->
        <div id="adminPanel" class="panel hidden">
            <h3>Cadastrar / Editar Usuário</h3>
            <input type="hidden" id="userId">
            <input type="text" id="username" placeholder="Usuário">
            <input type="password" id="password" placeholder="Senha (deixe em branco para não alterar na edição)">
            <button onclick="saveUser()">Salvar</button>
            <button onclick="logout()">Sair</button>
            <p id="adminMsg"></p>
        </div>

        <!-- Lista Pública -->
        <div class="panel">
            <h3>Lista de Usuários (Pública)</h3>
            <button onclick="loadUsers()">Atualizar Lista</button>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Usuário</th>
                        <th>Ações (Requer Login)</th>
                    </tr>
                </thead>
                <tbody id="userTableBody"></tbody>
            </table>
        </div>
    </div>

    <script src="app.js"></script>
</body>
</html>
```

---

### `public/app.js`
*(Coloque este arquivo dentro da pasta `public`)*
```javascript
// app.js - Lógica do Frontend
let token = localStorage.getItem('token');

// Configura a UI baseada no estado de autenticação
function checkAuth() {
    if (token) {
        document.getElementById('loginPanel').classList.add('hidden');
        document.getElementById('adminPanel').classList.remove('hidden');
    } else {
        document.getElementById('loginPanel').classList.remove('hidden');
        document.getElementById('adminPanel').classList.add('hidden');
    }
}

// Função de Login
async function login() {
    const u = document.getElementById('loginUser').value;
    const p = document.getElementById('loginPass').value;
    
    const res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: u, password: p })
    });
    
    const data = await res.json();
    if (res.ok) {
        token = data.token;
        localStorage.setItem('token', token);
        document.getElementById('loginMsg').innerText = '';
        checkAuth();
    } else {
        document.getElementById('loginMsg').innerText = data.error;
    }
}

function logout() {
    token = null;
    localStorage.removeItem('token');
    checkAuth();
}

// Carregar lista pública
async function loadUsers() {
    const res = await fetch('/api/users');
    const users = await res.json();
    const tbody = document.getElementById('userTableBody');
    tbody.innerHTML = '';
    
    users.forEach(user => {
        tbody.innerHTML += `
            <tr>
                <td>${user.id}</td>
                <td>${user.username}</td>
                <td>
                    <button onclick="editUser(${user.id}, '${user.username}')">Editar</button>
                    <button onclick="deleteUser(${user.id})">Excluir</button>
                </td>
            </tr>
        `;
    });
}

// Salvar (Criar ou Editar)
async function saveUser() {
    const id = document.getElementById('userId').value;
    const u = document.getElementById('username').value;
    const p = document.getElementById('password').value;
    
    const method = id ? 'PUT' : 'POST';
    const url = id ? `/api/users/${id}` : '/api/users';
    
    const res = await fetch(url, {
        method: method,
        headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ username: u, password: p })
    });
    
    if (res.ok) {
        document.getElementById('adminMsg').innerText = 'Sucesso!';
        document.getElementById('userId').value = '';
        document.getElementById('username').value = '';
        document.getElementById('password').value = '';
        loadUsers();
    } else {
        const data = await res.json();
        document.getElementById('adminMsg').innerText = data.error || 'Erro de autenticação.';
    }
}

function editUser(id, username) {
    if(!token) return alert('Faça login para editar.');
    document.getElementById('userId').value = id;
    document.getElementById('username').value = username;
    document.getElementById('password').value = '';
}

async function deleteUser(id) {
    if(!token) return alert('Faça login para excluir.');
    if(!confirm('Tem certeza?')) return;

    const res = await fetch(`/api/users/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
    });
    
    if (res.ok) {
        loadUsers();
    } else {
        alert('Erro ao excluir ou não autorizado.');
    }
}

// Inicialização
checkAuth();
loadUsers();
```