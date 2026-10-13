Source: https://www.merlin.computer/

# Merlin clone spec, pages A: /pricing, /download (+ ?start=1), /manifesto

Measured live with Playwright (Chromium, macOS UA) on 2026-10-07 at 1440x900, 1280x800 and 390x844. All numbers are computed styles or `getBoundingClientRect()` results. Boxes are `[x, y(document), w, h]` in CSS px at 1440 unless stated. Read `CLONE_SPEC.md` §0–1 first. The build approach is the same: import the original compiled CSS verbatim, in the route's `<link>` order, and rebuild the DOM with the exact class names.

Reference files (all local, for measurement only):
- Hydrated `<body>` outerHTML: `reference/pages/pricing.html`, `reference/pages/download.html`, `reference/pages/manifesto.html`. These contain the exact markup, inline SVGs, `srcset`s and aria attributes. Copy the SVG markup from them.
- Annotated DOM trees with boxes: `reference/pages/{pricing,download,manifesto}-tree-1440.txt`. The manifesto tree lists word counts instead of essay text.
- Full computed-style dumps: `reference/pages/{pricing,download,manifesto}-styles-1440.json`.
- Full-page screenshots: `reference/pages/{pricing,download,manifesto}-full-{1440,1280,390}.png`. **Artifact:** in the full-page captures, the fixed `.skip-link` ("Skip to plans" / "Read the manifesto") shows up partway down the page. It is not visible on the live page because it sits at `translateY(-180%)` until focused.
- Route JS chunks: `reference/source/pages/pricing-page-8299730973590a41.js`, `download-page-bb533f8a3eddd657.js`, `manifesto-page-3b4268b2ba0b8b84.js`, plus shared chunks newly saved there: `6407-3385f66c9f91b609.js` and `7811-5a4570d8c66cf448.js`. Section and artifact icons are in the existing `reference/source/6950-9e48fb1cb1316049.js` (modules `17712`, `77159`).

---

## 0. CSS, fonts and assets per route

| Route | `<link rel=stylesheet>` order (apply in this order) | New for this run |
|---|---|---|
| /pricing | `357da7cf10d68108` → `437c25afc566ca52` → `a5f02e9d0c6db7af` → `f7c0a2656765fcca` → `f46c55d95248097e` → `922109019b2259fa` → `e2e0ba86a6b0d559` → **`2abce9a6dc03269b`** → `ea3e27f6a69b5df4` | `2abce9a6dc03269b.css` (pricing rules, 4.3 KB) |
| /download | `357da7cf10d68108` → `437c25afc566ca52` → **`9168513aa22c6d8a`** | `9168513aa22c6d8a.css` (install page, 2.9 KB) |
| /manifesto | `357da7cf10d68108` → `437c25afc566ca52` → `a5f02e9d0c6db7af` → `922109019b2259fa` → `f46c55d95248097e` → `e2e0ba86a6b0d559` → **`ae725ea36c48b431`** → `ea3e27f6a69b5df4` | `ae725ea36c48b431.css` (manifesto rules, 4.6 KB) |

- Every other hash was already in `src/styles/original/` with identical filenames. The three new files are now in `/Users/riyaghosh/V3/merlin/src/styles/original/`. None of them contains a non-data `url()`, so no rewriting was needed.
- On /download, the live `<head>` also gains preload links for all homepage CSS. That comes from Next prefetching `/` because of the brand link, not from the page itself, so do not import them. Pricing also preloads `ae725ea…` and manifesto preloads `2abce9a…`/`f7c0…` for the same reason. Only the stylesheets in the table are applied.
- The `:root{--mantine-font-family…}` inline style is present on all three routes. `src/index.css` already sets it.
- The order differs from the homepage. For example, pricing has `a5f02e9d` before `f7c0`/`f46c`/`9221`/`e2e0`. Keep each route's order, because `#top .x` specificity ties are decided by order.
- **Fonts:** no new files. Pricing and manifesto use Exposure plus Open Runde 400/500/600. Manifesto also uses `Caveat` (`/fonts/Caveat.ttf`, byte-identical to the live file, `font-weight 400 700`). Download uses Open Runde 400/500/600 and Exposure. All are already in `public/fonts/`.
- **New images (downloaded to `public/assets/`, original names, no conflicts):**
  - `open-download.png` 1448x1086 (original `/download/open-download.png`)
  - `move-to-applications.png` 1448x1086 (original `/download/move-to-applications.png`)
  - `launch-merlin.png` 1449x1086 (original `/download/launch-merlin.png`)
- **Reused images (verified byte-identical to the live originals):** `merlin-dock.png` (`/merlin-dock.png`), `companion.webp`, `meeting-scene.webp`, `hero-beach-reading.webp`, `mark.webp` (all `/story/handmade/*` → `/assets/*`). Footer SVGs are as on the homepage.
- No video or audio on these routes.

---

## 1. Shared components across these routes

