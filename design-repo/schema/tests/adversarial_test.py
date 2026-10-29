#!/usr/bin/env python3
"""Adversarial suite: every mutation must be REJECTED and every control must produce ZERO errors.

Run:  python3 schema/tests/adversarial_test.py
Exit code 0 only if all mutations are rejected and all controls pass.

Controls: the unmutated clone example, the seven mode=generation examples (schema/examples/), plus one synthesized minimal-valid PageSpec per real route (every real
template is covered by iterating templates.json, so a new template is auto-covered), plus both directions of
every graph rule that had a named exception (accepted: the real, correct structure; rejected: the bug).
"""
import copy, glob, json, os, sys
sys.dont_write_bytecode = True  # keep the repo free of __pycache__

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "schema"))
import semantic_validate as sv  # noqa: E402

CTX = sv.Ctx(REPO)
EXAMPLE = json.load(open(os.path.join(REPO, "schema", "example.pagespec.json"), encoding="utf-8"))
GEN = {os.path.basename(f).split(".")[1]: json.load(open(f, encoding="utf-8")) for f in sorted(glob.glob(os.path.join(REPO, "schema", "examples", "generated.*.pagespec.json")))}
BASE_TOKENS = {"surface": "color.surface.page", "text": "color.text.primary", "headingType": "typography.display.section",
               "bodyType": "typography.body.section", "sectionSpacing": "layout.section.hero-padding"}
RESULTS = {"mut": [0, 0], "ctl": [0, 0]}
FAILS = []


def run(spec):
    return sv.validate_all(spec, CTX)


# ----------------------------------------------------------------------------- synthesis
def synth_value(sch, rootdefs=None):
    if "const" in sch:
        return sch["const"]
    if "allOf" in sch:  # asset field
        return {"assetRole": sch["x-allowedRoles"][0], "assetRef": "placeholder:neutral"}
    if sch.get("$ref") == "#/definitions/assetRef":
        return {"assetRole": sch["x-allowedRoles"][0], "assetRef": "placeholder:neutral"}
    if "oneOf" in sch:
        return synth_value(sch["oneOf"][0])
    if "enum" in sch:
        return sch["enum"][0]
    t = sch.get("type")
    if t == "string":
        if "x-sample" in sch:
            return sch["x-sample"]
        n = max(1, min(3, sch.get("x-maxWords", 3)))
        return " ".join(["word"] * n)
    if t == "array":
        return [synth_value(sch["items"]) for _ in range(max(1, sch.get("minItems", 1)))]
    if t == "object":
        return {k: synth_value(sch["properties"][k]) for k in sch.get("required", [])}
    raise ValueError("cannot synthesize %r" % sch)


def synth_node(entry, route):
    c = CTX.sections[entry["section"]]
    content = synth_value(c["content"])
    variant = entry.get("variant")
    for vr in c.get("variantRules", []):
        if vr["variant"] == variant:
            for f in vr.get("required", []):
                content[f] = synth_value(c["content"]["properties"][f])
            content.update(vr.get("pinned", {}))
    pats = [p for p in c["motion"]["allowedPatterns"]]
    for vr in c.get("variantRules", []):
        if vr["variant"] == variant:
            pats = [p for p in pats if p not in vr.get("forbiddenPatterns", [])]
    n = {"section": entry["section"], "content": content, "motion": {"patterns": [pats[0]], "reducedMotionFallback": c["motion"]["reducedMotionFallback"]}}
    if c["variants"]:
        n["variant"] = variant or c["variants"][0]
    return n


def synth_spec(template, route):
    t = CTX.templates[template]
    nodes = [synth_node(e, route) for e in t["nodes"]]
    spec = {"pageSpecVersion": "2.0.0", "mode": "clone", "template": template, "route": route, "theme": "light", "tokens": dict(BASE_TOKENS), "meta": {"title": "Sample title", "description": "Sample description"}, "nodes": nodes}
    # cross-field fixups the generic synthesizer cannot know (each is a graph rule, proven both ways below)
    for n in nodes:
        if n["section"] == "pricing.plans":
            for i, p in enumerate(n["content"]["plans"]):
                p["ctaVariant"] = "primary" if i == 0 else "secondary"
        if n["section"] == "legal.heading":
            n["content"]["activeTab"] = {"/privacy": "privacy", "/terms": "terms"}[route]
            if route == "/terms":
                n["content"].pop("intro", None)
        if n["section"] == "blog.story-list":
            n["content"]["stories"][0]["slug"] = "another-story"
    return spec


# ----------------------------------------------------------------------------- harness
def must_reject(name, spec, expect=None, sem=False):
    """sem=True runs ONLY the semantic validator (proves the rule works without the JSON Schema layer)."""
    errs = sv.validate(spec, CTX)[0] if sem else run(spec)[0]
    RESULTS["mut"][1] += 1
    ok = bool(errs) and (expect is None or any(expect in e for e in errs))
    if ok:
        RESULTS["mut"][0] += 1
        print("  REJECTED  %-62s -> %s" % (name, errs[0][:92]))
    else:
        FAILS.append(name)
        print("  !! NOT REJECTED (or wrong reason) %s: errors=%s expect=%r" % (name, errs[:2], expect))


def must_warn(name, spec, expect):
    errs, warns = run(spec)
    RESULTS["mut"][1] += 1
    if not errs and any(expect in w for w in warns):
        RESULTS["mut"][0] += 1
        print("  WARNED    %-62s -> %s" % (name, [w for w in warns if expect in w][0][:92]))
    else:
        FAILS.append(name)
        print("  !! expected only a WARNING %s: errors=%s warnings=%s" % (name, errs[:2], warns[:2]))


def must_pass(name, spec):
    errs, warns = run(spec)
    RESULTS["ctl"][1] += 1
    if not errs and not warns:
        RESULTS["ctl"][0] += 1
        print("  PASS      %-62s 0 errors, 0 warnings" % name)
    else:
        FAILS.append("control " + name)
        print("  !! CONTROL FAILED %s: %s %s" % (name, errs[:3], warns[:2]))


