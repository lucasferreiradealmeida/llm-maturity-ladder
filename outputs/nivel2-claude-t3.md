<!--
nivel: 2 - API REST
provider: claude
model: claude-sonnet-5
tentativa: 3
temperature: 0.2
timestamp: 2026-08-31T08:40:23.030Z
metadata: {"model":"claude-sonnet-5","usage":{"input_tokens":339,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"cache_creation":{"ephemeral_5m_input_tokens":0,"ephemeral_1h_input_tokens":0},"output_tokens":6619,"output_tokens_details":{"thinking_tokens":733},"service_tier":"standard","inference_geo":"global"},"stop_reason":"end_turn"}
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

# Sistema de Cadastro de Usuários — API REST

## Decisões de projeto (documentadas conforme solicitado)

- **Framework**: Express foi utilizado por ser o mínimo necessário para roteamento HTTP, parsing de JSON e tratamento de erros de forma limpa em Node.js puro seria muito verboso (reimplementar roteamento, parsing de body etc.). Não foram usados frameworks adicionais (ORM, validação, etc.).
- **Banco de dados**: `better-sqlite3` foi escolhido por ser síncrono, rápido, sem dependências nativas problemáticas e simples de usar para um CRUD básico (evita a complexidade de callbacks/promises do pacote `sqlite3`).
- **Formato de data**: `data_nascimento` é armazenada como texto no formato `YYYY-MM-DD` (ISO 8601, apenas data). Validação garante formato correto e data não futura.
- **E-mail único**: constraint `UNIQUE` no banco; tentativa de duplicar retorna `409 Conflict`.
- **IDs**: autoincrement inteiro, expostos como `id` no JSON.
- **Timestamps**: `criado_em` e `atualizado_em` são gerenciados automaticamente pelo servidor.
- **Atualização parcial**: `PUT /usuarios/:id` aceita atualização total ou parcial dos campos (nome, email, data_nascimento) — qualquer campo omitido mantém o valor atual.
- **Banco de dados em arquivo**: `database.sqlite` criado automaticamente na raiz do projeto na primeira execução.

---

### `package.json`

```json
{
  "name": "api-cadastro-usuarios",
  "version": "1.0.0",
  "description": "API REST para cadastro de usuarios com persistencia em SQLite",
  "main": "src/server.js",
  "type": "commonjs",
  "scripts": {
    "start": "node src/server.js",
    "dev": "node --watch src/server.js"
  },
  "dependencies": {
    "better-sqlite3": "^11.3.0",
    "express": "^4.19.2"
  }
}
```

---

### `src/db.js`

```javascript
// db.js
// Responsavel por inicializar a conexao com o SQLite e criar a tabela
// de usuarios caso ainda nao exista.

const path = require('path');
const Database = require('better-sqlite3');

// Arquivo do banco fica na raiz do projeto.
const DB_PATH = path.join(__dirname, '..', 'database.sqlite');

const db = new Database(DB_PATH);

// Habilita chaves estrangeiras (nao usado neste sistema, mas e boa pratica)
db.pragma('journal_mode = WAL');

// Criacao da tabela de usuarios, caso nao exista.
// - nome: obrigatorio
// - email: obrigatorio e unico
// - data_nascimento: armazenada como TEXT no formato YYYY-MM-DD
// - criado_em / atualizado_em: timestamps ISO gerenciados pela aplicacao
db.exec(`
  CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    data_nascimento TEXT NOT NULL,
    criado_em TEXT NOT NULL,
    atualizado_em TEXT NOT NULL
  )
`);

module.exports = db;
```

---

### `src/validators.js`

```javascript
// validators.js
// Funcoes de validacao simples para os dados de usuario.
// Evita dependencia de bibliotecas externas de validacao.

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const DATE_REGEX = /^\d{4}-\d{2}-\d{2}$/;

/**
 * Valida o payload de criacao/atualizacao de usuario.
 * @param {object} data - { nome, email, data_nascimento }
 * @param {boolean} partial - se true, campos ausentes sao ignorados (usado no PUT parcial)
 * @returns {string[]} lista de mensagens de erro (vazia se valido)
 */
function validarUsuario(data, partial = false) {
  const erros = [];
  const { nome, email, data_nascimento } = data;

  // --- nome ---
  if (!partial || nome !== undefined) {
    if (typeof nome !== 'string' || nome.trim().length === 0) {
      erros.push('O campo "nome" e obrigatorio e deve ser uma string nao vazia.');
    } else if (nome.trim().length > 150) {
      erros.push('O campo "nome" deve ter no maximo 150 caracteres.');
    }
  }

  // --- email ---
  if (!partial || email !== undefined) {
    if (typeof email !== 'string' || !EMAIL_REGEX.test(email)) {
      erros.push('O campo "email" e obrigatorio e deve conter um endereco de e-mail valido.');
    }
  }

  // --- data_nascimento ---
  if (!partial || data_nascimento !== undefined) {
    if (typeof data_nascimento !== 'string' || !DATE_REGEX.test(data_nascimento)) {
      erros.push('O campo "data_nascimento" e obrigatorio e deve estar no formato YYYY-MM-DD.');
    } else {
      const data = new Date(data_nascimento + 'T00:00:00Z');
      const hoje = new Date();
      if (Number.isNaN(data.getTime())) {
        erros.push('O campo "data_nascimento" contem uma data invalida.');
      } else if (data.getTime() > hoje.getTime()) {
        erros.push('O campo "data_nascimento" nao pode ser uma data futura.');
      }
    }
  }

  return erros;
}

module.exports = { validarUsuario };
```

