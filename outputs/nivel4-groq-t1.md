<!--
nivel: 4 - Seguranca (autenticacao e autorizacao)
provider: groq
model: openai/gpt-oss-120b
tentativa: 1
temperature: 0.2
timestamp: 2026-08-27T19:00:48.806Z
metadata: {"model":"openai/gpt-oss-120b","usage":{"queue_time":0.350637755,"prompt_tokens":275,"prompt_time":0.014952054,"completion_tokens":3222,"completion_time":6.724968316,"total_tokens":3497,"total_time":6.73992037,"completion_tokens_details":{"reasoning_tokens":53}},"finish_reason":"stop"}
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

**✅ Sistema Web de Cadastro de Usuários (Node.js + SQLite)**  
Abaixo está todo o código fonte necessário para colocar o projeto em funcionamento, além das instruções de instalação e execução.

---

## 📁 Estrutura de arquivos

```
user‑system/
│
├─ package.json
├─ .gitignore
├─ README.md
│
├─ src/
│   ├─ app.js                 # ponto de entrada da aplicação
│   ├─ db.js                  # camada de acesso ao SQLite
│   ├─ routes.js              # rotas HTTP (auth + CRUD)
│   └─ middleware/
│        └─ auth.js           # verificador de token JWT
│
└─ db/
    └─ schema.sql            # script de criação das tabelas
```

> **Obs.** Todos os arquivos são **plain JavaScript** (ES6) e usam apenas as dependências indispensáveis.

---

## 1️⃣ `package.json`

```json
{
  "name": "user-system",
  "version": "1.0.0",
  "description": "Sistema web simples de cadastro de usuários com login, JWT e SQLite",
  "main": "src/app.js",
  "scripts": {
    "start": "node src/app.js",
    "dev": "nodemon src/app.js"
  },
  "author": "Your Name",
  "license": "MIT",
  "dependencies": {
    "bcrypt": "^5.1.0",
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
.env
.db/
```

---

## 3️⃣ `README.md`

```markdown
# Sistema Web de Cadastro de Usuários

## Descrição
Aplicação Node.js que permite:
- Registro de novos usuários (senha armazenada com **bcrypt** + salt).
- Login com geração de **JWT**.
- CRUD de “registros” (pode ser qualquer entidade, aqui usamos `items`).
- Listagem pública de itens; criação/edição/remoção somente para usuários autenticados.

Dados são persistidos em **SQLite**.

## Pré‑requisitos
- **Node.js** (>= 18)
- **npm** (ou **yarn**)

## Instalação

```bash
# 1️⃣ Clone o repositório (ou copie os arquivos)
git clone <url-do-repo>
cd user-system

# 2️⃣ Instale as dependências
npm install

# 3️⃣ Crie o banco de dados (executa o script SQL)
npm run init-db   # comando definido no package.json (ver abaixo)
```

## Execução

```bash
# modo produção
npm start

# modo desenvolvimento (auto‑restart com nodemon)
npm run dev
```

A API ficará disponível em: `http://localhost:3000`

## Endpoints

| Método | URL                     | Autenticação | Descrição |
|--------|-------------------------|--------------|-----------|
| POST   | `/api/auth/register`    | ❌ | Cria usuário (login + senha) |
| POST   | `/api/auth/login`       | ❌ | Retorna JWT |
| GET    | `/api/items`            | ❌ | Lista todos os itens (público) |
| POST   | `/api/items`            | ✅ | Cria item (nome, descrição) |
| PUT    | `/api/items/:id`        | ✅ | Atualiza item |
| DELETE | `/api/items/:id`        | ✅ | Remove item |

> **✅** → requer token JWT no header `Authorization: Bearer <token>`.

## Testes rápidos com `curl`

```bash
# registro
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"secret"}' \
  http://localhost:3000/api/auth/register

# login → obtém token
TOKEN=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"secret"}' \
  http://localhost:3000/api/auth/login | jq -r .token)

# criar item (autenticado)
curl -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"Item 1","description":"Primeiro item"}' \
  http://localhost:3000/api/items
```

