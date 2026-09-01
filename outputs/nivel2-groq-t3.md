<!--
nivel: 2 - API REST
provider: groq
model: openai/gpt-oss-120b
tentativa: 3
temperature: 0.2
timestamp: 2026-08-31T09:08:01.193Z
metadata: {"model":"openai/gpt-oss-120b","usage":{"queue_time":0.151508462,"prompt_tokens":261,"prompt_time":0.011892806,"completion_tokens":3239,"completion_time":6.851809037,"total_tokens":3500,"total_time":6.863701843,"completion_tokens_details":{"reasoning_tokens":38}},"finish_reason":"stop"}
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

**📦 Projeto – API REST de Usuários com Node.js + SQLite**

A seguir está tudo o que você precisa para colocar a API em funcionamento: estrutura de pastas, arquivos de código, `package.json`, script de inicialização e instruções detalhadas de como instalar as dependências e rodar a aplicação.

---  

## 1. Estrutura de pastas

```
user-api/
├─ src/
│  ├─ db.js          # conexão e funções de acesso ao SQLite
│  ├─ routes.js      # definição dos endpoints da API
│  └─ app.js         # ponto de entrada – configura o Express
├─ data/
│  └─ users.db       # arquivo SQLite (será criado automaticamente)
├─ package.json
└─ README.md
```

---  

## 2. Arquivo **package.json**

```json
// package.json
{
  "name": "user-api",
  "version": "1.0.0",
  "description": "API REST simples para cadastro de usuários (nome, email, data de nascimento) usando Node.js e SQLite.",
  "main": "src/app.js",
  "scripts": {
    "start": "node src/app.js",
    "dev": "nodemon src/app.js"
  },
  "keywords": [
    "node",
    "express",
    "sqlite",
    "rest",
    "api"
  ],
  "author": "Seu Nome <seu@email.com>",
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

> **Por que apenas estas dependências?**  
> - **express** – micro‑framework web minimalista, suficiente para criar rotas e enviar respostas JSON.  
> - **sqlite3** – driver oficial para SQLite, não requer servidor externo.  
> - **nodemon** (devDependency) – opcional, reinicia a aplicação automaticamente durante o desenvolvimento.

---  

## 3. Conexão e camada de acesso ao banco – **src/db.js**

```js
// src/db.js
/**
 * Módulo responsável por abrir a conexão com o SQLite,
 * garantir que a tabela `users` exista e expor funções CRUD.
 */

const path = require('path');
const sqlite3 = require('sqlite3').verbose();

// Caminho absoluto para o arquivo de banco (cria a pasta data se necessário)
const dbPath = path.resolve(__dirname, '..', 'data', 'users.db');
const db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error('❌ Erro ao abrir o banco SQLite:', err.message);
    process.exit(1);
  }
  console.log('✅ Conectado ao SQLite em', dbPath);
});

// Cria a tabela se ainda não existir
const initSQL = `
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    birthdate TEXT NOT NULL   -- armazenado como ISO string (YYYY-MM-DD)
  );
`;

db.run(initSQL, (err) => {
  if (err) {
    console.error('❌ Erro ao criar a tabela users:', err.message);
    process.exit(1);
  }
});

/* ---------- Funções de acesso ---------- */

function createUser({ name, email, birthdate }) {
  return new Promise((resolve, reject) => {
    const sql = `INSERT INTO users (name, email, birthdate) VALUES (?,?,?)`;
    db.run(sql, [name, email, birthdate], function (err) {
      if (err) return reject(err);
      // `this.lastID` contém o id gerado
      resolve({ id: this.lastID, name, email, birthdate });
    });
  });
}

function getAllUsers() {
  return new Promise((resolve, reject) => {
    db.all(`SELECT * FROM users`, [], (err, rows) => {
      if (err) return reject(err);
      resolve(rows);
    });
  });
}

function getUserById(id) {
  return new Promise((resolve, reject) => {
    db.get(`SELECT * FROM users WHERE id = ?`, [id], (err, row) => {
      if (err) return reject(err);
      resolve(row);
    });
  });
}

