<!--
nivel: 4 - Seguranca (autenticacao e autorizacao)
provider: gemini
model: gemini-3.1-pro-preview
modelo_resolvido: gemini-3.1-pro-preview
tentativa: 2
temperature: 0.2
timestamp: 2026-09-28T18:35:24.024Z
metadata: {"model":"gemini-3.1-pro-preview","modelVersion":"gemini-3.1-pro-preview","responseId":"bLO6apaoC93pz7IP56qWyA0","usage":{"promptTokenCount":224,"candidatesTokenCount":4022,"totalTokenCount":5707,"promptTokensDetails":[{"modality":"TEXT","tokenCount":224}],"thoughtsTokenCount":1461,"serviceTier":"standard"},"finish_reason":"STOP","parametros":{"maxOutputTokens":16000,"temperature":0.2,"thinkingConfig":{"thinkingBudget":2048}}}
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

Como engenheiro de software, projetei a solução utilizando **Node.js** com o micro-framework **Express** (padrão da indústria para roteamento HTTP minimalista). 

**Decisões de Arquitetura e Assunções:**
1. **Autenticação (Token):** Utilizei **JWT (JSON Web Token)** armazenado em um cookie `HttpOnly`. Isso protege contra ataques XSS (Cross-Site Scripting), pois o JavaScript do frontend não consegue ler o token, mas o navegador o envia automaticamente nas requisições.
2. **Segurança de Senha:** Utilizei a biblioteca **bcrypt**, que aplica automaticamente o *Salt* e o *Hash* de forma segura.
3. **Problema do "Ovo e a Galinha":** Como apenas usuários autenticados podem cadastrar novos usuários, o sistema cria automaticamente um usuário padrão (`admin` / senha: `admin123`) na primeira execução, caso o banco de dados esteja vazio.
4. **Frontend:** Criei uma página única (SPA) em HTML/JS puro (Vanilla JS) servida estaticamente pelo próprio Express para interagir com a API.

Abaixo estão os arquivos necessários e as instruções de execução.

### Instruções de Execução

1. Certifique-se de ter o **Node.js** instalado em sua máquina.
2. Crie uma pasta para o projeto e salve os três arquivos abaixo dentro dela (respeitando a pasta `public` para o HTML).
3. Abra o terminal na pasta do projeto e instale as dependências executando:
   ```bash
   npm install
   ```
4. Inicie o servidor:
   ```bash
   node server.js
   ```
5. Acesse no navegador: `http://localhost:3000`
6. **Credenciais iniciais:** Usuário: `admin` | Senha: `admin123`

---

### Arquivo: `package.json`
Este arquivo define as dependências estritamente necessárias para o projeto.

```json
{
  "name": "sistema-usuarios",
  "version": "1.0.0",
  "description": "Sistema de cadastro de usuários com autenticação",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "bcrypt": "^5.1.1",
    "cookie-parser": "^1.4.6",
    "express": "^4.18.2",
    "jsonwebtoken": "^9.0.2",
    "sqlite3": "^5.1.6"
  }
}
```

---

### Arquivo: `server.js`
Este é o backend da aplicação. Ele gerencia o banco de dados SQLite, as rotas da API e o controle de acesso.

```javascript
const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const cookieParser = require('cookie-parser');
const path = require('path');

const app = express();
const PORT = 3000;
const SECRET_KEY = 'chave_secreta_super_segura_para_jwt'; // Em produção, usar variável de ambiente

// Middlewares
app.use(express.json());
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

// Configuração do Banco de Dados SQLite
const db = new sqlite3.Database('./database.sqlite', (err) => {
    if (err) console.error('Erro ao abrir o banco de dados:', err.message);
    else console.log('Conectado ao banco de dados SQLite.');
});

// Inicialização do Banco de Dados
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )`);

    // Cria usuário admin padrão se o banco estiver vazio (para permitir o primeiro login)
    db.get("SELECT COUNT(*) AS count FROM users", async (err, row) => {
        if (row.count === 0) {
            const saltRounds = 10;
            const hashedPassword = await bcrypt.hash('admin123', saltRounds);
            db.run("INSERT INTO users (username, password) VALUES (?, ?)", ['admin', hashedPassword]);
            console.log('Usuário padrão criado -> admin : admin123');
        }
    });
});

