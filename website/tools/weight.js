// usage: node weight.js <route> <width> <dpr> — total bytes fetched after scrolling the whole page
const { chromium } = require('playwright');
(async () => {
  const [,, route = 'home', w = '390', dpr = '3'] = process.argv;
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: +w, height: Math.round(+w * 2.17) }, deviceScaleFactor: +dpr });
  const p = await ctx.newPage(); let bytes = 0, imgs = 0;
  p.on('response', async r => { try { const buf = await r.body(); bytes += buf.length; if (r.request().resourceType() === 'image') imgs += buf.length; } catch (e) {} });
  await p.goto(`http://localhost:8765/#${route}`); await p.waitForLoadState('networkidle');
  await p.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 600) { scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); } });
  await p.waitForLoadState('networkidle'); await p.waitForTimeout(500);
  console.log(`${route} @${w}x${dpr}: total ${(bytes / 1e6).toFixed(2)} MB, images ${(imgs / 1e6).toFixed(2)} MB`);
  await b.close();
})();
