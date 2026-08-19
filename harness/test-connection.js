// test-connection.js
// Testa a conexao com cada provedor sem NUNCA imprimir a chave no terminal.
// Le as chaves do .env (que fica so na sua maquina, nunca e colado no chat).
//
// Uso:
//   node test-connection.js            -> testa os 3 provedores
//   node test-connection.js gemini     -> testa so o Gemini
//   node test-connection.js claude     -> testa so a Anthropic
//   node test-connection.js gpt        -> testa so a OpenAI

import "dotenv/config";

const TIMEOUT_MS = Number(process.env.TEST_TIMEOUT_MS ?? 90000);

function withTimeout(promise, ms, label) {
  return Promise.race([
    promise,
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error(`Timeout apos ${ms / 1000}s (${label})`)), ms)
    ),
  ]);
}

function maskKey(key) {
  if (!key) return "(nao definida)";
  if (key.length <= 8) return "***";
  return key.slice(0, 4) + "..." + key.slice(-4) + ` (${key.length} chars)`;
}

async function testGemini() {
  const key = process.env.GEMINI_API_KEY;
  const model = process.env.GEMINI_MODEL || "gemini-3.1-pro-preview";
  console.log(`\n[gemini] chave carregada: ${maskKey(key)}`);
  console.log(`[gemini] modelo: ${model}`);
  if (!key) throw new Error("GEMINI_API_KEY nao definida no .env");

  const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${key}`;
  const res = await withTimeout(
    fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{ parts: [{ text: "diga oi" }] }],
        generationConfig: { thinkingConfig: { thinkingBudget: 1024 } },
      }),
    }),
    TIMEOUT_MS,
    "gemini"
  );
  const data = await res.json();
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${JSON.stringify(data)}`);
  const text = data.candidates?.[0]?.content?.parts?.[0]?.text ?? "(sem texto)";
  console.log(`[gemini] OK -> resposta: "${text.trim()}"`);
}

async function testClaude() {
  const key = process.env.ANTHROPIC_API_KEY;
  const model = process.env.ANTHROPIC_MODEL || "claude-sonnet-5";
  console.log(`\n[claude] chave carregada: ${maskKey(key)}`);
  console.log(`[claude] modelo: ${model}`);
  if (!key) throw new Error("ANTHROPIC_API_KEY nao definida no .env");

  const res = await withTimeout(
    fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model,
        max_tokens: 50,
        messages: [{ role: "user", content: "diga oi" }],
      }),
    }),
    TIMEOUT_MS,
    "claude"
  );
  const data = await res.json();
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${JSON.stringify(data)}`);
  const text = data.content?.[0]?.text ?? "(sem texto)";
  console.log(`[claude] OK -> resposta: "${text.trim()}"`);
}

async function testGpt() {
  const key = process.env.OPENAI_API_KEY;
  const model = process.env.OPENAI_MODEL || "gpt-5.6";
  console.log(`\n[gpt] chave carregada: ${maskKey(key)}`);
  console.log(`[gpt] modelo: ${model}`);
  if (!key) throw new Error("OPENAI_API_KEY nao definida no .env");

  const res = await withTimeout(
    fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${key}`,
      },
      body: JSON.stringify({
        model,
        max_completion_tokens: 50,
        messages: [{ role: "user", content: "diga oi" }],
      }),
    }),
    TIMEOUT_MS,
    "gpt"
  );
  const data = await res.json();
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${JSON.stringify(data)}`);
  const text = data.choices?.[0]?.message?.content ?? "(sem texto)";
  console.log(`[gpt] OK -> resposta: "${text.trim()}"`);
}

const TESTS = { gemini: testGemini, claude: testClaude, gpt: testGpt };

async function main() {
  const target = process.argv[2];
  const toRun = target ? [target] : Object.keys(TESTS);

  for (const name of toRun) {
    const fn = TESTS[name];
    if (!fn) {
      console.error(`Provedor desconhecido: ${name}`);
      continue;
    }
    const start = Date.now();
    try {
      await fn();
      console.log(`[${name}] tempo: ${((Date.now() - start) / 1000).toFixed(1)}s`);
    } catch (err) {
      console.error(`[${name}] FALHOU apos ${((Date.now() - start) / 1000).toFixed(1)}s -> ${err.message}`);
    }
  }
}

main();
