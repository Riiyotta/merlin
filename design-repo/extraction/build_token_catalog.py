#!/usr/bin/env python3
"""Derive tokens/llm/token-catalog.json from the real token files of this design-repo.

    python3 extraction/build_token_catalog.py            # --check (default): rebuild in memory, exit 1 on drift
    python3 extraction/build_token_catalog.py --write

Inputs (all inside design-repo/, so this runs standalone): tokens/00-foundation/*.json (color, typography,
radius, breakpoint, elevation, motion, motion-patterns), tokens/10-semantic/semantic.json,
tokens/20-component/component.json, tokens/30-layout/layout.json and tokens/themes/*.json. Those files were
themselves measured from the site CSS (histogramCount re-derived from extraction/derived-histograms.json by
verify_all.py); the clone's tailwind.config.js has `theme: { extend: {} }` (no Tailwind tokens: styling is the
original site CSS), so there is no second token source to merge. NO value is typed in here: every catalog
entry is a token path + its real $value / $ref, classified into a category by the rules below.

Category rules (keys of counts.byCategory; token-policy.json refers to these exact names):
  color           foundation colours (color.*)                       - catalogued, NOT PageSpec-approved (use semanticColor)
  semanticColor   tokens/10-semantic color.* aliases                 - PageSpec-approved, resolved by a theme
  fontFamily, fontSize, fontWeight, lineHeight, letterSpacing        - foundation type primitives (catalogued)
  typography      tokens/10-semantic typography.* roles              - PageSpec-approved type roles
  spacing         layout tokens that are paddings / gaps / nav heights (layout.section.*-padding, layout.grid.gap,
                  layout.header.nav-height) and component paddings (component.*.padding)
  layout          the remaining layout tokens (container widths, grids, column templates)
  radius, elevation, breakpoint                                       - foundation
  component       the remaining component tokens
  motion          duration.*, easing.*, spring.*, preset.*
  motionPattern   motion-patterns.json patterns (ids, used by node.motion.patterns)
"""
import argparse, glob, json, os, re, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(REPO, "tokens", "llm", "token-catalog.json")


def jl(rel):
    return json.load(open(os.path.join(REPO, rel), encoding="utf-8"))


def leaves(node, prefix=""):
    if isinstance(node, dict):
        if "$value" in node or "$ref" in node:
            yield prefix, node
            return
        for k, v in node.items():
            if k.startswith("_"):
                continue
            yield from leaves(v, prefix + "." + k if prefix else k)


SPACING = re.compile(r"^(layout\.section\.[a-z-]+-padding|layout\.grid\.gap|layout\.header\.nav-height|component\.[a-z-]+\.padding)$")
NOT_APPROVED = {
    # catalogued (real) but not for PageSpec slots; reasons are recorded in token-policy.json notApproved
    "fontFamily.mock-web", "fontFamily.demo-system", "layout.section.root-font-size",
}


def build():
    toks = {}

    def put(path, cat, t, src, **extra):
        e = {"category": cat, "type": t.get("$type"), "source": src}
        if "$value" in t:
            e["value"] = t["$value"]
        if "$ref" in t:
            e["ref"] = t["$ref"]
        if t.get("$description"):
            e["description"] = t["$description"]
        e.update(extra)
        e["approvedForPageSpec"] = path not in NOT_APPROVED and cat not in ("color", "fontFamily", "fontSize", "fontWeight", "lineHeight", "letterSpacing", "breakpoint", "component", "motionPattern")
        toks[path] = e

    for f in sorted(glob.glob(os.path.join(REPO, "tokens", "00-foundation", "*.json"))):
        base = os.path.basename(f)
        rel = "tokens/00-foundation/" + base
        if base == "motion-patterns.json":
            for pid, p in jl(rel)["patterns"].items():
                toks["motionPattern." + pid] = {"category": "motionPattern", "type": "motionPattern", "source": rel, "value": pid, "description": (p.get("description") if isinstance(p, dict) else str(p))[:160], "approvedForPageSpec": False}
            continue
        for path, t in leaves(jl(rel)):
            top = path.split(".")[0]
            cat = {"color": "color", "fontFamily": "fontFamily", "fontSize": "fontSize", "fontWeight": "fontWeight", "lineHeight": "lineHeight",
                   "letterSpacing": "letterSpacing", "radius": "radius", "breakpoint": "breakpoint", "elevation": "elevation",
                   "duration": "motion", "easing": "motion", "spring": "motion", "preset": "motion"}[top]
            put(path, cat, t, rel)
    sem = jl("tokens/10-semantic/semantic.json")
    for k, t in sem["color"].items():
        put("color." + k, "semanticColor", t, "tokens/10-semantic/semantic.json")
    for k, t in sem["typography"].items():
        put("typography." + k, "typography", t, "tokens/10-semantic/semantic.json")
    for path, t in leaves(jl("tokens/20-component/component.json")):
        put(path, "spacing" if SPACING.match(path) else "component", t, "tokens/20-component/component.json")
    for path, t in leaves(jl("tokens/30-layout/layout.json")):
        put(path, "spacing" if SPACING.match(path) else "layout", t, "tokens/30-layout/layout.json")

    # semanticColor scheme: the black privacy scene is a SECTION-LOCAL dark scheme inside the light theme
    for path, e in toks.items():
        if e["category"] == "semanticColor":
            e["scheme"] = "scene-dark" if re.search(r"(scene-dark|on-dark)$", path) else "light"

    themes = {}
    for f in sorted(glob.glob(os.path.join(REPO, "tokens", "themes", "*.json"))):
        th = json.load(open(f, encoding="utf-8"))
        themes[th["theme"]] = {"file": "tokens/themes/" + os.path.basename(f), "default": th.get("default", False),
                               "resolves": {k: v["value"] for k, v in sorted(th["resolved"].items())}}
    by = {}
    for e in toks.values():
        by[e["category"]] = by.get(e["category"], 0) + 1
    return {
        "_note": "GENERATED by extraction/build_token_catalog.py from tokens/{00-foundation,10-semantic,20-component,30-layout,themes}. Do not hand-edit; extraction/verify_all.py rebuilds it and fails on any difference. A PageSpec names tokens by these paths (approvedForPageSpec: true, see token-policy.json), never by raw values.",
        "version": "1.0.0",
        "counts": {"tokens": len(toks), "byCategory": dict(sorted(by.items())), "approvedForPageSpec": sum(1 for e in toks.values() if e["approvedForPageSpec"]), "themes": len(themes)},
        "themes": themes,
        "tokens": dict(sorted(toks.items())),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    new = build()
    if a.write:
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(new, f, indent=1, ensure_ascii=False); f.write("\n")
        print("wrote tokens/llm/token-catalog.json: %d tokens %s" % (new["counts"]["tokens"], new["counts"]["byCategory"]))
        return 0
    old = json.load(open(OUT, encoding="utf-8")) if os.path.isfile(OUT) else None
    if old != new:
        bad = sorted(k for k in set(new["tokens"]) | set((old or {}).get("tokens", {})) if (old or {}).get("tokens", {}).get(k) != new["tokens"].get(k))
        print("DRIFT: tokens/llm/token-catalog.json differs from a rebuild of the token files (%d token(s) differ, e.g. %s; counts/themes %s)" % (len(bad), bad[:4], "differ" if (old or {}).get("counts") != new["counts"] or (old or {}).get("themes") != new["themes"] else "same"))
        return 1
    print("token catalog: up to date (%d tokens)" % new["counts"]["tokens"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