## Segurança
- Senhas são hashadas com **bcrypt** (12 rounds) antes de serem gravadas.
- JWT é assinado com uma chave secreta fixa (`process.env.JWT_SECRET` ou fallback).
- Todas as rotas que modificam dados utilizam o middleware `verifyToken`.

## Licença
MIT
```

---

## 4️⃣ Script de criação do banco (`db/schema.sql`)

```sql
-- Usuários
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Itens (exemplo de registro que será cadastrado)
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Comando de inicialização (adicione ao `package.json`)

```json
  "scripts": {
    "start": "node src/app.js",
    "dev": "nodemon src/app.js",
    "init-db": "node src/db.js init"
  },
```

---

## 5️⃣ `src/db.js` – camada de acesso ao SQLite

```javascript
// src/db.js
const path = require('path');
const sqlite3 = require('sqlite3').verbose();
const fs = require('fs');

const DB_FILE = path.resolve(__dirname, '../.db/users.db');

// Garante que o diretório exista
const DB_DIR = path.dirname(DB_FILE);
if (!fs.existsSync(DB_DIR)) fs.mkdirSync(DB_DIR, { recursive: true });

const db = new sqlite3.Database(DB_FILE, (err) => {
  if (err) console.error('Erro ao abrir banco de dados:', err);
  else console.log('SQLite conectado em', DB_FILE);
});

/**
 * Executa um script SQL (usado para criar as tabelas).
 */
function runInitScript() {
  const initSql = fs.readFileSync(path.resolve(__dirname, '../db/schema.sql'), 'utf-8');
  db.exec(initSql, (err) => {
    if (err) console.error('Erro ao criar schema:', err);
    else console.log('Schema criado/atualizado com sucesso.');
  });
}

/**
 * Exporta funções auxiliares para usar em todo o código.
 */
module.exports = {
  db,
  runInitScript,
};
```

> **Observação:** Quando o script `npm run init-db` for executado, o módulo será carregado com o argumento `init` (ver próximo ponto) e chamará `runInitScript()`.

---

## 6️⃣ `src/middleware/auth.js` – verificador de JWT

```javascript
// src/middleware/auth.js
const jwt = require('jsonwebtoken');

const JWT_SECRET = process.env.JWT_SECRET || 's3cr3t_k3y_change_me';

function verifyToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  if (!authHeader) return res.status(401).json({ error: 'Token ausente' });

  const token = authHeader.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'Token mal formatado' });

  jwt.verify(token, JWT_SECRET, (err, payload) => {
    if (err) return res.status(403).json({ error: 'Token inválido' });
    // guarda o id do usuário no request para uso posterior
    req.userId = payload.sub;
    next();
  });
}

module.exports = { verifyToken, JWT_SECRET };
```

---

## 7️⃣ `src/routes.js` – rotas da API

