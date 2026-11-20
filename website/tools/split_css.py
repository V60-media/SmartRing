"""One-off migration: split src/css/pages.css into
   pages.css            skin (colour, type, radius, fit, overlays) – applies at every size
   layout-desktop.css   geometry (absolute positions, fixed rem sizes, spacing) – desktop only

Declarations keep their original order inside each file. A property is either skin or
geometry for a given rule, and the desktop file is loaded after pages.css, so the
computed desktop styles are unchanged (verified by the pixel-diff in tools/regress.sh).
"""
import re
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src" / "css"
text = (SRC / "pages.css").read_text()
text = re.sub(r"\{\{img:([\w-]+)\}\}", r"@@IMG:\1@@", text)

REM = re.compile(r"-?\d*\.?\d+(rem|px)")
ZEROISH = re.compile(r"^(0|auto|0 0|0 auto|auto 0)(\s+(0|auto))*$")

def is_geometry(prop, val, rule_decls):
    v = val.strip()
    overlay = rule_decls.get("inset", "").strip() == "0"
    if prop == "position":
        return v == "absolute" and not overlay
    if prop in ("left", "right", "top", "bottom"):
        if overlay:
            return False
        # full-width overlays (left:0; right:0) stay global
        if v == "0" and rule_decls.get("left", "").strip() == "0" and rule_decls.get("right", "").strip() == "0" and prop in ("left", "right"):
            return False
        return True
    if prop == "inset":
        return v != "0"
    if prop in ("width", "height", "min-height", "max-height", "min-width", "flex-basis"):
        return bool(REM.search(v)) or "var(--section-h)" in v or "var(--container)" in v
    if prop == "max-width":
        return True
    if prop.startswith("margin") or prop.startswith("padding"):
        return True  # all spacing is desktop geometry (keeps reset order intact)
    if prop in ("gap", "row-gap", "column-gap", "grid-template-columns", "grid-template-rows", "text-indent"):
        return True
    if prop == "transform":
        return "translate" in v
    if prop == "white-space":
        return v == "nowrap"
    if prop in ("font-size", "line-height", "letter-spacing"):
        return bool(REM.search(v))
    if prop == "justify-content":
        return v == "space-between" and False
    return False

out_skin, out_geo = [], []
pos = 0
for m in re.finditer(r"(/\*.*?\*/)|([^{}]+)\{([^{}]*)\}", text, re.S):
    if m.group(1):
        out_skin.append(m.group(1)); out_geo.append(m.group(1))
        continue
    sel, body = m.group(2).strip(), m.group(3)
    decls = []
    for d in body.split(";"):
        if ":" not in d:
            continue
        p, v = d.split(":", 1)
        decls.append((p.strip(), v.strip()))
    lookup = {p: v for p, v in decls}
    skin = [f"{p}: {v}" for p, v in decls if not is_geometry(p, v, lookup)]
    geo = [f"{p}: {v}" for p, v in decls if is_geometry(p, v, lookup)]
    if skin:
        out_skin.append(f"{sel} {{ {'; '.join(skin)}; }}")
    if geo:
        out_geo.append(f"{sel} {{ {'; '.join(geo)}; }}")

def clean(lines):
    # drop comment lines that end up with no rules after them in a file
    res = []
    for i, l in enumerate(lines):
        if l.startswith("/*"):
            nxt = next((x for x in lines[i + 1:] if not x.startswith("/*")), None)
            if nxt is None:
                continue
        res.append(l)
    return "\n".join(res)

header = "/* ==========================================================================\n   Section skin: colour, type, radius, image fit. Applies at every breakpoint.\n   Desktop geometry lives in layout-desktop.css; mobile/tablet flow in layout-flow.css.\n   ========================================================================== */\n"
unimg = lambda t: re.sub(r"@@IMG:([\w-]+)@@", r"{{img:\1}}", t)
(SRC / "pages.css").write_text(header + unimg(clean(out_skin[1:])) + "\n")
(SRC / "layout-desktop.css").write_text(
    "/* ==========================================================================\n   Desktop geometry (>= 1280px). Rem = Figma px / 16 on the 1728px canvas.\n   ========================================================================== */\n@media (--bp-desktop) {\n"
    + unimg(clean(out_geo[1:])) + "\n}\n")
print(len(out_skin), len(out_geo))
