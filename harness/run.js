// run.js
// Executa a escada de níveis em cada modelo configurado e salva, em <saida>/:
//   nivel{N}-{provedor}-t{tentativa}.md   resposta bruta com prompt e metadados
//   run-log.csv                            uma linha por chamada
//
// Uso:
//   node run.js                                  -> todos os níveis e provedores, 1 tentativa
//   node run.js --attempts=3                     -> 3 tentativas por combinação
//   node run.js --attempts=3 --start-attempt=3   -> roda só a tentativa 3
//   node run.js --levels=0,1,2                   -> só os níveis 0, 1 e 2
//   node run.js --providers=claude,gpt           -> só os provedores informados
//   node run.js --saida=../outputs-gemini-refeito  -> pasta de saída (padrão: outputs)
//   node run.js --simular                        -> mostra o que seria enviado, sem chamar as APIs
//   node run.js --sobrescrever                   -> permite substituir arquivos que já existem
//
// Por segurança, um arquivo de saída que já existe nunca é sobrescrito sem --sobrescrever.

import "dotenv/config";
import fs from "node:fs";
import path from "node:path";
import { LEVELS, buildPrompt } from "./prompts.js";
import * as claude from "./providers/anthropic.js";
import * as gpt from "./providers/openai.js";
import * as gemini from "./providers/gemini.js";
import * as groq from "./providers/groq.js";

// ---- configuração dos modelos testados -------------------------------------
// Documente no TCC o identificador exato usado: prefira identificadores fixos
// (ex.: gemini-3.1-pro-preview) a aliases como gemini-pro-latest, que podem
// apontar para versões diferentes ao longo do tempo.
const PROVIDERS = {
  claude: { ...claude, model: process.env.ANTHROPIC_MODEL || "claude-sonnet-5" },
  gpt: { ...gpt, model: process.env.OPENAI_MODEL || "gpt-5.6" },
  gemini: { ...gemini, model: process.env.GEMINI_MODEL || "gemini-3.1-pro-preview" },
  groq: { ...groq, model: process.env.GROQ_MODEL || "openai/gpt-oss-120b" },
};

function numeroOpcional(valor) {
  if (valor === undefined || valor === null) return undefined;
  const v = String(valor).trim().toLowerCase();
  if (v === "" || v === "padrao" || v === "padrão" || v === "default") return undefined;
  const n = Number(v);
  if (!Number.isFinite(n)) throw new Error(`Valor numérico inválido: ${valor}`);
  return n;
}

// Só o provider do Gemini envia temperatura. Vazio = padrão da API.
const TEMPERATURE = numeroOpcional(process.env.TEMPERATURE);

// ---- argumentos --------------------------------------------------------------
const args = Object.fromEntries(
  process.argv.slice(2).map((a) => {
    const [k, v] = a.replace(/^--/, "").split("=");
    return [k, v ?? true];
  })
);

const attempts = Number(args.attempts ?? 1);
const startAttempt = Number(args["start-attempt"] ?? 1);
const selectedLevels = args.levels ? String(args.levels).split(",").map(Number) : LEVELS.map((l) => l.id);
const selectedProviders = args.providers ? String(args.providers).split(",") : Object.keys(PROVIDERS);
const OUTPUT_DIR = path.resolve(process.cwd(), args.saida && args.saida !== true ? args.saida : "outputs");
const LOG_PATH = path.join(OUTPUT_DIR, "run-log.csv");
const SIMULAR = Boolean(args.simular);
const SOBRESCREVER = Boolean(args.sobrescrever);

// ---- utilitários -------------------------------------------------------------
function csvSafe(value) {
  const s = String(value ?? "");
  return s.includes(",") || s.includes('"') || s.includes("\n") ? `"${s.replace(/"/g, '""')}"` : s;
}

function ensureLogHeader() {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  if (!fs.existsSync(LOG_PATH)) {
    fs.writeFileSync(
      LOG_PATH,
      "timestamp,nivel_id,nivel_nome,provider,modelo_pedido,modelo_resolvido,tentativa,parametros,motivo_parada,sucesso,tamanho_chars,arquivo,erro\n"
    );
  }
}

