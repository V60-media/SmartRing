# SeeMyHealth: website prototype (desktop, tablet, mobile)

Built from the Figma file `SeeMyHealth_Internal` using the figma-to-website workflow:
Desktop Version and Sub Pages (1728 px) plus Mobile Responsive (402 px). Tablet is derived.

- **BUILD_PLAN.md**: desktop sitemap, tokens, typescale table, link map and assumptions
- **RESPONSIVE_PLAN.md**: breakpoints, per-breakpoint tokens, the section map for all 12 pages, the mobile UX rules, and what was built versus planned (§10)

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

`build.py` does the following:
- Inlines partials (`{{> name}}`) and image paths (`{{img:name}}`).
- Defines each SVG once in a hidden sprite and references it with `{{svg:name}}` → `<use>`, so `currentColor` still works.
- Replaces the breakpoint names (`@media (--bp-mobile)` etc.) with real media queries.
- Writes 480 / 960 / 1600 px `srcset` versions of every photo.

Raw Figma exports (`assets/_raw`) aren't committed. Without them, the build reuses the optimised images already in `dist/assets/img`.

## CSS layout

| File | Applies at | Contents |
|---|---|---|
| `tokens.css` | all | Colours, spacing scale, radii, and three typescale blocks (desktop / tablet / mobile) |
| `base.css` | all | Reset and type roles. The rem root is 16 px below 1280 and scales with the 1728 canvas above |
| `components.css` | all | Nav, buttons, footer, overlays, accordion and forms |
| `pages.css` | all | Section skin: colour, type, radius, image fit |
| `layout-desktop.css` | ≥ 1280 | Desktop geometry: absolute positions and fixed sizes from the 1728 frames |
| `layout-flow.css` | < 1280 | Mobile-first flow layouts, with tablet enhancements in `(--bp-tablet)` blocks |

Breakpoints: `--bp-mobile` 0–767, `--bp-tablet` 768–1279, `--bp-desktop` ≥ 1280. They are defined in `tools/build.py` (`CUSTOM_MEDIA`).

## QA helpers (Playwright)

- `node tools/qa.js [base-url] [widths]` runs every route at 11 widths (360 to 1920) and checks:
  - overflow, broken images, the h1 count and dead links
  - below 1280: tap targets ≥ 44 px, text ≥ 12 px and form fields ≥ 16 px
  - no raw hex colours in component CSS
- `tools/regress.sh <baseline-dir> <work-dir>`: desktop pixel regression against full-page baselines from `node tools/fullshots.js <dir> 1280,1728`
- `node tools/interact.js`: menu, focus return, scroll state, carousels (swipe and desktop arrows), colour swap, sticky add-to-cart
- `node tools/fullshots.js <dir> <widths> [routes]`: full-page screenshots
- `node tools/overlays.js <base-url> <out-prefix> [width]`: every overlay
- `node tools/weight.js <route> <width> <dpr>`: bytes downloaded after scrolling the page
- `node tools/probe.js <route> <width> <selector>…`: box metrics for debugging

`tools/split_css.py` is the one-off migration that split the original `pages.css` into skin and desktop geometry. Don't re-run it.

## Typescale QC switch

Press Cmd/Ctrl + \ (or use the floating switch) to cycle between:
- **Auto** (default): Figma sizes on desktop and tablet, the readable set on phones
- **Figma**: Figma sizes everywhere, including Figma's mobile variables
- **Normalized**: the normalized set everywhere

When you've decided, remove the `.ts-switch` block from `src/index.html` and the unused sets in `src/css/tokens.css`.