---

### `src/server.js`

```javascript
// server.js
// Ponto de entrada da API REST de cadastro de usuarios.
// Endpoints:
//   POST   /usuarios       -> cria um usuario
//   GET    /usuarios       -> lista todos os usuarios
//   GET    /usuarios/:id   -> obtem um usuario especifico
//   PUT    /usuarios/:id   -> atualiza um usuario (parcial ou total)
//   DELETE /usuarios/:id   -> remove um usuario

const express = require('express');
const db = require('./db');
const { validarUsuario } = require('./validators');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

// Middleware simples para tratar JSON invalido no body (express.json lanca erro sincrono)
app.use((err, req, res, next) => {
  if (err.type === 'entity.parse.failed') {
    return res.status(400).json({ erro: 'JSON invalido no corpo da requisicao.' });
  }
  next(err);
});

// ---------- Helpers ----------

function nowISO() {
  return new Date().toISOString();
}

function buscarUsuarioPorId(id) {
  const stmt = db.prepare('SELECT * FROM usuarios WHERE id = ?');
  return stmt.get(id);
}

// ---------- Rotas ----------

// Criar usuario
app.post('/usuarios', (req, res) => {
  const { nome, email, data_nascimento } = req.body || {};

  const erros = validarUsuario({ nome, email, data_nascimento }, false);
  if (erros.length > 0) {
    return res.status(400).json({ erros });
  }

  const timestamp = nowISO();

  try {
    const stmt = db.prepare(`
      INSERT INTO usuarios (nome, email, data_nascimento, criado_em, atualizado_em)
      VALUES (?, ?, ?, ?, ?)
    `);
    const info = stmt.run(nome.trim(), email.trim().toLowerCase(), data_nascimento, timestamp, timestamp);

    const usuarioCriado = buscarUsuarioPorId(info.lastInsertRowid);
    return res.status(201).json(usuarioCriado);
  } catch (err) {
    if (err.code === 'SQLITE_CONSTRAINT_UNIQUE' || /UNIQUE constraint failed/.test(err.message)) {
      return res.status(409).json({ erro: 'Ja existe um usuario cadastrado com este e-mail.' });
    }
    console.error(err);
    return res.status(500).json({ erro: 'Erro interno ao criar usuario.' });
  }
});

// Listar todos os usuarios
app.get('/usuarios', (req, res) => {
  try {
    const usuarios = db.prepare('SELECT * FROM usuarios ORDER BY id ASC').all();
    return res.status(200).json(usuarios);
  } catch (err) {
    console.error(err);
    return res.status(500).json({ erro: 'Erro interno ao listar usuarios.' });
  }
});

// Obter um usuario especifico
app.get('/usuarios/:id', (req, res) => {
  const id = Number(req.params.id);

  if (!Number.isInteger(id) || id <= 0) {
    return res.status(400).json({ erro: 'O parametro "id" deve ser um numero inteiro positivo.' });
  }

  const usuario = buscarUsuarioPorId(id);
  if (!usuario) {
    return res.status(404).json({ erro: 'Usuario nao encontrado.' });
  }

  return res.status(200).json(usuario);
});

// Atualizar usuario (aceita atualizacao parcial)
app.put('/usuarios/:id', (req, res) => {
  const id = Number(req.params.id);

  if (!Number.isInteger(id) || id <= 0) {
    return res.status(400).json({ erro: 'O parametro "id" deve ser um numero inteiro positivo.' });
  }

  const usuarioExistente = buscarUsuarioPorId(id);
  if (!usuarioExistente) {
    return res.status(404).json({ erro: 'Usuario nao encontrado.' });
  }

  const { nome, email, data_nascimento } = req.body || {};

  // Validacao parcial: apenas os campos enviados sao validados
  const erros = validarUsuario({ nome, email, data_nascimento }, true);
  if (erros.length > 0) {
    return res.status(400).json({ erros });
  }

  if (nome === undefined && email === undefined && data_nascimento === undefined) {
    return res.status(400).json({ erro: 'Informe ao menos um campo para atualizar (nome, email ou data_nascimento).' });
  }

  const novoNome = nome !== undefined ? nome.trim() : usuarioExistente.nome;
  const novoEmail = email !== undefined ? email.trim().toLowerCase() : usuarioExistente.email;
  const novaData = data_nascimento !== undefined ? data_nascimento : usuarioExistente.data_nascimento;
  const timestamp = nowISO();

  try {
    const stmt = db.prepare(`
      UPDATE usuarios
      SET nome = ?, email = ?, data_nascimento = ?, atualizado_em = ?
      WHERE id = ?
    `);
    stmt.run(novoNome, novoEmail, novaData, timestamp, id);

    const usuarioAtualizado = buscarUsuarioPorId(id);
    return res.status(200).json(usuarioAtualizado);
  } catch (err) {
    if (err.code === 'SQLITE_CONSTRAINT_UNIQUE' || /UNIQUE constraint failed/.test(err.message)) {
      return res.status(409).json({ erro: 'Ja existe um usuario cadastrado com este e-mail.' });
    }
    console.error(err);
    return res.status(500).json({ erro: 'Erro interno ao atualizar usuario.' });
  }
});

// Remover usuario
app.delete('/usuarios/:id', (req, res) => {
  const id = Number(req.params.id);

  if (!Number.isInteger(id) || id <= 0) {
    return res.status(400).json({ erro: 'O parametro "id" deve ser um numero inteiro positivo.' });
  }

  const usuarioExistente = buscarUsuarioPorId(id);
  if (!usuarioExistente) {
    return res.status(404).json({ erro: 'Usuario nao encontrado.' });
  }

  try {
    db.prepare('DELETE FROM usuarios WHERE id = ?').run(id);
    return res.status(204).send();
  } catch (err) {
    console.error(err);
    return res.status(500).json({ erro: 'Erro interno ao remover usuario.' });
  }
});

// Rota nao encontrada (404 generico)
app.use((req, res) => {
  res.status(404).json({ erro: 'Rota nao encontrada.' });
});

// Tratamento de erros nao previstos
app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ erro: 'Erro interno do servidor.' });
});

app.listen(PORT, () => {
  console.log(`API rodando em http://localhost:${PORT}`);
});
```

---

### `.gitignore`

```
node_modules/
database.sqlite
database.sqlite-wal
database.sqlite-shm
npm-debug.log
```

---

### `README.md`

```markdown
# API de Cadastro de Usuários

