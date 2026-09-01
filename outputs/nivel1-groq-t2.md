<!--
nivel: 1 - CRUD com persistencia em banco
provider: groq
model: openai/gpt-oss-120b
tentativa: 2
temperature: 0.2
timestamp: 2026-08-27T18:58:19.433Z
metadata: {"model":"openai/gpt-oss-120b","usage":{"queue_time":0.362122689,"prompt_tokens":286,"prompt_time":0.064666894,"completion_tokens":3620,"completion_time":7.515415522,"total_tokens":3906,"total_time":7.580082416,"completion_tokens_details":{"reasoning_tokens":31}},"finish_reason":"stop"}
-->

## Prompt enviado
```
Voce e um(a) engenheiro(a) de software responsavel por implementar o sistema
descrito abaixo. Gere o codigo completo, pronto para rodar, incluindo
instrucoes de execucao (como instalar dependencias e como rodar).

TAREFA:
Crie uma aplicacao de linha de comando (CLI) que permita cadastrar, listar,
atualizar e remover usuarios (nome, e-mail, data de nascimento), persistindo
os dados em um banco de dados relacional (SQLite), incluindo o script de
criacao do schema. Valide o formato do e-mail e impeca duplicidade de
e-mail. Trate erros de entrada de forma amigavel.

RESTRICOES:
- Linguagem: Node.js (JavaScript).
- Nao use frameworks alem dos estritamente necessarios para a tarefa.
- Nao peca esclarecimentos: assuma decisoes razoaveis e documente-as em comentarios.
- Entregue todos os arquivos necessarios, indicando o nome do arquivo antes de cada bloco de codigo.
```

## Resposta do modelo

**Resumo**  
Esta resposta entrega um pequeno projeto **Node.js** (JavaScript) que implementa uma aplicação de linha de comando (CLI) para **cadastrar, listar, atualizar e remover usuários**.  
Os usuários são armazenados em **SQLite**; o schema é criado automaticamente na primeira execução.  
O e‑mail é validado e não pode ser duplicado. Todos os erros de entrada são tratados de forma amigável.

---

## Estrutura de arquivos

```
user-cli/
│
├─ package.json
├─ index.js               # ponto de entrada da CLI
├─ db.js                  # camada de acesso ao SQLite
├─ utils.js               # funções auxiliares (validação, formatação)
├─ schema.sql             # script de criação do schema (usado por db.js)
└─ README.md              # instruções de instalação e uso
```

---

## 1️⃣ `package.json`

```json
{
  "name": "user-cli",
  "version": "1.0.0",
  "description": "CLI simples para gerenciamento de usuários (SQLite)",
  "main": "index.js",
  "type": "commonjs",
  "bin": {
    "user-cli": "./index.js"
  },
  "scripts": {
    "start": "node index.js"
  },
  "author": "Seu Nome",
  "license": "MIT",
  "dependencies": {
    "better-sqlite3": "^9.1.1",
    "commander": "^12.0.0",
    "inquirer": "^9.2.12",
    "validator": "^13.11.0"
  }
}
```

*Dependências*  

| Pacote | Por quê? |
|--------|----------|
| `better-sqlite3` | SQLite síncrono, simples de usar e sem callbacks. |
| `commander` | Parsing de argumentos da linha de comando. |
| `inquirer` | Perguntas interativas (para criar/atualizar usuários). |
| `validator` | Validação de e‑mail e data. |

---

## 2️⃣ `schema.sql`

```sql
-- schema.sql
-- Cria a tabela "users" caso ela ainda não exista.

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    birthdate TEXT NOT NULL   -- armazenado como ISO string (YYYY-MM-DD)
);
```

---

## 3️⃣ `db.js`

