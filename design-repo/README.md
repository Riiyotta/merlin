# Merlin design-repo

<!-- counts: tokens=352 primitives=13 components=21 sections=32 templates=7 routes=8 assetRoles=14 graphRules=19 -->

An AI-ready, machine-validated description of the pages of a **local React clone of https://www.merlin.computer**: tokens, primitives, components, section contracts, page templates, a compatibility graph, a Draft-07 PageSpec schema, a semantic validator and an adversarial test-suite. A generator can use it to produce new on-brand PageSpecs without inventing colors, copy budgets, sections or assets.

> **NOT FOR PUBLIC REDISTRIBUTION.** The source is a real company's live marketing site. Copy, logos, felt-character art, photographs, product screenshots and brand marks belong to Merlin or third parties. Do not publish this repository or `design-repo.zip`. Status: `design-review-pending`, `productionApproved: false`.

## What is in it (counts recomputed from disk by `extraction/verify_all.py`)

| | |
|---|---|
| tokens | 352 (foundation 249, semantic 57, component 20, layout 26) |
| primitives / components | 13 / 21 |
| sections (contracts) | 32 |
| templates / routes | 7 / 8 (+ 2 routing behaviors that are not pages) |
| asset roles / registered assets | 14 / 73 |
| compatibility-graph rules | 19 |
| motion patterns / reduced-motion fallbacks | 26 / 5 |

```
registry.manifest.json            status, counts, versions, entryPoints (all inside this folder)
tokens/00-foundation/             color, typography, radius, breakpoint, elevation, motion, motion-patterns
tokens/10-semantic|20-component|30-layout|themes   semantic roles, component values, layout, light theme
tokens/llm/                       component-allowlist.json (versioned), asset-roles.json (closed assetRole registry)
primitives/ components/ sections/ one JSON contract per id
templates/templates.json|routes.json      page shapes (structured nodes) and the 1:1 route map
compatibility/graph.json          rhythm/position rules, each severity error|warn, with named exceptions
schema/                           pagespec.schema.json, example.pagespec.json, semantic_validate.py, tests/adversarial_test.py
extraction/                       measured-values.json (citation trail), verify_all.py, prove_drift.py,
                                  derive_histograms.py (+derived-histograms.json), derive_template_comparison.py (+legal-template-comparison.json)
```

## Run it

```
python3 extraction/verify_all.py          # drift-proofed checks; exit 1 on any FAIL
python3 schema/semantic_validate.py [spec.json]
python3 schema/tests/adversarial_test.py  # every mutation rejected, every control passes
python3 extraction/prove_drift.py         # injects drift into scratch copies and proves verify_all catches each
python3 -I extraction/derive_histograms.py --write --source <project root>      # re-derive token histograms
python3 -I extraction/derive_template_comparison.py --write --source <project root>
```

Needs `python3` with `jsonschema` (`pip3 install --user jsonschema`). The validators read only this folder's own JSON, so they run without `-I` (the isolated flag also hides user-site packages such as jsonschema); the derive scripts read the external source tree and are run with `-I`. Every script derives the repo root from `__file__`; nothing is hard-coded. When no sibling source project is present (`design-repo/` alone), source-dependent checks degrade to **warnings**, never failures. The source project is not a git repository, so there is nothing to gitignore; if you put this under git, ignore `design-repo.zip` (it is a build artifact regenerated last with the CLI `zip`).

## Structurally unusual facts (documented, not normalized away)

