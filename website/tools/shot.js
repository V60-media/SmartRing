// usage: node shot.js <url-or-file> <out.png> [width] [height] [fullPage] [scale]
const { chromium } = require('playwright');
(async () => {
  const [,, target, out, w = '1440', h = '900', full = '0', scale = '1'] = process.argv;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: +scale });
  const errors = [];
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', e => errors.push(String(e)));
  const url = /^(https?|file):/.test(target) ? target : 'file://' + require('path').resolve(target);
  await page.goto(url, { waitUntil: 'load' });
  await page.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 600) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); } window.scrollTo(0, 0); });
  await page.waitForTimeout(800);
  await page.screenshot({ path: out, fullPage: full === '1' });
  if (errors.length) console.log('ERRORS:\n' + errors.join('\n'));
  await browser.close();
})();
