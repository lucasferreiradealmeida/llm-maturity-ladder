<!--
nivel: 2 - API REST
provider: gpt
model: gpt-5.6
tentativa: 3
temperature: 0.2
timestamp: 2026-08-31T08:21:34.076Z
metadata: {"model":"gpt-5.6-sol","usage":{"prompt_tokens":196,"completion_tokens":5868,"total_tokens":6064,"prompt_tokens_details":{"cached_tokens":0,"cache_write_tokens":0,"audio_tokens":0},"completion_tokens_details":{"reasoning_tokens":1536,"audio_tokens":0,"accepted_prediction_tokens":0,"rejected_prediction_tokens":0}},"finish_reason":"stop"}
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

A implementação abaixo usa **Express** apenas para a camada HTTP e **better-sqlite3** como driver SQLite. A API utiliza nomes de campos em português:

- `nome`
- `email`
- `data_nascimento` no formato `AAAA-MM-DD`

## Estrutura do projeto

```text
api-usuarios/
├── package.json
├── .gitignore
├── README.md
└── src/
    ├── database.js
    ├── validacao.js
    └── server.js
```

---

### Arquivo: `package.json`

```json
{
  "name": "api-usuarios-sqlite",
  "version": "1.0.0",
  "description": "API REST para cadastro de usuários com Node.js e SQLite",
  "main": "src/server.js",
  "type": "commonjs",
  "scripts": {
    "start": "node src/server.js",
    "dev": "node --watch src/server.js"
  },
  "engines": {
    "node": ">=20.0.0"
  },
  "dependencies": {
    "better-sqlite3": "^11.10.0",
    "express": "^5.1.0"
  }
}
```

---

### Arquivo: `.gitignore`

```gitignore
node_modules/
data/
*.db
*.db-shm
*.db-wal
.env
npm-debug.log*
```

---

### Arquivo: `src/database.js`

```javascript
const fs = require("node:fs");
const path = require("node:path");
const Database = require("better-sqlite3");

/*
 * Por padrão, o banco é salvo em data/usuarios.db.
 * A variável DATABASE_PATH pode alterar o local.
 *
 * Exemplos:
 * DATABASE_PATH=/tmp/usuarios.db npm start
 * DATABASE_PATH=:memory: npm start
 */
const caminhoConfigurado = process.env.DATABASE_PATH;

const caminhoBanco =
  caminhoConfigurado === ":memory:"
    ? ":memory:"
    : path.resolve(
        caminhoConfigurado ||
          path.join(__dirname, "..", "data", "usuarios.db")
      );

if (caminhoBanco !== ":memory:") {
  fs.mkdirSync(path.dirname(caminhoBanco), { recursive: true });
}

const db = new Database(caminhoBanco);

/*
 * WAL melhora a concorrência entre leituras e escritas.
 * busy_timeout faz o SQLite aguardar brevemente quando o banco estiver ocupado.
 */
db.pragma("journal_mode = WAL");
db.pragma("foreign_keys = ON");
db.pragma("busy_timeout = 5000");

db.exec(`
  CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL
      CHECK (length(nome) BETWEEN 1 AND 120),
    email TEXT NOT NULL COLLATE NOCASE UNIQUE
      CHECK (length(email) BETWEEN 3 AND 254),
    data_nascimento TEXT NOT NULL
      CHECK (
        length(data_nascimento) = 10
        AND date(data_nascimento) IS NOT NULL
      ),
    criado_em TEXT NOT NULL DEFAULT (
      strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
    ),
    atualizado_em TEXT NOT NULL DEFAULT (
      strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
    )
  );

  CREATE INDEX IF NOT EXISTS idx_usuarios_nome
  ON usuarios(nome);
`);

module.exports = {
  db,
  caminhoBanco
};
```

---

### Arquivo: `src/validacao.js`

