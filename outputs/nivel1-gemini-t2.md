<!--
nivel: 1 - CRUD com persistencia em banco
provider: gemini
model: gemini-3.1-pro-preview
modelo_resolvido: gemini-3.1-pro-preview
tentativa: 2
temperature: 0.2
timestamp: 2026-09-28T18:32:20.449Z
metadata: {"model":"gemini-3.1-pro-preview","modelVersion":"gemini-3.1-pro-preview","responseId":"tLK6ar_MJrnUz7IPl7fw8Q0","usage":{"promptTokenCount":235,"candidatesTokenCount":2344,"totalTokenCount":3931,"promptTokensDetails":[{"modality":"TEXT","tokenCount":235}],"thoughtsTokenCount":1352,"serviceTier":"standard"},"finish_reason":"STOP","parametros":{"maxOutputTokens":16000,"temperature":0.2,"thinkingConfig":{"thinkingBudget":2048}}}
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

Para manter a aplicação leve e aderir à restrição de não usar frameworks desnecessários, utilizei apenas o módulo nativo `readline` do Node.js para a interface de linha de comando e a biblioteca `sqlite3` para a comunicação com o banco de dados. O schema do banco de dados é criado automaticamente na primeira execução.

### Instruções de Execução

1. Certifique-se de ter o **Node.js** instalado em sua máquina (versão 14 ou superior recomendada).
2. Crie um diretório para o projeto e salve os dois arquivos abaixo (`package.json` e `index.js`) dentro dele.
3. Abra o terminal no diretório do projeto e instale a dependência do SQLite executando:
   ```bash
   npm install
   ```
4. Para iniciar a aplicação, execute:
   ```bash
   npm start
   ```

---

### Arquivo: `package.json`
Este arquivo gerencia as dependências e scripts do projeto.

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
    "sqlite3": "^5.1.6"
  }
}
```

---

### Arquivo: `index.js`
Este é o código-fonte principal da aplicação. Ele contém a inicialização do banco de dados, o schema, as validações e a lógica da interface de linha de comando.

```javascript
const sqlite3 = require('sqlite3').verbose();
const readline = require('readline');

// ==========================================
// CONFIGURAÇÃO DO BANCO DE DADOS E SCHEMA
// ==========================================
// Assumindo a decisão de usar um arquivo local para persistência.
const db = new sqlite3.Database('./database.sqlite', (err) => {
    if (err) {
        console.error('Erro ao conectar ao banco de dados:', err.message);
        process.exit(1);
    }
});

// Criação do Schema
const initDB = () => {
    return new Promise((resolve, reject) => {
        const schema = `
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                birthdate TEXT NOT NULL
            )
        `;
        db.run(schema, (err) => {
            if (err) reject(err);
            else resolve();
        });
    });
};

// ==========================================
// UTILITÁRIOS E VALIDAÇÕES
// ==========================================
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

// Promisify do readline para usar async/await
const askQuestion = (query) => {
    return new Promise(resolve => rl.question(query, resolve));
};

const isValidEmail = (email) => {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
};

const isValidDate = (date) => {
    // Validação simples de formato YYYY-MM-DD
    const regex = /^\d{4}-\d{2}-\d{2}$/;
    return regex.test(date);
};

// Wrappers em Promise para operações do SQLite
const runQuery = (query, params = []) => {
    return new Promise((resolve, reject) => {
        db.run(query, params, function (err) {
            if (err) reject(err);
            else resolve(this);
        });
    });
};

const getQuery = (query, params = []) => {
    return new Promise((resolve, reject) => {
        db.all(query, params, (err, rows) => {
            if (err) reject(err);
            else resolve(rows);
        });
    });
};

// ==========================================
// OPERAÇÕES CRUD
// ==========================================

const createUser = async () => {
    console.log('\n--- Cadastrar Novo Usuário ---');
    const name = await askQuestion('Nome: ');
    if (!name.trim()) return console.log('Erro: O nome não pode ser vazio.');

    const email = await askQuestion('E-mail: ');
    if (!isValidEmail(email)) return console.log('Erro: Formato de e-mail inválido.');

    const birthdate = await askQuestion('Data de Nascimento (YYYY-MM-DD): ');
    if (!isValidDate(birthdate)) return console.log('Erro: Formato de data inválido. Use YYYY-MM-DD.');

    try {
        await runQuery(`INSERT INTO users (name, email, birthdate) VALUES (?, ?, ?)`, [name, email, birthdate]);
        console.log('✅ Usuário cadastrado com sucesso!');
    } catch (error) {
        if (error.code === 'SQLITE_CONSTRAINT') {
            console.log('❌ Erro: Este e-mail já está cadastrado no sistema.');
        } else {
            console.log('❌ Erro ao cadastrar usuário:', error.message);
        }
    }
};