```js
// db.js
// Responsável por abrir a conexão SQLite e expor funções de CRUD.

const Database = require('better-sqlite3');
const fs = require('fs');
const path = require('path');

// Caminho do arquivo de BD (cria na pasta do projeto)
const DB_PATH = path.join(__dirname, 'users.db');

// Garantir que o arquivo exista (SQLite cria se necessário)
const db = new Database(DB_PATH);

// Carregar e executar o script de criação do schema
const schemaPath = path.join(__dirname, 'schema.sql');
const schema = fs.readFileSync(schemaPath, 'utf-8');
db.exec(schema);

/**
 * Insere um novo usuário.
 * @param {Object} user - { name, email, birthdate }
 * @throws se email já existir
 */
function createUser(user) {
  const stmt = db.prepare(`
    INSERT INTO users (name, email, birthdate)
    VALUES (@name, @email, @birthdate)
  `);
  stmt.run(user);
}

/**
 * Lista todos os usuários.
 * @returns {Array}
 */
function listUsers() {
  const stmt = db.prepare(`SELECT id, name, email, birthdate FROM users ORDER BY id`);
  return stmt.all();
}

/**
 * Busca um usuário por ID.
 * @param {number} id
 * @returns {Object|undefined}
 */
function getUserById(id) {
  const stmt = db.prepare(`SELECT * FROM users WHERE id = ?`);
  return stmt.get(id);
}

/**
 * Atualiza um usuário existente.
 * @param {number} id
 * @param {Object} fields - campos a atualizar (name,email,birthdate)
 */
function updateUser(id, fields) {
  const setClauses = [];
  const params = { id };

  if (fields.name !== undefined) {
    setClauses.push('name = @name');
    params.name = fields.name;
  }
  if (fields.email !== undefined) {
    setClauses.push('email = @email');
    params.email = fields.email;
  }
  if (fields.birthdate !== undefined) {
    setClauses.push('birthdate = @birthdate');
    params.birthdate = fields.birthdate;
  }

  if (setClauses.length === 0) return; // nada a fazer

  const stmt = db.prepare(`
    UPDATE users SET ${setClauses.join(', ')} WHERE id = @id
  `);
  stmt.run(params);
}

/**
 * Remove um usuário por ID.
 * @param {number} id
 */
function deleteUser(id) {
  const stmt = db.prepare(`DELETE FROM users WHERE id = ?`);
  stmt.run(id);
}

/**
 * Verifica se já existe um usuário com aquele e‑mail (exceto opcionalmente um ID).
 * @param {string} email
 * @param {number|null} excludeId
 * @returns {boolean}
 */
function emailExists(email, excludeId = null) {
  const stmt = excludeId
    ? db.prepare(`SELECT 1 FROM users WHERE email = ? AND id != ?`)
    : db.prepare(`SELECT 1 FROM users WHERE email = ?`);
  const row = excludeId ? stmt.get(email, excludeId) : stmt.get(email);
  return !!row;
}

module.exports = {
  createUser,
  listUsers,
  getUserById,
  updateUser,
  deleteUser,
  emailExists
};
```

---

## 4️⃣ `utils.js`

```js
// utils.js
// Funções auxiliares: validação de e‑mail, data, formatação.

const validator = require('validator');

/**
 * Valida e normaliza um e‑mail.
 * @param {string} email
 * @throws {Error} se inválido
 * @returns {string} email em minúsculas
 */
function validateEmail(email) {
  const normalized = email.trim().toLowerCase();
  if (!validator.isEmail(normalized)) {
    throw new Error('E‑mail inválido. Use o formato nome@exemplo.com');
  }
  return normalized;
}

/**
 * Valida a data de nascimento (deve ser YYYY-MM-DD e data real).
 * @param {string} dateStr
 * @throws {Error}
 * @returns {string} data no formato ISO (YYYY-MM-DD)
 */
function validateBirthdate(dateStr) {
  const trimmed = dateStr.trim();
  if (!validator.isISO8601(trimmed, { strict: true })) {
    throw new Error('Data de nascimento inválida. Use o formato YYYY-MM-DD');
  }
  // Opcional: garantir que a data não seja futura
  const today = new Date().toISOString().slice(0, 10);
  if (trimmed > today) {
    throw new Error('Data de nascimento não pode ser no futuro');
  }
  return trimmed;
}

/**
 * Formata um objeto usuário para exibição amigável.
 */
function formatUser(user) {
  return `ID: ${user.id}
