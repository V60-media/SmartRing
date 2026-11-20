# SeeMyHealth: mobile and tablet responsive plan

Status: **plan, not built yet**. It extends the desktop build described in `BUILD_PLAN.md`.
Figma source: section **Mobile Responsive** (`11655:18773`) in file `XKuvVaPoekCESjyfhYw798`.

## 0. What Figma gives us

| Figma frame | Width | Covers | Node |
|---|---|---|---|
| Homepage_Responsive | 402 | Home: banner + metrics, showcase, benefits collage, health tracking, community, final CTA, footer | 11655:19762 |
| Landing Mobile | 402 | Product page: hero, "Live in Clarity", 4 outcome panels, how it works, colour switch, clarity slider, tech specs, FAQ, CTA, footer | 11655:18774 |
| Color Switch - 4 | 402 | Colour switch, Aurora Gold state | 11655:19732 |
| Mobile type variables | — | `Mobile_Heading/*`, `Mobile_Body Text/*`, `Mobile_Button/*` | bound in 11655:19762 |

**Not in Figma:**
- Tablet frames.
- The opened mobile menu.
- Mobile versions of product detail, app, the three business pages, device demo, FAQ, legal, 404 and all overlays.

This plan derives those from the patterns in the two designed pages, so they look like the same product. Section 9 lists what needs designer sign-off.

---

## 1. Breakpoints and sizing model

| Name | Range | Layout | Design reference |
|---|---|---|---|
| `mobile` | 0–767 px | Single column, swipe carousels | Figma 402 frames (tested 360–767) |
| `tablet` | 768–1279 px | 2-column grids, carousels with 2 items visible | Derived (targets 768, 834, 1024, 1180) |
| `desktop` | ≥ 1280 px | Current build, unchanged | Figma 1728 frames |

The breakpoints are defined once, in `tokens.css`, as custom media names: `--bp-mobile`, `--bp-tablet`, `--bp-desktop`. `tools/build.py` replaces `@media (--bp-tablet)` with the real query at build time, because CSS can't read variables inside media queries. The numbers then live in one place.

**Root size.** Today `html { font-size: clamp(9px, 100vw/108, 17.78px) }`. At 402 px that is 9 px, so desktop body text would render at about 11 px. The new model:

```css
html { font-size: 100%; }                         /* < 1280: 1rem = 16px, respects user zoom */
@media (--bp-desktop) {
  html { font-size: clamp(11.85px, calc(100vw / 108), 17.78px); }  /* desktop: unchanged proportions */
}
```

**Desktop stays pixel-identical.** All desktop geometry moves inside `@media (--bp-desktop)`: `.canvas`, `.abs`, absolute `left`/`top`, fixed widths and fixed section heights. That's 96 `position:absolute` rules and every fixed `height`. Colours, type, borders and image fit stay global. Below 1280, layout is plain flow (flex and grid), written mobile-first. This avoids writing hundreds of "reset absolute" overrides.

---

## 2. Tokens: one set of names, different values per breakpoint

Components keep using **role tokens only** (`--text-h1-size`, `--space-*`, `--gutter`, …). Breakpoints change the values, never the names. The typescale toggle (Figma / normalized) keeps working at every size.

### 2.1 Typescale (size / line-height / tracking)

Mobile **Figma** values come from the Figma mobile variables. *Italic* values are not in Figma and are derived on the same ratio. Tablet sits between mobile and desktop.