```javascript
const TAMANHO_MAXIMO_NOME = 120;
const TAMANHO_MAXIMO_EMAIL = 254;

function objetoSimples(valor) {
  return (
    valor !== null &&
    typeof valor === "object" &&
    !Array.isArray(valor)
  );
}

function dataNascimentoValida(valor) {
  if (typeof valor !== "string") {
    return false;
  }

  const resultado = /^(\d{4})-(\d{2})-(\d{2})$/.exec(valor);

  if (!resultado) {
    return false;
  }

  const ano = Number(resultado[1]);
  const mes = Number(resultado[2]);
  const dia = Number(resultado[3]);

  const data = new Date(Date.UTC(ano, mes - 1, dia));

  /*
   * A comparação dos componentes evita que datas como 2024-02-31
   * sejam automaticamente convertidas para uma data de março.
   */
  if (
    data.getUTCFullYear() !== ano ||
    data.getUTCMonth() !== mes - 1 ||
    data.getUTCDate() !== dia
  ) {
    return false;
  }

  const hoje = new Date();
  const hojeUtc = Date.UTC(
    hoje.getUTCFullYear(),
    hoje.getUTCMonth(),
    hoje.getUTCDate()
  );

  // Decisão de domínio: data de nascimento futura não é aceita.
  return data.getTime() <= hojeUtc;
}

function emailValido(valor) {
  if (
    typeof valor !== "string" ||
    valor.length < 3 ||
    valor.length > TAMANHO_MAXIMO_EMAIL
  ) {
    return false;
  }

  /*
   * Validação propositalmente simples. A aplicação verifica a estrutura
   * prática de um e-mail sem tentar reproduzir integralmente a RFC 5322.
   */
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(valor);
}

function validarUsuario(corpo) {
  const erros = {};

  if (!objetoSimples(corpo)) {
    return {
      valido: false,
      erros: {
        corpo: "O corpo da requisição deve ser um objeto JSON."
      }
    };
  }

  const nome = typeof corpo.nome === "string" ? corpo.nome.trim() : "";
  const email =
    typeof corpo.email === "string"
      ? corpo.email.trim().toLowerCase()
      : "";
  const dataNascimento =
    typeof corpo.data_nascimento === "string"
      ? corpo.data_nascimento.trim()
      : "";

  if (!nome) {
    erros.nome = "O nome é obrigatório.";
  } else if (nome.length > TAMANHO_MAXIMO_NOME) {
    erros.nome = `O nome deve possuir no máximo ${TAMANHO_MAXIMO_NOME} caracteres.`;
  }

  if (!email) {
    erros.email = "O e-mail é obrigatório.";
  } else if (!emailValido(email)) {
    erros.email = "O e-mail informado é inválido.";
  }

  if (!dataNascimento) {
    erros.data_nascimento = "A data de nascimento é obrigatória.";
  } else if (!dataNascimentoValida(dataNascimento)) {
    erros.data_nascimento =
      "A data de nascimento deve ser uma data válida, não futura, no formato AAAA-MM-DD.";
  }

  return {
    valido: Object.keys(erros).length === 0,
    erros,
    dados: {
      nome,
      email,
      data_nascimento: dataNascimento
    }
  };
}

function validarId(valor) {
  if (!/^[1-9]\d*$/.test(valor)) {
    return null;
  }

  const id = Number(valor);

  if (!Number.isSafeInteger(id)) {
    return null;
  }

  return id;
}

module.exports = {
  validarUsuario,
  validarId
};
```

---

### Arquivo: `src/server.js`

```javascript
const express = require("express");
const { db, caminhoBanco } = require("./database");
const { validarUsuario, validarId } = require("./validacao");

const app = express();
const porta = Number(process.env.PORT) || 3000;

app.disable("x-powered-by");
app.use(express.json({ limit: "100kb" }));

const selecionarUsuarioPorId = db.prepare(`
  SELECT
    id,
    nome,
    email,
    data_nascimento,
    criado_em,
    atualizado_em
  FROM usuarios
  WHERE id = ?
`);

const listarUsuarios = db.prepare(`
  SELECT
    id,
    nome,
    email,
    data_nascimento,
    criado_em,
    atualizado_em
  FROM usuarios
  ORDER BY id ASC
`);

const inserirUsuario = db.prepare(`
  INSERT INTO usuarios (
    nome,
    email,
    data_nascimento
  )
  VALUES (
    @nome,
    @email,
    @data_nascimento
  )
`);

const atualizarUsuario = db.prepare(`
  UPDATE usuarios
  SET
    nome = @nome,
    email = @email,
    data_nascimento = @data_nascimento,
    atualizado_em = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
  WHERE id = @id
`);

const removerUsuario = db.prepare(`
  DELETE FROM usuarios
  WHERE id = ?
