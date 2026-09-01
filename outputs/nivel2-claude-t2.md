<!--
nivel: 2 - API REST
provider: claude
model: claude-sonnet-5
tentativa: 2
temperature: 0.2
timestamp: 2026-08-18T22:39:25.596Z
metadata: {"model":"claude-sonnet-5","stop_reason":"end_turn"}
-->

## Resposta do modelo

### `package.json`

```json
{
  "name": "users-rest-api",
  "version": "1.0.0",
  "description": "API REST para cadastro de usuarios (nome, email, data de nascimento) com persistencia em SQLite",
  "main": "server.js",
  "type": "commonjs",
  "scripts": {
    "start": "node server.js",
    "dev": "node --watch server.js"
  },
  "dependencies": {
    "better-sqlite3": "^11.3.0",
    "express": "^4.19.2"
  }
}
```

---

### `db.js`

```javascript
const path = require('path');
const Database = require('better-sqlite3');

const DB_PATH = path.join(__dirname, 'usuarios.db');

const db = new Database(DB_PATH);

db.pragma('foreign_keys = ON');

db.exec(`
  CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    data_nascimento TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
  );
`);

module.exports = db;
```

---

### `validation.js`

```javascript
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const DATE_REGEX = /^\d{4}-\d{2}-\d{2}$/;

function isValidDate(dateStr) {
  if (!DATE_REGEX.test(dateStr)) return false;
  const date = new Date(dateStr + 'T00:00:00Z');
  if (Number.isNaN(date.getTime())) return false;

  const [year, month, day] = dateStr.split('-').map(Number);
  return (
    date.getUTCFullYear() === year &&
    date.getUTCMonth() + 1 === month &&
    date.getUTCDate() === day
  );
}

function isFutureDate(dateStr) {
  const date = new Date(dateStr + 'T00:00:00Z');
  const today = new Date();
  today.setUTCHours(0, 0, 0, 0);
  return date.getTime() > today.getTime();
}

function validateUser(data, options = {}) {
  const { partial = false } = options;
  const errors = [];
  const { nome, email, data_nascimento } = data;

  if (!partial || nome !== undefined) {
    if (typeof nome !== 'string' || nome.trim().length === 0) {
      errors.push('O campo "nome" e obrigatorio e deve ser uma string nao vazia.');
    }
  }

  if (!partial || email !== undefined) {
    if (typeof email !== 'string' || !EMAIL_REGEX.test(email.trim())) {
      errors.push('O campo "email" e obrigatorio e deve conter um e-mail valido.');
    }
  }

  if (!partial || data_nascimento !== undefined) {
    if (typeof data_nascimento !== 'string' || !isValidDate(data_nascimento)) {
      errors.push('O campo "data_nascimento" e obrigatorio e deve estar no formato YYYY-MM-DD e ser uma data valida.');
    } else if (isFutureDate(data_nascimento)) {
      errors.push('O campo "data_nascimento" nao pode ser uma data futura.');
    }
  }

  return errors;
}

module.exports = { validateUser };
```

---

### `userRepository.js`

```javascript
const db = require('./db');

function nowISO() {
  return new Date().toISOString();
}

const stmts = {
  insert: db.prepare(`
    INSERT INTO usuarios (nome, email, data_nascimento, created_at, updated_at)
    VALUES (@nome, @email, @data_nascimento, @created_at, @updated_at)
  `),
  selectAll: db.prepare(`SELECT * FROM usuarios ORDER BY id ASC`),
  selectById: db.prepare(`SELECT * FROM usuarios WHERE id = ?`),
  update: db.prepare(`
    UPDATE usuarios
    SET nome = @nome, email = @email, data_nascimento = @data_nascimento, updated_at = @updated_at
    WHERE id = @id
  `),
  remove: db.prepare(`DELETE FROM usuarios WHERE id = ?`),
};

function create({ nome, email, data_nascimento }) {
  const timestamp = nowISO();
  const info = stmts.insert.run({
    nome: nome.trim(),
    email: email.trim().toLowerCase(),
    data_nascimento,
    created_at: timestamp,
    updated_at: timestamp,
  });
  return stmts.selectById.get(info.lastInsertRowid);
}

function findAll() {
  return stmts.selectAll.all();
}

function findById(id) {
  return stmts.selectById.get(id);
}

function update(id, current, changes) {
  const merged = {
    nome: changes.nome !== undefined ? changes.nome.trim() : current.nome,
    email: changes.email !== undefined ? changes.email.trim().toLowerCase() : current.email,
    data_nascimento: changes.data_nascimento !== undefined ? changes.data_nascimento : current.data_nascimento,
    updated_at: nowISO(),
    id,
  };
  stmts.update.run(merged);
  return stmts.selectById.get(id);
}

function remove(id) {
  const info = stmts.remove.run(id);
  return info.changes > 0;
}

module.exports = { create, findAll, findById, update, remove };
```

