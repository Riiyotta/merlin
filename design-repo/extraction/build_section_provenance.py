#!/usr/bin/env python3
"""Derive the R7 provenance/taxonomy split for every section contract.

Each sections/*.json gets two CLOSED objects:
  source   = {id, tag, file, lines}  - what the DOM element is and where it lives (traceable)
  semantic = {id, category}          - what the AI sees (semantic.id == contract id; source.id never does)

source is DERIVED from the contract's `domAnchor` (the last compound selector: tag + .class / #id) by
locating the opening tag in the real source file and walking to its matching closing tag. The file
searched first is each `implementedBy` entry; when none of them renders the anchor element itself (e.g.
install.intro's <section> wrapper lives in the page file), the rest of src/ is searched and that file is
recorded. CSS-module style maps (`nav: 'floating-navigation_nav__y4vuM'`) are resolved to `styles.nav`.
semantic.category is a hand-reviewed taxonomy (SEMANTIC_CATEGORY below, read from the real components);
wrapper/class naming never decides it.

Usage:
  python3 extraction/build_section_provenance.py            # --check (default): recompute, exit 1 on drift
  python3 extraction/build_section_provenance.py --write    # write source/semantic into sections/*.json
  [--source <project root>]                                  # default: parent of design-repo/

When the source tree is absent, --check prints a WARNING and exits 0 (graceful degradation);
check() returns None so verify_all can warn instead of failing.
"""
import argparse, glob, json, os, re, sys
sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DEFAULT_SOURCE = os.path.dirname(REPO)

# Closed AI-facing taxonomy (mirrored as an enum in schema/section-contract.schema.json).
CATEGORIES = ["SHELL", "HERO", "PROOF", "FEATURES", "TRUST", "FAQ", "PRICING", "CONVERSION", "CONTENT", "LEGAL", "INSTALL"]

# Hand-reviewed against the real components (R6 category honesty: conversion blocks are CONVERSION,
# editorial blocks are CONTENT, FEATURES = capabilities/workflows/benefits only).
SEMANTIC_CATEGORY = {
    "shell.corner-nav": "SHELL",
    "shell.floating-nav": "SHELL",
    "shell.footer-closing": "SHELL",
    "shell.install-header": "SHELL",
    "hero.marketing": "HERO",              # page-opening title + sub + download CTA (home) / plans intro (pricing)
    "hero.landscape": "FEATURES",          # second band under the hero: notification-stack capability demo, not a 2nd hero
    "proof.company-logos": "PROOF",
    "story.context-routines": "FEATURES",
    "story.browser-tasks": "FEATURES",
    "story.meetings-projects": "FEATURES",
    "story.companion": "FEATURES",
    "scene.privacy-trust": "TRUST",
    "faq.accordion": "FAQ",
    "pricing.plans": "PRICING",
    "pricing.included": "FEATURES",        # what every plan includes = capability list
    "pricing.faq": "FAQ",
    "install.intro": "CONVERSION",         # post-download thank-you + installer trigger / retry link
    "install.steps": "INSTALL",            # instructional 3-step install guide
    "manifesto.opening": "CONTENT",
    "manifesto.photo": "CONTENT",
    "manifesto.understanding": "CONTENT",
    "manifesto.action": "CONTENT",
    "manifesto.ending": "CONTENT",
    "blog.intro": "CONTENT",
    "blog.featured": "CONTENT",
    "blog.story-list": "CONTENT",
    "blog.manifesto-aside": "CONTENT",
    "blog.article-header": "CONTENT",
    "blog.prose": "CONTENT",
    "blog.article-end": "CONTENT",
    "legal.heading": "LEGAL",
    "legal.contents": "LEGAL",
    "legal.section": "LEGAL",
    "legal.document-footer": "LEGAL",
}

# R8: runtime/utility UI is not retrievable content. Decided from the source: the only such section is
# the floating nav - position:fixed (z-index 9999, src/styles/original/6385c293c5638848.css), mounted via
# AnimatePresence only while scrolled past 100px and hidden while #privacy is in view
# (src/components/FloatingNav.jsx:23-79). No cookie/consent banner, modal, dialog, drawer, toast or
# preloader section exists (the companion "selection popover" is part of the story.companion demo scene).
RETRIEVAL_INELIGIBLE = {
    "shell.floating-nav": "Runtime utility overlay: a position:fixed navigation pill that only mounts after scrolling and hides over the privacy scene; it carries no page content worth retrieving.",
    "legal.contents": "Derived in-page navigation: a sticky table of contents whose links are generated from the legal.section titles; it carries no content of its own.",
}

