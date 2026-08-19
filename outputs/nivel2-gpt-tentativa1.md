<!--
nivel: 2 - API REST
provider: gpt
model: gpt-5.6
tentativa: 1
temperature: 0.2
timestamp: 2026-08-18T17:04:36.984Z
metadata: {"model":"gpt-5.6-sol","usage":{"prompt_tokens":196,"completion_tokens":5019,"total_tokens":5215,"prompt_tokens_details":{"cached_tokens":0,"cache_write_tokens":0,"audio_tokens":0},"completion_tokens_details":{"reasoning_tokens":899,"audio_tokens":0,"accepted_prediction_tokens":0,"rejected_prediction_tokens":0}},"finish_reason":"stop"}
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

A implementação abaixo usa **Express** apenas para a camada HTTP e **better-sqlite3** para persistência SQLite. A API valida os dados, impede e-mails duplicados e retorna erros em JSON.

## Estrutura do projeto

```text
api-usuarios/
├── package.json
├── server.js
├── README.md
└── .gitignore
```

---

### `package.json`

```json
{
  "name": "api-usuarios-sqlite",
  "version": "1.0.0",
  "description": "API REST para cadastro de usuários com Node.js e SQLite",
  "main": "server.js",
  "type": "commonjs",
  "scripts": {
    "start": "node server.js",
    "dev": "node --watch server.js"
  },
  "engines": {
    "node": ">=20"
  },
  "dependencies": {
    "better-sqlite3": "^12.2.0",
    "express": "^5.1.0"
  }
}
```

---

### `server.js`

```javascript
'use strict';

const express = require('express');
const Database = require('better-sqlite3');
const fs = require('node:fs');
const path = require('node:path');

const app = express();

const port = Number(process.env.PORT || 3000);
const configuredDatabasePath =
  process.env.DB_PATH || path.join(__dirname, 'data', 'usuarios.sqlite');

if (!Number.isInteger(port) || port < 1 || port > 65535) {
  console.error('A variável PORT deve ser um número inteiro entre 1 e 65535.');
  process.exit(1);
}

/*
 * É possível usar DB_PATH=:memory: para executar a API com um banco
 * temporário em memória.
 */
const databasePath =
  configuredDatabasePath === ':memory:'
    ? configuredDatabasePath
    : path.resolve(configuredDatabasePath);

if (databasePath !== ':memory:') {
  fs.mkdirSync(path.dirname(databasePath), { recursive: true });
}

const db = new Database(databasePath);

/*
 * WAL melhora a concorrência entre leituras e escritas.
 * foreign_keys é habilitado por segurança para futuras tabelas relacionadas.
 */
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

db.exec(`
  CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL CHECK(length(nome) BETWEEN 1 AND 120),
    email TEXT NOT NULL COLLATE NOCASE UNIQUE
      CHECK(length(email) BETWEEN 3 AND 254),
    data_nascimento TEXT NOT NULL
  );
