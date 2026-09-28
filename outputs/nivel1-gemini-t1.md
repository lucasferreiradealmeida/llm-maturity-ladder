<!--
nivel: 1 - CRUD com persistencia em banco
provider: gemini
model: gemini-3.1-pro-preview
modelo_resolvido: gemini-3.1-pro-preview
tentativa: 1
temperature: 0.2
timestamp: 2026-09-28T18:31:45.714Z
metadata: {"model":"gemini-3.1-pro-preview","modelVersion":"gemini-3.1-pro-preview","responseId":"krK6aq7qI-KR_uMP5vurkAs","usage":{"promptTokenCount":235,"candidatesTokenCount":2194,"totalTokenCount":4263,"promptTokensDetails":[{"modality":"TEXT","tokenCount":235}],"thoughtsTokenCount":1834,"serviceTier":"standard"},"finish_reason":"STOP","parametros":{"maxOutputTokens":16000,"temperature":0.2,"thinkingConfig":{"thinkingBudget":2048}}}
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

### Decisões de Arquitetura e Design:
1. **Dependências:** Utilizei apenas o pacote `sqlite3` para a comunicação com o banco de dados. Não utilizei frameworks de CLI (como Commander ou Yargs) para manter o código o mais enxuto possível e aderir à restrição de "não usar frameworks além dos estritamente necessários". O parse dos argumentos é feito nativamente via `process.argv`.
2. **Validação:** A validação de e-mail é feita via Regex. A validação de data exige o formato `YYYY-MM-DD`.
3. **Atualização (Update):** Para simplificar a interface de linha de comando, o comando de atualização exige que todos os dados (nome, e-mail e data de nascimento) sejam fornecidos, substituindo os dados anteriores.
4. **Encerramento:** O banco de dados é fechado automaticamente após a execução de cada comando para evitar que o terminal fique travado.

---

### Instruções de Execução

**1. Pré-requisitos:**
* Node.js instalado (versão 14 ou superior recomendada).

**2. Instalação:**
Crie uma pasta para o projeto, salve os arquivos abaixo dentro dela e execute o comando para instalar a dependência do SQLite:
```bash
npm install
```

**3. Como usar:**
Antes de qualquer operação, inicialize o banco de dados (criação do schema):
```bash
node index.js init
```

* **Cadastrar usuário:**
```bash
node index.js add "João Silva" "joao@email.com" "1990-05-20"
```

* **Listar usuários:**
```bash
node index.js list
```

* **Atualizar usuário (exige o ID do usuário como primeiro parâmetro):**
```bash
node index.js update 1 "João da Silva" "joao.silva@email.com" "1990-05-20"
```

* **Remover usuário:**
```bash
node index.js delete 1
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

`db.js`
```javascript
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

// Conecta ao banco de dados SQLite (cria o arquivo database.sqlite na raiz do projeto)
const dbPath = path.resolve(__dirname, 'database.sqlite');
const db = new sqlite3.Database(dbPath, (err) => {
    if (err) {
        console.error('Erro ao conectar ao banco de dados:', err.message);
        process.exit(1);
    }
});

// Função para inicializar o Schema
const initDB = () => {
    return new Promise((resolve, reject) => {
        const query = `
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                dob TEXT NOT NULL
            )
        `;
        db.run(query, (err) => {
            if (err) reject(err);
            else resolve();
        });
    });
};

// Wrapper para executar queries (INSERT, UPDATE, DELETE) com Promises
const runQuery = (query, params = []) => {
    return new Promise((resolve, reject) => {
        db.run(query, params, function (err) {
            if (err) reject(err);
            else resolve(this); // Retorna o contexto (this.lastID, this.changes)
        });
    });
};

// Wrapper para buscar dados (SELECT) com Promises
const getQuery = (query, params = []) => {
    return new Promise((resolve, reject) => {
        db.all(query, params, (err, rows) => {
            if (err) reject(err);
            else resolve(rows);
        });
    });
};

