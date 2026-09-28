<!--
nivel: 0 - Persistencia simples
provider: gemini
model: gemini-pro-latest
tentativa: 1
temperature: 0.2
timestamp: 2026-08-18T21:56:17.709Z
metadata: {"model":"gemini-pro-latest","usage":{"promptTokenCount":193,"candidatesTokenCount":1074,"totalTokenCount":1994,"promptTokensDetails":[{"modality":"TEXT","tokenCount":193}],"thoughtsTokenCount":727,"serviceTier":"standard"},"finish_reason":"STOP"}
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

Como engenheiro de software, tomei as seguintes decisões de design (documentadas no código):
1. **Entrada de dados:** Utilizei argumentos de linha de comando (`process.argv`) para receber o nome do usuário, pois é a forma mais direta e eficiente para scripts simples.
2. **Manipulação de arquivos:** Utilizei o módulo nativo `fs` (File System) do Node.js. Nenhuma biblioteca externa (como `csv-writer`) foi utilizada para manter o projeto o mais leve possível, respeitando a restrição de não usar frameworks desnecessários.
3. **Formatação do CSV:** O nome do usuário é encapsulado em aspas duplas (`" "`) no CSV para evitar que nomes com vírgulas quebrem a estrutura do arquivo. A data é salva no formato ISO 8601 para padronização.
4. **Cabeçalho:** O script verifica se o arquivo já existe. Se não existir, ele cria o arquivo e adiciona o cabeçalho automaticamente antes de inserir o primeiro registro.

### Instruções de Execução

1. Certifique-se de ter o **Node.js** instalado em sua máquina (versão 14 ou superior recomendada).
2. Crie um diretório para o projeto e salve os arquivos abaixo com seus respectivos nomes.
3. Abra o terminal no diretório onde os arquivos foram salvos.
4. Como não há dependências externas, não é necessário rodar `npm install`.
5. Para executar o script e registrar um usuário, rode o comando:
   ```bash
   node index.js "João da Silva"
   ```
6. Você pode rodar o comando várias vezes com nomes diferentes. O arquivo `usuarios.csv` será criado/atualizado no mesmo diretório.

---

### Arquivo: `package.json`
*(Opcional, mas recomendado para definir a base do projeto Node.js)*

```json
{
  "name": "registro-usuarios-csv",
  "version": "1.0.0",
  "description": "Script para registrar usuários em um arquivo CSV",
  "main": "index.js",
  "scripts": {
    "start": "node index.js"
  },
  "author": "",
  "license": "ISC"
}
```

---

### Arquivo: `index.js`

```javascript
// Importa os módulos nativos do Node.js necessários
const fs = require('fs');
const path = require('path');

// Configurações
const NOME_ARQUIVO = 'usuarios.csv';
const CAMINHO_ARQUIVO = path.join(__dirname, NOME_ARQUIVO);

/**
 * Função principal para registrar o usuário
 */
function registrarUsuario() {
    // Captura o argumento passado na linha de comando (o índice 2 é o primeiro argumento real)
    // Exemplo: node index.js "Maria Souza" -> process.argv[2] será "Maria Souza"
    const nomeUsuario = process.argv[2];

    // Validação simples: verifica se o nome foi fornecido
    if (!nomeUsuario) {
        console.error('Erro: Você deve fornecer um nome de usuário.');
        console.log('Uso correto: node index.js "Nome do Usuario"');
        process.exit(1);
    }

    // Gera a data atual no formato ISO (ex: 2023-10-25T14:30:00.000Z)
    const dataCadastro = new Date().toISOString();

    // Escapa o nome com aspas duplas para evitar problemas caso o nome contenha vírgulas
    const linhaCsv = `"${nomeUsuario}",${dataCadastro}\n`;

    try {
        // Verifica se o arquivo já existe
        const arquivoExiste = fs.existsSync(CAMINHO_ARQUIVO);

        // Se o arquivo não existir, cria o arquivo e adiciona o cabeçalho primeiro
        if (!arquivoExiste) {
            const cabecalho = 'Nome,Data de Cadastro\n';
            fs.writeFileSync(CAMINHO_ARQUIVO, cabecalho, 'utf8');
            console.log(`Arquivo ${NOME_ARQUIVO} criado com sucesso.`);
        }

        // Adiciona a nova linha ao final do arquivo (append) sem sobrescrever
        fs.appendFileSync(CAMINHO_ARQUIVO, linhaCsv, 'utf8');
        
        console.log(`Sucesso! Usuário "${nomeUsuario}" registrado em ${dataCadastro}.`);
    } catch (erro) {
        console.error('Ocorreu um erro ao tentar escrever no arquivo:', erro.message);
        process.exit(1);
    }
}

// Executa a função
registrarUsuario();
```