1. **Real, live company source.** See the banner and `tokens/llm/asset-roles.json`: 14 closed `assetRole`s, each pinned to `must-reuse-exact`, `must-not-fabricate` or `may-generate-new` (membership in the enum is not enough; `verify_all.py` pins each role to its exact value). A generator must never reproduce the real third-party marks (Notion, Salesforce, Harvard, HubSpot, McKinsey, Qatar Airways, DoorDash, Instacart, Ashby, Google, Slack, Adobe, Zoom, Apple), the Merlin logo/app icon/mascot art, real people's photos, product screenshots or recordings; the safe choice is `placeholder:neutral`.
2. **Placeholder copy.** The manifesto essay and its handwriting overlays, /privacy and /terms bodies, blog post bodies, pricing FAQ answers and the blog aside are original filler sized to the live word counts. Content contracts carry structure and `maxWords` only. NOT placeholder in the clone: the 5 home FAQ answers, the email preview body and demo text (live copy; only budgets are recorded here). The bundled example uses short structural UI copy plus neutral placeholder prose.
3. **Local stand-ins / no external requests.** The FAQ ask form is a client-side mock (`apiMode: local-mock`); installer links go to `/download-stub.txt` (`installerSource: local-stub`). The clone makes no outbound requests and runs no analytics; PageSpecs may not contain `http(s)://` (rule `NO_EXTERNAL_REQUESTS`).
4. **Original CSS verbatim with per-route isolation.** Each route lazy-imports its own ordered stylesheet list (`templates/routes.json` `routeStylesheets`, checked against `src/styles/<route>.css`). Class names, including CSS-module hashes such as `blog_page__bLGfe`, are load-bearing (`extraction/measured-values.json` `loadBearingClassNames`). Tailwind is installed but disabled; tokens come from the original CSS custom properties and computed values.
5. **Time-of-day copy on /manifesto** (morning 5-11, afternoon 12-16, evening 17-21, night, before-5am variant); motion is IntersectionObserver- and spring-driven with a reduced-motion branch on every animated section (`reducedMotionFallback` is required and locked per section).
6. **Deliberate absences.** /pricing and /manifesto have no floating nav; /download has no nav and no footer (`main.install-page`); blog/legal pages have no entrance animation; there is no monthly/annual pricing toggle (the schema is closed, so a toggle field is rejected).

## Routes -> templates (1:1, verified against `src/App.jsx`)

| route | template | evidence | note |
|---|---|---|---|
| `/` | `home` | measured |  |
| `/pricing` | `pricing` | measured |  |
| `/download` | `install` | measured | `?start=1` alias (same page) |
| `/manifesto` | `manifesto` | measured |  |
| `/blog` | `blog-index` | measured |  |
| `/blog/:slug` | `blog-post` | measured-sample | 20 posts (19 in sitemap + 1 featured, no cover) |
| `/privacy` | `legal` | measured |  |
| `/terms` | `legal` | measured |  |

Routing behaviors (not pages): `*` renders Home; an unknown `/blog/<slug>` does `Navigate replace` to `/blog` (evidence level `derived-from-source`: never measured on the live site).

| template | routes | evidence | node sequence |
|---|---|---|---|
| `home` | `/` | measured | hero.marketing/home > hero.landscape > proof.company-logos > story.context-routines > story.browser-tasks > story.meetings-projects > story.companion > scene.privacy-trust > faq.accordion > shell.footer-closing > shell.floating-nav |
| `pricing` | `/pricing` | measured | hero.marketing/pricing > pricing.plans > pricing.included > pricing.faq > shell.footer-closing |
| `install` | `/download` | measured | shell.install-header > install.intro > install.steps |
| `manifesto` | `/manifesto` | measured | shell.corner-nav/manifesto > manifesto.opening > manifesto.photo/after-opening > manifesto.understanding > manifesto.photo/after-understanding > manifesto.action > manifesto.photo/after-action > manifesto.ending > shell.footer-closing |
| `blog-index` | `/blog` | measured | shell.corner-nav/blog > blog.intro > blog.featured > blog.story-list > blog.manifesto-aside > shell.footer-closing |
| `blog-post` | `/blog/:slug` | measured-sample | shell.corner-nav/blog > blog.article-header > blog.prose > blog.article-end > shell.footer-closing |
| `legal` | `/privacy`, `/terms` | measured | shell.corner-nav/legal > legal.heading > legal.body > shell.footer-closing |

`/privacy` and `/terms` share one template after a real structural comparison (`extraction/legal-template-comparison.json`: identical `main#top` children; only optional elements differ - intro on /privacy, h3/ul/li on /terms).

## Asset roles

