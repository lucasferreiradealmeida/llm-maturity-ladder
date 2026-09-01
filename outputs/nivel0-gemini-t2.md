<!--
nivel: 0 - Persistencia simples
provider: gemini
model: gemini-pro-latest
tentativa: 2
temperature: 0.2
timestamp: 2026-08-18T21:57:04.645Z
metadata: {"model":"gemini-pro-latest","usage":{"promptTokenCount":193,"candidatesTokenCount":1166,"totalTokenCount":2313,"promptTokensDetails":[{"modality":"TEXT","tokenCount":193}],"thoughtsTokenCount":954,"serviceTier":"standard"},"finish_reason":"STOP"}
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

Aqui está a solução completa para o sistema de registro de usuários em um arquivo CSV, utilizando apenas os módulos nativos do Node.js, conforme solicitado.

### Decisões de Implementação (Assunções)
1. **Interação via Terminal:** O script fará uma pergunta no terminal solicitando o nome do usuário.
2. **Formato do CSV:** O arquivo será criado com o nome `usuarios.csv`. A primeira linha conterá os cabeçalhos (`"Nome","Data de Cadastro"`). Os dados serão encapsulados em aspas duplas para evitar que vírgulas no nome quebrem a estrutura do CSV.
3. **Data:** A data de cadastro será salva no formato ISO 8601 (ex: `2023-10-25T12:00:00.000Z`) para manter um padrão universal.
4. **Módulos:** Foram utilizados apenas os módulos nativos `fs` (File System), `readline` (para ler o input do terminal) e `path` (para resolver o caminho do arquivo). Nenhuma dependência externa (como `npm install`) é necessária.

---

### Arquivos do Projeto

**`package.json`** (Opcional, mas recomendado para definir o projeto Node.js)
```json
{
  "name": "registro-usuarios-csv",
  "version": "1.0.0",
  "description": "Script para registrar usuários em um arquivo CSV",
  "main": "index.js",
  "scripts": {
    "start": "node index.js"
  },
  "author": "Engenheiro de Software",
  "license": "ISC"
}
```

**`index.js`** (Código fonte principal)
```javascript
const fs = require('fs');
const readline = require('readline');
const path = require('path');

// Configuração do arquivo de destino
const FILE_NAME = 'usuarios.csv';
const FILE_PATH = path.join(__dirname, FILE_NAME);

// Configuração da interface de leitura do terminal
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// Função principal
function registrarUsuario() {
  rl.question('Digite o nome do usuario: ', (nome) => {
    // Tratamento básico: remove espaços extras e escapa aspas duplas
    const nomeTratado = nome.trim().replace(/"/g, '""');
    
    if (!nomeTratado) {
      console.log('Erro: O nome não pode estar vazio.');
      rl.close();
      return;
    }

    // Gera a data atual no formato ISO
    const dataCadastro = new Date().toISOString();
    
    // Monta a linha do CSV
    const linhaCsv = `"${nomeTratado}","${dataCadastro}"\n`;

    try {
      // Verifica se o arquivo já existe. Se não, cria e adiciona o cabeçalho.
      if (!fs.existsSync(FILE_PATH)) {
        const cabecalho = '"Nome","Data de Cadastro"\n';
        fs.writeFileSync(FILE_PATH, cabecalho, 'utf8');
      }

      // Adiciona a nova linha ao final do arquivo (append) sem sobrescrever
      fs.appendFileSync(FILE_PATH, linhaCsv, 'utf8');
      
      console.log(`\nSucesso! Usuário "${nomeTratado}" registrado em ${FILE_NAME}.`);
    } catch (error) {
      console.error('\nErro ao salvar no arquivo CSV:', error.message);
    } finally {
      // Encerra o processo do terminal
      rl.close();
    }
  });
}

// Executa a função
registrarUsuario();
```

---

### Instruções de Execução

**1. Pré-requisitos:**
Certifique-se de ter o **Node.js** instalado na sua máquina. Você pode verificar executando `node -v` no seu terminal.

**2. Preparação do ambiente:**
1. Crie uma pasta para o projeto.
2. Salve os dois blocos de código acima em seus respectivos arquivos (`package.json` e `index.js`) dentro dessa pasta.

**3. Como rodar o script:**
Abra o terminal, navegue até a pasta onde os arquivos foram salvos e execute o seguinte comando:

```bash
node index.js
```
*(Alternativamente, se você salvou o `package.json`, pode rodar `npm start`)*

**4. Testando o comportamento:**
1. Ao rodar o comando, o terminal pedirá: `Digite o nome do usuario: `
2. Digite um nome (ex: `João da Silva`) e aperte `Enter`.
3. O script criará o arquivo `usuarios.csv` (se for a primeira vez) e adicionará o registro.
4. Rode o comando `node index.js` novamente, digite outro nome (ex: `Maria Souza`) e aperte `Enter`.
5. Abra o arquivo `usuarios.csv` gerado na mesma pasta. Você verá que ambas as linhas foram registradas corretamente, mantendo o histórico.