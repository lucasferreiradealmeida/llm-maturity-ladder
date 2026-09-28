# Além do "funciona" — material de apoio do TCC

Repositório de reprodutibilidade do TCC *"Além do 'funciona': uma escada de complexidade para
avaliar a profundidade de engenharia do código gerado por LLMs"*, apresentado ao Centro
Universitário IESB.

**Autor:** Lucas Ferreira de Almeida
**Orientador:** Prof. Pablo Coelho Ferreira

> O nome do repositório (`llm-maturity-ladder`) vem de uma versão anterior do trabalho. O artigo
> adota o termo **escada de complexidade**, e não modelo de maturidade, porque os degraus graduam a
> tarefa pedida, e não o processo de quem a executa (Seção 2). O nome foi mantido para não quebrar
> os links já publicados.

## Estrutura do repositório

```
harness/    → código que envia os prompts às APIs e salva as respostas brutas com metadados
outputs/    → as 60 respostas brutas (5 níveis × 4 modelos × 3 tentativas)
dados/      → planilha de avaliação (60 execuções × 6 critérios), com o registro da revisão
analise/    → scripts que extraem o código das respostas e refazem a análise estática (ESLint)
```

## Escopo da coleta

Quatro LLMs foram avaliados em uma escada de cinco níveis (persistência em CSV, CRUD em SQLite,
API REST, sistema web completo e sistema com autenticação e controle de acesso), com três
tentativas independentes por combinação. As tentativas 1 e 2 são de 18/08/2026 (GPT-OSS-120B:
27/08/2026); a tentativa 3, de 31/08/2026.

### Parâmetros efetivos

Os valores abaixo são os que o código do harness de fato enviou. O cabeçalho dos arquivos em
`outputs/` registra `temperature: 0.2` para todos os modelos, mas só o provider do Gemini repassa
esse parâmetro; os demais usaram a temperatura padrão da API.

| Modelo | Identificador pedido | Temperatura | Raciocínio | Teto de saída |
|---|---|---|---|---|
| Claude Sonnet 5 (API paga) | `claude-sonnet-5` | padrão | adaptativo, esforço médio | 16.000 (t1, t2); 32.000 com streaming (t3) |
| GPT-5.6 (API paga) | `gpt-5.6` (resolvido pela API como `gpt-5.6-sol`) | padrão | padrão da API | 16.000 (t1, t2); 28.000 (t3) |
| Gemini 3.1 Pro (API paga) | `gemini-pro-latest` (t1, t2); `gemini-3.1-pro-preview` (t3) | 0,2 | orçamento fixo de 2.048 tokens | 16.000 |
| GPT-OSS-120B (Groq, camada gratuita) | `openai/gpt-oss-120b` | padrão | esforço baixo | 7.500 (limite de 8.000 tokens por minuto) |

Duas ressalvas, discutidas no artigo (Seções 4.2, 4.3 e 5.6):

- **Gemini:** as tentativas 1 e 2 chamaram o alias `gemini-pro-latest`, e o provider registra só o
  nome pedido, não a versão resolvida; apenas a tentativa 3 usou o identificador fixo. O Gemini
  também foi o único modelo com temperatura 0,2, valor que o guia do Gemini 3 desaconselha.
- **GPT-OSS-120B:** além do teto menor, rodou com `reasoning_effort: "low"` (de 21 a 89 tokens de
  raciocínio por resposta). Nenhuma das 15 respostas atingiu o teto de 7.500 tokens.

O teto inicial de 8.000 tokens truncou respostas de modelos de raciocínio; as execuções afetadas
foram repetidas com o teto novo, e os arquivos em `outputs/` guardam a resposta final.

## harness/

Script Node.js que envia os prompts do Apêndice A do artigo para as APIs da Anthropic, OpenAI,
Google e Groq, com retry automático, e salva cada resposta com os metadados da chamada (modelo,
tokens, motivo de parada). A extração do código e os testes de execução foram feitos à parte; a
extração e a análise estática estão em `analise/`. Requer chaves de API próprias
(`.env.example` mostra as variáveis).

```bash
cd harness
npm install
cp .env.example .env   # preencha com suas chaves
node run.js                                     # 1 tentativa, todos os níveis/provedores
node run.js --attempts=3                        # 3 tentativas por combinação
node run.js --attempts=3 --start-attempt=3      # roda só a tentativa 3
node run.js --levels=0,1 --providers=claude,gpt # filtra níveis e/ou provedores
```

## outputs/

Os 60 arquivos brutos, nomeados `nivel{N}-{provedor}-t{1|2|3}.md`. Cada arquivo contém os
metadados da chamada, o prompt enviado e a resposta do modelo como recebida.

Cinco arquivos (`nivel2-claude-t1`, `nivel2-claude-t2`, `nivel3-gemini-t1`, `nivel3-gemini-t2` e
`nivel4-gemini-t1`) foram salvos sem a seção do prompt e sem os dados de uso de tokens. Nos três do
Gemini, a resposta publicada é menor que o tamanho registrado na planilha durante a avaliação
(colunas F e O da aba `Avaliacao`).

