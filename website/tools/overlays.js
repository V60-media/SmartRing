// usage: node overlays.js <baseurl> <outprefix> — screenshots each overlay open
const { chromium } = require('playwright');
(async () => {
  const [,, base, prefix] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1152, height: 745 } });
  const errors = []; p.on('pageerror', e => errors.push(String(e)));
  const shots = [['#product-detail', 'cart', null], ['#product-detail', 'sizing', null], ['#home', 'contact', null], ['#device-demo', 'video', null], ['#product-detail', 'cart', 'add']];
  for (const [hash, name, mode] of shots) {
    await p.goto(base + hash); await p.waitForTimeout(300);
    if (mode === 'add') { await p.evaluate(() => document.querySelector('.page:not([hidden]) [data-add-to-cart]').click()); await p.evaluate(() => document.querySelectorAll('.page:not([hidden]) .op-card__add')[1].click()); }
    else await p.evaluate(n => { const o = document.getElementById('overlay-' + n); o.classList.add('is-open'); }, name);
    await p.waitForTimeout(500);
    await p.screenshot({ path: `${prefix}-${name}${mode ? '-' + mode : ''}.png` });
    await p.evaluate(() => { try { localStorage.clear(); } catch (e) {} });
  }
  console.log(errors.length ? 'ERRORS:\n' + errors.join('\n') : 'no errors');
  await b.close();
})();
