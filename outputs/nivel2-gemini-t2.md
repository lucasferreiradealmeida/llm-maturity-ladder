<!--
nivel: 2 - API REST
provider: gemini
model: gemini-pro-latest
tentativa: 2
temperature: 0.2
timestamp: 2026-08-18T17:07:53.703Z
metadata: {"model":"gemini-pro-latest","usage":{"promptTokenCount":205,"candidatesTokenCount":2208,"totalTokenCount":3703,"promptTokensDetails":[{"modality":"TEXT","tokenCount":205}],"thoughtsTokenCount":1290,"serviceTier":"standard"},"finish_reason":"STOP"}
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

Aqui está a implementação completa do sistema de cadastro de usuários em uma API REST utilizando Node.js, Express e SQLite.

### Decisões de Arquitetura e Assunções:
1. **Framework Express:** Utilizei o `express` pois construir um roteador REST e um parser de JSON robustos do zero com o módulo nativo `http` seria reinventar a roda, o que vai contra as boas práticas de engenharia de software.
2. **Banco de Dados:** Utilizei o pacote `sqlite3`. O banco de dados será salvo em um arquivo local chamado `database.sqlite`.
3. **Validação:** Adicionei validações básicas para garantir que `nome`, `email` e `data_nascimento` sejam enviados. O e-mail foi configurado como `UNIQUE` no banco de dados para evitar duplicidade.
4. **Formato de Data:** Assumi que a data de nascimento (`data_nascimento`) será enviada e armazenada como uma string no formato ISO (`YYYY-MM-DD`).

---

### Instruções de Execução

**1. Pré-requisitos:**
Certifique-se de ter o [Node.js](https://nodejs.org/) instalado na sua máquina (versão 14 ou superior).

**2. Instalação:**
Crie uma pasta para o projeto, salve os arquivos abaixo dentro dela e, no terminal, execute os seguintes comandos:

```bash
# Inicializa o projeto Node.js
npm init -y

# Instala as dependências estritamente necessárias
npm install express sqlite3
```

**3. Como rodar:**
No terminal, dentro da pasta do projeto, execute:
```bash
node index.js
```
O servidor iniciará na porta `3000`.

---

### Arquivos do Projeto

`database.js`
```javascript
// database.js
// Responsável por inicializar a conexão com o SQLite e criar a tabela se não existir.

const sqlite3 = require('sqlite3').verbose();

// Cria ou conecta ao arquivo de banco de dados local
const db = new sqlite3.Database('./database.sqlite', (err) => {
    if (err) {
        console.error('Erro ao conectar ao banco de dados:', err.message);
    } else {
        console.log('Conectado ao banco de dados SQLite.');
    }
});

// Criação da tabela de usuários
db.serialize(() => {
    db.run(`
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            data_nascimento TEXT NOT NULL
        )
    `, (err) => {
        if (err) {
            console.error('Erro ao criar tabela:', err.message);
        }
    });
});

module.exports = db;
```