Nome: ${user.name}
E‑mail: ${user.email}
Nascimento: ${user.birthdate}`;
}

module.exports = {
  validateEmail,
  validateBirthdate,
  formatUser
};
```

---

## 5️⃣ `index.js` (CLI)

```js
#!/usr/bin/env node
// index.js
// Entrada da aplicação CLI usando commander + inquirer.

const { program } = require('commander');
const inquirer = require('inquirer');
const db = require('./db');
const utils = require('./utils');

// Definir a versão da CLI
program.version('1.0.0').description('Gerenciador de usuários (SQLite)');

// ---------- COMANDO: create ----------
program
  .command('add')
  .alias('c')
  .description('Cadastrar um novo usuário')
  .action(async () => {
    try {
      const answers = await inquirer.prompt([
        {
          type: 'input',
          name: 'name',
          message: 'Nome:',
          validate: (v) => (v.trim() ? true : 'Nome não pode ficar vazio')
        },
        {
          type: 'input',
          name: 'email',
          message: 'E‑mail:',
          validate: (v) => {
            try {
              utils.validateEmail(v);
              if (db.emailExists(v)) {
                return 'Este e‑mail já está cadastrado';
              }
              return true;
            } catch (e) {
              return e.message;
            }
          }
        },
        {
          type: 'input',
          name: 'birthdate',
          message: 'Data de nascimento (YYYY-MM-DD):',
          validate: (v) => {
            try {
              utils.validateBirthdate(v);
              return true;
            } catch (e) {
              return e.message;
            }
          }
        }
      ]);

      const user = {
        name: answers.name.trim(),
        email: utils.validateEmail(answers.email),
        birthdate: utils.validateBirthdate(answers.birthdate)
      };

      db.createUser(user);
      console.log('\n✅ Usuário cadastrado com sucesso!');
    } catch (err) {
      console.error('\n❌ Erro ao cadastrar usuário:', err.message);
    }
  });

// ---------- COMANDO: list ----------
program
  .command('list')
  .alias('l')
  .description('Listar todos os usuários')
  .action(() => {
    try {
      const users = db.listUsers();
      if (users.length === 0) {
        console.log('Nenhum usuário encontrado.');
        return;
      }
      console.log('\n=== Usuários cadastrados ===\n');
      users.forEach((u) => {
        console.log(utils.formatUser(u));
        console.log('---------------------------');
      });
    } catch (err) {
      console.error('Erro ao listar usuários:', err.message);
    }
  });

// ---------- COMANDO: update ----------
program
  .command('update <id>')
  .alias('u')
  .description('Atualizar dados de um usuário existente')
  .action(async (id) => {
    const numericId = parseInt(id, 10);
    if (isNaN(numericId)) {
      console.error('ID inválido.');
      return;
    }

    const user = db.getUserById(numericId);
    if (!user) {
      console.error(`Usuário com ID ${numericId} não encontrado.`);
      return;
    }

    try {
      const answers = await inquirer.prompt([
        {
          type: 'input',
          name: 'name',
          message: `Nome [${user.name}]:`,
          default: user.name,
          filter: (v) => v.trim()
        },
        {
          type: 'input',
          name: 'email',
          message: `E‑mail [${user.email}]:`,
          default: user.email,
          validate: (v) => {
            try {
              const norm = utils.validateEmail(v);
              if (db.emailExists(norm, numericId)) {
                return 'Este e‑mail já está cadastrado por outro usuário';
              }
              return true;
            } catch (e) {
              return e.message;
            }
          },
          filter: (v) => v.trim()
        },
        {
          type: 'input',
          name: 'birthdate',
          message: `Data de nascimento (YYYY-MM-DD) [${user.birthdate}]:`,
          default: user.birthdate,
          validate: (v) => {
            try {
              utils.validateBirthdate(v);
              return true;
            } catch (e) {
              return e.message;
            }
          },
          filter: (v) => v.trim()
        }
      ]);

      const updated = {
        name: answers.name,
        email: utils.validateEmail(answers.email),
        birthdate: utils.validateBirthdate(answers.birthdate)
      };

      db.updateUser(numericId, updated);
      console.log('\n✅ Usuário atualizado com sucesso!');
    } catch (err) {
      console.error('\n❌ Erro ao atualizar usuário:', err.message);
    }
  });

// ---------- COMANDO: delete ----------
program
  .command('delete <id>')
  .alias('d')
  .description('Remover um usuário')
  .action(async (id) => {
    const numericId = parseInt(id, 10);
    if (isNaN(numericId)) {
      console.error('ID inválido.');
      return;
    }

    const user = db.getUserById(numericId);
    if (!user) {
      console.error(`Usuário com ID ${numericId} não encontrado.`);
      return;
    }

    const { confirm } = await inquirer.prompt([
      {
        type: 'confirm',
        name: 'confirm',
        message: `Tem certeza que deseja remover o usuário "${user.name}"?`,
        default: false
      }
    ]);

    if (confirm) {
      db.deleteUser(numericId);
      console.log('✅ Usuário removido.');
    } else {
      console.log('Operação cancelada.');
    }
  });

// ---------- COMANDO: help ----------
program
  .command('help')
  .description('Exibe ajuda')
  .action(() => {
    program.outputHelp();
  });

program.parse(process.argv);

// Se nenhum comando for passado, exibe ajuda.
if (!process.argv.slice(2).length) {
  program.outputHelp();
}
```

