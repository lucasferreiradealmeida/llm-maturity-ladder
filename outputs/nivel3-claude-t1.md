<!--
nivel: 3 - Sistema web full-stack
provider: claude
model: claude-sonnet-5
tentativa: 1
temperature: 0.2
timestamp: 2026-08-18T21:32:59.108Z
metadata: {"model":"claude-sonnet-5","usage":{"input_tokens":331,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"cache_creation":{"ephemeral_5m_input_tokens":0,"ephemeral_1h_input_tokens":0},"output_tokens":7900,"output_tokens_details":{"thinking_tokens":166},"service_tier":"standard","inference_geo":"global"},"stop_reason":"end_turn"}
-->

## Prompt enviado
```
Voce e um(a) engenheiro(a) de software responsavel por implementar o sistema
descrito abaixo. Gere o codigo completo, pronto para rodar, incluindo
instrucoes de execucao (como instalar dependencias e como rodar).

TAREFA:
Crie um sistema web completo (frontend + backend) para cadastro de
usuarios. O frontend deve permitir listar, cadastrar, editar e remover
usuarios atraves de uma interface no navegador, consumindo uma API REST
que persiste os dados em SQLite.

RESTRICOES:
- Linguagem: Node.js (JavaScript).
- Nao use frameworks alem dos estritamente necessarios para a tarefa.
- Nao peca esclarecimentos: assuma decisoes razoaveis e documente-as em comentarios.
- Entregue todos os arquivos necessarios, indicando o nome do arquivo antes de cada bloco de codigo.
```

## Resposta do modelo

# Sistema de Cadastro de Usuários

Sistema completo com backend em Node.js (Express + SQLite3) e frontend em HTML/CSS/JS puro (sem frameworks front-end), consumindo uma API REST.

**Decisões de projeto (documentadas também no código):**
- Uso do **Express** apenas por ser o mínimo necessário para roteamento HTTP em Node puro sem reinventar parsing de rotas/métodos.
- Uso do driver **sqlite3** apenas para persistência em arquivo SQLite (requisito da tarefa).
- Frontend em HTML/CSS/JS "vanilla" (sem React/Vue/etc), usando `fetch` para consumir a API.
- Banco de dados criado automaticamente (arquivo `usuarios.db`) na primeira execução.
- Validação simples de campos obrigatórios (nome e email) tanto no backend quanto no frontend.
- Email definido como `UNIQUE` no banco para evitar duplicidade.

## Estrutura de arquivos

```
projeto/
├── package.json
├── server.js
├── db.js
└── public/
    ├── index.html
    ├── style.css
    └── app.js
```

---

### `package.json`

```json
{
  "name": "cadastro-usuarios",
  "version": "1.0.0",
  "description": "Sistema de cadastro de usuarios com Node.js, Express, SQLite e frontend vanilla JS",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "^4.19.2",
    "sqlite3": "^5.1.7"
  }
}
```

---

### `db.js`

```javascript
// db.js
// Responsavel por criar/abrir o banco SQLite e garantir que a tabela exista.
// Uso de sqlite3 (driver oficial mais simples/leve) apenas para persistencia.

const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const DB_PATH = path.join(__dirname, 'usuarios.db');

const db = new sqlite3.Database(DB_PATH, (err) => {
  if (err) {
    console.error('Erro ao conectar ao banco de dados:', err.message);
    process.exit(1);
  }
  console.log('Conectado ao banco SQLite em', DB_PATH);
});

// Cria a tabela de usuarios caso nao exista.
// email é UNIQUE para evitar cadastros duplicados.
db.run(`
  CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    telefone TEXT,
    criado_em TEXT DEFAULT CURRENT_TIMESTAMP
  )
`, (err) => {
  if (err) {
    console.error('Erro ao criar tabela usuarios:', err.message);
  }
});

module.exports = db;
```

---

### `server.js`

