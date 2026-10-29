#!/usr/bin/env python3
"""Derive the generation-mode leakage registry (schema/source-identity.json) from the REAL source.

    python3 extraction/build_source_identity.py            # --check (default): rebuild in memory, exit 1 on drift
    python3 extraction/build_source_identity.py --write    # rewrite schema/source-identity.json
    python3 extraction/build_source_identity.py --source <project root>

The source project is the PARENT of design-repo/ (derived from __file__) unless --source is given. When it is
absent the script prints a WARNING and exits 0, leaving the checked-in registry untouched (the semantic
validator only needs the checked-in file, so the design-repo stays usable on its own).

Every term carries file:line evidence harvested here; nothing is typed in by hand except the EXTRACTION
RULES below (which file / which attribute to read). Categories:
  brand       the site title's product name (index.html <title>), plus every host/email that contains it
  customers   social-proof logo names (Companies.jsx alt / aria-label) and the real third-party brands the
              browser-task scene names (Browser.jsx TASKS name:)
  people      the blog author (blog-posts.json author), the named mock personas (MockSites.jsx profile name,
              MeetingLandscape.jsx transcript speakers)
  urlHosts    every http(s) host in src/ (code + src/data/*.json), index.html, CLONE_SPEC*.md and ASSET_MANIFEST.json, except the XML
              namespace host www.w3.org and the reserved example.com
  installerPaths  the Mac installer download paths of the clone (InstallIntro.jsx / Download.jsx)
  assetFiles  every shipped source asset file name under public/assets/ (screenshots, photos, logos, art)
  claims      the real plan tiers (pricingData.js price + credits) and the social-proof claim heading
  copy        sha256[:16] of every normalised 5-word shingle of the site copy (JSX text + string literals
              of >= 5 words in src/components, src/pages, and the blog titles/excerpts/headings)
Normalisation is schema/textnorm.py (shared with the validator). Detection is string-based, see that file.
"""
import argparse, glob, json, os, re, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "schema"))
import textnorm as tn  # noqa: E402

OUT = os.path.join(REPO, "schema", "source-identity.json")
EXCLUDED_HOSTS = {"www.w3.org", "example.com"}  # XML namespace / RFC 2606 reserved: not source identity
COPY_EXCLUDE = ("src/lib/", "src/components/legal/placeholder.js")  # neutral filler generators, not site copy


def rel(src, p):
    return os.path.relpath(p, src).replace(os.sep, "/")


def lines(p):
    return open(p, encoding="utf-8", errors="replace").read().split("\n")


def find_all(src, files, regex, group=1):
    """Yield (value, 'file:line') for every regex match, line by line."""
    rx = re.compile(regex)
    for f in files:
        for i, ln in enumerate(lines(f), 1):
            for m in rx.finditer(ln):
                yield m.group(group), "%s:%d" % (rel(src, f), i)


def add(store, term, ev):
    k = term.strip()
    if not k:
        return
    e = store.setdefault(k, [])
    if ev not in e and len(e) < 3:
        e.append(ev)


def as_list(store, category):
    return [{"term": t, "category": category, "tokens": tn.tokens(t), "evidence": ev} for t, ev in sorted(store.items(), key=lambda kv: kv[0].lower())]


def strip_comments(text):
    text = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
    return re.sub(r"(^|[^:'\"`])//[^\n]*", r"\1", text)


def copy_strings(src):
    files = [f for f in glob.glob(os.path.join(src, "src", "components", "**", "*.js*"), recursive=True) + glob.glob(os.path.join(src, "src", "pages", "*.jsx"))
             if not rel(src, f).startswith(COPY_EXCLUDE)]
    out = []
    for f in sorted(files):
        t = strip_comments(open(f, encoding="utf-8").read())
        cands = re.findall(r"'((?:[^'\\\n]|\\.)*)'|\"((?:[^\"\\\n]|\\.)*)\"|`([^`]*)`", t)
        cands = [a or b or c for a, b, c in cands]
        cands += re.findall(r">([^<>{}]+)<", t)  # JSX text
        for s in cands:
            s = re.sub(r"\$\{[^}]*\}", " ", s)
            words = s.split()
            if len(words) < 5 or re.search(r"[={}();]|=>|\bclassName\b", s):
                continue
            if sum(1 for w in words if re.match(r"^[A-Za-z’'’,.!?:-]+$", w)) < 0.6 * len(words):
                continue
            out.append(s)
    posts = json.load(open(os.path.join(src, "src", "data", "blog-posts.json"), encoding="utf-8"))["posts"]
    for p in posts:
        for k in ("title", "excerpt", "metaDescription", "coverAlt"):
            if isinstance(p.get(k), str):
                out.append(p[k])
        for b in p["structure"]:
            if isinstance(b.get("text"), str):
                out.append(b["text"])
    return out


