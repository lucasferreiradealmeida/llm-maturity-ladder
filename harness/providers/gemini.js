// providers/gemini.js
import { GoogleGenerativeAI } from "@google/generative-ai";

export const providerId = "gemini";

export async function generate(prompt, { model, temperature }) {
  const client = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
  const generativeModel = client.getGenerativeModel({
    model,
    generationConfig: {
      temperature,
      maxOutputTokens: 16000,
      thinkingConfig: { thinkingBudget: 2048 },
    },
  });

  // Modelos "Pro" com thinking habilitado podem demorar bem mais que o
  // default - damos 120s de folga antes de desistir.
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 120000);

  try {
    const result = await generativeModel.generateContent(prompt, {
      signal: controller.signal,
    });
    const text = result.response.text();

    return {
      text,
      raw: {
        model,
        usage: result.response.usageMetadata,
        finish_reason: result.response.candidates?.[0]?.finishReason,
      },
    };
  } finally {
    clearTimeout(timeout);
  }
}
