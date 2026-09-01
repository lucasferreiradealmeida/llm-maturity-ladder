# Onde os Modelos Travam — Material de Apoio do TCC

Repositório de reprodutibilidade do TCC *"Onde os Modelos Travam: Uma Escada
de Maturidade para Avaliar a Capacidade de LLMs na Geração de Sistemas de
Software"*, apresentado ao Centro Universitário IESB.

**Autor:** Lucas Ferreira de Almeida
**Orientador:** Prof. Pablo Coelho Ferreira

## Estrutura do repositório

```
harness/    → código-fonte que chama as APIs, extrai e testa o código gerado
dados/      → planilha completa de avaliação (60 execuções x 6 critérios)
outputs/    → as 60 respostas brutas dos modelos (5 níveis x 4 provedores x 3 tentativas)
```

## Escopo da coleta

Quatro LLMs foram avaliados ao longo de uma escada de cinco níveis de
complexidade arquitetural e funcional progressiva (persistência simples,
CRUD com banco, API REST, sistema web full-stack, e sistema com
autenticação e controle de acesso), com três tentativas independentes por
combinação:

- **Claude** (Anthropic, `claude-sonnet-5`) — pago
- **GPT** (OpenAI, `gpt-5.6`) — pago
- **Gemini** (Google, `gemini-3.1-pro-preview`) — pago
- **GPT-OSS-120B** (via Groq) — aberto e gratuito

O modelo gratuito foi incluído para responder a uma pergunta prática:
vale a pena pagar por um LLM comercial para geração de código? A
discussão completa está na Seção 5.5 do TCC.

## harness/

Script Node.js que envia os prompts do Apêndice A do TCC para as APIs da
Anthropic, OpenAI, Google e Groq, com retry automático, extração de
código e registro de metadados de cada execução (modelo exato, tokens,
motivo de parada). Requer chaves de API próprias (`.env.example` mostra
as variáveis necessárias).

Uso básico:

```bash
npm install
cp .env.example .env   # preencha com suas chaves
node run.js                                    # 1 tentativa, todos os niveis/provedores
node run.js --attempts=3                       # 3 tentativas por combinacao
node run.js --attempts=3 --start-attempt=3      # roda so a tentativa 3 (nao repete 1 e 2)
node run.js --levels=0,1 --providers=claude,gpt # filtra niveis e/ou provedores
```

Duas particularidades de configuração documentadas na Seção 5.4 do TCC,
já refletidas no código:

- **Orçamento de tokens em modelos de raciocínio** (`anthropic.js`,
  `openai.js`, `groq.js`): o raciocínio interno consome o mesmo
  orçamento configurado para a resposta final, e pode truncar respostas
  em tarefas complexas. O Claude, especificamente, exigiu também modo
  streaming ao elevar o teto para 32.000 tokens (a API rejeita
  requisições muito longas em modo de chamada simples).
- **Limite de taxa da camada gratuita** (`groq.js`): o Groq impõe um
  teto de 8.000 tokens por minuto na camada gratuita, contado a partir
  do orçamento solicitado, não do efetivamente usado.

## dados/rubrica-tcc.xlsx

Planilha com uma linha por execução (60 no total), contendo os seis
critérios de avaliação usados no TCC: corretude, número de correções
manuais, completude (0-5), qualidade estática (avisos do ESLint), boas
práticas (0-5, conforme rubrica do Quadro 3 do TCC) e segurança (0-5,
exclusivo do nível 4), além de observações qualitativas por execução. A
aba "Resumo por Provedor" consolida as médias por modelo.

## outputs/

Os 60 arquivos brutos gerados durante a coleta, nomeados como
`nivel{N}-{provedor}-t{1|2|3}.md`. Cada arquivo contém o prompt enviado,
os metadados da chamada de API e a resposta completa do modelo,
exatamente como recebida — incluindo, nos casos truncados por
esgotamento de orçamento de tokens antes da correção documentada na
Seção 5.4, a resposta vazia original.

Quatro combinações (`nivel0-groq-t1`, `nivel1-groq-t2`, e as
combinações equivalentes do nível 1 do Gemini na coleta original) usam
bibliotecas de interação via terminal incompatíveis com execução
automatizada em lote, e foram validadas dinamicamente em ambiente local
pelo autor — ver limitações na Seção 6 do TCC.

## Principais achados (resumo)

- Os quatro modelos atingiram completude funcional equivalente ao longo
  da escada — não há ponto de ruptura abrupto associado ao aumento de
  complexidade dentro da faixa avaliada.
- Zero vulnerabilidade a injeção de SQL nos 48 projetos com persistência
  em banco, nos quatro provedores.
- O Gemini expôs segredo de sessão fixo e criou uma credencial
  administrativa padrão (`admin`/`admin123`) idêntica e funcional nas
  três tentativas do nível 4, sem exceção.
- O GPT manteve a postura de segurança mais consistente, com proteção
  efetiva contra CSRF verificada experimentalmente em todas as
  tentativas.
- O modelo gratuito (GPT-OSS-120B) entregou completude e qualidade
  comparáveis às dos modelos pagos, ao custo de mais correções manuais
  de integração (dependências ausentes, arquivos não gerados) — ver
  Seção 5.5 do TCC para a análise completa de custo-benefício.

## Citação

Se este material for reutilizado, cite:

ALMEIDA, Lucas Ferreira de. Onde os Modelos Travam: Uma Escada de
Maturidade para Avaliar a Capacidade de LLMs na Geração de Sistemas de
Software. Trabalho de Conclusão de Curso (Ciência da Computação) — Centro
Universitário IESB, Brasília, 2026.