```javascript
// server.js
// API REST para CRUD de usuarios, servindo tambem os arquivos estaticos do frontend.

const express = require('express');
const path = require('path');
const db = require('./db');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware para parsear JSON no corpo das requisicoes
app.use(express.json());

// Serve os arquivos estaticos do frontend (pasta public)
app.use(express.static(path.join(__dirname, 'public')));

// --------- Funcoes utilitarias de validacao ---------
function validarUsuario(body) {
  const erros = [];
  if (!body.nome || typeof body.nome !== 'string' || body.nome.trim() === '') {
    erros.push('O campo "nome" e obrigatorio.');
  }
  if (!body.email || typeof body.email !== 'string' || body.email.trim() === '') {
    erros.push('O campo "email" e obrigatorio.');
  } else {
    // validacao simples de formato de email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(body.email)) {
      erros.push('O campo "email" possui formato invalido.');
    }
  }
  return erros;
}

// --------- Rotas da API ---------

// GET /api/usuarios -> lista todos os usuarios
app.get('/api/usuarios', (req, res) => {
  db.all('SELECT * FROM usuarios ORDER BY id DESC', [], (err, rows) => {
    if (err) {
      return res.status(500).json({ erro: 'Erro ao buscar usuarios.', detalhes: err.message });
    }
    res.json(rows);
  });
});

// GET /api/usuarios/:id -> busca um usuario especifico
app.get('/api/usuarios/:id', (req, res) => {
  const { id } = req.params;
  db.get('SELECT * FROM usuarios WHERE id = ?', [id], (err, row) => {
    if (err) {
      return res.status(500).json({ erro: 'Erro ao buscar usuario.', detalhes: err.message });
    }
    if (!row) {
      return res.status(404).json({ erro: 'Usuario nao encontrado.' });
    }
    res.json(row);
  });
});

// POST /api/usuarios -> cria um novo usuario
app.post('/api/usuarios', (req, res) => {
  const { nome, email, telefone } = req.body;
  const erros = validarUsuario(req.body);
  if (erros.length > 0) {
    return res.status(400).json({ erro: 'Dados invalidos.', detalhes: erros });
  }

  const sql = 'INSERT INTO usuarios (nome, email, telefone) VALUES (?, ?, ?)';
  db.run(sql, [nome.trim(), email.trim(), telefone ? telefone.trim() : null], function (err) {
    if (err) {
      if (err.message.includes('UNIQUE')) {
        return res.status(409).json({ erro: 'Ja existe um usuario com este email.' });
      }
      return res.status(500).json({ erro: 'Erro ao criar usuario.', detalhes: err.message });
    }
    db.get('SELECT * FROM usuarios WHERE id = ?', [this.lastID], (err2, row) => {
      if (err2) {
        return res.status(500).json({ erro: 'Usuario criado, mas erro ao recuperar dados.' });
      }
      res.status(201).json(row);
    });
  });
});

// PUT /api/usuarios/:id -> atualiza um usuario existente
app.put('/api/usuarios/:id', (req, res) => {
  const { id } = req.params;
  const { nome, email, telefone } = req.body;
  const erros = validarUsuario(req.body);
  if (erros.length > 0) {
    return res.status(400).json({ erro: 'Dados invalidos.', detalhes: erros });
  }

  db.get('SELECT * FROM usuarios WHERE id = ?', [id], (err, row) => {
    if (err) {
      return res.status(500).json({ erro: 'Erro ao buscar usuario.', detalhes: err.message });
    }
    if (!row) {
      return res.status(404).json({ erro: 'Usuario nao encontrado.' });
    }

    const sql = 'UPDATE usuarios SET nome = ?, email = ?, telefone = ? WHERE id = ?';
    db.run(sql, [nome.trim(), email.trim(), telefone ? telefone.trim() : null, id], function (err2) {
      if (err2) {
        if (err2.message.includes('UNIQUE')) {
          return res.status(409).json({ erro: 'Ja existe um usuario com este email.' });
        }
        return res.status(500).json({ erro: 'Erro ao atualizar usuario.', detalhes: err2.message });
      }
      db.get('SELECT * FROM usuarios WHERE id = ?', [id], (err3, updatedRow) => {
        if (err3) {
          return res.status(500).json({ erro: 'Usuario atualizado, mas erro ao recuperar dados.' });
        }
        res.json(updatedRow);
      });
    });
  });
});

// DELETE /api/usuarios/:id -> remove um usuario
app.delete('/api/usuarios/:id', (req, res) => {
  const { id } = req.params;
  db.get('SELECT * FROM usuarios WHERE id = ?', [id], (err, row) => {
    if (err) {
      return res.status(500).json({ erro: 'Erro ao buscar usuario.', detalhes: err.message });
    }
    if (!row) {
      return res.status(404).json({ erro: 'Usuario nao encontrado.' });
    }
    db.run('DELETE FROM usuarios WHERE id = ?', [id], (err2) => {
      if (err2) {
        return res.status(500).json({ erro: 'Erro ao remover usuario.', detalhes: err2.message });
      }
      res.status(204).send();
    });
  });
});

// Fallback: qualquer outra rota GET nao correspondente devolve o index.html (SPA simples)
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Servidor rodando em http://localhost:${PORT}`);
});
```

---

### `public/index.html`

```html
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Cadastro de Usuarios</title>
  <link rel="stylesheet" href="style.css" />
