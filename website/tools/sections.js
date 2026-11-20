// usage: node sections.js <url> <outprefix> [width] — one viewport screenshot per top-level <section>
const { chromium } = require('playwright');
(async () => {
  const [,, url, prefix, w = '1728'] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: +w, height: Math.round(+w * 1117 / 1728) } });
  const errors = []; p.on('pageerror', e => errors.push(String(e))); p.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  await p.goto(url); await p.waitForTimeout(300);
  const n = await p.evaluate(() => document.querySelectorAll('.page:not([hidden]) main > section, .page:not([hidden]) > footer').length);
  for (let i = 0; i < n; i++) {
    await p.evaluate(i => { const s = document.querySelectorAll('.page:not([hidden]) main > section, .page:not([hidden]) > footer')[i]; window.scrollTo(0, s.getBoundingClientRect().top + scrollY); }, i);
    await p.waitForTimeout(500);
    await p.screenshot({ path: `${prefix}-${String(i).padStart(2, '0')}.png`, scale: 'css' });
  }
  console.log(n + ' sections' + (errors.length ? '\nERRORS:\n' + errors.join('\n') : ''));
  await b.close();
})();
