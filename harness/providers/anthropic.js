// providers/anthropic.js
import Anthropic from "@anthropic-ai/sdk";

export const providerId = "claude";

export async function generate(prompt, { model }) {
  const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

  const response = await client.messages.create({
    model,
    max_tokens: 16000,
    thinking: { type: "adaptive" },
    output_config: { effort: "medium" },
    messages: [{ role: "user", content: prompt }],
  });

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