// Middleware de Autenticação
const authenticate = (req, res, next) => {
    const token = req.cookies.token;
    if (!token) return res.status(401).json({ error: 'Acesso negado. Faça login.' });

    try {
        const decoded = jwt.verify(token, SECRET_KEY);
        req.user = decoded;
        next();
    } catch (err) {
        res.status(401).json({ error: 'Token inválido ou expirado.' });
    }
};

// --- ROTAS DE AUTENTICAÇÃO ---

app.post('/api/login', (req, res) => {
    const { username, password } = req.body;
    db.get("SELECT * FROM users WHERE username = ?", [username], async (err, user) => {
        if (err) return res.status(500).json({ error: 'Erro no servidor' });
        if (!user) return res.status(401).json({ error: 'Credenciais inválidas' });

        const match = await bcrypt.compare(password, user.password);
        if (!match) return res.status(401).json({ error: 'Credenciais inválidas' });

        const token = jwt.sign({ id: user.id, username: user.username }, SECRET_KEY, { expiresIn: '1h' });
        
        // Armazena o token em um cookie HttpOnly para segurança contra XSS
        res.cookie('token', token, { httpOnly: true, secure: false }); // secure: true em HTTPS
        res.json({ message: 'Login realizado com sucesso', username: user.username });
    });
});

app.post('/api/logout', (req, res) => {
    res.clearCookie('token');
    res.json({ message: 'Logout realizado com sucesso' });
});

app.get('/api/me', authenticate, (req, res) => {
    res.json({ username: req.user.username });
});

// --- ROTAS DE CRUD DE USUÁRIOS ---

// Listagem Pública (GET)
app.get('/api/users', (req, res) => {
    db.all("SELECT id, username FROM users", [], (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        res.json(rows);
    });
});

// Cadastro (POST) - Requer Autenticação
app.post('/api/users', authenticate, async (req, res) => {
    const { username, password } = req.body;
    if (!username || !password) return res.status(400).json({ error: 'Usuário e senha são obrigatórios' });

    try {
        const hashedPassword = await bcrypt.hash(password, 10);
        db.run("INSERT INTO users (username, password) VALUES (?, ?)", [username, hashedPassword], function(err) {
            if (err) return res.status(400).json({ error: 'Usuário já existe ou erro no banco' });
            res.status(201).json({ id: this.lastID, username });
        });
    } catch (err) {
        res.status(500).json({ error: 'Erro ao processar senha' });
    }
});

// Edição (PUT) - Requer Autenticação
app.put('/api/users/:id', authenticate, async (req, res) => {
    const { username, password } = req.body;
    const { id } = req.params;

    if (!username && !password) return res.status(400).json({ error: 'Nada para atualizar' });

    if (password) {
        const hashedPassword = await bcrypt.hash(password, 10);
        db.run("UPDATE users SET username = ?, password = ? WHERE id = ?", [username, hashedPassword, id], function(err) {
            if (err) return res.status(400).json({ error: err.message });
            res.json({ message: 'Usuário atualizado com sucesso' });
        });
    } else {
        db.run("UPDATE users SET username = ? WHERE id = ?", [username, id], function(err) {
            if (err) return res.status(400).json({ error: err.message });
            res.json({ message: 'Usuário atualizado com sucesso' });
        });
    }
});

// Remoção (DELETE) - Requer Autenticação
app.delete('/api/users/:id', authenticate, (req, res) => {
    const { id } = req.params;
    db.run("DELETE FROM users WHERE id = ?", id, function(err) {
        if (err) return res.status(500).json({ error: err.message });
        res.json({ message: 'Usuário removido com sucesso' });
    });
});