API REST simples para gerenciamento de usuários (nome, e-mail e data de
nascimento), com persistência em SQLite.

## Tecnologias

- Node.js
- Express (roteamento e parsing de JSON)
- better-sqlite3 (persistência em SQLite)

## Instalação

```bash
npm install
```

## Execução

```bash
npm start
```

O servidor sobe por padrão em `http://localhost:3000`. O arquivo do banco
(`database.sqlite`) é criado automaticamente na raiz do projeto na primeira
execução.

Para desenvolvimento com reinício automático ao salvar arquivos:

```bash
npm run dev
```

## Endpoints

### Criar usuário
`POST /usuarios`

Body (JSON):
```json
{
  "nome": "Maria Silva",
  "email": "maria@exemplo.com",
  "data_nascimento": "1990-05-20"
}
```

Respostas:
- `201 Created` — usuário criado com sucesso.
- `400 Bad Request` — dados inválidos.
- `409 Conflict` — e-mail já cadastrado.

### Listar usuários
`GET /usuarios`

Resposta: `200 OK` com array de usuários.

### Obter usuário por ID
`GET /usuarios/:id`

Respostas:
- `200 OK` — usuário encontrado.
- `404 Not Found` — usuário não existe.

### Atualizar usuário (parcial ou total)
`PUT /usuarios/:id`

Body (JSON, todos os campos opcionais, mas ao menos um deve ser enviado):
```json
{
  "nome": "Maria Souza"
}
```

Respostas:
- `200 OK` — usuário atualizado.
- `400 Bad Request` — dados inválidos.
- `404 Not Found` — usuário não existe.
- `409 Conflict` — e-mail já usado por outro usuário.

### Remover usuário
`DELETE /usuarios/:id`

Respostas:
- `204 No Content` — usuário removido com sucesso.
- `404 Not Found` — usuário não existe.

## Exemplos com curl

```bash
# Criar
curl -X POST http://localhost:3000/usuarios \
  -H "Content-Type: application/json" \
  -d '{"nome":"Maria Silva","email":"maria@exemplo.com","data_nascimento":"1990-05-20"}'

# Listar
curl http://localhost:3000/usuarios

# Obter um
curl http://localhost:3000/usuarios/1

# Atualizar
curl -X PUT http://localhost:3000/usuarios/1 \
  -H "Content-Type: application/json" \
  -d '{"nome":"Maria Souza"}'

# Remover
curl -X DELETE http://localhost:3000/usuarios/1
```

## Estrutura do projeto

```
.
├── package.json
├── README.md
├── database.sqlite      (gerado automaticamente)
└── src/
    ├── server.js         # rotas e inicialização do servidor
    ├── db.js             # conexão e schema do SQLite
    └── validators.js     # validação de dados de entrada
```
```

---

## Como executar (resumo rápido)

```bash
npm install
npm start
```

A API estará disponível em `http://localhost:3000`, com os endpoints descritos acima em `/usuarios`.