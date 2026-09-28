<!--
nivel: 2 - API REST
provider: gemini
model: gemini-pro-latest
tentativa: 1
temperature: 0.2
timestamp: 2026-08-18T17:06:59.625Z
metadata: {"model":"gemini-pro-latest","usage":{"promptTokenCount":205,"candidatesTokenCount":1931,"totalTokenCount":3374,"promptTokensDetails":[{"modality":"TEXT","tokenCount":205}],"thoughtsTokenCount":1238,"serviceTier":"standard"},"finish_reason":"STOP"}
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

### Decisões e Premissas Assumidas (Documentadas):
1. **Frameworks:** Utilizei o `express` para roteamento e parsing de JSON, pois é o padrão mais leve e consolidado no ecossistema Node.js para APIs REST. Utilizei o `sqlite3` para a persistência de dados.
2. **Banco de Dados:** O banco de dados será criado em um arquivo local chamado `database.sqlite` na raiz do projeto. A tabela `users` será criada automaticamente ao iniciar o servidor, caso não exista.
3. **Validação:** Adicionei uma validação básica para garantir que `name`, `email` e `birthdate` sejam enviados na criação e atualização. O formato esperado para a data é uma string (ex: "YYYY-MM-DD").
4. **Tratamento de Erros:** O e-mail foi definido como `UNIQUE` no banco de dados. Se houver tentativa de cadastrar um e-mail duplicado, a API retornará erro `400 Bad Request`.

---

### Instruções de Execução

1. Crie uma pasta para o projeto e entre nela.
2. Salve os três arquivos abaixo (`package.json`, `db.js` e `server.js`) dentro dessa pasta.
3. Abra o terminal na pasta do projeto e instale as dependências executando:
   ```bash
   npm install
   ```
4. Inicie o servidor executando:
   ```bash
   npm start
   ```
5. O servidor estará rodando em `http://localhost:3000`.

---

### Arquivos do Projeto

`package.json`
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

`db.js`
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

// Cria a tabela de usuários se ela não existir
db.serialize(() => {
  db.run(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      email TEXT NOT NULL UNIQUE,
      birthdate TEXT NOT NULL
    )
  `);
});

module.exports = db;
```

`server.js`
```javascript
const express = require('express');
const db = require('./db');

const app = express();
const PORT = 3000;

// Middleware para fazer o parse do corpo das requisições para JSON
app.use(express.json());

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
        return res.status(400).json({ error: 'Este e-mail já está cadastrado.' });
      }
      return res.status(500).json({ error: 'Erro interno do servidor.' });
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
        return res.status(400).json({ error: 'Este e-mail já está em uso por outro usuário.' });
      }
      return res.status(500).json({ error: 'Erro ao atualizar o usuário.' });
    }
    
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
    
    // Retorna 204 No Content (sucesso sem corpo na resposta) ou 200 com mensagem
    res.status(200).json({ message: 'Usuário removido com sucesso.' });
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