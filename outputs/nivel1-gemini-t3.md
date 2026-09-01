<!--
nivel: 1 - CRUD com persistencia em banco
provider: gemini
model: gemini-3.1-pro-preview
tentativa: 3
temperature: 0.2
timestamp: 2026-08-31T08:45:54.975Z
metadata: {"model":"gemini-3.1-pro-preview","usage":{"promptTokenCount":235,"candidatesTokenCount":2244,"totalTokenCount":3993,"promptTokensDetails":[{"modality":"TEXT","tokenCount":235}],"thoughtsTokenCount":1514,"serviceTier":"standard"},"finish_reason":"STOP"}
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

Para manter a aplicação estritamente dentro do necessário e evitar frameworks excessivos, decidi utilizar o módulo nativo `readline` do Node.js para a interface de linha de comando (CLI) interativa. A única dependência externa utilizada é o `sqlite3`, que é o driver necessário para conectar e operar o banco de dados SQLite.

### Instruções de Execução

1. Certifique-se de ter o **Node.js** instalado em sua máquina.
2. Crie um diretório para o projeto e salve os três arquivos abaixo dentro dele.
3. Abra o terminal no diretório do projeto e execute o comando abaixo para instalar a dependência do banco de dados:
   ```bash
   npm install
   ```
4. Para iniciar a aplicação, execute:
   ```bash
   node index.js
   ```

---

### Arquivos do Projeto

`package.json`
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
    "sqlite3": "^5.1.6"
  }
}
```

`database.js`
```javascript
// database.js
// Responsável pela conexão com o banco de dados e operações CRUD.
// Decisão: Utilizar Promises para envolver as chamadas de callback do sqlite3,
// permitindo o uso de async/await no arquivo principal para um código mais limpo.

const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const dbPath = path.resolve(__dirname, 'database.sqlite');
const db = new sqlite3.Database(dbPath);

// Funções auxiliares para transformar callbacks em Promises
const run = (query, params = []) => {
    return new Promise((resolve, reject) => {
        db.run(query, params, function (err) {
            if (err) reject(err);
            else resolve(this);
        });
    });
};

const all = (query, params = []) => {
    return new Promise((resolve, reject) => {
        db.all(query, params, (err, rows) => {
            if (err) reject(err);
            else resolve(rows);
        });
    });
};

// Script de criação do Schema
const initDB = async () => {
    const schema = `
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            birthdate TEXT NOT NULL
        );
    `;
    await run(schema);
};

const createUser = async (name, email, birthdate) => {
    try {
        await run(`INSERT INTO users (name, email, birthdate) VALUES (?, ?, ?)`, [name, email, birthdate]);
    } catch (error) {
        if (error.code === 'SQLITE_CONSTRAINT') {
            throw new Error('Este e-mail já está cadastrado no sistema.');
        }
        throw error;
    }
};

const getUsers = async () => {
    return await all(`SELECT * FROM users`);
};

const updateUser = async (id, name, email, birthdate) => {
    try {
        const result = await run(
            `UPDATE users SET name = ?, email = ?, birthdate = ? WHERE id = ?`,
            [name, email, birthdate, id]
        );
        if (result.changes === 0) {
            throw new Error('Usuário não encontrado.');
        }
    } catch (error) {
        if (error.code === 'SQLITE_CONSTRAINT') {
            throw new Error('Este e-mail já está sendo utilizado por outro usuário.');
        }
        throw error;
    }
};

const deleteUser = async (id) => {
    const result = await run(`DELETE FROM users WHERE id = ?`, [id]);
    if (result.changes === 0) {
        throw new Error('Usuário não encontrado.');
    }
};

module.exports = {
    initDB,
    createUser,
    getUsers,
    updateUser,
    deleteUser
};
```

`index.js`
```javascript
// index.js
// Ponto de entrada da aplicação. Gerencia a interface de linha de comando (CLI),
// validações de entrada e chamadas ao banco de dados.

