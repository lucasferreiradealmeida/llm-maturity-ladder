<!--
nivel: 0 - Persistencia simples
provider: gemini
model: gemini-3.1-pro-preview
tentativa: 3
temperature: 0.2
timestamp: 2026-08-31T08:44:48.137Z
metadata: {"model":"gemini-3.1-pro-preview","usage":{"promptTokenCount":193,"candidatesTokenCount":929,"totalTokenCount":2052,"promptTokensDetails":[{"modality":"TEXT","tokenCount":193}],"thoughtsTokenCount":930,"serviceTier":"standard"},"finish_reason":"STOP"}
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

Aqui está a solução completa para o seu problema. 

Como engenheiro de software, tomei as seguintes decisões de design (documentadas no código):
1. **Entrada de dados**: Optei por receber o nome do usuário via argumentos de linha de comando (CLI) para facilitar a automação e execução rápida.
2. **Formato da Data**: Utilizei o formato ISO 8601 (`YYYY-MM-DDTHH:mm:ss.sssZ`) por ser um padrão internacional, facilitando a leitura por outros sistemas caso o CSV seja exportado.
3. **Tratamento do CSV**: O script verifica se o arquivo já existe. Se não existir, ele cria o arquivo e insere um cabeçalho automaticamente. Os campos são encapsulados em aspas duplas para evitar que nomes com vírgulas quebrem a estrutura do CSV.
4. **Dependências**: Nenhuma biblioteca externa (como `npm install ...`) foi utilizada, apenas os módulos nativos do Node.js (`fs` e `path`), garantindo máxima performance e zero configuração extra.

### Instruções de Execução

**1. Pré-requisitos:**
Certifique-se de ter o **Node.js** instalado na sua máquina. Você pode verificar rodando `node -v` no seu terminal.

**2. Instalação:**
Como não há dependências externas, você não precisa rodar `npm install`. Basta salvar o arquivo abaixo em um diretório de sua preferência.

**3. Como rodar:**
Abra o terminal na pasta onde você salvou o arquivo e execute o comando passando o nome do usuário. 

Exemplos:
```bash
node index.js João da Silva
node index.js "Maria Souza"
```

---

### Arquivos do Projeto

`index.js`
```javascript
/**
 * Script para registro de usuários em um arquivo CSV.
 * 
 * Decisões assumidas:
 * - O nome do arquivo CSV será 'usuarios.csv' e será salvo no mesmo diretório do script.
 * - Os argumentos passados na linha de comando formarão o nome do usuário.
 * - Se o arquivo não existir, o script criará a primeira linha como cabeçalho.
 * - Os dados no CSV são envolvidos em aspas duplas para evitar problemas com vírgulas no nome.
 */

const fs = require('fs');
const path = require('path');

// Configurações do arquivo
const FILE_NAME = 'usuarios.csv';
const filePath = path.join(__dirname, FILE_NAME);

// Captura os argumentos da linha de comando (ignorando 'node' e 'index.js')
const args = process.argv.slice(2);

// Junta os argumentos com espaço caso o usuário não use aspas no terminal
const nome = args.join(' ').trim();

// Validação de entrada
if (!nome) {
    console.error('Erro: Nenhum nome foi fornecido.');
    console.log('Uso correto: node index.js <Nome do Usuario>');
    console.log('Exemplo: node index.js João da Silva');
    process.exit(1);
}

// Gera a data atual no formato ISO 8601
const dataCadastro = new Date().toISOString();

// Formata a linha do CSV
const csvLine = `"${nome}","${dataCadastro}"\n`;

try {
    // Verifica se o arquivo já existe
    const fileExists = fs.existsSync(filePath);

    // Se não existir, cria o arquivo e adiciona o cabeçalho
    if (!fileExists) {
        const header = '"Nome","Data de Cadastro"\n';
        fs.writeFileSync(filePath, header, 'utf8');
        console.log(`Arquivo ${FILE_NAME} criado com sucesso.`);
    }

    // Adiciona a nova linha sem sobrescrever as anteriores (append)
    fs.appendFileSync(filePath, csvLine, 'utf8');
    
    console.log(`✅ Sucesso: Usuário "${nome}" registrado em ${dataCadastro}.`);
} catch (error) {
    console.error('❌ Erro ao tentar escrever no arquivo CSV:', error.message);
    process.exit(1);
}
```