function updateUser(id, { name, email, birthdate }) {
  return new Promise((resolve, reject) => {
    const sql = `UPDATE users SET name = ?, email = ?, birthdate = ? WHERE id = ?`;
    db.run(sql, [name, email, birthdate, id], function (err) {
      if (err) return reject(err);
      if (this.changes === 0) return resolve(null); // usuário não encontrado
      resolve({ id, name, email, birthdate });
    });
  });
}

function deleteUser(id) {
  return new Promise((resolve, reject) => {
    db.run(`DELETE FROM users WHERE id = ?`, [id], function (err) {
      if (err) return reject(err);
      resolve(this.changes > 0); // true se apagou algo
    });
  });
}

/* ---------- Exporta ---------- */
module.exports = {
  createUser,
  getAllUsers,
  getUserById,
  updateUser,
  deleteUser,
  // Exportamos o objeto db apenas para testes ou fechamento manual, se necessário
  db,
};
```

---  

## 4. Definição das rotas – **src/routes.js**

```js
// src/routes.js
/**
 * Todas as rotas da API REST.
 * Cada rota devolve JSON e o código de status HTTP adequado.
 */

const express = require('express');
const router = express.Router();
const db = require('./db');

/* ---------- Validação simples (sem libs externas) ---------- */
function validateUserPayload(payload) {
  const errors = [];

  if (!payload.name || typeof payload.name !== 'string' || payload.name.trim() === '') {
    errors.push('`name` é obrigatório e deve ser uma string não vazia.');
  }

  if (!payload.email || typeof payload.email !== 'string' || !/^\S+@\S+\.\S+$/.test(payload.email)) {
    errors.push('`email` é obrigatório e deve ser um e‑mail válido.');
  }

  if (!payload.birthdate || typeof payload.birthdate !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(payload.birthdate)) {
    errors.push('`birthdate` é obrigatório e deve estar no formato YYYY-MM-DD.');
  }

  return errors;
}

/* ---------- CREATE – POST /users ---------- */
router.post('/users', async (req, res) => {
  const errors = validateUserPayload(req.body);
  if (errors.length) {
    return res.status(400).json({ errors });
  }

  try {
    const user = await db.createUser(req.body);
    res.status(201).json(user); // 201 Created
  } catch (err) {
    if (err.message.includes('UNIQUE constraint failed')) {
      return res.status(409).json({ error: 'E‑mail já cadastrado.' }); // 409 Conflict
    }
    console.error(err);
    res.status(500).json({ error: 'Erro interno ao criar usuário.' });
  }
});

/* ---------- READ – GET /users ---------- */
router.get('/users', async (req, res) => {
  try {
    const users = await db.getAllUsers();
    res.json(users);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Erro interno ao listar usuários.' });
  }
});

/* ---------- READ – GET /users/:id ---------- */
router.get('/users/:id', async (req, res) => {
  const id = Number(req.params.id);
  if (Number.isNaN(id)) return res.status(400).json({ error: 'ID inválido.' });

  try {
    const user = await db.getUserById(id);
    if (!user) return res.status(404).json({ error: 'Usuário não encontrado.' });
    res.json(user);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Erro interno ao buscar usuário.' });
  }
});

/* ---------- UPDATE – PUT /users/:id ---------- */
router.put('/users/:id', async (req, res) => {
  const id = Number(req.params.id);
  if (Number.isNaN(id)) return res.status(400).json({ error: 'ID inválido.' });

  const errors = validateUserPayload(req.body);
  if (errors.length) {
    return res.status(400).json({ errors });
  }

  try {
    const updated = await db.updateUser(id, req.body);
    if (!updated) return res.status(404).json({ error: 'Usuário não encontrado.' });
    res.json(updated);
  } catch (err) {
    if (err.message.includes('UNIQUE constraint failed')) {
      return res.status(409).json({ error: 'E‑mail já cadastrado por outro usuário.' });
    }
    console.error(err);
    res.status(500).json({ error: 'Erro interno ao atualizar usuário.' });
  }
});

/* ---------- DELETE – DELETE /users/:id ---------- */
router.delete('/users/:id', async (req, res) => {
  const id = Number(req.params.id);
  if (Number.isNaN(id)) return res.status(400).json({ error: 'ID inválido.' });

  try {
    const deleted = await db.deleteUser(id);
    if (!deleted) return res.status(404).json({ error: 'Usuário não encontrado.' });
    res.status(204).send(); // 204 No Content
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Erro interno ao remover usuário.' });
  }
});

