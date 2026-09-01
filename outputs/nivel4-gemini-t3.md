<!--
nivel: 4 - Seguranca (autenticacao e autorizacao)
provider: gemini
model: gemini-3.1-pro-preview
tentativa: 3
temperature: 0.2
timestamp: 2026-08-31T08:59:24.596Z
metadata: {"model":"gemini-3.1-pro-preview","usage":{"promptTokenCount":224,"candidatesTokenCount":3971,"totalTokenCount":5522,"promptTokensDetails":[{"modality":"TEXT","tokenCount":224}],"thoughtsTokenCount":1327,"serviceTier":"standard"},"finish_reason":"STOP"}
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

Olá! Como engenheiro de software, projetei a solução solicitada utilizando **Node.js** com o micro-framework **Express** (padrão da indústria para roteamento HTTP), **SQLite3** para persistência, **Bcrypt** para hash e salt de senhas, e **JSON Web Tokens (JWT)** armazenados em cookies HTTP-only para controle de sessão seguro.

Como a restrição exige que *apenas usuários autenticados possam cadastrar novos registros*, tomei a decisão arquitetural de **criar um usuário administrador padrão** na inicialização do banco de dados. Caso contrário, seria impossível cadastrar o primeiro usuário.

Abaixo estão as instruções de execução e os códigos-fonte.

### Instruções de Execução

1. **Pré-requisitos:** Certifique-se de ter o Node.js instalado (versão 14+ recomendada).
2. **Crie um diretório para o projeto** e entre nele:
   ```bash
   mkdir sistema-usuarios
   cd sistema-usuarios
   ```
3. **Crie os arquivos** listados abaixo com seus respectivos conteúdos.
4. **Instale as dependências:**
   ```bash
   npm install
   ```
5. **Inicie o servidor:**
   ```bash
   node server.js
   ```
6. **Acesse no navegador:** `http://localhost:3000`
7. **Credenciais padrão (criadas automaticamente):**
   - **Usuário:** `admin`
   - **Senha:** `admin123`

---

### Arquivos do Projeto

**`package.json`**
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

