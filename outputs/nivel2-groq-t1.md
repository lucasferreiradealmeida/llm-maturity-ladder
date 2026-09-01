<!--
nivel: 2 - API REST
provider: groq
model: openai/gpt-oss-120b
tentativa: 1
temperature: 0.2
timestamp: 2026-08-27T18:58:28.921Z
metadata: {"model":"openai/gpt-oss-120b","usage":{"queue_time":0.21080869,"prompt_tokens":261,"prompt_time":0.010295925,"completion_tokens":3214,"completion_time":6.685059164,"total_tokens":3475,"total_time":6.6953550889999995,"completion_tokens_details":{"reasoning_tokens":34}},"finish_reason":"stop"}
-->

## Prompt enviado
```
Voce e um(a) engenheiro(a) de software responsavel por implementar o sistema
descrito abaixo. Gere o codigo completo, pronto para rodar, incluindo
instrucoes de execucao (como instalar dependencias e como rodar).

TAREFA:
Transforme o sistema de cadastro de usuarios (nome, e-mail, data de
nascimento) em uma API REST (endpoints para criar, listar, atualizar e
remover usuarios), com respostas em JSON e codigos de status HTTP
apropriados. Persista os dados em SQLite.

RESTRICOES:
- Linguagem: Node.js (JavaScript).
- Nao use frameworks alem dos estritamente necessarios para a tarefa.
- Nao peca esclarecimentos: assuma decisoes razoaveis e documente-as em comentarios.
- Entregue todos os arquivos necessarios, indicando o nome do arquivo antes de cada bloco de codigo.
```

## Resposta do modelo

**Projeto:** `user-api`  
**Descrição:** API REST para cadastro de usuários (nome, e‑mail, data de nascimento) usando Node.js, Express e SQLite.  

---

## 1. Estrutura de diretórios

```
user-api/
├─ package.json
├─ package-lock.json   (gerado após npm install)
├─ src/
│  ├─ app.js
│  ├─ db.js
│  └─ routes/
│     └─ users.js
└─ README.md
```

---

## 2. Arquivo **package.json**

```json
// package.json
{
  "name": "user-api",
  "version": "1.0.0",
  "description": "API REST para cadastro de usuários com persistência em SQLite",
  "main": "src/app.js",
  "scripts": {
    "start": "node src/app.js",
    "dev": "nodemon src/app.js"
  },
  "author": "Seu Nome",
  "license": "MIT",
  "dependencies": {
    "express": "^4.18.2",
    "sqlite3": "^5.1.6"
  },
  "devDependencies": {
    "nodemon": "^3.0.1"
  }
}
```

> **Observação:**  
> - Apenas **express** (framework minimalista para HTTP) e **sqlite3** são usados, conforme a restrição de “frameworks estritamente necessários”.  
> - `nodemon` está como dev‑dependency para facilitar desenvolvimento, mas não é obrigatório para a execução em produção.

---

## 3. Configuração do banco de dados – **src/db.js**

```javascript
// src/db.js
/**
 * Módulo responsável por criar a conexão com o SQLite e garantir que a
 * tabela `users` exista.
 *
 * Estrutura da tabela:
 *   id               INTEGER PRIMARY KEY AUTOINCREMENT
 *   name             TEXT NOT NULL
 *   email            TEXT NOT NULL UNIQUE
 *   birthdate        TEXT NOT NULL  (ISO 8601, ex.: 1990-05-21)
 *
 * Todas as funções retornam Promises para que possam ser usadas com async/await.
 */

const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const dbPath = path.resolve(__dirname, '..', 'data', 'users.db');

// Garante que a pasta "data" exista
const fs = require('fs');
const dataDir = path.dirname(dbPath);
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
}

// Cria/abre o banco
const db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error('Erro ao abrir o banco SQLite:', err.message);
    process.exit(1);
  }
  console.log('Conectado ao banco SQLite em', dbPath);
});

// Inicializa a tabela se ela ainda não existir
db.serialize(() => {
  db.run(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      email TEXT NOT NULL UNIQUE,
      birthdate TEXT NOT NULL
    )
  `);
});

/**
 * Executa uma query que retorna múltiplas linhas.
 */
function all(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.all(sql, params, (err, rows) => {
      if (err) reject(err);
      else resolve(rows);
    });
  });
}

/**
 * Executa uma query que retorna uma única linha.
 */
function get(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.get(sql, params, (err, row) => {
      if (err) reject(err);
      else resolve(row);
    });
  });
}