def clone(x):
    return copy.deepcopy(x)


def node(spec, section, variant=None):
    return next(n for n in spec["nodes"] if n["section"] == section and (variant is None or n.get("variant") == variant))


def gen(name):
    return clone(GEN[name])


def extra_suites():
    print("== CONTROLS: generation examples (one per template family) + clone mode keeps real content ==")
    for name, spec in sorted(GEN.items()):
        must_pass("generation example %-12s (mode=generation, fictional brand)" % name, spec)
    real_home = clone(synth_spec("home", "/"))
    real_home["meta"]["title"] = "Merlin \u2014 Your AI assistant for Mac"
    node(real_home, "hero.marketing")["content"]["cta"]["label"] = "Get Merlin for Mac"
    node(real_home, "hero.landscape")["content"]["image"] = {"assetRole": "illustration.felt-scene", "assetRef": "reuse:asset.quiet-lakeside.webp"}
    node(real_home, "proof.company-logos")["content"]["logos"][0] = {"name": "Notion", "mark": {"assetRole": "logo.third-party-wordmark", "assetRef": "reuse:asset.notion.svg"}}
    must_pass("CONTROL clone mode: real brand, CTA, felt scene and customer logo accepted", real_home)
    must_pass("CONTROL clone mode: real pricing example (real tiers, 'Plans | Merlin')", EXAMPLE)
    m = clone(real_home); m["mode"] = "generation"; must_reject("same real home page in mode=generation is rejected", m, "GENERATION_MODE_")

    print("== MUTATIONS: generation-mode leakage (each must be rejected by its named rule) ==")
    G = lambda: gen("home")
    m = G(); m["meta"]["title"] = "Merlin for teams"; must_reject("brand name in meta.title", m, "GENERATION_MODE_BRAND", sem=True)
    m = G(); node(m, "hero.marketing")["content"]["cta"]["label"] = "Get Merlin for Mac"; must_reject("source CTA 'Get Merlin for Mac'", m, "GENERATION_MODE_BRAND", sem=True)
    m = G(); m["meta"]["title"] = "\uff2d\uff45\uff52\uff4c\uff49\uff4e planner"; must_reject("brand in fullwidth letters (NFKC)", m, "GENERATION_MODE_BRAND", sem=True)
    m = G(); m["meta"]["title"] = "Mer\u200blin planner"; must_reject("brand split by a zero-width space", m, "GENERATION_MODE_BRAND", sem=True)
    m = G(); node(m, "hero.marketing")["content"]["subtitle"] = "Visit www.merlin.computer today"; must_reject("source domain in copy", m, "GENERATION_MODE_URL", sem=True)
    m = G(); node(m, "shell.footer-closing")["content"]["brandWordmark"] = "merlin.computer"; must_reject("source wordmark/domain in footer", m, "GENERATION_MODE_BRAND", sem=True)
    m = G(); node(m, "hero.marketing")["content"]["subtitle"] = "Grab it from download.merlin.computer"; must_reject("Mac download host", m, "GENERATION_MODE_URL", sem=True)
    m = gen("install"); node(m, "install.intro")["content"]["installerHref"] = "/download-stub.txt?arch=arm64"; must_reject("source installer stub path (Mac download link)", m, "GENERATION_MODE_URL", sem=True)
    m = G(); node(m, "hero.marketing")["content"]["subtitle"] = "Images from cdn.sanity.io"; must_reject("source CMS host", m, "GENERATION_MODE_URL", sem=True)
    m = gen("legal"); node(m, "legal.document-footer")["content"]["contactEmail"] = "team@merlin.computer"; must_reject("source contact email", m, "GENERATION_MODE_BRAND", sem=True)
    m = gen("legal"); node(m, "legal.document-footer")["content"]["contactEmail"] = "hello@fernlight.com"; must_reject("email on a non-reserved domain", m, "GENERATION_MODE_URL", sem=True)
    m = G(); node(m, "proof.company-logos")["content"]["logos"][0]["name"] = "Salesforce"; must_reject("real customer name in the logo row", m, "GENERATION_MODE_CUSTOMER", sem=True)
    m = G(); node(m, "proof.company-logos")["content"]["logos"][0]["name"] = "McKinsey \u0026 Company"; must_reject("real customer with ampersand", m, "GENERATION_MODE_CUSTOMER", sem=True)
    m = G(); node(m, "proof.company-logos")["content"]["logos"][0]["mark"] = {"assetRole": "logo.third-party-wordmark", "assetRef": "placeholder:neutral"}; must_reject("third-party logo role (blocked-for-generation)", m, "GENERATION_MODE_CUSTOMER", sem=True)
    m = G(); node(m, "proof.company-logos")["content"]["logos"][0]["mark"] = {"assetRole": "logo.placeholder-customer", "assetRef": "generate:a Notion-style logo"}; must_reject("generate brief naming a real brand", m, "GENERATION_MODE_CUSTOMER", sem=True)
    m = G(); node(m, "proof.company-logos")["content"]["heading"] = "Used by professionals at"; must_reject("source social-proof claim", m, "GENERATION_MODE_CLAIM", sem=True)
    m = gen("pricing"); node(m, "pricing.plans")["content"]["plans"][1].update(price="99", credits="85,000"); must_reject("real plan tier (price + credits)", m, "GENERATION_MODE_CLAIM", sem=True)
    m = gen("blog-post"); node(m, "blog.article-header")["content"]["author"] = "Adeola Adeoti"; must_reject("real blog author name", m, "GENERATION_MODE_PERSON", sem=True)
    m = G(); node(m, "hero.marketing")["content"]["subtitle"] = "Sophie Hayes loves it"; must_reject("source mock persona name (testimonial-style)", m, "GENERATION_MODE_PERSON", sem=True)
    m = gen("blog-post"); node(m, "blog.article-header")["content"]["avatar"] = {"assetRole": "photo.person-portrait", "assetRef": "placeholder:neutral"}; must_reject("real-person portrait role", m, "GENERATION_MODE_PERSON", sem=True)
    m = G(); node(m, "hero.marketing")["content"]["subtitle"] = "Your AI assistant for Mac"; must_reject("source tagline (5-word shingle)", m, "GENERATION_MODE_COPY", sem=True)
    m = G(); node(m, "hero.marketing")["content"]["subtitle"] = "Book flights, order groceries, and fill out forms in your browser"; must_reject("source feature copy", m, "GENERATION_MODE_COPY", sem=True)
    m = G(); node(m, "hero.marketing")["content"]["subtitle"] = "Book flights \u2014 order groceries, and fill out forms in your browser"; must_reject("source copy with an em dash variant", m, "GENERATION_MODE_COPY", sem=True)
    m = G(); node(m, "hero.marketing")["content"]["subtitle"] = "Rewrite a reply, explain selected text, or ask about what\u2019s on your screen"; must_reject("source copy with a curly apostrophe", m, "GENERATION_MODE_COPY", sem=True)
    m = G(); node(m, "hero.landscape")["content"]["image"] = {"assetRole": "illustration.felt-scene", "assetRef": "reuse:asset.quiet-lakeside.webp"}; must_reject("proprietary felt scene (clone-only)", m, "GENERATION_MODE_ASSET", sem=True)
    m = G(); node(m, "hero.landscape")["content"]["image"] = {"assetRole": "illustration.generated", "assetRef": "reuse:asset.quiet-lakeside.webp"}; must_reject("reuse of a source asset file under a safe role", m, "GENERATION_MODE_ASSET", sem=True)
    m = G(); node(m, "hero.marketing")["content"]["subtitle"] = "see quiet-lakeside.webp for the mood"; must_reject("source asset file name in a string", m, "GENERATION_MODE_ASSET", sem=True)
    m = gen("install"); node(m, "install.steps")["content"]["steps"][0]["image"] = {"assetRole": "screenshot.os-install-step", "assetRef": "placeholder:neutral"}; must_reject("macOS install screenshot role", m, "GENERATION_MODE_SCREENSHOT", sem=True)
    m = gen("legal"); node(m, "shell.corner-nav")["content"]["brandIcon"] = {"assetRole": "brand.merlin-app-icon", "assetRef": "reuse:asset.merlin-dock-32.png"}; must_reject("source app icon / brand mark", m, "GENERATION_MODE_BRAND", sem=True)
    m = gen("manifesto"); node(m, "manifesto.ending")["content"]["signature"]["mark"] = {"assetRole": "brand.merlin-mascot-art", "assetRef": "placeholder:neutral"}; must_reject("mascot art role", m, "GENERATION_MODE_BRAND", sem=True)
    m = G(); node(m, "hero.landscape")["content"]["image"] = {"assetRole": "illustration.generated", "assetRef": "user:my-art"}; must_reject("user: ref on a non user-supplied role", m, "ASSET_REF_POLICY", sem=True)
    m = G(); node(m, "hero.landscape")["content"]["image"] = {"assetRole": "media.user-supplied", "assetRef": "generate:fake operator logo"}; must_reject("generating a stand-in for a user-supplied asset", m, "ASSET_REF_POLICY", sem=True)
    m = G(); node(m, "hero.landscape")["content"]["image"] = {"assetRole": "media.user-supplied", "assetRef": "user:operator-hero"}; must_pass("CONTROL generation: operator-supplied asset via user:<id>", m)

    print("== MUTATIONS: tokens (token-policy.json) ==")
    T = lambda: clone(EXAMPLE)
    def tok(slot, val, rule, name, sem=True, base=None):
        m = base or T(); m["tokens"][slot] = val; must_reject(name, m, rule, sem=sem)
    tok("text", "#333333", "TOKEN_RAW_COLOR", "raw hex colour in text")
    tok("surface", "rgb(255, 255, 255)", "TOKEN_RAW_COLOR", "raw rgb() colour in surface")
    tok("accent", "hsl(190 80% 40%)", "TOKEN_RAW_COLOR", "raw hsl() colour in accent")
    tok("surface", "white", "TOKEN_RAW_COLOR", "colour keyword in surface")
    tok("sectionSpacing", "96px", "TOKEN_ARBITRARY_SPACING", "arbitrary spacing 96px")
    tok("sectionSpacing", "160px 0 96px", "TOKEN_ARBITRARY_SPACING", "raw padding shorthand (the real value, untokenised)")
    tok("gap", "1.5rem", "TOKEN_ARBITRARY_SPACING", "arbitrary gap 1.5rem")
    tok("sectionSpacing", "clamp(24px,5vw,80px)", "TOKEN_ARBITRARY_SPACING", "clamp() spacing")
    tok("headingType", "Inter", "TOKEN_UNSUPPORTED_FONT", "unsupported font family Inter")
    tok("bodyType", "Georgia, serif", "TOKEN_UNSUPPORTED_FONT", "raw font stack")
    tok("headingType", "\"Open Runde\"", "TOKEN_UNSUPPORTED_FONT", "real family name written raw")
    tok("surface", "color.surface.neon", "TOKEN_UNKNOWN", "unknown token path")
    tok("bodyType", "typography.body.huge", "TOKEN_UNKNOWN", "unknown typography role")
    tok("text", "color.ink.primary", "TOKEN_NOT_APPROVED", "foundation colour instead of the semantic alias")
    tok("bodyType", "fontFamily.sans", "TOKEN_NOT_APPROVED", "raw type primitive (fontFamily) in a type slot")
    tok("gap", "component.download-button.radius", "TOKEN_NOT_APPROVED", "component token in a PageSpec")
    tok("surface", "typography.display.hero", "TOKEN_SLOT_MISMATCH", "typography token in a colour slot")
    tok("sectionSpacing", "layout.container.content-max", "TOKEN_SLOT_MISMATCH", "layout width in the spacing slot")
    tok("text", "color.text.muted-hero", "TOKEN_SLOT_MISMATCH", "denied role colour as body ink")
    tok("surface", "color.surface.scene-dark", "TOKEN_THEME_COMBINATION", "scene-dark surface as a light-theme page surface")
    tok("text", "color.text.on-dark", "TOKEN_THEME_COMBINATION", "on-dark ink as page text in the light theme")
    m = T(); m["tokens"]["surface"] = "color.surface.footer"; m["tokens"]["text"] = "color.text.muted"; must_reject("text/surface contrast 3.8 < 4.5", m, "TOKEN_THEME_COMBINATION", sem=True)
    m = T(); m["theme"] = "dark"; must_reject("invalid theme 'dark' (schema)", m)
    m = T(); m["theme"] = "dark"; must_reject("invalid theme 'dark' (semantic layer alone)", m, "TOKEN_THEME_COMBINATION", sem=True)
    m = T(); del m["tokens"]["surface"]; must_reject("missing required token slot (schema)", m)
    m = T(); m["tokens"]["fontSize"] = "fontSize.16"; must_reject("invented token slot (closed schema)", m)
    m = gen("home"); m["tokens"]["text"] = "#000"; must_reject("raw colour in a generation example", m, "TOKEN_RAW_COLOR", sem=True)
    print("== CONTROLS: every approved token in every slot ==")
    cat = CTX.catalog["tokens"]; pol = CTX.tpolicy["pageSpecTokenSlots"]; n_ok = n_all = 0
    for slot, sd in pol.items():
        for path, e in cat.items():
            if e["approvedForPageSpec"] and e["category"] in sd["allowCategories"] and any(path.startswith(px) for px in sd["allowPrefixes"]) and path not in sd["deny"]:
                m = T(); m["tokens"][slot] = path; n_all += 1
                errs = run(m)[0]
                if not errs: n_ok += 1
                else: FAILS.append("token control %s=%s" % (slot, path)); print("  !! token control failed", slot, path, errs[:1])
    RESULTS["ctl"][1] += 1
    if n_ok == n_all: RESULTS["ctl"][0] += 1
    print("  PASS      %d/%d (slot, approved token) combinations accepted" % (n_ok, n_all))

    print("== MUTATIONS: pins in code (availability R3, retrieval R8) ==")
    ctx2 = sv.Ctx(REPO); ctx2.roles = copy.deepcopy(ctx2.roles); ctx2.roles["illustration.felt-scene"]["availability"] = "generation-safe"
    _pin("registry flips felt-scene to generation-safe", ctx2, "ASSET_AVAILABILITY_PINNED")
    ctx2 = sv.Ctx(REPO); ctx2.roles = copy.deepcopy(ctx2.roles); ctx2.roles["photo.person-portrait"]["availability"] = "clone-only"
    _pin("registry changes a blocked role to another valid value", ctx2, "ASSET_AVAILABILITY_PINNED")
    ctx2 = sv.Ctx(REPO); ctx2.roles = copy.deepcopy(ctx2.roles); del ctx2.roles["copy.original"]["availability"]
    _pin("registry drops an availability", ctx2, "ASSET_AVAILABILITY_PINNED")
    ctx2 = sv.Ctx(REPO); ctx2.sections = copy.deepcopy(ctx2.sections); ctx2.sections["shell.floating-nav"]["retrievalEligible"] = True
    _pin("contract flips floating nav to retrievable", ctx2, "RETRIEVAL_ELIGIBILITY_PINNED")
    ctx2 = sv.Ctx(REPO); ctx2.sections = copy.deepcopy(ctx2.sections); ctx2.sections["legal.contents"]["retrievalEligible"] = True
    _pin("contract flips the legal TOC to retrievable", ctx2, "RETRIEVAL_ELIGIBILITY_PINNED")
    ctx2 = sv.Ctx(REPO); ctx2.sections = copy.deepcopy(ctx2.sections); ctx2.sections["faq.accordion"]["retrievalEligible"] = False
    _pin("content section marked ineligible", ctx2, "RETRIEVAL_ELIGIBILITY_PINNED")

    print("== R6 decomposition: repeatable legal.section / blog.prose chapters ==")
    lg = gen("legal"); ls = node(lg, "legal.section")
    m = clone(lg); i = m["nodes"].index(node(m, "legal.section")); s2 = clone(ls); s2["content"]["id"] = "second-part"; m["nodes"].insert(i + 1, s2)
    must_pass("CONTROL two legal.section parts with distinct ids", m)
    m2 = clone(m); m2["nodes"][i + 1]["content"]["id"] = ls["content"]["id"]; must_reject("duplicate legal.section id", m2, "LEGAL_SECTION_IDS_UNIQUE", sem=True)
    m = clone(lg); i = m["nodes"].index(node(m, "legal.section")); m["nodes"][i + 1:i + 1] = [dict(clone(ls), content=dict(ls["content"], id="part-%d" % k)) for k in range(14)]
    must_reject("15 legal.section parts (maxRepeat 14)", m, "TEMPLATE_ORDER", sem=True)
    bp = gen("blog-post"); ch = node(bp, "blog.prose")
    m = clone(bp); i = m["nodes"].index(node(m, "blog.prose"))
    c2 = clone(ch); c2["content"]["blocks"] = [{"type": "h2", "text": "A second chapter"}, {"type": "p", "text": "Fernlight notes."}]
    m["nodes"].insert(i + 1, c2); must_pass("CONTROL lead chapter + an h2 chapter", m)
    m2 = clone(m); m2["nodes"][i + 1]["content"]["blocks"] = [{"type": "p", "text": "No heading here."}]; must_reject("second chapter without its h2", m2, "BLOG_PROSE_CHAPTER_HEADING", sem=True)
    m2 = clone(m); m2["nodes"][i]["content"]["blocks"].append({"type": "h2", "text": "Hidden chapter"}); must_reject("h2 in the middle of a chapter", m2, "BLOG_PROSE_CHAPTER_HEADING", sem=True)
    m = clone(bp); m["nodes"][i:i + 1] = [clone(c2) for _ in range(13)]; must_reject("13 chapters (maxRepeat 12)", m, "TEMPLATE_ORDER", sem=True)

    print("== R9 wrapper gate (extraction/wrapper_gate.py self-test) ==")
    sys.path.insert(0, os.path.join(REPO, "extraction"))
    import io, contextlib, wrapper_gate
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = wrapper_gate.self_test()
    ok = [l for l in buf.getvalue().splitlines() if l.startswith("OK  ")]; bad = [l for l in buf.getvalue().splitlines() if l.startswith("FAIL")]
    RESULTS["mut"][1] += len(ok) + len(bad); RESULTS["mut"][0] += len(ok)
    print("  wrapper gate cases: %d OK, %d FAIL (HERO 1900/3100, majority share, whitelist rules, missing measurement, wrong viewport)" % (len(ok), len(bad)))
    if rc or bad: FAILS.append("wrapper gate self-test")


