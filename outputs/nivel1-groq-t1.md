<!--
nivel: 1 - CRUD com persistencia em banco
provider: groq
model: openai/gpt-oss-120b
tentativa: 1
temperature: 0.2
timestamp: 2026-08-27T18:57:13.440Z
metadata: {"model":"openai/gpt-oss-120b","usage":{"queue_time":0.24382606,"prompt_tokens":286,"prompt_time":0.013032126,"completion_tokens":3409,"completion_time":7.071381296,"total_tokens":3695,"total_time":7.084413422,"completion_tokens_details":{"reasoning_tokens":57}},"finish_reason":"stop"}
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

**Resumo da solução**  
* Uma aplicação CLI em Node.js que permite **criar**, **listar**, **atualizar** e **remover** usuários.  
* Cada usuário tem **nome**, **e‑mail** e **data de nascimento**.  
* Os dados são armazenados em **SQLite** (arquivo `users.db`).  
* O script `schema.sql` cria a tabela `users` com constraint `UNIQUE(email)`.  
* O e‑mail é validado com expressão regular; se inválido ou já existir, a aplicação mostra mensagem amigável.  
* Todas as dependências são mínimas: `sqlite3` (driver oficial) e `commander` (para parsing de argumentos).  

---

## 1. Estrutura de arquivos

```
user-cli/
│
├─ package.json
├─ index.js            # ponto de entrada da CLI
├─ db.js               # módulo de acesso ao SQLite
├─ schema.sql          # script de criação do schema
└─ README.md           # instruções de uso
```

---

## 2. Código fonte

### `package.json`
```json
{
  "name": "user-cli",
  "version": "1.0.0",
  "description": "CLI para cadastrar, listar, atualizar e remover usuários usando SQLite",
  "main": "index.js",
  "bin": {
    "usercli": "./index.js"
  },
  "scripts": {
    "setup": "node db.js init"
  },
  "author": "Seu Nome",
  "license": "MIT",
  "dependencies": {
    "commander": "^11.0.0",
    "sqlite3": "^5.1.7"
  }
}
```

### `schema.sql`
```sql
-- Criação da tabela users
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    birthdate TEXT NOT NULL   -- armazenado como ISO string (YYYY-MM-DD)
);
```

### `db.js`
```js
#!/usr/bin/env node
/**
 * Módulo de acesso ao SQLite.
 * Exporta funções async para CRUD de usuários e para inicializar o banco.
 */

const path = require('path');
const fs = require('fs');
const sqlite3 = require('sqlite3').verbose();

const DB_FILE = path.join(__dirname, 'users.db');
let db;

/**
 * Abre a conexão (ou cria) com o banco.
 */
function open() {
    if (!db) {
        db = new sqlite3.Database(DB_FILE);
    }
}

/**
 * Executa o script de criação do schema (schema.sql).
 * Usado na primeira execução (`npm run setup` ou `node db.js init`).
 */
function initSchema() {
    open();
    const sql = fs.readFileSync(path.join(__dirname, 'schema.sql'), 'utf8');
    return new Promise((resolve, reject) => {
        db.exec(sql, err => {
            if (err) reject(err);
            else resolve();
        });
    });
}

/**
 * Insere um novo usuário.
 * @returns {Promise<number>} id do usuário inserido
 */
function createUser({ name, email, birthdate }) {
    open();
    const sql = `INSERT INTO users (name, email, birthdate) VALUES (?, ?, ?)`;
    return new Promise((resolve, reject) => {
        db.run(sql, [name, email, birthdate], function (err) {
            if (err) reject(err);
            else resolve(this.lastID);
        });
    });
}

/**
 * Lista todos os usuários.
 * @returns {Promise<Array>}
 */
function listUsers() {
    open();
    const sql = `SELECT id, name, email, birthdate FROM users ORDER BY id`;
    return new Promise((resolve, reject) => {
        db.all(sql, [], (err, rows) => {
            if (err) reject(err);
            else resolve(rows);
        });
    });
}

/**
 * Atualiza um usuário existente (por id).
 * @returns {Promise<void>}
 */
function updateUser(id, { name, email, birthdate }) {
    open();
    const sql = `UPDATE users SET name = ?, email = ?, birthdate = ? WHERE id = ?`;
    return new Promise((resolve, reject) => {
        db.run(sql, [name, email, birthdate, id], function (err) {
            if (err) reject(err);
            else if (this.changes === 0) reject(new Error('Usuário não encontrado'));
            else resolve();
        });
    });
}

/**
 * Remove um usuário (por id).
 * @returns {Promise<void>}
 */
function deleteUser(id) {
    open();
    const sql = `DELETE FROM users WHERE id = ?`;
    return new Promise((resolve, reject) => {
        db.run(sql, [id], function (err) {
            if (err) reject(err);
            else if (this.changes === 0) reject(new Error('Usuário não encontrado'));
            else resolve();
        });
    });
}

/**
 * Encerra a conexão (usado ao final de scripts de manutenção).
 */
function close() {
    if (db) db.close();
}

/**
 * Quando o script for chamado diretamente, aceita o comando "init"
 * para criar o schema.
 */
if (require.main === module) {
    const [, , cmd] = process.argv;
    if (cmd === 'init') {
        initSchema()
            .then(() => {
                console.log('Banco de dados e schema criados com sucesso.');
                close();
            })
            .catch(err => {
                console.error('Erro ao criar schema:', err.message);
                process.exit(1);
            });
    } else {
        console.error('Uso: node db.js init');
        process.exit(1);
    }
}

module.exports = {
    initSchema,
    createUser,
    listUsers,
    updateUser,
    deleteUser,
    close
};
```

