# Onde os Modelos Travam — Material de Apoio do TCC

Repositório de reprodutibilidade do TCC *"Onde os Modelos Travam: Uma Escada
de Maturidade para Avaliar a Capacidade de LLMs na Geração de Sistemas de
Software"*, apresentado ao Centro Universitário IESB.

**Autor:** Lucas Ferreira de Almeida
**Orientador:** Prof. Pablo Coelho Ferreira

## Estrutura do repositório

```
harness/    → código-fonte que chama as APIs, extrai e testa o código gerado
dados/      → planilha completa de avaliação (30 execuções x 6 critérios)
outputs/    → as 30 respostas brutas dos modelos (5 níveis x 3 provedores x 2 tentativas)
```

## harness/

Script Node.js que envia os prompts do Apêndice A do TCC para as APIs da
Anthropic, OpenAI e Google, com retry automático, extração de código e
registro de metadados de cada execução (modelo exato, tokens, motivo de
parada). Ver `harness/README.md` (se presente) ou os comentários em
`run.js` para instruções de uso — requer chaves de API próprias
(`.env.example` mostra as variáveis necessárias).

## dados/rubrica-tcc.xlsx

Planilha com uma linha por execução (30 no total), contendo os seis
critérios de avaliação usados no TCC: corretude, número de correções
manuais, completude (0-5), qualidade estática (avisos do ESLint), boas
práticas (0-5, conforme rubrica do Quadro 2 do TCC) e segurança (0-5,
exclusivo do nível 4), além de observações qualitativas por execução.

## outputs/

Os 30 arquivos brutos gerados durante a coleta, nomeados como
`nivel{N}-{provedor}-tentativa{1|2}.md`. Cada arquivo contém o prompt
enviado, os metadados da chamada de API e a resposta completa do modelo,
exatamente como recebida.

## Citação

Se este material for reutilizado, cite:

ALMEIDA, Lucas Ferreira de. Onde os Modelos Travam: Uma Escada de
Maturidade para Avaliar a Capacidade de LLMs na Geração de Sistemas de
Software. Trabalho de Conclusão de Curso (Ciência da Computação) — Centro
Universitário IESB, Brasília, 2026.