| Component | /pricing | /manifesto | /download |
|---|---|---|---|
| Hero corner nav `nav.hero-corner-nav` (brand + Pricing/Manifesto + spring dot), module `63154` | Identical to homepage. `aria-current="page"` on Pricing. Dot rests at `translate(-16px, 41px)` → box `[104,77,6,6]` | Identical. Wrapped in `div.site-container > header.manifesto-navigation` (relative, height 152px; 144px ≤600). `aria-current` on Manifesto. Dot rests at `translate(-16px, 70px)` → `[104,106,6,6]` | **Not used.** Own header (see §3) |
| Homepage hero title (`h1 > span.hero-title-line` + `.hero-title-muted`) | Same classes and CSS, **no load chroma sweep**. The h1 is server-rendered with no `hero-title-chroma` class ever added | No | No |
| `a.download-button` (module `13669`, `href="/download?start=1"`, label "Get Merlin for Mac" + `span.download-arrow` Feather arrow-right) | Plan CTAs: variants `download-button-secondary` (Pro, Max) and `download-button-primary` (Ultra), plus class `pricing-plan-cta` and `aria-label="Get Merlin for Mac — {Plan} plan"`. Footer has the standard primary button | Footer only | No |
| Footer `footer.closing-footer` (module `42077`) | Identical to homepage (clock, birds, beach, links) | Identical | No |
| Floating nav `floating-navigation_nav__y4vuM` | **Absent** (checked at scrollY 1500) | **Absent** | Absent |
| FAQ ask form `form.merlin-faq-form` (module `2292`) | Same component as homepage FAQ: input "What else would you like to know?", `aria-label="Your question about Merlin"`, maxLength 500, submit `aria-label="Ask Merlin"`, POST `/api/faq` (mock it), stop button, "Reading the docs…" shimmer, and the same error strings | No | No |
| Skip link `a.skip-link` | "Skip to plans" → `#plans` | "Read the manifesto" → `#manifesto` | none |

The hero corner nav, footer and download button can be lifted unchanged from the homepage clone (`src/components/hero/HeroNav.jsx`, `Footer.jsx`, `shared/DownloadButton.jsx`). HeroNav needs to know the current path to set `aria-current` and the dot's rest target (`/` → brand, `/pricing` → Pricing link, `/manifesto` → Manifesto link). DownloadButton needs `variant`, `className` and `ariaLabel` props.

---

## 2. /pricing

Title "Plans | Merlin". Meta description: "Choose your Merlin plan: Pro, Ultra, or Max. Your AI assistant for Mac, with room for the work you want to do." The og/twitter tags are the same as the homepage.

**No monthly/annual toggle exists.** The page shows monthly prices only (`section#plans[aria-label="Monthly plans"]`). Annual billing is only mentioned in an FAQ answer.

### 2.1 Structure (1440)
```
main#top.merlin-story.site-layout.pricing-page            [0,0,1440,3550]  doc height 3550 (1280: 3528, 390: 5311)
  a.skip-link[href=#plans] "Skip to plans"
  section.story-hero[aria-labelledby=pricing-title]       [120,0,1200,466]  padding 160 0 96
    nav.hero-corner-nav (shared)                           [120,36,157,84]
    h1#pricing-title                                       [260,160,920,148]
      span.hero-title-line "Make room for"
      span.hero-title-line.hero-title-muted "the rest of your day."
    div.hero-bottom                                        [446,316,549,54]  (no button here)
      p "Your ideas. Your to-dos. Your time back.<br>Choose how much Merlin you need along the way."  [487,316,465,54]
  div.site-container                                       [120,466,1200,2179]
    section#plans.pricing-plans[aria-label="Monthly plans"] [120,466,1200,501]
      div.pricing-plan-grid  (3 x 389.33, gap 16)
        article.pricing-plan.pricing-plan-{sage|lavender|peach}  [120|525.3|930.7, 466, 389.3, 501.5]
          h2 "{Pro|Ultra|Max}"                             [151,495,327,47]
          p.pricing-plan-description                       [151,563,327,84]
          div.pricing-plan-price  <span>$<!-- -->29</span><span>/ month</span>   [151,671,327,48]
          a.download-button.download-button-{secondary|primary|secondary}.pricing-plan-cta  [151,743,327,68]
          div.pricing-plan-details                         [151,836,327,102]
            p > svg(Feather check, polyline "20 6 9 17 4 12") + <span><strong>25,000</strong> credits each month</span>
            p > svg(check) + "All of Merlin, included"
    section.pricing-included[aria-labelledby=included-title]  [120,967,1200,887]
      div.pricing-section-intro                            [120,1103,427,639]
        h2#included-title "All the places<br><span>your day takes you.</span>"   [120,1103,427,108]
        p "The same thoughtful assistant, wherever the work happens. Every plan comes with all of this."  [120,1233,350,82]
      div.pricing-feature-grid (2 x 314.35, gap 48/36)     [655,1103,665,639]
        article x6 > svg(40x40 viewBox, width/height attr 36, CSS forces 40x40) + h3 + p
    section.pricing-faq[aria-labelledby=pricing-faq-title] [120,1855,1200,791]
      div > h2#pricing-faq-title "A few things<br><span>you might be wondering.</span>"  [120,1966,491,94]
      div.pricing-questions                                [731,1966,589,560]
        details x6 > summary "{question}" + svg(Feather plus 20x20) ; p "{answer}"
        form.merlin-faq-form.ph-no-capture > div.merlin-faq-input-row > input + button   [731,2447,589,79]
        div.merlin-faq-response.ph-no-capture[aria-busy]  (empty)
  footer.closing-footer (shared)                           [0,2645,1440,905]
```

