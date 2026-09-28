<!--
nivel: 1 - CRUD com persistencia em banco
provider: gemini
model: gemini-pro-latest
tentativa: 2
temperature: 0.2
timestamp: 2026-08-18T17:01:52.507Z
metadata: {"model":"gemini-pro-latest","usage":{"promptTokenCount":235,"candidatesTokenCount":1961,"totalTokenCount":3673,"promptTokensDetails":[{"modality":"TEXT","tokenCount":235}],"thoughtsTokenCount":1477,"serviceTier":"standard"},"finish_reason":"STOP"}
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

Aqui está a implementação completa do sistema solicitado. 

### Decisões de Design Assumidas:
1. **Interface CLI:** Optei por usar argumentos de linha de comando (`process.argv`) em vez de um prompt interativo. Isso torna a ferramenta rápida para uso em scripts e automações.
2. **Biblioteca de Banco de Dados:** Utilizei o `better-sqlite3`. Ele é síncrono, o que simplifica muito o código para scripts CLI, evitando a complexidade de callbacks ou Promises desnecessárias para esta escala de aplicação.
3. **Identificador Único:** Para as operações de atualização e remoção, assumi o uso do `ID` gerado pelo banco de dados, pois é a forma mais segura de identificar um registro (já que nomes podem se repetir e e-mails podem ser alterados).
4. **Formato de Data:** Assumi o formato `YYYY-MM-DD` (padrão ISO) para facilitar a ordenação e validação.

---

### Instruções de Execução

**1. Pré-requisitos:**
* Ter o [Node.js](https://nodejs.org/) instalado na sua máquina (versão 14 ou superior).

**2. Instalação:**
Crie uma pasta para o projeto, salve os arquivos abaixo dentro dela e, no terminal, execute:
```bash
npm install
```

**3. Como usar:**
* **Adicionar usuário:**
  `node index.js add "João Silva" "joao@email.com" "1990-05-20"`
* **Listar usuários:**
  `node index.js list`
* **Atualizar usuário (requer o ID listado no comando anterior):**
  `node index.js update 1 "João da Silva" "joao.silva@email.com" "1990-05-20"`
* **Remover usuário:**
  `node index.js remove 1`

---

### Arquivos do Projeto

`package.json`
```json
{
  "name": "cli-users-crud",
  "version": "1.0.0",
  "description": "CLI para gerenciamento de usuários com SQLite",
  "main": "index.js",
  "scripts": {
    "start": "node index.js"
  },
  "dependencies": {
    "better-sqlite3": "^9.4.3"
  }
}
```

`db.js`
```javascript
const Database = require('better-sqlite3');
const path = require('path');

// Conecta ao banco de dados (cria o arquivo se não existir)
const dbPath = path.join(__dirname, 'database.sqlite');
const db = new Database(dbPath);

// Script de criação do Schema
// A restrição UNIQUE no email garante que não haverá duplicidade no nível do banco
const initDb = () => {
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      email TEXT UNIQUE NOT NULL,
      birthdate TEXT NOT NULL
    )
  `);
};

initDb();

module.exports = db;
```

`index.js`
```javascript
const db = require('./db');

// Captura os argumentos passados na linha de comando
const [,, command, ...args] = process.argv;

// Funções de Validação
const isValidEmail = (email) => {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
};

const isValidDate = (date) => {
  const regex = /^\d{4}-\d{2}-\d{2}$/;
  return regex.test(date);
};

// Controladores (CRUD)
const addUser = (name, email, birthdate) => {
  if (!name || !email || !birthdate) {
    return console.error('Erro: Para adicionar, informe <nome> <email> <data_nascimento YYYY-MM-DD>.');
  }
  if (!isValidEmail(email)) {
    return console.error('Erro: O formato do e-mail é inválido.');
  }
  if (!isValidDate(birthdate)) {
    return console.error('Erro: A data de nascimento deve estar no formato YYYY-MM-DD.');
  }

  try {
    const stmt = db.prepare('INSERT INTO users (name, email, birthdate) VALUES (?, ?, ?)');
    const info = stmt.run(name, email, birthdate);
    console.log(`✅ Usuário cadastrado com sucesso! (ID: ${info.lastInsertRowid})`);
  } catch (error) {
    if (error.code === 'SQLITE_CONSTRAINT_UNIQUE') {
      console.error('Erro: Este e-mail já está cadastrado no sistema.');
    } else {
      console.error('Erro ao cadastrar usuário:', error.message);
    }
  }
};

const listUsers = () => {
  try {
    const stmt = db.prepare('SELECT * FROM users');
    const users = stmt.all();
    
    if (users.length === 0) {
      console.log('Nenhum usuário cadastrado.');
    } else {
      console.table(users);
    }
  } catch (error) {
    console.error('Erro ao listar usuários:', error.message);
  }
};

const updateUser = (id, name, email, birthdate) => {
  if (!id || !name || !email || !birthdate) {
    return console.error('Erro: Para atualizar, informe <id> <nome> <email> <data_nascimento YYYY-MM-DD>.');
  }
  if (!isValidEmail(email)) {
    return console.error('Erro: O formato do e-mail é inválido.');
  }
  if (!isValidDate(birthdate)) {
    return console.error('Erro: A data de nascimento deve estar no formato YYYY-MM-DD.');
  }

  try {
    const stmt = db.prepare('UPDATE users SET name = ?, email = ?, birthdate = ? WHERE id = ?');
    const info = stmt.run(name, email, birthdate, id);
    
    if (info.changes > 0) {
      console.log(`✅ Usuário ID ${id} atualizado com sucesso!`);
    } else {
      console.error(`Erro: Usuário com ID ${id} não encontrado.`);
    }
  } catch (error) {
    if (error.code === 'SQLITE_CONSTRAINT_UNIQUE') {
      console.error('Erro: Este e-mail já está sendo usado por outro usuário.');
    } else {
      console.error('Erro ao atualizar usuário:', error.message);
    }
  }
};

const removeUser = (id) => {
  if (!id) {
    return console.error('Erro: Para remover, informe o <id> do usuário.');
  }

  try {
    const stmt = db.prepare('DELETE FROM users WHERE id = ?');
    const info = stmt.run(id);
    
    if (info.changes > 0) {
      console.log(`✅ Usuário ID ${id} removido com sucesso!`);
    } else {
      console.error(`Erro: Usuário com ID ${id} não encontrado.`);
    }
  } catch (error) {
    console.error('Erro ao remover usuário:', error.message);
  }
};

// Roteador de Comandos
switch (command) {
  case 'add':
    addUser(args[0], args[1], args[2]);
    break;
  case 'list':
    listUsers();
    break;
  case 'update':
    updateUser(args[0], args[1], args[2], args[3]);
    break;
  case 'remove':
    removeUser(args[0]);
    break;
  default:
    console.log(`
CLI de Gerenciamento de Usuários
Uso: node index.js <comando> [argumentos]

Comandos disponíveis:
  add <nome> <email> <data_nascimento>   Cadastra um novo usuário (Data em YYYY-MM-DD)
  list                                   Lista todos os usuários
  update <id> <nome> <email> <data>      Atualiza os dados de um usuário existente
  remove <id>                            Remove um usuário pelo ID
    `);
    break;
}
```