function appendLog(row) {
  const campos = [
    row.timestamp, row.nivel_id, row.nivel_nome, row.provider, row.modelo_pedido, row.modelo_resolvido,
    row.tentativa, row.parametros, row.motivo_parada, row.sucesso, row.tamanho_chars, row.arquivo, row.erro ?? "",
  ];
  fs.appendFileSync(LOG_PATH, campos.map(csvSafe).join(",") + "\n");
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// Erros transitórios (servidor sobrecarregado, limite de taxa) valem nova
// tentativa; erros de configuração (chave inválida, modelo inexistente) não.
function isRetryable(err) {
  return /\b(429|500|502|503|504)\b/.test(err.message) || /timeout/i.test(err.message) || /abort/i.test(err.message);
}

async function generateWithRetry(provider, prompt, opts, maxRetries = 3) {
  let lastErr;
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await provider.generate(prompt, opts);
    } catch (err) {
      lastErr = err;
      if (!isRetryable(err) || attempt === maxRetries) throw err;
      const backoffMs = 5000 * attempt;
      console.warn(`  nova tentativa ${attempt}/${maxRetries - 1} após erro transitório (${err.message.slice(0, 80)}...) - aguardando ${backoffMs / 1000}s`);
      await sleep(backoffMs);
    }
  }
  throw lastErr;
}

function modeloResolvido(raw, pedido) {
  return raw?.modelVersion || raw?.model || pedido;
}

// ---- loop principal ----------------------------------------------------------
async function main() {
  const levels = LEVELS.filter((l) => selectedLevels.includes(l.id));
  console.log(
    `${SIMULAR ? "[SIMULAÇÃO] " : ""}${levels.length} nível(is) x ${selectedProviders.length} provedor(es) x ` +
      `${attempts - startAttempt + 1} tentativa(s) (de ${startAttempt} a ${attempts}) -> ${OUTPUT_DIR}`
  );
  if (selectedProviders.includes("gemini")) {
    console.log(`Gemini: modelo ${PROVIDERS.gemini.model}, parâmetros ${JSON.stringify(gemini.parametros(TEMPERATURE))}`);
  }
  if (!SIMULAR) ensureLogHeader();

  for (const level of levels) {
    const prompt = buildPrompt(level);
    for (const providerKey of selectedProviders) {
      const provider = PROVIDERS[providerKey];
      if (!provider) {
        console.warn(`Provedor desconhecido: ${providerKey} (pulando)`);
        continue;
      }
      for (let attempt = startAttempt; attempt <= attempts; attempt++) {
        const label = `[nivel ${level.id} | ${providerKey} | tentativa ${attempt}]`;
        const nomeArquivo = `nivel${level.id}-${providerKey}-t${attempt}.md`;
        const filePath = path.join(OUTPUT_DIR, nomeArquivo);

        if (SIMULAR) {
          const params = providerKey === "gemini" ? gemini.parametros(TEMPERATURE) : "(ver providers/" + providerKey + ".js)";
          console.log(`${label} modelo=${provider.model} parametros=${JSON.stringify(params)} -> ${nomeArquivo}`);
          continue;
        }
        if (fs.existsSync(filePath) && !SOBRESCREVER) {
          console.warn(`${label} ${nomeArquivo} já existe - pulando (use --sobrescrever para substituir)`);
          continue;
        }

        console.log(`${label} chamando ${provider.model}...`);
        const timestamp = new Date().toISOString();
        try {
          const { text, raw } = await generateWithRetry(provider, prompt, {
            model: provider.model,
            temperature: TEMPERATURE,
          });
          const params = raw?.parametros ?? {};
          const fileContent = [
            `<!--`,
            `nivel: ${level.id} - ${level.nome}`,
            `provider: ${providerKey}`,
            `model: ${provider.model}`,
            `modelo_resolvido: ${modeloResolvido(raw, provider.model)}`,
            `tentativa: ${attempt}`,
            `temperature: ${params.temperature ?? "padrao da API"}`,
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

          const motivo = raw?.stop_reason ?? raw?.finish_reason ?? "";
          appendLog({
            timestamp, nivel_id: level.id, nivel_nome: level.nome, provider: providerKey,
            modelo_pedido: provider.model, modelo_resolvido: modeloResolvido(raw, provider.model),
            tentativa: attempt, parametros: JSON.stringify(params), motivo_parada: motivo,
            sucesso: true, tamanho_chars: text.length, arquivo: nomeArquivo,
          });
          const alerta = /max_tokens|length|MAX_TOKENS/.test(String(motivo)) ? "  ATENÇÃO: resposta truncada pelo teto de tokens" : "";
          console.log(`${label} ok (${text.length} chars, parada: ${motivo}) -> ${nomeArquivo}${alerta}`);
        } catch (err) {
          appendLog({
            timestamp, nivel_id: level.id, nivel_nome: level.nome, provider: providerKey,
            modelo_pedido: provider.model, modelo_resolvido: "", tentativa: attempt, parametros: "",
            motivo_parada: "", sucesso: false, tamanho_chars: 0, arquivo: "", erro: err.message,
          });
          console.error(`${label} ERRO: ${err.message}`);
        }
        await sleep(1500); // pausa curta entre chamadas, por causa dos limites de taxa
      }
    }
  }
  console.log(SIMULAR ? "\nSimulação concluída (nenhuma API foi chamada)." : `\nConcluído. Log em: ${LOG_PATH}`);
}

main();