> **Observação:** O shebang (`#!/usr/bin/env node`) permite que o script seja executado diretamente após tornar o arquivo executável (`chmod +x index.js`) ou ao instalar via `npm link`.

---

## 6️⃣ `README.md`

```markdown
# User CLI

Aplicação de linha de comando (CLI) para gerenciar usuários (nome, e‑mail, data de nascimento) usando SQLite.

## Requisitos

- Node.js (versão 14 ou superior)
- npm (vem com o Node)

## Instalação

```bash
# 1️⃣ Clone o repositório (ou copie os arquivos)
git clone <url-do-repositorio>
cd user-cli

# 2️⃣ Instale as dependências
npm install

# 3️⃣ Torne o script principal executável (opcional)
chmod +x index.js
```

## Uso

Existem quatro comandos principais:

| Comando | Descrição |
|---------|-----------|
| `node index.js add` (ou `npm start -- add`) | Cadastrar novo usuário |
| `node index.js list` | Listar todos os usuários |
| `node index.js update <id>` | Atualizar usuário existente |
| `node index.js delete <id>` | Remover usuário |

### Exemplos

```bash
# Cadastrar
node index.js add

# Listar
node index.js list

# Atualizar (ex.: ID = 3)
node index.js update 3

# Remover (ex.: ID = 2)
node index.js delete 2
```

### Instalação global (opcional)

Para usar o comando `user-cli` de qualquer lugar:

```bash
npm link   # cria um link global para o bin definido em package.json
user-cli add
```

## Arquivos importantes

- `db.js` – camada de acesso ao SQLite (CRUD).
- `utils.js` – validações de e‑mail e data.
- `schema.sql` – script que cria a tabela `users`.
- `users.db` – arquivo SQLite gerado na primeira execução.

## Tratamento de erros

- E‑mail inválido ou já cadastrado → mensagem amigável.
- Data de nascimento fora do formato `YYYY-MM-DD` ou futura → aviso.
- ID inexistente ao atualizar/remover → notifica o usuário.

## Licença

MIT © 2026 Seu Nome
```

---

## 📦 Como executar tudo de uma vez (passo a passo)

```bash
# 1. Crie uma pasta e copie os arquivos acima dentro dela
mkdir user-cli && cd user-cli
# (coloque cada bloco de código nos arquivos correspondentes)

# 2. Instale as dependências
npm install

# 3. Rode a CLI
node index.js add          # cadastra
node index.js list         # lista
node index.js update 1     # atualiza usuário com ID 1
node index.js delete 1     # remove usuário com ID 1
```

Pronto! 🎉  
A aplicação está completa, pronta para ser instalada e usada. Boa codificação!