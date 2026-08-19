<!--
nivel: 2 - API REST
provider: claude
model: claude-sonnet-5
tentativa: 1
temperature: 0.2
timestamp: 2026-08-18T22:38:26.168Z
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
    "dev": "node server.js"
  },
  "dependencies": {
    "express": "^4.19.2",
    "better-sqlite3": "^11.3.0"
  },
  "engines": {
    "node": ">=18"
  }
}
```

---

### `db.js`

```javascript
const path = require('path');
const Database = require('better-sqlite3');

const DB_PATH = path.join(__dirname, 'users.db');

const db = new Database(DB_PATH, { verbose: null });

db.pragma('foreign_keys = ON');

db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    birth_date TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
  );
`);

module.exports = db;
```

---

### `validators.js`

```javascript
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const DATE_REGEX = /^\d{4}-\d{2}-\d{2}$/;

function validateUser(data, partial = false) {
  const errors = [];
  const { name, email, birth_date } = data;

  if (!partial || name !== undefined) {
    if (typeof name !== 'string' || name.trim().length < 2 || name.trim().length > 100) {
      errors.push('O campo "name" deve ser uma string entre 2 e 100 caracteres.');
    }
  }

  if (!partial || email !== undefined) {
    if (typeof email !== 'string' || !EMAIL_REGEX.test(email.trim())) {
      errors.push('O campo "email" deve ser um endereco de e-mail valido.');
    }
  }

  if (!partial || birth_date !== undefined) {
    if (typeof birth_date !== 'string' || !DATE_REGEX.test(birth_date)) {
      errors.push('O campo "birth_date" deve estar no formato YYYY-MM-DD.');
    } else {
      const date = new Date(birth_date + 'T00:00:00Z');
      const now = new Date();
      if (isNaN(date.getTime())) {
        errors.push('O campo "birth_date" nao representa uma data valida.');
      } else if (date.getTime() > now.getTime()) {
        errors.push('O campo "birth_date" nao pode ser uma data futura.');
      }
    }
  }

  return errors;
}

module.exports = { validateUser };
```

---

### `app.js`

```javascript
const express = require('express');
const db = require('./db');
const { validateUser } = require('./validators');

const app = express();

app.use(express.json());

function errorResponse(res, status, message, details) {
  const body = { error: message };
  if (details) body.details = details;
  return res.status(status).json(body);
}

app.post('/users', (req, res) => {
  const { name, email, birth_date } = req.body || {};
  const errors = validateUser({ name, email, birth_date }, false);

  if (errors.length > 0) {
    return errorResponse(res, 400, 'Dados invalidos.', errors);
  }

  try {
    const stmt = db.prepare(
      'INSERT INTO users (name, email, birth_date) VALUES (?, ?, ?)'
    );
    const info = stmt.run(name.trim(), email.trim().toLowerCase(), birth_date);

    const created = db
      .prepare('SELECT * FROM users WHERE id = ?')
      .get(info.lastInsertRowid);

    return res.status(201).json(created);
  } catch (err) {
    if (err.code === 'SQLITE_CONSTRAINT_UNIQUE' || /UNIQUE/.test(err.message)) {
      return errorResponse(res, 409, 'Ja existe um usuario cadastrado com este e-mail.');
    }
    console.error(err);
    return errorResponse(res, 500, 'Erro interno ao criar usuario.');
  }
});

app.get('/users', (req, res) => {
  try {
    let { page, limit } = req.query;

    page = parseInt(page, 10);
    limit = parseInt(limit, 10);

    if (!Number.isInteger(page) || page < 1) page = 1;
    if (!Number.isInteger(limit) || limit < 1 || limit > 100) limit = 20;

    const offset = (page - 1) * limit;

    const total = db.prepare('SELECT COUNT(*) as count FROM users').get().count;

    const rows = db
      .prepare('SELECT * FROM users ORDER BY id ASC LIMIT ? OFFSET ?')
      .all(limit, offset);

    return res.status(200).json({
      data: rows,
      meta: {
        page,
        limit,
        total,
        total_pages: Math.ceil(total / limit) || 1,
      },
    });
  } catch (err) {
    console.error(err);
    return errorResponse(res, 500, 'Erro interno ao listar usuarios.');
  }
});

app.get('/users/:id', (req, res) => {
  const id = parseInt(req.params.id, 10);
  if (!Number.isInteger(id)) {
    return errorResponse(res, 400, 'ID invalido.');
  }

  try {
    const user = db.prepare('SELECT * FROM users WHERE id = ?').get(id);
    if (!user) {
      return errorResponse(res, 404, 'Usuario nao encontrado.');
    }
    return res.status(200).json(user);
  } catch (err) {
    console.error(err);
    return errorResponse(res, 500, 'Erro interno ao buscar usuario.');
  }
});

app.put('/users/:id', (req, res) => {
  const id = parseInt(req.params.id, 10);
  if (!Number.isInteger(id)) {
    return errorResponse(res, 400, 'ID invalido.');
  }

  const existing = db.prepare('SELECT * FROM users WHERE id = ?').get(id);
  if (!existing) {
    return errorResponse(res, 404, 'Usuario nao encontrado.');
  }

  const { name, email, birth_date } = req.body || {};

  if (name === undefined && email === undefined && birth_date === undefined) {
    return errorResponse(res, 400, 'Informe ao menos um campo para atualizar (name, email ou birth_date).');
  }

  const errors = validateUser({ name, email, birth_date }, true);
  if (errors.length > 0) {
    return errorResponse(res, 400, 'Dados invalidos.', errors);
  }

  const updated = {
    name: name !== undefined ? name.trim() : existing.name,
    email: email !== undefined ? email.trim().toLowerCase() : existing.email,
    birth_date: birth_date !== undefined ? birth_date : existing.birth_date,
  };

  try {
    db.prepare(
      `UPDATE users
       SET name = ?, email = ?, birth_date = ?, updated_at = datetime('now')
       WHERE id = ?`
    ).run(updated.name, updated.email, updated.birth_date, id);

    const result = db.prepare('SELECT * FROM users WHERE id = ?').get(id);
    return res.status(200).json(result);
  } catch (err) {
    if (err.code === 'SQLITE_CONSTRAINT_UNIQUE' || /UNIQUE/.test(err.message)) {
      return errorResponse(res, 409, 'Ja existe um usuario cadastrado com este e-mail.');
    }
    console.error(err);
    return errorResponse(res, 500, 'Erro interno ao atualizar usuario.');
  }
});

app.delete('/users/:id', (req, res) => {
  const id = parseInt(req.params.id, 10);
  if (!Number.isInteger(id)) {
    return errorResponse(res, 400, 'ID invalido.');
  }

  try {
    const existing = db.prepare('SELECT * FROM users WHERE id = ?').get(id);
    if (!existing) {
      return errorResponse(res, 404, 'Usuario nao encontrado.');
    }

    db.prepare('DELETE FROM users WHERE id = ?').run(id);
    return res.status(204).send();
  } catch (err) {
    console.error(err);
    return errorResponse(res, 500, 'Erro interno ao remover usuario.');
  }
});

app.use((req, res) => {
  return errorResponse(res, 404, 'Rota nao encontrada.');
});

app.use((err, req, res, next) => {
  if (err.type === 'entity.parse.failed') {
    return errorResponse(res, 400, 'Corpo da requisicao JSON invalido.');
  }
  console.error(err);
  return errorResponse(res, 500, 'Erro interno do servidor.');
});

module.exports = app;
```

---

### `server.js`

```javascript
const app = require('./app');

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log(`API de usuarios rodando em http://localhost:${PORT}`);
});
```