### 2.2 Copy (verbatim)
- Plans:
  | Class / accent | Name | Description | Price | CTA variant | Credits |
  |---|---|---|---|---|---|
  | `pricing-plan-sage`, `--accent:#72886c` | Pro | For the replies, research, and little projects that fill your week. | $29 / month | secondary | **25,000** credits each month |
  | `pricing-plan-lavender`, `--accent:#9082b1` | Ultra | For deeper research, bigger projects, and a fuller working day. | $99 / month | **primary** (black) | **85,000** credits each month |
  | `pricing-plan-peach`, `--accent:#c9916c` | Max | For ambitious work and an assistant you turn to throughout the day. | $299 / month | secondary | **250,000** credits each month |
  The second bullet on every plan is "All of Merlin, included". The check icons use `color: var(--accent)`.
- Feature grid (icon = homepage section-label SVG from `6950` module `17712`, key in brackets):
  1. [context] "A little more context." / "Find an email, catch up on Slack, and prepare for your next calendar event."
  2. [browser] "A hand in your browser." / "Book flights, order groceries, and fill out forms in your browser, with your approval."
  3. [companion] "Right where you are." / "Rewrite a reply, explain selected text, or ask about what’s on your screen with Option + Space."
  4. [meeting] "Be there for the meeting." / "Record meetings, get speaker-labelled transcripts, and turn the conversation into notes and next steps."
  5. [project] "From thought to a real thing." / "Create slide decks, spreadsheets, PDFs, and websites you can preview, edit, and share."
  6. [routine] "One less thing to repeat." / "Get a morning briefing, prepare for upcoming meetings, and receive a weekly summary on a schedule."
- FAQ (native `<details>`, all closed initially, several can be open at once):
  1. "Which plan should I choose?" — "Choose based on how much you expect to use Merlin. Pro gives you 25,000 monthly credits for everyday help. Ultra gives you 85,000 for more involved work, and Max gives you 250,000 for frequent use and bigger projects. All three include the capabilities above."
  2. "What are credits?" — "Credits cover Merlin’s AI usage, including model calls and paid tools. The amount a task uses depends on the model, tools, and work involved, so one message doesn’t always use the same number of credits. Follow your balance and recent activity in Settings → Usage."
  3. "Do unused credits roll over?" — "Unused included credits don’t roll over. Your allowance refreshes each month, and you can see your renewal date in Settings → Usage."
  4. "What happens if I run out?" — "When your balance reaches zero, new paid work won’t start. You can check your remaining credits and renewal date in Settings → Usage, and manage your subscription in Settings → Billing."
  5. "Is there an annual option?" — "Yes. Annual subscriptions save 20% on the subscription price. You receive the same monthly credit allowance as the equivalent monthly plan, and credits refresh every month. You can review the annual plan details in the app before subscribing."
  6. "How do I get started?" — "Download Merlin for Mac and follow the setup in the app. Your trial starts with 2,000 credits to explore. You can choose your plan and manage billing in the app."

### 2.3 Typography and color (computed, 1440)
| Role | Font | Size/LH | Weight | Letter-spacing | Color |
|---|---|---|---|---|---|
| Page base `.pricing-page` | Open Runde | 15/24 | 400 | normal | `#242424`, bg `#fff` |
| h1 lines | Exposure, Georgia, serif | 64/67.84 | 400 | -0.64px | `#242424` / muted `#858585` |
| Hero p | Open Runde | 20/27 | 400 | -0.2px | `#737373` |
| Plan name h2 | Exposure | 43/47.3 | 400 | -1.075px (-.025em) | `#242424`, margin-bottom 12 |
| Plan description | Open Runde | 17/27.2 | 400 | normal | `#696966`, margin-top 9, min-height 84, max-width 340 |
| Price amount | Exposure | 48/48 | 400 | -1.92px (-.04em) | `#242424` |
| "/ month" | Open Runde | 16/25.6 | 400 | normal | `#696966`. Price row: flex, baseline, gap 9, margin 24px 0 |
| CTA label | ui-monospace, SFMono-Regular, Menlo, monospace | 14/16.8 | 700 | 0.91px, uppercase | secondary `#242424`, primary `#fff` |
| Plan bullet | Open Runde | 16/25.6 | 400 (strong 600) | normal | `#242424`. Flex, gap 10, margin 10px 0; icon 17x17 |
| Section h2 (`#included-title`) | Exposure | `clamp(34px,3.5vw,48px)` = 48/53.76 | 400 | -1.2px | `#242424`, span `#858585`, margin-bottom 22 |
| FAQ h2 (`#pricing-faq-title`) | Exposure | `clamp(32px,3vw,42px)` = 42/47.04 | 400 | -1.05px | same |
| Intro p | Open Runde | 17/27.2 | 400 | normal | `#737373`, max-width 350 |
| Feature h3 | Open Runde | 20/28 | 500 | normal | `#242424`, margin-bottom 10 |
| Feature p | Open Runde | 17/28.05 (1.65) | 400 | normal | `#737373`, max-width 340 |
| FAQ summary | Open Runde | 18/27 | 400 | normal | `#242424`, padding 26px 0, flex space-between, gap 20 |
| FAQ plus icon | 20x20 | | | | `#737373` |
| FAQ answer | Open Runde | 17/28.9 (1.7) | 400 | normal | `#737373`, padding 0 25px 26px 0 |
| FAQ input | Open Runde | 17/25.5 | 400 | normal | `#333338`, placeholder `#74747c` |

