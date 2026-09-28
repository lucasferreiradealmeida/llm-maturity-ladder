<!--
nivel: 0 - Persistencia simples
provider: gemini
model: gemini-3.1-pro-preview
modelo_resolvido: gemini-3.1-pro-preview
tentativa: 2
temperature: 0.2
timestamp: 2026-09-28T18:31:27.752Z
metadata: {"model":"gemini-3.1-pro-preview","modelVersion":"gemini-3.1-pro-preview","responseId":"gLK6aoT8NqHoz7IPw5Wj2Aw","usage":{"promptTokenCount":193,"candidatesTokenCount":918,"totalTokenCount":2000,"promptTokensDetails":[{"modality":"TEXT","tokenCount":193}],"thoughtsTokenCount":889,"serviceTier":"standard"},"finish_reason":"STOP","parametros":{"maxOutputTokens":16000,"temperature":0.2,"thinkingConfig":{"thinkingBudget":2048}}}
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

Aqui está a implementação completa do sistema solicitado. 

### Decisões de Design Assumidas:
1. **Entrada de Dados**: Optei por receber o nome do usuário via argumentos de linha de comando (`process.argv`). Isso torna o script fácil de automatizar e testar.
2. **Formato da Data**: Utilizei o formato ISO 8601 (`YYYY-MM-DDTHH:mm:ss.sssZ`) por ser um padrão internacional seguro para ordenação e parsing em planilhas ou bancos de dados.
3. **Cabeçalho do CSV**: O script verifica se o arquivo já existe. Se não existir, ele cria o arquivo e insere um cabeçalho (`"Nome","Data de Cadastro"`) antes de inserir o primeiro registro.
4. **Módulos**: Utilizei apenas o módulo nativo `fs` (File System) do Node.js. Nenhuma biblioteca externa (como `csv-writer`) foi utilizada para manter o projeto o mais enxuto possível, conforme a restrição.

---

### Instruções de Execução

**1. Pré-requisitos:**
Certifique-se de ter o [Node.js](https://nodejs.org/) instalado na sua máquina (versão 14 ou superior recomendada).

**2. Instalação de dependências:**
Como o script utiliza apenas módulos nativos do Node.js, **não é necessário instalar nenhuma dependência externa** (não há necessidade de `npm install`).

**3. Como rodar:**
Abra o terminal no diretório onde o arquivo `index.js` foi salvo e execute o comando passando o nome do usuário como argumento:

```bash
node index.js João da Silva
```

Para adicionar outro usuário, basta rodar novamente:
```bash
node index.js Maria Oliveira
```

---

### Arquivos do Projeto

**`index.js`**
```javascript
// Importa o módulo nativo de File System (Sistema de Arquivos) do Node.js
const fs = require('fs');
const path = require('path');

// Define o nome do arquivo CSV
const FILE_NAME = path.join(__dirname, 'usuarios.csv');

function registrarUsuario() {
    // Captura os argumentos passados na linha de comando (ignorando 'node' e 'index.js')
    const args = process.argv.slice(2);
    
    // Junta os argumentos para formar o nome completo
    const nome = args.join(' ').trim();

    // Valida se o nome foi fornecido
    if (!nome) {
        console.error('Erro: Nenhum nome fornecido.');
        console.log('Uso correto: node index.js <Nome do Usuario>');
        console.log('Exemplo: node index.js João da Silva');
        process.exit(1);
    }

    // Gera a data atual no formato ISO 8601
    const dataCadastro = new Date().toISOString();

    // Formata a linha do CSV. 
    // Aspas duplas são usadas para evitar quebras caso o nome contenha vírgulas.
    const linhaCsv = `"${nome}","${dataCadastro}"\n`;

    try {
        // Verifica se o arquivo já existe
        const arquivoExiste = fs.existsSync(FILE_NAME);

        // Se o arquivo não existir, cria o arquivo e adiciona o cabeçalho
        if (!arquivoExiste) {
            const cabecalho = '"Nome","Data de Cadastro"\n';
            fs.writeFileSync(FILE_NAME, cabecalho, 'utf8');
            console.log('Arquivo CSV criado com cabeçalho.');
        }

        // Adiciona a nova linha ao final do arquivo (append) sem sobrescrever
        fs.appendFileSync(FILE_NAME, linhaCsv, 'utf8');
        
        console.log(`Sucesso! Usuário "${nome}" registrado em ${FILE_NAME}.`);
    } catch (erro) {
        console.error('Ocorreu um erro ao tentar escrever no arquivo:', erro.message);
        process.exit(1);
    }
}

// Executa a função principal
registrarUsuario();
```