def _pin(name, ctx2, rule):
    errs = sv.validate(EXAMPLE, ctx2)[0]
    RESULTS["mut"][1] += 1
    if any(rule in e for e in errs):
        RESULTS["mut"][0] += 1; print("  REJECTED  %-62s -> %s" % (name, [e for e in errs if rule in e][0][:92]))
    else:
        FAILS.append(name); print("  !! NOT REJECTED %s: %s" % (name, errs[:2]))


def main():
    print("== CONTROLS ==")
    must_pass("unmutated example (pricing)", EXAMPLE)
    controls = {}
    for rpath, r in sorted(CTX.routes.items()):
        s = synth_spec(r["template"], rpath)
        controls[rpath] = s
        must_pass("synthesized control %-12s (template %s)" % (rpath, r["template"]), s)
    # both-direction controls for rules with named exceptions
    home = controls["/"]
    must_pass("home: floating-nav may FOLLOW the footer (named exception)", home)
    s = clone(controls["/manifesto"]); must_pass("manifesto: manifesto.photo x3 with 3 distinct variants", s)
    install = controls["/download"]
    must_pass("install: no footer, no nav (named exceptions)", install)

    print("== MUTATIONS: schema layer ==")
    m = clone(EXAMPLE); node(m, "pricing.plans")["content"]["plans"][0]["tone"] = "purple"; must_reject("wrong enum (plan tone)", m)
    m = clone(EXAMPLE); del node(m, "pricing.plans")["content"]["plans"][0]["price"]; must_reject("missing required content field (price)", m)
    m = clone(EXAMPLE); m["nodes"][0]["section"] = "hero.invented"; must_reject("invented section type", m)
    m = clone(EXAMPLE); del m["nodes"][1]["motion"]["reducedMotionFallback"]; must_reject("missing reducedMotionFallback", m)
    m = clone(EXAMPLE); del m["nodes"][1]["motion"]; must_reject("missing motion object", m)
    m = clone(EXAMPLE); m["nodes"][1]["motion"]["inventedAnimation"] = "spin"; must_reject("invented motion field (closed motion schema)", m)
    m = clone(EXAMPLE); m["nodes"][1]["motion"]["reducedMotionFallback"] = "final-state-static"; must_reject("valid-enum but wrong locked fallback for section", m, "MOTION_FALLBACK_REQUIRED", sem=True)
    m = clone(EXAMPLE); m["nodes"][1]["motion"]["patterns"] = ["scroll-pin-card-deck"]; must_reject("motion pattern not allowed for the section", m, "MOTION_FALLBACK_REQUIRED", sem=True)
    m = clone(EXAMPLE); del m["nodes"][1]["motion"]["reducedMotionFallback"]; must_reject("missing reducedMotionFallback (semantic layer alone)", m, "MOTION_FALLBACK_REQUIRED", sem=True)
    m = clone(EXAMPLE); del m["nodes"][1]["motion"]; must_reject("missing motion object (semantic layer alone)", m, "MOTION_FALLBACK_REQUIRED", sem=True)
    m = clone(EXAMPLE); node(m, "pricing.plans")["content"]["billingToggle"] = {"annual": True}; must_reject("invented field: monthly/annual billing toggle (NO_BILLING_TOGGLE)", m)
    m = clone(EXAMPLE); m["nodes"][0]["content"]["inventedField"] = "x"; must_reject("invented content field", m)
    m = clone(EXAMPLE); m["nodes"][0]["styleOverride"] = {"color": "#fff"}; must_reject("invented node property (no token/style override exists)", m)
    m = clone(EXAMPLE); m["inventedTop"] = 1; must_reject("invented top-level property", m)
    m = clone(EXAMPLE); node(m, "shell.footer-closing")["content"]["beachArt"]["assetRole"] = "photo.invented"; must_reject("invented assetRole", m)
    m = clone(EXAMPLE); node(m, "shell.footer-closing")["content"]["beachArt"]["assetRef"] = "https://cdn.example.com/x.svg"; must_reject("assetRef pointing at an external URL", m)
    m = clone(EXAMPLE); node(m, "shell.footer-closing")["content"]["cta"]["href"] = "https://www.merlin.computer/download"; must_reject("external href (no external requests)", m)
    m = clone(EXAMPLE); node(m, "pricing.faq")["content"]["items"][0]["answer"] = "See http://example.com for details"; must_reject("external URL inside copy (NO_EXTERNAL_REQUESTS)", m, "NO_EXTERNAL_REQUESTS")
    m = clone(EXAMPLE); m["template"] = "pricing-v2"; must_reject("invented template", m)
    m = clone(EXAMPLE); m["route"] = "/pricing/annual"; must_reject("invented route", m)
    m = clone(EXAMPLE); m["pageSpecVersion"] = "one"; must_reject("malformed pageSpecVersion", m)
    m = clone(EXAMPLE); node(m, "pricing.plans")["variant"] = "x"; must_reject("variant on a variant-less section", m)

    print("== MUTATIONS: structural / template cross-reference ==")
    m = clone(EXAMPLE); m["nodes"].insert(1, clone(m["nodes"][0])); must_reject("duplicate one-per-page section (hero.marketing x2)", m, "ONE_HERO_MARKETING", sem=True)
    m = clone(EXAMPLE); m["nodes"] = [n for n in m["nodes"] if n["section"] != "pricing.faq"]; must_reject("removed mandatory section (pricing.faq)", m, "TEMPLATE_ORDER")
    m = clone(EXAMPLE); m["nodes"][2], m["nodes"][3] = m["nodes"][3], m["nodes"][2]; must_reject("reordered sections (included <-> faq)", m, "TEMPLATE_ORDER")
    m = clone(EXAMPLE); m["nodes"].insert(0, m["nodes"].pop()); must_reject("reordered fixed-position section (footer first)", m, "FOOTER_PRESENT_AND_LAST", sem=True)
    m = clone(EXAMPLE); m["template"] = "home"; m["route"] = "/"; must_reject("template/node mismatch (pricing nodes declared as home)", m, "TEMPLATE_ORDER")
    m = clone(EXAMPLE); m["template"] = "blog-post"; must_reject("template/route mismatch (route /pricing under blog-post)", m, "ROUTE_TEMPLATE_BINDING")
    m = clone(EXAMPLE); m["route"] = "/blog"; must_reject("route bound to a different template (/blog under pricing)", m, "ROUTE_TEMPLATE_BINDING")
    m = clone(EXAMPLE); m["nodes"].append(clone(home["nodes"][-1])); must_reject("floating nav on pricing (home-only section)", m, "FLOATING_NAV_HOME_ONLY", sem=True)
    m = clone(EXAMPLE); node(m, "hero.marketing")["content"]["cta"] = {"label": "Get Merlin for Mac", "href": "/download?start=1", "variant": "primary"}; must_reject("pricing hero WITH a download button (variant rule)", m, "VARIANT_FIELD_RULES", sem=True)
    m = clone(EXAMPLE); node(m, "hero.marketing")["motion"]["patterns"].append("hero-title-chroma-sweep"); must_reject("pricing hero WITH chroma sweep (variant rule)", m, "VARIANT_FIELD_RULES", sem=True)
    m = clone(EXAMPLE); node(m, "hero.marketing")["variant"] = "home"; must_reject("home-variant hero on pricing template (needs cta; template pins variant)", m)
    m = clone(home); del node(m, "hero.marketing")["content"]["cta"]; must_reject("home hero WITHOUT its download button", m, "VARIANT_FIELD_RULES", sem=True)
    m = clone(home); m["nodes"].insert(len(m["nodes"]) - 1, clone(node(m, "shell.footer-closing"))); must_reject("home: duplicated footer", m, "ONE_PER_PAGE", sem=True)
    m = clone(home); m["nodes"] = m["nodes"][:-2] + [m["nodes"][-1], m["nodes"][-2]]; must_reject("home: floating-nav BEFORE footer (template order: nav is last)", m, "TEMPLATE_ORDER", sem=True)
    m = clone(home); m["nodes"].insert(5, clone(node(m, "story.browser-tasks"))); must_reject("two pinned scroll stages (browser-tasks x2)", m, "MAX_ONE_PINNED_STAGE", sem=True)
    m = clone(home); m["nodes"].insert(1, clone(node(m, "hero.marketing"))); must_reject("two heroes on home (ONE_HERO_MARKETING)", m, "ONE_HERO_MARKETING", sem=True)
    man = controls["/manifesto"]
    m = clone(man); m["nodes"][4]["variant"] = "after-opening"; must_reject("manifesto: photo variant duplicated (after-opening twice)", m, "ONE_PER_PAGE", sem=True)
    m = clone(man); m["nodes"][2], m["nodes"][4] = m["nodes"][4], m["nodes"][2]; must_reject("manifesto: photo variants swapped out of order", m, "TEMPLATE_ORDER")
    m = clone(man); node(m, "shell.corner-nav")["content"]["activeLink"] = "none"; must_reject("manifesto: corner-nav activeLink not pinned to 'manifesto'", m, "VARIANT_FIELD_RULES", sem=True)
    m = clone(man); m["nodes"].insert(1, m["nodes"].pop(0)); must_reject("manifesto: corner-nav moved off first position", m, "CORNER_NAV_FIRST", sem=True)
    m = clone(man); m["nodes"].append(clone(man["nodes"][0])); must_reject("manifesto: nav duplicated after footer", m)
    m = clone(man); m["nodes"] = [n for n in m["nodes"] if n["section"] != "shell.footer-closing"]; must_reject("manifesto: footer removed", m)
    m = clone(install); m["nodes"].append(clone(home["nodes"][-2])); must_reject("install: footer appended (install has no footer)", m, "FOOTER_PRESENT_AND_LAST", sem=True)
    m = clone(install); m["nodes"].insert(0, clone(man["nodes"][0])); must_reject("install: standalone corner-nav added (own brand-only header)", m, "CORNER_NAV_FIRST", sem=True)
    m = clone(controls["/blog"]); m["nodes"].insert(1, clone(home["nodes"][0])); must_reject("blog-index: hero.marketing added (hero-less template)", m, "ONE_HERO_MARKETING", sem=True)
    leg = controls["/privacy"]
    m = clone(leg); node(m, "legal.heading")["content"]["activeTab"] = "terms"; must_reject("legal: activeTab does not match route (/privacy says terms)", m, "LEGAL_ACTIVE_TAB_MATCHES_ROUTE")
    m = clone(controls["/terms"]); node(m, "legal.heading")["content"]["intro"] = "A short intro"; must_warn("legal: /terms with an intro paragraph (warn, not error)", m, "LEGAL_INTRO_ONLY_ON_PRIVACY")
    m = clone(controls["/blog"]); node(m, "blog.story-list")["content"]["stories"][0]["slug"] = node(m, "blog.featured")["content"]["slug"]; must_reject("blog-index: featured post duplicated in story list", m, "BLOG_FEATURED_NOT_IN_STORY_LIST")
    m = clone(EXAMPLE); [p.__setitem__("ctaVariant", "secondary") for p in node(m, "pricing.plans")["content"]["plans"]]; must_warn("pricing: no primary CTA plan (warn)", m, "PLAN_ONE_PRIMARY_CTA")
    m = clone(EXAMPLE); [p.__setitem__("ctaVariant", "primary") for p in node(m, "pricing.plans")["content"]["plans"]]; must_warn("pricing: three primary CTA plans (warn)", m, "PLAN_ONE_PRIMARY_CTA")
    m = clone(EXAMPLE); node(m, "pricing.plans")["content"]["plans"].append(clone(node(m, "pricing.plans")["content"]["plans"][0])); must_reject("pricing: a 4th plan card (exactly 3 exist)", m)
    m = clone(install); node(m, "install.intro")["content"]["installerSource"] = "live-host"; must_reject("install: installer source other than the local stub", m)
    m = clone(install); node(m, "install.intro")["content"]["installerHref"] = "/download-stub.txt?arch=ppc"; must_reject("install: installer href outside the stub pattern", m)
    m = clone(home); node(m, "faq.accordion")["content"]["askForm"]["apiMode"] = "live-api"; must_reject("home faq: ask form not a local mock", m)

    print("== MUTATIONS: runtime (maxWords) ==")
    m = clone(EXAMPLE); node(m, "hero.marketing")["content"]["subtitle"] = " ".join(["word"] * 40); must_reject("maxWords overflow (hero subtitle 40 > 22)", m, "MAX_WORDS")
    m = clone(EXAMPLE); node(m, "pricing.faq")["content"]["items"][0]["answer"] = " ".join(["word"] * 46); must_reject("maxWords overflow (pricing faq answer 46 > 45)", m, "MAX_WORDS")
    m = clone(EXAMPLE); m["meta"]["title"] = " ".join(["word"] * 21); must_reject("maxWords overflow (meta.title 21 > 20)", m, "MAX_WORDS")
    post = controls["/blog/:slug"]
    m = clone(post); node(m, "blog.prose")["content"]["blocks"] = [{"type": "p", "text": " ".join(["word"] * 265)}]; must_reject("maxWords overflow (blog paragraph 265 > 264)", m, "MAX_WORDS")
    m = clone(post); node(m, "blog.prose")["content"]["blocks"] = [{"type": "ul", "items": [" ".join(["word"] * 900), " ".join(["word"] * 492)]}]; must_reject("maxWordsTotal overflow (blog list 1392 > 1391)", m, "MAX_WORDS")
    m = clone(post); node(m, "blog.prose")["content"]["blocks"] = [{"type": "img", "src": "x"}]; must_reject("blog prose: invented block type (img)", m)
    m = clone(post); node(m, "blog.prose")["content"]["blocks"] = [{"type": "p", "text": "ok", "extra": 1}]; must_reject("blog prose: invented block property", m)
    m = clone(leg); node(m, "legal.section")["content"]["blocks"] = [{"type": "p", "text": " ".join(["word"] * 83)}]; must_reject("maxWords overflow (legal paragraph 83 > 82)", m, "MAX_WORDS")
    m = clone(man); node(m, "manifesto.opening")["content"]["openingParagraph"] = " ".join(["word"] * 29); must_reject("maxWords overflow (manifesto opening 29 > 28)", m, "MAX_WORDS")

    print("== MUTATIONS: asset roles (pinned-value / policy) ==")
    m = clone(home); node(m, "proof.company-logos")["content"]["logos"][0]["mark"] = {"assetRole": "logo.third-party-wordmark", "assetRef": "generate:a Notion-style logo"}; must_reject("GENERATE a real third-party logo (must-not-fabricate)", m, "ASSET_REF_POLICY")
    m = clone(home); node(m, "proof.company-logos")["content"]["logos"][0]["mark"] = {"assetRole": "logo.third-party-wordmark", "assetRef": "reuse:asset.gmail.png"}; must_reject("reuse an asset registered under another role", m, "ASSET_REF_POLICY")
    m = clone(home); node(m, "proof.company-logos")["content"]["logos"][0]["mark"] = {"assetRole": "icon.generic-ui", "assetRef": "placeholder:neutral"}; must_reject("role not allowed for the field (generic icon as a company logo)", m, "ASSET_REF_POLICY")
    m = clone(home); node(m, "hero.landscape")["content"]["image"] = {"assetRole": "illustration.felt-scene", "assetRef": "generate:felt lakeside"}; must_reject("GENERATE new felt-scene art (must-reuse-exact)", m, "ASSET_REF_POLICY")
    m = clone(home); node(m, "hero.landscape")["content"]["image"] = {"assetRole": "illustration.felt-scene", "assetRef": "reuse:asset.nope.webp"}; must_reject("reuse of an unregistered asset id", m, "ASSET_REF_POLICY")
    m = clone(post); node(m, "blog.article-header")["content"]["avatar"] = {"assetRole": "photo.person-portrait", "assetRef": "generate:smiling woman portrait"}; must_reject("GENERATE a real person's portrait (must-not-fabricate)", m, "ASSET_REF_POLICY")
    m = clone(install); node(m, "install.steps")["content"]["steps"][0]["image"] = {"assetRole": "screenshot.os-install-step", "assetRef": "generate:macOS dock screenshot"}; must_reject("GENERATE a macOS screenshot (must-not-fabricate)", m, "ASSET_REF_POLICY")
    m = clone(home); node(m, "proof.company-logos")["content"]["logos"][0]["mark"] = {"assetRole": "logo.third-party-wordmark", "assetRef": "placeholder:neutral"}; must_pass("CONTROL: placeholder:neutral for a third-party logo is accepted", m)
    m = clone(home); node(m, "story.context-routines")["content"]["appTiles"][0]["icon"] = {"assetRole": "icon.third-party-app", "assetRef": "reuse:asset.gmail.png"}; must_pass("CONTROL: reuse of a registered exact app icon is accepted", m)
    m = clone(EXAMPLE); node(m, "shell.footer-closing")["content"]["beachArt"] = {"assetRole": "art.footer-ascii", "assetRef": "generate:ascii beach"}; must_reject("GENERATE footer ascii art (must-reuse-exact)", m, "ASSET_REF_POLICY")

    print("== SWEEPS (every template / every section) ==")
    n_sweep = 0
    for rpath, spec in sorted(controls.items()):
        for i in range(len(spec["nodes"])):
            m = clone(spec); removed = m["nodes"].pop(i)
            n_sweep += 1
            must_reject_quiet = run(m)[0]
            RESULTS["mut"][1] += 1
            if must_reject_quiet: RESULTS["mut"][0] += 1
            else: FAILS.append("sweep remove %s %s" % (rpath, removed["section"])); print("  !! removal not rejected", rpath, removed["section"])
            m = clone(spec); m["nodes"].insert(i + 1, clone(spec["nodes"][i]))
            RESULTS["mut"][1] += 1
            if run(m)[0]: RESULTS["mut"][0] += 1
            else: FAILS.append("sweep dup %s %s" % (rpath, removed["section"])); print("  !! duplicate not rejected", rpath, removed["section"])
        if len(spec["nodes"]) > 1:
            m = clone(spec); m["nodes"].reverse()
            RESULTS["mut"][1] += 1
            if run(m)[0]: RESULTS["mut"][0] += 1
            else: FAILS.append("sweep reverse " + rpath); print("  !! reversed order not rejected", rpath)
    print("  template sweeps: remove each node / duplicate each node / reverse order, over %d routes -> done" % len(controls))
    base = {}
    for rpath, spec in controls.items():
        for n in spec["nodes"]:
            base.setdefault((n["section"], n.get("variant")), (rpath, n))
    for (sec, var), (rpath, n) in sorted(base.items(), key=lambda kv: (kv[0][0], str(kv[0][1]))):
        spec_ = controls[rpath]
        c = CTX.sections[sec]
        checks = []
        for f in c["content"]["required"]:
            m = clone(spec_); k = next(x for x in m["nodes"] if x["section"] == sec and x.get("variant") == var); del k["content"][f]; checks.append(("drop required content.%s" % f, m))
        m = clone(spec_); k = next(x for x in m["nodes"] if x["section"] == sec and x.get("variant") == var); k["content"]["__invented__"] = 1; checks.append(("invented content field", m))
        m = clone(spec_); k = next(x for x in m["nodes"] if x["section"] == sec and x.get("variant") == var); k["motion"]["__invented__"] = 1; checks.append(("invented motion field", m))
        m = clone(spec_); k = next(x for x in m["nodes"] if x["section"] == sec and x.get("variant") == var); del k["motion"]["reducedMotionFallback"]; checks.append(("missing reducedMotionFallback", m))
        m = clone(spec_); k = next(x for x in m["nodes"] if x["section"] == sec and x.get("variant") == var); k["motion"]["reducedMotionFallback"] = "bogus"; checks.append(("bogus reducedMotionFallback", m))
        if c["variants"]:
            m = clone(spec_); k = next(x for x in m["nodes"] if x["section"] == sec and x.get("variant") == var); k["variant"] = "bogus"; checks.append(("bogus variant", m))
        for label, m in checks:
            RESULTS["mut"][1] += 1
            if run(m)[0]: RESULTS["mut"][0] += 1
            else: FAILS.append("%s/%s %s" % (sec, var, label)); print("  !! NOT REJECTED %s/%s %s" % (sec, var, label))
        n_sweep += len(checks)
    print("  per-section sweeps over %d (section, variant) pairs: drop each required field, invented content/motion field, missing/bogus fallback, bogus variant -> done" % len(base))

    print("== VALIDATOR MACHINERY (flags no real template uses: required:false) ==")
    ctx2 = sv.Ctx(REPO)
    ctx2.templates = copy.deepcopy(ctx2.templates)
    for n in ctx2.templates["pricing"]["nodes"]:
        if n["section"] == "pricing.included":
            n["required"] = False
    m = clone(EXAMPLE); m["nodes"] = [n for n in m["nodes"] if n["section"] != "pricing.included"]
    errs = sv.validate_all(m, ctx2)[0]
    RESULTS["ctl"][1] += 1
    if not errs: RESULTS["ctl"][0] += 1; print("  PASS      optional node (required:false) may be omitted                  0 errors")
    else: FAILS.append("required:false machinery"); print("  !! CONTROL FAILED optional node omitted:", errs[:2])
    m = clone(EXAMPLE); m["nodes"].insert(2, clone(m["nodes"][2])); errs = sv.validate_all(m, ctx2)[0]
    RESULTS["mut"][1] += 1
    if errs: RESULTS["mut"][0] += 1; print("  REJECTED  duplicate of an optional non-repeatable node                 -> %s" % errs[0][:80])
    else: FAILS.append("dup optional"); print("  !! duplicate optional node accepted")
    print("  (repeatable:true nodes - legal.section, blog.prose chapters - are proven in the R6 decomposition block)")
    extra_suites()

    mp, mt = RESULTS["mut"]; cp, ct = RESULTS["ctl"]
    print("\nMUTATIONS rejected: %d/%d   CONTROLS passed: %d/%d" % (mp, mt, cp, ct))
    if FAILS:
        print("FAILURES:", FAILS)
        return 1
    print("ADVERSARIAL SUITE: ALL MUTATIONS REJECTED, ALL CONTROLS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
