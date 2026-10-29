# Merlin design-repo

<!-- counts: tokens=352 primitives=13 components=21 sections=34 templates=7 routes=8 assetRoles=22 graphRules=38 -->

An AI-ready, machine-validated description of the pages of a **local React clone of https://www.merlin.computer**: tokens, primitives, components, section contracts, page templates, a compatibility graph, a Draft-07 PageSpec schema, a semantic validator and an adversarial test-suite. A generator can use it in two explicit modes: `mode: "clone"` (faithful reconstruction; real brand, copy and assets may be reused) and `mode: "generation"` (a new page for someone else: the semantic validator rejects every source brand, customer, person, URL, claim, copy shingle and proprietary asset it can detect).

> **NOT FOR PUBLIC REDISTRIBUTION.** The source is a real company's live marketing site. Copy, logos, felt-character art, photographs, product screenshots and brand marks belong to Merlin or third parties. Do not publish this repository or `design-repo.zip`. Status: `design-review-pending`, `productionApproved: false`. Category binding: `saas` -> `n0-saas-design-constraints-common` 0.1.0 (`policy/design-policy.json`, pending architecture review).

## What is in it (counts recomputed from disk by `extraction/verify_all.py`)

| | |
|---|---|
| tokens | 352 (foundation 249, semantic 57, component 20, layout 26) |
| token catalog / PageSpec-approved / token slots | 375 / 145 / 14 (`tokens/llm/token-catalog.json`, `token-policy.json`) |
| primitives / components | 13 / 21 |
| sections (contracts) | 34 |
| templates / routes | 7 / 8 (+ 2 routing behaviors that are not pages) |
| asset roles / registered assets | 22 / 73 |
| compatibility-graph rules | 38 |
| motion patterns / reduced-motion fallbacks | 26 / 5 |
| example PageSpecs | 1 clone (`schema/example.pagespec.json`) + 7 generation (`schema/examples/`, one per template) |

```
registry.manifest.json            status, counts, versions, entryPoints (all inside this folder)
tokens/00-foundation/             color, typography, radius, breakpoint, elevation, motion, motion-patterns
tokens/10-semantic|20-component|30-layout|themes   semantic roles, component values, layout, light theme
tokens/llm/                       component-allowlist.json (versioned), token-catalog.json (GENERATED), token-policy.json
assets/asset-roles.json           closed assetRole registry: generationPolicy + availability (pinned in code) + substitutes
policy/design-policy.json         common-policy binding (saas -> n0-saas-design-constraints-common 0.1.0) + classification evidence
primitives/ components/ sections/ one JSON contract per id
templates/templates.json|routes.json      page shapes (structured nodes) and the 1:1 route map
compatibility/graph.json          rhythm/position rules, each severity error|warn, with named exceptions
schema/                           pagespec.schema.json, section-contract.schema.json, example.pagespec.json (clone),
                                  examples/generated.*.pagespec.json (generation), semantic_validate.py, textnorm.py,
                                  source-identity.json (GENERATED leakage registry), tests/adversarial_test.py
extraction/                       measured-values.json (citation trail), verify_all.py, prove_drift.py,
                                  derive_histograms.py (+derived-histograms.json), derive_template_comparison.py (+legal-template-comparison.json),
                                  build_token_catalog.py, build_source_identity.py, build_section_provenance.py,
                                  measure_sections.mjs + wrapper_gate.py (+ wrapper-gate-whitelist.json)
```

## Run it

```
python3 extraction/verify_all.py          # drift-proofed checks; exit 1 on any FAIL
python3 schema/semantic_validate.py [spec.json]
python3 schema/tests/adversarial_test.py  # every mutation rejected, every control passes
python3 extraction/prove_drift.py [--scratch DIR]   # injects drift into scratch copies and proves verify_all catches each
python3 extraction/build_token_catalog.py [--write]        # default --check: catalog == rebuild of tokens/
python3 extraction/build_source_identity.py [--write]      # default --check: leakage registry == rebuild of the source
python3 extraction/build_section_provenance.py [--write]   # default --check: source/semantic == the real files
python3 extraction/wrapper_gate.py [--self-test]           # R9 gate over measured sectionHeights
NODE_PATH="$(npm root -g)" node extraction/measure_sections.mjs --base http://localhost:<port> [--write]   # re-measure a served build
python3 -I extraction/derive_histograms.py --write --source <project root>      # re-derive token histograms
python3 -I extraction/derive_template_comparison.py --write --source <project root>
```

