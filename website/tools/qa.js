// DOM QA: overflow, broken images, console errors, dead hash links, h1 count, per route & width
const { chromium } = require('playwright');
(async () => {
  const base = process.argv[2] || 'http://localhost:8765/';
  const b = await chromium.launch();
  const routes = ['home','product','product-detail','app','business-providers','business-insurance','business-distributor','device-demo','faq','terms','privacy','not-found'];
  let problems = 0;
  for (const w of [1280, 1440, 1920]) {
    const p = await b.newPage({ viewport: { width: w, height: 900 } });
    const errors = []; p.on('pageerror', e => errors.push(String(e))); p.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
    for (const r of routes) {
      await p.goto(base + '#' + r); await p.waitForTimeout(150);
      await p.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 900) { scrollTo(0, y); await new Promise(r => setTimeout(r, 30)); } scrollTo(0, 0); });
      await p.waitForTimeout(400);
      const res = await p.evaluate(() => {
        const page = document.querySelector('.page:not([hidden])');
        const out = { route: page.dataset.route, overflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth };
        out.brokenImgs = [...page.querySelectorAll('img')].filter(i => i.complete && i.naturalWidth === 0).map(i => i.getAttribute('src'));
        out.h1 = page.querySelectorAll('h1').length;
        const routes = [...document.querySelectorAll('.page')].map(p => p.dataset.route).concat(['contact','faq-general','faq-products','faq-app','faq-orders','faq-warranty']);
        out.deadLinks = [...new Set([...page.querySelectorAll('a[href^="#"]')].map(a => a.getAttribute('href').slice(1)).filter(h => h && !routes.includes(h) && !document.getElementById(h)))];
        out.emptyLinks = [...page.querySelectorAll('a[href=""], a:not([href])')].length;
        return out;
      });
      const bad = res.overflowX > 0 || res.brokenImgs.length || res.h1 !== 1 || res.deadLinks.length || res.emptyLinks;
      if (bad) { problems++; console.log(w, JSON.stringify(res)); }
    }
    if (errors.length) { problems++; console.log(w, 'console errors:', [...new Set(errors)].join(' | ')); }
    await p.close();
  }
  console.log(problems ? `${problems} problem(s)` : 'all routes clean at 1280/1440/1920');
  await b.close();
})();
