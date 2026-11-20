// usage: node fullshots.js <outdir> <width>[,<width>...] [route,...]
// Full-page screenshot of every route (and key overlays) with lazy images forced to load.
// Used as the desktop regression baseline and for mobile/tablet review.
const { chromium } = require('playwright');
const fs = require('fs');
const ROUTES = ['home', 'product', 'product-detail', 'app', 'business-providers', 'business-insurance',
  'business-distributor', 'device-demo', 'faq', 'terms', 'privacy', 'not-found'];
(async () => {
  const [,, out, widths = '1728', only] = process.argv;
  const routes = only ? only.split(',') : ROUTES;
  fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch();
  const errors = [];
  for (const w of widths.split(',').map(Number)) {
    const h = w >= 1280 ? Math.round(w * 1117 / 1728) : (w < 768 ? Math.round(w * 874 / 402) : Math.round(w * 4 / 3));
    const p = await b.newPage({ viewport: { width: w, height: h } });
    p.on('pageerror', e => errors.push(`${w} ${e}`));
    for (const r of routes) {
      await p.goto(`http://localhost:8765/#${r}`);
      await p.evaluate(() => { localStorage.clear(); document.querySelectorAll('img[loading=lazy]').forEach(i => { i.loading = 'eager'; }); });
      await p.waitForLoadState('networkidle');
      await p.evaluate(() => Promise.all([...document.images].filter(i => !i.complete).map(i => new Promise(r => { i.onload = i.onerror = r; }))));
      await p.waitForTimeout(250);
      await p.screenshot({ path: `${out}/${r}-${w}.png`, fullPage: true, scale: 'css', animations: 'disabled' });
    }
    await p.close();
  }
  console.log('done' + (errors.length ? '\nERRORS:\n' + errors.join('\n') : ''));
  await b.close();
})();
