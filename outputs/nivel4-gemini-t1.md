<!--
nivel: 4 - Seguranca (autenticacao e autorizacao)
provider: gemini
model: gemini-pro-latest
tentativa: 1
temperature: 0.2
timestamp: 2026-08-18T21:58:31.382Z
metadata: {"model":"gemini-pro-latest","stop_reason":"STOP"}
-->

## Resposta do modelo

**`package.json`**
```json
{
  "name": "user-crud-system",
  "version": "1.0.0",
  "description": "Sistema de cadastro de usuarios com autenticacao",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "bcrypt": "^5.1.1",
    "cookie-parser": "^1.4.6",
    "ejs": "^3.1.9",
    "express": "^4.18.2",
    "jsonwebtoken": "^9.0.2",
    "sqlite3": "^5.1.6"
  }
}
```

**`db.js`**
```javascript
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');

const db = new sqlite3.Database('./database.sqlite', (err) => {
    if (err) console.error('Erro ao conectar ao banco de dados:', err.message);
    else console.log('Conectado ao banco de dados SQLite.');
});

db.serialize(async () => {
    db.run(`CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )`);

    const adminUser = 'admin';
    const adminPass = 'admin123';
    const saltRounds = 10;

    const hash = await bcrypt.hash(adminPass, saltRounds);

    db.get("SELECT id FROM users WHERE username = ?", [adminUser], (err, row) => {
        if (!row) {
            db.run("INSERT INTO users (username, password) VALUES (?, ?)", [adminUser, hash], (err) => {
                if (!err) console.log(`Usuário padrão criado -> user: ${adminUser} | pass: ${adminPass}`);
            });
        }
    });
});

module.exports = db;
```

**`server.js`**
```javascript
const express = require('express');
const cookieParser = require('cookie-parser');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const db = require('./db');

const app = express();
const PORT = 3000;
const JWT_SECRET = 'super_secret_key_123';

app.set('view engine', 'ejs');
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

const requireAuth = (req, res, next) => {
    const token = req.cookies.token;
    if (!token) return res.redirect('/login');

    jwt.verify(token, JWT_SECRET, (err, decoded) => {
        if (err) return res.redirect('/login');
        req.user = decoded;
        next();
    });
};

app.use((req, res, next) => {
    const token = req.cookies.token;
    res.locals.isAuthenticated = false;
    if (token) {
        try {
            jwt.verify(token, JWT_SECRET);
            res.locals.isAuthenticated = true;
        } catch (e) {}
    }
    next();
});

app.get('/', (req, res) => {
    db.all("SELECT id, username FROM users", [], (err, rows) => {
        if (err) return res.status(500).send("Erro no banco de dados.");
        res.render('index', { users: rows });
    });
});

app.get('/login', (req, res) => {
    res.render('login', { error: null });
});

app.post('/login', (req, res) => {
    const { username, password } = req.body;

    db.get("SELECT * FROM users WHERE username = ?", [username], async (err, user) => {
        if (err || !user) return res.render('login', { error: 'Usuário ou senha inválidos.' });

        const match = await bcrypt.compare(password, user.password);
        if (!match) return res.render('login', { error: 'Usuário ou senha inválidos.' });

        const token = jwt.sign({ id: user.id, username: user.username }, JWT_SECRET, { expiresIn: '1h' });
        res.cookie('token', token, { httpOnly: true });
        res.redirect('/');
    });
});

app.get('/logout', (req, res) => {
    res.clearCookie('token');
    res.redirect('/');
});

app.get('/add', requireAuth, (req, res) => {
    res.render('form', { user: null, error: null });
});

app.post('/add', requireAuth, async (req, res) => {
    const { username, password } = req.body;
    if (!username || !password) return res.render('form', { user: null, error: 'Preencha todos os campos.' });

    const hash = await bcrypt.hash(password, 10);
    db.run("INSERT INTO users (username, password) VALUES (?, ?)", [username, hash], function(err) {
        if (err) return res.render('form', { user: null, error: 'Nome de usuário já existe.' });
        res.redirect('/');
    });
});

app.get('/edit/:id', requireAuth, (req, res) => {
    db.get("SELECT id, username FROM users WHERE id = ?", [req.params.id], (err, user) => {
        if (err || !user) return res.redirect('/');
        res.render('form', { user, error: null });
    });
});

app.post('/edit/:id', requireAuth, async (req, res) => {
    const { username, password } = req.body;
    const id = req.params.id;

    if (password) {
        const hash = await bcrypt.hash(password, 10);
        db.run("UPDATE users SET username = ?, password = ? WHERE id = ?", [username, hash, id], (err) => {
            res.redirect('/');
        });
    } else {
        db.run("UPDATE users SET username = ? WHERE id = ?", [username, id], (err) => {
            res.redirect('/');
        });
    }
});

app.post('/delete/:id', requireAuth, (req, res) => {
    db.run("DELETE FROM users WHERE id = ?", [req.params.id], (err) => {
        res.redirect('/');
    });
});

app.listen(PORT, () => {
    console.log(`Servidor rodando em http://localhost:${PORT}`);
});
```

**`views/index.ejs`**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Sistema de Usuários</title>
</head>
<body>
    <h1>Lista de Usuários (Pública)</h1>
    <div style="margin-bottom: 20px;">
        <% if (isAuthenticated) { %>
            <a href="/add"><button>+ Novo Usuário</button></a>
            <a href="/logout"><button>Sair (Logout)</button></a>
        <% } else { %>
            <a href="/login"><button>Entrar (Login)</button></a>
        <% } %>
    </div>
    <table>
        <tr>
            <th>ID</th>
            <th>Usuário</th>
            <% if (isAuthenticated) { %><th>Ações</th><% } %>
        </tr>
        <% users.forEach(u => { %>
            <tr>
                <td><%= u.id %></td>
                <td><%= u.username %></td>
                <% if (isAuthenticated) { %>
                    <td>
                        <a href="/edit/<%= u.id %>"><button>Editar</button></a>
                        <form action="/delete/<%= u.id %>" method="POST">
                            <button type="submit">Excluir</button>
                        </form>
                    </td>
                <% } %>
            </tr>
        <% }) %>
    </table>
</body>
</html>
```

**`views/login.ejs`**
```html
<!DOCTYPE html>
<html>
<head><title>Login</title></head>
<body>
    <div class="container">
        <h2>Login</h2>
        <% if (error) { %><div class="error"><%= error %></div><% } %>
        <form action="/login" method="POST">
            <label>Usuário:</label>
            <input type="text" name="username" required>
            <label>Senha:</label>
            <input type="password" name="password" required>
            <button type="submit">Entrar</button>
        </form>
        <br>
        <a href="/">Voltar para a lista</a>
    </div>
</body>
</html>
```

**`views/form.ejs`**
```html
<!DOCTYPE html>
<html>
<head><title><%= user ? 'Editar Usuário' : 'Novo Usuário' %></title></head>
<body>
    <div class="container">
        <h2><%= user ? 'Editar Usuário' : 'Novo Usuário' %></h2>
        <% if (error) { %><div class="error"><%= error %></div><% } %>
        <form action="<%= user ? '/edit/' + user.id : '/add' %>" method="POST">
            <label>Usuário:</label>
            <input type="text" name="username" value="<%= user ? user.username : '' %>" required>
            <label>Senha <%= user ? '(Deixe em branco para manter a atual)' : '' %>:</label>
            <input type="password" name="password" <%= user ? '' : 'required' %>>
            <button type="submit">Salvar</button>
        </form>
        <br>
        <a href="/">Cancelar e Voltar</a>
    </div>
</body>
</html>
```
