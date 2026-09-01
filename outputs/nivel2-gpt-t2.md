<!--
nivel: 2 - API REST
provider: gpt
model: gpt-5.6
tentativa: 2
temperature: 0.2
timestamp: 2026-08-18T17:05:45.009Z
metadata: {"model":"gpt-5.6-sol","usage":{"prompt_tokens":196,"completion_tokens":5584,"total_tokens":5780,"prompt_tokens_details":{"cached_tokens":0,"cache_write_tokens":0,"audio_tokens":0},"completion_tokens_details":{"reasoning_tokens":1024,"audio_tokens":0,"accepted_prediction_tokens":0,"rejected_prediction_tokens":0}},"finish_reason":"stop"}
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

A implementação abaixo usa apenas o módulo HTTP nativo do Node.js e a biblioteca `better-sqlite3` para persistência. Não há framework web.

### Estrutura do projeto

```text
api-usuarios/
├── package.json
├── .gitignore
└── src/
    ├── database.js
    └── server.js
```

---

### `package.json`

```json
{
  "name": "api-rest-usuarios",
  "version": "1.0.0",
  "description": "API REST de cadastro de usuários com Node.js e SQLite",
  "main": "src/server.js",
  "type": "commonjs",
  "scripts": {
    "start": "node src/server.js",
    "dev": "node --watch src/server.js"
  },
  "engines": {
    "node": ">=18"
  },
  "dependencies": {
    "better-sqlite3": "^11.8.1"
  }
}
```

---

### `.gitignore`

```gitignore
node_modules/
data/
.env
npm-debug.log*
.DS_Store
```

---

### `src/database.js`

```javascript
const fs = require('node:fs');
const path = require('node:path');
const Database = require('better-sqlite3');

/*
 * Decisões assumidas:
 * - O banco é salvo em ./data/usuarios.db por padrão.
 * - O caminho pode ser alterado pela variável DATABASE_PATH.
 * - E-mails são únicos sem diferenciar letras maiúsculas e minúsculas.
 * - Datas de nascimento são armazenadas como texto no formato YYYY-MM-DD.
 */

const configuredPath = process.env.DATABASE_PATH;
const databasePath = configuredPath
  ? configuredPath === ':memory:'
    ? configuredPath
    : path.resolve(configuredPath)
  : path.resolve(process.cwd(), 'data', 'usuarios.db');

if (databasePath !== ':memory:') {
  fs.mkdirSync(path.dirname(databasePath), { recursive: true });
}

const database = new Database(databasePath);

database.pragma('foreign_keys = ON');
database.pragma('journal_mode = WAL');

database.exec(`
  CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL COLLATE NOCASE UNIQUE,
    data_nascimento TEXT NOT NULL,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
  );
`);

const statements = {
  create: database.prepare(`
    INSERT INTO usuarios (nome, email, data_nascimento)
    VALUES (@nome, @email, @data_nascimento)
  `),

  findAll: database.prepare(`
    SELECT
      id,
      nome,
      email,
      data_nascimento,
      criado_em,
      atualizado_em
    FROM usuarios
    ORDER BY id ASC
  `),

  findById: database.prepare(`
    SELECT
      id,
      nome,
      email,
      data_nascimento,
      criado_em,
      atualizado_em
    FROM usuarios
    WHERE id = ?
  `),

  deleteById: database.prepare(`
    DELETE FROM usuarios
    WHERE id = ?
  `)
};

function createUser(user) {
  const result = statements.create.run(user);
  return findUserById(Number(result.lastInsertRowid));
}

function listUsers() {
  return statements.findAll.all();
}

function findUserById(id) {
  return statements.findById.get(id);
}

function updateUser(id, fields) {
  const allowedFields = ['nome', 'email', 'data_nascimento'];
  const fieldsToUpdate = allowedFields.filter((field) =>
    Object.prototype.hasOwnProperty.call(fields, field)
  );

  if (fieldsToUpdate.length === 0) {
    return findUserById(id);
  }

  // Os nomes das colunas são escolhidos apenas a partir de uma lista fixa.
  const assignments = fieldsToUpdate
    .map((field) => `${field} = @${field}`)
    .join(', ');

  const statement = database.prepare(`
    UPDATE usuarios
    SET
      ${assignments},
      atualizado_em = CURRENT_TIMESTAMP
    WHERE id = @id
  `);

  statement.run({
    id,
    ...fields
  });

  return findUserById(id);
}

function deleteUser(id) {
  const result = statements.deleteById.run(id);
  return result.changes > 0;
}

function closeDatabase() {
  if (database.open) {
    database.close();
  }
}

module.exports = {
  databasePath,
  createUser,
  listUsers,
  findUserById,
  updateUser,
  deleteUser,
  closeDatabase
};
```

---