Needs `python3` with `jsonschema` (`pip3 install --user jsonschema`). The validators read only this folder's own JSON, so they run without `-I` (the isolated flag also hides user-site packages such as jsonschema); the derive scripts read the external source tree and are run with `-I`. Every script derives the repo root from `__file__`; nothing is hard-coded. When no sibling source project is present (`design-repo/` alone), source-dependent checks degrade to **warnings**, never failures. `design-repo.zip` is a build artifact: it is gitignored in the source project and is not tracked.

## Structurally unusual facts (documented, not normalized away)

1. **Real, live company source.** See the banner and `assets/asset-roles.json` (and "Modes" below): the original 14 closed `assetRole`s, each pinned to `must-reuse-exact`, `must-not-fabricate` or `may-generate-new` (membership in the enum is not enough; `verify_all.py` pins each role to its exact value). A generator must never reproduce the real third-party marks (Notion, Salesforce, Harvard, HubSpot, McKinsey, Qatar Airways, DoorDash, Instacart, Ashby, Google, Slack, Adobe, Zoom, Apple), the Merlin logo/app icon/mascot art, real people's photos, product screenshots or recordings; the safe choice is `placeholder:neutral`.
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
| `blog-post` | `/blog/:slug` | measured-sample | shell.corner-nav/blog > blog.article-header > blog.prose (repeatable: one h2-bounded chapter per node, max 12) > blog.article-end > shell.footer-closing |
| `legal` | `/privacy`, `/terms` | measured | shell.corner-nav/legal > legal.heading > legal.contents (sticky TOC) > legal.section (repeatable: one per h2, max 14) > legal.document-footer > shell.footer-closing |

`/privacy` and `/terms` share one template after a real structural comparison (`extraction/legal-template-comparison.json`: identical `main#top` children; only optional elements differ - intro on /privacy, h3/ul/li on /terms).

## Asset roles

`generationPolicy` says how an asset may be produced; `availability` says in which mode it may appear (`clone-only` / `blocked-for-generation` roles are rejected in `mode: "generation"` and name their `generationSafeSubstitutes`). Availability is pinned in code twice (`PINNED_AVAILABILITY` in `schema/semantic_validate.py` and `extraction/verify_all.py`), so editing the registry alone cannot loosen a role. A real logo/wordmark is never usable in generation mode. `link.placeholder-url` and `copy.original` are non-media roles (hrefs/emails on `.example`/`.invalid` only; original copy). Each section contract lists its `generatedAssetRoles`.

