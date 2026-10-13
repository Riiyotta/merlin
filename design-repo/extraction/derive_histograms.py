#!/usr/bin/env python3 -I
"""Derive token-evidence histograms from the source project's compiled CSS.

The source project ships no color/type histogram, so this script derives one:
it counts color values, font-size / font-weight / font-family / line-height,
border-radius, box-shadow, transition/animation timing and @media breakpoints
in the site's own CSS (src/styles/original/*.css and src/styles/*.css).

Run:  python3 -I extraction/derive_histograms.py [--source <project root>] [--write]

The source tree is located as the PARENT of this design-repo (derived from
__file__, never hard-coded). When it is absent the script prints a WARNING and
exits 0, leaving the checked-in extraction/derived-histograms.json untouched, so
the design-repo stays verifiable on its own (graceful degradation).

Scope notes (honest limits):
  * 437c25afc566ca52.css is the Mantine UI base bundle (179 KB). Almost none of
    it is used by the site; it is tallied separately under "vendor" so it cannot
    skew the site histograms. Only ~6 of its base rules matter (CLONE_SPEC §0).
  * Counts are DECLARATION OCCURRENCES in the CSS text, not rendered-element
    counts. They rank how much of the stylesheet uses a value; computed values
    recorded in the CLONE_SPEC files are the cross-check (see tokens/*).
"""
import argparse, collections, glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DEFAULT_SOURCE = os.path.dirname(REPO)
OUT = os.path.join(HERE, "derived-histograms.json")
VENDOR = {"437c25afc566ca52.css"}

DECL = re.compile(r"(--[\w-]+|[a-z-]+)\s*:\s*([^;{}]+)")
HEX = re.compile(r"#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})\b")
RGB = re.compile(r"rgba?\(\s*\d[^)]*\)")
MEDIA = re.compile(r"@media[^{]*")
BP = re.compile(r"(max|min)-width\s*:\s*([\d.]+)(px|em)")
EASE = re.compile(r"cubic-bezier\([^)]*\)|\bease-in-out\b|\bease-out\b|\bease-in\b|\bease\b|\blinear\b|\bstep-end\b")
DUR = re.compile(r"(?<![\w.#-])(\d*\.?\d+)(ms|s)\b")


def norm_hex(h):
    h = h.lower()
    if len(h) == 4:
        h = "#" + "".join(c * 2 for c in h[1:])
    return h


def collect(files):
    out = {k: collections.Counter() for k in [
        "color", "color_by_property", "fontSize", "fontWeight", "fontFamily", "lineHeight",
        "letterSpacing", "borderRadius", "boxShadow", "transitionDuration", "easing", "breakpoint"]}
    by_prop = collections.defaultdict(collections.Counter)
    for path in files:
        css = open(path, encoding="utf-8", errors="replace").read()
        css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
        css = re.sub(r"url\([^)]*\)", "url()", css)  # data URIs would pollute color counts
        for m in MEDIA.finditer(css):
            for kind, val, unit in BP.findall(m.group(0)):
                px = float(val) * (16 if unit == "em" else 1)
                out["breakpoint"][f"{kind}-width:{px:g}px"] += 1
        for prop, val in DECL.findall(css):
            val = val.strip()
            if prop in ("font-size",):
                out["fontSize"][val] += 1
            elif prop == "font-weight":
                out["fontWeight"][val] += 1
            elif prop == "font-family":
                out["fontFamily"][val] += 1
            elif prop == "line-height":
                out["lineHeight"][val] += 1
            elif prop == "letter-spacing":
                out["letterSpacing"][val] += 1
            elif prop == "border-radius":
                out["borderRadius"][val] += 1
            elif prop == "box-shadow":
                out["boxShadow"][val] += 1
            elif prop in ("transition", "transition-duration", "animation", "animation-duration"):
                for n, u in DUR.findall(val):
                    out["transitionDuration"][f"{float(n):g}{u}"] += 1
                for e in EASE.findall(val):
                    out["easing"][e] += 1
            if not prop.startswith("--") or prop.startswith("--"):
                for h in HEX.findall(val):
                    c = norm_hex(h)
                    out["color"][c] += 1
                    by_prop[prop][c] += 1
                for r in RGB.findall(val):
                    out["color"][re.sub(r"\s+", "", r)] += 1
    out["color_by_property"] = {p: dict(c.most_common(8)) for p, c in by_prop.items()
                                if p in ("color", "background", "background-color", "border", "border-color", "fill", "stroke")}
    return out


def top(counter, n=25):
    return [[k, v] for k, v in counter.most_common(n)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=DEFAULT_SOURCE, help="project root containing src/styles (default: parent of design-repo)")
    ap.add_argument("--write", action="store_true", help="write extraction/derived-histograms.json")
    a = ap.parse_args()
    css_dir = os.path.join(a.source, "src", "styles")
    files = sorted(glob.glob(os.path.join(css_dir, "original", "*.css")))
    if not files:
        print(f"WARNING: no source CSS under {os.path.relpath(css_dir, a.source)} (source tree absent); "
              "keeping the checked-in extraction/derived-histograms.json unchanged.")
        return 0
    site = [f for f in files if os.path.basename(f) not in VENDOR]
    vendor = [f for f in files if os.path.basename(f) in VENDOR]
    wrapper = sorted(glob.glob(os.path.join(css_dir, "*.css")))  # route import lists only (@import), no declarations
    site_h = collect(site)
    vend_h = collect(vendor)
    result = {
        "_note": "DERIVED by extraction/derive_histograms.py (no histogram shipped with the source). Counts are declaration occurrences in compiled CSS, not element counts.",
        "files": {"site": [os.path.basename(f) for f in site], "vendor": [os.path.basename(f) for f in vendor],
                  "routeImportLists": [os.path.basename(f) for f in wrapper]},
        "site": {k: (top(v, 5000 if k == "color" else 80) if isinstance(v, collections.Counter) else v) for k, v in site_h.items()},
        "vendor": {k: top(v, 8) for k, v in vend_h.items() if isinstance(v, collections.Counter) and k in ("fontFamily", "borderRadius")},
    }
    text = json.dumps(result, indent=1, ensure_ascii=False)
    if a.write:
        open(OUT, "w", encoding="utf-8").write(text + "\n")
        print("wrote", os.path.relpath(OUT, REPO))
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
