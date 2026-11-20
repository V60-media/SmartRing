// DOM QA per route & width: overflow, broken images, console errors, dead hash links, h1 count,
// plus on phone/tablet widths: tap targets >= 44px, text >= 12px, form fields >= 16px.
// Also lints component CSS for raw hex colours (tokens only).
// usage: node qa.js [baseUrl] [widths]   e.g. node qa.js http://localhost:8765/ 360,402,834,1280
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
(async () => {
  const base = process.argv[2] || 'http://localhost:8765/';
  const widths = (process.argv[3] || '360,390,402,430,768,834,1024,1180,1280,1440,1920').split(',').map(Number);
  const routes = ['home', 'product', 'product-detail', 'app', 'business-providers', 'business-insurance', 'business-distributor', 'device-demo', 'faq', 'terms', 'privacy', 'not-found'];
  let problems = 0;

  // token lint: no raw hex in section/component CSS
  for (const f of ['pages.css', 'components.css', 'layout-flow.css', 'layout-desktop.css']) {
    const css = fs.readFileSync(path.join(__dirname, '..', 'src', 'css', f), 'utf8');
    const hex = css.match(/#[0-9a-fA-F]{3,8}\b/g);
    if (hex) { problems++; console.log(`lint ${f}: raw hex ${[...new Set(hex)].join(' ')}`); }
  }

  const b = await chromium.launch();
  for (const w of widths) {
    const h = w < 768 ? Math.round(w * 874 / 402) : 900;
    const p = await b.newPage({ viewport: { width: w, height: h }, hasTouch: w < 1280 });
    const errors = []; p.on('pageerror', e => errors.push(String(e))); p.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
    for (const r of routes) {
      await p.goto(base + '#' + r); await p.waitForTimeout(150);
      await p.evaluate(async (h) => { for (let y = 0; y < document.body.scrollHeight; y += h) { scrollTo(0, y); await new Promise(r => setTimeout(r, 30)); } scrollTo(0, 0); }, h);
      await p.waitForTimeout(400);
      const res = await p.evaluate((w) => {
        const page = document.querySelector('.page:not([hidden])');
        const out = { route: page.dataset.route, overflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth };
        out.brokenImgs = [...page.querySelectorAll('img')].filter(i => i.complete && i.naturalWidth === 0).map(i => i.getAttribute('src'));
        out.h1 = page.querySelectorAll('h1').length;
        const routes = [...document.querySelectorAll('.page')].map(p => p.dataset.route).concat(['contact', 'faq-general', 'faq-products', 'faq-app', 'faq-orders', 'faq-warranty']);
        out.deadLinks = [...new Set([...page.querySelectorAll('a[href^="#"]')].map(a => a.getAttribute('href').slice(1)).filter(h => h && !routes.includes(h) && !document.getElementById(h)))];
        out.emptyLinks = [...page.querySelectorAll('a[href=""], a:not([href])')].length;
        const visible = el => { const r = el.getBoundingClientRect(); const cs = getComputedStyle(el); return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none' && !el.closest('[aria-hidden="true"]'); };
        if (w < 1280) {
          // tap targets: interactive elements smaller than 44px in both dimensions (inline text links excluded)
          out.smallTargets = [...page.querySelectorAll('a[href], button, [role=tab], input, select, textarea')]
            .filter(visible)
            .filter(el => !el.closest('p, li > p, .legal__body, .faq-qa__a, .accordion__panel') || el.matches('button'))
            .filter(el => { const r = el.getBoundingClientRect(); return r.height < 43.5 && r.width < 43.5 || r.height < 24 || r.width < 24; })
            .map(el => `${el.tagName.toLowerCase()}.${[...el.classList].join('.')}:${Math.round(el.getBoundingClientRect().width)}x${Math.round(el.getBoundingClientRect().height)}`);
          out.smallTargets = [...new Set(out.smallTargets)].slice(0, 8);
          // minimum text size
          const walker = document.createTreeWalker(page, NodeFilter.SHOW_TEXT);
          const tiny = new Set();
          while (walker.nextNode()) {
            const t = walker.currentNode; if (!t.textContent.trim()) continue;
            const el = t.parentElement; if (!visible(el) || el.closest('.store-badge')) continue; // official badge artwork; link has an aria-label
            const fs = parseFloat(getComputedStyle(el).fontSize);
            if (fs < 12) tiny.add(`${el.tagName.toLowerCase()}.${[...el.classList].join('.')}:${fs}px`);
          }
          out.tinyText = [...tiny].slice(0, 8);
          out.smallInputs = [...page.querySelectorAll('input:not([type=checkbox]), select, textarea')].filter(visible)
            .filter(i => parseFloat(getComputedStyle(i).fontSize) < 16).map(i => i.id || i.name);
        }
        return out;
      }, w);
      const bad = res.overflowX > 0 || res.brokenImgs.length || res.h1 !== 1 || res.deadLinks.length || res.emptyLinks ||
        (res.smallTargets && res.smallTargets.length) || (res.tinyText && res.tinyText.length) || (res.smallInputs && res.smallInputs.length);
      if (bad) {
        problems++;
        const show = Object.fromEntries(Object.entries(res).filter(([k, v]) => k === 'route' || (Array.isArray(v) ? v.length : (k === 'h1' ? v !== 1 : v))));
        console.log(w, JSON.stringify(show));
      }
    }
    if (errors.length) { problems++; console.log(w, 'console errors:', [...new Set(errors)].join(' | ')); }
    await p.close();
  }
  console.log(problems ? `${problems} problem(s)` : `all routes clean at ${widths.join('/')}`);
  await b.close();
  process.exit(problems ? 1 : 0);
})();
