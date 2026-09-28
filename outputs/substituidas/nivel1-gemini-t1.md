<!--
nivel: 1 - CRUD com persistencia em banco
provider: gemini
model: gemini-pro-latest
tentativa: 1
temperature: 0.2
timestamp: 2026-08-18T17:01:01.516Z
metadata: {"model":"gemini-pro-latest","usage":{"promptTokenCount":235,"candidatesTokenCount":2200,"totalTokenCount":4216,"promptTokensDetails":[{"modality":"TEXT","tokenCount":235}],"thoughtsTokenCount":1781,"serviceTier":"standard"},"finish_reason":"STOP"}
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

Aqui está a solução completa para o sistema solicitado. 

Para manter a aplicação simples, robusta e sem frameworks desnecessários, optei por utilizar a biblioteca `better-sqlite3` para a comunicação com o banco de dados. Ela é síncrona, rápida e ideal para scripts CLI em Node.js. Para a interface de linha de comando, utilizei o módulo nativo `readline` do Node.js, encapsulado em Promises para permitir o uso de `async/await`, criando um menu interativo amigável.

### Instruções de Execução

1. Certifique-se de ter o **Node.js** instalado em sua máquina (versão 14 ou superior).
2. Crie uma pasta para o projeto e salve os 4 arquivos abaixo dentro dela.
3. Abra o terminal na pasta do projeto e instale a dependência do banco de dados executando:
   ```bash
   npm install
   ```
4. Para iniciar a aplicação, execute:
   ```bash
   npm start
   ```

---

### Arquivos do Projeto

**`package.json`**
Este arquivo gerencia as dependências e os scripts de execução do projeto.
```json
{
  "name": "cli-user-manager",
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

**`schema.sql`**
Script de criação do banco de dados. A restrição `UNIQUE` no e-mail garante a não duplicidade a nível de banco de dados.
```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    birthdate TEXT NOT NULL
);
```

**`db.js`**
Módulo responsável por conectar ao SQLite e inicializar o banco de dados usando o script SQL.
```javascript
const Database = require('better-sqlite3');
const fs = require('fs');
const path = require('path');

// Conecta ao banco de dados (cria o arquivo database.sqlite se não existir)
const db = new Database('database.sqlite');

// Lê o arquivo schema.sql e executa para garantir que a tabela existe
const schemaPath = path.join(__dirname, 'schema.sql');
const schema = fs.readFileSync(schemaPath, 'utf8');
db.exec(schema);

module.exports = db;
```

**`index.js`**
Arquivo principal contendo a lógica da CLI, validações e operações CRUD.
```javascript
const readline = require('readline');
const db = require('./db');

// Configuração do readline para interface interativa no terminal
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

// Encapsula o rl.question em uma Promise para usar async/await
const question = (query) => new Promise((resolve) => rl.question(query, resolve));

// Funções de Validação
const isValidEmail = (email) => {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
};

const isValidDate = (date) => {
    // Valida formato YYYY-MM-DD
    const regex = /^\d{4}-\d{2}-\d{2}$/;
    return regex.test(date);
};

// Operações CRUD
async function createUser() {
    console.log('\n--- Cadastrar Novo Usuário ---');
    const name = await question('Nome: ');
    
    const email = await question('E-mail: ');
    if (!isValidEmail(email)) {
        console.log('❌ Erro: Formato de e-mail inválido.');
        return;
    }

    const birthdate = await question('Data de Nascimento (YYYY-MM-DD): ');
    if (!isValidDate(birthdate)) {
        console.log('❌ Erro: Formato de data inválido. Use YYYY-MM-DD.');
        return;
    }

    try {
        const stmt = db.prepare('INSERT INTO users (name, email, birthdate) VALUES (?, ?, ?)');
        stmt.run(name, email, birthdate);
        console.log('✅ Usuário cadastrado com sucesso!');
    } catch (error) {
        if (error.code === 'SQLITE_CONSTRAINT_UNIQUE') {
            console.log('❌ Erro: Este e-mail já está cadastrado no sistema.');
        } else {
            console.log('❌ Erro ao cadastrar usuário:', error.message);
        }
    }
}

