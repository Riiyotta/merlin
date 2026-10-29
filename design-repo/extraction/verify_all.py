#!/usr/bin/env python3
"""Self-containment + schema + structural + drift verifier for this design-repo.

Run:  python3 extraction/verify_all.py [--source <project root>]

The repo root is derived from __file__. The source project (CLONE_SPEC*.md, src/, public/, reference/) is
looked up as the PARENT of design-repo/ unless --source is given; when it is absent every source-dependent
check degrades to a WARNING (never a failure) so the repo stays verifiable standalone.

Checks (each prints PASS / WARN / FAIL):
  json parse; Draft-07 schema + example (0 errors); allowlist parity BOTH ways (no phantom entries, no orphans)
  + allowlistVersion machine-check + settable-field parity with contracts/schema; manifest counts RECOMPUTED from
  disk; manifest hygiene (status, productionApproved, entryPoints inside the repo, no '..'); template/route 1:1
  coverage (also against src/App.jsx); graph <-> semantic_validate.py agreement (rule ids, exception lists);
  schema <-> section-contract parity; citation-range validity AND quote-in-range content checks; histogramCount
  recompute; token reference resolution; asset-role closure + PINNED policies; per-route stylesheet lists vs the
  source wrappers; package.json version drift; blog maxima recomputed from blog-posts.json; no absolute paths.

Added in 2.0.0: token catalog rebuild + token policy resolution; mode/generation examples (one per template
  family, Draft-07 + semantic); source-identity registry rebuild + evidence; PINNED_AVAILABILITY (here AND in
  semantic_validate.py) vs registry; RETRIEVAL_INELIGIBLE pin (here AND in semantic_validate.py) vs contracts and
  allowlist; closed section-contract schema; source/semantic provenance re-derived from the real files; wrapper
  gate (extraction/wrapper_gate.py) over measured sectionHeights; repeatable-node exception parity; design-policy
  binding + contentHash.

Documentation-only version fields (NOT machine-checked): registry.manifest.json repositoryVersion and
pageSpecVersion. Machine-checked: allowlistVersion (must equal tokens/llm/component-allowlist.json).
"""
import argparse, glob, json, os, re, sys
sys.dont_write_bytecode = True  # keep the repo free of __pycache__

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "schema"))
sys.path.insert(0, HERE)

# R3 pin, kept independently of schema/semantic_validate.py's copy (both are compared below).
PINNED_AVAILABILITY = {
    "logo.third-party-wordmark": "blocked-for-generation", "icon.third-party-app": "blocked-for-generation",
    "brand.merlin-app-icon": "clone-only", "brand.merlin-mascot-art": "clone-only", "illustration.felt-scene": "clone-only",
    "screenshot.os-install-step": "blocked-for-generation", "screenshot.product-output": "clone-only",
    "photo.stock-cover": "blocked-for-generation", "photo.person-portrait": "blocked-for-generation",
    "photo.mock-product": "blocked-for-generation", "media.audio-sample": "clone-only", "art.footer-ascii": "clone-only",
    "icon.generic-ui": "generation-safe", "art.line-illustration": "generation-safe",
    "brand.placeholder-mark": "generation-safe", "media.user-supplied": "generation-safe", "illustration.generated": "generation-safe",
    "screenshot.placeholder": "generation-safe", "photo.fictional-person": "generation-safe", "logo.placeholder-customer": "generation-safe",
    "link.placeholder-url": "generation-safe", "copy.original": "generation-safe",
}
REQUIRED_GENERATION_SAFE = {"brand.placeholder-mark", "media.user-supplied", "illustration.generated", "screenshot.placeholder",
                            "photo.fictional-person", "logo.placeholder-customer", "link.placeholder-url", "copy.original"}
# R8 pin, kept independently of schema/semantic_validate.py's copy.
RETRIEVAL_INELIGIBLE = {"shell.floating-nav", "legal.contents"}
RUNTIME_UI = re.compile(r"cookie|consent|modal|dialog|drawer|popup|popover|overlay|preloader|toast|cursor|floating|contents|toc\b", re.I)

OUT = {"pass": 0, "warn": 0, "fail": 0}
WARNED = []


def p(kind, name, detail=""):
    OUT[kind] += 1
    tag = {"pass": "PASS", "warn": "WARN", "fail": "FAIL"}[kind]
    print("%s  %s%s" % (tag, name, (": " + detail) if detail else ""))


def check(name, ok, detail=""):
    p("pass" if ok else "fail", name, "" if ok else detail)
    return ok


