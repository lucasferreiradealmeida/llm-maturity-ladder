// run.js
// Executa a escada de niveis em cada modelo configurado e salva:
//   outputs/nivel-<id>-<nome>/<provider>/tentativa-<n>.md   (codigo bruto gerado)
//   outputs/run-log.csv                                     (planilha-base para a rubrica de avaliacao)
//
// Uso:
//   node run.js                          -> roda tudo, 1 tentativa por combinacao
//   node run.js --attempts=3             -> 3 tentativas por combinacao (recomendado p/ medir variancia)
//   node run.js --levels=0,1,2           -> roda so os niveis 0,1,2
//   node run.js --providers=claude,gpt   -> roda so os provedores informados

import "dotenv/config";
import fs from "node:fs";
import path from "node:path";
import { LEVELS, buildPrompt } from "./prompts.js";
import * as claude from "./providers/anthropic.js";
import * as gpt from "./providers/openai.js";
import * as gemini from "./providers/gemini.js";

// ---- configuracao dos modelos testados --------------------------------
// Ajuste os model IDs para a versao vigente no momento em que voce for
// rodar o experimento (documente a versao exata usada no TCC - modelos
// mudam com frequencia). O nome/versao pode ser sobrescrito por variavel
// de ambiente sem precisar editar este arquivo.
const PROVIDERS = {
  claude: {
    ...claude,
    model: process.env.ANTHROPIC_MODEL || "claude-sonnet-5",
  },
  gpt: {
    ...gpt,
    model: process.env.OPENAI_MODEL || "gpt-5.6",
  },
  gemini: {
    ...gemini,
    model: process.env.GEMINI_MODEL || "gemini-3.1-pro-preview",
  },
};

const TEMPERATURE = Number(process.env.TEMPERATURE ?? 0.2);

// ---- parse de argumentos simples ---------------------------------------
const args = Object.fromEntries(
  process.argv.slice(2).map((a) => {
    const [k, v] = a.replace(/^--/, "").split("=");
    return [k, v ?? true];
  })
);

const attempts = Number(args.attempts ?? 1);
const selectedLevels = args.levels
  ? args.levels.split(",").map(Number)
  : LEVELS.map((l) => l.id);
const selectedProviders = args.providers
  ? args.providers.split(",")
  : Object.keys(PROVIDERS);

// ---- utilitarios ---------------------------------------------------------
const OUTPUT_DIR = path.join(process.cwd(), "outputs");
const LOG_PATH = path.join(OUTPUT_DIR, "run-log.csv");

function ensureLogHeader() {
  if (!fs.existsSync(LOG_PATH)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    fs.writeFileSync(
      LOG_PATH,
      "timestamp,nivel_id,nivel_nome,provider,model,tentativa,temperature,sucesso,tamanho_chars,arquivo,erro\n"
    );
  }
}

function appendLog(row) {
  const line =
    [
      row.timestamp,
      row.nivel_id,
      csvSafe(row.nivel_nome),
      row.provider,
      csvSafe(row.model),
      row.tentativa,
      row.temperature,
      row.sucesso,
      row.tamanho_chars,
      csvSafe(row.arquivo),
      csvSafe(row.erro ?? ""),
    ].join(",") + "\n";
  fs.appendFileSync(LOG_PATH, line);
}

function csvSafe(value) {
  const s = String(value ?? "");
  return s.includes(",") || s.includes('"') || s.includes("\n")
    ? `"${s.replace(/"/g, '""')}"`
    : s;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// Erros transitorios (servidor sobrecarregado, rate limit) valem retry;
// erros de configuracao (chave invalida, modelo inexistente) nao.
function isRetryable(err) {
  return (
    /\b(429|500|502|503|504)\b/.test(err.message) ||
    /timeout/i.test(err.message) ||
    /abort/i.test(err.message)
  );
}

async function generateWithRetry(provider, prompt, opts, maxRetries = 3) {
  let lastErr;
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await provider.generate(prompt, opts);
    } catch (err) {
      lastErr = err;
      if (!isRetryable(err) || attempt === maxRetries) throw err;
      const backoffMs = 5000 * attempt; // 5s, 10s, 15s...
      console.warn(
        `  retry ${attempt}/${maxRetries - 1} apos erro transitorio (${err.message.slice(0, 80)}...) - aguardando ${backoffMs / 1000}s`
      );
      await sleep(backoffMs);
    }
  }
  throw lastErr;
}

// ---- loop principal --------------------------------------------------
async function main() {
  ensureLogHeader();

  const levels = LEVELS.filter((l) => selectedLevels.includes(l.id));

  console.log(
    `Rodando ${levels.length} nivel(is) x ${selectedProviders.length} provedor(es) x ${attempts} tentativa(s)`
  );

  for (const level of levels) {
    const prompt = buildPrompt(level);
    const levelDirName = `nivel-${level.id}-${slug(level.nome)}`;

    for (const providerKey of selectedProviders) {
      const provider = PROVIDERS[providerKey];
      if (!provider) {
        console.warn(`Provedor desconhecido: ${providerKey} (pulando)`);
        continue;
      }

      const providerDir = path.join(OUTPUT_DIR, levelDirName, providerKey);
      fs.mkdirSync(providerDir, { recursive: true });

      for (let attempt = 1; attempt <= attempts; attempt++) {
        const label = `[nivel ${level.id} | ${providerKey} | tentativa ${attempt}]`;
        console.log(`${label} chamando ${provider.model}...`);

        const timestamp = new Date().toISOString();
        const filePath = path.join(providerDir, `tentativa-${attempt}.md`);

        try {
          const { text, raw } = await generateWithRetry(provider, prompt, {
            model: provider.model,
            temperature: TEMPERATURE,
          });

          const fileContent = [
            `<!--`,
            `nivel: ${level.id} - ${level.nome}`,
            `provider: ${providerKey}`,
            `model: ${provider.model}`,
            `tentativa: ${attempt}`,
            `temperature: ${TEMPERATURE}`,
            `timestamp: ${timestamp}`,
            `metadata: ${JSON.stringify(raw)}`,
            `-->`,
            ``,
            `## Prompt enviado`,
            "```",
            prompt,
            "```",
            ``,
            `## Resposta do modelo`,
            ``,
            text,
          ].join("\n");

          fs.writeFileSync(filePath, fileContent, "utf-8");

          appendLog({
            timestamp,
            nivel_id: level.id,
            nivel_nome: level.nome,
            provider: providerKey,
            model: provider.model,
            tentativa: attempt,
            temperature: TEMPERATURE,
            sucesso: true,
            tamanho_chars: text.length,
            arquivo: path.relative(OUTPUT_DIR, filePath),
          });

          console.log(`${label} ok (${text.length} chars) -> ${filePath}`);
        } catch (err) {
          appendLog({
            timestamp,
            nivel_id: level.id,
            nivel_nome: level.nome,
            provider: providerKey,
            model: provider.model,
            tentativa: attempt,
            temperature: TEMPERATURE,
            sucesso: false,
            tamanho_chars: 0,
            arquivo: "",
            erro: err.message,
          });
          console.error(`${label} ERRO: ${err.message}`);
        }

        // pequena pausa entre chamadas para respeitar rate limits
        await sleep(1500);
      }
    }
  }

  console.log(`\nConcluido. Log consolidado em: ${LOG_PATH}`);
}

function slug(text) {
  return text
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "");
}

main();
