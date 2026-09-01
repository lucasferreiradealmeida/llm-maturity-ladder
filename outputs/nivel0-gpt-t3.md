<!--
nivel: 0 - Persistencia simples
provider: gpt
model: gpt-5.6
tentativa: 3
temperature: 0.2
timestamp: 2026-08-31T08:19:35.429Z
metadata: {"model":"gpt-5.6-sol","usage":{"prompt_tokens":182,"completion_tokens":1507,"total_tokens":1689,"prompt_tokens_details":{"cached_tokens":0,"cache_write_tokens":0,"audio_tokens":0},"completion_tokens_details":{"reasoning_tokens":512,"audio_tokens":0,"accepted_prediction_tokens":0,"rejected_prediction_tokens":0}},"finish_reason":"stop"}
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

A implementação abaixo usa apenas módulos nativos do Node.js. O nome pode ser fornecido como argumento ou digitado interativamente. Os registros são adicionados ao arquivo `usuarios.csv`, preservando os anteriores.

### `package.json`

```json
{
  "name": "cadastro-usuarios-csv",
  "version": "1.0.0",
  "private": true,
  "description": "Script para registrar usuários em um arquivo CSV",
  "main": "cadastro.js",
  "scripts": {
    "start": "node cadastro.js"
  },
  "engines": {
    "node": ">=18"
  }
}
```

### `cadastro.js`

```javascript
'use strict';

const fs = require('node:fs/promises');
const path = require('node:path');
const readline = require('node:readline/promises');
const { stdin, stdout } = require('node:process');

// Decisão assumida: o CSV fica no mesmo diretório deste script,
// independentemente do diretório a partir do qual ele for executado.
const CAMINHO_CSV = path.join(__dirname, 'usuarios.csv');
const CABECALHO_CSV = 'nome,data_de_cadastro\n';

/**
 * Escapa um valor de acordo com o formato CSV.
 * Aspas internas são duplicadas e o valor é colocado entre aspas.
 * Isso permite registrar nomes com vírgulas, aspas ou quebras de linha.
 */
function escaparValorCsv(valor) {
  return `"${String(valor).replace(/"/g, '""')}"`;
}

async function obterNome() {
  // Permite executar, por exemplo:
  // node cadastro.js "Maria da Silva"
  const nomeInformadoPorArgumento = process.argv.slice(2).join(' ').trim();

  if (nomeInformadoPorArgumento) {
    return nomeInformadoPorArgumento;
  }

  // Quando nenhum argumento é informado, solicita o nome interativamente.
  const interfaceLeitura = readline.createInterface({
    input: stdin,
    output: stdout
  });

  try {
    return (await interfaceLeitura.question('Digite o nome do usuário: ')).trim();
  } finally {
    interfaceLeitura.close();
  }
}

async function registrarUsuario(nome) {
  if (!nome) {
    throw new Error('O nome do usuário não pode estar vazio.');
  }

  // Decisão assumida: a data é armazenada no padrão ISO 8601 e em UTC,
  // evitando ambiguidades de formato e fuso horário.
  const dataCadastro = new Date().toISOString();

  const linhaCsv =
    `${escaparValorCsv(nome)},${escaparValorCsv(dataCadastro)}\n`;

  // O modo "a+" cria o arquivo se ele não existir e garante que toda escrita
  // seja feita no final, sem sobrescrever os registros anteriores.
  const arquivo = await fs.open(CAMINHO_CSV, 'a+');

  try {
    const informacoes = await arquivo.stat();

    // Adiciona o cabeçalho somente quando o arquivo é novo ou está vazio.
    const conteudo = informacoes.size === 0
      ? CABECALHO_CSV + linhaCsv
      : linhaCsv;

    await arquivo.appendFile(conteudo, 'utf8');
  } finally {
    await arquivo.close();
  }

  return dataCadastro;
}

async function executar() {
  try {
    const nome = await obterNome();
    const dataCadastro = await registrarUsuario(nome);

    console.log('Usuário cadastrado com sucesso.');
    console.log(`Nome: ${nome}`);
    console.log(`Data de cadastro: ${dataCadastro}`);
    console.log(`Arquivo: ${CAMINHO_CSV}`);
  } catch (erro) {
    console.error(`Erro: ${erro.message}`);
    process.exitCode = 1;
  }
}

executar();
```

## Como executar

Requisito: Node.js 18 ou superior.

Não há dependências externas para instalar. Opcionalmente, execute:

```bash
npm install
```

Informando o nome como argumento:

```bash
node cadastro.js "Maria da Silva"
```

Ou com o comando do `package.json`:

```bash
npm start -- "Maria da Silva"
```

Também é possível executar sem argumentos e informar o nome quando solicitado:

```bash
node cadastro.js
```

O arquivo `usuarios.csv` será criado automaticamente. Após múltiplas execuções, terá conteúdo semelhante a:

```csv
nome,data_de_cadastro
"Maria da Silva","2026-08-31T14:30:00.000Z"
"João Souza","2026-08-31T14:35:00.000Z"
```