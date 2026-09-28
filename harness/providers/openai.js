// providers/openai.js
// max_completion_tokens elevado para 28000: gpt-5.6 e um modelo de
// raciocinio, e o raciocinio interno tambem consome esse orcamento
// (mesmo problema ja documentado no TCC para Claude e Groq). Em uma
// das coletas, o valor anterior (16000) foi insuficiente numa execucao
// especifica dos niveis mais complexos, resultando em resposta vazia
// (finish_reason "length") mesmo apos ter funcionado em tentativas
// anteriores com o mesmo prompt - variancia estocastica do proprio
// modelo, nao um erro de configuracao unico.
import OpenAI from "openai";

export const providerId = "gpt";

export async function generate(prompt, { model }) {
  const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

  const response = await client.chat.completions.create({
    model,
    max_completion_tokens: 28000,
    messages: [{ role: "user", content: prompt }],
  });

  const text = response.choices[0]?.message?.content ?? "";

  return {
    text,
    raw: {
      model: response.model,
      usage: response.usage,
      finish_reason: response.choices[0]?.finish_reason,
      parametros: { max_completion_tokens: 28000, reasoning_effort: "padrao da API", temperature: "padrao da API" },
    },
  };
}