| Role | Desktop (Figma) | Tablet | Mobile Figma | Mobile normalized (recommended) |
|---|---|---|---|---|
| D1 display ("Live in Clarity") | 312 / .88 / −5% | *176 / .9 / −5%* | *96 / .9 / −5%* (measured) | 96 / .92 / −4.5% |
| H1 | 128 / 1 / −6% | *80 / 1 / −5%* | **56 / 1 / −6%** | 52 / 1.04 / −4.5% |
| H2 | 96 / 1 / −4% | *64 / 1 / −4%* | **48 / 1 / −4%** | 44 / 1.05 / −4% |
| H3 | 80 / 1 / −4% | *56 / 1 / −4%* | **40 / 1 / −4%** | 38 / 1.06 / −3.5% |
| H4 | 64 / 1 / −4% | *48 / 1 / −4%* | **36 / 1 / −4%** | 34 / 1.08 / −3.5% |
| H5 | 56 / 1 / −4% | *44 / 1 / −4%* | *32 / 1.04 / −4%* | 30 / 1.1 / −3% |
| H6 | 48 / 1 / −4% | *36 / 1.04 / −4%* | **28 / 1.08 / −4%** | 28 / 1.1 / −3% |
| B-XLarge | 40 / 1 / −4% | *30 / 1.05 / −4%* | *24 / 1.1 / −4%* | 24 / 1.15 / −3% |
| B-Large | 32 / 1 / −4% | *24 / 1.1 / −4%* | **20 / 1.12 / −4%** | 20 / 1.2 / −2.5% |
| B-Medium | 28 / 1.3 / −4% | *22 / 1.2 / −4%* | **18 / 1.12 / −4%** | 18 / 1.25 / −2.5% |
| B-Small | 24 / 1 / −4% | *20 / 1.15 / −4%* | **16 / 1.3 / −4%** | 17 / 1.3 / −2% |
| B-Main (body) | 20 / 1.3 / −2% | *17 / 1.4 / −2%* | **14 / 1.3 / −2%** | **16 / 1.45 / −1%** |
| B-XSmall | 18 / 1.3 / 0 | *15 / 1.4 / 0* | **13 / 1.3 / 0** | **14 / 1.45 / 0** |
| Caption | 14 / 1.3 / 0 | *13 / 1.4 / 0* | *12 / 1.35 / 0* | 13 / 1.4 / 0 |
| Bt1 | 20 SB / 1.2 / −4% | *16 / 1.2 / −4%* | **14 SB / 1.2 / −4%** | 16 / 1.2 / −1.5% |
| Bt2 | 16 M / 1.2 / −4% | *14 / 1.2 / −4%* | **13 M / 1.2 / −4%** | 14 / 1.2 / −1% |

**Why normalized on mobile.** Figma's mobile body is 14 px and its secondary text is 13 px, often at 40–60 % white. That is below comfortable reading size on a phone and fails contrast in several places. Also, iOS zooms the page into any form field under 16 px. The recommendation is to ship the **normalized** set as the mobile default and keep Figma values behind the toggle. Whatever is set, **form inputs are always ≥ 16 px**.

Long headings use `text-wrap: balance` and body copy uses `text-wrap: pretty`, so lines don't end on single orphan words on narrow screens.

### 2.2 Layout and spacing

| Token | Mobile | Tablet | Desktop |
|---|---|---|---|
| `--gutter` (page side padding) | **24** (Figma home x=24) | 40 | 35 (unchanged) |
| `--container` | 100% − 2×gutter | 100% − 2×gutter, max 1024 | 1658 |
| `--nav-h` | **85** (Figma) → 64 when condensed on scroll | 80 | 87 |
| `--section-pad-y` | 64 | 96 | as designed |
| `--section-gap` (heading → content) | 32 | 48 | as designed |
| `--card-pad` | 20 | 24 | as designed |
| `--grid-gap` | 12 | 16 | as designed |
| Full-bleed hero / media sections | `min-height: 100svh` (Figma 874 = 402×874 viewport) | `min-height: 80svh` | 1117 |

A new 4-pt spacing scale is shared by all breakpoints: `--space-1…12` = 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96. Mobile and tablet layout uses only these.

The radius tokens keep the same names and px values everywhere (8 / 16 / 24 / pill). They are rem-based, and below 1280 1rem = 16 px, so no new tokens are needed.

### 2.3 Token consistency fixes found during the audit

These need doing even if mobile weren't being built:

