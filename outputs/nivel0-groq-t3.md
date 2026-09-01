<!--
nivel: 0 - Persistencia simples
provider: groq
model: openai/gpt-oss-120b
tentativa: 3
temperature: 0.2
timestamp: 2026-08-31T09:06:49.115Z
metadata: {"model":"openai/gpt-oss-120b","usage":{"queue_time":0.248659017,"prompt_tokens":247,"prompt_time":0.067615911,"completion_tokens":1738,"completion_time":3.6502838,"total_tokens":1985,"total_time":3.7178997110000003,"completion_tokens_details":{"reasoning_tokens":89}},"finish_reason":"stop"}
-->

## Prompt enviado
```
Voce e um(a) engenheiro(a) de software responsavel por implementar o sistema
descrito abaixo. Gere o codigo completo, pronto para rodar, incluindo
instrucoes de execucao (como instalar dependencias e como rodar).

TAREFA:
Crie um script que registre o nome de um usuario em um arquivo CSV
(nome, data de cadastro). Deve ser possivel rodar o script varias vezes e
cada execucao adicionar uma nova linha sem sobrescrever as anteriores.

RESTRICOES:
- Linguagem: Node.js (JavaScript).
- Nao use frameworks alem dos estritamente necessarios para a tarefa.
- Nao peca esclarecimentos: assuma decisoes razoaveis e documente-as em comentarios.
- Entregue todos os arquivos necessarios, indicando o nome do arquivo antes de cada bloco de codigo.
```

## Resposta do modelo

**📂 Projeto:** `user‑register‑csv`  
**Linguagem:** Node.js (JavaScript) – sem frameworks externos, usando apenas módulos nativos.  

---

## 1️⃣ Estrutura de arquivos

```
user-register-csv/
│
├─ package.json            # Metadados do projeto + script de start
├─ registerUser.js         # Script principal que grava no CSV
├─ users.csv               # Arquivo de dados (gerado na primeira execução)
└─ README.md               # Como instalar e rodar
```

> **Obs:** Se você clonar ou copiar apenas o `registerUser.js`, o `package.json` e o `README.md` são opcionais – eles servem apenas para facilitar a instalação das dependências (nenhuma, na verdade) e para deixar o passo‑a‑passo bem claro.

---

## 2️⃣ Código fonte

### 📄 **package.json**

```json
{
  "name": "user-register-csv",
  "version": "1.0.0",
  "description": "Script simples que registra nome e data de cadastro em um arquivo CSV.",
  "main": "registerUser.js",
  "scripts": {
    "start": "node registerUser.js"
  },
  "author": "Seu Nome <seu@email.com>",
  "license": "MIT"
}
```

---

### 📄 **registerUser.js**

