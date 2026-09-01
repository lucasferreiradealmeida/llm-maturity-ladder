<!--
nivel: 4 - Seguranca (autenticacao e autorizacao)
provider: groq
model: openai/gpt-oss-120b
tentativa: 3
temperature: 0.2
timestamp: 2026-08-31T09:08:28.859Z
metadata: {"model":"openai/gpt-oss-120b","usage":{"queue_time":0.216628686,"prompt_tokens":275,"prompt_time":0.016015283,"completion_tokens":4511,"completion_time":9.512253093,"total_tokens":4786,"total_time":9.528268376,"completion_tokens_details":{"reasoning_tokens":53}},"finish_reason":"stop"}
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

**📂 Estrutura do projeto**

```
user‑auth‑sqlite/
│
├─ package.json
├─ package-lock.json        # (gerado após npm install)
├─ README.md
├─ .gitignore
│
├─ db.js                    # camada de acesso ao SQLite
├─ app.js                   # ponto de entrada (Express)
├─ routes.js                # rotas da API + páginas HTML simples
│
└─ public/
   ├─ index.html            # página pública (listagem de usuários)
   ├─ login.html            # formulário de login
   ├─ register.html         # formulário de cadastro
   └─ style.css
```

---

## 1️⃣  `package.json`

```json
{
  "name": "user-auth-sqlite",
  "version": "1.0.0",
  "description": "Sistema web simples de cadastro e login com SQLite",
  "main": "app.js",
  "scripts": {
    "start": "node app.js",
    "dev": "nodemon app.js"
  },
  "keywords": [
    "express",
    "sqlite",
    "bcrypt",
    "jwt",
    "authentication"
  ],
  "author": "Seu Nome",
  "license": "MIT",
  "dependencies": {
    "bcrypt": "^5.1.1",
    "express": "^4.19.2",
    "jsonwebtoken": "^9.0.2",
    "sqlite3": "^5.1.7"
  },
  "devDependencies": {
    "nodemon": "^3.1.0"
  }
}
```

---

## 2️⃣  `.gitignore`

```gitignore
node_modules/
*.sqlite
.env
```

---

## 3️⃣  `db.js` – camada de acesso ao SQLite

```js
// db.js
// --------------------------
// Cria / abre o arquivo SQLite e exporta funções de acesso.
// O banco tem duas tabelas:
//  - users(id, username, password_hash, salt)
//  - profiles(id, user_id, name, email)   // exemplo de “registro” que só
//                                         // usuários autenticados podem
//                                         // criar/editar/excluir.

const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const DB_PATH = path.join(__dirname, 'data.sqlite');
const db = new sqlite3.Database(DB_PATH);

// Cria as tabelas caso ainda não existam
db.serialize(() => {
  db.run(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      salt TEXT NOT NULL
    )
  `);

  db.run(`
    CREATE TABLE IF NOT EXISTS profiles (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      name TEXT NOT NULL,
      email TEXT NOT NULL,
      FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    )
  `);
});

