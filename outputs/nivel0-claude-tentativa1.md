<!--
nivel: 0 - Persistencia simples
provider: claude
model: claude-sonnet-5
tentativa: 1
temperature: 0.2
timestamp: 2026-08-18T16:48:20.275Z
metadata: {"model":"claude-sonnet-5","usage":{"input_tokens":323,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"cache_creation":{"ephemeral_5m_input_tokens":0,"ephemeral_1h_input_tokens":0},"output_tokens":3547,"output_tokens_details":{"thinking_tokens":408},"service_tier":"standard","inference_geo":"global"},"stop_reason":"end_turn"}
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

# Solução

Abaixo está a implementação completa. Decisões de projeto (documentadas também nos comentários do código):

1. **Sem dependências externas** — uso apenas dos módulos nativos do Node.js (`fs`, `path`, `readline`), já que a tarefa é simples e não justifica bibliotecas como `csv-writer` ou `commander`.
2. **Dois modos de uso**: o nome pode ser passado como argumento de linha de comando (`node register.js "João Silva"`) ou, se omitido, o script pergunta interativamente via `readline`. Isso torna o script utilizável tanto em scripts automatizados quanto manualmente.
3. **Escrita incremental (append)**: uso `fs.appendFile` para garantir que cada execução apenas adicione uma linha, nunca sobrescrevendo o arquivo.
4. **Cabeçalho criado apenas uma vez**: antes de escrever, verifico se o arquivo já existe; se não existir, escrevo primeiro a linha de cabeçalho (`nome,data_cadastro`).
5. **Escape de CSV**: nomes com vírgula, aspas ou quebra de linha são tratados conforme a RFC 4180 (colocados entre aspas duplas, com aspas internas duplicadas), evitando corromper o CSV.
6. **Data em formato ISO 8601** (`new Date().toISOString()`), por ser um padrão não ambíguo e fácil de ordenar/parsear depois.
7. **Validação básica**: nome vazio é rejeitado, com o script pedindo novamente (modo interativo) ou encerrando com erro (modo CLI).

---

### Arquivo: `package.json`

```json
{
  "name": "registro-usuario-csv",
  "version": "1.0.0",
  "description": "Script CLI para registrar nome e data de cadastro de usuarios em um arquivo CSV, adicionando uma linha por execucao sem sobrescrever o arquivo.",
  "main": "register.js",
  "scripts": {
    "start": "node register.js"
  },
  "license": "MIT",
  "author": "",
  "engines": {
    "node": ">=14.0.0"
  }
}
```

---

### Arquivo: `register.js`

```javascript
#!/usr/bin/env node

/**
 * register.js
 * -----------
 * Script para registrar o nome de um usuario em um arquivo CSV,
 * junto com a data/hora de cadastro.
 *
 * Decisoes de design:
 * - Apenas modulos nativos do Node.js sao usados (fs, path, readline).
 * - Cada execucao ADICIONA uma nova linha (fs.appendFile), nunca sobrescreve
 *   o arquivo existente.
 * - O cabecalho "nome,data_cadastro" e escrito apenas na primeira execucao
 *   (quando o arquivo ainda nao existe).
 * - O nome pode ser passado via argumento de linha de comando:
 *       node register.js "Nome do Usuario"
 *   ou, se omitido, o script pergunta interativamente.
 * - Valores sao escapados no formato CSV (RFC 4180) para suportar nomes
 *   contendo virgulas, aspas ou quebras de linha.
 * - A data e gravada em formato ISO 8601 (UTC), por ser padrao e facil
 *   de ordenar/interpretar posteriormente.
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

// Caminho do arquivo CSV (na mesma pasta do script).
// Pode ser sobrescrito pela variavel de ambiente CSV_FILE, se desejado.
const CSV_FILE = process.env.CSV_FILE || path.join(__dirname, 'usuarios.csv');

const CSV_HEADER = 'nome,data_cadastro';

/**
 * Escapa um valor para uso seguro em um campo CSV (RFC 4180).
 * Se o valor contiver virgula, aspas duplas ou quebra de linha,
 * ele e envolvido em aspas duplas, com aspas internas duplicadas.
 */
function escapeCsvField(value) {
  const str = String(value);
  if (/[",\n\r]/.test(str)) {
    return `"${str.replace(/"/g, '""')}"`;
  }
  return str;
}