module.exports = { db, initDB, runQuery, getQuery };
```

`index.js`
```javascript
const { db, initDB, runQuery, getQuery } = require('./db');

// Captura os argumentos passados na linha de comando
const args = process.argv.slice(2);
const command = args[0];

// Funções de validação
const isValidEmail = (email) => {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
};

const isValidDate = (date) => {
    // Valida formato YYYY-MM-DD
    const regex = /^\d{4}-\d{2}-\d{2}$/;
    return regex.test(date);
};

// Tratamento de erros amigável
const handleError = (err) => {
    if (err.code === 'SQLITE_CONSTRAINT') {
        console.error('❌ Erro: O e-mail informado já está cadastrado no sistema.');
    } else {
        console.error('❌ Ocorreu um erro inesperado:', err.message);
    }
};

// Lógica principal da CLI
const main = async () => {
    try {
        switch (command) {
            case 'init':
                await initDB();
                console.log('✅ Banco de dados e tabelas inicializados com sucesso!');
                break;

            case 'add': {
                const [, name, email, dob] = args;
                if (!name || !email || !dob) {
                    console.log('Uso correto: node index.js add "<nome>" "<email>" "<data_nascimento YYYY-MM-DD>"');
                    return;
                }
                if (!isValidEmail(email)) {
                    console.log('❌ Erro: Formato de e-mail inválido.');
                    return;
                }
                if (!isValidDate(dob)) {
                    console.log('❌ Erro: A data de nascimento deve estar no formato YYYY-MM-DD.');
                    return;
                }

                await runQuery('INSERT INTO users (name, email, dob) VALUES (?, ?, ?)', [name, email, dob]);
                console.log(`✅ Usuário '${name}' cadastrado com sucesso!`);
                break;
            }

            case 'list': {
                const users = await getQuery('SELECT * FROM users');
                if (users.length === 0) {
                    console.log('Nenhum usuário cadastrado.');
                } else {
                    console.log('\n--- Lista de Usuários ---');
                    console.table(users);
                }
                break;
            }

            case 'update': {
                const [, id, newName, newEmail, newDob] = args;
                if (!id || !newName || !newEmail || !newDob) {
                    console.log('Uso correto: node index.js update <id> "<novo_nome>" "<novo_email>" "<nova_data YYYY-MM-DD>"');
                    return;
                }
                if (!isValidEmail(newEmail)) {
                    console.log('❌ Erro: Formato de e-mail inválido.');
                    return;
                }
                if (!isValidDate(newDob)) {
                    console.log('❌ Erro: A data de nascimento deve estar no formato YYYY-MM-DD.');
                    return;
                }

                const result = await runQuery(
                    'UPDATE users SET name = ?, email = ?, dob = ? WHERE id = ?',
                    [newName, newEmail, newDob, id]
                );

                if (result.changes === 0) {
                    console.log(`⚠️ Nenhum usuário encontrado com o ID ${id}.`);
                } else {
                    console.log(`✅ Usuário ID ${id} atualizado com sucesso!`);
                }
                break;
            }

            case 'delete': {
                const [, deleteId] = args;
                if (!deleteId) {
                    console.log('Uso correto: node index.js delete <id>');
                    return;
                }

                const result = await runQuery('DELETE FROM users WHERE id = ?', [deleteId]);
                
                if (result.changes === 0) {
                    console.log(`⚠️ Nenhum usuário encontrado com o ID ${deleteId}.`);
                } else {
                    console.log(`✅ Usuário ID ${deleteId} removido com sucesso!`);
                }
                break;
            }

            default:
                console.log(`
Comandos disponíveis:
  init                                  - Cria o banco de dados e a tabela
  add <nome> <email> <data_nasc>        - Cadastra um novo usuário
  list                                  - Lista todos os usuários
  update <id> <nome> <email> <data_nasc>- Atualiza um usuário existente
  delete <id>                           - Remove um usuário
                `);
                break;
        }
    } catch (err) {
        handleError(err);
    } finally {
        // Garante que a conexão com o banco seja fechada para liberar o terminal
        db.close();
    }
};

main();
```