Quatro execuções (`nivel0-groq-t1`, `nivel1-groq-t2` e as duas do nível 1 do Gemini na coleta
original) usam bibliotecas de terminal interativo, incompatíveis com a execução em lote, e foram
validadas manualmente pelo autor em ambiente local.

## dados/rubrica-tcc.xlsx

Uma linha por execução, com os seis critérios do artigo e as observações de cada teste. As regras
aplicadas igualmente às 60 execuções são:

- **Rodou sem alteração:** "S" só quando nenhuma alteração foi necessária (fórmula sobre a coluna H).
- **Correções manuais:** qualquer alteração nos arquivos gerados para o sistema rodar (dependência
  ausente ou em versão que não instala, JSON inválido, diretório não criado). Falha do extrator não conta.
- **Completude (0-5):** parte de 5 e perde 1 ponto por requisito do prompt não atendido. Escolhas que
  o prompt não fixa (interface de entrada, porta, modelo de dados, 400 ou 409 para duplicidade) não
  perdem ponto.
- **Qualidade estática:** problemas do ESLint por 100 linhas de JavaScript, com a configuração de
  `analise/`. A contagem original fica preservada na coluna J.
- **Boas práticas (0-5):** rubrica holística do Quadro 3 do artigo.
- **Segurança (0-5, só nível 4):** soma de cinco aspectos (0; 0,5; 1): senha com derivação lenta e
  sal; segredo de sessão fora do código; sessão protegida contra CSRF; login com o mesmo trabalho
  para usuário inexistente; nenhuma credencial padrão (colunas U a Y).

As abas `Resumo por Provedor` e `Resumo por Nivel` são calculadas por fórmula a partir da aba
`Avaliacao`.

### Revisão de 28/09/2026

As notas foram revistas depois da coleta para aplicar as regras acima de forma uniforme. A aba
`Revisao` lista cada nota alterada, com o valor original, o novo valor e o motivo. Em resumo:

- a completude deixou de penalizar escolhas não fixadas pelo prompt (Gemini nos níveis 0 e 2; Claude
  no nível 4, cuja separação entre contas de login e registros também aparece no Claude t3 e no
  GPT-OSS t1 e t3, que tinham nota 5);
- o mesmo ajuste de versão do `better-sqlite3` passou a contar como correção também no Gemini
  (nível 1, t1 e t2), e o `db/schema.sql` do GPT-OSS no nível 4 deixou de contar, porque estava na
  resposta e só não foi reconhecido pelo extrator;
- a nota de segurança passou a ser a soma dos cinco aspectos, conferidos no código das 12
  execuções do nível 4; a proteção CSRF da tentativa 3 do GPT foi verificada com requisição forjada
  (`analise/teste_csrf_gpt_t3.py`);
- a nota de boas práticas que faltava (GPT-OSS, nível 4, t1) foi atribuída pela rubrica.

## analise/

Reproduz a extração do código e a análise estática. Requer Python 3 e Node.js 18 ou superior.

```bash
cd analise
npm install
python3 extrair.py ../outputs ../projetos       # uma pasta por execução em projetos/
node eslint.mjs ../projetos resultados-eslint.csv
```

A configuração do ESLint (regras recomendadas do ESLint 9, globais de navegador nos arquivos de
`public/` e similares, duas exceções documentadas para falsos positivos) está descrita no cabeçalho
de `eslint.mjs`. O resultado da execução de 28/09/2026 está em `analise/resultados-eslint.csv`.

## Principais achados

- A completude ficou no teto em todos os níveis (59 das 60 notas máximas): não há ponto de ruptura
  associado à complexidade na faixa avaliada.
- A engenharia sentiu a complexidade: as boas práticas caíram no nível 4 no Claude, no Gemini e no
  GPT-OSS-120B, e os problemas do ESLint se concentraram nesse nível.
- Nos 48 projetos com banco, todas as consultas usaram parâmetros.
- No nível 4, o GPT atendeu os cinco aspectos de segurança nas três tentativas, com token anti-CSRF
  verificado por requisição forjada. O Gemini repetiu segredo fixo no código e a credencial
  `admin`/`admin123` nas três tentativas.
- O GPT-OSS-120B precisou de correções em 7 das 15 execuções (contra 2 das 45 dos modelos pagos) e
  ficou perto da média dos pagos em segurança; a variação entre os pagos foi maior que a distância
  entre pagos e aberto.

## Citação

ALMEIDA, Lucas Ferreira de. **Além do "funciona"**: uma escada de complexidade para avaliar a
profundidade de engenharia do código gerado por LLMs. Trabalho de Conclusão de Curso (Ciência da
Computação) — Centro Universitário IESB, Brasília, 2026.