### `src/server.js`

```javascript
const http = require('node:http');
const {
  databasePath,
  createUser,
  listUsers,
  findUserById,
  updateUser,
  deleteUser,
  closeDatabase
} = require('./database');

const HOST = process.env.HOST || '0.0.0.0';
const PORT = parsePort(process.env.PORT || '3000');
const MAX_BODY_SIZE = 1024 * 1024; // 1 MB

const USER_FIELDS = ['nome', 'email', 'data_nascimento'];

class HttpError extends Error {
  constructor(statusCode, message, details) {
    super(message);
    this.name = 'HttpError';
    this.statusCode = statusCode;
    this.details = details;
  }
}

function parsePort(value) {
  const port = Number(value);

  if (!Number.isInteger(port) || port < 1 || port > 65535) {
    throw new Error('A variável PORT deve ser um número inteiro entre 1 e 65535.');
  }

  return port;
}

function sendJson(response, statusCode, data, additionalHeaders = {}) {
  const body = JSON.stringify(data);

  response.writeHead(statusCode, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': Buffer.byteLength(body),
    'X-Content-Type-Options': 'nosniff',
    ...additionalHeaders
  });

  response.end(body);
}

function sendError(response, statusCode, message, details) {
  const payload = {
    erro: {
      status: statusCode,
      mensagem: message
    }
  };

  if (details) {
    payload.erro.detalhes = details;
  }

  sendJson(response, statusCode, payload);
}

async function readJsonBody(request) {
  const contentType = request.headers['content-type'] || '';

  if (!contentType.toLowerCase().startsWith('application/json')) {
    throw new HttpError(
      415,
      'O cabeçalho Content-Type deve ser application/json.'
    );
  }

  const chunks = [];
  let totalSize = 0;
  let bodyTooLarge = false;

  for await (const chunk of request) {
    totalSize += chunk.length;

    if (totalSize > MAX_BODY_SIZE) {
      bodyTooLarge = true;
      continue;
    }

    chunks.push(chunk);
  }

  if (bodyTooLarge) {
    throw new HttpError(
      413,
      `O corpo da requisição excede o limite de ${MAX_BODY_SIZE} bytes.`
    );
  }

  const rawBody = Buffer.concat(chunks).toString('utf8').trim();

  if (!rawBody) {
    throw new HttpError(400, 'O corpo JSON da requisição é obrigatório.');
  }

  let body;

  try {
    body = JSON.parse(rawBody);
  } catch {
    throw new HttpError(400, 'O corpo da requisição contém JSON inválido.');
  }

  if (
    body === null ||
    Array.isArray(body) ||
    typeof body !== 'object'
  ) {
    throw new HttpError(400, 'O corpo da requisição deve ser um objeto JSON.');
  }

  return body;
}

function parseUserId(rawId) {
  if (!/^\d+$/.test(rawId)) {
    throw new HttpError(400, 'O ID do usuário deve ser um inteiro positivo.');
  }

  const id = Number(rawId);

  if (!Number.isSafeInteger(id) || id <= 0) {
    throw new HttpError(400, 'O ID do usuário deve ser um inteiro positivo.');
  }

  return id;
}

function isValidDate(date) {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(date);

  if (!match) {
    return false;
  }

  const year = Number(match[1]);
  const month = Number(match[2]);
  const day = Number(match[3]);

  const parsedDate = new Date(Date.UTC(year, month - 1, day));

  return (
    parsedDate.getUTCFullYear() === year &&
    parsedDate.getUTCMonth() === month - 1 &&
    parsedDate.getUTCDate() === day
  );
}

function normalizeAndValidateUser(body, { partial = false } = {}) {
  /*
   * Decisões assumidas:
   * - Campos desconhecidos são rejeitados para evitar erros silenciosos.
   * - Nome deve ter de 2 a 120 caracteres.
   * - E-mail deve ter no máximo 254 caracteres.
   * - Data deve usar exatamente o formato YYYY-MM-DD e representar uma
   *   data válida.
   * - Não é aplicada a regra de que a data precisa estar no passado,
   *   pois isso não foi especificado.
   */
  const unknownFields = Object.keys(body).filter(
    (field) => !USER_FIELDS.includes(field)
  );

  if (unknownFields.length > 0) {
    throw new HttpError(400, 'A requisição contém campos desconhecidos.', {
      campos: unknownFields
    });
  }

  if (!partial) {
    const missingFields = USER_FIELDS.filter(
      (field) => !Object.prototype.hasOwnProperty.call(body, field)
    );

    if (missingFields.length > 0) {
      throw new HttpError(400, 'Existem campos obrigatórios ausentes.', {
        campos: missingFields
      });
    }
  } else if (Object.keys(body).length === 0) {
    throw new HttpError(
      400,
      'Informe pelo menos um campo para atualização.'
    );
  }

  const errors = {};
  const normalized = {};

  if (Object.prototype.hasOwnProperty.call(body, 'nome')) {
    if (typeof body.nome !== 'string') {
      errors.nome = 'O nome deve ser uma string.';
    } else {
      const nome = body.nome.trim();

      if (nome.length < 2 || nome.length > 120) {
        errors.nome = 'O nome deve ter entre 2 e 120 caracteres.';
      } else {
        normalized.nome = nome;
      }
    }
  }

  if (Object.prototype.hasOwnProperty.call(body, 'email')) {
    if (typeof body.email !== 'string') {
      errors.email = 'O e-mail deve ser uma string.';
    } else {
      const email = body.email.trim().toLowerCase();
      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

      if (email.length > 254 || !emailPattern.test(email)) {
        errors.email = 'Informe um endereço de e-mail válido.';
      } else {
        normalized.email = email;
      }
    }
  }

  if (Object.prototype.hasOwnProperty.call(body, 'data_nascimento')) {
    if (typeof body.data_nascimento !== 'string') {
      errors.data_nascimento =
        'A data de nascimento deve ser uma string no formato YYYY-MM-DD.';
    } else {
      const dataNascimento = body.data_nascimento.trim();

      if (!isValidDate(dataNascimento)) {
        errors.data_nascimento =
          'Informe uma data válida no formato YYYY-MM-DD.';
      } else {
        normalized.data_nascimento = dataNascimento;
      }
    }
  }

  if (Object.keys(errors).length > 0) {
    throw new HttpError(422, 'Os dados informados são inválidos.', errors);
  }

  return normalized;
}

function isUniqueEmailError(error) {
  return (
    error &&
    typeof error.code === 'string' &&
    error.code.startsWith('SQLITE_CONSTRAINT') &&
    String(error.message).includes('usuarios.email')
  );
}

async function handleCreateUser(request, response) {
  const body = await readJsonBody(request);
  const data = normalizeAndValidateUser(body);

  try {
    const user = createUser(data);

    sendJson(response, 201, user, {
      Location: `/usuarios/${user.id}`
    });
  } catch (error) {
    if (isUniqueEmailError(error)) {
      throw new HttpError(409, 'Já existe um usuário com este e-mail.');
    }

    throw error;
  }
}

function handleListUsers(response) {
  sendJson(response, 200, listUsers());
}

function handleGetUser(response, id) {
  const user = findUserById(id);

  if (!user) {
    throw new HttpError(404, 'Usuário não encontrado.');
  }

  sendJson(response, 200, user);
}

async function handleUpdateUser(request, response, id, partial) {
  if (!findUserById(id)) {
    throw new HttpError(404, 'Usuário não encontrado.');
  }

  const body = await readJsonBody(request);
  const data = normalizeAndValidateUser(body, { partial });

  try {
    const updatedUser = updateUser(id, data);
    sendJson(response, 200, updatedUser);
  } catch (error) {
    if (isUniqueEmailError(error)) {
      throw new HttpError(409, 'Já existe um usuário com este e-mail.');
    }

    throw error;
  }
}

function handleDeleteUser(response, id) {
  const removed = deleteUser(id);

  if (!removed) {
    throw new HttpError(404, 'Usuário não encontrado.');
  }

  /*
   * Foi escolhido status 200, em vez de 204, para que a remoção também
   * tenha uma resposta JSON conforme solicitado.
   */
  sendJson(response, 200, {
    mensagem: 'Usuário removido com sucesso.',
    id
  });
}

async function requestHandler(request, response) {
  try {
    const url = new URL(request.url, `http://${request.headers.host || 'localhost'}`);
    const pathname =
      url.pathname.length > 1 && url.pathname.endsWith('/')
        ? url.pathname.slice(0, -1)
        : url.pathname;

    if (url.search && pathname !== '/usuarios') {
      // Parâmetros desconhecidos não alteram as rotas por ID.
    }

    if (pathname === '/' && request.method === 'GET') {
      return sendJson(response, 200, {
        nome: 'API REST de usuários',
        endpoints: {
          criar: 'POST /usuarios',
          listar: 'GET /usuarios',
          buscar: 'GET /usuarios/:id',
          substituir: 'PUT /usuarios/:id',
          atualizar_parcialmente: 'PATCH /usuarios/:id',
          remover: 'DELETE /usuarios/:id'
        }
      });
    }

    if (pathname === '/usuarios') {
      if (request.method === 'GET') {
        return handleListUsers(response);
      }

      if (request.method === 'POST') {
        return await handleCreateUser(request, response);
      }

      response.setHeader('Allow', 'GET, POST');
      throw new HttpError(405, 'Método HTTP não permitido para esta rota.');
    }

    const userRouteMatch = /^\/usuarios\/([^/]+)$/.exec(pathname);

    if (userRouteMatch) {
      const id = parseUserId(decodeURIComponent(userRouteMatch[1]));

      if (request.method === 'GET') {
        return handleGetUser(response, id);
      }

      if (request.method === 'PUT') {
        return await handleUpdateUser(request, response, id, false);
      }

      if (request.method === 'PATCH') {
        return await handleUpdateUser(request, response, id, true);
      }

      if (request.method === 'DELETE') {
        return handleDeleteUser(response, id);
      }

      response.setHeader('Allow', 'GET, PUT, PATCH, DELETE');
      throw new HttpError(405, 'Método HTTP não permitido para esta rota.');
    }

    throw new HttpError(404, 'Endpoint não encontrado.');
  } catch (error) {
    if (error instanceof HttpError) {
      return sendError(
        response,
        error.statusCode,
        error.message,
        error.details
      );
    }

    console.error('Erro interno não tratado:', error);

    return sendError(
      response,
      500,
      'Ocorreu um erro interno no servidor.'
    );
  }
}