`);

function responderErro(res, status, codigo, mensagem, detalhes) {
  const resposta = {
    erro: {
      codigo,
      mensagem
    }
  };

  if (detalhes) {
    resposta.erro.detalhes = detalhes;
  }

  return res.status(status).json(resposta);
}

function exigirJson(req, res, next) {
  if (!req.is("application/json")) {
    return responderErro(
      res,
      415,
      "TIPO_DE_CONTEUDO_NAO_SUPORTADO",
      "O cabeçalho Content-Type deve ser application/json."
    );
  }

  return next();
}

function obterId(req, res) {
  const id = validarId(req.params.id);

  if (id === null) {
    responderErro(
      res,
      400,
      "ID_INVALIDO",
      "O ID deve ser um número inteiro positivo."
    );

    return null;
  }

  return id;
}

function emailDuplicado(erro) {
  return (
    erro &&
    (erro.code === "SQLITE_CONSTRAINT_UNIQUE" ||
      String(erro.message).includes("usuarios.email"))
  );
}

app.get("/health", (req, res) => {
  res.status(200).json({
    status: "ok"
  });
});

/*
 * Lista todos os usuários.
 * Para manter a tarefa simples, não foi implementada paginação.
 */
app.get("/usuarios", (req, res) => {
  const usuarios = listarUsuarios.all();

  res.status(200).json({
    dados: usuarios,
    total: usuarios.length
  });
});

app.get("/usuarios/:id", (req, res) => {
  const id = obterId(req, res);

  if (id === null) {
    return;
  }

  const usuario = selecionarUsuarioPorId.get(id);

  if (!usuario) {
    return responderErro(
      res,
      404,
      "USUARIO_NAO_ENCONTRADO",
      "Usuário não encontrado."
    );
  }

  return res.status(200).json(usuario);
});

app.post("/usuarios", exigirJson, (req, res, next) => {
  const validacao = validarUsuario(req.body);

  if (!validacao.valido) {
    return responderErro(
      res,
      422,
      "DADOS_INVALIDOS",
      "Os dados informados são inválidos.",
      validacao.erros
    );
  }

  try {
    const resultado = inserirUsuario.run(validacao.dados);
    const usuario = selecionarUsuarioPorId.get(resultado.lastInsertRowid);

    return res
      .status(201)
      .location(`/usuarios/${usuario.id}`)
      .json(usuario);
  } catch (erro) {
    if (emailDuplicado(erro)) {
      return responderErro(
        res,
        409,
        "EMAIL_JA_CADASTRADO",
        "Já existe um usuário cadastrado com este e-mail."
      );
    }

    return next(erro);
  }
});

/*
 * PUT representa a substituição completa dos dados editáveis.
 * Por isso, nome, email e data_nascimento são obrigatórios.
 */
app.put("/usuarios/:id", exigirJson, (req, res, next) => {
  const id = obterId(req, res);

  if (id === null) {
    return;
  }

  const validacao = validarUsuario(req.body);

  if (!validacao.valido) {
    return responderErro(
      res,
      422,
      "DADOS_INVALIDOS",
      "Os dados informados são inválidos.",
      validacao.erros
    );
  }

  if (!selecionarUsuarioPorId.get(id)) {
    return responderErro(
      res,
      404,
      "USUARIO_NAO_ENCONTRADO",
      "Usuário não encontrado."
    );
  }

  try {
    atualizarUsuario.run({
      id,
      ...validacao.dados
    });

    const usuarioAtualizado = selecionarUsuarioPorId.get(id);

    return res.status(200).json(usuarioAtualizado);
  } catch (erro) {
    if (emailDuplicado(erro)) {
      return responderErro(
        res,
        409,
        "EMAIL_JA_CADASTRADO",
        "Já existe um usuário cadastrado com este e-mail."
      );
    }

    return next(erro);
  }
});

app.delete("/usuarios/:id", (req, res) => {
  const id = obterId(req, res);

  if (id === null) {
    return;
  }

  const resultado = removerUsuario.run(id);

  if (resultado.changes === 0) {
    return responderErro(
      res,
      404,
      "USUARIO_NAO_ENCONTRADO",
      "Usuário não encontrado."
    );
  }

  /*
   * Uma remoção bem-sucedida retorna 204 e, conforme o padrão HTTP,
   * não possui corpo JSON.
   */
  return res.status(204).send();
});

app.use((req, res) => {
  return responderErro(
    res,
    404,
    "ROTA_NAO_ENCONTRADA",
    "A rota solicitada não existe."
  );
});

/*
 * Middleware centralizado de erros.
 * Trata separadamente JSON malformado e não expõe detalhes internos.
 */
app.use((erro, req, res, next) => {
  if (
    erro instanceof SyntaxError &&
    erro.status === 400 &&
    Object.prototype.hasOwnProperty.call(erro, "body")
  ) {
    return responderErro(
      res,
      400,
      "JSON_INVALIDO",
      "O corpo da requisição contém JSON inválido."
    );
  }

  console.error(erro);

  return responderErro(
    res,
    500,
    "ERRO_INTERNO",
    "Ocorreu um erro interno no servidor."
  );
});

const servidor = app.listen(porta, () => {
  console.log(`API disponível em http://localhost:${porta}`);
  console.log(`Banco SQLite: ${caminhoBanco}`);
});

