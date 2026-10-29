#!/usr/bin/env python3
"""Semantic validator for Merlin design-repo PageSpecs.

Enforces what JSON Schema (schema/pagespec.schema.json) cannot express, by CROSS-REFERENCING the
declared template against that template's real node list (templates/templates.json) - never
nodes[] in isolation - plus the rhythm rules in compatibility/graph.json (severity error|warn),
per-(section, variant) rules from each section contract, per-field maxWords, asset-role policy and the
no-external-requests constraint.

2.0.0 adds: the PageSpec `mode` (clone | generation) and its consequences (GENERATION_MODE_* leakage rules over
schema/source-identity.json, which extraction/build_source_identity.py derives from the real source; strings are
normalised by schema/textnorm.py first), asset availability (PINNED_AVAILABILITY, pinned here AND in
extraction/verify_all.py), the retrieval pin (RETRIEVAL_INELIGIBLE), page-level token slots checked against
tokens/llm/token-catalog.json + token-policy.json (TOKEN_* rules), and the repeatable legal.section / blog.prose
chapter rules. Leakage detection is string-based (no paraphrase / image-text detection).

Usage:  python3 schema/semantic_validate.py [spec.json ...]      (default: schema/example.pagespec.json + schema/examples/*)
Exit code 1 if any ERROR is reported (warnings are printed but non-fatal).

The repo root is derived from __file__ (no absolute paths). Exceptions listed in the graph (hero-less
templates, footer-less templates, ...) are READ FROM THE GRAPH, so the rule prose and this code cannot
silently diverge; extraction/verify_all.py additionally checks that IMPLEMENTED_RULES matches graph.json.
"""
import glob, json, os, re, sys
sys.dont_write_bytecode = True  # keep the repo free of __pycache__

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import textnorm as tn  # noqa: E402  (shared with extraction/build_source_identity.py)

# R3: asset-role availability PINNED IN CODE (independent of assets/asset-roles.json; extraction/verify_all.py
# carries the same table). Editing the registry alone cannot loosen a role: validate() reports any difference.
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
# R8: runtime/utility UI that is NOT retrievable content, pinned in code (verify_all.py carries the same set).
RETRIEVAL_INELIGIBLE = {"shell.floating-nav", "legal.contents"}
# Which GENERATION_MODE_* rule a non-generation-safe asset role trips.
ROLE_LEAK_RULE = {
    "brand.merlin-app-icon": "GENERATION_MODE_BRAND", "brand.merlin-mascot-art": "GENERATION_MODE_BRAND",
    "logo.third-party-wordmark": "GENERATION_MODE_CUSTOMER", "icon.third-party-app": "GENERATION_MODE_CUSTOMER",
    "photo.person-portrait": "GENERATION_MODE_PERSON",
    "screenshot.os-install-step": "GENERATION_MODE_SCREENSHOT", "screenshot.product-output": "GENERATION_MODE_SCREENSHOT",
}
TERM_RULE = {"BRAND": "GENERATION_MODE_BRAND", "CUSTOMER": "GENERATION_MODE_CUSTOMER", "PERSON": "GENERATION_MODE_PERSON",
             "URL": "GENERATION_MODE_URL", "CLAIM": "GENERATION_MODE_CLAIM", "ASSET": "GENERATION_MODE_ASSET"}
# keys whose values are structural identifiers, not copy (never scanned for leakage)
STRUCTURAL_KEYS = {"pageSpecVersion", "mode", "template", "route", "theme", "section", "variant", "assetRole", "patterns",
                   "reducedMotionFallback", "tone", "ctaVariant", "type", "icon", "activeTab", "activeLink", "id", "slug",
                   "app", "scene", "kind", "apiMode", "installerSource"}
RESERVED_TLDS = (".example", ".invalid")