const readline = require('readline');
const db = require('./database');

// Configuração da interface de leitura nativa do Node.js
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

// Transforma a função question em Promise para uso com async/await
const askQuestion = (query) => new Promise(resolve => rl.question(query, resolve));

// Validação de formato de e-mail via Regex
const isValidEmail = (email) => {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
};

// Validação de data (Formato YYYY-MM-DD)
const isValidDate = (date) => {
    const regex = /^\d{4}-\d{2}-\d{2}$/;
    return regex.test(date);
};

const showMenu = () => {
    console.log('\n=== GERENCIADOR DE USUÁRIOS ===');
    console.log('1. Cadastrar usuário');
    console.log('2. Listar usuários');
    console.log('3. Atualizar usuário');
    console.log('4. Remover usuário');
    console.log('5. Sair');
    console.log('===============================');
};

const handleCreate = async () => {
    console.log('\n--- Novo Cadastro ---');
    const name = await askQuestion('Nome: ');
    
    const email = await askQuestion('E-mail: ');
    if (!isValidEmail(email)) {
        console.log('❌ Erro: Formato de e-mail inválido.');
        return;
    }

    const birthdate = await askQuestion('Data de Nascimento (YYYY-MM-DD): ');
    if (!isValidDate(birthdate)) {
        console.log('❌ Erro: Formato de data inválido. Use YYYY-MM-DD.');
        return;
    }

    try {
        await db.createUser(name, email, birthdate);
        console.log('✅ Usuário cadastrado com sucesso!');
    } catch (error) {
        console.log(`❌ Erro ao cadastrar: ${error.message}`);
    }
};

const handleList = async () => {
    console.log('\n--- Lista de Usuários ---');
    try {
        const users = await db.getUsers();
        if (users.length === 0) {
            console.log('Nenhum usuário cadastrado.');
        } else {
            console.table(users);
        }
    } catch (error) {
        console.log(`❌ Erro ao buscar usuários: ${error.message}`);
    }
};

const handleUpdate = async () => {
    console.log('\n--- Atualizar Usuário ---');
    const id = await askQuestion('ID do usuário que deseja atualizar: ');
    
    const name = await askQuestion('Novo Nome: ');
    
    const email = await askQuestion('Novo E-mail: ');
    if (!isValidEmail(email)) {
        console.log('❌ Erro: Formato de e-mail inválido.');
        return;
    }

    const birthdate = await askQuestion('Nova Data de Nascimento (YYYY-MM-DD): ');
    if (!isValidDate(birthdate)) {
        console.log('❌ Erro: Formato de data inválido. Use YYYY-MM-DD.');
        return;
    }

    try {
        await db.updateUser(id, name, email, birthdate);
        console.log('✅ Usuário atualizado com sucesso!');
    } catch (error) {
        console.log(`❌ Erro ao atualizar: ${error.message}`);
    }
};

const handleDelete = async () => {
    console.log('\n--- Remover Usuário ---');
    const id = await askQuestion('ID do usuário que deseja remover: ');
    
    try {
        await db.deleteUser(id);
        console.log('✅ Usuário removido com sucesso!');
    } catch (error) {
        console.log(`❌ Erro ao remover: ${error.message}`);
    }
};

const main = async () => {
    try {
        await db.initDB();
        
        let running = true;
        while (running) {
            showMenu();
            const option = await askQuestion('Escolha uma opção: ');
            
            switch (option.trim()) {
                case '1':
                    await handleCreate();
                    break;
                case '2':
                    await handleList();
                    break;
                case '3':
                    await handleUpdate();
                    break;
                case '4':
                    await handleDelete();
                    break;
                case '5':
                    console.log('Saindo...');
                    running = false;
                    break;
                default:
                    console.log('❌ Opção inválida. Tente novamente.');
            }
        }
    } catch (error) {
        console.error('Erro fatal na aplicação:', error);
    } finally {
        rl.close();
        process.exit(0);
    }
};

// Inicia a aplicação
main();
```