- Plan card: `display:grid; grid-template-rows:subgrid; grid-row:span 5; padding:28px 30px; background:#fff; border:1px solid #c8c8c8; border-radius:12px; box-shadow:5px 5px 0 #d9d9d9`. Subgrid rows keep descriptions, prices, CTAs and details aligned across the three cards.
- `.pricing-plan-details`: `margin-top:25px; padding-top:20px; border-top:1px solid #2424241c`.
- CTA overrides: `#top.merlin-story .pricing-plan-cta{width:100%; justify-content:space-between; gap:12px; padding-left:18px; margin-top:0}`, so 327x68, `border:6px`, radius 22. Secondary: bg `#fff`, border `#e2e2e2`, `::before` `#e2e2e2`, arrow `#242424`. Primary: bg `#000`, border `#000`, `::before` `#73e7f5`.
- `.pricing-included`: grid `.9fr 1.4fr` (427.3 / 664.7), gap 9%, padding `136px 0 112px`. `.pricing-feature-grid`: padding-top 3, row gap 48, column gap 36. Feature icon `display:block; 40x40; margin-bottom:18px; overflow:visible`.
- `.pricing-faq`: `border-top:1px solid #e8e8e8`, grid `1fr 1.2fr` (490.9 / 589.1), gap 10%, padding `110px 0 120px`. Each `details` has `border-bottom:1px solid #e8e8e8`, and the first also has a top border. Summary marker hidden. Input row as on the homepage: `padding:26px 0; border-bottom:1px solid #e6e6e9`, focus-within `#2798a8`.
- Focus ring: `outline:2px solid #12889a; outline-offset:6px` on links and summaries.

### 2.4 Responsive
- **1280:** container `[107, w 1067]`. Cards 345 wide (`[107|468|828, 466, 345, 501]`), inner 283. `.pricing-included` 379.8 / 590.8, `#included-title` 44.8/50.18 (151 tall, wraps to 3 lines). Feature cols 277.4. FAQ cols 436.4 / 523.6, h2 38.4/43.0. Footer as on the homepage at 1280 (starts y 2701). Doc height 3528.
- **≤1000:** card padding 24px 20px, description min-height 86, included gap 6%, feature gap 32/22.
- **≤700 (390 measured):** `.pricing-plan-grid` is a single column with gap 18. Cards are `display:flex; flex-direction:column; padding:24px 27px`, 358x468 at y 444 / 930 / 1416. Description min-height 0 (2 lines, 54 tall). Price margin 26px 0. `.pricing-included` is one column, gap 40, padding 76px 0 (`[16,1883,358,1593]`), h2 40/44.8. Feature grid is one column, gap 36. `.pricing-faq` is one column, gap 35, padding 70px 0 (`[16,3476,358,878]`), h2 36/40.32. Hero as on the homepage at 390: `.story-hero` padding 136 8 64, h1 48.75/51.675 (165 tall, 3 lines), p 17/22.95. Nav 13px links, 16px brand, dot hidden. Footer starts at 4355. Doc height 5311. Root font-size 8.16px.

### 2.5 Motion and interaction
- No entrance or scroll animations on pricing-specific content (`getAnimations()` only returns the footer birds). No floating nav.
- Hero nav: dot spring and brand sweep exactly as on the homepage (`CLONE_SPEC.md` §3 Motion). Spring `{stiffness:170,damping:15,mass:.8}`, axis y, bend -8, lead 10, size 6. Its rest target is the Pricing link. On resize it re-snaps to that link.
- CTA hover/focus: `::before` slides from `translateX(calc(100% - 56px))` to `0` over `.55s cubic-bezier(.22,1,.36,1)`. Text color transitions over `.36s`. Measured while hovering the secondary button: `::before` matrix(…,0,0), bg `#e2e2e2`, text stays `#242424`, border `#e2e2e2` (a grey wipe). The primary does the cyan wipe and turns the text black, as on the homepage.
- FAQ details: when open, the plus SVG rotates 45deg (`transition: transform .2s`). The open/close of the content is native and not animated. An open `details` for Q1 is 222.6px tall.
- FAQ ask form state machine is the same as the homepage (`pricing-page…js` module `2292`): idle → submit (trimmed, non-empty) → `loading` (input disabled, button becomes Stop `aria-label="Stop answering"`, `p.merlin-faq-loading > span.merlin-faq-shimmer "Reading the docs…"`) → answer `p.merlin-faq-generated` (17px/1.7 in pricing) or `p.merlin-faq-error[role=alert]`. Stopping shows "Stopped. You can edit your question and ask again."
- `prefers-reduced-motion`: `.pricing-page *, :before {transition:none; scroll-behavior:auto}`.