# Rule ids implemented here (verify_all.py compares this set with compatibility/graph.json).
IMPLEMENTED_RULES = {
    "ROUTE_TEMPLATE_BINDING", "TEMPLATE_ORDER", "ONE_HERO_MARKETING", "FOOTER_PRESENT_AND_LAST",
    "FLOATING_NAV_HOME_ONLY", "CORNER_NAV_FIRST", "NO_ADJACENT_SAME_SECTION_VARIANT", "ONE_PER_PAGE",
    "MAX_ONE_PINNED_STAGE", "MOTION_FALLBACK_REQUIRED", "VARIANT_FIELD_RULES", "ASSET_REF_POLICY",
    "NO_EXTERNAL_REQUESTS", "MAX_WORDS", "LEGAL_ACTIVE_TAB_MATCHES_ROUTE", "LEGAL_INTRO_ONLY_ON_PRIVACY",
    "BLOG_FEATURED_NOT_IN_STORY_LIST", "PLAN_ONE_PRIMARY_CTA", "LEGAL_SECTION_IDS_UNIQUE", "BLOG_PROSE_CHAPTER_HEADING",
    "ASSET_AVAILABILITY_PINNED", "RETRIEVAL_ELIGIBILITY_PINNED",
    "GENERATION_MODE_BRAND", "GENERATION_MODE_CUSTOMER", "GENERATION_MODE_PERSON", "GENERATION_MODE_URL",
    "GENERATION_MODE_CLAIM", "GENERATION_MODE_COPY", "GENERATION_MODE_ASSET", "GENERATION_MODE_SCREENSHOT",
    "TOKEN_UNKNOWN", "TOKEN_RAW_COLOR", "TOKEN_ARBITRARY_SPACING", "TOKEN_UNSUPPORTED_FONT", "TOKEN_SLOT_MISMATCH",
    "TOKEN_NOT_APPROVED", "TOKEN_THEME_COMBINATION",
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
        ar = _load(root, "assets/asset-roles.json")
        self.roles = {r["id"]: r for r in ar["roles"]}
        self.assets = {a["id"]: a for a in ar["assets"]}
        self.pinned = ar["pinnedPolicies"]
        self.pageschema = _load(root, "schema/pagespec.schema.json")
        self.identity = _load(root, "schema/source-identity.json")
        self.id_terms = [(x["category"], x["term"], x["tokens"]) for x in self.identity["terms"]] + \
                        [("ASSET", x["term"], x["tokens"]) for x in self.identity["assetFiles"]]
        self.id_shingles = set(self.identity["copy"]["hashes"])
        self.catalog = _load(root, "tokens/llm/token-catalog.json")
        self.tpolicy = _load(root, "tokens/llm/token-policy.json")


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


def asset_checker(rep, ctx, node_path, mode="clone"):
    def check(a, allowed, path):
        role, ref = a.get("assetRole"), a.get("assetRef", "")
        p = node_path + path
        if role not in ctx.roles:
            rep.add("ASSET_REF_POLICY", p, "assetRole %r is not in the closed role registry" % role)
            return
        if allowed and role not in allowed:
            rep.add("ASSET_REF_POLICY", p, "role %s not allowed for this field (allowed: %s)" % (role, ", ".join(allowed)))
        policy = ctx.roles[role]["generationPolicy"]
        if ref.startswith("user:") and role != "media.user-supplied":
            rep.add("ASSET_REF_POLICY", p, "user: refs are only for media.user-supplied (got %s)" % role)
        elif ref.startswith("user:"):
            pass
        elif role == "media.user-supplied" and not ref == "placeholder:neutral":
            rep.add("ASSET_REF_POLICY", p, "media.user-supplied takes user:<id> or placeholder:neutral, never %r" % ref[:30])
        elif ref.startswith("generate:") and policy != "may-generate-new":
            rep.add("ASSET_REF_POLICY", p, "%s is %s: generate: refs are forbidden (use reuse: or placeholder:neutral)" % (role, policy))
        elif ref.startswith("reuse:"):
            asset = ctx.assets.get(ref[6:])
            if asset is None:
                rep.add("ASSET_REF_POLICY", p, "unknown asset id %s" % ref[6:])
            elif asset["role"] != role:
                rep.add("ASSET_REF_POLICY", p, "asset %s is registered as role %s, not %s" % (ref[6:], asset["role"], role))
        elif not (ref.startswith("generate:") or ref.startswith("user:") or ref == "placeholder:neutral"):
            rep.add("ASSET_REF_POLICY", p, "assetRef %r is not reuse:/generate:/user:/placeholder:neutral" % ref)
        if mode == "generation":
            av = PINNED_AVAILABILITY.get(role)
            if av != "generation-safe":
                rep.add(ROLE_LEAK_RULE.get(role, "GENERATION_MODE_ASSET"), p, "assetRole %s is %s: not allowed in mode=generation (use %s)" % (role, av, ", ".join(ctx.roles[role].get("generationSafeSubstitutes", [])) or "a generation-safe role"))
            elif ref.startswith("reuse:"):
                rep.add("GENERATION_MODE_ASSET", p, "reuse:%s is a registered SOURCE asset file: not allowed in mode=generation" % ref[6:])
    return check


def _lum(hexv):
    h = hexv.lstrip("#")[:6]
    c = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a, b):
    la, lb = _lum(a), _lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def classify_token(ctx, slot, value):
    """Return (rule, message) or None for one PageSpec token slot value."""
    pol, cat = ctx.tpolicy, ctx.catalog["tokens"]
    sd = pol["pageSpecTokenSlots"].get(slot)
    v = str(value).strip()
    if not re.match(pol["rawValueRestrictions"]["tokenPathPattern"], v) or v not in cat:
        for rule in ("TOKEN_RAW_COLOR", "TOKEN_ARBITRARY_SPACING", "TOKEN_UNSUPPORTED_FONT"):
            if any(re.search(rx, v) for rx in pol["rawValueRestrictions"]["forbiddenPatterns"][rule]):
                return rule, "%s: raw value %r; name an approved token (e.g. %s)" % (slot, v, sd["allowPrefixes"][0] + "..." if sd else "a catalog path")
        return "TOKEN_UNKNOWN", "%s: %r is not a token in tokens/llm/token-catalog.json" % (slot, v)
    e = cat[v]
    if not e["approvedForPageSpec"]:
        why = pol["notApproved"].get(v) or pol["catalogOnlyCategories"].get(e["category"], "")
        return "TOKEN_NOT_APPROVED", "%s: %r (%s) is not approved for PageSpecs: %s" % (slot, v, e["category"], why[:90])
    if sd is None:
        return "TOKEN_SLOT_MISMATCH", "unknown token slot %r" % slot
    if e["category"] not in sd["allowCategories"] or not any(v.startswith(px) for px in sd["allowPrefixes"]) or v in sd["deny"]:
        if e.get("scheme") == "scene-dark":
            return "TOKEN_THEME_COMBINATION", "%s: %r belongs to the section-local scene-dark scheme (scene.privacy-trust only), not a page token of theme light" % (slot, v)
        return "TOKEN_SLOT_MISMATCH", "%s: %r (%s) is not accepted by this slot (allowed: %s)" % (slot, v, e["category"], ", ".join(sd["allowPrefixes"]))
    return None