let encerrando = false;

function encerrar(signal) {
  if (encerrando) {
    return;
  }

  encerrando = true;
  console.log(`\nSinal ${signal} recebido. Encerrando...`);

  servidor.close(() => {
    db.close();
    process.exit(0);
  });

  /*
   * Evita que o processo permaneça aberto indefinidamente caso existam
   * conexões HTTP que não sejam finalizadas.
   */
  setTimeout(() => {
    try {
      db.close();
    } catch {
      // O banco pode já estar fechado.
    }

    process.exit(1);
  }, 5000).unref();
}

process.on("SIGINT", () => encerrar("SIGINT"));
process.on("SIGTERM", () => encerrar("SIGTERM"));
```

---

### Arquivo: `README.md`

```markdown
# API REST de usuários

API REST em Node.js para cadastrar, listar, consultar, atualizar e remover
usuários. Os dados são persistidos em SQLite.

## Requisitos

- Node.js 20 ou superior
- npm

## Instalação

Na raiz do projeto, execute:

```bash
npm install
```

## Execução

```bash
npm start
```

A API estará disponível em:

```text
http://localhost:3000
```

O banco será criado automaticamente em:

```text
data/usuarios.db
```

## Desenvolvimento com reinicialização automática

```bash
npm run dev
```

## Variáveis de ambiente

### Porta HTTP

```bash
PORT=8080 npm start
```

### Caminho do banco

```bash
DATABASE_PATH=/tmp/usuarios.db npm start
```

Também é possível usar um banco em memória:

```bash
DATABASE_PATH=:memory: npm start
```

## Formato do usuário

```json
{
  "nome": "Maria da Silva",
  "email": "maria@example.com",
  "data_nascimento": "1990-05-20"
}
```

A data de nascimento deve usar o formato `AAAA-MM-DD` e não pode ser futura.

O e-mail é único e sua comparação não diferencia letras maiúsculas de
minúsculas.

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| GET | `/health` | Verifica se a API está disponível |
| POST | `/usuarios` | Cria um usuário |
| GET | `/usuarios` | Lista os usuários |
| GET | `/usuarios/:id` | Consulta um usuário |
| PUT | `/usuarios/:id` | Atualiza completamente um usuário |
| DELETE | `/usuarios/:id` | Remove um usuário |

## Exemplos

### Criar usuário

```bash
curl -i \
  -X POST http://localhost:3000/usuarios \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Maria da Silva",
    "email": "maria@example.com",
    "data_nascimento": "1990-05-20"
  }'
```

Resposta esperada: `201 Created`

```json
{
  "id": 1,
  "nome": "Maria da Silva",
  "email": "maria@example.com",
  "data_nascimento": "1990-05-20",
  "criado_em": "2026-08-31T12:00:00.000Z",
  "atualizado_em": "2026-08-31T12:00:00.000Z"
}
```

### Listar usuários

```bash
curl -i http://localhost:3000/usuarios
```

Resposta esperada: `200 OK`

```json
{
  "dados": [
    {
      "id": 1,
      "nome": "Maria da Silva",
      "email": "maria@example.com",
      "data_nascimento": "1990-05-20",
      "criado_em": "2026-08-31T12:00:00.000Z",
      "atualizado_em": "2026-08-31T12:00:00.000Z"
    }
  ],
  "total": 1
}
```

### Consultar usuário

```bash
curl -i http://localhost:3000/usuarios/1
```

### Atualizar usuário

O `PUT` exige todos os campos editáveis.

```bash
curl -i \
  -X PUT http://localhost:3000/usuarios/1 \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Maria Souza",
    "email": "maria.souza@example.com",
    "data_nascimento": "1990-05-20"
  }'
```

Resposta esperada: `200 OK`

### Remover usuário

```bash
curl -i \
  -X DELETE http://localhost:3000/usuarios/1
```

Resposta esperada: `204 No Content`

## Principais códigos HTTP

- `200 OK`: consulta ou atualização realizada.
- `201 Created`: usuário criado.
- `204 No Content`: usuário removido.
- `400 Bad Request`: ID ou JSON inválido.
- `404 Not Found`: usuário ou rota não encontrada.
- `409 Conflict`: e-mail já cadastrado.
- `415 Unsupported Media Type`: corpo enviado sem `application/json`.
- `422 Unprocessable Entity`: dados de usuário inválidos.
- `500 Internal Server Error`: erro interno inesperado.
```