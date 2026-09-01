<!--
nivel: 0 - Persistencia simples
provider: groq
model: openai/gpt-oss-120b
tentativa: 2
temperature: 0.2
timestamp: 2026-08-27T18:56:11.275Z
metadata: {"model":"openai/gpt-oss-120b","usage":{"queue_time":0.214256729,"prompt_tokens":247,"prompt_time":0.014626315,"completion_tokens":1567,"completion_time":3.273438096,"total_tokens":1814,"total_time":3.288064411,"completion_tokens_details":{"reasoning_tokens":21}},"finish_reason":"stop"}
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

**Projeto:** `user‑register-csv`  
**Linguagem:** Node.js (JavaScript) – sem frameworks externos, apenas a API padrão do Node.

---

## 1️⃣ Estrutura de arquivos

```
user-register-csv/
│
├─ package.json          # informações do projeto e script de start
├─ index.js              # código principal que faz o registro
├─ users.csv             # (gerado na primeira execução) armazena os registros
└─ README.md             # instruções de instalação e uso
```

---

## 2️⃣ Código-fonte

### 📄 `package.json`
```json
{
  "name": "user-register-csv",
  "version": "1.0.0",
  "description": "Script simples para registrar nome de usuário e data de cadastro em um arquivo CSV.",
  "main": "index.js",
  "type": "commonjs",
  "scripts": {
    "start": "node index.js"
  },
  "author": "Seu Nome <seu@email.com>",
  "license": "MIT"
}
```

---

### 📄 `index.js`
```js
#!/usr/bin/env node

/**
 * user-register-csv
 * -----------------
 * Script que recebe o nome de um usuário via linha de comando,
 * grava no arquivo `users.csv` o nome e a data/hora de cadastro.
 *
 * Cada execução adiciona uma nova linha ao final do CSV,
 * sem sobrescrever o conteúdo existente.
 *
 * Uso:
 *   node index.js "Nome Completo"
 *
 * Se nenhum nome for informado, o script exibirá um help simples.
 */

const fs = require('fs');
const path = require('path');

// Caminho absoluto para o arquivo CSV (na raiz do projeto)
const CSV_PATH = path.resolve(__dirname, 'users.csv');

// Função para formatar a data no padrão ISO (YYYY-MM-DD HH:MM:SS)
function getCurrentTimestamp() {
  const now = new Date();
  // Padroniza com dois dígitos
  const pad = (n) => n.toString().padStart(2, '0');

  const date = [
    now.getFullYear(),
    pad(now.getMonth() + 1),
    pad(now.getDate())
  ].join('-');

  const time = [
    pad(now.getHours()),
    pad(now.getMinutes()),
    pad(now.getSeconds())
  ].join(':');

  return `${date} ${time}`;
}

// Função principal
function main() {
  const args = process.argv.slice(2);

  // Se o usuário pedir ajuda ou não passar nome, exibe mensagem
  if (args.length === 0 || ['-h', '--help', 'help'].includes(args[0].toLowerCase())) {
    console.log('Uso: node index.js "Nome Completo"');
    console.log('Exemplo: node index.js "Ana Silva"');
    process.exit(0);
  }

  const userName = args[0].trim();

  if (userName.length === 0) {
    console.error('Erro: o nome do usuário não pode ser vazio.');
    process.exit(1);
  }

  const timestamp = getCurrentTimestamp();

  // Monta a linha CSV. Se o nome contiver vírgula, envolvemos entre aspas.
  const safeName = userName.includes(',') ? `"${userName.replace(/"/g, '""')}"` : userName;
  const line = `${safeName},${timestamp}\n`;

  // Garantimos que o diretório exista (no caso, a raiz já existe)
  // e então adicionamos ao arquivo usando modo 'a' (append).
  fs.appendFile(CSV_PATH, line, 'utf8', (err) => {
    if (err) {
      console.error('Falha ao gravar no CSV:', err);
      process.exit(1);
    } else {
      console.log(`Usuário "${userName}" registrado com sucesso em ${timestamp}.`);
    }
  });
}

// Executa a função principal
main();
```

> **Observação:** o script usa `fs.appendFile` (modo *append*) para garantir que
> nenhuma linha anterior seja sobrescrita. Caso o arquivo `users.csv` ainda não
> exista, ele será criado automaticamente na primeira execução.

---

### 📄 `README.md`
```markdown
# user-register-csv

Script Node.js que registra o nome de um usuário e a data/hora de cadastro
em um arquivo CSV (`users.csv`). Cada execução acrescenta uma nova linha,
preservando os registros anteriores.

## 📦 Pré‑requisitos

- **Node.js** (versão 14 ou superior).  
  Verifique com `node -v`. Caso ainda não tenha, baixe em https://nodejs.org/.

## 📥 Instalação

```bash
# Clone o repositório (ou copie a pasta para o seu ambiente)
git clone https://github.com/seu-usuario/user-register-csv.git
cd user-register-csv

# Instale as dependências (na verdade só o próprio Node, mas o comando cria o lockfile)
npm install
```

> Não há dependências externas; o `package.json` serve apenas para padronizar
> o comando `npm start`.

## ▶️ Como usar

```bash
# Forma geral:
node index.js "Nome Completo"

# Exemplo:
node index.js "Maria Oliveira"
```

O script criará (ou atualizará) o arquivo **users.csv** na raiz do projeto,
com o seguinte formato:

```
Nome,Data de cadastro
Maria Oliveira,2026-08-27 14:35:12
```

### Ajuda rápida

```bash
node index.js --help
```

## 📂 Arquivo gerado

- **users.csv** – contém todas as linhas adicionadas.  
  Se precisar abrir em planilha, basta importá‑lo como CSV padrão.

## 🛠️ Personalizações (opcional)

- **Separador:** se preferir outro delimitador, altere a constante `line` em `index.js`.
- **Formato de data:** a função `getCurrentTimestamp` pode ser adaptada para ISO 8601
  (`new Date().toISOString()`) ou outro padrão.

---

## ✅ Teste rápido

```bash
node index.js "Teste 1"
node index.js "Teste 2"
cat users.csv
```

Deve exibir algo como:

```
Teste 1,2026-08-27 15:01:03
Teste 2,2026-08-27 15:01:07
```

Pronto! 🎉
```

---

## 3️⃣ Instruções de execução resumidas

```bash
# 1. Instale o Node (se ainda não estiver instalado)
# 2. Baixe o projeto
git clone https://github.com/seu-usuario/user-register-csv.git
cd user-register-csv

# 3. Instale dependências (nenhuma além do Node)
npm install

# 4. Registre um usuário
node index.js "João da Silva"

# 5. Verifique o CSV
cat users.csv
```

O script está pronto para ser usado em qualquer ambiente que possua Node.js. Boa codificação!