module.exports = {
  /**
   * Busca um usuário pelo nome de usuário.
   * @param {string} username
   * @returns {Promise<Object|null>}
   */
  getUserByUsername(username) {
    return new Promise((resolve, reject) => {
      db.get(
        `SELECT * FROM users WHERE username = ?`,
        [username],
        (err, row) => (err ? reject(err) : resolve(row))
      );
    });
  },

  /**
   * Insere um novo usuário.
   * @param {string} username
   * @param {string} passwordHash
   * @param {string} salt
   * @returns {Promise<number>} id do usuário inserido
   */
  createUser(username, passwordHash, salt) {
    return new Promise((resolve, reject) => {
      db.run(
        `INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)`,
        [username, passwordHash, salt],
        function (err) {
          err ? reject(err) : resolve(this.lastID);
        }
      );
    });
  },

  /**
   * Busca perfil(s) - usado para a listagem pública.
   * @returns {Promise<Array>}
   */
  listProfiles() {
    return new Promise((resolve, reject) => {
      db.all(
        `SELECT p.id, u.username, p.name, p.email
         FROM profiles p
         JOIN users u ON p.user_id = u.id
         ORDER BY p.id DESC`,
        [],
        (err, rows) => (err ? reject(err) : resolve(rows))
      );
    });
  },

  /**
   * Cria/atualiza/exclui perfil – todas exigem userId (verificado antes).
   */
  createProfile(userId, name, email) {
    return new Promise((resolve, reject) => {
      db.run(
        `INSERT INTO profiles (user_id, name, email) VALUES (?, ?, ?)`,
        [userId, name, email],
        function (err) {
          err ? reject(err) : resolve(this.lastID);
        }
      );
    });
  },

  updateProfile(profileId, userId, name, email) {
    return new Promise((resolve, reject) => {
      db.run(
        `UPDATE profiles SET name = ?, email = ? WHERE id = ? AND user_id = ?`,
        [name, email, profileId, userId],
        function (err) {
          err ? reject(err) : resolve(this.changes);
        }
      );
    });
  },

  deleteProfile(profileId, userId) {
    return new Promise((resolve, reject) => {
      db.run(
        `DELETE FROM profiles WHERE id = ? AND user_id = ?`,
        [profileId, userId],
        function (err) {
          err ? reject(err) : resolve(this.changes);
        }
      );
    });
  }
};
```

---

## 4️⃣  `app.js` – configuração do Express

```js
// app.js
// --------------------------
// Servidor Express que usa JSON Web Tokens (JWT) para autenticação.
// Não usamos nenhum framework extra além do Express e das libs citadas.

const express = require('express');
const path = require('path');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const db = require('./db');

// ------------------- Configurações -------------------
const app = express();
const PORT = process.env.PORT || 3000;
const JWT_SECRET = process.env.JWT_SECRET || 'super_secret_key_change_me';

// Middleware padrão
app.use(express.json());               // parseia corpos JSON
app.use(express.urlencoded({ extended: true })); // para formulários HTML
app.use(express.static(path.join(__dirname, 'public'))); // arquivos estáticos

// ------------------- Helpers -------------------
/**
 * Middleware que verifica o header Authorization: Bearer <token>
 * e anexa `req.user` contendo o payload do JWT (id e username).
 */
function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'Token ausente' });

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) return res.status(403).json({ error: 'Token inválido' });
    req.user = user;
    next();
  });
}

// ------------------- Rotas da API -------------------
const router = require('./routes')(db, bcrypt, jwt, JWT_SECRET, authenticateToken);
app.use('/api', router);

// Página raiz (HTML estático)
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// ------------------- Inicia o servidor -------------------
app.listen(PORT, () => {
  console.log(`🚀 Servidor rodando em http://localhost:${PORT}`);
});
```

---

## 5️⃣  `routes.js` – rotas REST + páginas auxiliares

```js
// routes.js
// --------------------------
// Recebe dependências injetadas (facilita testes) e devolve um Router.

