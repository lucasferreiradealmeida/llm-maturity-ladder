<!--
nivel: 2 - API REST
provider: gemini
model: gemini-3.1-pro-preview
modelo_resolvido: gemini-3.1-pro-preview
tentativa: 1
temperature: 0.2
timestamp: 2026-09-28T18:32:48.636Z
metadata: {"model":"gemini-3.1-pro-preview","modelVersion":"gemini-3.1-pro-preview","responseId":"0LK6arO7MPjUz7IP1cP10Q8","usage":{"promptTokenCount":205,"candidatesTokenCount":1985,"totalTokenCount":3479,"promptTokensDetails":[{"modality":"TEXT","tokenCount":205}],"thoughtsTokenCount":1289,"serviceTier":"standard"},"finish_reason":"STOP","parametros":{"maxOutputTokens":16000,"temperature":0.2,"thinkingConfig":{"thinkingBudget":2048}}}
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

Aqui está a implementação completa do sistema solicitado. 

Para manter a simplicidade e seguir a restrição de usar apenas os frameworks estritamente necessários, utilizei o **Express** (padrão da indústria para roteamento e APIs REST em Node.js) e o **sqlite3** (driver nativo para interagir com o banco de dados SQLite).

### Instruções de Execução

1. Certifique-se de ter o **Node.js** instalado em sua máquina.
2. Crie uma nova pasta para o projeto e abra o terminal nela.
3. Crie os três arquivos abaixo (`package.json`, `database.js` e `server.js`) e cole os respectivos códigos.
4. No terminal, execute o comando abaixo para instalar as dependências:
   ```bash
   npm install
   ```
5. Para iniciar o servidor, execute:
   ```bash
   npm start
   ```
6. O servidor estará rodando em `http://localhost:3000`. O arquivo do banco de dados (`database.sqlite`) será criado automaticamente na raiz do projeto.

---

### `package.json`
Este arquivo define as dependências do projeto e o script de inicialização.

```json
{
  "name": "user-api",
  "version": "1.0.0",
  "description": "API REST para cadastro de usuários com SQLite",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "sqlite3": "^5.1.6"
  }
}
```

---

### `database.js`
Este arquivo é responsável por conectar ao banco de dados SQLite e criar a tabela de usuários caso ela não exista.

```javascript
const sqlite3 = require('sqlite3').verbose();

// Assunção: O banco de dados será salvo em um arquivo local chamado 'database.sqlite'.
const db = new sqlite3.Database('./database.sqlite', (err) => {
    if (err) {
        console.error('Erro ao conectar ao banco de dados:', err.message);
    } else {
        console.log('Conectado ao banco de dados SQLite.');
    }
});

// Assunção: A tabela 'users' terá id (auto-incremento), nome, email (único) e data de nascimento.
// A data de nascimento será armazenada como TEXT (formato esperado: YYYY-MM-DD).
db.serialize(() => {
    db.run(`
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            birthdate TEXT NOT NULL
        )
    `, (err) => {
        if (err) {
            console.error('Erro ao criar tabela:', err.message);
        }
    });
});

module.exports = db;
```

---

### `server.js`
Este é o arquivo principal da aplicação, contendo a configuração do Express e os endpoints da API REST.

```javascript
const express = require('express');
const db = require('./database');

const app = express();
const PORT = 3000;

// Middleware para fazer o parse do corpo das requisições em JSON
app.use(express.json());

// ==========================================
// ENDPOINTS DA API
// ==========================================

// 1. CREATE: Criar um novo usuário (POST /users)
app.post('/users', (req, res) => {
    const { name, email, birthdate } = req.body;

    // Validação básica
    if (!name || !email || !birthdate) {
        return res.status(400).json({ error: 'Nome, e-mail e data de nascimento são obrigatórios.' });
    }

    const sql = `INSERT INTO users (name, email, birthdate) VALUES (?, ?, ?)`;
    
    db.run(sql, [name, email, birthdate], function(err) {
        if (err) {
            // Assunção: Se houver erro de constraint (ex: email duplicado), retorna 400.
            if (err.message.includes('UNIQUE constraint failed')) {
                return res.status(400).json({ error: 'Este e-mail já está cadastrado.' });
            }
            return res.status(500).json({ error: 'Erro interno do servidor.' });
        }
        
        // Retorna 201 Created com os dados do usuário recém-criado
        res.status(201).json({
            id: this.lastID,
            name,
            email,
            birthdate
        });
    });
});

// 2. READ: Listar todos os usuários (GET /users)
app.get('/users', (req, res) => {
    const sql = `SELECT * FROM users`;
    
    db.all(sql, [], (err, rows) => {
        if (err) {
            return res.status(500).json({ error: 'Erro ao buscar usuários.' });
        }
        res.status(200).json(rows);
    });
});

// 3. READ: Obter um usuário específico por ID (GET /users/:id)
app.get('/users/:id', (req, res) => {
    const { id } = req.params;
    const sql = `SELECT * FROM users WHERE id = ?`;
    
    db.get(sql, [id], (err, row) => {
        if (err) {
            return res.status(500).json({ error: 'Erro ao buscar o usuário.' });
        }
        if (!row) {
            return res.status(404).json({ error: 'Usuário não encontrado.' });
        }
        res.status(200).json(row);
    });
});

// 4. UPDATE: Atualizar um usuário existente (PUT /users/:id)
app.put('/users/:id', (req, res) => {
    const { id } = req.params;
    const { name, email, birthdate } = req.body;

    if (!name || !email || !birthdate) {
        return res.status(400).json({ error: 'Nome, e-mail e data de nascimento são obrigatórios.' });
    }

    const sql = `UPDATE users SET name = ?, email = ?, birthdate = ? WHERE id = ?`;
    
    db.run(sql, [name, email, birthdate, id], function(err) {
        if (err) {
            if (err.message.includes('UNIQUE constraint failed')) {
                return res.status(400).json({ error: 'Este e-mail já está em uso por outro usuário.' });
            }
            return res.status(500).json({ error: 'Erro ao atualizar o usuário.' });
        }
        
        // this.changes indica quantas linhas foram afetadas pela query
        if (this.changes === 0) {
            return res.status(404).json({ error: 'Usuário não encontrado.' });
        }
        
        res.status(200).json({ id: Number(id), name, email, birthdate });
    });
});

// 5. DELETE: Remover um usuário (DELETE /users/:id)
app.delete('/users/:id', (req, res) => {
    const { id } = req.params;
    const sql = `DELETE FROM users WHERE id = ?`;
    
    db.run(sql, [id], function(err) {
        if (err) {
            return res.status(500).json({ error: 'Erro ao deletar o usuário.' });
        }
        
        if (this.changes === 0) {
            return res.status(404).json({ error: 'Usuário não encontrado.' });
        }
        
        // Retorna 204 No Content (sucesso, sem corpo na resposta)
        res.status(204).send();
    });
});

// Inicia o servidor
app.listen(PORT, () => {
    console.log(`Servidor rodando na porta ${PORT}`);
    console.log(`Endpoints disponíveis:`);
    console.log(`- POST   /users`);
    console.log(`- GET    /users`);
    console.log(`- GET    /users/:id`);
    console.log(`- PUT    /users/:id`);
    console.log(`- DELETE /users/:id`);
});
```