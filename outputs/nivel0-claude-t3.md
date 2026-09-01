<!--
nivel: 0 - Persistencia simples
provider: claude
model: claude-sonnet-5
tentativa: 3
temperature: 0.2
timestamp: 2026-08-31T08:38:41.346Z
metadata: {"model":"claude-sonnet-5","usage":{"input_tokens":323,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"cache_creation":{"ephemeral_5m_input_tokens":0,"ephemeral_1h_input_tokens":0},"output_tokens":4161,"output_tokens_details":{"thinking_tokens":357},"service_tier":"standard","inference_geo":"global"},"stop_reason":"end_turn"}
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

Vou implementar um script Node.js que usa **apenas módulos nativos** (`fs`, `path`, `readline`), sem dependências externas, conforme solicitado.

## Decisões de projeto (documentadas também no código)

1. **Sem dependências externas**: uso `fs` para manipular arquivos e `readline` para ler entrada do usuário via terminal — ambos nativos do Node.js.
2. **Entrada do nome**: o script aceita o nome como argumento de linha de comando (`node registrarUsuario.js "João Silva"`) **ou**, se nenhum argumento for passado, pergunta interativamente via terminal.
3. **Persistência sem sobrescrever**: uso `fs.appendFileSync` (ou `fs.promises.appendFile`), que sempre adiciona ao final do arquivo, nunca sobrescreve.
4. **Cabeçalho do CSV**: se o arquivo ainda não existir, o script cria o arquivo com o cabeçalho `nome,data_cadastro` antes de inserir a primeira linha. Se já existir, apenas adiciona a nova linha.
5. **Formato da data**: uso `new Date().toISOString()` (padrão ISO 8601, ex: `2024-05-20T14:30:00.000Z`) por ser um formato não ambíguo e ordenável.
6. **Escape de CSV**: nomes que contenham vírgulas, aspas ou quebras de linha são colocados entre aspas duplas (com aspas internas duplicadas), seguindo a especificação RFC 4180, para evitar corromper o CSV.
7. **Local do arquivo**: `usuarios.csv` é criado no mesmo diretório do script (pode ser customizado via variável de ambiente `CSV_FILE`).

---

### `package.json`

```json
{
  "name": "registro-usuarios-csv",
  "version": "1.0.0",
  "description": "Script simples para registrar nome de usuario e data de cadastro em um arquivo CSV, sem sobrescrever registros anteriores.",
  "main": "registrarUsuario.js",
  "type": "commonjs",
  "scripts": {
    "start": "node registrarUsuario.js"
  },
  "engines": {
    "node": ">=14.0.0"
  },
  "license": "MIT"
}
```

---

### `registrarUsuario.js`

```javascript
#!/usr/bin/env node

/**
 * Script: registrarUsuario.js
 *
 * Objetivo:
 *   Registrar o nome de um usuario em um arquivo CSV (nome, data de cadastro).
 *   Cada execucao adiciona uma nova linha ao final do arquivo, sem apagar
 *   os registros anteriores.
 *
 * Decisoes de implementacao (ver README.md para mais detalhes):
 *   - Apenas modulos nativos do Node.js sao utilizados (fs, path, readline).
 *   - O nome pode ser passado como argumento de linha de comando; caso
 *     contrario, o script pergunta interativamente via terminal.
 *   - O arquivo CSV e criado com cabecalho na primeira execucao. Nas
 *     execucoes seguintes, apenas novas linhas sao anexadas (fs.appendFile).
 *   - A data de cadastro e gravada em formato ISO 8601 (UTC).
 *   - Valores sao escapados no padrao CSV (RFC 4180) para lidar com
 *     nomes contendo virgulas, aspas ou quebras de linha.
 *   - O caminho do arquivo CSV pode ser sobrescrito pela variavel de
 *     ambiente CSV_FILE; por padrao, usa "usuarios.csv" no diretorio
 *     do script.
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

// Caminho do arquivo CSV (customizavel via variavel de ambiente).
const CSV_FILE = process.env.CSV_FILE
  ? path.resolve(process.env.CSV_FILE)
  : path.join(__dirname, 'usuarios.csv');

const CSV_HEADER = 'nome,data_cadastro';

/**
 * Escapa um valor para uso seguro em um campo CSV (RFC 4180).
 * Se o valor contiver virgula, aspas duplas ou quebra de linha,
 * ele e envolvido em aspas duplas, e aspas internas sao duplicadas.
 */
function escaparCampoCSV(valor) {
  const precisaEscapar = /[",\n\r]/.test(valor);
  if (!precisaEscapar) {
    return valor;
  }
  const valorComAspasDuplicadas = valor.replace(/"/g, '""');
  return `"${valorComAspasDuplicadas}"`;
}

/**
 * Verifica se o arquivo CSV ja existe.
 */
function arquivoExiste(caminho) {
  try {
    fs.accessSync(caminho, fs.constants.F_OK);
    return true;
  } catch {
    return false;
  }
}

/**
 * Garante que o arquivo exista com o cabecalho correto.
 * Se o arquivo nao existir, cria com o cabecalho.
 */
function garantirArquivoComCabecalho() {
  if (!arquivoExiste(CSV_FILE)) {
    fs.writeFileSync(CSV_FILE, CSV_HEADER + '\n', { encoding: 'utf8' });
  }
}

/**
 * Adiciona uma nova linha (nome, data) ao final do arquivo CSV.
 * Usa appendFile, que nunca sobrescreve o conteudo existente.
 */
function registrarLinhaCSV(nome) {
  garantirArquivoComCabecalho();

  const dataCadastro = new Date().toISOString();
  const nomeEscapado = escaparCampoCSV(nome);
  const dataEscapada = escaparCampoCSV(dataCadastro);
  const linha = `${nomeEscapado},${dataEscapada}\n`;

  fs.appendFileSync(CSV_FILE, linha, { encoding: 'utf8' });

  console.log('Usuario registrado com sucesso!');
  console.log(`  Nome: ${nome}`);
  console.log(`  Data de cadastro: ${dataCadastro}`);
  console.log(`  Arquivo: ${CSV_FILE}`);
}

/**
 * Solicita o nome do usuario interativamente via terminal.
 */
function perguntarNome() {
  return new Promise((resolve) => {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    });

    rl.question('Digite o nome do usuario: ', (resposta) => {
      rl.close();
      resolve(resposta.trim());
    });
  });
}

/**
 * Funcao principal.
 */
async function main() {
  // Pega o nome a partir dos argumentos de linha de comando (ignorando
  // "node" e o nome do script). Ex: node registrarUsuario.js "Maria Silva"
  const argumentos = process.argv.slice(2);
  let nome = argumentos.join(' ').trim();

  if (!nome) {
    nome = await perguntarNome();
  }

  if (!nome) {
    console.error('Erro: nome do usuario nao pode ser vazio.');
    process.exitCode = 1;
    return;
  }

  try {
    registrarLinhaCSV(nome);
  } catch (erro) {
    console.error('Erro ao registrar usuario no arquivo CSV:', erro.message);
    process.exitCode = 1;
  }
}

main();
```