`);

const statements = {
  listar: db.prepare(`
    SELECT id, nome, email, data_nascimento
    FROM usuarios
    ORDER BY id ASC
  `),

  buscarPorId: db.prepare(`
    SELECT id, nome, email, data_nascimento
    FROM usuarios
    WHERE id = ?
  `),

  criar: db.prepare(`
    INSERT INTO usuarios (nome, email, data_nascimento)
    VALUES (@nome, @email, @data_nascimento)
  `),

  atualizar: db.prepare(`
    UPDATE usuarios
    SET nome = @nome,
        email = @email,
        data_nascimento = @data_nascimento
    WHERE id = @id
  `),

  remover: db.prepare(`
    DELETE FROM usuarios
    WHERE id = ?
  `)
};

app.disable('x-powered-by');
app.use(express.json({ limit: '100kb' }));

function converterUsuarioParaJson(usuario) {
  return {
    id: usuario.id,
    nome: usuario.nome,
    email: usuario.email,
    dataNascimento: usuario.data_nascimento
  };
}

function validarId(valor) {
  /*
   * IDs com zeros à esquerda são aceitos, mas números decimais,
   * negativos, zero e textos misturados são rejeitados.
   */
  if (!/^[1-9]\d*$/.test(valor)) {
    return null;
  }

  const id = Number(valor);

  if (!Number.isSafeInteger(id)) {
    return null;
  }

  return id;
}

function ehAnoBissexto(ano) {
  return ano % 400 === 0 || (ano % 4 === 0 && ano % 100 !== 0);
}

function ehDataValida(data) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(data)) {
    return false;
  }

  const [ano, mes, dia] = data.split('-').map(Number);
  const diasPorMes = [
    31,
    ehAnoBissexto(ano) ? 29 : 28,
    31,
    30,
    31,
    30,
    31,
    31,
    30,
    31,
    30,
    31
  ];

  if (ano < 1 || mes < 1 || mes > 12) {
    return false;
  }

  if (dia < 1 || dia > diasPorMes[mes - 1]) {
    return false;
  }

  /*
   * Por se tratar de data de nascimento, datas futuras são rejeitadas.
   * A comparação funciona porque o formato ISO YYYY-MM-DD é ordenável.
   */
  const hoje = new Date();
  const hojeIso = [
    String(hoje.getFullYear()).padStart(4, '0'),
    String(hoje.getMonth() + 1).padStart(2, '0'),
    String(hoje.getDate()).padStart(2, '0')
  ].join('-');

  return data <= hojeIso;
}

function ehEmailValido(email) {
  /*
   * Esta é uma validação prática, não uma implementação completa do RFC 5322.
   * Ela evita formatos evidentemente inválidos sem rejeitar a maioria dos
   * endereços de e-mail usados normalmente.
   */
  return (
    email.length >= 3 &&
    email.length <= 254 &&
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
  );
}

function validarUsuario(body) {
  if (body === null || typeof body !== 'object' || Array.isArray(body)) {
    return {
      erro: 'O corpo da requisição deve ser um objeto JSON.'
    };
  }

  const camposPermitidos = new Set([
    'nome',
    'email',
    'dataNascimento'
  ]);

  const camposDesconhecidos = Object.keys(body).filter(
    (campo) => !camposPermitidos.has(campo)
  );

  if (camposDesconhecidos.length > 0) {
    return {
      erro: `Campos não reconhecidos: ${camposDesconhecidos.join(', ')}.`
    };
  }

  if (typeof body.nome !== 'string') {
    return {
      erro: 'O campo "nome" é obrigatório e deve ser uma string.'
    };
  }

  const nome = body.nome.trim();

  if (nome.length < 1 || nome.length > 120) {
    return {
      erro: 'O campo "nome" deve ter entre 1 e 120 caracteres.'
    };
  }

  if (typeof body.email !== 'string') {
    return {
      erro: 'O campo "email" é obrigatório e deve ser uma string.'
    };
  }

  /*
   * E-mails são normalizados para letras minúsculas.
   * A coluna também usa COLLATE NOCASE para garantir unicidade sem
   * diferenciação entre letras maiúsculas e minúsculas.
   */
  const email = body.email.trim().toLowerCase();

  if (!ehEmailValido(email)) {
    return {
      erro: 'O campo "email" deve conter um endereço de e-mail válido.'
    };
  }

  if (typeof body.dataNascimento !== 'string') {
    return {
      erro:
        'O campo "dataNascimento" é obrigatório e deve usar o formato YYYY-MM-DD.'
    };
  }

  const dataNascimento = body.dataNascimento.trim();

  if (!ehDataValida(dataNascimento)) {
    return {
      erro:
        'O campo "dataNascimento" deve ser uma data válida, não futura, no formato YYYY-MM-DD.'
    };
  }

  return {
    dados: {
      nome,
      email,
      data_nascimento: dataNascimento
    }
  };
}

function exigirJson(req, res, next) {
  if (!req.is('application/json')) {
    return res.status(415).json({
      erro: 'O cabeçalho Content-Type deve ser application/json.'
    });
  }

  next();
}

function ehErroDeEmailDuplicado(error) {
  return (
    error &&
    typeof error.code === 'string' &&
    error.code.startsWith('SQLITE_CONSTRAINT') &&
    String(error.message).includes('usuarios.email')
  );
}

app.get('/', (req, res) => {
  res.status(200).json({
    nome: 'API de usuários',
    endpoints: {
      criar: 'POST /usuarios',
      listar: 'GET /usuarios',
      buscar: 'GET /usuarios/:id',
      atualizar: 'PUT /usuarios/:id',
      remover: 'DELETE /usuarios/:id'
    }
  });
});

app.post('/usuarios', exigirJson, (req, res, next) => {
  const validacao = validarUsuario(req.body);

  if (validacao.erro) {
    return res.status(400).json({
      erro: validacao.erro
    });
  }

  try {
    const resultado = statements.criar.run(validacao.dados);
    const usuario = statements.buscarPorId.get(resultado.lastInsertRowid);

    return res
      .status(201)
      .location(`/usuarios/${usuario.id}`)
      .json(converterUsuarioParaJson(usuario));
  } catch (error) {
    if (ehErroDeEmailDuplicado(error)) {
      return res.status(409).json({
        erro: 'Já existe um usuário cadastrado com este e-mail.'
      });
    }

    return next(error);
  }
});

app.get('/usuarios', (req, res) => {
  const usuarios = statements.listar.all().map(converterUsuarioParaJson);
  res.status(200).json(usuarios);
});

app.get('/usuarios/:id', (req, res) => {
  const id = validarId(req.params.id);

  if (id === null) {
    return res.status(400).json({
      erro: 'O ID do usuário deve ser um número inteiro positivo.'
    });
  }

  const usuario = statements.buscarPorId.get(id);

  if (!usuario) {
    return res.status(404).json({
      erro: 'Usuário não encontrado.'
    });
  }

  return res.status(200).json(converterUsuarioParaJson(usuario));
});

app.put('/usuarios/:id', exigirJson, (req, res, next) => {
  const id = validarId(req.params.id);

  if (id === null) {
    return res.status(400).json({
      erro: 'O ID do usuário deve ser um número inteiro positivo.'
    });
  }

  /*
   * PUT foi adotado como substituição completa do recurso.
   * Portanto, nome, email e dataNascimento são sempre obrigatórios.
   */
  const validacao = validarUsuario(req.body);

  if (validacao.erro) {
    return res.status(400).json({
      erro: validacao.erro
    });
  }

  if (!statements.buscarPorId.get(id)) {
    return res.status(404).json({
      erro: 'Usuário não encontrado.'
    });
  }

  try {
    statements.atualizar.run({
      id,
      ...validacao.dados
    });

    const usuarioAtualizado = statements.buscarPorId.get(id);

    return res.status(200).json(
      converterUsuarioParaJson(usuarioAtualizado)
    );
  } catch (error) {
    if (ehErroDeEmailDuplicado(error)) {
      return res.status(409).json({
        erro: 'Já existe um usuário cadastrado com este e-mail.'
      });
    }

    return next(error);
  }
});

app.delete('/usuarios/:id', (req, res) => {
  const id = validarId(req.params.id);

  if (id === null) {
    return res.status(400).json({
      erro: 'O ID do usuário deve ser um número inteiro positivo.'
    });
  }

  const resultado = statements.remover.run(id);

  if (resultado.changes === 0) {
    return res.status(404).json({
      erro: 'Usuário não encontrado.'
    });
  }

  /*
   * Uma remoção bem-sucedida retorna HTTP 204 e, por definição,
   * não possui corpo de resposta.
   */
  return res.status(204).send();
});

app.use((req, res) => {
  res.status(404).json({
    erro: 'Rota não encontrada.'
  });
});

/*
 * Middleware para JSON malformado e erros inesperados.
 * Detalhes internos não são enviados ao cliente.
 */
app.use((error, req, res, next) => {
  if (error instanceof SyntaxError && error.status === 400 && 'body' in error) {
    return res.status(400).json({
      erro: 'O corpo da requisição contém JSON inválido.'
    });
  }

  console.error('Erro interno:', error);

  if (res.headersSent) {
    return next(error);
  }

  return res.status(500).json({
    erro: 'Ocorreu um erro interno no servidor.'
  });
});

const server = app.listen(port, () => {
  console.log(`API disponível em http://localhost:${port}`);
  console.log(
    `Banco de dados: ${
      databasePath === ':memory:' ? 'memória' : databasePath
    }`
  );
});