const server = http.createServer(requestHandler);

server.on('clientError', (error, socket) => {
  console.error('Erro na conexão HTTP:', error.message);

  if (socket.writable) {
    socket.end(
      'HTTP/1.1 400 Bad Request\r\n' +
      'Content-Type: application/json; charset=utf-8\r\n' +
      'Connection: close\r\n' +
      '\r\n' +
      JSON.stringify({
        erro: {
          status: 400,
          mensagem: 'Requisição HTTP inválida.'
        }
      })
    );
  }
});

server.listen(PORT, HOST, () => {
  console.log(`API disponível em http://localhost:${PORT}`);
  console.log(`Banco SQLite: ${databasePath}`);
});

function shutdown(signal) {
  console.log(`\nSinal ${signal} recebido. Encerrando servidor...`);

  server.close(() => {
    closeDatabase();
    console.log('Servidor e banco de dados encerrados.');
    process.exit(0);
  });

  setTimeout(() => {
    console.error('Encerramento forçado após tempo limite.');
    closeDatabase();
    process.exit(1);
  }, 10_000).unref();
}

process.on('SIGINT', () => shutdown('SIGINT'));
process.on('SIGTERM', () => shutdown('SIGTERM'));
```

## Instalação e execução

É necessário ter o Node.js 18 ou superior instalado.

```bash
mkdir api-usuarios
cd api-usuarios
```

Crie os arquivos conforme apresentados e execute:

```bash
npm install
npm start
```

A API ficará disponível em:

```text
http://localhost:3000
```

Para executar com recarregamento automático durante o desenvolvimento:

```bash
npm run dev
```

É possível alterar a porta e o caminho do banco:

```bash
PORT=8080 DATABASE_PATH=./meu-banco.db npm start
```

No PowerShell:

```powershell
$env:PORT=8080
$env:DATABASE_PATH="./meu-banco.db"
npm start
```

## Exemplos de uso

### Criar usuário

```bash
curl -X POST http://localhost:3000/usuarios \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Maria da Silva",
    "email": "maria@example.com",
    "data_nascimento": "1990-05-20"
  }'
