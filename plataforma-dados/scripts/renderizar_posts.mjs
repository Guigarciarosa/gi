// Renderiza cada <section> de instagram/posts/posts.html em PNG.
//   node scripts/renderizar_posts.mjs
// Requer Playwright com Chromium (npm i -D playwright && npx playwright install chromium).
import { createRequire } from "node:module";
import { mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const raiz = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const pagina = resolve(raiz, "instagram/posts/posts.html");
const saida = resolve(raiz, "instagram/png");
mkdirSync(saida, { recursive: true });

const navegador = await chromium.launch();
const aba = await navegador.newPage({ viewport: { width: 1200, height: 2000 }, deviceScaleFactor: 1 });
await aba.goto(pathToFileURL(pagina).href);
await aba.evaluate(() => document.fonts.ready);
await aba.waitForTimeout(300);

const ids = await aba.$$eval("section[id]", (els) => els.map((e) => e.id));
for (const id of ids) {
  const el = await aba.$(`#${id}`);
  await el.screenshot({ path: resolve(saida, `${id}.png`) });
  console.log(`instagram/png/${id}.png`);
}
await navegador.close();