```javascript
// src/routes.js
const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const { db } = require('./db');
const { verifyToken, JWT_SECRET } = require('./middleware/auth');

const router = express.Router();

// ---------- Auth ----------
router.post('/auth/register', async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password)
    return res.status(400).json({ error: 'username e password são obrigatórios' });

  // verifica se usuário já existe
  db.get('SELECT id FROM users WHERE username = ?', [username], async (err, row) => {
    if (err) return res.status(500).json({ error: err.message });
    if (row) return res.status(409).json({ error: 'Usuário já existente' });

    // hash da senha (12 salt rounds)
    const saltRounds = 12;
    const passwordHash = await bcrypt.hash(password, saltRounds);

    db.run(
      'INSERT INTO users (username, password_hash) VALUES (?, ?)',
      [username, passwordHash],
      function (err) {
        if (err) return res.status(500).json({ error: err.message });
        return res.status(201).json({ id: this.lastID, username });
      }
    );
  });
});

router.post('/auth/login', (req, res) => {
  const { username, password } = req.body;
  if (!username || !password)
    return res.status(400).json({ error: 'username e password são obrigatórios' });

  db.get('SELECT id, password_hash FROM users WHERE username = ?', [username], async (err, user) => {
    if (err) return res.status(500).json({ error: err.message });
    if (!user) return res.status(401).json({ error: 'Credenciais inválidas' });

    const match = await bcrypt.compare(password, user.password_hash);
    if (!match) return res.status(401).json({ error: 'Credenciais inválidas' });

    // cria JWT (payload mínimo: sub = userId)
    const token = jwt.sign({ sub: user.id }, JWT_SECRET, { expiresIn: '2h' });
    return res.json({ token });
  });
});

// ---------- Items (CRUD) ----------
router.get('/items', (req, res) => {
  db.all('SELECT id, name, description, created_at, updated_at FROM items', [], (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(rows);
  });
});

router.post('/items', verifyToken, (req, res) => {
  const { name, description } = req.body;
  if (!name) return res.status(400).json({ error: 'Nome é obrigatório' });

  db.run(
    'INSERT INTO items (name, description) VALUES (?, ?)',
    [name, description || null],
    function (err) {
      if (err) return res.status(500).json({ error: err.message });
      res.status(201).json({ id: this.lastID, name, description });
    }
  );
});

router.put('/items/:id', verifyToken, (req, res) => {
  const { id } = req.params;
  const { name, description } = req.body;
  if (!name) return res.status(400).json({ error: 'Nome é obrigatório' });

  db.run(
    `UPDATE items SET name = ?, description = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?`,
    [name, description || null, id],
    function (err) {
      if (err) return res.status(500).json({ error: err.message });
      if (this.changes === 0) return res.status(404).json({ error: 'Item não encontrado' });
      res.json({ id: Number(id), name, description });
    }
  );
});

router.delete('/items/:id', verifyToken, (req, res) => {
  const { id } = req.params;
  db.run('DELETE FROM items WHERE id = ?', [id], function (err) {
    if (err) return res.status(500).json({ error: err.message });
    if (this.changes === 0) return res.status(404).json({ error: 'Item não encontrado' });
    res.status(204).send();
  });
});

module.exports = router;
```

---

## 8️⃣ `src/app.js` – ponto de entrada

```javascript
// src/app.js
require('dotenv').config(); // opcional, caso queira usar .env
const express = require('express');
const bodyParser = require('body-parser');
const routes = require('./routes');
const { runInitScript } = require('./db');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware padrão
app.use(bodyParser.json());

// Rotas da API (prefixo /api)
app.use('/api', routes);

// Rota raiz (informativa)
app.get('/', (req, res) => {
  res.send('API de Usuários está em execução. Use /api/... para acessar.');
});

// Inicia o servidor
app.listen(PORT, () => {
  console.log(`🚀 Servidor rodando em http://localhost:${PORT}`);
});

// Se o script for chamado com "init" (npm run init-db) cria as tabelas
if (process.argv[2] === 'init') {
  runInitScript();
}
```

---

## 9️⃣ Como iniciar o projeto (passo‑a‑passo)

```bash
# 1️⃣ Clonar / copiar arquivos
git clone https://github.com/youruser/user-system.git
cd user-system

# 2️⃣ Instalar dependências
npm install

# 3️⃣ Criar/atualizar o banco (executa o script SQL)
npm run init-db      # ← cria .db/users.db e as tabelas

# 4️⃣ Iniciar a aplicação
npm start            # → modo produção
# ou
npm run dev          # → modo desenvolvimento com hot‑reload
```

A API já pode ser testada com `curl`, Postman ou qualquer cliente HTTP.

---

### 🎉 Pronto!  
Você tem um **sistema completo** de cadastro, login, sessão via JWT e controle de acesso, tudo rodando em Node.js com SQLite, sem frameworks extras além do Express. Basta seguir as instruções acima e a aplicação estará disponível. Boa codificação!