def build(src):
    jsx = sorted(glob.glob(os.path.join(src, "src", "**", "*.jsx"), recursive=True) + glob.glob(os.path.join(src, "src", "**", "*.js"), recursive=True))
    docs = sorted(glob.glob(os.path.join(src, "CLONE_SPEC*.md"))) + [os.path.join(src, "index.html"), os.path.join(src, "ASSET_MANIFEST.json")]

    # brand root: the product name in the site <title>
    title = next(find_all(src, [os.path.join(src, "index.html")], r"<title>([^<]+)</title>"))
    root = re.split(r"\s+[—|-]\s+", title[0])[0].strip()
    brand = {}
    add(brand, root, title[1])
    for v, ev in find_all(src, jsx + docs, r"https?://([A-Za-z0-9.-]+)"):
        if root.lower() in v.lower():
            add(brand, v.lower(), ev)
    for v, ev in find_all(src, jsx, r"([A-Za-z0-9._-]+@[A-Za-z0-9.-]+\.[a-z]+)"):
        if root.lower() in v.lower():
            add(brand, v.lower(), ev)

    customers = {}
    comp = [os.path.join(src, "src", "components", "Companies.jsx")]
    for v, ev in find_all(src, comp, r'(?:alt|aria-label)="([^"]+)"'):
        if v != "Used by professionals at":
            add(customers, v.replace("&amp;", "&"), ev)
    for v, ev in find_all(src, [os.path.join(src, "src", "components", "Browser.jsx")], r"^\s*\{ name: '([^']+)'"):
        add(customers, v, ev)

    people = {}
    bp = os.path.join(src, "src", "data", "blog-posts.json")
    for v, ev in find_all(src, [bp], r'"author": "([^"]+)"'):
        add(people, v, ev)
    for v, ev in find_all(src, [os.path.join(src, "src", "components", "browser", "MockSites.jsx")], r"_PROFILE = \{ name: '([^']+)'"):
        add(people, v, ev)
    for v, ev in find_all(src, [os.path.join(src, "src", "components", "meetings", "MeetingLandscape.jsx")], r"\{ name: '([^']+)', initials:"):
        add(people, v, ev)

    hosts = {}
    data = sorted(glob.glob(os.path.join(src, "src", "data", "*.json")))
    for v, ev in find_all(src, jsx + docs + data, r"https?://([A-Za-z0-9.-]+[A-Za-z0-9])"):
        if v.lower() not in EXCLUDED_HOSTS:
            add(hosts, v.lower(), ev)

    installer = {}
    for v, ev in find_all(src, jsx, r"(/download-stub[A-Za-z0-9._-]*)"):
        add(installer, v, ev)

    assets = {}
    pub = os.path.join(src, "public", "assets")
    for f in sorted(glob.glob(os.path.join(pub, "**", "*"), recursive=True)):
        if os.path.isfile(f):
            add(assets, os.path.basename(f), rel(src, f))

    claims = {}
    pd = os.path.join(src, "src", "components", "pricing", "pricingData.js")
    L = lines(pd)
    tiers = []
    for i, ln in enumerate(L, 1):
        m = re.match(r"\s*price: '([^']+)',", ln)
        if m:
            cm = next(re.match(r"\s*credits: '([^']+)',", L[j]) for j in range(i, min(i + 4, len(L))) if re.match(r"\s*credits: '([^']+)',", L[j]))
            tiers.append({"price": m.group(1), "credits": cm.group(1), "evidence": ["%s:%d" % (rel(src, pd), i)]})
    for v, ev in find_all(src, comp, r'className="companies-heading">([^<]+)<'):
        add(claims, v, ev)

    shingles = set()
    texts = copy_strings(src)
    for s in texts:
        shingles |= tn.shingle_hashes(s)

    return {
        "_note": "GENERATED by extraction/build_source_identity.py from the real source (do not hand-edit; verify_all.py re-derives it and fails on drift when the source tree is present). Used by schema/semantic_validate.py to reject source identity/content in mode=generation PageSpecs. Detection is string-based on schema/textnorm.py-normalised text; nobody has hand-reviewed these patterns.",
        "normalization": "NFKC; zero-width + soft hyphen removed; curly quotes -> straight; dash variants -> '-'; lower-case; apostrophes dropped; tokens [a-z0-9]+; terms match as contiguous token sequences",
        "brandRoot": root,
        "terms": as_list(brand, "BRAND") + as_list(customers, "CUSTOMER") + as_list(people, "PERSON") + as_list(hosts, "URL") + as_list(installer, "URL") + as_list(claims, "CLAIM"),
        "assetFiles": as_list(assets, "ASSET"),
        "planTiers": tiers,
        "copy": {"shingleSize": tn.SHINGLE, "hash": "sha256 hex[:16] of the space-joined normalised tokens", "sourceStrings": len(texts), "hashes": sorted(shingles)},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=os.path.dirname(REPO))
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if not (os.path.isdir(os.path.join(a.source, "src")) and os.path.isfile(os.path.join(a.source, "index.html"))):
        print("WARNING: source tree absent; schema/source-identity.json not re-derived (checked-in copy used)")
        return 0
    new = build(a.source)
    if a.write:
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(new, f, indent=1, ensure_ascii=False); f.write("\n")
        print("wrote schema/source-identity.json: %d terms, %d asset files, %d plan tiers, %d copy shingles" % (len(new["terms"]), len(new["assetFiles"]), len(new["planTiers"]), len(new["copy"]["hashes"])))
        return 0
    old = json.load(open(OUT, encoding="utf-8")) if os.path.isfile(OUT) else None
    if old != new:
        diff = [k for k in new if (old or {}).get(k) != new[k]]
        print("DRIFT: schema/source-identity.json differs from a rebuild from the source (keys: %s)" % diff)
        return 1
    print("source identity registry: up to date (%d terms, %d copy shingles)" % (len(new["terms"]), len(new["copy"]["hashes"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
