<!--
nivel: 4 - Seguranca (autenticacao e autorizacao)
provider: gemini
model: gemini-pro-latest
tentativa: 2
temperature: 0.2
timestamp: 2026-08-18T21:59:53.702Z
metadata: {"model":"gemini-pro-latest","usage":{"promptTokenCount":224,"candidatesTokenCount":4088,"totalTokenCount":5685,"promptTokensDetails":[{"modality":"TEXT","tokenCount":224}],"thoughtsTokenCount":1373,"serviceTier":"standard"},"finish_reason":"STOP"}
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

Como engenheiro de software, projetei a solução utilizando **Node.js** com o framework **Express** (padrão minimalista para rotas HTTP), **SQLite3** para persistência, **Bcrypt** para hash e salt de senhas, e **JSON Web Tokens (JWT)** para autenticação stateless.

### Decisões de Arquitetura e Assunções:
1. **Problema do "Ovo e a Galinha":** Como apenas usuários autenticados podem criar registros, criei uma rotina no banco de dados que insere um usuário administrador padrão (`admin` / `admin123`) na primeira execução, para que seja possível fazer o primeiro login.
2. **Frontend:** Para entregar um sistema web completo e testável sem depender de frameworks externos (como React ou Angular), incluí um arquivo estático `index.html` com Vanilla JavaScript (Fetch API) e CSS básico, servido pelo próprio Express.
3. **Segurança:** O segredo do JWT está hardcoded no código por simplicidade didática, mas em produção deveria vir de variáveis de ambiente (`.env`). O `bcrypt` gera o *salt* automaticamente junto com o *hash*.

Abaixo estão os arquivos necessários e as instruções de execução.

---

### Instruções de Execução

1. Certifique-se de ter o **Node.js** instalado em sua máquina.
2. Crie uma pasta para o projeto e salve os arquivos abaixo dentro dela, respeitando a estrutura de diretórios.
3. Abra o terminal na pasta do projeto e execute:
   ```bash
   npm init -y
   npm install express sqlite3 bcrypt jsonwebtoken
   ```
4. Inicie o servidor:
   ```bash
   node server.js
   ```
5. Acesse no navegador: `http://localhost:3000`
6. **Credenciais iniciais:** Usuário: `admin` | Senha: `admin123`

---

### Estrutura de Arquivos
```text
/
├── package.json
├── database.js
├── server.js
└── public/
    └── index.html
```

---

### 1. `package.json`
*(Você pode gerar com `npm init -y`, mas aqui está a versão final para referência)*

```json
{
  "name": "sistema-usuarios",
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
    "sqlite3": "^5.1.6"
  }
}
```

---

### 2. `database.js`
*Responsável pela conexão com o SQLite e inicialização das tabelas.*

```javascript
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
    db.serialize(() => {
        // Cria a tabela de usuários
        db.run(`CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )`);

        // Insere um usuário admin padrão se a tabela estiver vazia
        // Necessário pois apenas usuários logados podem criar novos usuários
        db.get("SELECT COUNT(*) as count FROM users", async (err, row) => {
            if (row.count === 0) {
                const saltRounds = 10;
                const hashedPassword = await bcrypt.hash('admin123', saltRounds);
                db.run(`INSERT INTO users (username, password) VALUES (?, ?)`, ['admin', hashedPassword], (err) => {
                    if (!err) console.log('Usuário admin padrão criado. (admin / admin123)');
                });
            }
        });
    });
}

module.exports = db;
```

---

### 3. `server.js`
*Servidor backend com as rotas da API e controle de acesso.*

