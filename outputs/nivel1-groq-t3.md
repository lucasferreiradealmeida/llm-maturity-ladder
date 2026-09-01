<!--
nivel: 1 - CRUD com persistencia em banco
provider: groq
model: openai/gpt-oss-120b
tentativa: 3
temperature: 0.2
timestamp: 2026-08-31T09:06:54.890Z
metadata: {"model":"openai/gpt-oss-120b","usage":{"queue_time":0.21146342,"prompt_tokens":286,"prompt_time":0.01435936,"completion_tokens":3561,"completion_time":7.415840703,"total_tokens":3847,"total_time":7.430200063,"completion_tokens_details":{"reasoning_tokens":25}},"finish_reason":"stop"}
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

**⚙️ Projeto:** `user‑cli` – Gerenciador de usuários em linha de comando  
**Linguagem:** Node.js (JavaScript)  
**Banco:** SQLite (arquivo local)  

---  

## 1️⃣ Estrutura de pastas / arquivos

```
user-cli/
│
├─ package.json
├─ package-lock.json   (gerado após `npm install`)
│
├─ src/
│   ├─ index.js        # ponto de entrada da CLI
│   ├─ db.js           # camada de acesso ao SQLite
│   ├─ validators.js   # funções de validação (e‑mail, data)
│   └─ commands/
│        ├─ add.js
│        ├─ list.js
│        ├─ update.js
│        └─ delete.js
│
└─ schema.sql          # script de criação do schema (executado pelo código)
```

---  

## 2️⃣ Como executar

### Pré‑requisitos
* Node.js >= 14 (versão LTS) instalado
* npm (vem com o Node)

### Passos

```bash
# 1️⃣ Clone ou copie a pasta user-cli para sua máquina
cd user-cli

# 2️⃣ Instale as dependências
npm install

# 3️⃣ Torne o comando disponível (opcional, mas recomendado)
npm link   # cria o comando `user-cli` globalmente

# 4️⃣ Use a CLI
#   - Ajuda geral
user-cli --help

#   - Cadastrar usuário
user-cli add --name "Ana Silva" --email ana@example.com --birth "1990-05-12"

#   - Listar usuários
user-cli list

#   - Atualizar usuário (por ID)
user-cli update 3 --name "Ana S. Oliveira" --email ana.oliveira@example.com

#   - Remover usuário (por ID)
user-cli delete 3
```

> **Obs.:** Se não usar `npm link`, execute a CLI com `node src/index.js …`.

---  

## 3️⃣ Código completo

---  

### `package.json`

```json
{
  "name": "user-cli",
  "version": "1.0.0",
  "description": "Aplicação de linha de comando para cadastrar, listar, atualizar e remover usuários usando SQLite.",
  "main": "src/index.js",
  "bin": {
    "user-cli": "./src/index.js"
  },
  "scripts": {
    "start": "node src/index.js"
  },
  "author": "Engenheiro(a) de Software",
  "license": "MIT",
  "dependencies": {
    "better-sqlite3": "^9.4.3",
    "commander": "^11.1.0",
    "chalk": "^5.3.0",
    "email-validator": "^2.0.4",
    "dayjs": "^1.11.10"
  }
}
```

---  

### `schema.sql`

```sql
-- Cria a tabela de usuários, se ainda não existir
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    birth_date TEXT NOT NULL   -- armazenado como ISO string (YYYY-MM-DD)
);
```

---  

### `src/db.js`

```js
// src/db.js
// Responsável por abrir a conexão SQLite e prover funções de CRUD.
// Usa better-sqlite3 (síncrono) por ser simples e não precisar de async/await.

const Database = require('better-sqlite3');
const path = require('path');
const fs = require('fs');

const DB_FILE = path.resolve(__dirname, '..', 'users.db');
const SCHEMA_FILE = path.resolve(__dirname, '..', 'schema.sql');

// Garante que o arquivo de banco exista e cria a tabela caso ainda não exista
function initDatabase() {
    const db = new Database(DB_FILE);
    const schema = fs.readFileSync(SCHEMA_FILE, 'utf-8');
    db.exec(schema);
    return db;
}

const db = initDatabase();

// ---------- CRUD ----------

function addUser({ name, email, birthDate }) {
    const stmt = db.prepare(`
        INSERT INTO users (name, email, birth_date)
        VALUES (?, ?, ?)
    `);
    const info = stmt.run(name, email, birthDate);
    return info.lastInsertRowid;
}

function getAllUsers() {
    const stmt = db.prepare(`SELECT id, name, email, birth_date FROM users ORDER BY id`);
    return stmt.all();
}

function getUserById(id) {
    const stmt = db.prepare(`SELECT id, name, email, birth_date FROM users WHERE id = ?`);
    return stmt.get(id);
}

function getUserByEmail(email) {
    const stmt = db.prepare(`SELECT id FROM users WHERE email = ?`);
    return stmt.get(email);
}

function updateUser(id, { name, email, birthDate }) {
    // Constrói dinamicamente a query apenas com os campos informados
    const fields = [];
    const values = [];

    if (name !== undefined) {
        fields.push('name = ?');
        values.push(name);
    }
    if (email !== undefined) {
        fields.push('email = ?');
        values.push(email);
    }
    if (birthDate !== undefined) {
        fields.push('birth_date = ?');
        values.push(birthDate);
    }

    if (fields.length === 0) return 0; // nada a atualizar

    const stmt = db.prepare(`
        UPDATE users SET ${fields.join(', ')} WHERE id = ?
    `);
    values.push(id);
    const info = stmt.run(...values);
    return info.changes; // 1 se alterou, 0 se não encontrou
}

function deleteUser(id) {
    const stmt = db.prepare(`DELETE FROM users WHERE id = ?`);
    const info = stmt.run(id);
    return info.changes;
}

// Exporta as funções
module.exports = {
    addUser,
    getAllUsers,
    getUserById,
    getUserByEmail,
    updateUser,
    deleteUser,
};
```