---

### `README.md`

```markdown
# Registro de Usuarios em CSV

Script simples em Node.js que registra o nome de um usuario e a data de
cadastro em um arquivo CSV (`usuarios.csv`). Cada execucao adiciona uma
nova linha ao arquivo, sem apagar os registros anteriores.

## Requisitos

- Node.js versao 14 ou superior (nenhuma dependencia externa e necessaria).

## Instalacao

Nao ha dependencias para instalar (o script usa apenas modulos nativos
do Node.js: `fs`, `path` e `readline`).

Se desejar, ainda assim rode o `npm install` para gerar a estrutura
padrao do projeto (nao ha pacotes a serem baixados):

\`\`\`bash
npm install
\`\`\`

## Como executar

### Opcao 1: Passando o nome como argumento

\`\`\`bash
node registrarUsuario.js "Joao da Silva"
\`\`\`

### Opcao 2: Modo interativo (sem argumento)

\`\`\`bash
node registrarUsuario.js
\`\`\`

O script vai perguntar:

\`\`\`
Digite o nome do usuario:
\`\`\`

Basta digitar o nome e pressionar Enter.

### Usando npm script

\`\`\`bash
npm start -- "Maria Souza"
\`\`\`

## Resultado

Cada execucao adiciona uma linha ao arquivo `usuarios.csv`, criado no
mesmo diretorio do script. Exemplo de conteudo apos 3 execucoes:

\`\`\`csv
nome,data_cadastro
Joao da Silva,2024-05-20T14:30:00.000Z
Maria Souza,2024-05-20T14:31:12.000Z
"Ana, Paula",2024-05-20T14:32:05.000Z
\`\`\`

Note que nomes contendo virgulas ou aspas sao automaticamente escapados
no formato padrao CSV (RFC 4180).

## Customizando o caminho do arquivo CSV

Por padrao, o arquivo e criado como `usuarios.csv` no diretorio do
script. Para usar outro caminho, defina a variavel de ambiente
`CSV_FILE`:

\`\`\`bash
CSV_FILE=./dados/meus_usuarios.csv node registrarUsuario.js "Carlos"
\`\`\`

## Testando multiplas execucoes

\`\`\`bash
node registrarUsuario.js "Usuario 1"
node registrarUsuario.js "Usuario 2"
node registrarUsuario.js "Usuario 3"
cat usuarios.csv
\`\`\`

Voce vera as tres linhas no arquivo, uma abaixo da outra, confirmando
que nenhuma execucao sobrescreve as anteriores.
```

---

## Resumo de uso rápido

```bash
# Não é necessário instalar nada (só módulos nativos do Node.js)
node registrarUsuario.js "Nome do Usuário"

# ou modo interativo
node registrarUsuario.js
```

O arquivo `usuarios.csv` será criado (se não existir) e cada execução adiciona uma nova linha ao final, preservando o histórico completo de cadastros.