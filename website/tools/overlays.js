// usage: node overlays.js <baseurl> <outprefix> [width] — screenshots each overlay open (width defaults to 1152)
const { chromium } = require('playwright');
(async () => {
  const [,, base, prefix, w = '1152'] = process.argv;
  const vw = +w, vh = vw < 768 ? Math.round(vw * 874 / 402) : (vw < 1280 ? Math.round(vw * 4 / 3) : 745);
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: vw, height: vh } });
  const errors = []; p.on('pageerror', e => errors.push(String(e)));
  const shots = [['#product-detail', 'cart', null], ['#product-detail', 'sizing', null], ['#home', 'contact', null], ['#device-demo', 'video', null], ['#product-detail', 'cart', 'add'], ['#home', 'menu', null], ['#product-detail', 'checkout-note', null]];
  for (const [hash, name, mode] of shots) {
    await p.goto(base + hash); await p.waitForTimeout(300);
    if (mode === 'add') { await p.evaluate(() => document.querySelector('.page:not([hidden]) [data-add-to-cart]').click()); await p.evaluate(() => document.querySelectorAll('.page:not([hidden]) .op-card__add')[1].click()); }
    else await p.evaluate(n => { const o = document.getElementById('overlay-' + n); o.classList.add('is-open'); }, name);
    await p.waitForTimeout(500);
    await p.screenshot({ path: `${prefix}-${name}${mode ? '-' + mode : ''}-${vw}.png` });
    await p.evaluate(() => { try { localStorage.clear(); } catch (e) {} });
  }
  console.log(errors.length ? 'ERRORS:\n' + errors.join('\n') : 'no errors');
  await b.close();
})();