let encerrando = false;

function encerrarServidor(signal) {
  if (encerrando) {
    return;
  }

  encerrando = true;
  console.log(`\nSinal ${signal} recebido. Encerrando servidor...`);

  server.close(() => {
    db.close();
    console.log('Servidor e banco de dados encerrados.');
    process.exit(0);
  });

  setTimeout(() => {
    console.error('Encerramento forçado após tempo limite.');
    process.exit(1);
  }, 10_000).unref();
}

process.on('SIGINT', () => encerrarServidor('SIGINT'));
process.on('SIGTERM', () => encerrarServidor('SIGTERM'));
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

### `README.md`

```markdown
# API REST de usuários

API REST em Node.js para cadastro de usuários, com persistência em SQLite.

## Requisitos

- Node.js 20 ou superior
- npm

## Instalação

No diretório do projeto, execute:

```bash
npm install
```

## Execução

```bash
npm start
```

A API ficará disponível em:

```text
http://localhost:3000
```

O banco será criado automaticamente em:

```text
data/usuarios.sqlite
```

## Desenvolvimento com reinicialização automática

```bash
npm run dev
```

## Variáveis de ambiente

### Alterar a porta

Linux/macOS:

```bash
PORT=8080 npm start
```

Windows PowerShell:

```powershell
$env:PORT=8080
npm start
```

### Alterar o arquivo do banco

Linux/macOS:

```bash
DB_PATH=./meu-banco.sqlite npm start
```

Windows PowerShell:

```powershell
$env:DB_PATH="./meu-banco.sqlite"
npm start
```

Também é possível usar um banco temporário em memória:

Linux/macOS:

```bash
DB_PATH=:memory: npm start
```

Windows PowerShell:

```powershell
$env:DB_PATH=":memory:"
npm start
```

## Modelo de usuário

```json
{
  "id": 1,
  "nome": "Maria Silva",
  "email": "maria@example.com",
  "dataNascimento": "1990-05-20"
}
```

A data de nascimento deve usar o formato `YYYY-MM-DD`.

## Endpoints

### Criar usuário

```http
POST /usuarios
Content-Type: application/json
```

Exemplo:

```bash
curl -i -X POST http://localhost:3000/usuarios \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Maria Silva",
    "email": "maria@example.com",
    "dataNascimento": "1990-05-20"
  }'