---

## 3. /download and /download?start=1

Title "Download Merlin for Mac". Meta description: "Get Merlin for Mac. Open your download, move Merlin to Applications, and open the app." Canonical `https://www.merlin.computer/download`. The route uses **no** homepage chrome: no `#top`, no hero nav, no footer.

### 3.1 Structure (1440). Doc height 1000 (min-height 100vh), 1280: 966, 390: 1795
```
main.install-page                                    [0,0,1440,1000]  bg #fafaf7, padding 0 6vw 72px (86.4px)
  header.install-header                              [86,0,1267,100]  max-width 1280, height 100, flex space-between, centered vertically, 14px
    a.install-brand[href=/] > img(merlin-dock 30x30, alt "") + "merlin.computer"   [86,35,152,30]  gap 10
  section.install-intro                              [295,164,850,292]  margin 64px auto 72px, max-width 850, centered text
    h1#install-title "Thanks for choosing Merlin.<br><span>Here’s how to get started.</span>"  [295,164,850,140]
    p.install-description                            [435,326,570,54]
    p.install-retry "Download not starting? " + a[target=merlin-installer] "Download Merlin again"  [295,402,850,22]
    p.install-alternative > a[target=merlin-installer] "Download for Intel Macs"   [295,435,850,21]
    iframe.install-download-frame[name=merlin-installer][title="Merlin installer download"]  display:none
    noscript > p "Choose <a>Apple Silicon</a> or <a>Intel</a> to download Merlin."
  ol.install-steps                                   [120,528,1200,400]  grid 3 x 380, gap 30, max-width 1200, list-style none
    li x3:
      div.install-step-heading > span "01" + h2 "Open your download"           [120,528,380,32]  margin-bottom 17
      div.install-art > img (aspect 4/3, cover)       [120,577,380,285]
      p (with <strong>)                               [150,882,320,46]
```
Step copy (verbatim; bold parts in **):
1. "01" / "Open your download" / "Find the Merlin **.dmg** file in your **Downloads** folder and double-click it." Image `open-download.png`.
2. "02" / "Move to Applications" / "Drag the **Merlin icon** into the **Applications** folder beside it." Image `move-to-applications.png`.
3. "03" / "Open Merlin" / "Open **Merlin** from Applications, and sign in to get started." Image `launch-merlin.png`.

All three images have `alt=""`, `width 1448 height 1086`, `sizes="(max-width: 620px) 90vw, (max-width: 1400px) 30vw, 380px"`, quality 90. Each is drawn at 378x283 inside a 1px border.

Description text by state:
- default/`ready`/`requested`: "Your download will start automatically. Follow these steps to finish installing Merlin."
- `other-device` (non-Mac or touch device): "Merlin is made for Mac. Open this page on your Mac to get started."

### 3.2 Typography and color
| Role | Font | Size/LH | Weight | LS | Color |
|---|---|---|---|---|---|
| Base `.install-page` | Open Runde | 16/25.6 | 400 | normal | `#262626` on `#fafaf7` |
| Brand link | Open Runde | 14/22.4 | 600 | normal | `#73736f`. Because the brand is the header's only and therefore last child, it matches `.install-header>a:last-child`. No underline |
| h1 | Exposure | `clamp(42px,4.5vw,66px)/1.08` = 64.8/69.98 | 400 | -.035em = -2.268px | `#262626`, span `#777b70`, margin-bottom 22 |
| Description | Open Runde | 17/27.2 | 400 | | `#75756e`, max-width 570, margin 0 auto 22 |
| Retry line | Open Runde | 14/22.4 | 400 | | `#75756e`. Link `#303e33`, weight 500, underline offset 4px, thickness 1px |
| Alternative line | Open Runde | 13/20.8 | 400 | | `#8b8b83`, margin-top 10. Link `#686c61` underlined |
| Step number | `monospace` | 12/12 | 500 | | `#777b70`. 32x32 circle, `1px solid #dddfd5`, grid centered |
| Step h2 | Open Runde | 16/22.4 | 500 | | `#262626` |
| Step p | Open Runde | 14/23.1 (1.65) | 400 | | `#83847c`, centered, max-width 320, margin 20px auto 0. Strong 500 `#4c5245` |
| Art box | | | | | bg `#f4f4f0`, `border:1px solid rgba(80,90,75,.12)`, radius 16, overflow hidden |

Focus ring: `3px solid #57899b`, offset 6px, radius 3px.