| role | policy | availability | generation-safe substitutes | what it covers |
|---|---|---|---|---|
| `logo.third-party-wordmark` | `must-not-fabricate` | `blocked-for-generation` | `logo.placeholder-customer` | Real third-party company/brand logos and wordmarks: the companies logo row (Notion, Salesforce, Harvard, HubSpot, McKinsey) and the brand logos inside the browser-task mock sites (Qatar Airways, Instacart, Ashby) |
| `icon.third-party-app` | `must-not-fabricate` | `blocked-for-generation` | `icon.generic-ui`, `logo.placeholder-customer` | Real third-party app icons (Gmail, Google Calendar, Slack, Notion, Granola, Linear, Google Meet, Zoom, Chrome, Finder, Photoshop, DoorDash, Ashby favicon) |
| `brand.merlin-app-icon` | `must-reuse-exact` | `clone-only` | `brand.placeholder-mark`, `media.user-supplied` | The Merlin dock/app icon and the inline Merlin face mark |
| `brand.merlin-mascot-art` | `must-reuse-exact` | `clone-only` | `brand.placeholder-mark`, `illustration.generated`, `media.user-supplied` | The felt Merlin mascot artwork (mark.webp) used as the manifesto signature mark and as the artwork opened in the Photoshop demo |
| `illustration.felt-scene` | `must-reuse-exact` | `clone-only` | `illustration.generated`, `media.user-supplied` | Merlin's commissioned felt-character scene art (lakeside landscape, armchair, meeting, studio, beach) |
| `screenshot.os-install-step` | `must-not-fabricate` | `blocked-for-generation` | `screenshot.placeholder`, `media.user-supplied` | macOS screenshots of the install steps (Dock/Downloads, Applications drag, launch) |
| `screenshot.product-output` | `must-not-fabricate` | `clone-only` | `screenshot.placeholder`, `media.user-supplied` | Real product-output screenshots: the six launch-deck slide images shown in the hero notification detail |
| `photo.stock-cover` | `must-not-fabricate` | `blocked-for-generation` | `illustration.generated`, `media.user-supplied` | Blog article cover photographs (third-party stock imagery served from the CMS CDN in the live site) |
| `photo.person-portrait` | `must-not-fabricate` | `blocked-for-generation` | `photo.fictional-person`, `media.user-supplied` | Photographs of a real, named person (the blog author avatar) |
| `photo.mock-product` | `must-not-fabricate` | `blocked-for-generation` | `illustration.generated`, `media.user-supplied` | Food and grocery product photographs inside the DoorDash/Instacart mock sites (third-party imagery) |
| `media.audio-sample` | `must-not-fabricate` | `clone-only` | `media.user-supplied` | The recorded audio clip played by the meeting transcript player (merlin-introduction.mp3) |
| `art.footer-ascii` | `must-reuse-exact` | `clone-only` | `art.line-illustration`, `illustration.generated` | The ASCII bird and beach SVGs of the closing footer (Merlin's own art) |
| `icon.generic-ui` | `may-generate-new` | `generation-safe` | - | Generic interface glyphs (Feather/Ionicons arrows, chevrons, check, clock, play) |
| `art.line-illustration` | `may-generate-new` | `generation-safe` | - | Decorative hand-drawn arrows and the privacy trust-card line art |
| `brand.placeholder-mark` | `may-generate-new` | `generation-safe` | - | A placeholder brand mark for a fictional or not-yet-branded product: simple generated monogram/shape, no resemblance to the source or any real brand |
| `media.user-supplied` | `must-not-fabricate` | `generation-safe` | - | An asset the operator/user supplies for their own product (their logo, screenshots, photos, audio) |
| `illustration.generated` | `may-generate-new` | `generation-safe` | - | An original generated illustration (scene, cover art, product art) for a generated page |
| `screenshot.placeholder` | `may-generate-new` | `generation-safe` | - | A neutral placeholder product screenshot (wireframe-like UI frame with fictional content) for a generated page |
| `photo.fictional-person` | `may-generate-new` | `generation-safe` | - | A generated avatar/portrait of a clearly fictional person, paired with a fictional name |
| `logo.placeholder-customer` | `may-generate-new` | `generation-safe` | - | A placeholder customer/partner logo: a generated neutral wordmark of a fictional company for social-proof rows |
| `link.placeholder-url` | `may-generate-new` | `generation-safe` | - | Placeholder links for generated pages: relative internal routes, or hosts/emails on the reserved .example / .invalid domains only (RFC 2606 / 6761) |
| `copy.original` | `may-generate-new` | `generation-safe` | - | Original copy written for the generated page (headings, body, CTAs, FAQ, legal placeholder text) |

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
| `LEGAL_SECTION_IDS_UNIQUE` | error | semantic_validate.py |
| `BLOG_PROSE_CHAPTER_HEADING` | error | semantic_validate.py |
| `ASSET_AVAILABILITY_PINNED` | error | semantic_validate.py |
| `RETRIEVAL_ELIGIBILITY_PINNED` | error | semantic_validate.py |
| `GENERATION_MODE_BRAND` | error | semantic_validate.py |
| `GENERATION_MODE_CUSTOMER` | error | semantic_validate.py |
| `GENERATION_MODE_PERSON` | error | semantic_validate.py |
| `GENERATION_MODE_URL` | error | semantic_validate.py |
| `GENERATION_MODE_CLAIM` | error | semantic_validate.py |
| `GENERATION_MODE_COPY` | error | semantic_validate.py |
| `GENERATION_MODE_ASSET` | error | semantic_validate.py |
| `GENERATION_MODE_SCREENSHOT` | error | semantic_validate.py |
| `TOKEN_UNKNOWN` | error | semantic_validate.py |
| `TOKEN_RAW_COLOR` | error | semantic_validate.py |
| `TOKEN_ARBITRARY_SPACING` | error | semantic_validate.py |
| `TOKEN_UNSUPPORTED_FONT` | error | semantic_validate.py |
| `TOKEN_SLOT_MISMATCH` | error | semantic_validate.py |
| `TOKEN_NOT_APPROVED` | error | semantic_validate.py |
| `TOKEN_THEME_COMBINATION` | error | semantic_validate.py |

Exceptions (hero-less templates, footer-less install, nav embedded in hero on home/pricing, floating nav home-only, repeatable legal.section / blog.prose nodes) live in the graph and are READ by `semantic_validate.py`; `verify_all.py` checks they equal what `templates.json` actually contains.

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

## Modes: clone vs generation (BASELINE R1-R5)

Every PageSpec carries a required, closed `mode`:

- `clone`: faithful reconstruction of the source. Real brand, copy and registered assets may be reused for fidelity (the pricing example `schema/example.pagespec.json` is a clone spec; an adversarial control proves real brand/CTA/felt-scene/customer-logo content still validates in this mode).
- `generation`: a new page for someone else. `schema/semantic_validate.py` rejects, each with its own rule: `GENERATION_MODE_BRAND` (Merlin, its domains/emails, `brand.*` roles), `_CUSTOMER` (the social-proof and browser-task brands, third-party logo/app-icon roles), `_PERSON` (blog author, named mock personas, real-person portraits), `_URL` (source hosts, the Mac download host and installer stub path, any email/host not on `.example`/`.invalid`), `_CLAIM` (the social-proof claim, any real `(price, credits)` plan tier), `_COPY` (any normalised 5-word shingle of the source copy), `_ASSET` (`reuse:` of a source file, a source file name, any clone-only/blocked role) and `_SCREENSHOT` (OS-install / product-output screenshots).

The patterns are not typed by hand: `extraction/build_source_identity.py` derives `schema/source-identity.json` from the real source (`index.html` title, `src/**`, `src/data/blog-posts.json`, `CLONE_SPEC*.md`, `ASSET_MANIFEST.json`, `public/assets/`), with `file:line` evidence per term; copy is stored only as sha256-truncated 5-word shingle hashes. `verify_all.py` re-derives it and checks every evidence line contains its term. Strings are normalised by `schema/textnorm.py` (NFKC, zero-width removal, curly quotes, dash variants) before matching.

One `mode: "generation"` example per template family lives in `schema/examples/` (fictional brand "Fernlight", original copy, generated/placeholder/user-supplied assets, `.example` contacts, invented plan tiers).

**Honest limits.** Detection is string-based: it does not catch paraphrase, translation, text inside images, or deliberate misspelling. Common 5-word phrases that also occur in the source copy are rejected (false positives are possible). No human has reviewed the derived patterns. Fixed demo scenes (`story.*` scripted demos) render third-party app chrome inside their implementation; the PageSpec only selects them by closed enum, so a generation renderer must swap the baked-in assets for the roles' `generationSafeSubstitutes` - the validator cannot see inside an implementation.

## Tokens for PageSpecs (BASELINE R10)

`tokens/llm/token-catalog.json` is GENERATED by `extraction/build_token_catalog.py` from the token files (no values typed in; the clone's `tailwind.config.js` has an empty `theme.extend`, the tokens come from the original CSS). It lists every token with category, value/ref, source file, `approvedForPageSpec` and (for semantic colours) its scheme, plus the theme's resolved values. `tokens/llm/token-policy.json` defines the closed PageSpec `tokens` slots (surface, text, border, accent, headingType, bodyType, labelType, sectionSpacing, gap, contentWidth, cardRadius, cardElevation, motionDuration, motionEasing), the approved vs catalogue-only categories, forbidden raw-value patterns, alias/fallback rules (no raw fallback; font fallbacks live inside the family token) and theme restrictions (one theme, `light`; the black privacy scene is a section-local `scene-dark` scheme; text/surface contrast >= 4.5). The semantic validator enforces it as `TOKEN_UNKNOWN`, `TOKEN_RAW_COLOR`, `TOKEN_ARBITRARY_SPACING`, `TOKEN_UNSUPPORTED_FONT`, `TOKEN_SLOT_MISMATCH`, `TOKEN_NOT_APPROVED`, `TOKEN_THEME_COMBINATION`. Both files are registered in `registry.manifest.json` (entryPoints + `counts.tokenCatalog`), and `verify_all.py` fails if the catalog differs from a rebuild or a policy name does not resolve.

## Sections: semantic units, provenance, retrieval, wrapper gate (R6-R9)

- **R6.** The whole-document `legal.body` was decomposed into `legal.contents` (sticky TOC), `legal.section` (repeatable, one per h2 part) and `legal.document-footer`; `blog.prose` is now one h2-bounded chapter per node (repeatable). The decomposition was driven by measured heights: before it, `legal.body` held 63.6% (/privacy) and 79.0% (/terms) of the page and `blog.prose` 81.2% of a post.
- **R7.** Every contract has a closed `source {id, tag, file, lines}` (where the element really is) and `semantic {id, category}` (what the AI sees), validated by the closed `schema/section-contract.schema.json`. `extraction/build_section_provenance.py` derives `source` from the real files; `verify_all.py` re-derives it and checks each range is inside the file and the tag opens at the start line.
- **R8.** `retrievalEligible` is explicit on every contract; `shell.floating-nav` (fixed, scroll-mounted utility nav) and `legal.contents` (derived TOC) are `false` with a reason. The set is pinned in code in both validators and mirrored in the allowlist.
- **R9.** `extraction/measure_sections.mjs` measured every template's sections at 1440px from a local `vite preview` of the built clone (not the live site); results are in `extraction/measured-values.json` `sectionHeights`. `extraction/wrapper_gate.py` (thresholds pinned in code: HERO > 1800px warn / > 3000px error, one section > 50% warn / > 60% error, missing measurement or wrong viewport = error) runs inside `verify_all.py`. The current data has no errors and one warning: `blog.story-list` is 52.3% of /blog (a flat list of 19 posts; below the error threshold, so not whitelisted). The whitelist is empty; any future entry must say "agent attestation, not a human sign-off" when an agent reviewed it.

## Common-policy binding (requirement 10)

`registry.manifest.json` binds `category: "saas"` to `n0-saas-design-constraints-common` 0.1.0 (commonIrVersion 0.5, `hard-and-soft`). Evidence (in `policy/design-policy.json`): three monthly subscription plans with usage credits, a "Subscription and Billing" terms section, a professional audience ("Used by professionals at ..."), and delivery as a downloadable Mac client. It is self-serve prosumer SaaS, not sales-led B2B, so the policy's B2B-only constructs (dashboards, demo booking, feature matrices, integration directories) must not be invented. `designPolicy.contentHash` is sha256 over the policy's `enforcedBy` files and is recomputed by `verify_all.py`. The classification is an agent's decision (agent attestation, not a human sign-off); `approval.architectureDecisionRecorded` is `false`.

## What was not done or measured

- Visual parity of the clone against the live site was not measured in this revision (no live capture); the section heights are from the local build only.
- No IR file was generated.
- Agent attestation is not a human sign-off: no human reviewed the pinned patterns, the SaaS classification or the section categories.

## Versions

`allowlistVersion` (2.0.0) is machine-checked (manifest == `tokens/llm/component-allowlist.json`), as is `designPolicy.contentHash`. `repositoryVersion` (2.0.0) and `pageSpecVersion` (2.0.0: required `mode`, `theme`, `tokens`) are documentation-only markers that nothing checks. The design-repo is a snapshot of the clone as measured on 2026-10-07; re-run `verify_all.py` with the source present after any upgrade (it diffs `package.json` versions, the route set, asset files and stylesheet lists).
