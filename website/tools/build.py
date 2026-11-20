#!/usr/bin/env python3
"""Assemble the SeeMyHealth desktop prototype into dist/ (artifact-ready).

- src/pages/<route>.html   page bodies. First line may be a meta comment:
    <!-- meta title="..." description="..." nav="dark|light|none" footer="yes|no" -->
- src/partials/*.html      shared chunks, included with {{> name}}
- assets/svg/*.svg         inlined with {{svg:name}} (so currentColor works)
- assets/_raw/*            source images from Figma -> optimised into dist/assets/img
"""
import json, os, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC, DIST, ASSETS = ROOT / "src", ROOT / "dist", ROOT / "assets"

# Route order = sitemap order. route -> page file
CSS_FILES = ["tokens.css", "base.css", "components.css", "pages.css", "layout-desktop.css", "layout-flow.css"]
# Breakpoints: single source of truth (mirrored in tokens.css comments and RESPONSIVE_PLAN.md).
CUSTOM_MEDIA = {
    "--bp-mobile": "(max-width: 767.98px)",
    "--bp-tablet": "(min-width: 768px) and (max-width: 1279.98px)",
    "--bp-tablet-up": "(min-width: 768px)",
    "--bp-below-desktop": "(max-width: 1279.98px)",
    "--bp-desktop": "(min-width: 1280px)",
}

ROUTES = [
    "home", "product", "product-detail", "app", "business-providers",
    "business-insurance", "business-distributor", "device-demo",
    "faq", "terms", "privacy", "not-found",
]

META_RE = re.compile(r'<!--\s*meta\s+(.*?)-->', re.S)
ATTR_RE = re.compile(r'(\w+)="([^"]*)"')


def read(p):
    return Path(p).read_text(encoding="utf-8")


SPRITE_DEFS = []
SPRITES = {}   # name -> <symbol> markup; each SVG is defined once and referenced with <use>


def svg(name, cls=""):
    """Inline SVG by reference: the artwork lives once in a hidden sprite (unique ids, small HTML),
    each use is <svg><use href="#i-name"/></svg>, so currentColor still recolours it."""
    raw = read(ASSETS / "svg" / f"{name}.svg")
    raw = re.sub(r'<\?xml.*?\?>', '', raw).strip()
    m = re.match(r'<svg([^>]*)>(.*)</svg>\s*$', raw, re.S)
    root, inner = m.group(1), m.group(2)
    view_box = re.search(r'viewBox="([^"]+)"', root).group(1)
    if name not in SPRITES:
        # masks / clip paths do not resolve reliably from inside a <symbol>: hoist them to sprite-level <defs>
        hoisted = re.findall(r'<mask\b.*?</mask>|<defs>.*?</defs>', inner, re.S)
        for h in hoisted:
            inner = inner.replace(h, "", 1)
        SPRITE_DEFS.extend(re.sub(r'^<defs>|</defs>$', '', h) for h in hoisted)
        SPRITES[name] = f'<symbol id="i-{name}" viewBox="{view_box}">{inner}</symbol>'
    vb = view_box.split()
    # the symbol carries the original viewBox; the referencing <svg> must start at 0 0 or the origin is applied twice
    keep = " ".join(f'{k}="{v}"' for k, v in re.findall(r'([\w:-]+)="([^"]*)"', root) if k not in ("xmlns", "viewBox"))
    keep += f' viewBox="0 0 {vb[2]} {vb[3]}"'
    attrs = f' {keep} aria-hidden="true" focusable="false"'
    if cls:
        attrs += f' class="{cls}"'
    return f'<svg{attrs}><use href="#i-{name}"></use></svg>'


def expand(html, depth=0):
    if depth > 6:
        return html
    html = re.sub(r'\{\{>\s*([\w/-]+)\s*\}\}',
                  lambda m: expand(read(SRC / "partials" / f"{m.group(1)}.html"), depth + 1), html)
    html = re.sub(r'\{\{svg:([\w-]+)(?:\s+class="([^"]*)")?\}\}',
                  lambda m: svg(m.group(1), m.group(2) or ""), html)
    return html


SRCSET_WIDTHS = (480, 960, 1600)   # phone / tablet / small desktop; the full file (<= 2400) is the top candidate
VARIANTS = {}                       # name -> [(width, file), ...] smallest first, plus the full file


def make_variants(full, out):
    """Write name-480/960/1600.webp next to a full-size webp (only widths smaller than the source)."""
    w = int(subprocess.run(["identify", "-format", "%w", str(full)], capture_output=True, text=True, check=True).stdout)
    found = []
    for vw in SRCSET_WIDTHS:
        if vw >= w * 0.9:
            continue
        v = out / f"{full.stem}-{vw}.webp"
        if not v.exists() or v.stat().st_mtime < full.stat().st_mtime:
            subprocess.run(["convert", str(full), "-resize", f"{vw}x", "-quality", "78", "-define", "webp:use-sharp-yuv=true",
                            "-define", "webp:method=6", str(v)], check=True)
        found.append((vw, v.name))
    if found:
        VARIANTS[full.stem] = found + [(w, full.name)]


