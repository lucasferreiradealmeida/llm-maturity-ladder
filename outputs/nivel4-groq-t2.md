<!--
nivel: 4 - Seguranca (autenticacao e autorizacao)
provider: groq
model: openai/gpt-oss-120b
tentativa: 2
temperature: 0.2
timestamp: 2026-08-27T19:01:24.711Z
metadata: {"model":"openai/gpt-oss-120b","usage":{"queue_time":0.212039188,"prompt_tokens":275,"prompt_time":0.013189786,"completion_tokens":3882,"completion_time":8.077449935,"total_tokens":4157,"total_time":8.090639721,"completion_tokens_details":{"reasoning_tokens":38}},"finish_reason":"stop"}
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

**🗂️ Estrutura do projeto**

```
user‑auth/
├─ package.json
├─ .gitignore
├─ README.md
├─ db.js                # camada de acesso ao SQLite
├─ server.js            # ponto de entrada da aplicação
├─ middleware/
│   └─ auth.js          # verificação de token JWT
├─ routes/
│   ├─ auth.js          # login / registro
│   └─ users.js         # CRUD de usuários (listagem pública, demais protegidos)
└─ utils/
    └─ hash.js          # funções de hash/salt (bcrypt)
```

---

## 1️⃣ `package.json`

```json
{
  "name": "user-auth",
  "version": "1.0.0",
  "description": "Sistema web simples de cadastro e login com SQLite",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js"
  },
  "author": "Your Name",
  "license": "MIT",
  "dependencies": {
    "bcrypt": "^5.1.0",
    "cookie-parser": "^1.4.6",
    "express": "^4.18.2",
    "jsonwebtoken": "^9.0.2",
    "sqlite3": "^5.1.6"
  },
  "devDependencies": {
    "nodemon": "^3.0.1"
  }
}
```

---

## 2️⃣ `.gitignore`

```gitignore
node_modules/
*.db
.env
```

---

## 3️⃣ `README.md`

```markdown
# Sistema Web de Cadastro e Autenticação

## Descrição
Aplicação Node.js que permite:
- Registro de usuário (email + senha)
- Login com geração de **JWT** armazenado em cookie http‑only
- Listagem pública de usuários
- Criação, edição e remoção de usuários **apenas** por usuários autenticados

Os dados são persistidos em **SQLite** e as senhas são armazenadas usando **bcrypt** (hash + salt).

## Requisitos
- Node.js >= 16
- npm (ou yarn)

## Instalação

```bash
# clonar o repositório (ou copiar os arquivos)
git clone <repo-url> user-auth
cd user-auth

# instalar dependências
npm install

# opcional: instalar nodemon para desenvolvimento
npm install -D nodemon
```

## Execução

```bash
# modo produção
npm start

# modo desenvolvimento (recarrega ao mudar arquivos)
npm run dev
```

A API ficará disponível em `http://localhost:3000`.

## Endpoints

| Método | Rota                | Protegida? | Descrição                                 |
|--------|--------------------|------------|-------------------------------------------|
| POST   | `/api/auth/register` | ❌         | Cria novo usuário (email + senha)         |
| POST   | `/api/auth/login`    | ❌         | Valida credenciais e devolve cookie JWT    |
| POST   | `/api/auth/logout`   | ✅         | Remove o cookie de sessão                 |
| GET    | `/api/users`         | ❌         | Lista todos os usuários (público)          |
| POST   | `/api/users`         | ✅         | Cria novo usuário (mesmo que register)    |
| PUT    | `/api/users/:id`     | ✅         | Atualiza usuário (nome, email, senha)     |
| DELETE | `/api/users/:id`     | ✅         | Remove usuário                            |

> **Obs:** o token JWT tem validade de 1 hora. O cookie é `httpOnly` e `secure` quando a variável de ambiente `NODE_ENV` estiver em `production`.

## Variáveis de ambiente (opcional)

- `PORT` – porta HTTP (default 3000)
- `JWT_SECRET` – segredo usado para assinar o token (default **"supersecretkey"**; **mude em produção!**)

---

```

---

## 4️⃣ `db.js` – camada SQLite

```js
// db.js
// Responsável por abrir/fechar a conexão e fornecer helpers para queries.

const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const DB_PATH = process.env.NODE_ENV === 'test' ? ':memory:' : path.join(__dirname, 'data.db');

const db = new sqlite3.Database(DB_PATH, (err) => {
  if (err) {
    console.error('❌ Erro ao conectar ao SQLite:', err.message);
    process.exit(1);
  }
  console.log(`✅ Conectado ao SQLite (${DB_PATH})`);
});

// Cria a tabela de usuários caso não exista.
db.serialize(() => {
  db.run(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      email TEXT NOT NULL UNIQUE,
      password_hash TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);
});

/**
 * Executa uma query que retorna várias linhas.
 * @param {string} sql
 * @param {Array<any>} params
 * @returns {Promise<Array<Object>>}
 */
function all(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
  });
}