| Found | Where | Fix |
|---|---|---|
| Blush pink `#EBB7BA` only exists inside SVG strokes. Mobile uses it for the "Clarity" text and pink "Shop Now" buttons (`#FDDBDD`). | clarity-path SVGs, Figma mobile product | Add `--color-blush-400 #EBB7BA` and `--color-blush-100 #FDDBDD`; add a `btn--blush` variant |
| `#262626` hard-coded ×4 | footer, sub-page surfaces | `--color-surface-footer` |
| `#ebe4e0` ×5 | card and media placeholders, contact details, eco arrows | `--color-sand-200` |
| `#fffbf8` ×4 | light cards | `--color-card-light` |
| `#357090`, `#20230f` | section backgrounds | `--color-section-ocean`, `--color-section-olive` |
| `#b3261e`, `#ff8a80` | form errors (light / dark backgrounds) | `--color-error`, `--color-error-on-dark` |
| `#7a7d86` | muted text | Map to `--color-black-60` or add `--color-muted` |
| Mobile gutters differ: 24 (home), 32 (product nav), ~36 (spec cards) | Figma mobile | One value: `--gutter` = 24 |
| Secondary text at `--color-white-40` on `#1a1a1a` is ≈ 3.8:1, which fails AA for 13–14 px | metric cards, footer, community | Use `--color-white-60` (≈ 6.9:1) for small text; 40 % only for ≥ 24 px or decoration |
| Glass blur 30 / 60 px | `--blur-glass`, `--blur-bg` | Same tokens; reduce to 20 / 30 on mobile for scrolling performance |

`tools/qa.js` will also fail the build if a raw hex appears in `pages.css` or `components.css`, so new hard-coded colours can't creep back in.

---

## 3. Shared components

| Component | Mobile | Tablet | Notes |
|---|---|---|---|
| **Nav** | Logo mark (no wordmark), 44 px cart button, 44 px menu button (Figma). Transparent over hero; solid `#1a1a1a` with blur after 8 px of scroll; condenses to 64 px. | Logo + wordmark, cart, menu button | Desktop links hidden below 1280 |
| **Mobile menu** (needs design) | Full-screen dark sheet. Close button in the same spot as the menu button. Groups: **Products** (Ring One, Smart Scale, Smart Flask, BP Monitor), **App**, **For Business** (Providers, Insurance, Distributor), **Support** (Device Demo, FAQ, Order & Shipping, Warranty). Links at B-Large. A "Shop The Ring One" blush pill and store badges at the bottom. | Same sheet, max-width 480, from the right | `aria-expanded`, focus trap, Esc closes, background `inert`, scroll lock, closes on route change |
| **Buttons** | Pill, min height 48, Bt1. Primary CTAs in a single-column section go full-width (`btn--block`). | Natural width | Variants: white, dark, glass, blush, outline-light/dark |
| **Carousels** (product tabs, clarity cards, testimonials, partners, segments, ecosystem, other products, ring card) | CSS `scroll-snap` with a 24 px peek of the next card (as in Figma "Clarity, day to night" and "Our Partners"). Dots under it with 24 px hit areas; arrows only where Figma shows them. | 2 cards visible | Becomes **interactive** (desktop is static, first state only). No JS needed to swipe; JS only syncs the dots. `role="region"` + `aria-roledescription="carousel"`, arrow keys work |
| **Product tabs** ("01 Ring One  02 Smart Scale …") | Horizontal scroller under the showcase, active underline (Figma) | Same | Tap switches the showcase |
| **Accordion** (FAQ, community features, specs on PD) | Whole row is the button, number + question + ± icon (Figma FAQ) | Same | Already built; only sizes change |
| **Metric cards** (99 %, 85 %, 24/7, 50k+) | Stacked, full width (Figma) | 2 × 2 grid | |
| **Footer** | Figma Footer_Responsive: logo, blurb, 2-column link groups, social, legal links, store badges, full-width watermark, copyright row | 4 columns | Every link gets a 44 px tall hit area (padding, not bigger text) |
| **Store badges** | Side by side, 48 px tall | Same | |
| **Forms** (newsletter, contact) | Inputs 16 px, 48 px tall, correct `type` / `inputmode` / `autocomplete`; errors shown below the field | Same | |

### Overlays