def check_tokens(rep, ctx, spec):
    toks = spec.get("tokens")
    if not isinstance(toks, dict):
        return
    theme = spec.get("theme")
    tr = ctx.tpolicy["themeRestrictions"]
    if theme not in ctx.catalog["themes"] or theme not in tr["themes"]:
        rep.add("TOKEN_THEME_COMBINATION", "theme", "theme %r is not a theme of the token catalog %s" % (theme, sorted(ctx.catalog["themes"])))
        return
    ok = {}
    for slot, v in toks.items():
        res = classify_token(ctx, slot, v)
        if res:
            rep.add(res[0], "tokens." + slot, res[1])
        else:
            ok[slot] = v
    res_map = ctx.catalog["themes"][theme]["resolves"]
    for slot, v in ok.items():
        if ctx.catalog["tokens"][v]["category"] == "semanticColor" and v not in res_map:
            rep.add("TOKEN_THEME_COMBINATION", "tokens." + slot, "%r is not resolved by theme %r" % (v, theme))
    if "text" in ok and "surface" in ok and ok["text"] in res_map and ok["surface"] in res_map:
        r = contrast(res_map[ok["text"]], res_map[ok["surface"]])
        if r < tr["minTextContrast"]:
            rep.add("TOKEN_THEME_COMBINATION", "tokens.text", "text %s on surface %s has contrast %.2f < %s in theme %r" % (ok["text"], ok["surface"], r, tr["minTextContrast"], theme))


def leak_strings(node, path="$", key=None):
    """Yield (path, string) for every copy-bearing string (structural identifiers skipped)."""
    if isinstance(node, str):
        if key not in STRUCTURAL_KEYS:
            yield path, node
    elif isinstance(node, dict):
        for k, v in node.items():
            if k in ("tokens", "motion"):
                continue
            yield from leak_strings(v, "%s.%s" % (path, k), k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from leak_strings(v, "%s[%d]" % (path, i), key)


EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})")
HOST = re.compile(r"(?:^|[\s/@(])((?:[a-z0-9-]+\.)+(?:com|net|org|io|computer|ai|app|co|dev|me|so|xyz|example|invalid))\b", re.I)


def check_generation(rep, ctx, spec):
    seen = set()
    for p, s in leak_strings(spec):
        toks = tn.tokens(s)
        for cat, term, tt in ctx.id_terms:
            if tn.contains_terms(toks, tt):
                key = (p, cat, term)
                if key not in seen:
                    seen.add(key)
                    rep.add(TERM_RULE[cat], p, "source %s %r in %r" % (cat.lower(), term, s[:50]))
        for dom in EMAIL.findall(s) + HOST.findall(s):
            if not dom.lower().endswith(RESERVED_TLDS):
                rep.add("GENERATION_MODE_URL", p, "host/email domain %r is not a reserved .example/.invalid placeholder" % dom)
        hits = tn.shingle_hashes(s) & ctx.id_shingles
        if hits:
            rep.add("GENERATION_MODE_COPY", p, "%d 5-word shingle(s) of source copy in %r" % (len(hits), s[:50]))
    tiers = {(t["price"], t["credits"]) for t in ctx.identity["planTiers"]}
    for a, n in enumerate(spec.get("nodes", [])):
        if n.get("section") == "pricing.plans":
            for i, pl in enumerate((n.get("content") or {}).get("plans", [])):
                if isinstance(pl, dict) and (pl.get("price"), pl.get("credits")) in tiers:
                    rep.add("GENERATION_MODE_CLAIM", "nodes[%d].content.plans[%d]" % (a, i), "price %s / credits %s is a real source plan tier" % (pl.get("price"), pl.get("credits")))