</head>
<body>
  <div class="container">
    <h1>Cadastro de Usuarios</h1>

    <!-- Formulario de cadastro/edicao -->
    <section class="form-section">
      <h2 id="form-title">Novo Usuario</h2>
      <form id="user-form">
        <input type="hidden" id="user-id" />

        <label for="nome">Nome *</label>
        <input type="text" id="nome" name="nome" placeholder="Nome completo" required />

        <label for="email">Email *</label>
        <input type="email" id="email" name="email" placeholder="email@exemplo.com" required />

        <label for="telefone">Telefone</label>
        <input type="text" id="telefone" name="telefone" placeholder="(00) 00000-0000" />

        <div class="form-actions">
          <button type="submit" id="submit-btn">Salvar</button>
          <button type="button" id="cancel-btn" style="display:none;">Cancelar edicao</button>
        </div>
      </form>
      <p id="feedback" class="feedback"></p>
    </section>

    <!-- Lista de usuarios -->
    <section class="list-section">
      <h2>Usuarios Cadastrados</h2>
      <table id="user-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nome</th>
            <th>Email</th>
            <th>Telefone</th>
            <th>Acoes</th>
          </tr>
        </thead>
        <tbody id="user-table-body">
          <!-- Preenchido via JS -->
        </tbody>
      </table>
      <p id="empty-msg" style="display:none;">Nenhum usuario cadastrado.</p>
    </section>
  </div>

  <script src="app.js"></script>
</body>
</html>
```

---

### `public/style.css`

```css
/* style.css - estilos simples, sem frameworks CSS externos */

* {
  box-sizing: border-box;
}

body {
  font-family: Arial, Helvetica, sans-serif;
  background-color: #f4f6f8;
  margin: 0;
  padding: 0;
  color: #333;
}

.container {
  max-width: 800px;
  margin: 40px auto;
  padding: 0 20px;
}

h1 {
  text-align: center;
  color: #2c3e50;
}

.form-section, .list-section {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.1);
  margin-bottom: 30px;
}

label {
  display: block;
  margin-top: 10px;
  margin-bottom: 4px;
  font-weight: bold;
  font-size: 14px;
}

input[type="text"],
input[type="email"] {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
}

.form-actions {
  margin-top: 16px;
  display: flex;
  gap: 10px;
}

button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

#submit-btn {
  background-color: #2980b9;
  color: #fff;
}