| role | policy | what it covers |
|---|---|---|
| `logo.third-party-wordmark` | `must-not-fabricate` | Real third-party company/brand logos and wordmarks: the companies logo row (Notion, Salesforce, Harvard, HubSpot, McKinsey) and the brand logos inside the browser-task mock sites (Qatar Airways, Instacart, Ashby). |
| `icon.third-party-app` | `must-not-fabricate` | Real third-party app icons (Gmail, Google Calendar, Slack, Notion, Granola, Linear, Google Meet, Zoom, Chrome, Finder, Photoshop, DoorDash, Ashby favicon). |
| `brand.merlin-app-icon` | `must-reuse-exact` | The Merlin dock/app icon and the inline Merlin face mark. |
| `brand.merlin-mascot-art` | `must-reuse-exact` | The felt Merlin mascot artwork (mark. |
| `illustration.felt-scene` | `must-reuse-exact` | Merlin's commissioned felt-character scene art (lakeside landscape, armchair, meeting, studio, beach). |
| `screenshot.os-install-step` | `must-not-fabricate` | macOS screenshots of the install steps (Dock/Downloads, Applications drag, launch). |
| `screenshot.product-output` | `must-not-fabricate` | Real product-output screenshots: the six launch-deck slide images shown in the hero notification detail. |
| `photo.stock-cover` | `must-not-fabricate` | Blog article cover photographs (third-party stock imagery served from the CMS CDN in the live site). |
| `photo.person-portrait` | `must-not-fabricate` | Photographs of a real, named person (the blog author avatar). |
| `photo.mock-product` | `must-not-fabricate` | Food and grocery product photographs inside the DoorDash/Instacart mock sites (third-party imagery). |
| `media.audio-sample` | `must-not-fabricate` | The recorded audio clip played by the meeting transcript player (merlin-introduction. |
| `art.footer-ascii` | `must-reuse-exact` | The ASCII bird and beach SVGs of the closing footer (Merlin's own art). |
| `icon.generic-ui` | `may-generate-new` | Generic interface glyphs (Feather/Ionicons arrows, chevrons, check, clock, play). |
| `art.line-illustration` | `may-generate-new` | Decorative hand-drawn arrows and the privacy trust-card line art. |

## Compatibility graph

| rule | severity | enforced by |
|---|---|---|
| `ONE_HERO_MARKETING` | error | semantic_validate.py |
| `TEMPLATE_ORDER` | error | semantic_validate.py |
| `FOOTER_PRESENT_AND_LAST` | error | semantic_validate.py |
| `FLOATING_NAV_HOME_ONLY` | error | semantic_validate.py |
| `CORNER_NAV_FIRST` | error | semantic_validate.py |
| `NO_ADJACENT_SAME_SECTION_VARIANT` | error | semantic_validate.py |
| `ONE_PER_PAGE` | error | semantic_validate.py |
| `MAX_ONE_PINNED_STAGE` | error | semantic_validate.py |
| `MOTION_FALLBACK_REQUIRED` | error | schema+semantic_validate.py |
| `VARIANT_FIELD_RULES` | error | schema+semantic_validate.py |
| `ASSET_REF_POLICY` | error | schema+semantic_validate.py |
| `NO_EXTERNAL_REQUESTS` | error | schema+semantic_validate.py |
| `MAX_WORDS` | error | semantic_validate.py |
| `LEGAL_ACTIVE_TAB_MATCHES_ROUTE` | error | semantic_validate.py |
| `LEGAL_INTRO_ONLY_ON_PRIVACY` | warn | semantic_validate.py |
| `BLOG_FEATURED_NOT_IN_STORY_LIST` | error | semantic_validate.py |
| `PLAN_ONE_PRIMARY_CTA` | warn | semantic_validate.py |
| `ROUTE_TEMPLATE_BINDING` | error | semantic_validate.py |
| `NO_BILLING_TOGGLE` | error | schema |

Exceptions (hero-less templates, footer-less install, nav embedded in hero on home/pricing, floating nav home-only) live in the graph and are READ by `semantic_validate.py`; `verify_all.py` checks they equal what `templates.json` actually contains.

## Motion and responsive

`node.motion` is closed to `{patterns, reducedMotionFallback}` (no `additionalProperties: true`). Patterns are a closed catalog grounded in framer-motion springs/`whileInView`, GSAP ScrollTrigger pin+snap, CSS keyframes and hover transitions (`tokens/00-foundation/motion-patterns.json`); each section lists its allowed patterns and a locked fallback. Responsive behavior is a structured per-section array (`query`, `breakpoint` token, `change`, cited against real CSS/spec lines): breakpoints 1023/1000, 767/768, 699/700 and route-specific values (760 blog, 640/900 legal, 620/900 install, 600/1023 manifesto).

## Evidence, inference and honesty

Every token, section, template, route and rule carries `measuredFrom` citations (`path:line[-line]`) and `measuredQuotes` pinning the cited text; `verify_all.py` checks range validity AND that each quote sits inside its cited lines. Colors/sizes/radii/breakpoints/durations also carry a `histogramCount` recomputed from `extraction/derived-histograms.json` (derived by script from the compiled CSS; the source ships no histogram). Evidence levels: `measured`, `measured-sample` (blog posts: 2 of 20 measured), `derived-from-source`. Scene internals (mock sites, Photoshop/Slack/Chrome demos, notification detail views) are documented at contract level only. Mock-site brand colors are deliberately not tokenized. See `extraction/measured-values.json` `inferredVsMeasured`.

### Where the pre-existing specs were wrong or inconsistent with the real source

- **D1** (CLONE_SPEC_PAGES_A.md section 2.2): claim: pricing FAQ answers given '(verbatim)'. Reality: src/components/pricing/pricingData.js uses ORIGINAL placeholder answers (up to 43 words vs the live 45); only the questions are verbatim.
- **D2** (CLONE_SPEC_PAGES_A.md section 4.4): claim: placeholder word counts per variant: morning finish 32, fallback finish 34. Reality: the clone's placeholders have morning finish 33 and fallback finish 33 (all other counts match: 21/18, 22/19, 22/19/33, 28|24/18/35, 19/18).
- **D3** (CLONE_SPEC_PAGES_B.md section 5): claim: /terms has '40 p'. Reality: the spec's own outline table, the clone data and the live DOM capture all give 30 paragraphs (19 h3, 2 ul); the '40' is wrong.
- **D4** (CLONE_SPEC_PAGES_B.md section 0.1): claim: 'The clone can therefore import all original CSS once, globally'. Reality: the real clone does the opposite on purpose: per-route lazy CSS lists (src/styles/<route>.css), matching Next.js per-route chunks; only 357da7... and 437c25... are global (src/index.css).
- **D5** (CLONE_SPEC.md section 0 (step 1)): claim: copy only the first ~6 rules of the Mantine bundle 437c25afc566ca52.css. Reality: the clone imports the whole 179 KB Mantine bundle globally in src/index.css (harmless; the histogram script tallies it separately as vendor so it cannot skew tokens).
- **D6** (task brief / CLONE_SPEC.md sections 5c, 10): claim: long-form text in the clone is placeholder. Reality: the 5 home FAQ answers, the Gmail email body and the demo/notification text are LIVE copy transcribed in the clone and spec; only manifesto, legal, blog bodies, pricing FAQ answers and the blog aside are placeholders.
- **D7** (CLONE_SPEC_PAGES_B.md section 1.1): claim: blog aside handwriting is a specific live phrase. Reality: the clone replaces it with an original placeholder of the same word count (the spec reproduces the live phrase, so this design-repo does not copy it).

## Versions

`allowlistVersion` is machine-checked (manifest == `tokens/llm/component-allowlist.json`). `repositoryVersion` and `pageSpecVersion` are documentation-only markers that nothing checks. The design-repo is a snapshot of the clone as measured on 2026-10-07; re-run `verify_all.py` with the source present after any upgrade (it diffs `package.json` versions, the route set, asset files and stylesheet lists).
