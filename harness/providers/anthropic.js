// providers/anthropic.js
// max_tokens elevado para 32000: numa das coletas, o valor anterior
// (16000) travou o raciocinio adaptativo (effort:medium) em exatos
// 8000 tokens (stop_reason "max_tokens"), sugerindo que o orcamento de
// raciocinio pode ser proporcional ao max_tokens total, e nao um valor
// fixo. Dobrar o teto testa essa hipotese e da mais folga.
//
// Com max_tokens alto, a API da Anthropic exige modo streaming (requisicoes
// que poderiam levar mais de 10 minutos nao sao aceitas como chamada
// simples/bloqueante) - client.messages.stream(...).finalMessage() resolve
// isso mantendo o mesmo formato de resposta usado no resto do harness.
import Anthropic from "@anthropic-ai/sdk";

export const providerId = "claude";

export async function generate(prompt, { model }) {
  const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

  const stream = client.messages.stream({
    model,
    max_tokens: 32000,
    thinking: { type: "adaptive" },
    output_config: { effort: "medium" },
    messages: [{ role: "user", content: prompt }],
  });

  const response = await stream.finalMessage();

  const text = response.content
    .filter((block) => block.type === "text")
    .map((block) => block.text)
    .join("\n");

  return {
    text,
    raw: {
      model: response.model,
      usage: response.usage,
      stop_reason: response.stop_reason,
    },
  };
}