| Overlay | Mobile | Tablet |
|---|---|---|
| Cart | Full-screen sheet (`100dvh`). The header with close button and the footer with total + Checkout both stay visible. Respects `env(safe-area-inset-bottom)`. | 440 px side drawer |
| Contact | Full-screen sheet; the submit button stays visible at the bottom | 480 px side drawer |
| Ring sizing | Full-screen scrollable sheet | Centred modal, max 640 |
| Video | Full-width 16:9; close button 44 px, outside the video; rotating to landscape works | Centred, max 90 vw |

All sheets: `overscroll-behavior: contain`, the page behind is `inert`, Esc and a visible close button both work, and focus returns to the trigger on close (already built).

---

## 4. Page-by-page section map

Legend: **F** = designed in Figma mobile (build to match); **D** = derived from F patterns.

### Home (F: Homepage_Responsive)
| Section | Mobile | Tablet |
|---|---|---|
| Hero | Full-screen swirl image (mobile crop), H1 56 at the bottom left, body, "Start Your Journey" pill, Ring One mini card | Same, H1 80, card at the bottom right |
| Clarity intro + metrics | Hairline, eyebrow, B-XL statement, 4 stacked metric cards | Statement in 2 columns; 2×2 metrics |
| Showcase | Full-screen photo, eyebrow, H2, Shop Now + Learn More, product tabs scroller at the bottom | Same |
| Benefits ("Early Risk Detection") | Collage of 5 photos around the heading, arcs behind. Built as a `%`-positioned aspect-ratio box so it scales 360–767 without overlaps | Same box, wider |
| Health tracking | Eyebrow, H2, body, divider, counter `01 — 06` + dots, image card, title, body. Swipe changes the slide | Image and text side by side |
| Community | Brown gradient; H4 statement with the fade; join pill; accordion (Connect & Meet Up open with photo); testimonial carousel; partners carousel | Accordion + image in 2 columns |
| Final CTA | Full-bleed photo; H2; body; store badges; newsletter field; Ring One card carousel with peek | Same, 2 cards visible |
| Footer | Figma footer | 4 columns |

### Product (F: Landing Mobile)
| Section | Mobile | Tablet |
|---|---|---|
| Hero | Ring visual, eyebrow "The Ring One", H2 "Sensing, made human.", blush Shop Now, caption | Same |
| Live in Clarity | D1 96 centred, "Clarity" in `--color-blush-400`, 3 arcs | D1 176 |
| Outcomes | **4 full-screen panels stacked** (Sleep, …): number + H4 title, glass card with icon, H3, body (Figma 25–28). Desktop shows only the first state; mobile shows all 4 | 2 × 2 grid of glass cards over the image |
| How it works | H3 centred, subtitle, 3 stacked step cards (number, line illustration, title, body) | 3 columns from 900 px, else stacked |
| Colour switch | H3 "Switch The Mood", ring render, 2 chips (Phantom Black / Aurora Gold) that swap the image (Figma Color Switch 1 and 4) | Same, larger render |
| Clarity, day to night | H3, peek carousel of image cards, arrows + dots (Figma) | 2 visible |
| Technical specs | H3, 6 stacked spec cards (icon, title, body, bullets), "What's included" card over a photo (Figma) | 2-column card grid |
| FAQ | H3 centred, accordion card (Figma) | Max 720 centred |
| CTA | Glass card: ring image, eyebrow, H3, body, blush Shop Now; "Zero Friction" line below (Figma) | Card and text side by side |

### Product detail (D)
Gallery as a swipe carousel (1:1) with dots, then the buy panel stacked: name, price, colour swatches (44 px), size chips (44 px) with a "Learn more" sizing link, quantity, full-width Add to Cart.

A **sticky bottom bar** (price + Add to Cart, safe-area aware) appears once the main button scrolls out of view.

Below that, reusing the product-page patterns: clarity carousel, specs as an accordion of 6, app features stacked, FAQ accordion, and "Other products" as a carousel. On tablet, the gallery and buy panel sit in 2 columns.

