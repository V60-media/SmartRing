# SeeMyHealth: Figma → website build plan

Source: Figma `XKuvVaPoekCESjyfhYw798`, page `2:3` (🎨 Design). Sections in scope: **Dekstop Version** (`11654:10501`) and **Sub Pages** (`11655:13457`).
Mobile Responsive (`11655:18773`) was built later; see `RESPONSIVE_PLAN.md`. The human checkpoints were skipped, as requested.

Target: one multi-file **Claude artifact** with hash routing, plus this source folder.
Stack: plain HTML, CSS and vanilla JS, assembled by `tools/build.py` into `dist/`.
Fidelity: high. Variant frames are built as their **static first state** (per brief).
Typescale: **both sets shipped** with a QC toggle (Cmd/Ctrl + \\). The default is Figma-exact.

## Sitemap (route → Figma frame)

| Route (`#…`) | Page | Figma node | Status |
|---|---|---|---|
| `home` | Homepage | 11654:10502 | ✅ |
| `product` | Product Page, "Live in Clarity" | 11654:11422 | ✅ |
| `product-detail` | Product Detail + sticky add to cart | 11654:12651 (+12104) | ✅ |
| `app` | App Landing, "All One Story" | 11654:14240 | ✅ |
| `business-providers` | For Business (Providers) | 11654:13647 | ✅ |
| `business-insurance` | For Business (Insurance) | 11654:13937 | ✅ |
| `business-distributor` | For Business (Distributor) | 11654:14848 | ✅ |
| `device-demo` | Device Demo | 11654:15484 | ✅ |
| `faq` (+ `faq-products`, `faq-app`, `faq-orders`, `faq-warranty`) | FAQ: 5 tabs | 11655:13591 … 14031 | ✅ |
| `terms` | Terms of service | 11655:13467 | ✅ |
| `privacy` | Privacy Policy | 11655:13534 | ✅ |
| `not-found` (any unknown hash) | 404 Error | 11655:14128 | ✅ |

Overlays (opened from any page):

| Trigger | Overlay | Figma node |
|---|---|---|
| cart icon / Add to Cart | Cart drawer, empty and filled states | 11654:13177 / 11654:13408 |
| "Learn more" (size) | Ring sizing instructions | 11654:12563 |
| `#contact`, "Get in touch", "Become a partner" | Contact us (form) | 11654:13498 / 13573 |
| Device Demo cards | Video pop-up (still frame + controls) | 11654:15608 |

## Layout system
- The design canvas is 1728 px. `html { font-size: clamp(9px, 100vw/108, 17.78px) }`, so **1rem = 16px at 1728**. Every Figma px value is `px / 16` rem, which keeps proportions at every desktop width up to 1920.
- `.canvas` (108rem) hosts art-directed sections. Absolute positions are used only where the Figma composition is free-form (collages, overlapping cards). Lists, grids, cards, FAQ, legal pages and the footer use flex and grid.
- Text boxes are trimmed (`text-box: trim-both cap alphabetic`) to match Figma's cap-height boxes, so spacing values come straight from Figma.
- Container: 1658 px (103.625rem) and a 35 px gutter (2.1875rem).

## Tokens (`src/css/tokens.css`)
Colour: `--color-black #1A1A1A`, `--color-bg-light #F8F2EE`, white, white 10/20/30/40/60 %, black 30/60 %. Footer and sub-pages use `#262626`. Radii 8/16/24 px and a pill. Glass blur 30 px.
Font: **Overused Grotesk** (OFL, self-hosted woff2, weights 400/500/600/700).