---

### `routes/users.js`

```javascript
const express = require('express');
const router = express.Router();

const repo = require('../userRepository');
const { validateUser } = require('../validation');

function isUniqueConstraintError(err) {
  return err && err.code === 'SQLITE_CONSTRAINT_UNIQUE';
}

router.post('/', (req, res) => {
  const { nome, email, data_nascimento } = req.body || {};
  const errors = validateUser({ nome, email, data_nascimento });

  if (errors.length > 0) {
    return res.status(400).json({ errors });
  }

  try {
    const user = repo.create({ nome, email, data_nascimento });
    return res.status(201).json(user);
  } catch (err) {
    if (isUniqueConstraintError(err)) {
      return res.status(409).json({ errors: ['Ja existe um usuario cadastrado com este e-mail.'] });
    }
    console.error(err);
    return res.status(500).json({ errors: ['Erro interno ao criar usuario.'] });
  }
});

router.get('/', (req, res) => {
  try {
    const users = repo.findAll();
    return res.status(200).json(users);
  } catch (err) {
    console.error(err);
    return res.status(500).json({ errors: ['Erro interno ao listar usuarios.'] });
  }
});

router.get('/:id', (req, res) => {
  const id = Number(req.params.id);
  if (!Number.isInteger(id) || id <= 0) {
    return res.status(400).json({ errors: ['ID invalido.'] });
  }

  const user = repo.findById(id);
  if (!user) {
    return res.status(404).json({ errors: ['Usuario nao encontrado.'] });
  }
  return res.status(200).json(user);
});

router.put('/:id', (req, res) => {
  const id = Number(req.params.id);
  if (!Number.isInteger(id) || id <= 0) {
    return res.status(400).json({ errors: ['ID invalido.'] });
  }

  const current = repo.findById(id);
  if (!current) {
    return res.status(404).json({ errors: ['Usuario nao encontrado.'] });
  }

  const { nome, email, data_nascimento } = req.body || {};

  if (nome === undefined && email === undefined && data_nascimento === undefined) {
    return res.status(400).json({ errors: ['Informe ao menos um campo para atualizar (nome, email ou data_nascimento).'] });
  }

  const errors = validateUser({ nome, email, data_nascimento }, { partial: true });
  if (errors.length > 0) {
    return res.status(400).json({ errors });
  }

  try {
    const updated = repo.update(id, current, { nome, email, data_nascimento });
    return res.status(200).json(updated);
  } catch (err) {
    if (isUniqueConstraintError(err)) {
      return res.status(409).json({ errors: ['Ja existe um usuario cadastrado com este e-mail.'] });
    }
    console.error(err);
    return res.status(500).json({ errors: ['Erro interno ao atualizar usuario.'] });
  }
});

router.delete('/:id', (req, res) => {
  const id = Number(req.params.id);
  if (!Number.isInteger(id) || id <= 0) {
    return res.status(400).json({ errors: ['ID invalido.'] });
  }

  const removed = repo.remove(id);
  if (!removed) {
    return res.status(404).json({ errors: ['Usuario nao encontrado.'] });
  }
  return res.status(204).send();
});

module.exports = router;
```

---

### `server.js`

```javascript
const express = require('express');
const usersRouter = require('./routes/users');

const app = express();

app.use(express.json());

app.use((err, req, res, next) => {
  if (err.type === 'entity.parse.failed') {
    return res.status(400).json({ errors: ['JSON invalido no corpo da requisicao.'] });
  }
  next(err);
});

app.use('/users', usersRouter);

app.get('/', (req, res) => {
  res.status(200).json({ status: 'ok', service: 'users-rest-api' });
});

app.use((req, res) => {
  res.status(404).json({ errors: ['Rota nao encontrada.'] });
});

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ errors: ['Erro interno no servidor.'] });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`API rodando em http://localhost:${PORT}`);
});

module.exports = app;
```