### App (D)
- **Hero:** H1, store badges.
- **All One Story:** the D1 pattern.
- **A day with:** a vertical timeline (morning → night) on mobile, a carousel on tablet.
- **Tracking:** 7 cards in a 2-column grid on mobile, 3-column on tablet.
- **Data rules:** the home health-tracking pattern.
- **Community and final CTA:** reuse the home sections.

### Business: Providers, Insurance, Distributor (D, one shared pattern)
| Section | Mobile | Tablet |
|---|---|---|
| Hero | Photo, H1, body, full-width "Become a partner" button | Same |
| Value props (3-image collage) | Centre image only + 3 stacked value cards | Collage at 60 % scale + 3-column cards |
| Segments slider | Swipe carousel | 2 visible |
| Ways to work / steps | Numbered vertical list | 2 columns |
| Ecosystem | Card carousel | 2 visible |
| Metrics | Stacked metric cards (home pattern) | 2 × 2 |
| ROI (Insurance, Distributor) | Stacked rows | 2 columns |
| Final CTA | Home final-CTA pattern | |

### Device demo (D)
Demo cards in 1 column on mobile and 2 on tablet. A tap opens the video sheet. Final CTA reused.

### FAQ (D)
Sub-page hero (H2). The five topic tabs become a horizontal chip scroller that **sticks under the nav**; the active chip scrolls into view. Accordion items are full width.

### Terms / Privacy (D)
The hero shrinks to H3 + date. The sidebar table of contents becomes an "On this page" disclosure at the top. Body is 16 / 1.6 with lines capped at 68 characters. A "Back to top" link follows each long section.

### 404 (D)
Centred stack: the large "404" as D1 mobile, body, Home button.

---

## 5. Mobile-friendly and UX rules (acceptance criteria)

1. **Touch targets** are at least 44×44 px, with 8 px between them. Small icons and dots get padding rather than larger artwork.
2. **No sideways scrolling** of the page at 360 px. Only carousels scroll sideways, and they always show a peek.
3. **Readable text:** body ≥ 16 px (normalized set), nothing below 12 px, form inputs ≥ 16 px.
4. **Contrast:** WCAG AA. 4.5:1 for text under 24 px, 3:1 for large text and icons. Photos with text on top get a gradient scrim token.
5. **No fixed section heights below 1280 px.** Sections grow with their content, so large-text settings and landscape phones never clip.
6. **Viewport units:** `svh` for heroes and `dvh` for sheets, so phone browser bars don't cut content off.
7. **Safe areas:** `viewport-fit=cover` plus `env(safe-area-inset-*)` on the nav, the sticky buy bar and sheet footers.
8. **No hover-only information.** Every hover state has a tap or focus equivalent, and `:focus-visible` rings are on everything.
9. **Pinch zoom is allowed:** no `maximum-scale` or `user-scalable=no`.
10. **Motion:** `prefers-reduced-motion` disables smooth scroll, carousel auto-advance and parallax.
11. **Keyboard and screen reader:** the menu, sheets, carousels and tabs have correct roles, labels and focus order. The skip link is kept.
12. **Landscape phones** (e.g. 874×402): heroes switch to `min-height: auto` with padding so content isn't cut off.

---

## 6. Images and performance

- `build.py` writes each photo at **480 / 960 / 1600 / 2400** widths and outputs `srcset` + `sizes`, so phones download about 480–960 px images instead of 2400.
- **Art-directed crops** use `<picture>` with a mobile source wherever the Figma mobile crop differs from desktop: home hero swirl, showcase portrait, product hero ring, outcome photos, CTA photo. These are exported from the 402 frames at 2× and 3×.
- The hero image is preloaded with `fetchpriority="high"`; everything below the fold uses `loading="lazy"` and `decoding="async"`.
- Only the Regular and SemiBold font weights are preloaded.
- **Budgets on a mid-range phone over 4G:** LCP < 2.5 s, CLS < 0.05, home first load ≤ 1.2 MB, Lighthouse mobile Performance ≥ 90 and Accessibility ≥ 95.
- `backdrop-filter` is reduced on mobile (§2.3). If it's unsupported, a solid `--color-white-10` fill is used instead.