/**
 * Executa INSERT/UPDATE/DELETE.
 * Resolve com o objeto { lastID, changes }.
 */
function run(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.run(sql, params, function (err) {
      if (err) reject(err);
      else resolve({ lastID: this.lastID, changes: this.changes });
    });
  });
}

// Exporta as funções úteis
module.exports = {
  all,
  get,
  run,
  // Expor o objeto db só se precisar de acesso direto (ex.: fechar conexão)
  db,
};
```

---

## 4. Rotas – **src/routes/users.js**

```javascript
// src/routes/users.js
/**
 * Endpoints da API de usuários:
 *
 * POST    /users          → criar novo usuário
 * GET     /users          → listar todos
 * GET     /users/:id      → obter usuário por id
 * PUT     /users/:id      → atualizar (nome, email, birthdate)
 * DELETE  /users/:id      → remover usuário
 *
 * Todas as respostas são JSON e utilizam códigos de status HTTP adequados.
 */

const express = require('express');
const router = express.Router();
const db = require('../db');

// Validação simples – pode ser melhorada com bibliotecas como Joi (não usadas aqui)
function validateUserPayload(payload) {
  const { name, email, birthdate } = payload;
  if (!name || typeof name !== 'string') return 'Nome é obrigatório e deve ser texto.';
  if (!email || typeof email !== 'string') return 'E‑mail é obrigatório e deve ser texto.';
  if (!birthdate || typeof birthdate !== 'string') return 'Data de nascimento é obrigatória e deve ser texto (ISO 8601).';
  // Opcional: validar formato ISO da data
  if (isNaN(Date.parse(birthdate))) return 'Data de nascimento deve estar no formato ISO (ex.: 1990-05-21).';
  return null;
}

/* ---------- CREATE ---------- */
router.post('/', async (req, res) => {
  const error = validateUserPayload(req.body);
  if (error) return res.status(400).json({ error });

  const { name, email, birthdate } = req.body;

  try {
    const { lastID } = await db.run(
      `INSERT INTO users (name, email, birthdate) VALUES (?, ?, ?)`,
      [name, email, birthdate]
    );
    const newUser = await db.get(`SELECT * FROM users WHERE id = ?`, [lastID]);
    res.status(201).json(newUser);
  } catch (err) {
    if (err.message.includes('UNIQUE constraint failed')) {
      return res.status(409).json({ error: 'E‑mail já está em uso.' });
    }
    console.error(err);
    res.status(500).json({ error: 'Erro interno ao criar usuário.' });
  }
});

/* ---------- LIST ALL ---------- */
router.get('/', async (req, res) => {
  try {
    const users = await db.all(`SELECT * FROM users`);
    res.json(users);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Erro ao obter usuários.' });
  }
});

/* ---------- GET BY ID ---------- */
router.get('/:id', async (req, res) => {
  const id = parseInt(req.params.id, 10);
  if (Number.isNaN(id)) return res.status(400).json({ error: 'ID inválido.' });

  try {
    const user = await db.get(`SELECT * FROM users WHERE id = ?`, [id]);
    if (!user) return res.status(404).json({ error: 'Usuário não encontrado.' });
    res.json(user);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Erro ao buscar usuário.' });
  }
});

/* ---------- UPDATE ---------- */
router.put('/:id', async (req, res) => {
  const id = parseInt(req.params.id, 10);
  if (Number.isNaN(id)) return res.status(400).json({ error: 'ID inválido.' });

  const error = validateUserPayload(req.body);
  if (error) return res.status(400).json({ error });

  const { name, email, birthdate } = req.body;

  try {
    const result = await db.run(
      `UPDATE users SET name = ?, email = ?, birthdate = ? WHERE id = ?`,
      [name, email, birthdate, id]
    );

    if (result.changes === 0) {
      return res.status(404).json({ error: 'Usuário não encontrado.' });
    }

    const updatedUser = await db.get(`SELECT * FROM users WHERE id = ?`, [id]);
    res.json(updatedUser);
  } catch (err) {
    if (err.message.includes('UNIQUE constraint failed')) {
      return res.status(409).json({ error: 'E‑mail já está em uso por outro usuário.' });
    }
    console.error(err);
    res.status(500).json({ error: 'Erro ao atualizar usuário.' });
  }
});

