<!--
nivel: 0 - Persistencia simples
provider: gpt
model: gpt-5.6
tentativa: 1
temperature: 0.2
timestamp: 2026-08-18T16:49:30.996Z
metadata: {"model":"gpt-5.6-sol","usage":{"prompt_tokens":182,"completion_tokens":1502,"total_tokens":1684,"prompt_tokens_details":{"cached_tokens":0,"cache_write_tokens":0,"audio_tokens":0},"completion_tokens_details":{"reasoning_tokens":512,"audio_tokens":0,"accepted_prediction_tokens":0,"rejected_prediction_tokens":0}},"finish_reason":"stop"}
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

A implementação usa apenas módulos nativos do Node.js. O nome pode ser informado como argumento ou digitado interativamente. O arquivo `usuarios.csv` é criado no mesmo diretório do script e recebe novas linhas sem apagar os registros existentes.

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

// Decisão: o CSV será salvo no mesmo diretório deste script,
// independentemente do diretório a partir do qual ele for executado.
const CAMINHO_CSV = path.join(__dirname, 'usuarios.csv');
const CABECALHO = 'nome,data_cadastro\n';

/**
 * Escapa um valor conforme as regras comuns do formato CSV:
 * - o valor fica entre aspas;
 * - aspas internas são duplicadas.
 */
function escaparCampoCsv(valor) {
  return `"${String(valor).replace(/"/g, '""')}"`;
}

async function obterNome() {
  // Permite executar, por exemplo:
  // node cadastro.js "Maria da Silva"
  const nomePorArgumento = process.argv.slice(2).join(' ').trim();

  if (nomePorArgumento) {
    return nomePorArgumento;
  }

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

function validarNome(nome) {
  if (!nome) {
    throw new Error('O nome do usuário não pode ficar vazio.');
  }

  // Cada cadastro deve ocupar uma única linha física no arquivo.
  if (/[\r\n]/.test(nome)) {
    throw new Error('O nome não pode conter quebras de linha.');
  }
}

async function registrarUsuario(nome) {
  // A data é armazenada no padrão ISO 8601, em UTC, incluindo horário.
  const dataCadastro = new Date().toISOString();

  const linha = [
    escaparCampoCsv(nome),
    escaparCampoCsv(dataCadastro)
  ].join(',') + '\n';

  // O modo "a+" cria o arquivo se ele não existir e sempre escreve no final,
  // evitando que execuções posteriores sobrescrevam os cadastros anteriores.
  const arquivo = await fs.open(CAMINHO_CSV, 'a+');

  try {
    const informacoes = await arquivo.stat();

    // O cabeçalho é incluído apenas na criação de um arquivo vazio.
    const conteudo = informacoes.size === 0
      ? CABECALHO + linha
      : linha;

    await arquivo.appendFile(conteudo, 'utf8');
  } finally {
    await arquivo.close();
  }

  return dataCadastro;
}

async function main() {
  try {
    const nome = await obterNome();
    validarNome(nome);

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

main();
```

## Como executar

Requisito: Node.js 18 ou superior.

1. Salve `package.json` e `cadastro.js` no mesmo diretório.
2. Abra um terminal nesse diretório.
3. Não há dependências externas para instalar. Opcionalmente, execute:

```bash
npm install
```

4. Execute interativamente:

```bash
npm start
```

Ou informe o nome diretamente:

```bash
node cadastro.js "Maria da Silva"
```

Cada execução adicionará um registro ao arquivo `usuarios.csv`, por exemplo:

```csv
nome,data_cadastro
"Maria da Silva","2026-08-18T14:30:00.000Z"
"João Souza","2026-08-18T14:35:00.000Z"
```