module.exports = router;
```

---  

## 5. Aplicação principal – **src/app.js**

```js
// src/app.js
/**
 * Entrypoint da aplicação.
 * Configura o Express, middlewares JSON e as rotas.
 */

const express = require('express');
const routes = require('./routes');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware para receber JSON no corpo da requisição
app.use(express.json());

// Rotas da API
app.use('/api', routes);

// Tratamento de rotas inexistentes
app.use((req, res) => {
  res.status(404).json({ error: 'Rota não encontrada.' });
});

// Inicia o servidor
app.listen(PORT, () => {
  console.log(`🚀 API rodando em http://localhost:${PORT}/api`);
});
```

---  

## 6. Arquivo de instruções – **README.md**

```markdown
# API REST de Usuários (Node.js + SQLite)

Esta é uma API mínima para cadastrar, listar, atualizar e remover usuários,
armazenando os dados em um banco SQLite local.

## 📋 Requisitos

- **Node.js** ≥ 14 (recomendado ≥ 18)
- **npm** (vem junto com o Node)

## 📦 Instalação

```bash
# 1. Clone ou copie o projeto para sua máquina
git clone https://github.com/SEU_USUARIO/user-api.git   # (ou simplesmente copie a pasta)

cd user-api

# 2. Instale as dependências
npm install
```

> O script `npm install` criará a pasta `data/` e o arquivo `data/users.db` quando a aplicação for iniciada pela primeira vez.

## ▶️ Executando

```bash
# Modo produção
npm start

# Ou, para desenvolvimento (reinicia ao salvar arquivos)
npm run dev
```

A API ficará disponível em:

```
http://localhost:3000/api
```

## 📚 Endpoints

| Método | URL                     | Descrição                         | Corpo (JSON)                                 | Respostas |
|--------|------------------------|-----------------------------------|---------------------------------------------|-----------|
| POST   | `/api/users`           | Cria novo usuário                 | `{ "name": "...", "email": "...", "birthdate": "YYYY-MM-DD" }` | `201 Created` (usuario), `400 Bad Request`, `409 Conflict` |
| GET    | `/api/users`           | Lista todos os usuários           | —                                           | `200 OK` (array) |
| GET    | `/api/users/:id`       | Busca usuário por ID              | —                                           | `200 OK`, `404 Not Found`, `400 Bad Request` |
| PUT    | `/api/users/:id`       | Atualiza usuário existente        | mesmo payload de **POST**                   | `200 OK`, `400 Bad Request`, `404 Not Found`, `409 Conflict` |
| DELETE | `/api/users/:id`       | Remove usuário                    | —                                           | `204 No Content`, `404 Not Found`, `400 Bad Request` |

## 🛠️ Testando rapidamente com **curl**

```bash
# Criar usuário
curl -X POST http://localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Ana Silva","email":"ana@example.com","birthdate":"1990-04-12"}'

# Listar usuários
curl http://localhost:3000/api/users

# Atualizar (id = 1)
curl -X PUT http://localhost:3000/api/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"Ana S.","email":"ana.s@example.com","birthdate":"1990-04-12"}'

# Deletar (id = 1)
curl -X DELETE http://localhost:3000/api/users/1
```

## 📂 Onde estão os dados?

O SQLite é salvo em `data/users.db`. Você pode abrir esse arquivo com
qualquer cliente SQLite (por exemplo, `sqlite3 data/users.db`).

## ⚙️ Personalizações

- **Porta** – altere a variável de ambiente `PORT` antes de iniciar:
  ```bash
  PORT=4000 npm start
  ```
- **Validação** – o código usa validação mínima em‑line; caso precise
  de regras mais avançadas, basta substituir `validateUserPayload`
  por uma biblioteca como `joi` (não incluída para manter a restrição
  de “frameworks estritamente necessários”).

## 📄 Licença

Este projeto está licenciado sob a **MIT License** – sinta‑se à vontade
para usar, modificar e distribuir.

---  

**Pronto!** Basta seguir as instruções acima e sua API REST de usuários
estará rodando em poucos segundos. Boa codificação! 🚀