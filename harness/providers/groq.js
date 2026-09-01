// providers/groq.js
// Groq expoe uma API compativel com a da OpenAI (mesmo formato de
// chat.completions), so muda a base URL e a chave. Camada gratuita,
// sem cartao de credito, usada aqui para o modelo aberto GPT-OSS-120B.
//
// gpt-oss-120b e um modelo de raciocinio: por padrao, os tokens gastos
// "pensando" contam dentro do mesmo orcamento de max_tokens (mesmo
// problema documentado no TCC para o Claude). Alem disso, a camada
// gratuita do Groq tem um teto rigido de 8000 tokens por minuto (TPM),
// contado a partir do max_tokens PEDIDO na requisicao, nao do que de
// fato e gerado - por isso o max_tokens aqui precisa ficar bem abaixo
// de 8000 (deixando folga para os tokens de entrada do prompt), e o
// reasoning_effort e reduzido para "low" para priorizar espaco de
// resposta final dentro desse orcamento apertado.
import OpenAI from "openai";

export const providerId = "groq";

export async function generate(prompt, { model }) {
  const client = new OpenAI({
    apiKey: process.env.GROQ_API_KEY,
    baseURL: "https://api.groq.com/openai/v1",
  });

  const response = await client.chat.completions.create({
    model,
    max_tokens: 7500,
    reasoning_effort: "low",
    messages: [{ role: "user", content: prompt }],
  });

  const text = response.choices[0]?.message?.content ?? "";

  return {
    text,
    raw: {
      model: response.model,
      usage: response.usage,
      finish_reason: response.choices[0]?.finish_reason,
    },
  };
}
