<!--
nivel: 2 - API REST
provider: groq
model: openai/gpt-oss-120b
tentativa: 2
temperature: 0.2
timestamp: 2026-08-27T18:59:16.454Z
metadata: {"model":"openai/gpt-oss-120b","usage":{"queue_time":0.243611419,"prompt_tokens":261,"prompt_time":0.010022174,"completion_tokens":3142,"completion_time":6.541004204,"total_tokens":3403,"total_time":6.5510263779999995,"completion_tokens_details":{"reasoning_tokens":46}},"finish_reason":"stop"}
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

**📦 Projeto:** `user-api`  
**Descrição:** API REST simples para cadastro de usuários (nome, e‑mail, data de nascimento) usando **Node.js**, **Express** e **SQLite**.  

---

## 1. Estrutura de pastas / arquivos

```
user-api/
│
├─ package.json
├─ .gitignore
├─ README.md
│
├─ src/
│   ├─ index.js          # ponto de entrada da aplicação
│   ├─ db.js             # módulo de acesso ao SQLite
│   └─ routes/
│        └─ users.js     # rotas da API de usuários
│
└─ migrations/
        └─ init.sql       # script de criação da tabela
```

---

## 2. Código-fonte

### **`package.json`**
```json
{
  "name": "user-api",
  "version": "1.0.0",
  "description": "API REST para cadastro de usuários usando SQLite",
  "main": "src/index.js",
  "type": "module",
  "scripts": {
    "start": "node src/index.js",
    "dev": "nodemon src/index.js",
    "migrate": "node src/db.js init"
  },
  "keywords": [
    "express",
    "sqlite",
    "rest",
    "api"
  ],
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

### **`.gitignore`**
```
node_modules/
database.sqlite
.env
```

### **`README.md`**
```markdown
# User API

API REST para criar, listar, atualizar e remover usuários. Os dados são armazenados em um banco SQLite.

## Pré‑requisitos

- **Node.js** (v18 ou superior recomendado)
- **npm** (ou **yarn**)

## Instalação

```bash
# clonar o repositório (ou copie os arquivos)
git clone <url-do-repositorio>
cd user-api

# instalar dependências
npm install

# criar/atualizar o banco de dados (executa o script migrations/init.sql)
npm run migrate
```

## Executando

```bash
# modo produção
npm start

# modo desenvolvimento (recarrega ao mudar arquivos)
npm run dev
```

A API ficará disponível em **http://localhost:3000**.

## Endpoints

| Método | URL                | Descrição                              | Corpo (JSON)                              |
|--------|--------------------|----------------------------------------|-------------------------------------------|
| GET    | `/users`           | Lista todos os usuários                | –                                         |
| GET    | `/users/:id`       | Busca usuário por ID                   | –                                         |
| POST   | `/users`           | Cria novo usuário                      | `{ "name":"...", "email":"...", "birthdate":"YYYY-MM-DD" }` |
| PUT    | `/users/:id`       | Atualiza usuário existente             | `{ "name":"...", "email":"...", "birthdate":"YYYY-MM-DD" }` |
| DELETE | `/users/:id`       | Remove usuário                         | –                                         |

## Tratamento de erros

- **400** – Dados de entrada inválidos.  
- **404** – Usuário não encontrado.  
- **500** – Erro interno do servidor.

---

```

### **`migrations/init.sql`**
```sql
-- Cria a tabela 'users' caso ainda não exista
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    birthdate TEXT NOT NULL   -- armazenado no formato ISO (YYYY-MM-DD)
);
```

### **`src/db.js`**
```js
/**
 * Módulo de acesso ao SQLite.
 * 
 * - Usa a biblioteca `sqlite3` em modo "verbose" para facilitar debugging.
 * - Exporta funções auxiliares usadas nas rotas.
 * - Também permite rodar migrações simples via `node src/db.js init`.
 */