#submit-btn:hover {
  background-color: #1f6391;
}

#cancel-btn {
  background-color: #bdc3c7;
  color: #333;
}

#cancel-btn:hover {
  background-color: #95a5a6;
}

.feedback {
  margin-top: 10px;
  font-size: 14px;
}

.feedback.error {
  color: #c0392b;
}

.feedback.success {
  color: #27ae60;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

th, td {
  padding: 10px;
  border-bottom: 1px solid #eee;
  text-align: left;
  font-size: 14px;
}

th {
  background-color: #ecf0f1;
}

.actions-cell button {
  margin-right: 6px;
}

.edit-btn {
  background-color: #f39c12;
  color: #fff;
}

.edit-btn:hover {
  background-color: #d68910;
}

.delete-btn {
  background-color: #e74c3c;
  color: #fff;
}

.delete-btn:hover {
  background-color: #c0392b;
}

#empty-msg {
  text-align: center;
  color: #777;
  margin-top: 10px;
}
```

---

### `public/app.js`

```javascript
// app.js - logica do frontend (vanilla JS), consome a API REST via fetch.

const API_URL = '/api/usuarios';

const form = document.getElementById('user-form');
const formTitle = document.getElementById('form-title');
const idInput = document.getElementById('user-id');
const nomeInput = document.getElementById('nome');
const emailInput = document.getElementById('email');
const telefoneInput = document.getElementById('telefone');
const submitBtn = document.getElementById('submit-btn');
const cancelBtn = document.getElementById('cancel-btn');
const feedback = document.getElementById('feedback');
const tableBody = document.getElementById('user-table-body');
const emptyMsg = document.getElementById('empty-msg');

// Exibe mensagem de feedback (sucesso ou erro) por alguns segundos
function mostrarFeedback(mensagem, tipo = 'success') {
  feedback.textContent = mensagem;
  feedback.className = `feedback ${tipo}`;
  setTimeout(() => {
    feedback.textContent = '';
    feedback.className = 'feedback';
  }, 4000);
}

// Busca e renderiza a lista de usuarios
async function carregarUsuarios() {
  try {
    const resp = await fetch(API_URL);
    if (!resp.ok) throw new Error('Erro ao carregar usuarios.');
    const usuarios = await resp.json();
    renderizarTabela(usuarios);
  } catch (err) {
    mostrarFeedback(err.message, 'error');
  }
}

// Renderiza as linhas da tabela
function renderizarTabela(usuarios) {
  tableBody.innerHTML = '';

  if (usuarios.length === 0) {
    emptyMsg.style.display = 'block';
    return;
  }
  emptyMsg.style.display = 'none';

  usuarios.forEach((usuario) => {
    const tr = document.createElement('tr');

    tr.innerHTML = `
      <td>${usuario.id}</td>
      <td>${escapeHtml(usuario.nome)}</td>
      <td>${escapeHtml(usuario.email)}</td>
      <td>${escapeHtml(usuario.telefone || '-')}</td>
      <td class="actions-cell">
        <button class="edit-btn" data-id="${usuario.id}">Editar</button>
        <button class="delete-btn" data-id="${usuario.id}">Remover</button>
      </td>
    `;

    tableBody.appendChild(tr);
  });

  // Liga os eventos dos botoes recem-criados
  document.querySelectorAll('.edit-btn').forEach((btn) => {
    btn.addEventListener('click', () => iniciarEdicao(btn.dataset.id));
  });
  document.querySelectorAll('.delete-btn').forEach((btn) => {
    btn.addEventListener('click', () => removerUsuario(btn.dataset.id));
  });
}

// Previne XSS simples ao inserir texto no HTML
function escapeHtml(texto) {
  const div = document.createElement('div');
  div.textContent = texto;
  return div.innerHTML;
}