### 3.3 Responsive
- ≥1500: intro margin 85px top/bottom.
- **1280:** padding 0 76.8. Header `[77,0,1126,100]`. h1 57.6/62.21, ls -2.016 (124 tall). Intro `[215,164,850,276]`. Steps `[77,512,1126,382]`, columns 355.47, art 355x267. Doc height 966.
- ≤900: page padding 0 5vw 64px, steps gap 18, step heading gap 8, h2 14px, intro margin-top 40.
- **≤620 (390 measured):** page padding 0 19.5px 64px. Header height 80, 12px (brand text 11px through the `:last-child` rule, brand box `[20,25,128,30]`). Intro margin 40 auto 45 (`[20,120,351,351]`). h1 42/45.36, ls -1.47 (181 tall, 4 lines). Description 15/24, max-width 310. Steps single column, gap 40, max-width 360 (351 measured), each li 378 tall at y 516 / 934 / 1352. Step h2 back to 16px, heading gap 8. Art 351x263. Doc height 1795.

### 3.4 Behaviour (`download-page-bb533f8a3eddd657.js`, module `3991`)
State: `arch` (`"arm64"` by default), `status` ∈ `ready | requested | other-device`, plus refs `iframeRef` and `started`.
1. On mount, `isMac(navigator)` = not `/iPhone|iPad|iPod|Android/` AND `maxTouchPoints <= 1` AND (`userAgentData.platform === "macOS"` OR UA matches `/Macintosh|Mac OS X/`). If not a Mac, set `status="other-device"` (description text changes) and do nothing else.
2. On a Mac, detect the architecture: `navigator.userAgentData.getHighEntropyValues(["architecture"])` raced against a **600 ms** timeout. `"arm"` → `arm64`, `"x86"` → `x64`, anything else or a timeout → `arm64` (detected:false). Safari/Firefox have no userAgentData, so they default to arm64.
3. Set `arch`. If the URL has `?start=1` and the download has not started yet: set `started=true`, delete `start` from the URL with `history.replaceState(history.state, "", pathname+search+hash)` so the URL becomes `/download`, set **`iframe.src = https://download.merlin.computer/mac/latest?arch={arch}`** (the hidden iframe performs the download), set `status="requested"`, and fire analytics `website_download_requested {architecture, architecture_detected, trigger:"automatic"}`.
4. Without `?start=1` (plain /download), nothing downloads. The copy still says "Your download will start automatically".
5. Links: "Download Merlin again" → `href = latest?arch={arch}`. "Download for Intel Macs" / "Download for Apple Silicon" shows the *other* arch (`arch==="arm64"` → x64 label "Download for Intel Macs"). Both use `target="merlin-installer"` (they load into the hidden iframe, so the page stays put). onClick sets `arch` to the clicked arch, `status="requested"`, and fires `trigger:"manual"`.
- **Measured live** (iframe `src` setter intercepted so no binary was fetched; Playwright UA is macOS, arch `arm`): navigating to `/download?start=1` caused one `replaceState("/download")` and one `iframe.src = "https://download.merlin.computer/mac/latest?arch=arm64"` within about 1 s. There is no redirect and no visible UI change. A `HEAD` on that URL returns **302** → `https://download.merlin.computer/mac/0.1.14/merlin.computer-0.1.14-mac-arm64.dmg` (x64 → `…-mac-x64.dmg`).
- **Clone recommendation:** reproduce the state machine but point the iframe and links at a stub (e.g. keep the real URL behind a flag, or use `about:blank`) so local testing never fetches the DMG. Keep the `history.replaceState` removal of `start`.
- No animations or transitions on this page apart from link underlines. Nothing animates on load or scroll.

---

## 4. /manifesto

Title "The Merlin manifesto". Meta description: "Why we’re building Merlin: an AI assistant for your Mac that helps across your apps, browser, meetings, and projects, giving you more time for life." og/twitter tags are the same as the homepage.

**Copy policy:** the essay paragraphs are not reproduced here. Headings, mention labels and the signature are given verbatim. For paragraphs, use placeholder text of the listed word count. The four Caveat handwriting overlays (2, 2, 4 and 4 words) are part of the essay's art direction. Take their exact text from `reference/pages/manifesto.html` (classes `manifesto-handwriting-time`, `manifesto-handwriting-back`, `manifesto-handwritten-note` x2) if the owner approves, otherwise use placeholders of the same word count.