```

Resposta: `201 Created`

```json
{
  "id": 1,
  "nome": "Maria da Silva",
  "email": "maria@example.com",
  "data_nascimento": "1990-05-20",
  "criado_em": "2026-08-18 12:00:00",
  "atualizado_em": "2026-08-18 12:00:00"
}
```

### Listar usuários

```bash
curl http://localhost:3000/usuarios
```

### Buscar usuário por ID

```bash
curl http://localhost:3000/usuarios/1
```

### Substituir todos os dados

O `PUT` exige todos os campos:

```bash
curl -X PUT http://localhost:3000/usuarios/1 \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Maria Souza",
    "email": "maria.souza@example.com",
    "data_nascimento": "1990-05-20"
  }'
```

### Atualizar parcialmente

```bash
curl -X PATCH http://localhost:3000/usuarios/1 \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Maria Souza"
  }'
```

### Remover usuário

```bash
curl -X DELETE http://localhost:3000/usuarios/1
```

Resposta: `200 OK`

```json
{
  "mensagem": "Usuário removido com sucesso.",
  "id": 1
}
```

Principais códigos HTTP utilizados:

- `200`: operação realizada com sucesso.
- `201`: usuário criado.
- `400`: JSON, ID ou requisição inválida.
- `404`: usuário ou endpoint não encontrado.
- `405`: método HTTP não permitido.
- `409`: e-mail já cadastrado.
- `413`: corpo da requisição muito grande.
- `415`: `Content-Type` diferente de `application/json`.
- `422`: dados de usuário inválidos.
- `500`: erro interno inesperado.