/**
 * Executa uma query que retorna uma única linha.
 * @param {string} sql
 * @param {Array<any>} params
 * @returns {Promise<Object>}
 */
function get(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
  });
}

/**
 * Executa uma query que modifica dados (INSERT, UPDATE, DELETE).
 * @param {string} sql
 * @param {Array<any>} params
 * @returns {Promise<{lastID: number, changes: number}>}
 */
function run(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.run(sql, params, function (err) {
      if (err) reject(err);
      else resolve({ lastID: this.lastID, changes: this.changes });
    });
  });
}

module.exports = { all, get, run };
```

---

## 5️⃣ `utils/hash.js` – bcrypt wrapper

```js
// utils/hash.js
// Funções para gerar e comparar hashes de senha usando bcrypt.

const bcrypt = require('bcrypt');
const SALT_ROUNDS = 12; // custo razoável para produção

/**
 * Gera hash + salt a partir da senha em texto puro.
 * @param {string} plainPassword
 * @returns {Promise<string>} hash
 */
async function hashPassword(plainPassword) {
  return await bcrypt.hash(plainPassword, SALT_ROUNDS);
}

/**
 * Compara senha em texto puro com o hash armazenado.
 * @param {string} plainPassword
 * @param {string} hash
 * @returns {Promise<boolean>}
 */
async function comparePassword(plainPassword, hash) {
  return await bcrypt.compare(plainPassword, hash);
}

module.exports = { hashPassword, comparePassword };
```

---

## 6️⃣ `middleware/auth.js` – validação do JWT

```js
// middleware/auth.js
// Verifica se o request possui um JWT válido em cookie "token".

const jwt = require('jsonwebtoken');
const JWT_SECRET = process.env.JWT_SECRET || 'supersecretkey';

/**
 * Middleware que adiciona `req.user` (payload do token) quando o token for válido.
 * Caso não exista ou seja inválido, responde 401.
 */
function requireAuth(req, res, next) {
  const token = req.cookies?.token;
  if (!token) {
    return res.status(401).json({ error: 'Token ausente. Autentique-se.' });
  }

  try {
    const payload = jwt.verify(token, JWT_SECRET);
    req.user = payload; // { id, email, iat, exp }
    next();
  } catch (err) {
    return res.status(401).json({ error: 'Token inválido ou expirado.' });
  }
}

/**
 * Função utilitária para gerar um token JWT.
 * @param {Object} payload - dados a incluir (ex: { id, email })
 * @returns {string}
 */
function generateToken(payload) {
  // 1 hora de validade
  return jwt.sign(payload, JWT_SECRET, { expiresIn: '1h' });
}

module.exports = { requireAuth, generateToken };
```

---

## 7️⃣ `routes/auth.js` – registro & login

```js
// routes/auth.js
const express = require('express');
const router = express.Router();
const db = require('../db');
const { hashPassword, comparePassword } = require('../utils/hash');
const { generateToken } = require('../middleware/auth');

/**
 * @api {post} /api/auth/register Registro de novo usuário
 * @apiBody {string} name
 * @apiBody {string} email
 * @apiBody {string} password
 */
router.post('/register', async (req, res) => {
  const { name, email, password } = req.body;
  if (!name || !email || !password)
    return res.status(400).json({ error: 'Nome, email e senha são obrigatórios.' });

  try {
    const password_hash = await hashPassword(password);
    const { lastID } = await db.run(
      `INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)`,
      [name, email, password_hash]
    );
    res.status(201).json({ id: lastID, name, email });
  } catch (err) {
    if (err.message.includes('UNIQUE')) {
      return res.status(409).json({ error: 'Email já cadastrado.' });
    }
    console.error(err);
    res.status(500).json({ error: 'Erro interno.' });
  }
});

/**
 * @api {post} /api/auth/login Autenticação
 * @apiBody {string} email
 * @apiBody {string} password
 */