### Typescale audit (role → Figma → normalized)
| Role | Figma (size / lh / tracking) | Normalized |
|---|---|---|
| Display D1 | 312 / .88 / −5 % | 300 / .90 / −4.5 % |
| H1 | 128 / 1 / −6 % | 120 / 1.02 / −4.5 % |
| H2 | 96 / 1 / −4 % | 96 / 1.02 / −4 % |
| H3 | 80 / 1 / −4 % | 76 / 1.04 / −4 % |
| H4 | 64 / 1 / −4 % | 60 / 1.06 / −3.5 % |
| H6 | 48 / 1 / −4 % | 48 / 1.08 / −3 % |
| B-XLarge | 40 / 1 / −4 % | 40 / 1.05 / −3 % |
| B-Large | 32 / 1 / −4 % | 32 / 1.1 / −3 % |
| B-Medium | 28 / 1.3 / −4 % | 26 / 1.25 / −3 % |
| B-Small | 24 / 1 / −4 % | 24 / 1.15 / −2.5 % |
| B-Main | 20 / 1.3 / −2 % | 20 / 1.4 / −1 % |
| B-XSmall | 18 / 1.3 / 0 | 18 / 1.4 / 0 |
| Bt1 / Bt2 | 20 SB, 16 M / 1.2 / −4 % | −2 % tracking |
**Decision pending.** Both sets ship. Toggle with Cmd/Ctrl + \\ or the floating switch, then remove `.ts-switch` from `src/index.html` and the unused block in `tokens.css`.

## Components (shared partials)
`nav`, `footer`, `product-tabs`, `glass-store-badges`, `community-body`, `slider-controls-{glass,white}`, `clarity-cards`, `tech-spec-body`, `product-faq`, `ecosystem-cards`, `metrics-body`, `overlays`.
Generated pages: `tools/gen_business.py` (3 business pages), `tools/gen_faq.py`, `tools/gen_legal.py`.

## Link map
Nav: The Ring One → `#product`. Smart Scale, BP Monitor and Smart Flask → `#product-detail` (no dedicated pages in Figma).
Hero CTAs: "Start Your Journey" → `#product`. "Shop Now" → `#product-detail`. "Join Our Community" → `#app`. "Become a partner/distributor" → `#contact`.
Footer: Providers / Insurance / Distributor → business pages. Device Demo → `#device-demo`. FAQ → `#faq`. Order & Shipping → `#faq-orders`. Product Warranty → `#faq-warranty`. Get in touch → `#contact`. Terms → `#terms`. Privacy → `#privacy`.
External: store badges and social icons link to the generic App Store / Google Play / social home pages.

## Assets
About 190 files exported from Figma (`assets/_raw`, not committed, ≈124 MB). They are optimised into `dist/assets/img` (WebP q80, max 2400 px). Mesh gradients are lossless 900 px WebP so they don't band. Icons are SVG. The logo mark and wordmark are inlined SVG, so they recolour via `currentColor`.

## Assumptions and deviations
1. **Variants:** only the first state is built: Product Showcase _2/_3/_4, Health Tracking 1–5, Color Switch, A Day With 1–4, and the business sliders. Slider arrows and dots render but don't page.
2. **Copy fixes:** design copy that names a competitor ("Oura Ring") in the Product Detail FAQ and sizing pop-up was changed to "Ring One". The business testimonial quoted a named, real-sounding physician praising "Oura". It is anonymised to *Clinical Partner*, and the copy says "SeeMyHealth". **Replace it with a real, approved quote.**
3. **Product FAQ answers:** Figma shows only answer 2. The other answers come from the FAQ sub-pages and the spec copy.
4. **Contact** is a drawer overlay, as in Figma (the frame is a 596 px panel), not a standalone page.
5. **Video pop-up:** Figma has no video file, so it shows the still frame with static controls.
6. **No backend:** the forms validate and show an in-page confirmation, and checkout shows a notice. The cart persists in `localStorage`.
7. Partner and hospital logos and claims ("Trusted by top organizations") are kept as designed. Verify the partnerships before publishing externally.
8. Mobile and tablet were added later. See `RESPONSIVE_PLAN.md`. Desktop (≥ 1280) is unchanged.