/**
 * Garante que o arquivo CSV exista com o cabecalho correto.
 * Se o arquivo ja existir, nao faz nada (evita sobrescrever dados).
 */
function ensureFileWithHeader(filePath) {
  if (!fs.existsSync(filePath)) {
    fs.writeFileSync(filePath, CSV_HEADER + '\n', { encoding: 'utf8' });
  }
}

/**
 * Adiciona uma linha (nome, data) ao arquivo CSV.
 */
function appendUserToCsv(nome, filePath) {
  ensureFileWithHeader(filePath);

  const dataCadastro = new Date().toISOString();
  const linha = `${escapeCsvField(nome)},${escapeCsvField(dataCadastro)}\n`;

  fs.appendFileSync(filePath, linha, { encoding: 'utf8' });

  console.log(`Usuario registrado com sucesso!`);
  console.log(`  Nome: ${nome}`);
  console.log(`  Data: ${dataCadastro}`);
  console.log(`  Arquivo: ${filePath}`);
}

/**
 * Solicita o nome interativamente via terminal.
 */
function perguntarNome(callback) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  rl.question('Digite o nome do usuario: ', (resposta) => {
    rl.close();
    callback(resposta.trim());
  });
}

function main() {
  // Nome pode vir como argumento de linha de comando (todos os args juntos,
  // permitindo nomes com espaco sem precisar escapar aspas em todo shell).
  const argNome = process.argv.slice(2).join(' ').trim();

  if (argNome) {
    if (argNome.length === 0) {
      console.error('Erro: o nome informado esta vazio.');
      process.exit(1);
    }
    appendUserToCsv(argNome, CSV_FILE);
    return;
  }

  // Modo interativo: pergunta o nome e valida que nao esta vazio.
  const tentarPerguntar = () => {
    perguntarNome((nome) => {
      if (!nome) {
        console.log('Nome nao pode ser vazio. Tente novamente.');
        tentarPerguntar();
        return;
      }
      appendUserToCsv(nome, CSV_FILE);
    });
  };

  tentarPerguntar();
}

main();
```

---

### Arquivo: `README.md`

```markdown
# Registro de Usuario em CSV

Script Node.js que registra o nome de um usuario e a data de cadastro
em um arquivo CSV (`usuarios.csv`). Cada execucao adiciona uma nova
linha, sem sobrescrever os registros anteriores.

## Requisitos

- Node.js >= 14 (nao ha dependencias externas a instalar).

## Instalacao

Nao ha dependencias de terceiros. Basta ter o Node.js instalado.
Opcionalmente, rode:

```bash
npm install
```

(nao instalara nada, apenas valida o `package.json`).

## Como executar

### Modo 1: Interativo (o script pergunta o nome)

```bash
node register.js
```

Sera exibido o prompt:

```
Digite o nome do usuario:
```

### Modo 2: Passando o nome via argumento

```bash
node register.js "Maria da Silva"
```

## Resultado

Cada execucao adiciona uma linha ao arquivo `usuarios.csv`
(criado automaticamente na primeira execucao, na mesma pasta do script):

```csv
nome,data_cadastro
Joao Silva,2024-05-20T14:32:10.123Z
Maria da Silva,2024-05-20T14:33:02.456Z
```

## Observacoes

- O arquivo CSV padrao e `usuarios.csv`, na mesma pasta do script.
  Para usar outro caminho/arquivo, defina a variavel de ambiente
  `CSV_FILE`:

  ```bash
  CSV_FILE=./dados/meus_usuarios.csv node register.js "Ana"
  ```

- Nomes contendo virgulas, aspas ou quebras de linha sao
  automaticamente escapados no formato CSV padrao (RFC 4180).
- A data e gravada em UTC, no formato ISO 8601.
```

---

## Resumo de execução

```bash
# 1. Extraia os arquivos em uma pasta
# 2. Rode:
node register.js "Nome do Usuario"
# ou
node register.js
# (e digite o nome quando solicitado)

# 3. Verifique o resultado:
cat usuarios.csv
```