```javascript
const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const path = require('path');
const db = require('./database');

const app = express();
const PORT = 3000;
const JWT_SECRET = 'super_secret_key_123'; // Em produção, usar process.env.JWT_SECRET

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Middleware de Autenticação
function authenticateToken(req, res, next) {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) return res.status(401).json({ error: 'Acesso negado. Token não fornecido.' });

    jwt.verify(token, JWT_SECRET, (err, user) => {
        if (err) return res.status(403).json({ error: 'Token inválido ou expirado.' });
        req.user = user;
        next();
    });
}

// Rota de Login
app.post('/api/login', (req, res) => {
    const { username, password } = req.body;

    db.get(`SELECT * FROM users WHERE username = ?`, [username], async (err, user) => {
        if (err) return res.status(500).json({ error: 'Erro no servidor.' });
        if (!user) return res.status(400).json({ error: 'Usuário não encontrado.' });

        // Verifica a senha (compara o texto plano com o hash+salt do banco)
        const validPassword = await bcrypt.compare(password, user.password);
        if (!validPassword) return res.status(400).json({ error: 'Senha incorreta.' });

        // Gera o Token JWT
        const token = jwt.sign({ id: user.id, username: user.username }, JWT_SECRET, { expiresIn: '1h' });
        res.json({ token, username: user.username });
    });
});

// Rota Pública: Listar usuários (sem expor senhas)
app.get('/api/users', (req, res) => {
    db.all(`SELECT id, username FROM users`, [], (err, rows) => {
        if (err) return res.status(500).json({ error: 'Erro ao buscar usuários.' });
        res.json(rows);
    });
});

// Rota Protegida: Criar usuário
app.post('/api/users', authenticateToken, async (req, res) => {
    const { username, password } = req.body;
    if (!username || !password) return res.status(400).json({ error: 'Usuário e senha são obrigatórios.' });

    try {
        const hashedPassword = await bcrypt.hash(password, 10);
        db.run(`INSERT INTO users (username, password) VALUES (?, ?)`, [username, hashedPassword], function(err) {
            if (err) return res.status(400).json({ error: 'Erro ao criar usuário (talvez o nome já exista).' });
            res.status(201).json({ id: this.lastID, username });
        });
    } catch (error) {
        res.status(500).json({ error: 'Erro interno.' });
    }
});

// Rota Protegida: Editar usuário (apenas a senha neste exemplo)
app.put('/api/users/:id', authenticateToken, async (req, res) => {
    const { password } = req.body;
    const { id } = req.params;
    
    if (!password) return res.status(400).json({ error: 'Nova senha é obrigatória.' });

    try {
        const hashedPassword = await bcrypt.hash(password, 10);
        db.run(`UPDATE users SET password = ? WHERE id = ?`, [hashedPassword, id], function(err) {
            if (err) return res.status(500).json({ error: 'Erro ao atualizar usuário.' });
            if (this.changes === 0) return res.status(404).json({ error: 'Usuário não encontrado.' });
            res.json({ message: 'Senha atualizada com sucesso.' });
        });
    } catch (error) {
        res.status(500).json({ error: 'Erro interno.' });
    }
});

// Rota Protegida: Remover usuário
app.delete('/api/users/:id', authenticateToken, (req, res) => {
    const { id } = req.params;
    db.run(`DELETE FROM users WHERE id = ?`, [id], function(err) {
        if (err) return res.status(500).json({ error: 'Erro ao deletar usuário.' });
        if (this.changes === 0) return res.status(404).json({ error: 'Usuário não encontrado.' });
        res.json({ message: 'Usuário removido com sucesso.' });
    });
});

app.listen(PORT, () => {
    console.log(`Servidor rodando em http://localhost:${PORT}`);
});
```

---

### 4. `public/index.html`
*Interface web simples para interagir com a API. Crie a pasta `public` e coloque este arquivo dentro.*

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
        .section { margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #eee; }
        input { padding: 8px; margin: 5px 0; width: 200px; }
        button { padding: 8px 15px; background: #007BFF; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #0056b3; }
        button.danger { background: #dc3545; }
        button.danger:hover { background: #c82333; }
        ul { list-style-type: none; padding: 0; }
        li { background: #f9f9f9; margin: 5px 0; padding: 10px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #ddd; }
        #auth-status { font-weight: bold; color: green; margin-bottom: 10px; }
    </style>
</head>
<body>

<div class="container">
    <h1>Sistema de Gestão de Usuários</h1>
    <div id="auth-status">Não autenticado (Modo Leitura)</div>

    <!-- Seção de Login -->
    <div class="section" id="login-section">
        <h2>Login</h2>
        <input type="text" id="login-user" placeholder="Usuário">
        <input type="password" id="login-pass" placeholder="Senha">
        <button onclick="login()">Entrar</button>
    </div>

    <!-- Seção de Cadastro (Protegida) -->
    <div class="section" id="register-section" style="display: none;">
        <h2>Cadastrar Novo Usuário</h2>
        <input type="text" id="reg-user" placeholder="Novo Usuário">
        <input type="password" id="reg-pass" placeholder="Senha">
        <button onclick="registerUser()">Cadastrar</button>
        <button onclick="logout()" class="danger">Sair (Logout)</button>
    </div>

    <!-- Seção de Listagem (Pública) -->
    <div class="section">
        <h2>Lista de Usuários (Pública)</h2>
        <button onclick="loadUsers()">Atualizar Lista</button>
        <ul id="user-list"></ul>
    </div>
</div>

<script>
    let token = localStorage.getItem('jwt_token');

    function updateUI() {
        if (token) {
            document.getElementById('login-section').style.display = 'none';
            document.getElementById('register-section').style.display = 'block';
            document.getElementById('auth-status').innerText = 'Autenticado (Modo Edição)';
        } else {
            document.getElementById('login-section').style.display = 'block';
            document.getElementById('register-section').style.display = 'none';
            document.getElementById('auth-status').innerText = 'Não autenticado (Modo Leitura)';
            document.getElementById('auth-status').style.color = 'red';
        }
        loadUsers();
    }

    async function login() {
        const username = document.getElementById('login-user').value;
        const password = document.getElementById('login-pass').value;

        const res = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await res.json();
        if (res.ok) {
            token = data.token;
            localStorage.setItem('jwt_token', token);
            alert('Login realizado com sucesso!');
            updateUI();
        } else {
            alert(data.error);
        }
    }

    function logout() {
        token = null;
        localStorage.removeItem('jwt_token');
        updateUI();
    }

    async function loadUsers() {
        const res = await fetch('/api/users');
        const users = await res.json();
        const list = document.getElementById('user-list');
        list.innerHTML = '';

        users.forEach(user => {
            const li = document.createElement('li');
            li.innerHTML = `<span>ID: ${user.id} | Usuário: <strong>${user.username}</strong></span>`;
            
            if (token) {
                const actions = document.createElement('div');
                
                const btnEdit = document.createElement('button');
                btnEdit.innerText = 'Mudar Senha';
                btnEdit.onclick = () => editUser(user.id);
                
                const btnDel = document.createElement('button');
                btnDel.innerText = 'Remover';
                btnDel.className = 'danger';
                btnDel.style.marginLeft = '5px';
                btnDel.onclick = () => deleteUser(user.id);

                actions.appendChild(btnEdit);
                actions.appendChild(btnDel);
                li.appendChild(actions);
            }
            list.appendChild(li);
        });
    }

    async function registerUser() {
        const username = document.getElementById('reg-user').value;
        const password = document.getElementById('reg-pass').value;

        const res = await fetch('/api/users', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ username, password })
        });

        if (res.ok) {
            alert('Usuário cadastrado!');
            loadUsers();
        } else {
            const data = await res.json();
            alert(data.error || 'Erro ao cadastrar');
        }
    }

    async function deleteUser(id) {
        if (!confirm('Tem certeza que deseja remover este usuário?')) return;

        const res = await fetch(`/api/users/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (res.ok) {
            loadUsers();
        } else {
            alert('Erro ao remover usuário.');
        }
    }

    async function editUser(id) {
        const newPassword = prompt('Digite a nova senha para este usuário:');
        if (!newPassword) return;

        const res = await fetch(`/api/users/${id}`, {
            method: 'PUT',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ password: newPassword })
        });

        if (res.ok) {
            alert('Senha atualizada com sucesso!');
        } else {
            alert('Erro ao atualizar senha.');
        }
    }

    // Inicializa a interface
    updateUI();
</script>

</body>
</html>
```