---  

### `src/validators.js`

```js
// src/validators.js
// Funções auxiliares de validação de e‑mail e data de nascimento.

const emailValidator = require('email-validator');
const dayjs = require('dayjs');

// Valida e‑mail usando a biblioteca email-validator
function isValidEmail(email) {
    return emailValidator.validate(email);
}

// Verifica se a string representa uma data válida no formato YYYY-MM-DD
function isValidDate(dateStr) {
    return dayjs(dateStr, 'YYYY-MM-DD', true).isValid();
}

// Converte data para o mesmo formato usado no DB (ISO sem horário)
function formatDate(dateStr) {
    return dayjs(dateStr).format('YYYY-MM-DD');
}

module.exports = {
    isValidEmail,
    isValidDate,
    formatDate,
};
```

---  

### `src/commands/add.js`

```js
// src/commands/add.js
const chalk = require('chalk');
const { addUser, getUserByEmail } = require('../db');
const { isValidEmail, isValidDate, formatDate } = require('../validators');

function runAdd(options) {
    const { name, email, birth } = options;

    // ---- Validação amigável ----
    if (!name) {
        console.error(chalk.red('❌ O parâmetro --name é obrigatório.'));
        process.exit(1);
    }
    if (!email) {
        console.error(chalk.red('❌ O parâmetro --email é obrigatório.'));
        process.exit(1);
    }
    if (!birth) {
        console.error(chalk.red('❌ O parâmetro --birth é obrigatório (YYYY-MM-DD).'));
        process.exit(1);
    }
    if (!isValidEmail(email)) {
        console.error(chalk.red('❌ E‑mail inválido.'));
        process.exit(1);
    }
    if (!isValidDate(birth)) {
        console.error(chalk.red('❌ Data de nascimento inválida. Use o formato YYYY-MM-DD.'));
        process.exit(1);
    }

    // ---- Checa duplicidade de e‑mail ----
    const existing = getUserByEmail(email);
    if (existing) {
        console.error(chalk.red(`❌ Já existe um usuário com o e‑mail "${email}".`));
        process.exit(1);
    }

    const birthDate = formatDate(birth);
    const id = addUser({ name, email, birthDate });

    console.log(chalk.green(`✅ Usuário criado com ID ${id}.`));
}

module.exports = runAdd;
```

---  

### `src/commands/list.js`

```js
// src/commands/list.js
const chalk = require('chalk');
const { getAllUsers } = require('../db');

function runList() {
    const users = getAllUsers();

    if (users.length === 0) {
        console.log(chalk.yellow('⚠️  Nenhum usuário cadastrado.'));
        return;
    }

    console.log(chalk.blue('ID | Nome               | E‑mail                | Nascimento'));
    console.log(chalk.blue('---+--------------------+----------------------+------------'));

    users.forEach(u => {
        const line = `${String(u.id).padEnd(2)} | ${u.name.padEnd(18)} | ${u.email.padEnd(20)} | ${u.birth_date}`;
        console.log(line);
    });
}

module.exports = runList;
```

---  

### `src/commands/update.js`

```js
// src/commands/update.js
const chalk = require('chalk');
const { getUserById, getUserByEmail, updateUser } = require('../db');
const { isValidEmail, isValidDate, formatDate } = require('../validators');

function runUpdate(id, options) {
    const user = getUserById(id);
    if (!user) {
        console.error(chalk.red(`❌ Usuário com ID ${id} não encontrado.`));
        process.exit(1);
    }

    const { name, email, birth } = options;

    // Se nada foi passado, avisa
    if (!name && !email && !birth) {
        console.error(chalk.yellow('⚠️  Nenhum campo para atualização foi informado.'));
        process.exit(1);
    }

    // Valida cada campo individualmente
    if (email && !isValidEmail(email)) {
        console.error(chalk.red('❌ E‑mail inválido.'));
        process.exit(1);
    }
    if (birth && !isValidDate(birth)) {
        console.error(chalk.red('❌ Data de nascimento inválida. Use o formato YYYY-MM-DD.'));
        process.exit(1);
    }

    // Se o e‑mail será alterado, verifica duplicidade
    if (email) {
        const existing = getUserByEmail(email);
        if (existing && existing.id !== Number(id)) {
            console.error(chalk.red(`❌ Já existe outro usuário com o e‑mail "${email}".`));
            process.exit(1);
        }
    }

    const updateData = {
        name,
        email,
        birthDate: birth ? formatDate(birth) : undefined,
    };

    const changed = updateUser(id, updateData);
    if (changed) {
        console.log(chalk.green(`✅ Usuário ${id} atualizado com sucesso.`));
    } else {
        console.log(chalk.yellow(`⚠️  Nenhuma alteração foi feita no usuário ${id}.`));
    }
}

module.exports = runUpdate;
```