```

Resposta: `201 Created`.

### Listar usuários

```http
GET /usuarios
```

Exemplo:

```bash
curl -i http://localhost:3000/usuarios
```

Resposta: `200 OK`.

### Buscar usuário pelo ID

```http
GET /usuarios/:id
```

Exemplo:

```bash
curl -i http://localhost:3000/usuarios/1
```

Respostas possíveis:

- `200 OK`
- `400 Bad Request`, para ID inválido
- `404 Not Found`, caso não exista

### Atualizar usuário

O `PUT` substitui todos os dados editáveis do usuário. Por isso, os três campos são obrigatórios.

```http
PUT /usuarios/:id
Content-Type: application/json
```

Exemplo:

```bash
curl -i -X PUT http://localhost:3000/usuarios/1 \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Maria Souza",
    "email": "maria.souza@example.com",
    "dataNascimento": "1990-05-20"
  }'
```

Respostas possíveis:

- `200 OK`
- `400 Bad Request`, para dados inválidos
- `404 Not Found`, caso não exista
- `409 Conflict`, caso o e-mail já esteja cadastrado

### Remover usuário

```http
DELETE /usuarios/:id
```

Exemplo:

```bash
curl -i -X DELETE http://localhost:3000/usuarios/1
```

Respostas possíveis:

- `204 No Content`
- `400 Bad Request`, para ID inválido
- `404 Not Found`, caso não exista

## Formato dos erros

Os erros são retornados em JSON:

```json
{
  "erro": "Descrição do erro."
}
```

## Códigos HTTP utilizados

- `200 OK`: consulta ou atualização bem-sucedida
- `201 Created`: usuário criado
- `204 No Content`: usuário removido
- `400 Bad Request`: ID, JSON ou dados inválidos
- `404 Not Found`: rota ou usuário não encontrado
- `409 Conflict`: e-mail duplicado
- `415 Unsupported Media Type`: `Content-Type` diferente de `application/json`
- `500 Internal Server Error`: erro inesperado
```

## Como executar rapidamente

```bash
mkdir api-usuarios
cd api-usuarios
```

Crie os arquivos acima e execute:

```bash
npm install
npm start
```

Depois, acesse:

```text
http://localhost:3000/usuarios
```