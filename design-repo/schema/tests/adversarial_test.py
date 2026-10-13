#!/usr/bin/env python3
"""Adversarial suite: every mutation must be REJECTED and every control must produce ZERO errors.

Run:  python3 schema/tests/adversarial_test.py
Exit code 0 only if all mutations are rejected and all controls pass.

Controls: the unmutated example, plus one synthesized minimal-valid PageSpec per real route (every real
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
    spec = {"pageSpecVersion": "1.0.0", "template": template, "route": route, "meta": {"title": "Sample title", "description": "Sample description"}, "nodes": nodes}
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
    m = clone(leg); node(m, "legal.body")["content"]["sections"][0]["blocks"] = [{"type": "p", "text": " ".join(["word"] * 83)}]; must_reject("maxWords overflow (legal paragraph 83 > 82)", m, "MAX_WORDS")
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
    print("  (note: repeatable is false on every real template node - no real section repeats adjacently - so only the required flag needs a machinery proof)")

    mp, mt = RESULTS["mut"]; cp, ct = RESULTS["ctl"]
    print("\nMUTATIONS rejected: %d/%d   CONTROLS passed: %d/%d" % (mp, mt, cp, ct))
    if FAILS:
        print("FAILURES:", FAILS)
        return 1
    print("ADVERSARIAL SUITE: ALL MUTATIONS REJECTED, ALL CONTROLS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
