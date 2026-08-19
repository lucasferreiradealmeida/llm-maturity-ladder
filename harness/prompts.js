// prompts.js
// Escada de complexidade progressiva usada no experimento do TCC.
// Cada nivel e um prompt AUTOCONTIDO (nao e continuacao do nivel anterior).
// Isso evita que diferencas de janela de contexto entre modelos
// contaminem a comparacao - ver secao de metodologia do TCC.

export const PROMPT_BASE = `Voce e um(a) engenheiro(a) de software responsavel por implementar o sistema
descrito abaixo. Gere o codigo completo, pronto para rodar, incluindo
instrucoes de execucao (como instalar dependencias e como rodar).

TAREFA:
{{TAREFA}}

RESTRICOES:
- Linguagem: Node.js (JavaScript).
- Nao use frameworks alem dos estritamente necessarios para a tarefa.
- Nao peca esclarecimentos: assuma decisoes razoaveis e documente-as em comentarios.
- Entregue todos os arquivos necessarios, indicando o nome do arquivo antes de cada bloco de codigo.`;

export const LEVELS = [
  {
    id: 0,
    nome: "Persistencia simples",
    tarefa: `Crie um script que registre o nome de um usuario em um arquivo CSV
(nome, data de cadastro). Deve ser possivel rodar o script varias vezes e
cada execucao adicionar uma nova linha sem sobrescrever as anteriores.`,
  },
  {
    id: 1,
    nome: "CRUD com persistencia em banco",
    tarefa: `Crie uma aplicacao de linha de comando (CLI) que permita cadastrar, listar,
atualizar e remover usuarios (nome, e-mail, data de nascimento), persistindo
os dados em um banco de dados relacional (SQLite), incluindo o script de
criacao do schema. Valide o formato do e-mail e impeca duplicidade de
e-mail. Trate erros de entrada de forma amigavel.`,
  },
  {
    id: 2,
    nome: "API REST",
    tarefa: `Transforme o sistema de cadastro de usuarios (nome, e-mail, data de
nascimento) em uma API REST (endpoints para criar, listar, atualizar e
remover usuarios), com respostas em JSON e codigos de status HTTP
apropriados. Persista os dados em SQLite.`,
  },
  {
    id: 3,
    nome: "Sistema web full-stack",
    tarefa: `Crie um sistema web completo (frontend + backend) para cadastro de
usuarios. O frontend deve permitir listar, cadastrar, editar e remover
usuarios atraves de uma interface no navegador, consumindo uma API REST
que persiste os dados em SQLite.`,
  },
  {
    id: 4,
    nome: "Seguranca (autenticacao e autorizacao)",
    tarefa: `Crie um sistema web para cadastro de usuarios que inclua um mecanismo de
login (usuario e senha), com senha armazenada de forma segura (hash + salt),
sessao/token de autenticacao, e controle de acesso: apenas usuarios
autenticados podem cadastrar, editar ou remover registros; a listagem e
publica. Persista os dados em SQLite.`,
  },
];

export function buildPrompt(level) {
  return PROMPT_BASE.replace("{{TAREFA}}", level.tarefa);
}