### 4.1 Structure (1440). Doc height 7913 (1280: 7446, 390: 5536)
```
main#top.merlin-story.site-layout.manifesto-page                 bg #fff, color #171717
  a.skip-link[href=#manifesto] "Read the manifesto"
  div.site-container > header.manifesto-navigation (relative, h 152)   [120,0,1200,152]
    nav.hero-corner-nav (shared; aria-current on Manifesto)
  article#manifesto.manifesto-poster (overflow hidden, padding-bottom 110)  [0,152,1440,6855]
    section.manifesto-poster-opening (relative, padding 220 0 230)        [0,152,1440,1091]
      div.manifesto-handwriting.manifesto-handwriting-time [aria-hidden]  [167,66,900,449]   2 words, Caveat
      div.manifesto-poster-copy                                           [360,372,720,641]
        h1#manifesto-title "Less managing.<br>More living."             [360,372,720,146]
        p  P1 — 22 words, 3 lines  (DYNAMIC: part "opening", time-of-day)
        p  P2 — ~35 words, 5 lines; fixed lead-in with 2 inline mentions [meeting](section icon) and [document](artifact pdf), then a DYNAMIC "interruption" tail
      div.manifesto-handwriting.manifesto-handwriting-back                [248,868,1172,470]  2 words
    figure.manifesto-photo > img companion.webp                           [280,1291,880,587] r24
       alt "Merlin sitting comfortably in an armchair with a laptop in a sunlit room."
    section.manifesto-poster-understanding (relative, padding 120 0 100) [0,1878,1440,1414]
      div.manifesto-poster-copy (shifted left: margin-left calc(50% - 440px))  [280,1998,720,1037]
        h2#manifesto-understanding-title "We know that day.<br>We’ve lived it too."
        p  P3 — 30 words, 4 lines (static)
        p  P4 — 30 words, 5 lines (static)
        p  P5 — 36 words, 6 lines (static), 1 mention [meeting]
      span.manifesto-handwritten-note                                     [432,3045,576,180]  4 words
    figure.manifesto-photo > img meeting-scene.webp                       [280,3340,880,587]
       alt "Merlin sharing tea and a conversation with a friend at a sunny garden studio table."
    section.manifesto-poster-action (relative, padding 120 0 100)        [0,3926,1440,1175]
      div.manifesto-poster-copy (shifted right: margin-right calc(50% - 440px))  [440,4046,720,798]
        h2#manifesto-action-title "And there it is.<br>A little room."
        p  P6 — 34 words, 5 lines (static), 1 mention [browser]
        p  P7 — 37 words, 6 lines (DYNAMIC part "return"), 3 mentions [deck] [spreadsheet] [website] (artifact icons)
      span.manifesto-handwritten-note                                     [420,4854,600,183]  4 words
    figure.manifesto-photo > img hero-beach-reading.webp                  [280,5149,880,587]
       alt "Merlin enjoying a book under a beach umbrella beside the sea at sunset."
    section.manifesto-poster-ending (padding 130 0 30)                    [0,5736,1440,1162]
      div.manifesto-poster-copy                                           [360,5866,720,695]
        p  P8 — 34 words, 4 lines (static)
        p  P9 — 36 words, 5 lines (DYNAMIC part "finish")
        h2#manifesto-ending-title "Your time.<br>Yours to spend."           [360,6416,720,146]  margin-top 50
      div.manifesto-signature                                             [563,6609,314,273]
        span.manifesto-circled-yours "Yours" + svg[viewBox 0 0 180 90, preserveAspectRatio none] > path[pathLength=1]
        ", Merlin"
        img.manifesto-signature-mark mark.webp (148x148, alt "")         [644,6712,163,163] (rotated box)
  footer.closing-footer (shared)                                          [0,7007,1440,905]
```
- Paragraphs have no `strong`, `em` or `a` and there are no pull quotes. The only inline decoration is `span.manifesto-mention`. Total: 9 paragraphs, about 294 words at the time measured (afternoon variant).
- Mentions (`span.manifesto-mention` = icon + the word): `kind` browser/meeting → `<svg viewBox="0 0 40 40" width=36 height=36>` section icon (`6950` module `17712`, `D({section})`). Other kinds → `span.story-artifact-icons > svg` (module `77159`, `n({type})`, with `document` mapping to type `pdf`). Label words: "meeting", "document", "meeting", "browser", "deck", "spreadsheet", "website". The icon is `1em` square (36px at 1440) with `margin-right:.12em; vertical-align:-.14em`, and the mention is `white-space:nowrap`.
- Signature path `d="M155 17C126 1 55 6 22 28C-9 49 6 77 61 80C115 84 172 62 175 37C177 20 157 10 134 9"`.

### 4.2 Typography and color (1440)
| Role | Font | Size/LH | Weight | LS | Color / other |
|---|---|---|---|---|---|
| h1 / h2 (`#top .manifesto-poster h1,h2`) | Open Runde (`var(--font-open-runde)`) | `clamp(38px,4.4vw,64px)/1.15` = 63.36/72.86 | 600 | -.025em = -1.584px | `#171717`, margin 0 0 48, `text-wrap:balance`, centered |
| Body p | Open Runde | `clamp(23px,2.55vw,36px)/1.45` = 36/52.2 | 500 | -.01em = -0.36px | `#242424`, `text-wrap:pretty`, `p+p` margin-top 30 |
| Handwriting overlay | Caveat, cursive | `clamp(160px,24vw,380px)/.8` = 345.6/276.48 | 500 | -.065em = -22.46px | `#12889a`, absolute, `left:50%`, `width:max-content`, nowrap, pointer-events none, user-select none |
| `-time` overlay | | | | | `top:0; transform:translateX(-62%) rotate(-12deg)` |
| `-back` overlay | | | | | `bottom:2px; transform:translateX(-40%) rotate(-10deg)` |
| Handwritten note | Caveat | `clamp(55px,8vw,112px)/1` = 112/112 | 500 | -.04em = -4.48px | `#12889a`, block, `width:fit-content; max-width:90%; margin:45px auto 0; rotate(-7deg)` |
| Signature | Caveat | 64/64 | 500 | normal | `#12889a`, `margin:62px auto 0; rotate(-6deg); width:fit-content` |
| Signature mark img | | | | | width 148, `margin:32px auto 0; rotate(12deg)` |