`index.js`
```javascript
// index.js
// Arquivo principal da API REST contendo as rotas (Endpoints)

const express = require('express');
const db = require('./database');

const app = express();
const PORT = 3000;

// Middleware para fazer o parse do corpo das requisições em JSON
app.use(express.json());

// ==========================================
// ENDPOINTS (CRUD)
// ==========================================

// 1. CREATE - Criar um novo usuário
app.post('/usuarios', (req, res) => {
    const { nome, email, data_nascimento } = req.body;

    // Validação básica
    if (!nome || !email || !data_nascimento) {
        return res.status(400).json({ erro: 'Nome, email e data_nascimento são obrigatórios.' });
    }

    const sql = `INSERT INTO usuarios (nome, email, data_nascimento) VALUES (?, ?, ?)`;
    
    db.run(sql, [nome, email, data_nascimento], function(err) {
        if (err) {
            // Tratamento para e-mail duplicado (Constraint UNIQUE)
            if (err.message.includes('UNIQUE constraint failed')) {
                return res.status(400).json({ erro: 'Este e-mail já está cadastrado.' });
            }
            return res.status(500).json({ erro: 'Erro interno do servidor.' });
        }
        
        // Retorna 201 (Created) e os dados do usuário criado
        res.status(201).json({
            id: this.lastID,
            nome,
            email,
            data_nascimento
        });
    });
});

// 2. READ - Listar todos os usuários
app.get('/usuarios', (req, res) => {
    const sql = `SELECT * FROM usuarios`;
    
    db.all(sql, [], (err, rows) => {
        if (err) {
            return res.status(500).json({ erro: 'Erro ao buscar usuários.' });
        }
        res.status(200).json(rows);
    });
});

// 3. READ - Buscar um usuário específico por ID
app.get('/usuarios/:id', (req, res) => {
    const { id } = req.params;
    const sql = `SELECT * FROM usuarios WHERE id = ?`;
    
    db.get(sql, [id], (err, row) => {
        if (err) {
            return res.status(500).json({ erro: 'Erro ao buscar o usuário.' });
        }
        if (!row) {
            return res.status(404).json({ erro: 'Usuário não encontrado.' });
        }
        res.status(200).json(row);
    });
});

// 4. UPDATE - Atualizar dados de um usuário
app.put('/usuarios/:id', (req, res) => {
    const { id } = req.params;
    const { nome, email, data_nascimento } = req.body;

    if (!nome || !email || !data_nascimento) {
        return res.status(400).json({ erro: 'Nome, email e data_nascimento são obrigatórios.' });
    }

    const sql = `UPDATE usuarios SET nome = ?, email = ?, data_nascimento = ? WHERE id = ?`;
    
    db.run(sql, [nome, email, data_nascimento, id], function(err) {
        if (err) {
            if (err.message.includes('UNIQUE constraint failed')) {
                return res.status(400).json({ erro: 'Este e-mail já está em uso por outro usuário.' });
            }
            return res.status(500).json({ erro: 'Erro ao atualizar o usuário.' });
        }
        
        if (this.changes === 0) {
            return res.status(404).json({ erro: 'Usuário não encontrado.' });
        }
        
        res.status(200).json({
            mensagem: 'Usuário atualizado com sucesso.',
            usuario: { id: Number(id), nome, email, data_nascimento }
        });
    });
});

// 5. DELETE - Remover um usuário
app.delete('/usuarios/:id', (req, res) => {
    const { id } = req.params;
    const sql = `DELETE FROM usuarios WHERE id = ?`;
    
    db.run(sql, [id], function(err) {
        if (err) {
            return res.status(500).json({ erro: 'Erro ao deletar o usuário.' });
        }
        
        if (this.changes === 0) {
            return res.status(404).json({ erro: 'Usuário não encontrado.' });
        }
        
        res.status(200).json({ mensagem: 'Usuário removido com sucesso.' });
    });
});

// Inicia o servidor
app.listen(PORT, () => {
    console.log(`Servidor rodando na porta ${PORT}`);
    console.log(`Endpoints disponíveis:`);
    console.log(`POST   http://localhost:${PORT}/usuarios`);
    console.log(`GET    http://localhost:${PORT}/usuarios`);
    console.log(`GET    http://localhost:${PORT}/usuarios/:id`);
    console.log(`PUT    http://localhost:${PORT}/usuarios/:id`);
    console.log(`DELETE http://localhost:${PORT}/usuarios/:id`);
});
```

### Como testar (Exemplos com cURL)

Você pode usar ferramentas como Postman, Insomnia ou o próprio terminal (cURL) para testar:

**Criar usuário:**
```bash
curl -X POST http://localhost:3000/usuarios \
-H "Content-Type: application/json" \
-d '{"nome": "João Silva", "email": "joao@email.com", "data_nascimento": "1990-05-15"}'
```

**Listar usuários:**
```bash
curl -X GET http://localhost:3000/usuarios
```

**Atualizar usuário (supondo ID 1):**
```bash
curl -X PUT http://localhost:3000/usuarios/1 \
-H "Content-Type: application/json" \
-d '{"nome": "João da Silva", "email": "joao.silva@email.com", "data_nascimento": "1990-05-15"}'
```

**Deletar usuário (supondo ID 1):**
```bash
curl -X DELETE http://localhost:3000/usuarios/1
```