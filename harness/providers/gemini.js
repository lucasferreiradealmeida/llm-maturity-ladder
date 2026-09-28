// providers/gemini.js
// Chama a API REST do Gemini diretamente (sem SDK) para registrar, em cada
// arquivo de saída, a versão resolvida pelo servidor (modelVersion), o uso
// de tokens (inclusive os de raciocínio) e os parâmetros de fato enviados.
//
// Parâmetros (ver .env.example):
//   GEMINI_MODEL              identificador fixo, ex.: gemini-3.1-pro-preview
//   TEMPERATURE               vazio = não envia (usa o padrão da API, 1.0 no Gemini 3)
//   GEMINI_THINKING_BUDGET    orçamento de raciocínio (parâmetro legado); vazio = não envia
//   GEMINI_THINKING_LEVEL     alternativa ao orçamento: low ou high; vazio = não envia
//   GEMINI_MAX_OUTPUT_TOKENS  teto de saída (inclui o raciocínio); vazio = 32000
//
// A coleta original (18/08 e 31/08/2026) usou o SDK @google/generative-ai com
// temperatura 0.2, thinkingBudget 2048 e maxOutputTokens 16000; nas tentativas
// 1 e 2, com o alias gemini-pro-latest, e na 3, com gemini-3.1-pro-preview.
// O .env.example repete essa configuração com o identificador fixo, para que
// tentativas refeitas fiquem comparáveis à tentativa 3. A requisição é a mesma
// que o SDK montava: o prompt como única mensagem do usuário e o generationConfig.

export const providerId = "gemini";

const BASE_URL = process.env.GEMINI_BASE_URL || "https://generativelanguage.googleapis.com/v1beta";

function numeroOpcional(valor) {
  if (valor === undefined || valor === null) return undefined;
  const v = String(valor).trim().toLowerCase();
  if (v === "" || v === "padrao" || v === "padrão" || v === "default") return undefined;
  const n = Number(v);
  if (!Number.isFinite(n)) throw new Error(`Valor numérico inválido: ${valor}`);
  return n;
}

export function parametros(temperature) {
  const generationConfig = {
    maxOutputTokens: numeroOpcional(process.env.GEMINI_MAX_OUTPUT_TOKENS) ?? 32000,
  };
  if (temperature !== undefined) generationConfig.temperature = temperature;
  const budget = numeroOpcional(process.env.GEMINI_THINKING_BUDGET);
  const nivel = (process.env.GEMINI_THINKING_LEVEL || "").trim();
  if (budget !== undefined) generationConfig.thinkingConfig = { thinkingBudget: budget };
  else if (nivel) generationConfig.thinkingConfig = { thinkingLevel: nivel };
  return generationConfig;
}

export async function generate(prompt, { model, temperature }) {
  const key = process.env.GEMINI_API_KEY;
  if (!key) throw new Error("GEMINI_API_KEY nao definida no .env");

  const generationConfig = parametros(temperature);
  // Modelos Pro com raciocínio podem demorar vários minutos no nível 4.
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), numeroOpcional(process.env.GEMINI_TIMEOUT_MS) ?? 600000);

  try {
    const res = await fetch(`${BASE_URL}/models/${model}:generateContent`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-goog-api-key": key },
      body: JSON.stringify({
        contents: [{ role: "user", parts: [{ text: prompt }] }],
        generationConfig,
      }),
      signal: controller.signal,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${JSON.stringify(data).slice(0, 500)}`);
    }

    const candidato = data.candidates?.[0];
    const text = (candidato?.content?.parts ?? [])
      .filter((p) => !p.thought && typeof p.text === "string")
      .map((p) => p.text)
      .join("");

    return {
      text,
      raw: {
        model,
        modelVersion: data.modelVersion ?? null,
        responseId: data.responseId ?? null,
        usage: data.usageMetadata ?? null,
        finish_reason: candidato?.finishReason ?? null,
        parametros: {
          ...generationConfig,
          temperature: generationConfig.temperature ?? "padrao da API",
          thinkingConfig: generationConfig.thinkingConfig ?? "padrao do modelo",
        },
      },
    };
  } finally {
    clearTimeout(timeout);
  }
}
