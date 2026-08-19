<!--
nivel: 0 - Persistencia simples
provider: claude
model: claude-sonnet-5
tentativa: 2
temperature: 0.2
timestamp: 2026-08-18T16:48:55.856Z
metadata: {"model":"claude-sonnet-5","usage":{"input_tokens":323,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"cache_creation":{"ephemeral_5m_input_tokens":0,"ephemeral_1h_input_tokens":0},"output_tokens":3692,"output_tokens_details":{"thinking_tokens":408},"service_tier":"standard","inference_geo":"global"},"stop_reason":"end_turn"}
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

Vou implementar um script Node.js usando **apenas módulos nativos** (`fs`, `path`, `readline`), sem dependências externas, conforme solicitado.

## Decisões de design (documentadas também no código):

1. **Nome via argumento CLI ou modo interativo**: o script aceita o nome como argumento (`node registrar_usuario.js "João Silva"`) para uso rápido/scriptável, mas se nenhum argumento for passado, pergunta interativamente via `readline`.
2. **Cabeçalho criado apenas na primeira execução**: verificamos se o arquivo já existe antes de escrever o cabeçalho, evitando duplicá-lo.
3. **Modo de escrita = append (`fs.appendFileSync`)**: garante que execuções sucessivas apenas adicionem linhas, nunca sobrescrevem.
4. **Escaping CSV básico**: se o nome contiver vírgula, aspas ou quebra de linha, ele é encapsulado em aspas duplas (regra padrão RFC 4180) para não corromper o CSV.
5. **Data no formato ISO 8601** (`new Date().toISOString()`): evita ambiguidade de fuso/formato e é facilmente parseável depois.
6. **Validação de entrada**: nome vazio é rejeitado com mensagem de erro clara.

---

### `package.json`

```json
{
  "name": "registro-usuario-csv",
  "version": "1.0.0",
  "description": "Script simples para registrar nome e data de cadastro em um arquivo CSV, sem sobrescrever registros anteriores.",
  "main": "registrar_usuario.js",
  "scripts": {
    "start": "node registrar_usuario.js"
  },
  "license": "MIT"
}
```

---

### `registrar_usuario.js`

```javascript
#!/usr/bin/env node

/**
 * registrar_usuario.js
 * ---------------------
 * Script para registrar o nome de um usuário em um arquivo CSV
 * (colunas: nome, data_cadastro), sem sobrescrever registros
 * já existentes.
 *
 * Uso:
 *   node registrar_usuario.js "Nome do Usuario"
 *   node registrar_usuario.js            (modo interativo, pede o nome)
 *
 * Decisões de implementação:
 * - Apenas módulos nativos do Node.js (fs, path, readline) são usados,
 *   sem dependências externas (conforme restrição do projeto).
 * - O arquivo CSV é criado com cabeçalho apenas se ainda não existir.
 * - Cada execução usa fs.appendFileSync, que sempre adiciona ao final
 *   do arquivo, garantindo que registros anteriores não sejam perdidos.
 * - Data registrada em formato ISO 8601 (UTC), por ser um padrão
 *   universal e fácil de ordenar/parsear posteriormente.
 * - Valores do CSV são "escapados" seguindo a convenção RFC 4180:
 *   se contiverem vírgula, aspas ou quebra de linha, são envolvidos
 *   em aspas duplas (e aspas internas são duplicadas).
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

// Caminho do arquivo CSV (mesmo diretório do script)
const CSV_PATH = path.join(__dirname, 'usuarios.csv');
const CSV_HEADER = 'nome,data_cadastro';

/**
 * Escapa um valor para uso seguro em uma linha CSV,
 * seguindo a convenção RFC 4180.
 * @param {string} value
 * @returns {string}
 */
function escapeCsvValue(value) {
  const strValue = String(value);
  const precisaEscapar = /[",\n\r]/.test(strValue);

  if (!precisaEscapar) {
    return strValue;
  }

  // Duplica aspas internas e envolve o valor inteiro em aspas duplas
  const escapado = strValue.replace(/"/g, '""');
  return `"${escapado}"`;
}

/**
 * Garante que o arquivo CSV exista com o cabeçalho correto.
 * Só escreve o cabeçalho se o arquivo ainda não existir,
 * para não duplicá-lo em execuções subsequentes.
 */
function garantirArquivoComCabecalho() {
  if (!fs.existsSync(CSV_PATH)) {
    fs.writeFileSync(CSV_PATH, CSV_HEADER + '\n', { encoding: 'utf8' });
  }
}

/**
 * Adiciona uma nova linha ao CSV com o nome informado e a data atual.
 * Usa appendFileSync para garantir que o conteúdo anterior seja preservado.
 * @param {string} nome
 */
function registrarUsuario(nome) {
  const nomeLimpo = nome.trim();

  if (nomeLimpo.length === 0) {
    console.error('Erro: o nome não pode ser vazio.');
    process.exit(1);
  }

  garantirArquivoComCabecalho();

  const dataCadastro = new Date().toISOString();
  const linha = `${escapeCsvValue(nomeLimpo)},${escapeCsvValue(dataCadastro)}\n`;

  fs.appendFileSync(CSV_PATH, linha, { encoding: 'utf8' });

  console.log(`✔ Usuário registrado com sucesso!`);
  console.log(`  Nome: ${nomeLimpo}`);
  console.log(`  Data: ${dataCadastro}`);
  console.log(`  Arquivo: ${CSV_PATH}`);
}

/**
 * Solicita o nome do usuário via terminal (modo interativo),
 * usado quando nenhum argumento é passado na linha de comando.
 */
function pedirNomeInterativamente() {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  rl.question('Digite o nome do usuário: ', (nome) => {
    rl.close();
    registrarUsuario(nome);
  });
}

// --- Ponto de entrada do script ---
function main() {
  // Argumentos após "node registrar_usuario.js"
  const args = process.argv.slice(2);

  if (args.length > 0) {
    // Junta todos os argumentos em caso de nome passado sem aspas
    // (ex: node registrar_usuario.js Joao Silva -> "Joao Silva")
    const nome = args.join(' ');
    registrarUsuario(nome);
  } else {
    pedirNomeInterativamente();
  }
}

main();
```

