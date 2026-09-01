<!--
nivel: 2 - API REST
provider: gemini
model: gemini-3.1-pro-preview
tentativa: 3
temperature: 0.2
timestamp: 2026-08-31T08:47:11.780Z
metadata: {"model":"gemini-3.1-pro-preview","usage":{"promptTokenCount":205,"candidatesTokenCount":2037,"totalTokenCount":3507,"promptTokensDetails":[{"modality":"TEXT","tokenCount":205}],"thoughtsTokenCount":1265,"serviceTier":"standard"},"finish_reason":"STOP"}
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

Para esta solução, tomei as seguintes decisões arquiteturais e premissas (documentadas no código):
1. **Express.js**: Utilizado como framework web minimalista, pois é o padrão da indústria para APIs REST em Node.js e facilita o roteamento e o parse de JSON.
2. **SQLite3**: Utilizado o driver oficial `sqlite3` para persistência. O banco de dados será salvo em um arquivo local chamado `database.sqlite`.
3. **Validação**: Implementei uma validação básica para garantir que os campos obrigatórios sejam enviados. Assumi que a data de nascimento será enviada como uma string (ex: "YYYY-MM-DD").
4. **Segurança**: Utilizei *Prepared Statements* (parâmetros `?`) em todas as queries SQL para evitar SQL Injection.

### Instruções de Execução

1. Certifique-se de ter o **Node.js** instalado em sua máquina.
2. Crie uma pasta para o projeto e salve os dois arquivos abaixo dentro dela.
3. Abra o terminal na pasta do projeto e execute o comando para instalar as dependências:
   ```bash
   npm install
   ```
4. Inicie o servidor com o comando:
   ```bash
   npm start
   ```
5. A API estará rodando em `http://localhost:3000`.

---

### `package.json`
```json
{
  "name": "user-registration-api",
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

### `server.js`
```javascript
const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

// Inicializa o aplicativo Express
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware para fazer o parse do corpo das requisições para JSON
app.use(express.json());

// Configuração e conexão com o banco de dados SQLite
// Assunção: O banco será salvo em um arquivo local na raiz do projeto.
const dbPath = path.resolve(__dirname, 'database.sqlite');
const db = new sqlite3.Database(dbPath, (err) => {
    if (err) {
        console.error('Erro ao conectar ao banco de dados SQLite:', err.message);
    } else {
        console.log('Conectado ao banco de dados SQLite.');
        // Criação da tabela de usuários caso não exista
        // Assunção: O email deve ser único no sistema.
        db.run(`
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                birthdate TEXT NOT NULL
            )
        `);
    }
});

// ==========================================
// ENDPOINTS DA API REST
// ==========================================

// 1. CREATE - Criar um novo usuário
app.post('/users', (req, res) => {
    const { name, email, birthdate } = req.body;

    // Validação básica
    if (!name || !email || !birthdate) {
        return res.status(400).json({ error: 'Nome, e-mail e data de nascimento são obrigatórios.' });
    }

    const sql = `INSERT INTO users (name, email, birthdate) VALUES (?, ?, ?)`;
    
    db.run(sql, [name, email, birthdate], function(err) {
        if (err) {
            // Tratamento para e-mail duplicado (constraint UNIQUE)
            if (err.message.includes('UNIQUE constraint failed')) {
                return res.status(409).json({ error: 'Este e-mail já está cadastrado.' });
            }
            return res.status(500).json({ error: 'Erro interno ao criar usuário.' });
        }
        // Retorna 201 Created com os dados do usuário inserido
        res.status(201).json({
            id: this.lastID,
            name,
            email,
            birthdate
        });
    });
});

// 2. READ - Listar todos os usuários
app.get('/users', (req, res) => {
    const sql = `SELECT * FROM users`;
    
    db.all(sql, [], (err, rows) => {
        if (err) {
            return res.status(500).json({ error: 'Erro ao buscar usuários.' });
        }
        res.status(200).json(rows);
    });
});

// 3. READ - Obter um usuário específico por ID
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

// 4. UPDATE - Atualizar um usuário existente
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
                return res.status(409).json({ error: 'Este e-mail já está em uso por outro usuário.' });
            }
            return res.status(500).json({ error: 'Erro ao atualizar o usuário.' });
        }
        
        // this.changes contém o número de linhas afetadas pela query
        if (this.changes === 0) {
            return res.status(404).json({ error: 'Usuário não encontrado.' });
        }
        
        res.status(200).json({
            id: Number(id),
            name,
            email,
            birthdate
        });
    });
});

// 5. DELETE - Remover um usuário
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
        
        // Retorna 204 No Content (sucesso sem corpo de resposta)
        res.status(204).send();
    });
});

// Tratamento para rotas não encontradas
app.use((req, res) => {
    res.status(404).json({ error: 'Rota não encontrada.' });
});

// Inicia o servidor
app.listen(PORT, () => {
    console.log(`Servidor rodando na porta ${PORT}`);
    console.log(`Endpoints disponíveis:`);
    console.log(`  POST   /users`);
    console.log(`  GET    /users`);
    console.log(`  GET    /users/:id`);
    console.log(`  PUT    /users/:id`);
    console.log(`  DELETE /users/:id`);
});

// Tratamento para fechar o banco de dados graciosamente ao encerrar o processo
process.on('SIGINT', () => {
    db.close((err) => {
        if (err) {
            console.error(err.message);
        }
        console.log('Conexão com o banco de dados fechada.');
        process.exit(0);
    });
});
```