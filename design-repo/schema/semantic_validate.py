#!/usr/bin/env python3
"""Semantic validator for Merlin design-repo PageSpecs.

Enforces what JSON Schema (schema/pagespec.schema.json) cannot express, by CROSS-REFERENCING the
declared template against that template's real node list (templates/templates.json) - never
nodes[] in isolation - plus the rhythm rules in compatibility/graph.json (severity error|warn),
per-(section, variant) rules from each section contract, per-field maxWords, asset-role policy and the
no-external-requests constraint.

Usage:  python3 schema/semantic_validate.py [spec.json ...]      (default: schema/example.pagespec.json)
Exit code 1 if any ERROR is reported (warnings are printed but non-fatal).

The repo root is derived from __file__ (no absolute paths). Exceptions listed in the graph (hero-less
templates, footer-less templates, ...) are READ FROM THE GRAPH, so the rule prose and this code cannot
silently diverge; extraction/verify_all.py additionally checks that IMPLEMENTED_RULES matches graph.json.
"""
import glob, json, os, re, sys
sys.dont_write_bytecode = True  # keep the repo free of __pycache__

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

# Rule ids implemented here (verify_all.py compares this set with compatibility/graph.json).
IMPLEMENTED_RULES = {
    "ROUTE_TEMPLATE_BINDING", "TEMPLATE_ORDER", "ONE_HERO_MARKETING", "FOOTER_PRESENT_AND_LAST",
    "FLOATING_NAV_HOME_ONLY", "CORNER_NAV_FIRST", "NO_ADJACENT_SAME_SECTION_VARIANT", "ONE_PER_PAGE",
    "MAX_ONE_PINNED_STAGE", "MOTION_FALLBACK_REQUIRED", "VARIANT_FIELD_RULES", "ASSET_REF_POLICY",
    "NO_EXTERNAL_REQUESTS", "MAX_WORDS", "LEGAL_ACTIVE_TAB_MATCHES_ROUTE", "LEGAL_INTRO_ONLY_ON_PRIVACY",
    "BLOG_FEATURED_NOT_IN_STORY_LIST", "PLAN_ONE_PRIMARY_CTA",
}


def _load(root, rel):
    with open(os.path.join(root, rel), encoding="utf-8") as f:
        return json.load(f)


class Ctx:
    def __init__(self, root=REPO):
        self.root = root
        self.templates = _load(root, "templates/templates.json")["templates"]
        rj = _load(root, "templates/routes.json")
        self.routes = {r["path"]: r for r in rj["routes"]}
        self.graph = {r["id"]: r for r in _load(root, "compatibility/graph.json")["rules"]}
        self.sections = {}
        for p in sorted(glob.glob(os.path.join(root, "sections", "*.json"))):
            s = json.load(open(p, encoding="utf-8"))
            self.sections[s["id"]] = s
        ar = _load(root, "tokens/llm/asset-roles.json")
        self.roles = {r["id"]: r for r in ar["roles"]}
        self.assets = {a["id"]: a for a in ar["assets"]}
        self.pinned = ar["pinnedPolicies"]
        self.pageschema = _load(root, "schema/pagespec.schema.json")


def words(s):
    return len(str(s).split())


class Report:
    def __init__(self, ctx):
        self.ctx, self.errors, self.warnings = ctx, [], []

    def add(self, rule, path, msg):
        sev = self.ctx.graph[rule]["severity"] if rule in self.ctx.graph else "error"
        (self.errors if sev == "error" else self.warnings).append("%s %s: %s" % (rule, path, msg))


def strings(node, path="$"):
    if isinstance(node, str):
        yield path, node
    elif isinstance(node, dict):
        for k, v in node.items():
            for x in strings(v, "%s.%s" % (path, k)):
                yield x
    elif isinstance(node, list):
        for i, v in enumerate(node):
            for x in strings(v, "%s[%d]" % (path, i)):
                yield x


def leaf_words(node):
    return sum(words(s) for _, s in strings(node))


