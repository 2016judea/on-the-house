// Driven by send_demolition.sh. One connect for the whole run.
import { createRequire } from "node:module";
import { readFileSync, writeFileSync } from "node:fs";
const require = createRequire(process.env.NODE_PATH + "/");
const puppeteer = require("puppeteer-core");

const HERE = process.argv[2];
const msgs = JSON.parse(readFileSync(`${HERE}/messages_demolition.json`, "utf8"));
const csvPath = `${HERE}/tokens_demolition.csv`;
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
const BLOCK = /checkpoint|captcha|security check|you can't message|you're temporarily blocked|confirm (it's|that it's) you|we limit how often/i;

const browser = await puppeteer.connect({ browserURL: "http://localhost:9491", defaultViewport: { width: 1280, height: 900 } });
const page = (await browser.pages())[0];
const sent = {};

for (const [i, m] of msgs.entries()) {
  const url = `https://www.facebook.com/marketplace/item/${m.item_id}/`;
  if (i > 0) await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 });
  await wait(6000);
  const body = await page.evaluate(() => document.body.innerText);
  if (BLOCK.test(body) || /checkpoint/.test(page.url())) { console.log("STOP gate on", m.seller, page.url()); break; }
  // the seller box: a textarea (or textbox) prefilled "Is this available?"
  const box = await page.evaluateHandle(() =>
    [...document.querySelectorAll('textarea, [role="textbox"]')].find((el) => /available/i.test(el.value || el.textContent || el.getAttribute("placeholder") || "")) ||
    document.querySelector('textarea'));
  if (!box || !(await box.asElement())) { console.log("SKIP no message box", m.seller); await page.screenshot({ path: `${HERE}/shots/${m.token}_nobox.png` }); continue; }
  await box.asElement().click({ clickCount: 3 });
  await page.keyboard.down("Meta"); await page.keyboard.press("a"); await page.keyboard.up("Meta");
  await page.keyboard.press("Backspace");
  // newlines as Shift+Enter so Enter never sends half a message
  const parts = m.message_text.split("\n");
  for (const [k, line] of parts.entries()) {
    await page.keyboard.type(line, { delay: 8 });
    if (k < parts.length - 1) { await page.keyboard.down("Shift"); await page.keyboard.press("Enter"); await page.keyboard.up("Shift"); }
  }
  await page.screenshot({ path: `${HERE}/shots/${m.token}_typed.png` });
  const clicked = await page.evaluate(() => {
    const b = [...document.querySelectorAll('[role="button"], button')].find((el) => /^send( message)?$/i.test((el.getAttribute("aria-label") || el.innerText || "").trim()));
    if (b) { b.click(); return true; } return false;
  });
  if (!clicked) { console.log("SKIP no Send button", m.seller); continue; }
  await wait(8000);
  await page.screenshot({ path: `${HERE}/shots/${m.token}_sent.png` });
  const after = await page.evaluate(() => document.body.innerText);
  if (BLOCK.test(after)) { console.log("STOP gate after send", m.seller); break; }
  // verify: the token URL now shows on the page (the item page swaps to "Message sent" / the thread)
  const ok = after.includes(m.token) || /message sent|view (conversation|message)/i.test(after);
  console.log(ok ? "SENT" : "UNVERIFIED", m.seller);
  if (ok) sent[m.token] = new Date().toISOString();
  if (i < msgs.length - 1) await wait(60000);
}
browser.disconnect();

// write sent_at back into the ledger (only for verified sends)
const lines = readFileSync(csvPath, "utf8");
let out = lines;
for (const [tok, at] of Object.entries(sent)) out = out.replace(new RegExp(`(,${tok},[^,]+,)(,)`), `$1${at}$2`);
writeFileSync(csvPath, out);
console.log(JSON.stringify(sent));
