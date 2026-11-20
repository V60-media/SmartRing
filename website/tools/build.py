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
ROUTES = [
    "home", "product", "product-detail", "app", "business-providers",
    "business-insurance", "business-distributor", "device-demo",
    "faq", "terms", "privacy", "not-found",
]

META_RE = re.compile(r'<!--\s*meta\s+(.*?)-->', re.S)
ATTR_RE = re.compile(r'(\w+)="([^"]*)"')


def read(p):
    return Path(p).read_text(encoding="utf-8")


def svg(name, cls=""):
    s = read(ASSETS / "svg" / f"{name}.svg")
    s = re.sub(r'<\?xml.*?\?>', '', s).strip()
    attrs = ' aria-hidden="true" focusable="false"'
    if cls:
        attrs += f' class="{cls}"'
    return s.replace("<svg", "<svg" + attrs, 1)


def expand(html, depth=0):
    if depth > 6:
        return html
    html = re.sub(r'\{\{>\s*([\w/-]+)\s*\}\}',
                  lambda m: expand(read(SRC / "partials" / f"{m.group(1)}.html"), depth + 1), html)
    html = re.sub(r'\{\{svg:([\w-]+)(?:\s+class="([^"]*)")?\}\}',
                  lambda m: svg(m.group(1), m.group(2) or ""), html)
    return html


def optimise_images():
    raw = ASSETS / "_raw"
    out = DIST / "assets" / "img"
    out.mkdir(parents=True, exist_ok=True)
    manifest = {}
    if not raw.exists() or not any(raw.iterdir()):
        # Raw Figma exports are not committed (≈124 MB). Reuse the optimised images in dist/.
        print("  (assets/_raw missing: reusing dist/assets/img)")
        return {f.stem: f.name for f in out.iterdir() if f.is_file()}
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
    shell = re.sub(r'\{\{img:([\w-]+)\}\}', img, shell)
    (DIST / "index.html").write_text(shell, encoding="utf-8")

    css = "\n".join(read(SRC / "css" / f) for f in ["tokens.css", "base.css", "components.css", "pages.css"])
    css = re.sub(r'\{\{img:([\w-]+)\}\}', img, css)
    (DIST / "site.css").write_text(css, encoding="utf-8")
    shutil.copy2(SRC / "js" / "app.js", DIST / "app.js")

    # remove stale images no longer in _raw
    live = set(manifest.values()) if (ASSETS / "_raw").exists() else {f.name for f in (DIST / "assets" / "img").iterdir()}
    for f in (DIST / "assets" / "img").glob("*"):
        if f.name not in live:
            f.unlink()
    total = sum(f.stat().st_size for f in DIST.rglob("*") if f.is_file())
    print(f"built {len(pages)} pages, {len(manifest)} images, {total/1e6:.1f} MB")


if __name__ == "__main__":
    build()