def jl(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as f:
        return json.load(f)


def relfiles(pattern):
    return sorted(os.path.relpath(x, REPO) for x in glob.glob(os.path.join(REPO, pattern), recursive=True))


def leaf_tokens(node, prefix=""):
    """Yield (id, token) for every DTCG leaf ($value or $ref)."""
    if isinstance(node, dict):
        if "$value" in node or "$ref" in node:
            yield prefix, node
            return
        for k, v in node.items():
            if k.startswith("_"):
                continue
            for x in leaf_tokens(v, prefix + "." + k if prefix else k):
                yield x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=os.path.dirname(REPO))
    a = ap.parse_args()
    SRC = a.source
    have_src = os.path.isfile(os.path.join(SRC, "CLONE_SPEC.md")) and os.path.isdir(os.path.join(SRC, "src"))
    print("repo: %s" % os.path.basename(REPO))
    print("source tree: %s" % ("present" if have_src else "ABSENT (source-dependent checks degrade to warnings)"))

    # ------------------------------------------------------------------ json parse
    files = relfiles("**/*.json")
    bad = []
    for f in files:
        try:
            jl(f)
        except Exception as e:
            bad.append("%s: %s" % (f, e))
    check("all %d JSON files parse" % len(files), not bad, "; ".join(bad))
    if bad:
        return finish()

    manifest = jl("registry.manifest.json")
    allow = jl("tokens/llm/component-allowlist.json")
    roles_doc = jl("assets/asset-roles.json")
    schema = jl("schema/pagespec.schema.json")
    templates = jl("templates/templates.json")["templates"]
    routes_doc = jl("templates/routes.json")
    graph = jl("compatibility/graph.json")["rules"]
    patterns_doc = jl("tokens/00-foundation/motion-patterns.json")
    sections = {s["id"]: s for s in (jl(f) for f in relfiles("sections/*.json"))}
    prims = {s["id"]: s for s in (jl(f) for f in relfiles("primitives/*.json"))}
    comps = {s["id"]: s for s in (jl(f) for f in relfiles("components/*.json"))}

    # ------------------------------------------------------------------ 1 draft-07 schema + example
    from jsonschema import Draft7Validator
    try:
        Draft7Validator.check_schema(schema)
        check("pagespec.schema.json is a valid Draft-07 schema", True)
    except Exception as e:
        check("pagespec.schema.json is a valid Draft-07 schema", False, str(e)[:200])
    example = jl("schema/example.pagespec.json")
    errs = list(Draft7Validator(schema).iter_errors(example))
    check("example.pagespec.json: Draft-07 validation, 0 errors", not errs, "%d errors, first: %s" % (len(errs), errs[0].message[:150] if errs else ""))
    import semantic_validate as sv
    ctx = sv.Ctx(REPO)
    se, sw = sv.validate_all(example, ctx)
    check("example.pagespec.json: semantic validation, 0 errors", not se, "; ".join(se[:3]))

    # ------------------------------------------------------------------ 2 allowlist parity
    fileset = {"primitives": set(prims), "components": set(comps), "sections": set(sections)}
    for kind in ("primitives", "components", "sections"):
        ids = [e["id"] for e in allow[kind]]
        phantom = [e["id"] for e in allow[kind] if not os.path.isfile(os.path.join(REPO, e["file"])) or e["id"] not in fileset[kind]]
        orphan = sorted(fileset[kind] - set(ids))
        dup = sorted({i for i in ids if ids.count(i) > 1})
        check("allowlist parity [%s]: no phantom entries, no orphan contracts, no duplicates" % kind, not (phantom or orphan or dup),
              "phantom=%s orphan=%s dup=%s" % (phantom, orphan, dup))
    # file path <-> id agreement
    mism = [e["id"] for k in ("primitives", "components", "sections") for e in allow[k] if e["file"] != "%s/%s.json" % (k, e["id"])]
    check("allowlist entries point at the file named by their id", not mism, str(mism))
    check("allowlistVersion machine-check: manifest == component-allowlist.json", manifest.get("allowlistVersion") == allow.get("allowlistVersion"),
          "manifest=%r allowlist=%r" % (manifest.get("allowlistVersion"), allow.get("allowlistVersion")))
    node_props = sorted(schema["definitions"]["node"]["properties"])
    check("allowlist settableNodeProperties == schema node properties", sorted(allow["settableNodeProperties"]) == node_props, "%s vs %s" % (allow["settableNodeProperties"], node_props))
    bad = []
    for e in allow["sections"]:
        s = sections.get(e["id"])
        if s and sorted(e["settableContentFields"]) != sorted(s["content"]["properties"]):
            bad.append(e["id"])
        if s and e.get("variants") != s["variants"]:
            bad.append(e["id"] + ":variants")
    check("allowlist settableContentFields/variants == section contract properties", not bad, str(bad))
    bad = [e["id"] for k in ("primitives", "components") for e in allow[k] if e["overridableProps"] != sorted((prims if k == "primitives" else comps)[e["id"]]["props"])]
    check("allowlist overridableProps == primitive/component contract props", not bad, str(bad))
    role_ids = [r["id"] for r in roles_doc["roles"]]
    media_ids = [r["id"] for r in roles_doc["roles"] if r.get("kind", "media") == "media"]
    check("assetRole closure: allowlist == registry, schema assetRef enum == registry media roles (link/copy roles are non-media)", sorted(allow["assetRoles"]) == sorted(role_ids) and sorted(media_ids) == sorted(schema["definitions"]["assetRef"]["properties"]["assetRole"]["enum"]),
          "%s | %s | %s" % (sorted(allow["assetRoles"]), sorted(role_ids), sorted(schema["definitions"]["assetRef"]["properties"]["assetRole"]["enum"])))

    # ------------------------------------------------------------------ 3 manifest counts recomputed
    tok_files = {"foundation": relfiles("tokens/00-foundation/*.json"), "semantic": relfiles("tokens/10-semantic/*.json"), "component": relfiles("tokens/20-component/*.json"), "layout": relfiles("tokens/30-layout/*.json")}
    tok_counts = {}
    for grp, fl in tok_files.items():
        n = 0
        for f in fl:
            if os.path.basename(f) == "motion-patterns.json":
                continue
            n += sum(1 for _ in leaf_tokens(jl(f)))
        tok_counts[grp] = n
    tok_counts["total"] = sum(tok_counts.values())
    real = {
        "tokens": tok_counts, "primitives": len(prims), "components": len(comps), "sections": len(sections), "templates": len(templates),
        "routes": len(routes_doc["routes"]), "routingBehaviors": len(routes_doc["behaviors"]), "assetRoles": len(role_ids), "registeredAssets": len(roles_doc["assets"]),
        "graphRules": len(graph), "motionPatterns": len(patterns_doc["patterns"]), "reducedMotionFallbacks": len(patterns_doc["reducedMotionFallbacks"]),
        "jsonFiles": len(files),
    }
    mc = manifest.get("counts", {})
    diffs = {k: (mc.get(k), v) for k, v in real.items() if mc.get(k) != v}
    check("manifest counts recomputed from disk match (manifest vs disk)", not diffs, str(diffs))

    # README states real counts (machine-readable marker), CHANGELOG exists
    import io
    rd = open(os.path.join(REPO, "README.md"), encoding="utf-8").read()
    mk = re.search(r"<!-- counts: ([^>]*?) -->", rd)
    if mk:
        kv = dict(x.split("=") for x in mk.group(1).split())
        want = {"tokens": str(tok_counts["total"]), "primitives": str(len(prims)), "components": str(len(comps)), "sections": str(len(sections)), "templates": str(len(templates)), "routes": str(len(routes_doc["routes"])), "assetRoles": str(len(role_ids)), "graphRules": str(len(graph))}
        check("README counts marker == counts recomputed from disk (no stale README numbers)", kv == want, "README=%s disk=%s" % (kv, want))
    else:
        check("README carries a machine-readable counts marker", False, "missing <!-- counts: ... -->")
    check("CHANGELOG.md mentions the current allowlistVersion and repositoryVersion", ("allowlistVersion " + allow["allowlistVersion"]) in open(os.path.join(REPO, "CHANGELOG.md"), encoding="utf-8").read() and ("repositoryVersion " + manifest["repositoryVersion"]) in open(os.path.join(REPO, "CHANGELOG.md"), encoding="utf-8").read(), "CHANGELOG missing version mentions")

    # ------------------------------------------------------------------ 4 manifest hygiene
    check("manifest status == design-review-pending and productionApproved == false", manifest.get("status") == "design-review-pending" and manifest.get("productionApproved") is False)
    need = ["repositoryId", "defaultTheme", "schemaValidatedThemes", "entryPoints", "allowlistVersion", "versionFieldNote"]
    check("manifest has %s" % ", ".join(need), all(k in manifest for k in need), str([k for k in need if k not in manifest]))
    eps = manifest.get("entryPoints", {})
    flat_eps = []
    for k, v in eps.items():
        flat_eps += v if isinstance(v, list) else [v]
    badep = [e for e in flat_eps if ".." in e or e.startswith("/") or re.match(r"^[A-Za-z]:", e) or not os.path.exists(os.path.join(REPO, e))]
    check("manifest entryPoints are all INSIDE design-repo/ and exist (no '../', no absolute)", not badep, str(badep))
    check("manifest defaultTheme resolves to a theme file in schemaValidatedThemes", manifest.get("defaultTheme") in manifest.get("schemaValidatedThemes", []) and os.path.isfile(os.path.join(REPO, "tokens/themes/%s.json" % manifest.get("defaultTheme"))))
    check("version fields are labeled (versionFieldNote says allowlistVersion is machine-checked, others documentation-only)", "documentation" in manifest.get("versionFieldNote", "").lower() and "machine" in manifest.get("versionFieldNote", "").lower())
    check("pageSpecVersion field is labeled documentation-only in the schema", "DOCUMENTATION ONLY" in schema["properties"]["pageSpecVersion"].get("description", ""))

    # ------------------------------------------------------------------ 5 templates / routes
    bad = []
    for tid, t in templates.items():
        for n in t["nodes"]:
            if not (isinstance(n, dict) and set(n) >= {"section", "required", "repeatable"} and isinstance(n["required"], bool) and isinstance(n["repeatable"], bool)):
                bad.append("%s:%r" % (tid, n))
            elif n["section"] not in sections:
                bad.append("%s: unknown section %s" % (tid, n["section"]))
            elif n.get("variant") and n["variant"] not in sections[n["section"]]["variants"]:
                bad.append("%s: %s variant %s" % (tid, n["section"], n["variant"]))
            elif sections[n["section"]]["variants"] and not n.get("variant") and tid != "home" and False:
                bad.append("variant missing")
    check("every template node is a structured {section, required, repeatable} object naming a real section/variant", not bad, str(bad[:4]))
    r_by_t = {}
    paths = [r["path"] for r in routes_doc["routes"]]
    for r in routes_doc["routes"]:
        r_by_t.setdefault(r["template"], []).append(r["path"])
    check("route coverage is 1:1: no duplicate paths, every route -> exactly one real template", len(paths) == len(set(paths)) and all(r["template"] in templates for r in routes_doc["routes"]))
    check("every template's `routes` equals the routes bound to it (no gap, no double assignment)", all(sorted(t["routes"]) == sorted(r_by_t.get(tid, [])) for tid, t in templates.items()), str({k: (templates[k]["routes"], r_by_t.get(k)) for k in templates if sorted(templates[k]["routes"]) != sorted(r_by_t.get(k, []))}))
    check("schema enums match templates.json / routes.json", sorted(schema["properties"]["template"]["enum"]) == sorted(templates) and sorted(schema["properties"]["route"]["enum"]) == sorted(paths))
    sheets = routes_doc["routeStylesheets"]
    mvr = jl("extraction/measured-values.json")["routeStylesheets"]["lists"]
    check("measured-values.json routeStylesheets == templates/routes.json routeStylesheets (same ordered lists)", {k: v["order"] for k, v in mvr.items()} == {k: v["order"] for k, v in sheets.items()})
    check("every template's stylesheetKey has a per-route stylesheet list", all(t["stylesheetKey"] in sheets for t in templates.values()))
    bad = []
    for sp in sections.values():
        for r in sp["responsive"]:
            if r["breakpoint"] not in jl("tokens/00-foundation/breakpoint.json")["breakpoint"]:
                bad.append((sp["id"], r["breakpoint"]))
    check("every section responsive breakpoint is a breakpoint token", not bad, str(bad))
    if have_src:
        app = open(os.path.join(SRC, "src/App.jsx"), encoding="utf-8").read()
        real_paths = re.findall(r'<Route path="([^"]+)"', app)
        want = set(real_paths) - {"*"}
        check("routes.json == the real <Route path> set in src/App.jsx (plus '*' as a behavior)", want == set(paths) and "*" in real_paths and any(b["path"] == "*" for b in routes_doc["behaviors"]), "App.jsx=%s routes.json=%s" % (sorted(want), sorted(paths)))
        posts = json.load(open(os.path.join(SRC, "src/data/blog-posts.json"), encoding="utf-8"))["posts"]
        inst = next(r for r in routes_doc["routes"] if r["path"] == "/blog/:slug")["instances"]
        check("blog slug instances match blog-posts.json (20 posts, 19 in sitemap)", inst["count"] == len(posts) and inst["inSitemap"] == sum(1 for x in posts if x["inSitemap"]), "%s vs %d/%d" % (inst, len(posts), sum(1 for x in posts if x["inSitemap"])))
        # per-route stylesheet lists vs the wrapper CSS imports
        bad = []
        for k, sh in sheets.items():
            txt = open(os.path.join(SRC, sh["importList"]), encoding="utf-8").read()
            got = ["357da7cf10d68108.css", "437c25afc566ca52.css"] + re.findall(r"original/([0-9a-f]{16}\.css)", txt)
            if got != sh["order"]:
                bad.append((k, got, sh["order"]))
        check("per-route stylesheet lists (ORDER) == the real src/styles/<route>.css import lists", not bad, str(bad[:2]))
        # blog maxima
        mx = {}
        for post in posts:
            for b in post["structure"]:
                if "words" in b:
                    mx[b["type"]] = max(mx.get(b["type"], 0), b["words"])
        oneof = sections["blog.prose"]["content"]["properties"]["blocks"]["items"]["oneOf"]
        cp = oneof[0]["properties"]["text"]["x-maxWords"]; cb = oneof[3]["properties"]["text"]["x-maxWords"]; cl = oneof[2]["properties"]["items"]["x-maxWordsTotal"]
        check("blog.prose maxWords recomputed from all 20 outlines (p %d, blockquote %d, list total %d)" % (mx["p"], mx["blockquote"], max(mx["ul"], mx["ol"])), (cp, cb, cl) == (mx["p"], mx["blockquote"], max(mx["ul"], mx["ol"])), "contract=%s" % ((cp, cb, cl),))
        # implementedBy files exist + page-level component ORDER == template node order (home, pricing)
        missing = sorted({f for sc in sections.values() for f in sc["implementedBy"] if not os.path.isfile(os.path.join(SRC, f))})
        check("every section's implementedBy file exists in the source project", not missing, str(missing))
        bad = []
        for tid, t in templates.items():
            pf = t.get("pageFile")
            if not pf:
                continue
            src = open(os.path.join(SRC, pf), encoding="utf-8").read()
            imports = dict(re.findall(r"import (\w+) from '([^']+)'", src))
            body = src[src.index("return ("):] if "return (" in src else src
            tags = [os.path.normpath(os.path.join(os.path.dirname(pf), imports[tg])) for tg in re.findall(r"<([A-Z]\w+)[ />]", body) if tg in imports]
            j = 0
            for n in t["nodes"]:
                impl = [os.path.normpath(x) for x in sections[n["section"]]["implementedBy"]]
                if j < len(tags) and tags[j] in impl:
                    continue
                if j + 1 < len(tags) and tags[j + 1] in impl:
                    j += 1
                    continue
                bad.append("%s: node %s not matched at page tag #%d (%s)" % (tid, n["section"], j, tags[j] if j < len(tags) else "end"))
            if j != len(tags) - 1:
                bad.append("%s: page renders %d components in order but the template maps only to #%d" % (tid, len(tags), j))
        check("route->template precision: component ORDER in the real page file (Home.jsx, Pricing.jsx) == template node order", not bad, "; ".join(bad[:3]))
    else:
        p("warn", "src/App.jsx route set / blog slug counts / stylesheet order / blog maxima / page component order not re-checked (source tree absent)")

    # ------------------------------------------------------------------ 6 graph <-> semantic_validate agreement
    sem_rules = {r["id"] for r in graph if "semantic" in r["enforcedBy"]}
    check("graph rules enforced by semantic_validate.py == IMPLEMENTED_RULES (no phantom, no unimplemented)", sem_rules == sv.IMPLEMENTED_RULES, "graph-only=%s code-only=%s" % (sorted(sem_rules - sv.IMPLEMENTED_RULES), sorted(sv.IMPLEMENTED_RULES - sem_rules)))
    check("every graph rule has severity error|warn", all(r["severity"] in ("error", "warn") for r in graph))
    g = {r["id"]: r for r in graph}
    has = lambda sec: {tid for tid, t in templates.items() if any(n["section"] == sec for n in t["nodes"])}
    all_t = set(templates)
    check("ONE_HERO_MARKETING exception list == templates lacking hero.marketing", set(g["ONE_HERO_MARKETING"]["exceptions"]["heroLessTemplates"]) == all_t - has("hero.marketing"))
    check("FOOTER rule exception == templates lacking shell.footer-closing", set(g["FOOTER_PRESENT_AND_LAST"]["exceptions"]["templatesWithoutFooter"]) == all_t - has("shell.footer-closing"))
    check("FLOATING_NAV_HOME_ONLY.onlyTemplates == templates containing shell.floating-nav", set(g["FLOATING_NAV_HOME_ONLY"]["params"]["onlyTemplates"]) == has("shell.floating-nav"))
    check("CORNER_NAV_FIRST exceptions + users partition all templates; users have it first", set(g["CORNER_NAV_FIRST"]["exceptions"]["embeddedInHero"]) | set(g["CORNER_NAV_FIRST"]["exceptions"]["ownHeader"]) == all_t - has("shell.corner-nav") and all(templates[t]["nodes"][0]["section"] == "shell.corner-nav" for t in has("shell.corner-nav")))
    check("every template with a footer ends with footer (+ optional floating nav)", all([n["section"] for n in templates[t]["nodes"]][-2:] in (["shell.footer-closing"], ["shell.footer-closing", "shell.floating-nav"]) or templates[t]["nodes"][-1]["section"] == "shell.footer-closing" for t in has("shell.footer-closing")))

    # ------------------------------------------------------------------ 7 schema <-> contract parity
    allof = schema["definitions"]["node"]["allOf"]
    bad = []
    for sid, s in sections.items():
        cid = "content_" + sid.replace(".", "_")
        d = schema["definitions"].get(cid)
        if not d or sorted(d["properties"]) != sorted(s["content"]["properties"]) or sorted(d["required"]) != sorted(s["content"]["required"]):
            bad.append(sid)
        m = schema["definitions"].get("motion_" + sid.replace(".", "_"))
        if not m or m["properties"]["reducedMotionFallback"]["const"] != s["motion"]["reducedMotionFallback"] or sorted(m["properties"]["patterns"]["items"]["enum"]) != sorted(s["motion"]["allowedPatterns"]):
            bad.append(sid + ":motion")
        if m and m.get("additionalProperties") is not False:
            bad.append(sid + ":motion-open")
        if not any(b.get("if", {}).get("properties", {}).get("section", {}).get("const") == sid for b in allof):
            bad.append(sid + ":no-branch")
    check("schema content_/motion_ definitions == section contracts (properties, required, patterns, locked fallback; motion CLOSED)", not bad, str(bad))
    check("schema node.section enum == all section contracts", sorted(schema["definitions"]["node"]["properties"]["section"]["enum"]) == sorted(sections))
    pats = set(patterns_doc["patterns"]); fbs = set(patterns_doc["reducedMotionFallbacks"])
    bad = [sid for sid, s in sections.items() if not set(s["motion"]["allowedPatterns"]) <= pats or s["motion"]["reducedMotionFallback"] not in fbs]
    check("every section's motion patterns/fallback exist in the motion-pattern catalog", not bad, str(bad))
    check("no open additionalProperties (true) anywhere in the schema or contracts", "\"additionalProperties\": true" not in json.dumps(schema, indent=1) and not any("\"additionalProperties\": true" in json.dumps(s, indent=1) for s in sections.values()))
    bad = [sid for sid, s in sections.items() for u in s["uses"]["primitives"] if u not in prims] + [sid for sid, s in sections.items() for u in s["uses"]["components"] if u not in comps]
    check("sections only `use` real primitives/components", not bad, str(bad))
    # example vs required (second-pass check, by hand-rolled walk)
    miss = []
    for n in example["nodes"]:
        c = sections[n["section"]]
        for f in c["content"]["required"]:
            if f not in n["content"]:
                miss.append((n["section"], f))
    check("example contains every required content field of each node's section", not miss, str(miss))

    # ------------------------------------------------------------------ 8 tokens
    hist = jl("extraction/derived-histograms.json")["site"]
    hmap = {k: {v[0]: v[1] for v in hist[k]} for k in ("color", "fontSize", "fontWeight", "lineHeight", "letterSpacing", "borderRadius", "transitionDuration", "easing")}
    bphist = {}
    for k, v in hist["breakpoint"]:
        px = int(float(k.split(":")[1][:-2])); bphist[px] = bphist.get(px, 0) + v
    kindmap = {"color.json": "color", "typography.json": None, "radius.json": "borderRadius", "breakpoint.json": "bp", "motion.json": None}
    bad, noev = [], []
    found = {}
    for f in tok_files["foundation"]:
        base = os.path.basename(f)
        doc = jl(f)
        for tid, t in leaf_tokens(doc):
            if "histogramCount" in t:
                top = tid.split(".")[0]
                if base == "color.json": exp = hmap["color"].get(t["$value"], 0)
                elif base == "radius.json": exp = hmap["borderRadius"].get(t["$value"], 0)
                elif base == "breakpoint.json": exp = bphist.get(int(t["$value"][:-2]), 0)
                elif top == "fontSize": exp = hmap["fontSize"].get(t["$value"], 0)
                elif top == "fontWeight": exp = hmap["fontWeight"].get(str(t["$value"]), 0)
                elif top == "lineHeight": exp = hmap["lineHeight"].get(("%g" % t["$value"]), 0)
                elif top == "letterSpacing": exp = hmap["letterSpacing"].get(t["$value"], 0)
                elif top == "duration": exp = hmap["transitionDuration"].get(t["$value"], 0)
                elif top == "easing": exp = hmap["easing"].get(t["$value"], 0)
                else: exp = t["histogramCount"]
                if exp != t["histogramCount"]:
                    bad.append("%s %s: recorded %s derived %s" % (base, tid, t["histogramCount"], exp))
            if base != "motion-patterns.json" and not (t.get("histogramCount", 0) > 0 or t.get("measuredQuotes")):
                noev.append("%s:%s" % (base, tid))
    check("histogramCount of every foundation token == recomputed from extraction/derived-histograms.json", not bad, "; ".join(bad[:4]))
    check("every foundation token has evidence (histogramCount > 0 or a quoted citation)", not noev, str(noev[:6]))
    fl = {}
    for f in tok_files["foundation"]:
        for tid, t in leaf_tokens(jl(f)):
            fl[tid] = t
    sem = jl("tokens/10-semantic/semantic.json")
    theme = jl("tokens/themes/light.json")
    bad = [k for k, t in sem["color"].items() if t["$ref"] not in fl]
    check("every semantic color $ref resolves to a foundation token", not bad, str(bad))
    bad = []
    for k, t in sem["color"].items():
        r = theme["resolved"].get("color." + k)
        if not r or r["ref"] != t["$ref"] or r["value"] != fl[t["$ref"]]["$value"]:
            bad.append(k)
    check("light theme resolves EVERY semantic color to its foundation value (no gaps, no drift)", not bad and len(theme["resolved"]) == len(sem["color"]), str(bad))
    bad = []
    for k, t in sem["typography"].items():
        for part in ("fontFamily", "fontWeight"):
            ref = t["$value"][part].strip("{}")
            if ref not in fl:
                bad.append((k, ref))
    check("semantic typography family/weight refs resolve", not bad, str(bad))
    comp = jl("tokens/20-component/component.json")["component"]
    bad = [k for k, t in comp.items() if "$ref" in t and t["$ref"] not in fl]
    sem_ids = set(sem["color"])
    for k, t in comp.items():
        v = str(t["$value"])
        if v.startswith("{") and v.strip("{}") not in sem_ids:
            bad.append(k)
    check("component token refs resolve to foundation/semantic tokens", not bad, str(bad))
    check("tokens: no mock-site brand colors tokenized (#eb1700 DoorDash, #5c0632 Qatar, #23727c Instacart, #69529d Ashby)", not any(t["$value"] in ("#eb1700", "#5c0632", "#23727c", "#69529d") for tid, t in fl.items() if tid.startswith("color.")))

    # ------------------------------------------------------------------ 9 asset-role registry: closure + PINNED values
    pol = roles_doc["pinnedPolicies"]
    enum = set(roles_doc["generationPolicies"])
    check("assetRole registry: generationPolicy in the closed 3-value enum", all(r["generationPolicy"] in enum for r in roles_doc["roles"]) and enum == {"must-reuse-exact", "must-not-fabricate", "may-generate-new"})
    bad = [r["id"] for r in roles_doc["roles"] if pol.get(r["id"]) != r["generationPolicy"]]
    check("PINNED policies: each role is exactly its pinned value (membership alone is not enough)", not bad and set(pol) == set(role_ids), str(bad))
    expect_nf = {"logo.third-party-wordmark", "icon.third-party-app", "screenshot.os-install-step", "screenshot.product-output", "photo.stock-cover", "photo.person-portrait", "photo.mock-product", "media.audio-sample"}
    check("compliance-critical roles hard-pinned to must-not-fabricate (logos, people, screenshots, recordings)", all(pol.get(r) == "must-not-fabricate" for r in expect_nf), str({r: pol.get(r) for r in expect_nf}))
    check("brand roles hard-pinned to must-reuse-exact", all(pol.get(r) == "must-reuse-exact" for r in ("brand.merlin-app-icon", "brand.merlin-mascot-art", "illustration.felt-scene", "art.footer-ascii")))
    ban = " ".join(roles_doc["hardBans"]) + " " + " ".join(r["guidance"] + r["description"] for r in roles_doc["roles"])
    names = ["Notion", "Salesforce", "Harvard", "HubSpot", "McKinsey", "Qatar", "DoorDash", "Instacart", "Ashby", "Merlin"]
    check("asset guidance explicitly names the real third-party marks it forbids (%s)" % ", ".join(names), all(n in ban for n in names) and "not for public redistribution" in ban.lower(), str([n for n in names if n not in ban]))
    bad = [x["id"] for x in roles_doc["assets"] if x["role"] not in role_ids]
    check("every registered asset has a registered role", not bad, str(bad))
    used_roles = set()
    for s in sections.values():
        js = json.dumps(s["content"])
        used_roles |= set(re.findall(r'"(?:logo|icon|brand|illustration|screenshot|photo|media|art)\.[a-z-]+"', js))
    used_roles = {x.strip('"') for x in used_roles}
    for d in list(prims.values()) + list(comps.values()):
        used_roles |= set(d.get("assetRoles", []))
    for s in sections.values():
        used_roles |= set(s.get("generatedAssetRoles", []))
    check("every assetRole is wired into a section content field or a primitive/component assetRoles list (fixed-scene assets)", set(role_ids) <= used_roles, str(sorted(set(role_ids) - used_roles)))
    if have_src:
        pub = os.path.join(SRC, "public", "assets")
        disk = {"public/assets/" + f for f in os.listdir(pub) if os.path.isfile(os.path.join(pub, f))} | {"public/assets/blog/" + f for f in os.listdir(os.path.join(pub, "blog"))}
        reg = {x["file"] for x in roles_doc["assets"] if x["file"]}
        check("asset registry == files on disk under public/assets (no phantom, no orphan)", disk == reg, "disk-only=%s registry-only=%s" % (sorted(disk - reg)[:3], sorted(reg - disk)[:3]))
        # every <img src> literal in the JSX maps to a registered asset
        reg_names = {os.path.basename(f) for f in reg}
        used = set()
        for jf in glob.glob(os.path.join(SRC, "src", "**", "*.jsx"), recursive=True) + glob.glob(os.path.join(SRC, "src", "**", "*.js"), recursive=True):
            used |= set(re.findall(r"/assets/([A-Za-z0-9._-]+\.(?:png|webp|svg|jpg|mp3))", open(jf, encoding="utf-8").read()))
        missing = sorted(u for u in used if u not in reg_names)
        check("every /assets/<file> literal referenced in src/**/*.jsx|js is a registered asset", not missing, str(missing))
        pj = json.load(open(os.path.join(SRC, "package.json")))
        mv = jl("extraction/measured-values.json")["sourceProject"]["dependencies"]
        deps = dict(pj["dependencies"], **pj["devDependencies"])
        drift = {k: (v, deps.get(k)) for k, v in mv.items() if deps.get(k) != v}
        check("source package.json versions == measured-values.json sourceProject.dependencies (snapshot drift)", not drift, str(drift))
    else:
        p("warn", "asset registry vs public/assets, /assets literals, package.json versions not re-checked (source tree absent)")

    # ------------------------------------------------------------------ 10 citations: range + quote content
    cite_re = re.compile(r"^(?P<path>[^:]+):(?P<a>\d+)(?:-(?P<b>\d+))?$")
    ncit = nbad = nwarn = nq = nqbad = 0
    cache = {}
    bad_list, quote_bad = [], []

    def lines_of(path):
        if path not in cache:
            for base in (REPO, SRC):
                fp = os.path.join(base, path)
                if os.path.isfile(fp):
                    cache[path] = (base, open(fp, encoding="utf-8", errors="replace").read().split("\n"))
                    break
            else:
                cache[path] = (None, None)
        return cache[path]

    def norm(s):
        return re.sub(r"\s+", " ", s)

    for f in files:
        doc = jl(f)
        stack = [(doc, f)]
        while stack:
            node, where = stack.pop()
            if isinstance(node, dict):
                if "measuredFrom" in node and isinstance(node["measuredFrom"], list):
                    cites = node["measuredFrom"]
                    for c in cites:
                        ncit += 1
                        m = cite_re.match(c)
                        if not m:
                            if os.path.isfile(os.path.join(REPO, c)):
                                continue  # whole-file in-repo evidence (e.g. derived-histograms.json)
                            nbad += 1; bad_list.append("%s: unparseable citation %r" % (where, c)); continue
                        base, L = lines_of(m.group("path"))
                        if L is None:
                            nwarn += 1; WARNED.append(m.group("path")); continue
                        hi = int(m.group("b") or m.group("a")); lo = int(m.group("a"))
                        if lo < 1 or hi < lo or hi > len(L) or (len(L) and L[-1] == "" and hi > len(L) - 1 and hi != len(L) and False):
                            nbad += 1; bad_list.append("%s: %s exceeds file length %d" % (where, c, len(L)))
                    for q in node.get("measuredQuotes", []):
                        nq += 1
                        m = cite_re.match(q["cite"])
                        if q["cite"] not in cites:
                            nqbad += 1; quote_bad.append("%s: quote cite %s not in measuredFrom" % (where, q["cite"])); continue
                        base, L = lines_of(m.group("path"))
                        if L is None:
                            continue
                        lo, hi = int(m.group("a")), int(m.group("b") or m.group("a"))
                        seg = norm(" ".join(L[lo - 1:hi]))
                        if norm(q["contains"]) not in seg:
                            nqbad += 1; quote_bad.append("%s: %s does not contain %r" % (where, q["cite"], q["contains"][:60]))
                for k, v in node.items():
                    stack.append((v, where))
            elif isinstance(node, list):
                for v in node:
                    stack.append((v, where))
    check("citation-range validity: %d citations resolve inside real files and do not exceed their length" % ncit, nbad == 0, "; ".join(bad_list[:4]))
    check("citation CONTENT: %d quoted citations contain their quoted text inside the cited line range" % nq, nqbad == 0, "; ".join(quote_bad[:4]))
    if nwarn:
        p("warn", "%d citation(s) into the source project could not be resolved (source tree absent) - range/content NOT verified" % nwarn)

    # ------------------------------------------------------------------ 11 misc evidence
    lc = jl("extraction/legal-template-comparison.json")
    check("/privacy + /terms grouping backed by a real structural comparison (verdict SAME_TEMPLATE)", lc.get("verdict") == "SAME_TEMPLATE" and lc.get("sameTopLevelSequence") is True)
    mvv = jl("extraction/measured-values.json")
    check("measured-values.json records the structurally unusual facts (live source, placeholder copy, local stand-ins, per-route CSS, time-of-day, deliberate absences)", all(k in mvv for k in ("liveSource", "placeholderCopy", "localStandIns", "perRouteCssIsolation", "timeOfDayCopy", "deliberateAbsences", "constraints", "specDiscrepancies")))
    check("constraint 'no-external-requests' is recorded", any(c["id"] == "no-external-requests" for c in mvv["constraints"]))

    # ------------------------------------------------------------------ 13 baseline 2.0.0 checks
    baseline_checks(have_src, SRC, manifest, allow, roles_doc, schema, templates, routes_doc, graph, sections, sv, ctx)

    # ------------------------------------------------------------------ 12 no absolute paths
    hits = []
    for root, _, fs in os.walk(REPO):
        for fn in fs:
            if fn.endswith((".pyc",)) or fn == ".DS_Store":
                continue
            fp = os.path.join(root, fn)
            try:
                t = open(fp, encoding="utf-8").read()
            except Exception:
                continue
            if re.search("/" + "Users/|/ho" + "me/[a-z]|[A-Za-z]:" + "\\\\Users", t):
                hits.append(os.path.relpath(fp, REPO))
    check("no absolute local paths anywhere in the repo (unix home dirs, windows user dirs)", not hits, str(hits))
    junk = [x for x in relfiles("**/*") if "__MACOSX" in x or x.endswith(".DS_Store") or "__pycache__" in x]
    check("no __MACOSX/.DS_Store/__pycache__ inside the repo", not junk, str(junk))
    return finish()