def pick_branch(schema, data):
    """oneOf branch selection by the `type` discriminator."""
    for br in schema["oneOf"]:
        t = br.get("properties", {}).get("type", {})
        if isinstance(data, dict) and (t.get("const") == data.get("type") or data.get("type") in t.get("enum", [])):
            return br
    return None


def walk(rep, data, schema, path, node_path, on_asset):
    """Walk data against a contract field schema, applying x-maxWords / x-maxWordsTotal / asset checks."""
    if schema is None:
        return
    if schema.get("$ref") == "#/definitions/assetRef":
        if isinstance(data, dict):
            on_asset(data, schema.get("x-allowedRoles", []), path)
        return
    if "oneOf" in schema:
        br = pick_branch(schema, data)
        if br is not None:
            walk(rep, data, br, path, node_path, on_asset)
        return
    if isinstance(data, str):
        mw = schema.get("x-maxWords")
        if mw is not None and words(data) > mw:
            rep.add("MAX_WORDS", node_path + path, "%d words > maxWords %d" % (words(data), mw))
    elif isinstance(data, dict):
        props = schema.get("properties", {})
        for k, v in data.items():
            if k in props:
                walk(rep, v, props[k], path + "." + k, node_path, on_asset)
    elif isinstance(data, list):
        tot = schema.get("x-maxWordsTotal")
        if tot is not None and leaf_words(data) > tot:
            rep.add("MAX_WORDS", node_path + path, "%d words in list > maxWordsTotal %d" % (leaf_words(data), tot))
        for i, v in enumerate(data):
            walk(rep, v, schema.get("items"), "%s[%d]" % (path, i), node_path, on_asset)


def asset_checker(rep, ctx, node_path):
    def check(a, allowed, path):
        role, ref = a.get("assetRole"), a.get("assetRef", "")
        p = node_path + path
        if role not in ctx.roles:
            rep.add("ASSET_REF_POLICY", p, "assetRole %r is not in the closed role registry" % role)
            return
        if allowed and role not in allowed:
            rep.add("ASSET_REF_POLICY", p, "role %s not allowed for this field (allowed: %s)" % (role, ", ".join(allowed)))
        policy = ctx.roles[role]["generationPolicy"]
        if ref.startswith("generate:") and policy != "may-generate-new":
            rep.add("ASSET_REF_POLICY", p, "%s is %s: generate: refs are forbidden (use reuse: or placeholder:neutral)" % (role, policy))
        elif ref.startswith("reuse:"):
            asset = ctx.assets.get(ref[6:])
            if asset is None:
                rep.add("ASSET_REF_POLICY", p, "unknown asset id %s" % ref[6:])
            elif asset["role"] != role:
                rep.add("ASSET_REF_POLICY", p, "asset %s is registered as role %s, not %s" % (ref[6:], asset["role"], role))
        elif not (ref.startswith("generate:") or ref == "placeholder:neutral"):
            rep.add("ASSET_REF_POLICY", p, "assetRef %r is not reuse:/generate:/placeholder:neutral" % ref)
    return check


def match_template(rep, spec, tmpl):
    """TEMPLATE_ORDER: consume spec nodes against the template's real node list."""
    nodes, i = spec.get("nodes", []), 0
    used = set()
    for e in tmpl["nodes"]:
        taken = 0
        while i < len(nodes) and nodes[i].get("section") == e["section"] and (not e.get("variant") or nodes[i].get("variant") == e["variant"]):
            if taken >= 1 and not e["repeatable"]:
                break
            used.add(i)
            i += 1
            taken += 1
        if taken == 0 and e["required"]:
            rep.add("TEMPLATE_ORDER", "nodes", "missing required %s%s for template %r (or out of order)" % (e["section"], "/" + e["variant"] if e.get("variant") else "", spec.get("template")))
    known = [e["section"] for e in tmpl["nodes"]]
    for j in range(len(nodes)):
        if j in used:
            continue
        sec = nodes[j].get("section")
        if sec not in known:
            rep.add("TEMPLATE_ORDER", "nodes[%d]" % j, "section %s is not part of template %r" % (sec, spec.get("template")))
        else:
            rep.add("TEMPLATE_ORDER", "nodes[%d]" % j, "%s%s is duplicated, has the wrong variant, or is out of the template's order" % (sec, "/" + str(nodes[j].get("variant")) if nodes[j].get("variant") else ""))