# Anchors whose domAnchor names the HOST wrapper rather than the component's own element.
# shell.corner-nav: domAnchor 'div.site-container > header' is the per-page wrapper (BlogLayout /
# LegalPage / Manifesto each render <header className="...-navigation"><HeroNav/></header>); the
# section itself is HeroNav's <nav className="hero-corner-nav">, which is what we cite.
ANCHOR_OVERRIDE = {
    "shell.corner-nav": ("nav", ".hero-corner-nav"),
}


def parse_anchor(anchor):
    last = anchor.split(">")[-1].strip()
    m = re.match(r"^([a-z][a-z0-9]*)((?:[.#][A-Za-z0-9_-]+)*)$", last)
    if not m:
        raise ValueError("unparseable domAnchor %r" % anchor)
    tag, rest = m.group(1), m.group(2)
    sels = re.findall(r"([.#])([A-Za-z0-9_-]+)", rest)
    return tag, sels


def _open_re(tag):
    return re.compile(r"<(?:motion\.)?%s(?=[\s>/]|$)" % tag)


def locate(path, tag, sels):
    """Return (start, end) 1-based line numbers of the element, or None."""
    text = open(path, encoding="utf-8").read()
    lines = text.split("\n")
    cls = [n for k, n in sels if k == "."]
    ids = [n for k, n in sels if k == "#"]
    op = _open_re(tag)
    for i, ln in enumerate(lines):
        if not op.search(ln) or ln.lstrip().startswith("//"):
            continue
        # the opening tag: from this line through the first line that ends the tag ('>' not part of '=>')
        k = i
        while k < min(len(lines), i + 12) and not re.search(r"(?<!=)>\s*(\{.*)?$", lines[k][lines[k].find("<") if k == i else 0:]):
            k += 1
        head = " ".join(lines[i:k + 1])
        if ids and not all(('id="%s"' % x) in head for x in ids):
            continue
        ok = all(c in head or any(("styles.%s}" % k) in head for k in re.findall(r"(\w+)\s*:\s*'%s'" % re.escape(c), text)) for c in cls)
        if not ok:
            continue
        end = match_close(lines, i, tag)
        if end:
            return i + 1, end + 1
    return None


def match_close(lines, start, tag):
    op = re.compile(r"<(motion\.)?%s(?=[\s>/]|$)" % tag)
    cl = re.compile(r"</(?:motion\.)?%s\s*>" % tag)
    depth = 0
    for j in range(start, len(lines)):
        ln = lines[j]
        events = [(m.start(), 1, m) for m in op.finditer(ln)] + [(m.start(), -1, m) for m in cl.finditer(ln)]
        for pos, d, m in sorted(events, key=lambda e: e[0]):
            if d == 1:
                # self-closing opening tag on the same line
                rest = ln[m.end():]
                gt = rest.find(">")
                if gt != -1 and rest[:gt].rstrip().endswith("/"):
                    continue
                depth += 1
            else:
                depth -= 1
                if depth == 0:
                    return j
    return None


def derive(contract, source_root):
    cid = contract["id"]
    if cid in ANCHOR_OVERRIDE:
        tag, sel = ANCHOR_OVERRIDE[cid]
        _, sels = parse_anchor(tag + sel)
    else:
        tag, sels = parse_anchor(contract["domAnchor"])
    cands = list(contract.get("implementedBy", []))
    rest = sorted(os.path.relpath(p, source_root) for p in glob.glob(os.path.join(source_root, "src", "**", "*.jsx"), recursive=True))
    for f in cands + [r for r in rest if r not in cands]:
        fp = os.path.join(source_root, f)
        if not os.path.isfile(fp):
            continue
        hit = locate(fp, tag, sels)
        if hit:
            a, b = hit
            sel = "".join(k + n for k, n in sels)
            return {
                "id": "src:%s#%s%s" % (os.path.basename(f), tag, sel),
                "tag": tag,
                "file": f,
                "lines": "%d-%d" % (a, b),
            }
    return None


def semantic_for(contract):
    return {"id": contract["id"], "category": SEMANTIC_CATEGORY.get(contract["id"], "UNMAPPED")}


def contracts(repo_root):
    out = []
    for p in sorted(glob.glob(os.path.join(repo_root, "sections", "*.json"))):
        out.append((p, json.load(open(p, encoding="utf-8"))))
    return out