// Preenche o formulario com os dados do usuario selecionado para edicao
async function iniciarEdicao(id) {
  try {
    const resp = await fetch(`${API_URL}/${id}`);
    if (!resp.ok) throw new Error('Usuario nao encontrado.');
    const usuario = await resp.json();

    idInput.value = usuario.id;
    nomeInput.value = usuario.nome;
    emailInput.value = usuario.email;
    telefoneInput.value = usuario.telefone || '';

    formTitle.textContent = `Editar Usuario #${usuario.id}`;
    submitBtn.textContent = 'Atualizar';
    cancelBtn.style.display = 'inline-block';

    window.scrollTo({ top: 0, behavior: 'smooth' });
  } catch (err) {
    mostrarFeedback(err.message, 'error');
  }
}

// Cancela a edicao e volta ao modo de cadastro
function cancelarEdicao() {
  form.reset();
  idInput.value = '';
  formTitle.textContent = 'Novo Usuario';
  submitBtn.textContent = 'Salvar';
  cancelBtn.style.display = 'none';
}

// Remove um usuario apos confirmacao
async function removerUsuario(id) {
  if (!confirm('Tem certeza que deseja remover este usuario?')) return;

  try {
    const resp = await fetch(`${API_URL}/${id}`, { method: 'DELETE' });
    if (!resp.ok && resp.status !== 204) {
      const data = await resp.json();
      throw new Error(data.erro || 'Erro ao remover usuario.');
    }
    mostrarFeedback('Usuario removido com sucesso.', 'success');
    carregarUsuarios();
  } catch (err) {
    mostrarFeedback(err.message, 'error');
  }
}

// Submissao do formulario: cria ou atualiza dependendo se ha um ID preenchido
form.addEventListener('submit', async (e) => {
  e.preventDefault();

  const id = idInput.value;
  const payload = {
    nome: nomeInput.value.trim(),
    email: emailInput.value.trim(),
    telefone: telefoneInput.value.trim(),
  };

  const metodo = id ? 'PUT' : 'POST';
  const url = id ? `${API_URL}/${id}` : API_URL;

  try {
    const resp = await fetch(url, {
      method: metodo,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const data = await resp.json();

    if (!resp.ok) {
      const msg = Array.isArray(data.detalhes) ? data.detalhes.join(' ') : (data.erro || 'Erro ao salvar usuario.');
      throw new Error(msg);
    }

    mostrarFeedback(id ? 'Usuario atualizado com sucesso.' : 'Usuario cadastrado com sucesso.', 'success');
    cancelarEdicao();
    carregarUsuarios();
  } catch (err) {
    mostrarFeedback(err.message, 'error');
  }
});

cancelBtn.addEventListener('click', cancelarEdicao);

// Carrega a lista assim que a pagina abre
carregarUsuarios();
```

---

## Instruções de execução

1. **Pré-requisitos:** Node.js instalado (versão 16+ recomendada).

2. Crie a estrutura de pastas exatamente como mostrado acima e salve cada arquivo com o conteúdo correspondente.

3. Na raiz do projeto, instale as dependências:

```bash
npm install
```

4. Inicie o servidor:

```bash
npm start
```

5. Acesse no navegador:

```
http://localhost:3000
```

O arquivo `usuarios.db` (SQLite) será criado automaticamente na primeira execução, na raiz do projeto.

## Endpoints da API (para referência/testes via curl/Postman)

| Método | Rota                  | Descrição                    |
|--------|-----------------------|-------------------------------|
| GET    | /api/usuarios         | Lista todos os usuários       |
| GET    | /api/usuarios/:id     | Busca um usuário específico   |
| POST   | /api/usuarios         | Cria um novo usuário          |
| PUT    | /api/usuarios/:id     | Atualiza um usuário existente |
| DELETE | /api/usuarios/:id     | Remove um usuário             |

Corpo esperado (POST/PUT), em JSON:
```json
{
  "nome": "Nome do Usuário",
  "email": "email@exemplo.com",
  "telefone": "(11) 99999-9999"
}
```