**`server.js`**
```javascript
// Decisão: Utilização do Express para roteamento, bcrypt para hash seguro, 
// jsonwebtoken para tokens de sessão e cookie-parser para facilitar o tráfego do token.

const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const cookieParser = require('cookie-parser');
const path = require('path');

const app = express();
const PORT = 3000;
const JWT_SECRET = 'chave_secreta_super_segura_para_jwt_123'; // Em produção, usar variável de ambiente

// Middlewares
app.use(express.json());
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

// Configuração do Banco de Dados SQLite
const db = new sqlite3.Database('./database.sqlite', (err) => {
    if (err) console.error('Erro ao conectar ao banco:', err.message);
    else console.log('Conectado ao banco de dados SQLite.');
});

// Inicialização do Banco de Dados
db.serialize(async () => {
    db.run(`CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )`);

    // Decisão: Criar um usuário admin padrão se o banco estiver vazio, 
    // pois apenas usuários logados podem criar outros usuários.
    db.get("SELECT COUNT(*) as count FROM users", async (err, row) => {
        if (row.count === 0) {
            const saltRounds = 10;
            const hashedPassword = await bcrypt.hash('admin123', saltRounds);
            db.run("INSERT INTO users (username, password) VALUES (?, ?)", ['admin', hashedPassword]);
            console.log('Usuário padrão criado -> admin : admin123');
        }
    });
});

// Middleware de Autenticação
const authenticateToken = (req, res, next) => {
    const token = req.cookies.token;
    if (!token) return res.status(401).json({ error: 'Acesso negado. Faça login.' });

    jwt.verify(token, JWT_SECRET, (err, user) => {
        if (err) return res.status(403).json({ error: 'Token inválido ou expirado.' });
        req.user = user;
        next();
    });
};

// ================= ROTAS DE AUTENTICAÇÃO =================

app.post('/api/login', (req, res) => {
    const { username, password } = req.body;

    db.get("SELECT * FROM users WHERE username = ?", [username], async (err, user) => {
        if (err) return res.status(500).json({ error: 'Erro no servidor' });
        if (!user) return res.status(401).json({ error: 'Usuário ou senha incorretos' });

        const validPassword = await bcrypt.compare(password, user.password);
        if (!validPassword) return res.status(401).json({ error: 'Usuário ou senha incorretos' });

        const token = jwt.sign({ id: user.id, username: user.username }, JWT_SECRET, { expiresIn: '2h' });
        
        // Armazena o token em um cookie HTTP-only para segurança
        res.cookie('token', token, { httpOnly: true, secure: false }); // secure: true em HTTPS
        res.json({ message: 'Login realizado com sucesso', username: user.username });
    });
});

app.post('/api/logout', (req, res) => {
    res.clearCookie('token');
    res.json({ message: 'Logout realizado com sucesso' });
});

app.get('/api/me', authenticateToken, (req, res) => {
    res.json({ username: req.user.username });
});

// ================= ROTAS DE USUÁRIOS (CRUD) =================

// LISTAGEM PÚBLICA (Não usa o middleware authenticateToken)
app.get('/api/users', (req, res) => {
    db.all("SELECT id, username FROM users", [], (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        res.json(rows);
    });
});

// CADASTRO (Protegido)
app.post('/api/users', authenticateToken, async (req, res) => {
    const { username, password } = req.body;
    if (!username || !password) return res.status(400).json({ error: 'Usuário e senha são obrigatórios' });

    try {
        const hashedPassword = await bcrypt.hash(password, 10);
        db.run("INSERT INTO users (username, password) VALUES (?, ?)", [username, hashedPassword], function(err) {
            if (err) return res.status(400).json({ error: 'Usuário já existe ou erro no banco' });
            res.status(201).json({ id: this.lastID, username });
        });
    } catch (error) {
        res.status(500).json({ error: 'Erro ao processar senha' });
    }
});

// EDIÇÃO (Protegido)
app.put('/api/users/:id', authenticateToken, async (req, res) => {
    const { username, password } = req.body;
    const { id } = req.params;

    try {
        let query = "UPDATE users SET username = ? WHERE id = ?";
        let params = [username, id];

        if (password) {
            const hashedPassword = await bcrypt.hash(password, 10);
            query = "UPDATE users SET username = ?, password = ? WHERE id = ?";
            params = [username, hashedPassword, id];
        }

        db.run(query, params, function(err) {
            if (err) return res.status(400).json({ error: 'Erro ao atualizar usuário' });
            if (this.changes === 0) return res.status(404).json({ error: 'Usuário não encontrado' });
            res.json({ message: 'Usuário atualizado com sucesso' });
        });
    } catch (error) {
        res.status(500).json({ error: 'Erro ao processar requisição' });
    }
});

// REMOÇÃO (Protegido)
app.delete('/api/users/:id', authenticateToken, (req, res) => {
    const { id } = req.params;
    db.run("DELETE FROM users WHERE id = ?", id, function(err) {
        if (err) return res.status(500).json({ error: 'Erro ao deletar usuário' });
        if (this.changes === 0) return res.status(404).json({ error: 'Usuário não encontrado' });
        res.json({ message: 'Usuário removido com sucesso' });
    });
});

app.listen(PORT, () => {
    console.log(`Servidor rodando em http://localhost:${PORT}`);
});
```

**`public/index.html`**
*(Crie uma pasta chamada `public` na raiz do projeto e coloque este arquivo dentro dela)*
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
        .hidden { display: none; }
        input, button { padding: 10px; margin: 5px 0; width: 100%; box-sizing: border-box; }
        button { background-color: #007BFF; color: white; border: none; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        .danger { background-color: #dc3545; }
        .danger:hover { background-color: #c82333; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 10px; border: 1px solid #ddd; text-align: left; }
        .actions button { width: auto; padding: 5px 10px; margin-right: 5px; }
    </style>
</head>
<body>

<div class="container">
    <h1>Sistema de Usuários</h1>
    
    <!-- Área de Login -->
    <div id="loginArea">
        <h3>Login (Apenas autenticados podem gerenciar)</h3>
        <input type="text" id="loginUser" placeholder="Usuário">
        <input type="password" id="loginPass" placeholder="Senha">
        <button onclick="login()">Entrar</button>
    </div>

    <!-- Área Logada -->
    <div id="loggedArea" class="hidden">
        <h3>Bem-vindo, <span id="loggedUsername"></span>!</h3>
        <button class="danger" onclick="logout()">Sair</button>
        
        <hr>
        <h3>Gerenciar Usuário</h3>
        <input type="hidden" id="userId">
        <input type="text" id="manageUser" placeholder="Novo Usuário">
        <input type="password" id="managePass" placeholder="Nova Senha (deixe em branco para não alterar na edição)">
        <button id="btnSave" onclick="saveUser()">Cadastrar Usuário</button>
        <button id="btnCancel" class="hidden" onclick="resetForm()">Cancelar Edição</button>
    </div>

    <hr>
    <!-- Listagem Pública -->
    <h3>Lista de Usuários (Pública)</h3>
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Usuário</th>
                <th id="thActions" class="hidden">Ações</th>
            </tr>
        </thead>
        <tbody id="userTableBody"></tbody>
    </table>
</div>

<script>
    let isAuthenticated = false;

    // Verifica sessão ao carregar
    async function checkSession() {
        const res = await fetch('/api/me');
        if (res.ok) {
            const data = await res.json();
            isAuthenticated = true;
            document.getElementById('loginArea').classList.add('hidden');
            document.getElementById('loggedArea').classList.remove('hidden');
            document.getElementById('loggedUsername').innerText = data.username;
            document.getElementById('thActions').classList.remove('hidden');
        } else {
            isAuthenticated = false;
            document.getElementById('loginArea').classList.remove('hidden');
            document.getElementById('loggedArea').classList.add('hidden');
            document.getElementById('thActions').classList.add('hidden');
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
            checkSession();
        } else {
            alert('Falha no login');
        }
    }

    async function logout() {
        await fetch('/api/logout', { method: 'POST' });
        checkSession();
    }

    async function loadUsers() {
        const res = await fetch('/api/users');
        const users = await res.json();
        const tbody = document.getElementById('userTableBody');
        tbody.innerHTML = '';
        
        users.forEach(user => {
            let tr = document.createElement('tr');
            let actionsHtml = isAuthenticated ? 
                `<td class="actions">
                    <button onclick="editUser(${user.id}, '${user.username}')">Editar</button>
                    <button class="danger" onclick="deleteUser(${user.id})">Excluir</button>
                </td>` : '';
            
            tr.innerHTML = `<td>${user.id}</td><td>${user.username}</td>${actionsHtml}`;
            tbody.appendChild(tr);
        });
    }

    async function saveUser() {
        const id = document.getElementById('userId').value;
        const u = document.getElementById('manageUser').value;
        const p = document.getElementById('managePass').value;
        
        const method = id ? 'PUT' : 'POST';
        const url = id ? `/api/users/${id}` : '/api/users';
        
        const res = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: u, password: p })
        });

        if (res.ok) {
            resetForm();
            loadUsers();
        } else {
            const err = await res.json();
            alert('Erro: ' + err.error);
        }
    }

    function editUser(id, username) {
        document.getElementById('userId').value = id;
        document.getElementById('manageUser').value = username;
        document.getElementById('managePass').value = '';
        document.getElementById('btnSave').innerText = 'Salvar Alterações';
        document.getElementById('btnCancel').classList.remove('hidden');
    }

    function resetForm() {
        document.getElementById('userId').value = '';
        document.getElementById('manageUser').value = '';
        document.getElementById('managePass').value = '';
        document.getElementById('btnSave').innerText = 'Cadastrar Usuário';
        document.getElementById('btnCancel').classList.add('hidden');
    }

    async function deleteUser(id) {
        if (!confirm('Tem certeza que deseja excluir?')) return;
        const res = await fetch(`/api/users/${id}`, { method: 'DELETE' });
        if (res.ok) loadUsers();
        else alert('Erro ao excluir');
    }

    // Inicializa
    checkSession();
</script>
</body>
</html>
```