---

### `README.md`

```markdown
# Registro de Usuário em CSV

Script Node.js simples que registra o **nome** e a **data de cadastro** de um
usuário em um arquivo CSV (`usuarios.csv`), sem sobrescrever registros
anteriores a cada nova execução.

## Requisitos

- Node.js (versão 12 ou superior) — não é necessário instalar nenhuma
  dependência externa, o script usa apenas módulos nativos do Node.js
  (`fs`, `path`, `readline`).

## Instalação

Nenhuma instalação de dependências é necessária. Basta ter o Node.js
instalado. Opcionalmente, rode:

\`\`\`bash
npm install
\`\`\`

(o comando acima não instalará nada, pois não há dependências declaradas,
mas valida o `package.json`).

## Como executar

### Opção 1: passando o nome como argumento

\`\`\`bash
node registrar_usuario.js "Maria da Silva"
\`\`\`

### Opção 2: modo interativo (o script pergunta o nome)

\`\`\`bash
node registrar_usuario.js
\`\`\`

O terminal exibirá:

\`\`\`
Digite o nome do usuário: _
\`\`\`

Digite o nome e pressione Enter.

## Resultado

Cada execução adiciona uma nova linha ao arquivo `usuarios.csv`
(criado automaticamente no mesmo diretório do script, caso não exista):

\`\`\`csv
nome,data_cadastro
Maria da Silva,2024-05-20T14:32:10.123Z
João Pereira,2024-05-20T14:35:02.456Z
```

Rodar o script múltiplas vezes **não apaga** os registros anteriores —
cada execução apenas acrescenta uma nova linha ao final do arquivo.

## Observações técnicas

- A data é registrada em formato **ISO 8601 (UTC)**, garantindo um padrão
  consistente e fácil de ordenar/converter posteriormente.
- Nomes contendo vírgulas, aspas ou quebras de linha são automaticamente
  escapados segundo a convenção **RFC 4180** para arquivos CSV.
- Se nenhum argumento for passado, o script solicita o nome
  interativamente via terminal.
```

---

## Resumo de execução rápida

```bash
# 1. Certifique-se de ter o Node.js instalado
node --version

# 2. Rode o script (sem precisar instalar nada)
node registrar_usuario.js "Seu Nome Aqui"

# 3. Rode novamente para confirmar que adiciona uma nova linha
node registrar_usuario.js "Outro Nome"

# 4. Verifique o resultado
cat usuarios.csv
```