---

## 7. Implementation approach

```
src/css/
  tokens.css        + breakpoint names, spacing scale, new colour tokens, mobile and tablet typescale blocks
  base.css          root sizing per breakpoint; .canvas and .abs scoped to desktop
  components.css    mobile-first nav, menu sheet, carousel, overlays, footer
  pages.css         desktop geometry wrapped in @media (--bp-desktop); shared styles stay global
  pages-flow.css    NEW: mobile-first flow layouts per section (< 1280), tablet enhancements inside
src/partials/
  mobile-menu.html  NEW
src/js/app.js       + menu open/close, carousel dot sync, sticky buy bar, nav condense
tools/build.py      + custom-media substitution, responsive srcset, <picture> sources
tools/qa.js         + mobile and tablet viewports, tap-target audit, min font audit, raw-hex lint
```

Markup stays the same where possible. Mobile-only elements (menu, sticky buy bar) are added once in partials. A few sections need a wrapper element so flex and grid can reorder content. **No duplicated content** for mobile versus desktop.

### Phases

| Phase | Work | Size | Exit check |
|---|---|---|---|
| R0 Foundations | Desktop baseline screenshots first. Then tokens per breakpoint, root sizing, desktop-only geometry, custom media in the build, colour tokenisation | M | Desktop pixel-diff vs baseline ≤ 0.1 % at 1280 / 1440 / 1728 / 1920 |
| R1 Shared components | Nav + mobile menu, footer, buttons, carousel, accordion, forms, 4 overlays | M | Components pass the §5 checks at 360 / 402 / 768 / 1024 |
| R2 Figma pages | Home, Product | L | 402 px screenshots match the Figma mobile frames section by section |
| R3 Derived pages | Product detail (+ sticky bar), App, 3 business pages, Device demo | L | §5 checks; design review |
| R4 Sub pages | FAQ, Terms, Privacy, 404 | S | §5 checks |
| R5 Images and performance | srcset, mobile crops, preload | M | §6 budgets |
| R6 QA and publish | Full matrix, fixes, artifact republish, PR | M | All green |

---

## 8. QA matrix

- **Viewports:** 360×780, 390×844, **402×874 (Figma)**, 430×932, 874×402 landscape, 768×1024, 834×1194, 1024×1366, 1024×768, 1180×820. Desktop regression at 1280 / 1440 / 1728 / 1920.
- **Automated (`qa.js`):**
  - no horizontal overflow
  - broken images
  - one h1 per route
  - dead links
  - tap targets ≥ 44 px
  - computed font size ≥ 12 (inputs ≥ 16)
  - no raw hex in component CSS
  - axe-core accessibility scan
- **Visual:** per-section screenshots at 402 compared with the Figma mobile frames (Home, Product); tablet reviewed by eye.
- **Manual:**
  - iOS Safari (real device): safe areas, input zoom, 100svh
  - Android Chrome
  - VoiceOver: menu, sheets, carousels
  - 200 % text zoom
  - Lighthouse mobile

---

## 9. Decisions needed before building

1. **Mobile body size.** Ship the normalized set (body 16 / secondary 14) as the mobile default, or Figma's 14 / 13? *Recommend normalized.* This ties in with the pending typescale decision.
2. **Mobile menu.** Approve the sheet in §3, or have the designer add a frame.
3. **Tablet.** Approve derived rules, or have the designer add 834 px frames for Home and Product.
4. **Tech specs theme.** Mobile Figma uses light cards on sand; desktop uses a dark olive background. Which is the source of truth? *Recommend following each breakpoint's Figma as designed.*
5. **Carousels.** Mobile needs real swiping. Make desktop sliders interactive too, for consistency? *Recommend yes.*
6. **Blush accent.** Confirm `#EBB7BA` / `#FDDBDD` (sampled from Figma) and add them to Figma variables, so Figma and code share the token.
7. **Outcome panels and colour states.** Mobile shows all 4 outcomes and the Aurora Gold state. Confirm their copy (some Figma text is placeholder and repeats).