router.post('/login', async (req, res) => {
  const { email, password } = req.body;
  if (!email || !password)
    return res.status(400).json({ error: 'Email e senha são obrigatórios.' });

  try {
    const user = await db.get(`SELECT * FROM users WHERE email = ?`, [email]);
    if (!user) return res.status(401).json({ error: 'Credenciais inválidas.' });

    const match = await comparePassword(password, user.password_hash);
    if (!match) return res.status(401).json({ error: 'Credenciais inválidas.' });

    const token = generateToken({ id: user.id, email: user.email });

    // cookie httpOnly (e secure em produção)
    res.cookie('token', token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      maxAge: 60 * 60 * 1000 // 1h
    });

    res.json({ message: 'Login realizado com sucesso.' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Erro interno.' });
  }
});

/**
 * @api {post} /api/auth/logout Desloga usuário (remove cookie)
 */
router.post('/logout', (req, res) => {
  res.clearCookie('token');
  res.json({ message: 'Logout efetuado.' });
});

module.exports = router;
```

---

## 8️⃣ `routes/users.js` – CRUD de usuários

```js
// routes/users.js
const express = require('express');
const router = express.Router();
const db = require('../db');
const { requireAuth } = require('../middleware/auth');
const { hashPassword } = require('../utils/hash');

/**
 * @api {get} /api/users Listar usuários (público)
 */
router.get('/', async (req, res) => {
  try {
    const users = await db.all(`SELECT id, name, email, created_at FROM users`);
    res.json(users);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Erro interno.' });
  }
});

/**
 * @api {post} /api/users Cria usuário (autenticado)
 * Mesmo payload de /register, porém requer token.
 */
router.post('/', requireAuth, async (req, res) => {
  const { name, email, password } = req.body;
  if (!name || !email || !password)
    return res.status(400).json({ error: 'Nome, email e senha são obrigatórios.' });

  try {
    const password_hash = await hashPassword(password);
    const { lastID } = await db.run(
      `INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)`,
      [name, email, password_hash]
    );
    res.status(201).json({ id: lastID, name, email });
  } catch (err) {
    if (err.message.includes('UNIQUE')) {
      return res.status(409).json({ error: 'Email já cadastrado.' });
    }
    console.error(err);
    res.status(500).json({ error: 'Erro interno.' });
  }
});

/**
 * @api {put} /api/users/:id Atualiza usuário (autenticado)
 * Permite alterar name, email e/ou password.
 */
router.put('/:id', requireAuth, async (req, res) => {
  const { id } = req.params;
  const { name, email, password } = req.body;

  // Apenas os campos enviados serão atualizados.
  const fields = [];
  const params = [];

  if (name) {
    fields.push('name = ?');
    params.push(name);
  }
  if (email) {
    fields.push('email = ?');
    params.push(email);
  }
  if (password) {
    const password_hash = await hashPassword(password);
    fields.push('password_hash = ?');
    params.push(password_hash);
  }

  if (fields.length === 0) {
    return res.status(400).json({ error: 'Nenhum campo para atualizar.' });
  }

  params.push(id); // último parâmetro = WHERE id = ?

  try {
    const { changes } = await db.run(
      `UPDATE users SET ${fields.join(', ')} WHERE id = ?`,
      params
    );
    if (changes === 0) return res.status(404).json({ error: 'Usuário não encontrado.' });
    res.json({ message: 'Usuário atualizado.' });
  } catch (err) {
    if (err.message.includes('UNIQUE')) {
      return res.status(409).json({ error: 'Email já utilizado por outro usuário.' });
    }
    console.error(err);
    res.status(500).json({ error: 'Erro interno.' });
  }
});

/**
 * @api {delete} /api/users/:id Remove usuário (autenticado)
 */
router.delete('/:id', requireAuth, async (req, res) => {
  const { id } = req.params;
  try {
    const { changes } = await db.run(`DELETE FROM users WHERE id = ?`, [id]);
    if (changes === 0) return res.status(404).json({ error: 'Usuário não encontrado.' });
    res.json({ message: 'Usuário removido.' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Erro interno.' });
  }
});

module.exports = router;
```

---

## 9️⃣ `server.js` – ponto de entrada

```js
// server.js
// Configura o Express, middlewares e rotas.

const express = require('express');
const cookieParser = require('cookie-parser');
const authRoutes = require('./routes/auth');
const userRoutes = require('./routes/users');

const app = express();
const PORT = process.env.PORT || 3000;

// Middlewares básicos
app.use(express.json());          // parse JSON bodies
app.use(cookieParser());          // lê cookies (para JWT)

// Rotas de API
app.use('/api/auth', authRoutes);
app.use('/api/users', userRoutes);

// Rota de teste / raiz
app.get('/', (req, res) => {
  res.send('⚡ Sistema de cadastro e login está rodando.');
});

// Tratamento de rotas não encontradas
app.use((req, res) => {
  res.status(404).json({ error: 'Rota não encontrada.' });
});

// Inicia o servidor
app.listen(PORT, () => {
  console.log(`🚀 Servidor iniciado em http://localhost:${PORT}`);
});
```

---

## 10️⃣ Como executar tudo

```bash
# 1️⃣ Clone ou copie os arquivos acima na pasta "user-auth"
cd user-auth

# 2️⃣ Instale as dependências
npm install

# 3️⃣ (Opcional) Crie um .env se quiser mudar o segredo ou a porta
#    echo "JWT_SECRET=mysupersecret\nPORT=4000" > .env

# 4️⃣ Inicie a aplicação
npm start
```

A API ficará escutando em `http://localhost:3000`.  
Use ferramentas como **Postman**, **curl** ou **Insomnia** para testar os endpoints descritos no `README.md`.

--- 

**⚠️ Segurança**

- Em produção, defina `JWT_SECRET` com um valor aleatório forte e nunca o commit no repositório.
- O cookie `secure` só é ativado quando `NODE_ENV=production`; então rode atrás de HTTPS.
- O `SALT_ROUNDS` de 12 é um bom compromisso entre segurança e desempenho; ajuste conforme necessidade.

Pronto! 🎉 O código acima já está completo, autocontido e pronto para ser executado. Boa codificação!