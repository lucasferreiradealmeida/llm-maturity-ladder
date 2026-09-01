<!--
nivel: 0 - Persistencia simples
provider: gpt
model: gpt-5.6
tentativa: 2
temperature: 0.2
timestamp: 2026-08-18T16:51:02.619Z
metadata: {"model":"gpt-5.6-sol","usage":{"prompt_tokens":182,"completion_tokens":1826,"total_tokens":2008,"prompt_tokens_details":{"cached_tokens":0,"cache_write_tokens":0,"audio_tokens":0},"completion_tokens_details":{"reasoning_tokens":512,"audio_tokens":0,"accepted_prediction_tokens":0,"rejected_prediction_tokens":0}},"finish_reason":"stop"}
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

A solução usa apenas módulos nativos do Node.js. O nome pode ser informado como argumento ou digitado interativamente. O arquivo `cadastros.csv` é criado no mesmo diretório do script, e cada execução acrescenta um registro sem apagar os anteriores.

### `package.json`

```json
{
  "name": "cadastro-usuarios-csv",
  "version": "1.0.0",
  "private": true,
  "description": "Script Node.js para registrar usuários em um arquivo CSV.",
  "main": "cadastrar.js",
  "scripts": {
    "start": "node cadastrar.js"
  },
  "engines": {
    "node": ">=18"
  },
  "license": "UNLICENSED"
}
```

### `cadastrar.js`

```javascript
"use strict";

const fs = require("node:fs/promises");
const path = require("node:path");
const readline = require("node:readline/promises");
const { stdin, stdout } = require("node:process");

// Decisão: o CSV é sempre armazenado no mesmo diretório deste script,
// independentemente do diretório a partir do qual o comando é executado.
const CAMINHO_CSV = path.join(__dirname, "cadastros.csv");

/**
 * Prepara um valor para ser gravado em CSV.
 *
 * Os campos são sempre colocados entre aspas, e aspas internas são duplicadas,
 * conforme o formato CSV. Quebras de linha são substituídas por espaços para
 * garantir que cada cadastro ocupe exatamente uma linha no arquivo.
 */
function formatarCampoCsv(valor) {
  const valorNormalizado = String(valor)
    .replace(/\r\n|\r|\n/g, " ")
    .replace(/"/g, '""');

  return `"${valorNormalizado}"`;
}

/**
 * Obtém o nome pela linha de comando ou, caso não tenha sido informado,
 * solicita o valor interativamente.
 *
 * Exemplos:
 *   node cadastrar.js "Maria da Silva"
 *   node cadastrar.js
 */
async function obterNome() {
  const nomePelosArgumentos = process.argv.slice(2).join(" ").trim();

  if (nomePelosArgumentos) {
    return nomePelosArgumentos;
  }

  // Evita aguardar indefinidamente quando o script for executado em um
  // ambiente sem terminal interativo e sem um nome como argumento.
  if (!stdin.isTTY || !stdout.isTTY) {
    throw new Error(
      'Informe o nome como argumento. Exemplo: node cadastrar.js "Maria da Silva"'
    );
  }

  const interfaceLeitura = readline.createInterface({
    input: stdin,
    output: stdout
  });

  try {
    const resposta = await interfaceLeitura.question("Digite o nome do usuário: ");
    return resposta.trim();
  } finally {
    interfaceLeitura.close();
  }
}

/**
 * Adiciona um cadastro ao CSV sem sobrescrever o conteúdo existente.
 */
async function registrarUsuario(nome) {
  if (!nome) {
    throw new Error("O nome do usuário não pode estar vazio.");
  }

  // Decisão: a data é armazenada em ISO 8601 e UTC, evitando ambiguidades
  // de formato e fuso horário.
  const dataCadastro = new Date().toISOString();

  const cabecalho = `${formatarCampoCsv("nome")},${formatarCampoCsv(
    "data_de_cadastro"
  )}`;

  const novaLinha = `${formatarCampoCsv(nome)},${formatarCampoCsv(
    dataCadastro
  )}`;

  // "a+" cria o arquivo se ele não existir e garante que toda escrita seja
  // acrescentada ao final, sem substituir registros existentes.
  const arquivo = await fs.open(CAMINHO_CSV, "a+");

  try {
    const informacoes = await arquivo.stat();

    if (informacoes.size === 0) {
      // Arquivo novo ou vazio: grava o cabeçalho e o primeiro registro.
      await arquivo.appendFile(`${cabecalho}\n${novaLinha}\n`, "utf8");
      return dataCadastro;
    }

    // Se o arquivo tiver sido alterado manualmente e não terminar com uma
    // quebra de linha, adicionamos uma antes do novo registro.
    const ultimoByte = Buffer.alloc(1);
    await arquivo.read(ultimoByte, 0, 1, informacoes.size - 1);

    const terminaComQuebraDeLinha =
      ultimoByte[0] === 10 || // \n
      ultimoByte[0] === 13; // \r

    const prefixo = terminaComQuebraDeLinha ? "" : "\n";
    await arquivo.appendFile(`${prefixo}${novaLinha}\n`, "utf8");

    return dataCadastro;
  } finally {
    await arquivo.close();
  }
}

async function executar() {
  const nome = await obterNome();
  const dataCadastro = await registrarUsuario(nome);

  console.log("Usuário cadastrado com sucesso.");
  console.log(`Nome: ${nome}`);
  console.log(`Data de cadastro: ${dataCadastro}`);
  console.log(`Arquivo: ${CAMINHO_CSV}`);
}

executar().catch((erro) => {
  console.error(`Erro: ${erro.message}`);
  process.exitCode = 1;
});
```

## Como executar

1. Instale o [Node.js 18 ou superior](https://nodejs.org/).
2. Salve os arquivos `package.json` e `cadastrar.js` na mesma pasta.
3. Não é necessário instalar dependências externas.

Execute informando o nome diretamente:

```bash
node cadastrar.js "Maria da Silva"
```

Ou usando o comando do `package.json`:

```bash
npm start -- "Maria da Silva"
```

Também é possível executar de forma interativa:

```bash
node cadastrar.js
```

Cada execução acrescentará uma linha ao arquivo `cadastros.csv`, por exemplo:

```csv
"nome","data_de_cadastro"
"Maria da Silva","2026-08-18T14:30:00.000Z"
"João Souza","2026-08-18T14:35:00.000Z"
```