// providers/openai.js
import OpenAI from "openai";

export const providerId = "gpt";

export async function generate(prompt, { model }) {
  const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

  const response = await client.chat.completions.create({
    model,
    max_completion_tokens: 16000,
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