```javascript
#!/usr/bin/env node
/**
 * registerUser.js
 *
 * Script Node.js que recebe o nome de um usuário (via linha de comando ou stdin)
 * e grava uma linha no arquivo CSV "users.csv" contendo:
 *
 *   nome, data_de_cadastro
 *
 * Cada execução adiciona uma nova linha ao final do arquivo sem sobrescrever
 * o conteúdo existente.
 *
 * Uso:
 *   1) Passando o nome como argumento:
 *        node registerUser.js "Fulano da Silva"
 *
 *   2) Sem argumento – o script pergunta interativamente:
 *        node registerUser.js
 *
 * Dependências: nenhuma (usa apenas módulos nativos).
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

// Caminho absoluto para o CSV (cria na pasta do script)
const CSV_FILE = path.join(__dirname, 'users.csv');

/**
 * Formata a data atual no padrão ISO (YYYY-MM-DD HH:MM:SS)
 */
function getCurrentTimestamp() {
  const now = new Date();
  const pad = (n) => n.toString().padStart(2, '0');

  const year = now.getFullYear();
  const month = pad(now.getMonth() + 1);
  const day = pad(now.getDate());
  const hour = pad(now.getHours());
  const minute = pad(now.getMinutes());
  const second = pad(now.getSeconds());

  return `${year}-${month}-${day} ${hour}:${minute}:${second}`;
}

/**
 * Escapa aspas e vírgulas caso o nome contenha esses caracteres.
 * CSV simples: coloca o campo entre aspas duplas e duplica aspas internas.
 */
function escapeCsvField(field) {
  const escaped = String(field).replace(/"/g, '""');
  return `"${escaped}"`;
}

/**
 * Grava uma linha no CSV. Cria o arquivo caso ainda não exista.
 * @param {string} name - Nome do usuário.
 */
function appendToCsv(name) {
  const timestamp = getCurrentTimestamp();
  const line = `${escapeCsvField(name)},${escapeCsvField(timestamp)}\n`;

  // O flag 'a' abre o arquivo para escrita no final, criando-o se necessário.
  fs.writeFileSync(CSV_FILE, line, { flag: 'a', encoding: 'utf8' });
  console.log(`✅ Usuário "${name}" registrado em ${CSV_FILE}`);
}

/**
 * Obtém o nome do usuário:
 *   - Se houver argumento na linha de comando, usa-o.
 *   - Caso contrário, pergunta via stdin.
 */
function obtainUserName() {
  const argName = process.argv.slice(2).join(' ').trim();
  if (argName) {
    return Promise.resolve(argName);
  }

  // Pergunta interativamente
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  return new Promise((resolve) => {
    rl.question('Informe o nome do usuário: ', (answer) => {
      rl.close();
      resolve(answer.trim());
    });
  });
}

/* -------------------  Execução principal  ------------------- */
(async () => {
  try {
    const name = await obtainUserName();

    if (!name) {
      console.error('⚠️  Nome vazio. Nada a fazer.');
      process.exit(1);
    }

    appendToCsv(name);
  } catch (err) {
    console.error('❌ Erro inesperado:', err);
    process.exit(1);
  }
})();
```

---

### 📄 **README.md**

```markdown
# Registro de Usuários em CSV

Pequeno script Node.js que adiciona **nome** e **data de cadastro** a um
arquivo `users.csv`. Cada execução acrescenta uma linha ao final do arquivo,
preservando os registros anteriores.

## Requisitos

- Node.js ≥ 12 (qualquer versão LTS atual funciona)
- Nenhuma dependência externa – usa somente módulos nativos.

## Instalação

```bash
# 1️⃣ Clone o repositório ou copie os arquivos para um diretório
git clone https://github.com/seu-usuario/user-register-csv.git
cd user-register-csv

# 2️⃣ Instale (na verdade só cria o node_modules, mas não há pacotes)
npm install   # opcional, não há dependências reais
```

## Como usar

### 1️⃣ Passando o nome como argumento

```bash
node registerUser.js "Maria Oliveira"
```

### 2️⃣ Interativo (sem argumentos)

```bash
node registerUser.js
# → O script pedirá: "Informe o nome do usuário: "
```

### 3️⃣ Atalho via npm script

```bash
npm start -- "João da Silva"
# ou simplesmente
npm start
```

## Onde os dados ficam?

O arquivo `users.csv` será criado (ou usado, se já existir) no mesmo diretório
do script. O conteúdo tem o seguinte formato:

```
"Nome do Usuário","YYYY-MM-DD HH:MM:SS"
```

Exemplo:

```
"Maria Oliveira","2026-08-31 14:22:07"
"João da Silva","2026-08-31 14:23:12"
```

## Licença

MIT – sinta‑se à vontade para adaptar e distribuir.
```

---

## 3️⃣ Como executar passo a passo (caso você só tenha o `registerUser.js`)

1. **Crie a pasta e copie o script**

   ```bash
   mkdir user-register-csv
   cd user-register-csv
   # cole o conteúdo de registerUser.js em um arquivo com esse nome
   ```

2. **Torne o script executável (opcional)**

   ```bash
   chmod +x registerUser.js
   ```

3. **Execute**

   - Com argumento:

     ```bash
     node registerUser.js "Ana Pereira"
     ```

   - Interativamente:

     ```bash
     node registerUser.js
     # depois digite o nome quando solicitado
     ```

4. **Verifique o CSV**

   ```bash
   cat users.csv
   ```

Pronto! Cada chamada ao script adiciona uma nova linha ao `users.csv` sem sobrescrever os dados anteriores. 🚀