function listUsers() {
    console.log('\n--- Lista de Usuários ---');
    try {
        const stmt = db.prepare('SELECT * FROM users');
        const users = stmt.all();
        
        if (users.length === 0) {
            console.log('Nenhum usuário cadastrado.');
        } else {
            console.table(users);
        }
    } catch (error) {
        console.log('❌ Erro ao listar usuários:', error.message);
    }
}

async function updateUser() {
    console.log('\n--- Atualizar Usuário ---');
    const idStr = await question('ID do usuário que deseja atualizar: ');
    const id = parseInt(idStr, 10);

    if (isNaN(id)) {
        console.log('❌ Erro: ID inválido.');
        return;
    }

    // Verifica se o usuário existe
    const user = db.prepare('SELECT * FROM users WHERE id = ?').get(id);
    if (!user) {
        console.log('❌ Erro: Usuário não encontrado.');
        return;
    }

    console.log(`Deixe em branco para manter o valor atual.`);
    
    let name = await question(`Nome (${user.name}): `);
    name = name.trim() === '' ? user.name : name;

    let email = await question(`E-mail (${user.email}): `);
    email = email.trim() === '' ? user.email : email;
    if (email !== user.email && !isValidEmail(email)) {
        console.log('❌ Erro: Formato de e-mail inválido.');
        return;
    }

    let birthdate = await question(`Data de Nascimento (${user.birthdate}): `);
    birthdate = birthdate.trim() === '' ? user.birthdate : birthdate;
    if (birthdate !== user.birthdate && !isValidDate(birthdate)) {
        console.log('❌ Erro: Formato de data inválido. Use YYYY-MM-DD.');
        return;
    }

    try {
        const stmt = db.prepare('UPDATE users SET name = ?, email = ?, birthdate = ? WHERE id = ?');
        stmt.run(name, email, birthdate, id);
        console.log('✅ Usuário atualizado com sucesso!');
    } catch (error) {
        if (error.code === 'SQLITE_CONSTRAINT_UNIQUE') {
            console.log('❌ Erro: Este e-mail já está sendo usado por outro usuário.');
        } else {
            console.log('❌ Erro ao atualizar usuário:', error.message);
        }
    }
}

async function deleteUser() {
    console.log('\n--- Remover Usuário ---');
    const idStr = await question('ID do usuário que deseja remover: ');
    const id = parseInt(idStr, 10);

    if (isNaN(id)) {
        console.log('❌ Erro: ID inválido.');
        return;
    }

    try {
        const stmt = db.prepare('DELETE FROM users WHERE id = ?');
        const info = stmt.run(id);
        
        if (info.changes > 0) {
            console.log('✅ Usuário removido com sucesso!');
        } else {
            console.log('❌ Erro: Usuário não encontrado.');
        }
    } catch (error) {
        console.log('❌ Erro ao remover usuário:', error.message);
    }
}

// Menu Principal
async function mainMenu() {
    let running = true;
    while (running) {
        console.log('\n=========================');
        console.log(' GERENCIADOR DE USUÁRIOS ');
        console.log('=========================');
        console.log('1. Cadastrar usuário');
        console.log('2. Listar usuários');
        console.log('3. Atualizar usuário');
        console.log('4. Remover usuário');
        console.log('0. Sair');
        console.log('=========================');
        
        const option = await question('Escolha uma opção: ');

        switch (option.trim()) {
            case '1':
                await createUser();
                break;
            case '2':
                listUsers();
                break;
            case '3':
                await updateUser();
                break;
            case '4':
                await deleteUser();
                break;
            case '0':
                console.log('Saindo...');
                running = false;
                break;
            default:
                console.log('❌ Opção inválida. Tente novamente.');
        }
    }
    rl.close();
}

// Inicia a aplicação
mainMenu();
```