import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import { readFile } from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Caminho do arquivo SQLite (cria no diretório raiz do projeto)
const DB_FILE = path.resolve(__dirname, '..', 'database.sqlite');

// Instância singleton do DB
let db;

/**
 * Abre (ou cria) a conexão com o banco.
 */
export async function getDB() {
  if (!db) {
    db = await open({
      filename: DB_FILE,
      driver: sqlite3.Database
    });
  }
  return db;
}

/**
 * Executa a migração inicial (cria a tabela users).
 * Chamado via `npm run migrate`.
 */
export async function init() {
  const sql = await readFile(
    path.resolve(__dirname, '..', 'migrations', 'init.sql'),
    'utf8'
  );
  const connection = await getDB();
  await connection.exec(sql);
  console.log('✅ Banco de dados inicializado.');
}

/**
 * Permite usar o script diretamente: `node src/db.js init`
 */
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const cmd = process.argv[2];
  if (cmd === 'init') {
    init()
      .then(() => process.exit(0))
      .catch(err => {
        console.error('Erro ao inicializar o banco:', err);
        process.exit(1);
      });
  } else {
    console.log('Comandos disponíveis: init');
    process.exit(0);
  }
}
```

### **`src/routes/users.js`**
```js
/**
 * Rotas da API de usuários.
 * Cada rota devolve JSON e o código HTTP adequado.
 */

import { Router } from 'express';
import { getDB } from '../db.js';

const router = Router();

/**
 * Validação simples dos campos do usuário.
 * Lança um Error com a mensagem de erro caso algo esteja errado.
 */
function validateUserPayload(payload) {
  const { name, email, birthdate } = payload;
  if (!name || typeof name !== 'string' || name.trim() === '') {
    throw new Error('Campo "name" é obrigatório e deve ser uma string.');
  }
  if (!email || typeof email !== 'string' || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    throw new Error('Campo "email" é obrigatório e deve ser um e‑mail válido.');
  }
  if (!birthdate || typeof birthdate !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(birthdate)) {
    throw new Error('Campo "birthdate" é obrigatório e deve estar no formato YYYY-MM-DD.');
  }
}

/* ---------- CREATE ---------- */
router.post('/', async (req, res) => {
  try {
    validateUserPayload(req.body);
    const { name, email, birthdate } = req.body;
    const db = await getDB();

    const result = await db.run(
      `INSERT INTO users (name, email, birthdate) VALUES (?, ?, ?)`,
      [name, email, birthdate]
    );

    const createdUser = await db.get(`SELECT * FROM users WHERE id = ?`, result.lastID);
    res.status(201).json(createdUser);
  } catch (err) {
    if (err.message.includes('UNIQUE constraint failed')) {
      res.status(400).json({ error: 'E‑mail já cadastrado.' });
    } else if (err.message.startsWith('Campo')) {
      res.status(400).json({ error: err.message });
    } else {
      console.error(err);
      res.status(500).json({ error: 'Erro interno do servidor.' });
    }
  }
});

/* ---------- LIST ALL ---------- */
router.get('/', async (req, res) => {
  try {
    const db = await getDB();
    const users = await db.all(`SELECT * FROM users ORDER BY id`);
    res.json(users);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Erro interno do servidor.' });
  }
});

/* ---------- GET BY ID ---------- */
router.get('/:id', async (req, res) => {
  try {
    const db = await getDB();
    const user = await db.get(`SELECT * FROM users WHERE id = ?`, req.params.id);
    if (!user) {
      return res.status(404).json({ error: 'Usuário não encontrado.' });
    }
    res.json(user);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Erro interno do servidor.' });
  }
});