### `index.js`
```js
#!/usr/bin/env node
/**
 * CLI principal.
 * Comandos suportados:
 *   add      - Cadastrar novo usuário
 *   list     - Listar todos os usuários
 *   update   - Atualizar usuário existente
 *   delete   - Remover usuário
 *
 * Execução típica:
 *   $ usercli add --name "Ana Silva" --email ana@example.com --birthdate 1990-05-12
 *   $ usercli list
 *   $ usercli update 3 --name "Ana S." --email ana.s@example.com
 *   $ usercli delete 3
 */

const { program } = require('commander');
const db = require('./db');
const readline = require('readline');

// Regex simples para validação de e‑mail
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// Função auxiliar para ler input via stdin (usada ao pedir confirmação)
function askYesNo(question) {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });
    return new Promise(resolve => {
        rl.question(`${question} (y/n): `, answer => {
            rl.close();
            resolve(/^y(es)?$/i.test(answer.trim()));
        });
    });
}

// ---------- Comando: add ----------
program
    .command('add')
    .description('Cadastrar um novo usuário')
    .requiredOption('-n, --name <name>', 'Nome completo')
    .requiredOption('-e, --email <email>', 'Endereço de e‑mail')
    .requiredOption('-b, --birthdate <date>', 'Data de nascimento (YYYY-MM-DD)')
    .action(async opts => {
        const { name, email, birthdate } = opts;

        // Validação básica
        if (!EMAIL_REGEX.test(email)) {
            console.error('✖ E‑mail inválido.');
            process.exit(1);
        }
        if (!/^\d{4}-\d{2}-\d{2}$/.test(birthdate)) {
            console.error('✖ Data de nascimento deve estar no formato YYYY-MM-DD.');
            process.exit(1);
        }

        try {
            await db.createUser({ name, email, birthdate });
            console.log('✔ Usuário cadastrado com sucesso.');
        } catch (err) {
            if (err.message.includes('UNIQUE constraint failed')) {
                console.error('✖ Já existe um usuário com esse e‑mail.');
            } else {
                console.error('✖ Erro ao cadastrar usuário:', err.message);
            }
            process.exit(1);
        }
    });

// ---------- Comando: list ----------
program
    .command('list')
    .description('Listar todos os usuários')
    .action(async () => {
        try {
            const users = await db.listUsers();
            if (users.length === 0) {
                console.log('Nenhum usuário cadastrado.');
                return;
            }
            console.table(users);
        } catch (err) {
            console.error('✖ Erro ao listar usuários:', err.message);
            process.exit(1);
        }
    });

// ---------- Comando: update ----------
program
    .command('update <id>')
    .description('Atualizar dados de um usuário')
    .option('-n, --name <name>', 'Novo nome')
    .option('-e, --email <email>', 'Novo e‑mail')
    .option('-b, --birthdate <date>', 'Nova data de nascimento (YYYY-MM-DD)')
    .action(async (id, opts) => {
        const updates = {};
        if (opts.name) updates.name = opts.name;
        if (opts.email) {
            if (!EMAIL_REGEX.test(opts.email)) {
                console.error('✖ E‑mail inválido.');
                process.exit(1);
            }
            updates.email = opts.email;
        }
        if (opts.birthdate) {
            if (!/^\d{4}-\d{2}-\d{2}$/.test(opts.birthdate)) {
                console.error('✖ Data de nascimento deve estar no formato YYYY-MM-DD.');
                process.exit(1);
            }
            updates.birthdate = opts.birthdate;
        }

        if (Object.keys(updates).length === 0) {
            console.error('✖ Nenhum campo a ser atualizado foi informado.');
            process.exit(1);
        }

        // Busca usuário atual para preencher campos não informados
        try {
            const users = await db.listUsers();
            const user = users.find(u => u.id === Number(id));
            if (!user) {
                console.error('✖ Usuário não encontrado.');
                process.exit(1);
            }
            const data = {
                name: updates.name ?? user.name,
                email: updates.email ?? user.email,
                birthdate: updates.birthdate ?? user.birthdate
            };
            await db.updateUser(id, data);
            console.log('✔ Usuário atualizado com sucesso.');
        } catch (err) {
            if (err.message.includes('UNIQUE constraint failed')) {
                console.error('✖ Já existe outro usuário com esse e‑mail.');
            } else {
                console.error('✖ Erro ao atualizar usuário:', err.message);
            }
            process.exit(1);
        }
    });

// ---------- Comando: delete ----------
program
    .command('delete <id>')
    .description('Remover um usuário')
    .action(async id => {
        const confirm = await askYesNo(`Tem certeza que deseja remover o usuário com id ${id}?`);
        if (!confirm) {
            console.log('Operação cancelada.');
            return;
        }
        try {
            await db.deleteUser(id);
            console.log('✔ Usuário removido com sucesso.');
        } catch (err) {
            console.error('✖ Erro ao remover usuário:', err.message);
            process.exit(1);
        }
    });

// ---------- Configurações gerais ----------
program
    .name('usercli')
    .description('Gerenciador de usuários (CRUD) via linha de comando')
    .version('1.0.0');

program.parse(process.argv);

// Se nenhum comando foi informado, exibe ajuda
if (!process.argv.slice(2).length) {
    program.outputHelp();
}
```