def match_template(rep, spec, tmpl):
    """TEMPLATE_ORDER: consume spec nodes against the template's real node list."""
    nodes, i = spec.get("nodes", []), 0
    used = set()
    for e in tmpl["nodes"]:
        taken = 0
        while i < len(nodes) and nodes[i].get("section") == e["section"] and (not e.get("variant") or nodes[i].get("variant") == e["variant"]):
            if taken >= 1 and not e["repeatable"]:
                break
            if taken >= e.get("maxRepeat", 10 ** 6):
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
            rep.add("ASSET_REF_POLICY", "assets/asset-roles.json", "role %s has policy %s but is pinned to %s" % (rid, ctx.roles[rid]["generationPolicy"], pol))

    # ASSET_AVAILABILITY_PINNED: the registry may not drift from the in-code pin (either direction)
    reg = {rid: r.get("availability") for rid, r in ctx.roles.items()}
    if reg != PINNED_AVAILABILITY:
        diff = sorted(k for k in set(reg) | set(PINNED_AVAILABILITY) if reg.get(k) != PINNED_AVAILABILITY.get(k))
        rep.add("ASSET_AVAILABILITY_PINNED", "assets/asset-roles.json", "availability differs from PINNED_AVAILABILITY for %s" % diff)
    # RETRIEVAL_ELIGIBILITY_PINNED: contracts agree with the in-code pin
    for sid, c in ctx.sections.items():
        want = sid not in RETRIEVAL_INELIGIBLE
        if c.get("retrievalEligible") is not want:
            rep.add("RETRIEVAL_ELIGIBILITY_PINNED", "sections/%s.json" % sid, "retrievalEligible %r but the pin says %r" % (c.get("retrievalEligible"), want))
    # TOKEN_* (page-level token slots + theme)
    check_tokens(rep, ctx, spec)
    # GENERATION_MODE_* (string leakage; asset-role leakage is checked per asset field below)
    if spec.get("mode") == "generation":
        check_generation(rep, ctx, spec)

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

    # NO_ADJACENT_SAME_SECTION_VARIANT (named exception: repeatable template nodes, read from the graph)
    rep_ok = set(ctx.graph["NO_ADJACENT_SAME_SECTION_VARIANT"]["exceptions"]["repeatableTemplateNodes"])
    for a in range(1, len(keys)):
        if keys[a] == keys[a - 1] and keys[a][0] not in rep_ok:
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
        walk(rep, content, c["content"], ".content", np_, asset_checker(rep, ctx, np_, spec.get("mode")))

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

    # LEGAL_SECTION_IDS_UNIQUE
    lids = [n.get("content", {}).get("id") for n in nodes if n.get("section") == "legal.section" and isinstance(n.get("content"), dict)]
    dup = sorted({x for x in lids if lids.count(x) > 1 and x is not None})
    if dup:
        rep.add("LEGAL_SECTION_IDS_UNIQUE", "legal.section", "duplicate legal.section id(s) %s" % dup)

    # BLOG_PROSE_CHAPTER_HEADING
    ch = [(a, n) for a, n in enumerate(nodes) if n.get("section") == "blog.prose"]
    for k, (a, n) in enumerate(ch):
        blocks = [b for b in (n.get("content", {}) or {}).get("blocks", []) if isinstance(b, dict)]
        if any(b.get("type") == "h2" for b in blocks[1:]):
            rep.add("BLOG_PROSE_CHAPTER_HEADING", "nodes[%d]" % a, "an h2 may only open a chapter (split the chapter into its own blog.prose node)")
        if k > 0 and (not blocks or blocks[0].get("type") != "h2"):
            rep.add("BLOG_PROSE_CHAPTER_HEADING", "nodes[%d]" % a, "every chapter after the lead must start with its h2")

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
    files = argv or [os.path.join(HERE, "example.pagespec.json")] + sorted(glob.glob(os.path.join(HERE, "examples", "*.pagespec.json")))
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