app.listen(PORT, () => {
    console.log(`Servidor rodando em http://localhost:${PORT}`);
});
```

---

### Arquivo: `public/index.html`
Crie uma pasta chamada `public` no mesmo diretório do `server.js` e salve este arquivo dentro dela. Esta é a interface do usuário.

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema de Usuários</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f9; }
        .container { max-width: 800px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        h1, h2 { color: #333; }
        .panel { border: 1px solid #ccc; padding: 15px; margin-bottom: 20px; border-radius: 5px; }
        input { padding: 8px; margin: 5px 0; width: calc(100% - 18px); }
        button { padding: 10px; background: #28a745; color: white; border: none; cursor: pointer; border-radius: 4px; }
        button:hover { background: #218838; }
        .btn-danger { background: #dc3545; }
        .btn-danger:hover { background: #c82333; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .hidden { display: none; }
    </style>
</head>
<body>

<div class="container">
    <h1>Sistema de Usuários</h1>
    
    <!-- Painel de Login -->
    <div id="loginPanel" class="panel">
        <h2>Login (Acesso Restrito)</h2>
        <input type="text" id="loginUser" placeholder="Usuário">
        <input type="password" id="loginPass" placeholder="Senha">
        <button onclick="login()">Entrar</button>
    </div>

    <!-- Painel de Administração (Oculto por padrão) -->
    <div id="adminPanel" class="panel hidden">
        <h2>Bem-vindo, <span id="loggedUser"></span>!</h2>
        <button onclick="logout()" class="btn-danger">Sair</button>
        
        <hr>
        <h3>Cadastrar / Editar Usuário</h3>
        <input type="hidden" id="editId">
        <input type="text" id="regUser" placeholder="Novo Usuário">
        <input type="password" id="regPass" placeholder="Nova Senha">
        <button onclick="saveUser()">Salvar Usuário</button>
        <button onclick="cancelEdit()" class="hidden" id="btnCancel">Cancelar Edição</button>
    </div>

    <!-- Listagem Pública -->
    <div class="panel">
        <h2>Lista de Usuários (Pública)</h2>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Usuário</th>
                    <th id="actionHeader" class="hidden">Ações</th>
                </tr>
            </thead>
            <tbody id="userTableBody"></tbody>
        </table>
    </div>
</div>

<script>
    let isAuthenticated = false;

    // Verifica se o usuário está logado ao carregar a página
    async function checkAuth() {
        const res = await fetch('/api/me');
        if (res.ok) {
            const data = await res.json();
            isAuthenticated = true;
            document.getElementById('loggedUser').innerText = data.username;
            document.getElementById('loginPanel').classList.add('hidden');
            document.getElementById('adminPanel').classList.remove('hidden');
            document.getElementById('actionHeader').classList.remove('hidden');
        } else {
            isAuthenticated = false;
            document.getElementById('loginPanel').classList.remove('hidden');
            document.getElementById('adminPanel').classList.add('hidden');
            document.getElementById('actionHeader').classList.add('hidden');
        }
        loadUsers();
    }

    async function login() {
        const u = document.getElementById('loginUser').value;
        const p = document.getElementById('loginPass').value;
        const res = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: u, password: p })
        });
        if (res.ok) {
            document.getElementById('loginUser').value = '';
            document.getElementById('loginPass').value = '';
            checkAuth();
        } else {
            alert('Credenciais inválidas!');
        }
    }

    async function logout() {
        await fetch('/api/logout', { method: 'POST' });
        checkAuth();
    }

    async function loadUsers() {
        const res = await fetch('/api/users');
        const users = await res.json();
        const tbody = document.getElementById('userTableBody');
        tbody.innerHTML = '';
        
        users.forEach(user => {
            let tr = document.createElement('tr');
            let actions = isAuthenticated ? 
                `<td>
                    <button onclick="editUser(${user.id}, '${user.username}')">Editar</button>
                    <button class="btn-danger" onclick="deleteUser(${user.id})">Remover</button>
                 </td>` : '';
            
            tr.innerHTML = `<td>${user.id}</td><td>${user.username}</td>${actions}`;
            tbody.appendChild(tr);
        });
    }

    async function saveUser() {
        const id = document.getElementById('editId').value;
        const u = document.getElementById('regUser').value;
        const p = document.getElementById('regPass').value;
        
        const method = id ? 'PUT' : 'POST';
        const url = id ? `/api/users/${id}` : '/api/users';

        const res = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: u, password: p })
        });

        if (res.ok) {
            cancelEdit();
            loadUsers();
        } else {
            const data = await res.json();
            alert('Erro: ' + data.error);
        }
    }

    function editUser(id, username) {
        document.getElementById('editId').value = id;
        document.getElementById('regUser').value = username;
        document.getElementById('regPass').value = '';
        document.getElementById('btnCancel').classList.remove('hidden');
    }

    function cancelEdit() {
        document.getElementById('editId').value = '';
        document.getElementById('regUser').value = '';
        document.getElementById('regPass').value = '';
        document.getElementById('btnCancel').classList.add('hidden');
    }

    async function deleteUser(id) {
        if (!confirm('Tem certeza que deseja remover este usuário?')) return;
        const res = await fetch(`/api/users/${id}`, { method: 'DELETE' });
        if (res.ok) loadUsers();
        else alert('Erro ao remover usuário.');
    }

    // Inicialização
    checkAuth();
</script>
</body>
</html>
```