def verify_range(source_root, src):
    """Range inside the real file AND the element's opening tag at the start line."""
    fp = os.path.join(source_root, src["file"])
    if not os.path.isfile(fp):
        return "file %s missing" % src["file"]
    lines = open(fp, encoding="utf-8").read().split("\n")
    m = re.match(r"^(\d+)-(\d+)$", src["lines"])
    if not m:
        return "unparseable lines %r" % src["lines"]
    a, b = int(m.group(1)), int(m.group(2))
    if a < 1 or b < a or b > len(lines):
        return "%s:%s outside file (%d lines)" % (src["file"], src["lines"], len(lines))
    if not _open_re(src["tag"]).search(lines[a - 1]):
        return "%s:%d does not open <%s" % (src["file"], a, src["tag"])
    if not re.search(r"</(?:motion\.)?%s\s*>" % src["tag"], lines[b - 1]):
        return "%s:%d does not close </%s>" % (src["file"], b, src["tag"])
    return None


def check(repo_root=REPO, source_root=DEFAULT_SOURCE):
    """Return [] when every contract's recorded source/semantic equals the recomputed value and every
    cited range is valid; a list of problem strings otherwise; None when the source tree is absent."""
    if not os.path.isdir(os.path.join(source_root, "src")):
        return None
    probs = []
    for p, c in contracts(repo_root):
        cid = c.get("id")
        want = derive(c, source_root)
        if want is None:
            probs.append("%s: domAnchor %r not located in the source" % (cid, c.get("domAnchor")))
        elif c.get("source") != want:
            probs.append("%s: source %r != recomputed %r" % (cid, c.get("source"), want))
        if isinstance(c.get("source"), dict):
            err = verify_range(source_root, c["source"])
            if err:
                probs.append("%s: %s" % (cid, err))
            if c["source"].get("id") == cid:
                probs.append("%s: source.id must not equal the contract id" % cid)
        sem = c.get("semantic")
        if sem != semantic_for(c):
            probs.append("%s: semantic %r != expected %r" % (cid, sem, semantic_for(c)))
        want_re = cid not in RETRIEVAL_INELIGIBLE
        if c.get("retrievalEligible") is not want_re:
            probs.append("%s: retrievalEligible %r != expected %r" % (cid, c.get("retrievalEligible"), want_re))
        if not want_re and len(c.get("retrievalIneligibleReason", "")) < 30:
            probs.append("%s: retrievalIneligibleReason missing or < 30 chars" % cid)
        if want_re and "retrievalIneligibleReason" in c:
            probs.append("%s: retrievalIneligibleReason on an eligible section" % cid)
        if semantic_for(c)["category"] not in CATEGORIES:
            probs.append("%s: no reviewed semantic category (add it to SEMANTIC_CATEGORY)" % cid)
    return probs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=DEFAULT_SOURCE)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--write", action="store_true")
    g.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if not os.path.isdir(os.path.join(a.source, "src")):
        print("WARNING: source tree absent; section provenance not recomputed")
        return 0
    if a.write:
        bad = 0
        for p, c in contracts(REPO):
            src = derive(c, a.source)
            if src is None:
                print("NOT LOCATED: %s (%s)" % (c["id"], c.get("domAnchor"))); bad += 1; continue
            c["source"] = src
            c["semantic"] = semantic_for(c)
            c["retrievalEligible"] = c["id"] not in RETRIEVAL_INELIGIBLE
            c.pop("retrievalIneligibleReason", None)
            if c["id"] in RETRIEVAL_INELIGIBLE:
                c["retrievalIneligibleReason"] = RETRIEVAL_INELIGIBLE[c["id"]]
            front = ["id", "category", "source", "semantic", "retrievalEligible", "retrievalIneligibleReason"]
            c = dict([(k, c[k]) for k in front if k in c] + [(k, v) for k, v in c.items() if k not in front])
            with open(p, "w", encoding="utf-8") as f:
                json.dump(c, f, indent=2, ensure_ascii=False)
                f.write("\n")
            print("%-26s %-44s %-8s %-8s %s" % (c["id"], src["file"], src["tag"], src["lines"], c["semantic"]["category"]))
        return 1 if bad else 0
    probs = check(REPO, a.source)
    for x in probs:
        print("DRIFT", x)
    print("section provenance: %d contracts, %d problem(s)" % (len(contracts(REPO)), len(probs)))
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main())