/* ---------- DELETE ---------- */
router.delete('/:id', async (req, res) => {
  const id = parseInt(req.params.id, 10);
  if (Number.isNaN(id)) return res.status(400).json({ error: 'ID inválido.' });

  try {
    const result = await db.run(`DELETE FROM users WHERE id = ?`, [id]);
    if (result.changes === 0) {
      return res.status(404).json({ error: 'Usuário não encontrado.' });
    }
    res.status(204).send(); // No Content
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Erro ao remover usuário.' });
  }
});

module.exports = router;
```

---

## 5. Aplicação principal – **src/app.js**

```javascript
// src/app.js
/**
 * Entrada da aplicação.
 * Configura o Express, middlewares básicos e registra as rotas.
 * O servidor escuta na porta 3000 por padrão (pode ser sobrescrita via
 * variável de ambiente PORT).
 */

const express = require('express');
const usersRouter = require('./routes/users');
const path = require('path');

const app = express();

// Middleware para tratar JSON no corpo das requisições
app.use(express.json());

// Rota raiz simples
app.get('/', (req, res) => {
  res.json({ message: 'API de Usuários está funcionando.' });
});

// Monta o router em /users
app.use('/users', usersRouter);

// Tratamento de rotas não encontradas
app.use((req, res) => {
  res.status(404).json({ error: 'Endpoint não encontrado.' });
});

// Tratamento de erros inesperados
app.use((err, req, res, next) => {
  console.error('Erro inesperado:', err);
  res.status(500).json({ error: 'Erro interno do servidor.' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 Servidor rodando na porta ${PORT}`);
});
```

---

## 6. Documentação de execução – **README.md**

```markdown
# API REST de Cadastro de Usuários

Esta é uma API minimalista desenvolvida em **Node.js** que permite criar,
listar, atualizar e remover usuários (nome, e‑mail, data de nascimento).  
Os dados são armazenados em um banco **SQLite** local.

## Requisitos

- **Node.js** (versão 14 ou superior)
- **npm** (vem junto com o Node)

## Instalação

```bash
# 1. Clone ou copie o código para uma pasta
git clone <url-do-repositorio> user-api   # se houver repositório
cd user-api

# 2. Instale as dependências
npm install
```

## Execução

```bash
# modo produção
npm start

# modo desenvolvimento (recarrega ao mudar arquivos)
npm run dev
```

O servidor será iniciado em `http://localhost:3000`.

## Endpoints da API

| Método | URL               | Descrição                         | Corpo (JSON)                               |
|--------|-------------------|-----------------------------------|--------------------------------------------|
| POST   | `/users`          | Cria um novo usuário              | `{ "name": "...", "email": "...", "birthdate": "YYYY-MM-DD" }` |
| GET    | `/users`          | Lista todos os usuários           | -                                          |
| GET    | `/users/:id`      | Busca usuário pelo `id`           | -                                          |
| PUT    | `/users/:id`      | Atualiza usuário existente        | Mesmo payload de **POST**                  |
| DELETE | `/users/:id`      | Remove usuário                     | -                                          |

### Códigos de status relevantes

- **200 OK** – Operação bem‑sucedida (GET, PUT)
- **201 Created** – Usuário criado
- **204 No Content** – Usuário removido
- **400 Bad Request** – Dados inválidos ou ID mal‑formado
- **404 Not Found** – Usuário não encontrado
- **409 Conflict** – E‑mail já cadastrado
- **500 Internal Server Error** – Falha inesperada no servidor

## Estrutura de arquivos

```
user-api/
├─ package.json
├─ src/
│  ├─ app.js          # ponto de entrada
│  ├─ db.js           # camada de acesso ao SQLite
│  └─ routes/
│     └─ users.js     # rotas da API
└─ README.md
```

## Testes rápidos (usando curl)

```bash
# Criar usuário
curl -X POST http://localhost:3000/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Ana Silva","email":"ana@example.com","birthdate":"1992-03-15"}'

# Listar usuários
curl http://localhost:3000/users

# Atualizar usuário (id = 1)
curl -X PUT http://localhost:3000/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"Ana S. Santos","email":"ana.santos@example.com","birthdate":"1992-03-15"}'

# Deletar usuário
curl -X DELETE http://localhost:3000/users/1
```

## Observações

- O banco SQLite é criado automaticamente na primeira execução em `data/users.db`.  
- Não há camada de autenticação; a API é **aberta** por simplicidade. Em produção, adicione mecanismos de segurança (JWT, OAuth, etc.).  
- A validação de dados é básica; para projetos maiores recomenda‑se usar bibliotecas como **Joi** ou **Zod**.

---

**Pronto!** Basta seguir os passos acima e a API estará operacional. Boa codificação!