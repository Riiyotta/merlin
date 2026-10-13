#!/usr/bin/env python3
"""Proves extraction/verify_all.py actually CATCHES drift (MASTER-GUIDE 3.2 / 3.4 / 3.16 / 3.23).

For each injected defect: copy design-repo/ to a scratch dir, inject the defect, run the copy's own
verify_all.py (against the real source tree when present) and require a FAIL naming the defect. Finally
confirm the untouched repo still passes. Run:  python3 extraction/prove_drift.py [--source <project root>]

Without a source tree the source-dependent injections (out-of-range citation, wrong-content citation,
stylesheet order, App.jsx route set, blog maxima) are SKIPPED with a notice, never silently passed.
"""
import argparse, json, os, shutil, subprocess, sys, tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)


def jload(root, rel):
    return json.load(open(os.path.join(root, rel), encoding="utf-8"))


def jsave(root, rel, obj):
    json.dump(obj, open(os.path.join(root, rel), "w", encoding="utf-8"), indent=2, ensure_ascii=False)


def run_verify(root, source):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, os.path.join(root, "extraction", "verify_all.py"), "--source", source], capture_output=True, text=True, env=env)
    return r.returncode, [l for l in r.stdout.splitlines() if l.startswith("FAIL")], r.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=os.path.dirname(REPO))
    a = ap.parse_args()
    have_src = os.path.isfile(os.path.join(a.source, "CLONE_SPEC.md"))
    tmp = tempfile.mkdtemp(prefix="drift-")
    results = []

    def case(name, mutate, expect, needs_src=False):
        if needs_src and not have_src:
            print("SKIP   %-58s (needs the source tree)" % name)
            return
        root = os.path.join(tmp, "design-repo")
        shutil.rmtree(root, ignore_errors=True)
        shutil.copytree(REPO, root, ignore=shutil.ignore_patterns("__pycache__"))
        mutate(root)
        code, fails, _ = run_verify(root, a.source)
        hit = [f for f in fails if expect in f]
        ok = code != 0 and bool(hit)
        results.append(ok)
        print("%s %-58s -> %s" % ("CAUGHT " if ok else "MISSED!", name, (hit[0] if hit else "no matching FAIL (exit %d, fails=%s)" % (code, fails[:2]))[:150]))

    def m_phantom(r):
        d = jload(r, "tokens/llm/component-allowlist.json"); d["sections"].append({"id": "ghost.section", "file": "sections/ghost.section.json", "settableContentFields": [], "settableMotionFields": [], "variants": []}); jsave(r, "tokens/llm/component-allowlist.json", d)

    def m_phantom_prim(r):
        d = jload(r, "tokens/llm/component-allowlist.json"); d["primitives"].append({"id": "divider", "file": "primitives/divider.json", "overridableProps": []}); jsave(r, "tokens/llm/component-allowlist.json", d)

    def m_orphan(r):
        s = jload(r, "sections/hero.landscape.json"); s["id"] = "hero.orphan"; jsave(r, "sections/hero.orphan.json", s)

    def m_orphan_comp(r):
        shutil.copy(os.path.join(r, "components/trust-card.json"), os.path.join(r, "components/extra-card.json"))
        c = jload(r, "components/extra-card.json"); c["id"] = "extra-card"; jsave(r, "components/extra-card.json", c)

    def m_oor(r):
        s = jload(r, "sections/hero.landscape.json"); s["measuredFrom"][0] = "src/pages/Home.jsx:99999"; jsave(r, "sections/hero.landscape.json", s)

    def m_oor_range(r):
        s = jload(r, "sections/hero.landscape.json"); s["measuredFrom"][0] = "src/pages/Home.jsx:5-99999"; jsave(r, "sections/hero.landscape.json", s)

    def m_wrong_content(r):
        s = jload(r, "sections/hero.landscape.json")
        cite = s["measuredQuotes"][0]["cite"]
        path, ln = cite.split(":"); ln = int(ln.split("-")[0])
        new = "%s:%d" % (path, ln + 7)
        s["measuredFrom"] = [new if c == cite else c for c in s["measuredFrom"]]
        for q in s["measuredQuotes"]:
            if q["cite"] == cite: q["cite"] = new
        jsave(r, "sections/hero.landscape.json", s)

    def m_count(r):
        m = jload(r, "registry.manifest.json"); m["counts"]["sections"] += 1; jsave(r, "registry.manifest.json", m)

    def m_count_tokens(r):
        m = jload(r, "registry.manifest.json"); m["counts"]["tokens"]["total"] -= 3; jsave(r, "registry.manifest.json", m)

    def m_allowver(r):
        m = jload(r, "registry.manifest.json"); m["allowlistVersion"] = "9.9.9"; jsave(r, "registry.manifest.json", m)

    def m_pinned(r):
        d = jload(r, "tokens/llm/asset-roles.json")
        for x in d["roles"]:
            if x["id"] == "logo.third-party-wordmark": x["generationPolicy"] = "may-generate-new"
        jsave(r, "tokens/llm/asset-roles.json", d)

    def m_pinned_both(r):
        d = jload(r, "tokens/llm/asset-roles.json")
        for x in d["roles"]:
            if x["id"] == "photo.person-portrait": x["generationPolicy"] = "may-generate-new"
        d["pinnedPolicies"]["photo.person-portrait"] = "may-generate-new"
        jsave(r, "tokens/llm/asset-roles.json", d)

    def m_role_enum(r):
        d = jload(r, "tokens/llm/asset-roles.json")
        d["roles"][0]["generationPolicy"] = "free-for-all"; jsave(r, "tokens/llm/asset-roles.json", d)

    def m_rule_phantom(r):
        g = jload(r, "compatibility/graph.json"); g["rules"][0]["id"] = "ONE_HERO_RENAMED"; jsave(r, "compatibility/graph.json", g)

    def m_rule_unimpl(r):
        g = jload(r, "compatibility/graph.json"); g["rules"].append({"id": "BRAND_NEW_RULE", "severity": "error", "description": "x", "enforcedBy": "semantic_validate.py", "measuredFrom": [], "measuredQuotes": []}); jsave(r, "compatibility/graph.json", g)

    def m_rule_sev(r):
        g = jload(r, "compatibility/graph.json"); g["rules"][0]["severity"] = "fatal"; jsave(r, "compatibility/graph.json", g)

    def m_heroless(r):
        g = jload(r, "compatibility/graph.json"); g["rules"][0]["exceptions"]["heroLessTemplates"].remove("legal"); jsave(r, "compatibility/graph.json", g)

    def m_route_gap(r):
        d = jload(r, "templates/routes.json"); d["routes"] = [x for x in d["routes"] if x["path"] != "/terms"]; jsave(r, "templates/routes.json", d)

    def m_route_double(r):
        d = jload(r, "templates/routes.json"); d["routes"].append(dict(d["routes"][1], path="/pricing-copy")); jsave(r, "templates/routes.json", d)

    def m_entry(r):
        m = jload(r, "registry.manifest.json"); m["entryPoints"]["extraEvidence"] = "../CLONE_SPEC.md"; jsave(r, "registry.manifest.json", m)

    def m_abs(r):
        open(os.path.join(r, "README.md"), "a").write("\nsee /" + "Users/someone/project\n")

    def m_hist(r):
        d = jload(r, "tokens/00-foundation/color.json"); d["color"]["ink"]["primary"]["histogramCount"] += 5; jsave(r, "tokens/00-foundation/color.json", d)

    def m_theme(r):
        d = jload(r, "tokens/themes/light.json"); k = next(iter(d["resolved"])); d["resolved"][k]["value"] = "#123456"; jsave(r, "tokens/themes/light.json", d)

    def m_sheet(r):
        d = jload(r, "templates/routes.json"); o = d["routeStylesheets"]["blog"]["order"]; o[2], o[3] = o[3], o[2]; jsave(r, "templates/routes.json", d)

    def m_schema_parity(r):
        d = jload(r, "schema/pagespec.schema.json"); del d["definitions"]["content_hero_landscape"]["properties"]["sectionLabel"]; jsave(r, "schema/pagespec.schema.json", d)

    def m_allow_fields(r):
        d = jload(r, "tokens/llm/component-allowlist.json"); d["sections"][0]["settableContentFields"].append("invented"); jsave(r, "tokens/llm/component-allowlist.json", d)

    def m_blogmax(r):
        s = jload(r, "sections/blog.prose.json"); s["content"]["properties"]["blocks"]["items"]["oneOf"][0]["properties"]["text"]["x-maxWords"] = 200; jsave(r, "sections/blog.prose.json", s)

    def m_pkg(r):
        d = jload(r, "extraction/measured-values.json"); d["sourceProject"]["dependencies"]["react"] = "^17.0.0"; jsave(r, "extraction/measured-values.json", d)

    def m_example(r):
        d = jload(r, "schema/example.pagespec.json"); del d["nodes"][1]["content"]["plans"][0]["price"]; jsave(r, "schema/example.pagespec.json", d)

    def m_open_motion(r):
        d = jload(r, "schema/pagespec.schema.json"); d["definitions"]["motion_hero_marketing"]["additionalProperties"] = True; jsave(r, "schema/pagespec.schema.json", d)

    def m_legal_cmp(r):
        d = jload(r, "extraction/legal-template-comparison.json"); d["verdict"] = "DIFFERENT"; jsave(r, "extraction/legal-template-comparison.json", d)

    def m_order(r):
        d = jload(r, "templates/templates.json"); n = d["templates"]["home"]["nodes"]; n[3], n[4] = n[4], n[3]; jsave(r, "templates/templates.json", d)

    def m_readme(r):
        t = open(os.path.join(r, "README.md"), encoding="utf-8").read().replace("sections=32", "sections=31"); open(os.path.join(r, "README.md"), "w", encoding="utf-8").write(t)

    def m_mv_sheet(r):
        d = jload(r, "extraction/measured-values.json"); o = d["routeStylesheets"]["lists"]["home"]["order"]; o[3], o[4] = o[4], o[3]; jsave(r, "extraction/measured-values.json", d)

    case("measured-values stylesheet list drifts from routes.json", m_mv_sheet, "measured-values.json routeStylesheets")
    case("home template order drifts from the real Home.jsx component order", m_order, "route->template precision", True)
    case("README states a stale section count", m_readme, "README counts marker")
    case("phantom allowlist entry (sections)", m_phantom, "allowlist parity [sections]")
    case("phantom allowlist entry (primitives: Divider)", m_phantom_prim, "allowlist parity [primitives]")
    case("orphan section contract (no allowlist entry)", m_orphan, "allowlist parity [sections]")
    case("orphan component contract (no allowlist entry)", m_orphan_comp, "allowlist parity [components]")
    case("out-of-range citation (line 99999)", m_oor, "citation-range validity", True)
    case("out-of-range citation (range 5-99999)", m_oor_range, "citation-range validity", True)
    case("in-range but WRONG-content citation (line shifted +7)", m_wrong_content, "citation CONTENT", True)
    case("manifest count wrong (sections +1)", m_count, "manifest counts recomputed")
    case("manifest count wrong (tokens.total -3)", m_count_tokens, "manifest counts recomputed")
    case("allowlistVersion drift (manifest 9.9.9)", m_allowver, "allowlistVersion machine-check")
    case("PINNED policy flipped: logo role -> may-generate-new (valid enum)", m_pinned, "PINNED policies")
    case("pinned map + role flipped TOGETHER (person portrait)", m_pinned_both, "compliance-critical roles")
    case("generationPolicy outside the closed enum", m_role_enum, "generationPolicy in the closed 3-value enum")
    case("graph rule id drifts from semantic_validate.py", m_rule_phantom, "IMPLEMENTED_RULES")
    case("graph gains a semantic rule the code does not implement", m_rule_unimpl, "IMPLEMENTED_RULES")
    case("graph rule severity not error|warn", m_rule_sev, "severity error|warn")
    case("graph hero-less exception list drifts from templates", m_heroless, "ONE_HERO_MARKETING exception list")
    case("route gap (/terms removed)", m_route_gap, "route")
    case("route double-binding / unknown route (/pricing-copy)", m_route_double, "route")
    case("entryPoint outside the package ('../CLONE_SPEC.md')", m_entry, "entryPoints")
    case("absolute local path injected in README", m_abs, "no absolute local paths")
    case("histogramCount tampered (ink.primary +5)", m_hist, "histogramCount")
    case("light theme value drifts from foundation", m_theme, "light theme resolves")
    case("per-route stylesheet order swapped", m_sheet, "per-route stylesheet lists", True)
    case("schema content_ definition drops a contract field", m_schema_parity, "schema content_/motion_")
    case("allowlist settableContentFields gains an invented field", m_allow_fields, "settableContentFields")
    case("blog.prose maxWords diverges from the 20 outlines", m_blogmax, "blog.prose maxWords recomputed", True)
    case("package.json dependency drift (react ^17 recorded)", m_pkg, "package.json versions", True)
    case("example loses a required field", m_example, "example.pagespec.json")
    case("motion schema opened (additionalProperties true)", m_open_motion, "no open additionalProperties")
    case("legal grouping verdict flipped (comparison)", m_legal_cmp, "SAME_TEMPLATE")

    shutil.rmtree(tmp, ignore_errors=True)
    code, fails, out = run_verify(REPO, a.source)
    print("\nuntouched repo: verify_all exit %d, FAIL lines: %d" % (code, len(fails)))
    ok = all(results) and code == 0
    print("PROVE-DRIFT: %d/%d injected defects caught; real repo %s" % (sum(results), len(results), "passes" if code == 0 else "FAILS"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