---  

### `src/commands/delete.js`

```js
// src/commands/delete.js
const chalk = require('chalk');
const { getUserById, deleteUser } = require('../db');

function runDelete(id) {
    const user = getUserById(id);
    if (!user) {
        console.error(chalk.red(`❌ Usuário com ID ${id} não encontrado.`));
        process.exit(1);
    }

    const removed = deleteUser(id);
    if (removed) {
        console.log(chalk.green(`✅ Usuário ${id} removido.`));
    } else {
        console.log(chalk.yellow(`⚠️  Não foi possível remover o usuário ${id}.`));
    }
}

module.exports = runDelete;
```

---  

### `src/index.js`

```js
#!/usr/bin/env node
// src/index.js
// Entrada principal da CLI. Usa commander para parsing de comandos e opções.

const { program } = require('commander');
const chalk = require('chalk');

const addCmd = require('./commands/add');
const listCmd = require('./commands/list');
const updateCmd = require('./commands/update');
const deleteCmd = require('./commands/delete');

// Configurações globais
program
    .name('user-cli')
    .description('Gerenciador de usuários (CRUD) usando SQLite')
    .version('1.0.0');

// ---------- COMANDO ADD ----------
program
    .command('add')
    .description('Cadastrar um novo usuário')
    .requiredOption('-n, --name <name>', 'Nome completo')
    .requiredOption('-e, --email <email>', 'E‑mail (único)')
    .requiredOption('-b, --birth <date>', 'Data de nascimento (YYYY-MM-DD)')
    .action(addCmd);

// ---------- COMANDO LIST ----------
program
    .command('list')
    .description('Listar todos os usuários cadastrados')
    .action(listCmd);

// ---------- COMANDO UPDATE ----------
program
    .command('update <id>')
    .description('Atualizar dados de um usuário (por ID)')
    .option('-n, --name <name>', 'Novo nome')
    .option('-e, --email <email>', 'Novo e‑mail')
    .option('-b, --birth <date>', 'Nova data de nascimento (YYYY-MM-DD)')
    .action(updateCmd);

// ---------- COMANDO DELETE ----------
program
    .command('delete <id>')
    .description('Remover um usuário (por ID)')
    .action(deleteCmd);

// Tratar comando desconhecido
program.on('command:*', () => {
    console.error(chalk.red('❌ Comando desconhecido.'));
    program.help({ error: true });
});

program.parse(process.argv);

// Se nenhum sub‑comando foi passado, exibe a ajuda
if (!process.argv.slice(2).length) {
    program.outputHelp();
}
```

---  

## 4️⃣ Comentários sobre decisões de design

* **`better-sqlite3`** – driver síncrono, sem callbacks nem promessas, perfeito para scripts CLI simples.
* **`commander`** – pequeno e suficiente para parsing de sub‑comandos e opções.
* **`chalk`** – para mensagens coloridas e amigáveis.
* **Validação de e‑mail** – biblioteca `email-validator` (leve e confiável).
* **Validação de data** – `dayjs` com parsing estrito (`YYYY-MM-DD`), evitando datas como `2023-02-30`.
* **Unicidade de e‑mail** – feita tanto na camada de banco (`UNIQUE`) quanto verificada antes de inserir/atualizar para mensagens mais claras.
* **Persistência** – banco `users.db` criado na raiz do projeto; schema executado na primeira inicialização.
* **Mensagens de erro** – terminam o processo com `process.exit(1)` após imprimir o motivo, facilitando uso em scripts.

---  

## 5️⃣ Como testar rapidamente

```bash
# Limpar base (apagar o arquivo) para começar do zero
rm -f users.db

# Adicionar dois usuários
user-cli add -n "João da Silva" -e joao@example.com -b 1985-03-22
user-cli add -n "Maria Oliveira" -e maria@exemplo.com -b 1992-11-05

# Listar
user-cli list

# Tentar inserir e‑mail duplicado (deve falhar)
user-cli add -n "Outro" -e joao@example.com -b 2000-01-01

# Atualizar nome do primeiro usuário
user-cli update 1 -n "João S. da Silva"

# Remover o segundo usuário
user-cli delete 2

# Listar novamente
user-cli list
```

Tudo pronto! 🎉  

---  

**Boa codificação!**   (Se precisar de mais alguma coisa, é só chamar.)