- Copy column `.manifesto-poster-copy`: `position:relative; z-index:1; width:min(90%,720px); margin-inline:auto; text-align:center`. Text sits above the handwriting overlays, which run behind and under the h1/paragraphs (see the screenshot: the overlays cross the title).
- `.manifesto-photo`: `width:min(82%,880px); margin:48px auto 0`. Img `width:100%; height:auto; border-radius:24px`. Rendered 880x586.7. Sources are 1774x? webp (served at w=1080/3840 by next/image). Use `/assets/{companion,meeting-scene,hero-beach-reading}.webp`, lazy.
- Circled "Yours": span relative inline-block. SVG absolute `width:142%; height:140%; left:-21%; top:-13%; overflow:visible; transform:rotate(-10deg)`. Path `fill:none; stroke:currentColor; stroke-width:1.8; stroke-linecap:round; vector-effect:non-scaling-stroke; stroke-dasharray:1; stroke-dashoffset:1`.

### 4.3 Responsive
- **1280:** h1/h2 56.32/64.77 (ls -1.408). p 32.64/47.33. Handwriting 307.2px. Notes 102.4px. Copy column 720 (opening x 280; understanding x 200; action x 360). Photos x 200, 880 wide. Opening `[0,152,1280,1036]`, understanding y 1823 (h 1220), action y 3678 (h 1096), ending y 5408 (h 1101), signature `[483,6221,314,273]`, footer y 6619. Doc height 7446. Paragraph line counts 3,5,4,4,5,5,6,4,5.
- ≥1600: opening padding 280 0 290.
- ≤1023: copy `width:min(82%,660px)`, side-shifted columns re-centered, opening padding 200/210, understanding/action padding 90 0 70.
- **≤600 (390 measured):** `.manifesto-navigation` h 144. Poster padding-bottom 75. Opening padding 120 0 135 (`[0,144,390,774]`). Handwriting `clamp(76px,23vw,138px)` = 89.7/71.76 (ls -5.83). `-time` `top:5px; translateX(-50%) rotate(-10deg)`. `-back` `bottom:18px; translateX(-50%) rotate(-8deg)`. Copy column `calc(100% - 48px)` = 342 at x 24. h1/h2 36/41.4, margin-bottom 32. p 23/34.5 (ls -0.23), `p+p` 25. Photos `calc(100% - 48px)` = 342x228, radius 16, margin-top 32. Understanding/action padding 60 0. Notes 55px, margin-top 30. Ending padding 70 0 10. Signature 52px, margin-top 42 (`[68,4293,255,214]`). Mark 112 wide, margin-top 26. Footer y 4580. Doc height 5536. Paragraph line counts 4,7,5,6,8,7,8,6,7.

### 4.4 Motion and behaviour (`manifesto-page-3b4268b2ba0b8b84.js`)
- **Time-of-day copy (module `10256`, component `s({part})`):** rendered three times with `part = "opening"` (P1 + P2), `"return"` (P7) and `"finish"` (P9). It picks a variant set from `new Date().getHours()`:
  - `5 ≤ h < 12` morning
  - `12 ≤ h < 17` afternoon (measured)
  - `17 ≤ h < 22` evening
  - otherwise night, with a separate `opening` string for `h < 5` vs 22–23.

  Each set has `opening`, `interruption`, `returnToIdea` (the same 6-word sentence in all sets) and `finish`. Before mount (`state null`) it renders time-neutral fallback strings (SSR output). The choice is recomputed every **60 000 ms** (`setInterval`) and on `visibilitychange`. Placeholder word counts per variant (opening / interruption / finish): morning 21 / 18 / 32; afternoon 22 / 19 / 36; evening 22 / 19 / 33; night 28 (h<5) or 24 / 18 / 35; fallback 19 / 18 / 34. The builder can port the strings from the saved chunk if the owner clears the copy.
- **Signature circle draw (module `50047`):** an IntersectionObserver with `threshold: 0.5` on `.manifesto-signature`. On the first intersection it adds `is-visible` and disconnects. CSS: `.manifesto-signature.is-visible .manifesto-circled-yours path{animation:manifesto-circle-draw 1.6s ease-in-out forwards}` with `@keyframes manifesto-circle-draw{0%{stroke-dashoffset:1}to{stroke-dashoffset:0}}`. Verified live: the class is added once the element is 50% in view, and the path ends at dashoffset 0. Reduced motion: `animation:none; stroke-dashoffset:0`.
- Hero nav dot and footer as shared (§1). No floating nav, parallax or other scroll effects. The only other running animations are the footer birds.

---

## 5. Things not measurable or intentionally not captured
- `/api/faq` answers on pricing (server LLM); stub it.
- The real download binary was never fetched. The behaviour was verified by intercepting `HTMLIFrameElement.prototype.src` during a client-side navigation to `/download?start=1`, plus a `HEAD` request for the redirect target.
- The `other-device` branch of /download was not triggered live (Playwright's UA is macOS). It is documented from source.
- The manifesto essay text is intentionally omitted (copy policy). It is present only in `reference/pages/manifesto.html` and the saved chunk.
