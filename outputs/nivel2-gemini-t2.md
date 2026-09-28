<!--
nivel: 2 - API REST
provider: gemini
model: gemini-3.1-pro-preview
modelo_resolvido: gemini-3.1-pro-preview
tentativa: 2
temperature: 0.2
timestamp: 2026-09-28T18:33:14.274Z
metadata: {"model":"gemini-3.1-pro-preview","modelVersion":"gemini-3.1-pro-preview","responseId":"6rK6apHJGsqhz7IP95rZkAs","usage":{"promptTokenCount":205,"candidatesTokenCount":2264,"totalTokenCount":3699,"promptTokensDetails":[{"modality":"TEXT","tokenCount":205}],"thoughtsTokenCount":1230,"serviceTier":"standard"},"finish_reason":"STOP","parametros":{"maxOutputTokens":16000,"temperature":0.2,"thinkingConfig":{"thinkingBudget":2048}}}
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

Como engenheiro de software, projetei a solução utilizando **Node.js** com os pacotes **Express** (para roteamento e manipulação HTTP, sendo o padrão mais enxuto e aceito para APIs REST em Node) e **sqlite3** (driver nativo para comunicação com o banco de dados). 

### Decisões de Arquitetura e Premissas Assumidas:
1. **Validação Básica:** Assumi que todos os campos (nome, e-mail, data de nascimento) são obrigatórios.
2. **Formato de Data:** Assumi que a data de nascimento (`birthdate`) será enviada e armazenada como string no formato ISO 8601 (`YYYY-MM-DD`).
3. **Unicidade:** O campo `email` foi definido como `UNIQUE` no banco de dados. Tentativas de cadastrar e-mails duplicados retornarão erro `400 Bad Request`.
4. **Estrutura:** O código foi dividido em `database.js` (configuração do banco) e `server.js` (lógica da API) para manter a organização. O banco será salvo em um arquivo local chamado `database.sqlite`.

---

### Instruções de Execução

1. **Pré-requisitos:** Certifique-se de ter o [Node.js](https://nodejs.org/) instalado na sua máquina.
2. **Crie um diretório para o projeto** e entre nele:
   ```bash
   mkdir api-usuarios
   cd api-usuarios
   ```
3. **Crie os arquivos** listados abaixo com seus respectivos conteúdos.
4. **Instale as dependências**:
   ```bash
   npm install
   ```
5. **Inicie o servidor**:
   ```bash
   npm start
   ```
O servidor estará rodando em `http://localhost:3000`.

---

### Arquivos do Projeto

**`package.json`**
```json
{
  "name": "api-usuarios",
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

**`database.js`**
```javascript
const sqlite3 = require('sqlite3').verbose();

// Conecta ao banco de dados SQLite (cria o arquivo se não existir)
const db = new sqlite3.Database('./database.sqlite', (err) => {
    if (err) {
        console.error('Erro ao conectar ao banco de dados:', err.message);
    } else {
        console.log('Conectado ao banco de dados SQLite.');
    }
});

// Criação da tabela de usuários caso não exista
const createTableQuery = `
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        birthdate TEXT NOT NULL
    )
`;

db.run(createTableQuery, (err) => {
    if (err) {
        console.error('Erro ao criar tabela:', err.message);
    }
});

module.exports = db;
```

**`server.js`**
```javascript
const express = require('express');
const db = require('./database');

const app = express();
const PORT = 3000;

// Middleware para fazer o parse do corpo das requisições para JSON
app.use(express.json());

// ==========================================
// ENDPOINTS DA API
// ==========================================

// 1. CREATE: Criar um novo usuário
app.post('/users', (req, res) => {
    const { name, email, birthdate } = req.body;

    // Validação simples
    if (!name || !email || !birthdate) {
        return res.status(400).json({ error: 'Nome, e-mail e data de nascimento são obrigatórios.' });
    }

    const query = `INSERT INTO users (name, email, birthdate) VALUES (?, ?, ?)`;
    
    // Usamos function() em vez de arrow function para ter acesso ao 'this.lastID'
    db.run(query, [name, email, birthdate], function(err) {
        if (err) {
            // Tratamento para e-mail duplicado (constraint UNIQUE)
            if (err.message.includes('UNIQUE constraint failed')) {
                return res.status(400).json({ error: 'Este e-mail já está cadastrado.' });
            }
            return res.status(500).json({ error: 'Erro interno do servidor.' });
        }
        
        res.status(201).json({
            id: this.lastID,
            name,
            email,
            birthdate
        });
    });
});

// 2. READ: Listar todos os usuários
app.get('/users', (req, res) => {
    const query = `SELECT * FROM users`;
    
    db.all(query, [], (err, rows) => {
        if (err) {
            return res.status(500).json({ error: 'Erro ao buscar usuários.' });
        }
        res.status(200).json(rows);
    });
});

// 3. READ: Buscar um usuário específico por ID
app.get('/users/:id', (req, res) => {
    const { id } = req.params;
    const query = `SELECT * FROM users WHERE id = ?`;
    
    db.get(query, [id], (err, row) => {
        if (err) {
            return res.status(500).json({ error: 'Erro ao buscar usuário.' });
        }
        if (!row) {
            return res.status(404).json({ error: 'Usuário não encontrado.' });
        }
        res.status(200).json(row);
    });
});

// 4. UPDATE: Atualizar um usuário existente
app.put('/users/:id', (req, res) => {
    const { id } = req.params;
    const { name, email, birthdate } = req.body;

    if (!name || !email || !birthdate) {
        return res.status(400).json({ error: 'Nome, e-mail e data de nascimento são obrigatórios.' });
    }

    const query = `UPDATE users SET name = ?, email = ?, birthdate = ? WHERE id = ?`;
    
    db.run(query, [name, email, birthdate, id], function(err) {
        if (err) {
            if (err.message.includes('UNIQUE constraint failed')) {
                return res.status(400).json({ error: 'Este e-mail já está em uso por outro usuário.' });
            }
            return res.status(500).json({ error: 'Erro ao atualizar usuário.' });
        }
        
        // this.changes indica quantas linhas foram afetadas
        if (this.changes === 0) {
            return res.status(404).json({ error: 'Usuário não encontrado.' });
        }
        
        res.status(200).json({ id: Number(id), name, email, birthdate });
    });
});

// 5. DELETE: Remover um usuário
app.delete('/users/:id', (req, res) => {
    const { id } = req.params;
    const query = `DELETE FROM users WHERE id = ?`;
    
    db.run(query, [id], function(err) {
        if (err) {
            return res.status(500).json({ error: 'Erro ao deletar usuário.' });
        }
        
        if (this.changes === 0) {
            return res.status(404).json({ error: 'Usuário não encontrado.' });
        }
        
        // 204 No Content é o padrão REST para deleção com sucesso sem corpo de resposta
        res.status(204).send();
    });
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
```

### Como testar (Exemplos com `curl`)

**Criar usuário:**
```bash
curl -X POST http://localhost:3000/users \
-H "Content-Type: application/json" \
-d '{"name": "João Silva", "email": "joao@email.com", "birthdate": "1990-05-15"}'
```

**Listar usuários:**
```bash
curl -X GET http://localhost:3000/users
```

**Atualizar usuário (substitua o `1` pelo ID real):**
```bash
curl -X PUT http://localhost:3000/users/1 \
-H "Content-Type: application/json" \
-d '{"name": "João da Silva", "email": "joao.silva@email.com", "birthdate": "1990-05-15"}'
```

**Deletar usuário (substitua o `1` pelo ID real):**
```bash
curl -X DELETE http://localhost:3000/users/1
```