def optimise_images():
    raw = ASSETS / "_raw"
    out = DIST / "assets" / "img"
    out.mkdir(parents=True, exist_ok=True)
    manifest = {}
    if not raw.exists() or not any(raw.iterdir()):
        # Raw Figma exports are not committed (≈124 MB). Reuse the optimised images in dist/.
        print("  (assets/_raw missing: reusing dist/assets/img)")
        files = {f.stem: f.name for f in out.iterdir() if f.is_file() and not re.search(r"-(480|960|1600)$", f.stem)}
        for stem, name in files.items():
            if name.endswith(".webp") and not stem.startswith(("mesh", "gradient")):
                make_variants(out / name, out)
        return files
    for f in sorted(raw.glob("*")):
        if f.suffix.lower() == ".svg":
            shutil.copy2(f, out / f.name)
            manifest[f.stem] = f.name
            continue
        if f.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp", ".gif"):
            continue
        # keep PNG for images that need alpha (cut-outs); everything else to webp
        target = out / (f.stem + ".webp")
        if not target.exists() or target.stat().st_mtime < f.stat().st_mtime:
            if f.stem.startswith(("mesh", "gradient")):
                # smooth gradients: small lossless file, browser upscaling keeps it band-free
                subprocess.run(["convert", str(f), "-resize", "900x900>", "-define", "webp:lossless=true", str(target)], check=True)
                manifest[f.stem] = target.name
                continue
            subprocess.run(["convert", str(f), "-resize", "2400x2400>", "-quality", "80", "-define", "webp:use-sharp-yuv=true",
                            "-define", "webp:method=6", str(target)], check=True)
        manifest[f.stem] = target.name
        if not f.stem.startswith(("mesh", "gradient")):
            make_variants(target, out)
    return manifest


def build():
    if DIST.exists():
        for p in DIST.iterdir():
            if p.name != "assets":
                shutil.rmtree(p) if p.is_dir() else p.unlink()
    DIST.mkdir(exist_ok=True)
    manifest = optimise_images()
    (DIST / "assets" / "fonts").mkdir(parents=True, exist_ok=True)
    for f in (ASSETS / "fonts").glob("*"):
        shutil.copy2(f, DIST / "assets" / "fonts" / f.name)

    pages, metas = [], {}
    for route in ROUTES:
        p = SRC / "pages" / f"{route}.html"
        if not p.exists():
            print(f"  (skip missing page {route})")
            continue
        body = read(p)
        meta = {}
        m = META_RE.search(body)
        if m:
            meta = dict(ATTR_RE.findall(m.group(1)))
            body = body[:m.start()] + body[m.end():]
        nav = meta.get("nav", "dark")
        parts = []
        if nav != "none":
            parts.append(read(SRC / "partials" / "nav.html").replace("{{navTheme}}", nav))
        parts.append(f'<main id="main-{route}">{body}</main>')
        if meta.get("footer", "yes") == "yes":
            parts.append("{{> footer}}")
        html = expand("\n".join(parts)).replace("{{route}}", route)
        pages.append(f'<div class="page" data-route="{route}" data-nav="{nav}" hidden>\n{html}\n</div>')
        metas[route] = {"title": meta.get("title", "SeeMyHealth"), "description": meta.get("description", "")}

    # image references: {{img:name}} -> assets/img/<file>
    def img(m):
        name = m.group(1)
        if name not in manifest:
            print(f"  !! missing image {name}", file=sys.stderr)
            return f"assets/img/{name}.webp"
        return f"assets/img/{manifest[name]}"

    shell = read(SRC / "index.html")
    shell = shell.replace("{{pages}}", "\n".join(pages))
    shell = shell.replace("{{routeMeta}}", json.dumps(metas))
    shell = expand(shell)
    sprite = ('<svg xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false" '
              'style="position:absolute;width:0;height:0;overflow:hidden">'
              + "<defs>" + "".join(SPRITE_DEFS) + "</defs>" + "".join(SPRITES.values()) + "</svg>")
    shell = shell.replace("<body>", "<body>\n" + sprite, 1)

    def add_srcset(m):
        tag, name = m.group(0), m.group(1)
        if name not in VARIANTS or "srcset=" in tag:
            return tag
        cands = ", ".join(f"assets/img/{f} {w}w" for w, f in VARIANTS[name])
        full_w = VARIANTS[name][-1][0]
        return tag.replace(f'src="{{{{img:{name}}}}}"',
                           f'src="{{{{img:{name}}}}}" srcset="{cands}" sizes="(min-width: 1280px) {full_w}px, 100vw"', 1)
    shell = re.sub(r'<img\b[^>]*?src="\{\{img:([\w-]+)\}\}"[^>]*>', add_srcset, shell)
    shell = re.sub(r'\{\{img:([\w-]+)\}\}', img, shell)
    (DIST / "index.html").write_text(shell, encoding="utf-8")

    css = "\n".join(read(SRC / "css" / f) for f in CSS_FILES)
    for name, query in CUSTOM_MEDIA.items():
        css = css.replace(f"({name})", query)
    leftover = re.findall(r"\(--bp-[\w-]+\)", css)
    assert not leftover, f"unknown custom media: {leftover}"
    css = re.sub(r'\{\{img:([\w-]+)\}\}', img, css)
    (DIST / "site.css").write_text(css, encoding="utf-8")
    shutil.copy2(SRC / "js" / "app.js", DIST / "app.js")

    # remove stale images no longer in _raw
    live = set(manifest.values()) if (ASSETS / "_raw").exists() else {f.name for f in (DIST / "assets" / "img").iterdir()}
    live |= {f for v in VARIANTS.values() for _, f in v}
    for f in (DIST / "assets" / "img").glob("*"):
        if f.name not in live:
            f.unlink()
    total = sum(f.stat().st_size for f in DIST.rglob("*") if f.is_file())
    print(f"built {len(pages)} pages, {len(manifest)} images, {total/1e6:.1f} MB")


if __name__ == "__main__":
    build()
