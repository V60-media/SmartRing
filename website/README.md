# SeeMyHealth: desktop website prototype

Built from the Figma file `SeeMyHealth_Internal` (Desktop Version and Sub Pages) using the figma-to-website workflow.
See **BUILD_PLAN.md** for the sitemap, tokens, typescale table, link map and assumptions.

## Run locally

```bash
cd website/dist && python3 -m http.server 8765
```

Open http://localhost:8765/#home. Routes are plain hashes: `#product`, `#product-detail`, `#app`, `#business-providers`, `#business-insurance`, `#business-distributor`, `#device-demo`, `#faq`, `#terms`, `#privacy`, `#contact`.

## Rebuild

```bash
python3 website/tools/gen_business.py && python3 website/tools/gen_faq.py && python3 website/tools/gen_legal.py
python3 website/tools/build.py
```

`build.py` inlines partials (`{{> name}}`), SVGs (`{{svg:name}}`) and image paths (`{{img:name}}`) into `dist/index.html`, and concatenates the CSS into `dist/site.css`.
Raw Figma exports (`assets/_raw`) aren't committed. Without them, the build reuses the optimised images already in `dist/assets/img`.

## QA helpers (Playwright)

- `node tools/qa.js http://localhost:8765/`: overflow, broken images, h1 count and dead links on every route at 1280/1440/1920
- `node tools/sections.js <url> <out-prefix> [width]`: one screenshot per section
- `node tools/overlays.js <base-url> <out-prefix>`: cart, sizing, contact and video overlays

## Typescale QC switch

Press Cmd/Ctrl + \ (or use the floating switch) to compare the Figma-exact and normalized type scales. When you've decided, remove the `.ts-switch` block from `src/index.html` and the unused set in `src/css/tokens.css`.