### `README.md`
```markdown
# User CLI

Aplicação de linha de comando para **cadastrar**, **listar**, **atualizar** e **remover** usuários,
com persistência em SQLite.

## Requisitos

- Node.js (v14 ou superior)
- npm (ou yarn)

## Instalação

```bash
# Clone ou copie o projeto para sua máquina
git clone <repo-url> user-cli
cd user-cli

# Instala as dependências
npm install

# Cria o banco de dados e a tabela (executa apenas na primeira vez)
npm run setup
```

## Uso

O binário é exposto como `usercli`. Você pode chamar diretamente com `npx` ou
instalar globalmente:

```bash
# Executar via npx (não instala globalmente)
npx usercli <comando> [opções]

# OU instalar globalmente
npm link   # cria o comando `usercli` disponível no PATH
usercli <comando> [opções]
```

### Comandos

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `add`   | Cadastrar novo usuário | `usercli add -n "Ana Silva" -e ana@example.com -b 1990-05-12` |
| `list`  | Listar todos os usuários | `usercli list` |
| `update <id>` | Atualizar usuário (pode mudar nome, e‑mail e/ou data) | `usercli update 3 -n "Ana S." -e ana.s@example.com` |
| `delete <id>` | Remover usuário (pede confirmação) | `usercli delete 3` |

### Validações

- **E‑mail**: verificado por expressão regular simples; se inválido, a operação é abortada.
- **E‑mail duplicado**: a tabela tem `UNIQUE(email)`. Caso tente inserir/atualizar para um e‑mail já usado, será exibida mensagem de erro amigável.
- **Data de nascimento**: aceita apenas o formato `YYYY-MM-DD`.

## Estrutura do banco

Arquivo: `users.db` (gerado na raiz do projeto)

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    birthdate TEXT NOT NULL
);
```

## Desenvolvimento

Caso queira modificar ou melhorar a aplicação:

```bash
# Recriar o schema (apaga dados existentes!)
rm users.db
npm run setup
```

## Licença

MIT – sinta‑se livre para usar, modificar e distribuir.

```

---

## 3. Como executar tudo de uma vez (passo a passo)

```bash
# 1️⃣ Clone / copie o diretório
git clone https://github.com/SEU_USUARIO/user-cli.git
cd user-cli

# 2️⃣ Instala as dependências
npm install

# 3️⃣ Cria o banco e a tabela
npm run setup      # ou: node db.js init

# 4️⃣ Usa a CLI
node index.js add -n "João da Silva" -e joao@example.com -b 1985-03-20
node index.js list
node index.js update 1 -n "João S." -e joao.s@example.com
node index.js delete 1
```

Pronto! Você tem uma aplicação CLI completa, pronta para rodar, sem frameworks
pesados, usando apenas as dependências necessárias e com tratamento amigável
de erros e validações. Boa codificação!