def validate(spec, ctx=None):
    """Return (errors, warnings) lists of strings."""
    ctx = ctx or Ctx()
    rep = Report(ctx)
    nodes = spec.get("nodes", []) if isinstance(spec, dict) else []
    tname, route = spec.get("template"), spec.get("route")

    # registry pinned policies (load-bearing closed set)
    for rid, pol in ctx.pinned.items():
        if rid in ctx.roles and ctx.roles[rid]["generationPolicy"] != pol:
            rep.add("ASSET_REF_POLICY", "tokens/llm/asset-roles.json", "role %s has policy %s but is pinned to %s" % (rid, ctx.roles[rid]["generationPolicy"], pol))

    # ROUTE_TEMPLATE_BINDING
    r = ctx.routes.get(route)
    if r is None:
        rep.add("ROUTE_TEMPLATE_BINDING", "route", "%r is not a real route" % route)
    elif r["template"] != tname:
        rep.add("ROUTE_TEMPLATE_BINDING", "route", "route %s is bound to template %r, not %r" % (route, r["template"], tname))
    tmpl = ctx.templates.get(tname)
    if tmpl is None:
        rep.add("TEMPLATE_ORDER", "template", "unknown template %r" % tname)
        return rep.errors, rep.warnings

    match_template(rep, spec, tmpl)

    secs = [n.get("section") for n in nodes]
    keys = [(n.get("section"), n.get("variant")) for n in nodes]

    # ONE_HERO_MARKETING
    g = ctx.graph["ONE_HERO_MARKETING"]
    heroless = g["exceptions"]["heroLessTemplates"]
    cnt = secs.count(g["params"]["section"])
    if cnt > g["params"]["max"]:
        rep.add("ONE_HERO_MARKETING", "nodes", "%d hero.marketing nodes (max %d)" % (cnt, g["params"]["max"]))
    if tname in heroless and cnt:
        rep.add("ONE_HERO_MARKETING", "nodes", "template %r is hero-less (named exception) but has hero.marketing" % tname)

    # FOOTER_PRESENT_AND_LAST
    g = ctx.graph["FOOTER_PRESENT_AND_LAST"]
    foot, follow = g["params"]["section"], g["params"]["mayBeFollowedBy"]
    if tname in g["exceptions"]["templatesWithoutFooter"]:
        if foot in secs:
            rep.add("FOOTER_PRESENT_AND_LAST", "nodes", "template %r has no footer" % tname)
    else:
        if foot not in secs:
            rep.add("FOOTER_PRESENT_AND_LAST", "nodes", "missing %s" % foot)
        else:
            idx = secs.index(foot)
            if not all(s in follow for s in secs[idx + 1:]):
                rep.add("FOOTER_PRESENT_AND_LAST", "nodes", "%s must be last (only %s may follow)" % (foot, ", ".join(follow)))

    # FLOATING_NAV_HOME_ONLY
    g = ctx.graph["FLOATING_NAV_HOME_ONLY"]
    if g["params"]["section"] in secs and tname not in g["params"]["onlyTemplates"]:
        rep.add("FLOATING_NAV_HOME_ONLY", "nodes", "shell.floating-nav only exists on %s" % ", ".join(g["params"]["onlyTemplates"]))

    # CORNER_NAV_FIRST
    g = ctx.graph["CORNER_NAV_FIRST"]
    if g["params"]["section"] in secs:
        if tname in g["exceptions"]["embeddedInHero"] + g["exceptions"]["ownHeader"]:
            rep.add("CORNER_NAV_FIRST", "nodes", "template %r embeds/owns its nav; shell.corner-nav is not allowed" % tname)
        elif secs[0] != g["params"]["section"]:
            rep.add("CORNER_NAV_FIRST", "nodes", "shell.corner-nav must be the first node")

    # NO_ADJACENT_SAME_SECTION_VARIANT
    for a in range(1, len(keys)):
        if keys[a] == keys[a - 1]:
            rep.add("NO_ADJACENT_SAME_SECTION_VARIANT", "nodes[%d]" % a, "%s/%s repeated adjacently" % keys[a])

    # ONE_PER_PAGE (keyed on (section, variant) where the contract says so)
    seen = {}
    for a, n in enumerate(nodes):
        c = ctx.sections.get(n.get("section"))
        if not c:
            continue
        cons = c.get("constraints", {})
        key = None
        if cons.get("onePerPagePerVariant"):
            key = (n["section"], n.get("variant"))
        elif cons.get("onePerPage"):
            key = (n["section"], None)
        if key:
            if key in seen:
                rep.add("ONE_PER_PAGE", "nodes[%d]" % a, "%s%s appears more than once" % (key[0], "/" + key[1] if key[1] else ""))
            seen[key] = a

    # MAX_ONE_PINNED_STAGE
    g = ctx.graph["MAX_ONE_PINNED_STAGE"]
    pinned = sum(1 for n in nodes if g["params"]["pattern"] in (n.get("motion", {}) or {}).get("patterns", []))
    if pinned > g["params"]["max"]:
        rep.add("MAX_ONE_PINNED_STAGE", "nodes", "%d nodes use %s" % (pinned, g["params"]["pattern"]))

    # per-node rules
    for a, n in enumerate(nodes):
        np_ = "nodes[%d]" % a
        c = ctx.sections.get(n.get("section"))
        if c is None:
            continue
        content = n.get("content", {})
        mo = n.get("motion")
        # MOTION_FALLBACK_REQUIRED
        if not isinstance(mo, dict) or "reducedMotionFallback" not in mo:
            rep.add("MOTION_FALLBACK_REQUIRED", np_, "missing motion.reducedMotionFallback")
        else:
            if mo["reducedMotionFallback"] != c["motion"]["reducedMotionFallback"]:
                rep.add("MOTION_FALLBACK_REQUIRED", np_, "reducedMotionFallback %r != locked %r" % (mo["reducedMotionFallback"], c["motion"]["reducedMotionFallback"]))
            for p in mo.get("patterns", []):
                if p not in c["motion"]["allowedPatterns"]:
                    rep.add("MOTION_FALLBACK_REQUIRED", np_, "pattern %r not allowed for %s" % (p, c["id"]))
        # VARIANT_FIELD_RULES
        variants = c.get("variants", [])
        if variants and n.get("variant") not in variants:
            rep.add("VARIANT_FIELD_RULES", np_, "variant %r not in %s" % (n.get("variant"), variants))
        if not variants and "variant" in n:
            rep.add("VARIANT_FIELD_RULES", np_, "%s has no variants" % c["id"])
        for vr in c.get("variantRules", []):
            if vr["variant"] != n.get("variant"):
                continue
            for f in vr.get("required", []):
                if f not in content:
                    rep.add("VARIANT_FIELD_RULES", np_, "%s/%s requires content.%s" % (c["id"], vr["variant"], f))
            for f in vr.get("forbidden", []):
                if f in content:
                    rep.add("VARIANT_FIELD_RULES", np_, "%s/%s forbids content.%s" % (c["id"], vr["variant"], f))
            for k, v in vr.get("pinned", {}).items():
                if content.get(k) != v:
                    rep.add("VARIANT_FIELD_RULES", np_, "%s/%s pins content.%s = %r (got %r)" % (c["id"], vr["variant"], k, v, content.get(k)))
            for p in vr.get("forbiddenPatterns", []):
                if p in (mo or {}).get("patterns", []):
                    rep.add("VARIANT_FIELD_RULES", np_, "%s/%s forbids motion pattern %s" % (c["id"], vr["variant"], p))
        # MAX_WORDS + ASSET_REF_POLICY
        walk(rep, content, c["content"], ".content", np_, asset_checker(rep, ctx, np_))

    # meta maxWords
    ms = ctx.pageschema["properties"]["meta"]["properties"]
    meta = spec.get("meta", {})
    for k in ("title", "description"):
        if isinstance(meta.get(k), str) and words(meta[k]) > ms[k]["x-maxWords"]:
            rep.add("MAX_WORDS", "meta." + k, "%d words > maxWords %d" % (words(meta[k]), ms[k]["x-maxWords"]))

    # NO_EXTERNAL_REQUESTS
    for p, s in strings(spec):
        if re.search(r"\b(?:https?|ftp|wss?)://", s, re.I):
            rep.add("NO_EXTERNAL_REQUESTS", p, "external URL in %r" % s[:60])

    # legal rules
    if tname == "legal":
        head = next((n for n in nodes if n.get("section") == "legal.heading"), None)
        if head:
            tab = head.get("content", {}).get("activeTab")
            want = {"/privacy": "privacy", "/terms": "terms"}.get(route)
            if want and tab != want:
                rep.add("LEGAL_ACTIVE_TAB_MATCHES_ROUTE", "legal.heading", "route %s needs activeTab %r, got %r" % (route, want, tab))
            if route == "/terms" and "intro" in head.get("content", {}):
                rep.add("LEGAL_INTRO_ONLY_ON_PRIVACY", "legal.heading", "/terms has no intro paragraph on the real page")

    # blog featured vs list
    if tname == "blog-index":
        feat = next((n for n in nodes if n.get("section") == "blog.featured"), None)
        lst = next((n for n in nodes if n.get("section") == "blog.story-list"), None)
        if feat and lst:
            slug = feat.get("content", {}).get("slug")
            if slug in [s.get("slug") for s in lst.get("content", {}).get("stories", []) if isinstance(s, dict)]:
                rep.add("BLOG_FEATURED_NOT_IN_STORY_LIST", "blog.story-list", "featured slug %r is also in the story list" % slug)

    # pricing plans
    if tname == "pricing":
        pl = next((n for n in nodes if n.get("section") == "pricing.plans"), None)
        if pl:
            prim = [p for p in pl.get("content", {}).get("plans", []) if isinstance(p, dict) and p.get("ctaVariant") == "primary"]
            if len(prim) != 1:
                rep.add("PLAN_ONE_PRIMARY_CTA", "pricing.plans", "%d primary CTAs (the real page has exactly one)" % len(prim))
    return rep.errors, rep.warnings


def validate_all(spec, ctx=None):
    """JSON Schema (Draft 7) errors + semantic errors. Returns (errors, warnings)."""
    from jsonschema import Draft7Validator
    ctx = ctx or Ctx()
    errs = ["schema %s: %s" % ("/".join(str(p) for p in e.absolute_path), e.message[:160]) for e in Draft7Validator(ctx.pageschema).iter_errors(spec)]
    try:
        se, sw = validate(spec, ctx)
    except Exception as ex:  # a malformed spec must be rejected, never crash the suite silently
        return errs + ["semantic crashed on malformed spec: %r" % ex], []
    return errs + se, sw


def main(argv):
    files = argv or [os.path.join(HERE, "example.pagespec.json")]
    ctx, bad = Ctx(), 0
    for f in files:
        errs, warns = validate_all(json.load(open(f, encoding="utf-8")), ctx)
        for w in warns:
            print("WARN ", w)
        for e in errs:
            print("ERROR", e)
        print("%s: %d error(s), %d warning(s)" % (os.path.relpath(f, REPO) if f.startswith(REPO) else f, len(errs), len(warns)))
        bad += bool(errs)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
