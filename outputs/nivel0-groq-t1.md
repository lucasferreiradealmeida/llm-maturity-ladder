<!--
nivel: 0 - Persistencia simples
provider: groq
model: openai/gpt-oss-120b
tentativa: 1
temperature: 0.2
timestamp: 2026-08-27T18:56:05.472Z
metadata: {"model":"openai/gpt-oss-120b","usage":{"queue_time":0.196486376,"prompt_tokens":247,"prompt_time":0.069616711,"completion_tokens":1669,"completion_time":3.743012506,"total_tokens":1916,"total_time":3.812629217,"completion_tokens_details":{"reasoning_tokens":22}},"finish_reason":"stop"}
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

**Projeto:** `user‑register‑csv`  
**Linguagem:** Node.js (JavaScript)  
**Objetivo:** Script que recebe o nome de um usuário, grava `nome, data_de_cadastro` num arquivo **CSV** (`users.csv`). Cada execução do script adiciona uma nova linha, preservando os registros anteriores.

---

## Estrutura de arquivos

```
user-register-csv/
│
├─ package.json          # gerenciador de dependências
├─ index.js              # script principal
├─ .gitignore            # arquivos a ignorar no git (opcional)
└─ README.md             # instruções de uso
```

---  

## 1. `package.json`

```json
{
  "name": "user-register-csv",
  "version": "1.0.0",
  "description": "Script simples que grava nomes de usuários em um arquivo CSV (nome, data de cadastro).",
  "main": "index.js",
  "type": "commonjs",
  "scripts": {
    "start": "node index.js"
  },
  "author": "Seu Nome <seu@email.com>",
  "license": "MIT",
  "dependencies": {
    "prompt-sync": "^4.2.0"
  }
}
```

* **Por que `prompt-sync`?**  
  O Node não possui um método de leitura síncrona da linha de comando. `prompt-sync` é extremamente leve (≈ 2 KB) e nos permite solicitar o nome do usuário de forma interativa, sem precisar de frameworks maiores.

---  

## 2. `index.js`

```js
/**
 * index.js
 * ----------
 * Script que solicita o nome de um usuário e grava o registro
 * (nome, data de cadastro) em um arquivo CSV chamado "users.csv".
 *
 * Cada execução do script adiciona uma nova linha ao final do arquivo,
 * nunca sobrescrevendo os registros existentes.
 *
 * Como funciona:
 *   1. Lê o nome do usuário via prompt da linha de comando.
 *   2. Valida se o nome não está vazio.
 *   3. Gera a data atual no formato ISO (YYYY-MM-DD HH:mm:ss).
 *   4. Abre/Cria o arquivo "users.csv" em modo append e escreve a linha.
 *
 * Dependências:
 *   - prompt-sync : para leitura síncrona do stdin.
 *
 * Uso:
 *   $ npm install          # instala a dependência
 *   $ node index.js        # ou "npm start"
 *
 * O arquivo CSV será criado na mesma pasta do script, se ainda não existir.
 */

const fs = require('fs');
const path = require('path');
const prompt = require('prompt-sync')({ sigint: true }); // permite Ctrl+C

// ---------- Configurações ----------
const CSV_FILE = path.join(__dirname, 'users.csv');
// ---------------------------------------------------------

/**
 * Formata a data atual como string "YYYY-MM-DD HH:mm:ss".
 * @returns {string}
 */
function getCurrentTimestamp() {
  const now = new Date();

  const pad = (num) => String(num).padStart(2, '0');

  const year = now.getFullYear();
  const month = pad(now.getMonth() + 1); // months are 0-indexed
  const day = pad(now.getDate());

  const hour = pad(now.getHours());
  const minute = pad(now.getMinutes());
  const second = pad(now.getSeconds());

  return `${year}-${month}-${day} ${hour}:${minute}:${second}`;
}

/**
 * Escreve um registro no CSV. Cria o arquivo se ele não existir.
 * @param {string} name - Nome do usuário.
 */
function appendUserToCsv(name) {
  const timestamp = getCurrentTimestamp();

  // Escapa aspas e vírgulas que possam existir no nome
  const safeName = `"${name.replace(/"/g, '""')}"`;

  const line = `${safeName},${timestamp}\n`;

  // 'a' = append, cria o arquivo se não existir
  fs.appendFileSync(CSV_FILE, line, { encoding: 'utf8' });
}

/**
 * Função principal: solicita o nome e grava no CSV.
 */
function main() {
  console.log('=== Registro de Usuário ===\n');

  // Loop até receber um nome não vazio
  let name = '';
  while (!name.trim()) {
    name = prompt('Informe o nome do usuário: ').trim();
    if (!name) {
      console.log('⚠️  O nome não pode ser vazio. Tente novamente.\n');
    }
  }

  try {
    appendUserToCsv(name);
    console.log(`✅  Usuário "${name}" registrado com sucesso em "${CSV_FILE}".`);
  } catch (err) {
    console.error('❌  Erro ao gravar no arquivo CSV:', err.message);
    process.exit(1);
  }
}

// Executa apenas se o script for chamado diretamente
if (require.main === module) {
  main();
}
```

---  

## 3. `.gitignore` (opcional)

```gitignore
node_modules/
users.csv
```

*Ignora a pasta de dependências e o CSV gerado, caso você use controle de versão.*

---  

## 4. `README.md`

```markdown
# Registro de Usuário em CSV

Um script Node.js simples que permite registrar o nome de um usuário em um
arquivo `users.csv` com a data/hora do cadastro.

## Pré‑requisitos

- **Node.js** v14 ou superior (https://nodejs.org/)
- **npm** (vem com o Node)

## Instalação

```bash
# Clone ou copie o repositório
git clone <url-do-repositorio> user-register-csv
cd user-register-csv

# Instala a única dependência necessária
npm install
```

## Como usar

```bash
# Executa o script (pode ser repetido quantas vezes quiser)
node index.js
# ou
npm start
```

O script solicitará o nome do usuário. Após a confirmação, o registro será
adicionado ao final de `users.csv` no formato:

```
"Nome do Usuário",2026-08-27 14:32:10
```

Se o arquivo ainda não existir, ele será criado automaticamente.

## Arquivo CSV gerado

- **Local:** `./users.csv` (mesma pasta do script)  
- **Formato:** `nome,data_de_cadastro`  
- Cada linha corresponde a um registro; o script usa *append* para nunca
  sobrescrever dados já existentes.

## Licença

MIT – sinta‑se livre para adaptar e reutilizar.
```

---  

## Instruções de Execução (passo a passo)

1. **Instale o Node.js** (se ainda não estiver instalado).  
   ```bash
   # Verifique a versão
   node -v
   npm -v
   ```

2. **Baixe o projeto** (clone ou copie os arquivos acima para uma pasta, por
   exemplo `user-register-csv`).

3. **Instale a dependência**  
   ```bash
   cd user-register-csv
   npm install
   ```

4. **Rode o script**  
   ```bash
   node index.js          # ou npm start
   ```

5. **Resultado**  
   - Um arquivo `users.csv` aparecerá na mesma pasta.  
   - Cada execução adiciona uma nova linha; nenhum dado anterior é perdido.

---  

**Pronto!** Você tem um script completo, autocontido e pronto para rodar que cumpre
todos os requisitos da tarefa. 🚀