const listUsers = async () => {
    console.log('\n--- Lista de Usuários ---');
    try {
        const users = await getQuery(`SELECT * FROM users`);
        if (users.length === 0) {
            console.log('Nenhum usuário cadastrado.');
        } else {
            console.table(users);
        }
    } catch (error) {
        console.log('❌ Erro ao listar usuários:', error.message);
    }
};

const updateUser = async () => {
    console.log('\n--- Atualizar Usuário ---');
    const idStr = await askQuestion('ID do usuário que deseja atualizar: ');
    const id = parseInt(idStr);

    if (isNaN(id)) return console.log('Erro: ID inválido.');

    try {
        const users = await getQuery(`SELECT * FROM users WHERE id = ?`, [id]);
        if (users.length === 0) return console.log('❌ Erro: Usuário não encontrado.');

        const user = users[0];
        console.log('(Deixe em branco para manter o valor atual)');
        
        let name = await askQuestion(`Nome [${user.name}]: `);
        name = name.trim() || user.name;

        let email = await askQuestion(`E-mail [${user.email}]: `);
        email = email.trim() || user.email;
        if (email !== user.email && !isValidEmail(email)) {
            return console.log('Erro: Formato de e-mail inválido.');
        }

        let birthdate = await askQuestion(`Data de Nascimento [${user.birthdate}]: `);
        birthdate = birthdate.trim() || user.birthdate;
        if (birthdate !== user.birthdate && !isValidDate(birthdate)) {
            return console.log('Erro: Formato de data inválido. Use YYYY-MM-DD.');
        }

        await runQuery(`UPDATE users SET name = ?, email = ?, birthdate = ? WHERE id = ?`, [name, email, birthdate, id]);
        console.log('✅ Usuário atualizado com sucesso!');
    } catch (error) {
        if (error.code === 'SQLITE_CONSTRAINT') {
            console.log('❌ Erro: O novo e-mail informado já está em uso por outro usuário.');
        } else {
            console.log('❌ Erro ao atualizar usuário:', error.message);
        }
    }
};

const deleteUser = async () => {
    console.log('\n--- Remover Usuário ---');
    const idStr = await askQuestion('ID do usuário que deseja remover: ');
    const id = parseInt(idStr);

    if (isNaN(id)) return console.log('Erro: ID inválido.');

    try {
        const result = await runQuery(`DELETE FROM users WHERE id = ?`, [id]);
        if (result.changes === 0) {
            console.log('❌ Erro: Usuário não encontrado.');
        } else {
            console.log('✅ Usuário removido com sucesso!');
        }
    } catch (error) {
        console.log('❌ Erro ao remover usuário:', error.message);
    }
};

// ==========================================
// MENU PRINCIPAL
// ==========================================
const showMenu = async () => {
    console.log('\n=========================');
    console.log(' GERENCIADOR DE USUÁRIOS');
    console.log('=========================');
    console.log('1. Cadastrar Usuário');
    console.log('2. Listar Usuários');
    console.log('3. Atualizar Usuário');
    console.log('4. Remover Usuário');
    console.log('5. Sair');
    console.log('=========================');
    
    const option = await askQuestion('Escolha uma opção: ');

    switch (option.trim()) {
        case '1':
            await createUser();
            break;
        case '2':
            await listUsers();
            break;
        case '3':
            await updateUser();
            break;
        case '4':
            await deleteUser();
            break;
        case '5':
            console.log('Encerrando o sistema...');
            db.close();
            rl.close();
            return;
        default:
            console.log('Opção inválida. Tente novamente.');
    }

    // Loop do menu
    showMenu();
};

// Inicialização da Aplicação
const startApp = async () => {
    try {
        await initDB();
        showMenu();
    } catch (error) {
        console.error('Falha ao inicializar o banco de dados:', error);
        process.exit(1);
    }
};

startApp();
```