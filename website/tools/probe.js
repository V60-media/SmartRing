// usage: node probe.js <route> <width> "<selector>" ...  — prints box metrics for debugging layouts
const { chromium } = require('playwright');
(async () => {
  const [,, route, w, ...sels] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: +w, height: Math.round(+w * 874 / 402) } });
  await p.goto(`http://localhost:8765/#${route}`); await p.waitForTimeout(300);
  for (const s of sels) {
    const r = await p.evaluate(s => [...document.querySelectorAll('.page:not([hidden]) ' + s)].slice(0, 6).map(e => { const r = e.getBoundingClientRect(); const cs = getComputedStyle(e); return `${Math.round(r.left)},${Math.round(r.top + scrollY)} ${Math.round(r.width)}x${Math.round(r.height)} pos=${cs.position} disp=${cs.display} fs=${cs.fontSize}`; }), s);
    console.log(s, '\n  ' + r.join('\n  '));
  }
  await b.close();
})();