def baseline_checks(have_src, SRC, manifest, allow, roles_doc, schema, templates, routes_doc, graph, sections, sv, ctx):
    import hashlib
    from jsonschema import Draft7Validator
    # ---- R1 mode + R4 generation examples
    check("PageSpec schema: required closed mode enum [clone, generation] (+ theme, tokens required)", schema["properties"]["mode"].get("enum") == ["clone", "generation"] and {"mode", "theme", "tokens"} <= set(schema["required"]))
    ex = jl("schema/example.pagespec.json")
    check("clone example declares mode=clone", ex.get("mode") == "clone")
    gens = {}
    for f in relfiles("schema/examples/*.pagespec.json"):
        d = jl(f)
        e, w = sv.validate_all(d, ctx)
        check("%s: Draft-07 + semantic, 0 errors 0 warnings" % f, not e and not w, "; ".join((e + w)[:3]))
        if d.get("mode") == "generation":
            gens.setdefault(d["template"], []).append(f)
    check("a mode=generation example exists for EVERY template family (%d templates)" % len(templates), set(gens) == set(templates), "missing %s" % sorted(set(templates) - set(gens)))
    # ---- R3 availability pins
    reg = {r["id"]: r.get("availability") for r in roles_doc["roles"]}
    check("PINNED_AVAILABILITY (verify_all.py) == PINNED_AVAILABILITY (semantic_validate.py)", PINNED_AVAILABILITY == sv.PINNED_AVAILABILITY)
    check("assets/asset-roles.json availability == PINNED_AVAILABILITY (registry edit alone cannot loosen a role)", reg == PINNED_AVAILABILITY, str(sorted(k for k in set(reg) | set(PINNED_AVAILABILITY) if reg.get(k) != PINNED_AVAILABILITY.get(k))))
    check("registry pinnedAvailability mirror == PINNED_AVAILABILITY", roles_doc.get("pinnedAvailability") == PINNED_AVAILABILITY)
    check("availability is a closed 3-value enum", set(reg.values()) <= {"clone-only", "generation-safe", "blocked-for-generation"} and set(roles_doc["availabilityValues"]) == {"clone-only", "generation-safe", "blocked-for-generation"})
    check("required generation-safe roles exist (placeholder mark, user-supplied, generated illustration, placeholder screenshot, fictional person, placeholder customer logo, placeholder URL, original copy)", REQUIRED_GENERATION_SAFE <= {k for k, v in reg.items() if v == "generation-safe"})
    bad = [r["id"] for r in roles_doc["roles"] if r["availability"] != "generation-safe" and (not r.get("generationSafeSubstitutes") or any(PINNED_AVAILABILITY.get(s) != "generation-safe" for s in r["generationSafeSubstitutes"]))]
    bad += [r["id"] for r in roles_doc["roles"] if len(r.get("generatedModeGuidance", "")) < 30]
    check("every non-safe role has generation-safe substitutes; every role has generatedModeGuidance", not bad, str(bad))
    check("no real logo/wordmark/brand role is generation-safe or must-reuse-exact-in-generation (brand.merlin-*, logo.third-party-*, icon.third-party-app)", all(PINNED_AVAILABILITY[r] != "generation-safe" for r in ("brand.merlin-app-icon", "brand.merlin-mascot-art", "logo.third-party-wordmark", "icon.third-party-app")))
    bad = [sid for sid, s in sections.items() if any(PINNED_AVAILABILITY.get(r) != "generation-safe" for r in s.get("generatedAssetRoles", [])) or "copy.original" not in s.get("generatedAssetRoles", [])]
    check("every section lists generatedAssetRoles, all generation-safe (incl. copy.original)", not bad, str(bad))
    # ---- R8 retrieval pins
    check("RETRIEVAL_INELIGIBLE (verify_all.py) == RETRIEVAL_INELIGIBLE (semantic_validate.py)", RETRIEVAL_INELIGIBLE == sv.RETRIEVAL_INELIGIBLE)
    falses = {sid for sid, s in sections.items() if s.get("retrievalEligible") is False}
    check("contracts with retrievalEligible:false == RETRIEVAL_INELIGIBLE pin; every contract has an explicit boolean", falses == RETRIEVAL_INELIGIBLE and all(isinstance(s.get("retrievalEligible"), bool) for s in sections.values()), "contracts=%s pin=%s" % (sorted(falses), sorted(RETRIEVAL_INELIGIBLE)))
    check("ineligible contracts carry a reason >= 30 chars", all(len(sections[s].get("retrievalIneligibleReason", "")) >= 30 for s in falses))
    look = sorted(sid for sid, s in sections.items() if RUNTIME_UI.search(sid) and sid not in RETRIEVAL_INELIGIBLE)
    check("every section whose id looks like runtime UI is in the retrieval pin", not look, str(look))
    bad = [e["id"] for e in allow["sections"] if e.get("retrievalEligible") is not sections[e["id"]].get("retrievalEligible")]
    check("allowlist retrievalEligible == contract retrievalEligible", not bad, str(bad))
    # ---- R7 closed contract schema + provenance
    cs = jl("schema/section-contract.schema.json")
    Draft7Validator.check_schema(cs)
    bad = ["%s: %s" % (sid, e.message[:80]) for sid, s in sections.items() for e in Draft7Validator(cs).iter_errors(s)]
    check("every section contract validates against the CLOSED schema/section-contract.schema.json", not bad and cs.get("additionalProperties") is False, "; ".join(bad[:3]))
    bad = [sid for sid, s in sections.items() if s["semantic"]["id"] != sid or s["source"]["id"] == sid]
    check("semantic.id == contract id and source.id != contract id", not bad, str(bad))
    import build_section_provenance as bsp
    probs = bsp.check(REPO, SRC)
    if probs is None:
        p("warn", "section source ranges/tags not re-derived (source tree absent)")
    else:
        check("source {file, tag, lines} re-derived from the real files: range inside file, tag opens at start line, semantic category pinned", not probs, "; ".join(probs[:3]))
    # ---- R6 repeatable nodes
    rep_nodes = sorted({n["section"] for t in templates.values() for n in t["nodes"] if n.get("repeatable")})
    gx = {r["id"]: r for r in graph}
    check("NO_ADJACENT_SAME_SECTION_VARIANT repeatable exception == repeatable template nodes", sorted(gx["NO_ADJACENT_SAME_SECTION_VARIANT"]["exceptions"]["repeatableTemplateNodes"]) == rep_nodes, str(rep_nodes))
    check("whole-document legal.body is gone (decomposed into legal.contents / legal.section / legal.document-footer)", "legal.body" not in sections and {"legal.contents", "legal.section", "legal.document-footer"} <= set(sections))
    if have_src:
        posts = json.load(open(os.path.join(SRC, "src/data/blog-posts.json"), encoding="utf-8"))["posts"]
        chap, blocks = 0, 0
        for post in posts:
            s = post["structure"]; h = [i for i, b in enumerate(s) if b["type"] == "h2"]
            idx = ([0] if (not h or h[0] > 0) else []) + h + [len(s)]
            chap = max(chap, len(idx) - 1); blocks = max(blocks, max(idx[i + 1] - idx[i] for i in range(len(idx) - 1)))
        mr = next(n for n in templates["blog-post"]["nodes"] if n["section"] == "blog.prose")["maxRepeat"]
        mi = sections["blog.prose"]["content"]["properties"]["blocks"]["maxItems"]
        check("blog.prose maxRepeat (%d chapters) and per-chapter maxItems (%d blocks) recomputed from blog-posts.json" % (chap, blocks), (mr, mi) == (chap, blocks), "template=%s contract=%s" % (mr, mi))
    # ---- R9 wrapper gate
    import wrapper_gate
    ge, gw, _ = wrapper_gate.run(REPO)
    check("wrapper gate (HERO 1800/3000px, share 50/60%%, measured at %dpx): 0 errors" % wrapper_gate.REQUIRED_VIEWPORT, not ge, "; ".join(ge[:3]))
    for w in gw:
        p("warn", "wrapper gate: " + w)
    check("wrapper gate thresholds pinned in code (1800/3000/0.5/0.6/1440)", (wrapper_gate.HERO_WARN_PX, wrapper_gate.HERO_ERROR_PX, wrapper_gate.SHARE_WARN, wrapper_gate.SHARE_ERROR, wrapper_gate.REQUIRED_VIEWPORT) == (1800, 3000, 0.5, 0.6, 1440))
    # ---- R10 token catalog + policy
    import build_token_catalog as btc
    cat = jl("tokens/llm/token-catalog.json")
    check("tokens/llm/token-catalog.json == rebuild from the token files (build_token_catalog.py)", cat == btc.build(), "run python3 extraction/build_token_catalog.py --write after a token change")
    pol = jl("tokens/llm/token-policy.json")
    cats = set(cat["counts"]["byCategory"])
    used = set(pol["approvedCategoriesForPageSpec"]) | set(pol["catalogOnlyCategories"]) | {c for s in pol["pageSpecTokenSlots"].values() for c in s["allowCategories"]}
    check("token-policy category names are real catalog categories (and every category is classified)", used <= cats and set(pol["approvedCategoriesForPageSpec"]) | set(pol["catalogOnlyCategories"]) == cats, "unknown=%s unclassified=%s" % (sorted(used - cats), sorted(cats - set(pol["approvedCategoriesForPageSpec"]) - set(pol["catalogOnlyCategories"]))))
    tp = schema["properties"]["tokens"]
    check("token-policy slots == PageSpec tokens properties; required slots == schema required", set(pol["pageSpecTokenSlots"]) == set(tp["properties"]) and sorted(k for k, v in pol["pageSpecTokenSlots"].items() if v["required"]) == sorted(tp["required"]) and tp.get("additionalProperties") is False)
    bad = [(k, px) for k, v in pol["pageSpecTokenSlots"].items() for px in v["allowPrefixes"] if not any(path.startswith(px) and cat["tokens"][path]["approvedForPageSpec"] for path in cat["tokens"])]
    bad += [x for v in pol["pageSpecTokenSlots"].values() for x in v["deny"] if x not in cat["tokens"]]
    bad += [x for x in pol["notApproved"] if x not in cat["tokens"] or cat["tokens"][x]["approvedForPageSpec"]]
    bad += [x for x in pol["themeRestrictions"]["schemes"]["scene-dark"] if cat["tokens"].get(x, {}).get("scheme") != "scene-dark"]
    check("token-policy names resolve: every slot prefix matches an approved token, deny/notApproved/scheme paths exist", not bad, str(bad[:4]))
    check("token-policy themes == catalog themes == schema theme enum", pol["themeRestrictions"]["themes"] == sorted(cat["themes"]) == schema["properties"]["theme"]["enum"])
    ep = manifest.get("entryPoints", {})
    mc = manifest.get("counts", {}).get("tokenCatalog", {})
    check("manifest registers token-catalog.json + token-policy.json (entryPoints) and their counts match", ep.get("tokenCatalog") == "tokens/llm/token-catalog.json" and ep.get("tokenPolicy") == "tokens/llm/token-policy.json" and mc == {"tokens": cat["counts"]["tokens"], "approvedForPageSpec": cat["counts"]["approvedForPageSpec"], "categories": len(cat["counts"]["byCategory"]), "pageSpecTokenSlots": len(pol["pageSpecTokenSlots"])}, str(mc))
    # ---- R2 source identity registry
    import build_source_identity as bsi
    sid_doc = jl("schema/source-identity.json")
    if have_src:
        check("schema/source-identity.json == rebuild from the real source (build_source_identity.py)", sid_doc == bsi.build(SRC), "run python3 extraction/build_source_identity.py --write")
        import textnorm as tn
        bad = []
        for x in sid_doc["terms"] + sid_doc["assetFiles"]:
            for ev in x["evidence"]:
                f, _, ln = ev.partition(":")
                fp = os.path.join(SRC, f)
                txt = open(fp, encoding="utf-8", errors="replace").read().split("\n")[int(ln) - 1] if ln else os.path.basename(fp)
                txt = txt.replace("&amp;", "&")
                if not tn.contains_terms(tn.tokens(txt), x["tokens"]):
                    bad.append(ev)
        check("every source-identity term's file:line evidence really contains the term", not bad, str(bad[:3]))
    else:
        p("warn", "schema/source-identity.json not re-derived (source tree absent)")
    check("source-identity registry has brand, customer, person, URL, claim terms and copy shingles", {"BRAND", "CUSTOMER", "PERSON", "URL", "CLAIM"} <= {x["category"] for x in sid_doc["terms"]} and len(sid_doc["copy"]["hashes"]) > 100)
    # ---- requirement 10: common-policy binding
    dp = manifest.get("designPolicy", {})
    ok = manifest.get("category") == "saas" and dp.get("policyId") == "n0-saas-design-constraints-common" and dp.get("policyVersion") == "0.1.0" and dp.get("commonIrVersion") == "0.5" and dp.get("enforcementMode") == "hard-and-soft"
    check("manifest binds category=saas to n0-saas-design-constraints-common 0.1.0 (commonIrVersion 0.5, hard-and-soft)", ok, str(dp))
    pf = dp.get("ref", "")
    exists = bool(pf) and os.path.isfile(os.path.join(REPO, pf))
    check("designPolicy.ref points at an existing policy file inside the repo", exists, pf)
    if exists:
        pd = jl(pf)
        check("policy file agrees with the manifest (policyId, version, isSaaS, pending architecture review)", pd["policyId"] == dp["policyId"] and pd["policyVersion"] == dp["policyVersion"] and pd["classification"]["isSaaS"] is True and pd["approval"]["architectureDecisionRecorded"] is False)
        h = hashlib.sha256()
        for f in pd["enforcedBy"]:
            h.update(f.encode() + b"\n" + open(os.path.join(REPO, f), "rb").read() + b"\n")
        check("designPolicy.contentHash == sha256 over the policy's enforcedBy files", dp.get("contentHash") == "sha256:" + h.hexdigest(), "manifest=%s computed=sha256:%s" % (dp.get("contentHash"), h.hexdigest()))
        if have_src:
            bad = []
            for e in pd["classification"]["evidence"]:
                f, _, rg = e["cite"].partition(":")
                a_, _, b_ = rg.partition("-")
                n = len(open(os.path.join(SRC, f), encoding="utf-8").read().split("\n"))
                if int(b_ or a_) > n:
                    bad.append(e["cite"])
            check("policy classification evidence cites resolve inside the real files", not bad, str(bad))


def finish():
    print("\nSUMMARY: %d passed, %d warnings, %d FAILED" % (OUT["pass"], OUT["warn"], OUT["fail"]))
    return 1 if OUT["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
