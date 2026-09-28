// Reexecuta a análise estática do TCC sobre os projetos extraídos por extrair.py.
//
// Uso (dentro de analise/):
//   npm install
//   python3 extrair.py ../outputs ../projetos
//   node eslint.mjs ../projetos resultados-eslint.csv
//
// Configuração aplicada igualmente aos 60 projetos:
//   - regras recomendadas do ESLint 9 (@eslint/js, "recommended"), ecmaVersion "latest";
//   - arquivos em public/, frontend/, static/, client/ ou views/ recebem os globais de navegador;
//     os demais, os globais de Node.js;
//   - sourceType "module" para .mjs, para arquivos com import/export e para projetos com
//     "type": "module"; "commonjs" para os demais (.cjs sempre commonjs);
//   - duas exceções na regra no-unused-vars, para não contar falsos positivos:
//       * em scripts de navegador, funções globais não são cobradas (vars: "local"),
//         porque costumam ser chamadas pelo HTML (onclick etc.);
//       * parâmetros exigidos pela assinatura não são cobrados: nomes iniciados por "_"
//         e o "next" dos tratadores de erro do Express (err, req, res, next).
// São contados todos os problemas apontados (erros + avisos das regras), e as linhas
// não vazias dos arquivos analisados, para normalizar por 100 linhas.
import fs from "node:fs";
import path from "node:path";
import { ESLint } from "eslint";
import js from "@eslint/js";
import globals from "globals";

const [, , dirProjetos = "../projetos", saida = "resultados-eslint.csv"] = process.argv;
const DIRS_NAVEGADOR = new Set(["public", "frontend", "static", "client", "views"]);
const RE_ESM = /^\s*(import\s[^(]|import\s*["']|export\s)/m;

function arquivosJs(raiz) {
  const lista = [];
  (function andar(dir) {
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
      if (e.name === "node_modules") continue;
      const p = path.join(dir, e.name);
      if (e.isDirectory()) andar(p);
      else if (/\.(c|m)?js$/.test(e.name)) lista.push(path.relative(raiz, p).split(path.sep).join("/"));
    }
  })(raiz);
  return lista.sort();
}

function tipoPacote(raiz, arquivo) {
  // procura o package.json mais próximo do arquivo
  let dir = path.dirname(path.join(raiz, arquivo));
  while (dir.startsWith(raiz)) {
    const pj = path.join(dir, "package.json");
    if (fs.existsSync(pj)) {
      try { return JSON.parse(fs.readFileSync(pj, "utf8")).type || "commonjs"; } catch { return "commonjs"; }
    }
    if (dir === raiz) break;
    dir = path.dirname(dir);
  }
  return "commonjs";
}

async function analisar(raiz) {
  const arquivos = arquivosJs(raiz);
  if (!arquivos.length) return { arquivos: 0, linhas: 0, problemas: 0, sintaxe: 0, regras: {} };
  const config = [js.configs.recommended];
  let linhas = 0;
  for (const arq of arquivos) {
    const texto = fs.readFileSync(path.join(raiz, arq), "utf8");
    linhas += texto.split("\n").filter((l) => l.trim()).length;
    const navegador = arq.split("/").some((seg) => DIRS_NAVEGADOR.has(seg));
    const esm = arq.endsWith(".mjs") || (!arq.endsWith(".cjs") && (RE_ESM.test(texto) || tipoPacote(raiz, arq) === "module"));
    config.push({
      files: [arq],
      languageOptions: {
        ecmaVersion: "latest",
        sourceType: esm ? "module" : navegador ? "script" : "commonjs",
        globals: navegador ? { ...globals.browser } : { ...globals.node },
      },
      rules: {
        "no-unused-vars": ["error", {
          vars: navegador ? "local" : "all",
          args: "after-used",
          argsIgnorePattern: "^(_|next$)",
        }],
      },
    });
  }
  const eslint = new ESLint({ cwd: raiz, overrideConfigFile: true, overrideConfig: config });
  const resultados = await eslint.lintFiles(arquivos);
  let problemas = 0, sintaxe = 0;
  const regras = {};
  for (const r of resultados) {
    for (const m of r.messages) {
      if (m.fatal) { sintaxe++; continue; }
      problemas++;
      regras[m.ruleId] = (regras[m.ruleId] || 0) + 1;
    }
  }
  return { arquivos: arquivos.length, linhas, problemas, sintaxe, regras };
}

const execucoes = fs.readdirSync(dirProjetos).filter((d) => /^nivel\d-/.test(d)).sort();
const linhasCsv = ["execucao,arquivos_js,linhas,problemas,erros_de_sintaxe,problemas_por_100_linhas,regras"];
for (const exec of execucoes) {
  const r = await analisar(path.resolve(dirProjetos, exec));
  const por100 = r.linhas ? ((100 * r.problemas) / r.linhas).toFixed(2) : "0.00";
  const regras = Object.entries(r.regras).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k}:${v}`).join(" ");
  linhasCsv.push([exec, r.arquivos, r.linhas, r.problemas, r.sintaxe, por100, `"${regras}"`].join(","));
  console.log(exec, r.arquivos, r.linhas, r.problemas, r.sintaxe, por100, regras);
}
fs.writeFileSync(saida, linhasCsv.join("\n") + "\n");
console.log(`\nResultados em ${saida}`);
