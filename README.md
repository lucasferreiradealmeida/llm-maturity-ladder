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
analise/    → scripts que extraem o código das respostas, testam os sistemas gerados e refazem
              a análise estática (ESLint)
```

## Escopo da coleta

Quatro LLMs foram avaliados em uma escada de cinco níveis (persistência em CSV, CRUD em SQLite,
API REST, sistema web completo e sistema com autenticação e controle de acesso), com três
tentativas independentes por combinação. As tentativas 1 e 2 são de 18/08/2026 (GPT-OSS-120B:
27/08/2026); a tentativa 3, de 31/08/2026. As tentativas 1 e 2 do Gemini foram refeitas em
28/09/2026 (ver "Tentativas 1 e 2 do Gemini refeitas", abaixo).

### Parâmetros efetivos

Os valores abaixo são os que o código do harness de fato enviou. O cabeçalho dos arquivos em
`outputs/` registra `temperature: 0.2` para todos os modelos, mas só o provider do Gemini repassa
esse parâmetro; os demais usaram a temperatura padrão da API.

| Modelo | Identificador pedido | Temperatura | Raciocínio | Teto de saída |
|---|---|---|---|---|
| Claude Sonnet 5 (API paga) | `claude-sonnet-5` | padrão | adaptativo, esforço médio | 16.000 (t1, t2); 32.000 com streaming (t3) |
| GPT-5.6 (API paga) | `gpt-5.6` (resolvido pela API como `gpt-5.6-sol`) | padrão | padrão da API | 16.000 (t1, t2); 28.000 (t3) |
| Gemini 3.1 Pro (API paga) | `gemini-3.1-pro-preview` (t1 e t2 refeitas em 28/09/2026; t3) | 0,2 | orçamento fixo de 2.048 tokens | 16.000 |
| GPT-OSS-120B (Groq, camada gratuita) | `openai/gpt-oss-120b` | padrão | esforço baixo | 7.500 (limite de 8.000 tokens por minuto) |

Duas ressalvas, discutidas no artigo (Seções 4.2, 4.3 e 5.6):

- **Gemini:** na coleta original, as tentativas 1 e 2 chamaram o alias `gemini-pro-latest`, e o
  provider da época registrava só o nome pedido, não a versão resolvida. Elas foram refeitas em
  28/09/2026 com o identificador fixo e a configuração da tentativa 3, e a API confirmou a versão
  `gemini-3.1-pro-preview` nas dez chamadas. O Gemini também foi o único modelo com temperatura
  0,2, valor que o guia do Gemini 3 desaconselha; a configuração foi mantida na coleta refeita
  para que as três tentativas continuassem comparáveis.
- **GPT-OSS-120B:** além do teto menor, rodou com `reasoning_effort: "low"` (de 21 a 89 tokens de
  raciocínio por resposta). Nenhuma das 15 respostas atingiu o teto de 7.500 tokens.

O teto inicial de 8.000 tokens truncou respostas de modelos de raciocínio; as execuções afetadas
foram repetidas com o teto novo, e os arquivos em `outputs/` guardam a resposta final.

## harness/

Script Node.js (versão 18 ou superior) que envia os prompts do Apêndice A do artigo para as APIs
da Anthropic, OpenAI, Google e Groq, com nova tentativa automática em erros transitórios, e salva
cada resposta com o prompt e os metadados da chamada. Requer chaves de API próprias, que ficam só no
arquivo `.env` da sua máquina (`.env.example` mostra as variáveis).

```bash
cd harness
npm install
cp .env.example .env                  # preencha com suas chaves
node test-connection.js               # testa os 4 provedores (a chave nunca é impressa inteira)
node run.js --simular                 # mostra modelos e parâmetros, sem chamar as APIs
node run.js --attempts=3              # 3 tentativas por combinação, gravadas em harness/outputs/
node run.js --attempts=3 --start-attempt=3        # roda só a tentativa 3
node run.js --levels=0,1 --providers=claude,gpt   # filtra níveis e/ou provedores
node run.js --saida=../outra-pasta    # grava em outra pasta
```

Um arquivo que já existe nunca é sobrescrito sem `--sobrescrever`. Cada chamada também acrescenta
uma linha a `run-log.csv`, com o modelo pedido, a versão resolvida pela API, os parâmetros enviados
e o motivo de parada (`MAX_TOKENS` ou `length` indicam resposta truncada).

**Versão do harness.** O código que fez a coleta de agosto de 2026 é o do commit
[`7ab1784`](https://github.com/lucasferreiradealmeida/llm-maturity-ladder/tree/7ab1784/harness).
Em 28/09/2026, o harness foi revisto sem mudar o que é enviado aos modelos. O provider do Gemini
passou a chamar a API REST diretamente, no lugar do SDK legado `@google/generative-ai`, para
registrar a versão resolvida pelo servidor (`modelVersion`) e os tokens de raciocínio. Todos os
providers passaram a registrar os parâmetros de fato enviados, e o cabeçalho dos arquivos deixou
de anotar uma temperatura que só o Gemini recebia. Os parâmetros do Gemini, antes fixos no código,
vêm do `.env`; o `.env.example` repete os valores da coleta.

## outputs/

Os 60 arquivos brutos, nomeados `nivel{N}-{provedor}-t{1|2|3}.md`. Cada arquivo contém os
metadados da chamada, o prompt enviado e a resposta do modelo como recebida.

- `outputs/run-log-gemini-2026-09-28.csv`: registro das dez chamadas que refizeram as tentativas 1
  e 2 do Gemini (versão resolvida, parâmetros enviados e motivo de parada).
- `outputs/substituidas/`: as dez respostas originais dessas tentativas, preservadas para consulta.
  Elas não entram na análise.

Dois arquivos (`nivel2-claude-t1` e `nivel2-claude-t2`) foram salvos sem a seção do prompt e sem
os dados de uso de tokens. Outros três nessa situação (`nivel3-gemini-t1`, `nivel3-gemini-t2` e
`nivel4-gemini-t1`, cuja resposta publicada era menor que o tamanho registrado durante a
avaliação) eram da coleta original do Gemini e foram substituídos pelas tentativas refeitas.

Duas execuções (`nivel0-groq-t1` e `nivel1-groq-t2`) usam bibliotecas de terminal interativo
(prompt-sync e inquirer), incompatíveis com a execução em lote, e foram validadas manualmente pelo
autor, em ambiente local. Os menus em readline do Gemini no nível 1 (t2 e t3) foram testados no
ambiente automatizado, com as respostas enviadas a um terminal simulado; os dois têm teste
roteirizado em `analise/teste_interativo_nivel1_gemini.py`.

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
`Revisao` lista cada nota alterada, com o valor original, o novo valor e o motivo. Em resumo (os
itens sobre as tentativas 1 e 2 do Gemini referem-se às respostas originais, depois substituídas;
ver a seção seguinte):

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

### Tentativas 1 e 2 do Gemini refeitas (28/09/2026)

As dez execuções refeitas substituíram as originais na aba `Avaliacao` e foram avaliadas pelas
mesmas regras; a aba `Revisao` registra, numa seção própria, cada nota que mudou:

- correções: 1 → 0 no nível 1 (t1 e t2), porque as novas respostas usam o pacote `sqlite3`, que
  instala sem alteração, no lugar do `better-sqlite3` da coleta original;
- completude: 4 → 5 no nível 2, t2, porque a nova resposta entrega o `package.json`;
- boas práticas: 4 → 3 no nível 3, t2, e 3 → 2 no nível 4, t2;
- segurança: 1 → 1,5 no nível 4, t1 (token Bearer no lugar de cookie sem SameSite) e 1,5 → 1 na
  t2 (o inverso); a média do Gemini continua 1,2, com segredo fixo e `admin`/`admin123` nas três
  tentativas.

## analise/

Reproduz a extração do código, os testes de execução e a análise estática. Requer Python 3.9 ou
superior e Node.js 18 ou superior; no Windows, troque `python3` por `py`.

### Extração e ESLint

```bash
cd analise
npm install
python3 extrair.py ../outputs ../projetos       # uma pasta por execução em projetos/
node eslint.mjs ../projetos resultados-eslint.csv
```

A configuração do ESLint (regras recomendadas do ESLint 9, globais de navegador nos arquivos de
`public/` e similares, duas exceções documentadas para falsos positivos) está descrita no cabeçalho
de `eslint.mjs`. O resultado da execução de 28/09/2026 está em `analise/resultados-eslint.csv`.

### Testes dos sistemas gerados

`testar.py` refaz os testes de execução de forma automática. Para cada resposta bruta, extrai o
código, roda `npm install` sem alterar nada, sobe o sistema e testa os requisitos do prompt:

| Nível | O que é testado |
|---|---|
| 0 | duas execuções seguidas: o CSV precisa ter os dois nomes, com data, sem sobrescrever |
| 1 | pela CLI: cadastro, listagem, e-mail repetido, e-mail inválido, atualização e remoção |
| 2 | pela API REST: criação, listagem, duplicidade, atualização, remoção e respostas em JSON |
| 3 | criação, listagem, atualização e remoção pela API, a página e as chamadas feitas pelo front-end (JSON e código da duplicidade só como informação, porque o prompt do nível 3 não os fixa) |
| 4 | listagem pública, escrita sem login, cadastro e login, escrita autenticada, requisição forjada sem token (CSRF), atributos do cookie, credencial padrão e inspeção do código (hash de senha, segredo de sessão, tempo de login) |

```bash
# a partir da raiz do repositório
python3 analise/testar.py --outputs outputs --saida resultados-testes
python3 analise/testar.py --outputs outputs --filtro "nivel4-*" --saida resultados-nivel4
pip install openpyxl   # só para a comparação com a planilha
python3 analise/comparar_planilha.py resultados-testes/resumo.csv dados/rubrica-tcc.xlsx comparacao.csv
```

Na pasta de `--saida` ficam o `resumo.csv` (sugestões de "rodou sem alteração", completude e
aspectos de segurança, pelas regras da aba `Instrucoes` da planilha), o `relatorio.md` (as
evidências de cada teste) e um `.json` por execução. São sugestões: o avaliador confere as
evidências antes de registrar as notas, e as boas práticas continuam avaliadas pela rubrica.
Programas só interativos (menus) ficam marcados para teste manual, e um `npm install` que falha
sem alterações marca a execução como dependente de correção. Os sistemas gerados rodam na sua
máquina; prefira um ambiente descartável.

**Validação (28/09/2026).** Aplicado às 60 respostas atuais de `outputs/` (Linux, Node.js 22 e
Python 3.11), o script avaliou 50 execuções por conta própria, e as 50 notas de completude
coincidiram com as da planilha, assim como as notas de segurança das 11 execuções do nível 4
entre elas. As outras 10 são exatamente os casos documentados: as sete que precisaram de correção
manual, todas do GPT-OSS-120B, e três menus interativos (`nivel0-groq-t1`, `nivel1-gemini-t2` e
`nivel1-gemini-t3`). A coluna "rodou sem alteração" coincidiu nas outras 57 execuções.
Antes da troca, nas 60 respostas da coleta original, também não houve divergência: 49 de 49
iguais, com as nove correções e os dois menus documentados à época. As evidências estão em
`analise/validacao-testes-2026-09-28/`, com as transcrições dos testes roteirizados dos menus do
Gemini no nível 1 (t2 e t3), que passaram nos oito passos (cadastro, listagem, duplicidade, e-mail
inválido, identificador inválido, atualização, persistência entre execuções e remoção).

## Tentativas 1 e 2 do Gemini refeitas

Na coleta original, as tentativas 1 e 2 do Gemini chamaram o alias `gemini-pro-latest` sem
registrar a versão resolvida. Em 28/09/2026, as dez execuções foram refeitas com o identificador
fixo `gemini-3.1-pro-preview` e a mesma configuração da tentativa 3 (temperatura 0,2, orçamento de
raciocínio de 2.048 tokens e teto de 16.000 tokens). As dez terminaram normalmente (`STOP`), e a
API devolveu `gemini-3.1-pro-preview` como versão resolvida em todas. Para repetir o procedimento:

```bash
cd harness
npm install
cp .env.example .env            # preencha só GEMINI_API_KEY; os demais valores já são os da coleta
node test-connection.js gemini  # confere a chave e mostra a versão resolvida do modelo
node run.js --providers=gemini --attempts=2 --saida=../outputs-gemini-refeito --simular
node run.js --providers=gemini --attempts=2 --saida=../outputs-gemini-refeito
cd ..
python3 analise/testar.py --outputs outputs-gemini-refeito --saida resultados-gemini-refeito
```

As respostas novas estão em `outputs/`, e as originais, em `outputs/substituidas/`. Uma nova
coleta produzirá respostas diferentes (a amostragem não é determinística); o que se reproduz é o
procedimento.

Para rodar o Gemini no padrão da API (temperatura 1,0, a recomendada pelo Google para o Gemini 3),
refaça as três tentativas (`--attempts=3`) com os ajustes indicados no `.env.example`, para que elas
continuem comparáveis entre si.

## Principais achados

- A completude ficou no teto em todos os níveis (as 60 notas foram máximas): não há ponto de
  ruptura associado à complexidade na faixa avaliada.
- A engenharia sentiu a complexidade: as boas práticas caíram no nível 4 no Claude, no Gemini e no
  GPT-OSS-120B, e os problemas do ESLint se concentraram nesse nível.
- Nos 48 projetos com banco, todas as consultas usaram parâmetros.
- No nível 4, o GPT atendeu os cinco aspectos de segurança nas três tentativas, com token anti-CSRF
  verificado por requisição forjada. O Gemini repetiu segredo fixo no código e a credencial
  `admin`/`admin123` nas três tentativas, inclusive nas duas refeitas com o identificador fixo.
- O GPT-OSS-120B precisou de correções em 7 das 15 execuções (contra nenhuma das 45 dos modelos
  pagos) e ficou perto da média dos pagos em segurança; a variação entre os pagos foi maior que a
  distância entre pagos e aberto.

## Citação

ALMEIDA, Lucas Ferreira de. **Além do "funciona"**: uma escada de complexidade para avaliar a
profundidade de engenharia do código gerado por LLMs. Trabalho de Conclusão de Curso (Ciência da
Computação) — Centro Universitário IESB, Brasília, 2026.