module.exports = (db, bcrypt, jwt, JWT_SECRET, authenticateToken) => {
  const express = require('express');
  const router = express.Router();

  // ---------- 1️⃣ Registro ----------
  router.post('/register', async (req, res) => {
    const { username, password } = req.body;
    if (!username || !password)
      return res.status(400).json({ error: 'username e password são obrigatórios' });

    try {
      const existing = await db.getUserByUsername(username);
      if (existing) return res.status(409).json({ error: 'Usuário já existe' });

      const saltRounds = 12;
      const salt = await bcrypt.genSalt(saltRounds);
      const hash = await bcrypt.hash(password, salt);

      const userId = await db.createUser(username, hash, salt);
      res.status(201).json({ message: 'Usuário criado', userId });
    } catch (e) {
      console.error(e);
      res.status(500).json({ error: 'Erro interno' });
    }
  });

  // ---------- 2️⃣ Login ----------
  router.post('/login', async (req, res) => {
    const { username, password } = req.body;
    if (!username || !password)
      return res.status(400).json({ error: 'username e password são obrigatórios' });

    try {
      const user = await db.getUserByUsername(username);
      if (!user) return res.status(401).json({ error: 'Credenciais inválidas' });

      const match = await bcrypt.compare(password, user.password_hash);
      if (!match) return res.status(401).json({ error: 'Credenciais inválidas' });

      // Payload mínimo
      const payload = { id: user.id, username: user.username };
      const token = jwt.sign(payload, JWT_SECRET, { expiresIn: '2h' });

      res.json({ token });
    } catch (e) {
      console.error(e);
      res.status(500).json({ error: 'Erro interno' });
    }
  });

  // ---------- 3️⃣ Listagem pública ----------
  router.get('/profiles', async (req, res) => {
    try {
      const profiles = await db.listProfiles();
      res.json(profiles);
    } catch (e) {
      console.error(e);
      res.status(500).json({ error: 'Erro interno' });
    }
  });

  // ---------- 4️⃣ Criação de registro (autenticado) ----------
  router.post('/profiles', authenticateToken, async (req, res) => {
    const { name, email } = req.body;
    if (!name || !email)
      return res.status(400).json({ error: 'name e email são obrigatórios' });

    try {
      const profileId = await db.createProfile(req.user.id, name, email);
      res.status(201).json({ message: 'Perfil criado', profileId });
    } catch (e) {
      console.error(e);
      res.status(500).json({ error: 'Erro interno' });
    }
  });

  // ---------- 5️⃣ Atualizar registro ----------
  router.put('/profiles/:id', authenticateToken, async (req, res) => {
    const profileId = parseInt(req.params.id, 10);
    const { name, email } = req.body;
    if (!name || !email)
      return res.status(400).json({ error: 'name e email são obrigatórios' });

    try {
      const changes = await db.updateProfile(profileId, req.user.id, name, email);
      if (!changes) return res.status(404).json({ error: 'Perfil não encontrado ou sem permissão' });
      res.json({ message: 'Perfil atualizado' });
    } catch (e) {
      console.error(e);
      res.status(500).json({ error: 'Erro interno' });
    }
  });

  // ---------- 6️⃣ Remover registro ----------
  router.delete('/profiles/:id', authenticateToken, async (req, res) => {
    const profileId = parseInt(req.params.id, 10);
    try {
      const changes = await db.deleteProfile(profileId, req.user.id);
      if (!changes) return res.status(404).json({ error: 'Perfil não encontrado ou sem permissão' });
      res.json({ message: 'Perfil removido' });
    } catch (e) {
      console.error(e);
      res.status(500).json({ error: 'Erro interno' });
    }
  });

  return router;
};
```

---

## 6️⃣  Front‑end simples (na pasta `public/`)

### `public/style.css`

```css
body { font-family: Arial, sans-serif; margin: 2rem; }
h1 { color: #333; }
form { margin-bottom: 1.5rem; }
input, button { padding: .5rem; margin: .3rem 0; width: 100%; max-width: 300px; }
.success { color: green; }
.error { color: red; }
ul { list-style: none; padding: 0; }
li { background:#f9f9f9; margin: .5rem 0; padding:.5rem; border:1px solid #ddd; }
```

### `public/index.html` – listagem pública

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Listagem de Perfis</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <h1>Perfis públicos</h1>
  <div id="list"></div>

  <hr>
  <a href="login.html">Login</a> |
  <a href="register.html">Registrar</a>

  <script>
    async function load() {
      const res = await fetch('/api/profiles');
      const data = await res.json();
      const container = document.getElementById('list');
      if (data.length === 0) {
        container.innerHTML = '<p>Nenhum perfil cadastrado.</p>';
        return;
      }
      const ul = document.createElement('ul');
      data.forEach(p => {
        const li = document.createElement('li');
        li.textContent = `Usuário: ${p.username} | Nome: ${p.name} | Email: ${p.email}`;
        ul.appendChild(li);
      });
      container.appendChild(ul);
    }
    load();
  </script>
</body>
</html>
```

### `public/register.html`

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Registrar</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <h1>Registrar novo usuário</h1>
  <form id="form">
    <input type="text" name="username" placeholder="Nome de usuário" required>
    <input type="password" name="password" placeholder="Senha" required>
    <button type="submit">Registrar</button>
  </form>
  <p id="msg"></p>
  <a href="index.html">Voltar</a>

  <script>
    const form = document.getElementById('form');
    const msg = document.getElementById('msg');

    form.addEventListener('submit', async e => {
      e.preventDefault();
      const data = new FormData(form);
      const payload = Object.fromEntries(data.entries());

      const res = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const result = await res.json();
      if (res.ok) {
        msg.textContent = 'Usuário criado! Você pode fazer login.';
        msg.className = 'success';
      } else {
        msg.textContent = result.error || 'Erro';
        msg.className = 'error';
      }
    });
  </script>
</body>
</html>
```

### `public/login.html`

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Login</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <h1>Login</h1>
  <form id="form">
    <input type="text" name="username" placeholder="Nome de usuário" required>
    <input type="password" name="password" placeholder="Senha" required>
    <button type="submit">Entrar</button>
  </form>
  <p id="msg"></p>

  <hr>
  <a href="index.html">Voltar</a>

  <script>
    const form = document.getElementById('form');
    const msg = document.getElementById('msg');

    form.addEventListener('submit', async e => {
      e.preventDefault();
      const data = new FormData(form);
      const payload = Object.fromEntries(data.entries());

      const res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const result = await res.json();

      if (res.ok) {
        localStorage.setItem('token', result.token);
        msg.textContent = 'Login efetuado com sucesso! Abra o console para ver o token.';
        msg.className = 'success';
        console.log('Token JWT:', result.token);
      } else {
        msg.textContent = result.error || 'Erro';
        msg.className = 'error';
      }
    });
  </script>
</body>
</html>
```

*(Obs.: Para criar/editar/excluir perfis você pode usar ferramentas como **Postman** ou **cURL** enviando o header `Authorization: Bearer <token>` obtido no login.)*

---

## 7️⃣  Instruções de execução

### Pré‑requisitos
- **Node.js** (versão 18 ou superior) e **npm** instalados.

### Passos

```bash
# 1️⃣ Clone ou copie o diretório do projeto
git clone <url-do-repo> user-auth-sqlite   # (ou apenas crie a pasta)

cd user-auth-sqlite

# 2️⃣ Instale as dependências
npm install

# 3️⃣ (Opcional) Crie um .env para sobrescrever o JWT secret e a porta
#    Exemplo:
#    JWT_SECRET=alguma_coisa_muito_segura
#    PORT=4000

# 4️⃣ Inicie o servidor
npm start          # ou: npm run dev  (usa nodemon, recarrega ao mudar código)

# 5️⃣ Abra o navegador
http://localhost:3000
```

### Testando a API (exemplo com `curl`)

```bash
# Registro
curl -X POST http://localhost:3000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"senha123"}'

# Login (recebe token)
TOKEN=$(curl -s -X POST http://localhost:3000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"senha123"}' | jq -r .token)

# Cria um perfil (necessita token)
curl -X POST http://localhost:3000/api/profiles \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice Silva","email":"alice@example.com"}'

# Lista pública (não requer token)
curl http://localhost:3000/api/profiles
```

---

## 8️⃣  Considerações de segurança (documentadas no código)

1. **Senhas** são armazenadas usando **bcrypt** com `saltRounds = 12`.  
2. **JWT** contém apenas `id` e `username`; tem validade de 2 horas.  
3. Todas as rotas que modificam dados (`POST/PUT/DELETE /profiles`) passam pelo middleware `authenticateToken`.  
4. O banco SQLite está em um arquivo local (`data.sqlite`); em produção, recomenda‑se usar permissão de arquivo restrita.  
5. Não há controle de CSRF porque a API é *stateless* (token enviado no header).  
6. O front‑end simples não mantém sessão – o token fica em `localStorage`; em um app real, considere **httpOnly cookies**.

--- 

**Pronto!** 🎉  
Com os arquivos acima você tem um sistema web completo de cadastro, login, controle de acesso e persistência em SQLite usando apenas as dependências essenciais do Node.js. Boa codificação!