/* ---------- UPDATE ---------- */
router.put('/:id', async (req, res) => {
  try {
    validateUserPayload(req.body);
    const { name, email, birthdate } = req.body;
    const db = await getDB();

    const existing = await db.get(`SELECT * FROM users WHERE id = ?`, req.params.id);
    if (!existing) {
      return res.status(404).json({ error: 'Usuário não encontrado.' });
    }

    await db.run(
      `UPDATE users SET name = ?, email = ?, birthdate = ? WHERE id = ?`,
      [name, email, birthdate, req.params.id]
    );

    const updated = await db.get(`SELECT * FROM users WHERE id = ?`, req.params.id);
    res.json(updated);
  } catch (err) {
    if (err.message.includes('UNIQUE constraint failed')) {
      res.status(400).json({ error: 'E‑mail já cadastrado.' });
    } else if (err.message.startsWith('Campo')) {
      res.status(400).json({ error: err.message });
    } else {
      console.error(err);
      res.status(500).json({ error: 'Erro interno do servidor.' });
    }
  }
});

/* ---------- DELETE ---------- */
router.delete('/:id', async (req, res) => {
  try {
    const db = await getDB();
    const existing = await db.get(`SELECT * FROM users WHERE id = ?`, req.params.id);
    if (!existing) {
      return res.status(404).json({ error: 'Usuário não encontrado.' });
    }

    await db.run(`DELETE FROM users WHERE id = ?`, req.params.id);
    res.status(204).send(); // No Content
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Erro interno do servidor.' });
  }
});

export default router;
```

### **`src/index.js`**
```js
/**
 * Entrada da aplicação.
 * Configura o Express, middlewares e monta as rotas.
 */

import express from 'express';
import usersRouter from './routes/users.js';
import { init as initDB } from './db.js';

// Inicializa o banco antes de subir o servidor
await initDB();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware para JSON
app.use(express.json());

// Rotas da API
app.use('/users', usersRouter);

// Rota raiz simples (útil para health check)
app.get('/', (req, res) => {
  res.json({ message: 'User API está rodando.' });
});

// Tratamento de rotas não encontradas
app.use((req, res) => {
  res.status(404).json({ error: 'Rota não encontrada.' });
});

// Inicia o servidor
app.listen(PORT, () => {
  console.log(`🚀 Server rodando em http://localhost:${PORT}`);
});
```

---

## 3. Como executar

```bash
# 1️⃣ Clone / copie o projeto
git clone <url> user-api   # ou apenas crie a pasta e cole os arquivos
cd user-api

# 2️⃣ Instale as dependências
npm install

# 3️⃣ Crie / atualize o banco SQLite (executa o script de migração)
npm run migrate

# 4️⃣ Inicie a aplicação
npm start            # modo produção
# ou
npm run dev          # modo desenvolvimento (com nodemon)
```

A API ficará escutando em **http://localhost:3000**.

---

## 4. Testes rápidos (usando `curl`)

```bash
# criar usuário
curl -X POST http://localhost:3000/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Ana Silva","email":"ana@example.com","birthdate":"1990-04-12"}'

# listar todos
curl http://localhost:3000/users

# buscar por id
curl http://localhost:3000/users/1

# atualizar
curl -X PUT http://localhost:3000/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"Ana S.","email":"ana.s@example.com","birthdate":"1990-04-12"}'

# remover
curl -X DELETE http://localhost:3000/users/1 -i   # -i para ver o código 204
```

---

## 5. Observações & decisões de design

* **Framework mínimo:** Apenas `express` (necessário para roteamento e middleware).  
* **SQLite driver:** `sqlite3` (padrão da comunidade, sem dependências nativas extras).  
* **Validação:** Implementada manualmente para evitar bibliotecas adicionais (ex.: `joi`).  
* **Banco:** Arquivo `database.sqlite` na raiz do projeto – ideal para protótipos e testes.  
* **Migrations simples:** Um único script SQL executado via `npm run migrate`.  
* **Código modular:** Separação clara entre camada de banco (`db.js`), rotas (`users.js`) e servidor (`index.js`).  
* **Status HTTP:** 201 (criado), 200 (sucesso), 204 (no content para delete), 400 (bad request), 404 (not found), 500 (erro interno).  

Pronto! Basta seguir as instruções acima e a API estará funcionando. 🚀