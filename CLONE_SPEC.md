Source: https://www.merlin.computer/

# Merlin homepage clone spec (React 18 + Vite + Tailwind v3)

Measured live with Playwright on 2026-10-07 at 1440x900, 1280x800 and 390x844 (Chromium). All values are computed styles or `getBoundingClientRect()` results. Box notation is `[x, y(document), w, h]` in CSS px at 1440 unless stated otherwise.

Companion files:
- Asset manifest: `/Users/riyaghosh/V3/merlin/ASSET_MANIFEST.json` (every font/image/audio file, original path, local path, dims, where used).
- Reference screenshots: `/Users/riyaghosh/V3/merlin/reference/full-1440.png` (1440x11899 full page), `full-390.png`, `viewport-1440-hero.png`, `viewport-1440-browser-card2-doordash.png`, `viewport-1440-browser-mid-transition.png`. Note: in the full-page captures the pinned browser section shows pin-spacer artifacts (empty grey band), which is a screenshot artifact, not a real layout gap.
- Hydrated live DOM (exact markup, class names, inline SVGs): `/Users/riyaghosh/V3/merlin/reference/live-dom-1440.html` (outerHTML of `main#top`, 153 KB).
- Original component source (minified Next.js chunks, contains all copy, state machines, timings): `/Users/riyaghosh/V3/merlin/reference/source/`. `page.split.js` is the homepage chunk split one function per line; line numbers are cited below as `page.split.js:L`. Hero nav, download button, section labels, artifact icons and footer live in `6950-9e48fb1cb1316049.js`.
- Icon SVGs (Feather, Ionicons5, Simple Icons) keyed by minified id: `/Users/riyaghosh/V3/merlin/reference/icons.json`.
- Original compiled CSS (identical hashes to what the live page loads): `/Users/riyaghosh/V3/merlin/Merlin — Your AI assistant for Mac_files/*.css`.

## 0. Build strategy (strongly recommended)

The page is driven almost entirely by roughly 500 KB of hand-written class-based CSS plus React state machines. Re-deriving it in Tailwind utilities would not be pixel-faithful. Instead:

1. **Use the original CSS verbatim.** Copy these files into `src/styles/original/` and import them in this order (this is the live `<link>` order):
   `357da7cf10d68108.css` (root font-size, @font-face) → `437c25afc566ca52.css` (Mantine; only its first ~6 base rules matter: `*,:after,:before{box-sizing:border-box}`, `button,input,select,textarea{font:inherit}`, `body{margin:0;...}`, so you can copy just those rules plus the `:root` Mantine vars) → `e2e0ba86a6b0d559.css` → `4a4d88752d2165c6.css` → `6385c293c5638848.css` → `f46c55d95248097e.css` → `a5f02e9d0c6db7af.css` → `401561448b81938e.css` → `922109019b2259fa.css` → `0a5b07db1896be06.css` → `fc1769f629488e8f.css` → `f7c0a2656765fcca.css` → `ea3e27f6a69b5df4.css` (contains the footer birds/closing rules even though it is named for the blog).
   Also add the inline `:root{--mantine-font-family:var(--font-open-runde),sans-serif;--mantine-font-family-headings:var(--font-open-runde),sans-serif}`.
2. **Rewrite `url()`s.** The only non-data URLs in these files are: `/fonts/Exposure.woff2`, `/fonts/open-runde-{400,500,600,700}.woff2`, `/fonts/Caveat.ttf` (these already match `public/fonts/`), `/_next/static/media/3c6a8fcb177aeedf-s.p.ttf` → `/fonts/3c6a8fcb177aeedf-s.p.ttf`, and `/footer-bird-ascii.svg`, `/footer-bird-ascii-slow.svg`, `/footer-bird-ascii-fast.svg`, `/footer-beach-ascii.svg` → `/assets/<same name>`. JSX `src`s must be rewritten per ASSET_MANIFEST (`/brand-logos/x` becomes `/assets/x`, `/browser/x` becomes `/assets/x`, `/story/handmade/x` becomes `/assets/x`, `/story/launch-deck/review/0N-name.png` becomes `/assets/launch-deck-0N-name.png`).
3. **Disable Tailwind preflight** (`corePlugins: { preflight: false }`) or import the original CSS after `@tailwind base`. Preflight's `img{display:block}`/`h*{font-size:inherit}`/border resets fight the original rules. The original CSS already ships its own reset.
4. **Rebuild the DOM with the exact same class names / element hierarchy** as `reference/live-dom-1440.html`, porting behavior from `reference/source/page.split.js`. Root: `<main class="merlin-story site-layout" id="top">`. Most selectors are `#top ...` or `#top.merlin-story ...`, so the id and both classes are mandatory.
5. **Dependencies to add:** `framer-motion` (the site bundles motion; uses `motion.*`, `AnimatePresence`, `useScroll`, `useTransform`, `useInView`, `useSpring`, `useMotionValue`, `layoutId`) and `gsap` + `ScrollTrigger` (browser-tasks pinned deck). Icons can be inlined from `reference/icons.json` or replaced with `react-icons` (`fi`, `io5`, `si`).
6. `prefers-reduced-motion: reduce`: every animation has a reduced-motion branch in CSS (`animation:none`, `transition:none`) and JS (hook `useReducedMotion` = `matchMedia('(prefers-reduced-motion: reduce)')`). Keep both.

## 1. Global tokens

### Fonts (all downloaded to `/Users/riyaghosh/V3/merlin/public/fonts/`)
```css
@font-face{font-family:Exposure;src:url(/fonts/Exposure.woff2) format("woff2");font-display:swap;font-weight:100 900}
@font-face{font-family:Open Runde;src:url(/fonts/open-runde-400.woff2) format("woff2");font-weight:400;font-display:swap}
@font-face{font-family:Open Runde;src:url(/fonts/open-runde-500.woff2) format("woff2");font-weight:500;font-display:swap}
@font-face{font-family:Open Runde;src:url(/fonts/open-runde-600.woff2) format("woff2");font-weight:600;font-display:swap}
@font-face{font-family:Open Runde;src:url(/fonts/open-runde-700.woff2) format("woff2");font-weight:700;font-display:swap}
@font-face{font-family:Caveat;src:url(/fonts/Caveat.ttf) format("truetype");font-display:swap;font-weight:400 700}
/* next/font instance actually used for the handwritten notes (inline style fontFamily on those spans): */
@font-face{font-family:caveat;src:url(/fonts/3c6a8fcb177aeedf-s.p.ttf) format("truetype");font-display:swap;font-weight:400 700}
@font-face{font-family:caveat Fallback;src:local("Arial");ascent-override:128.40%;descent-override:40.12%;line-gap-override:0.00%;size-adjust:74.77%}
:root{--font-open-runde:"Open Runde"}
```
- Stacks: sans = `"Open Runde", sans-serif`; serif = `Exposure, Georgia, serif` (`--serif`); handwriting = `caveat, "caveat Fallback"` (set via inline `style={{fontFamily:"caveat, 'caveat Fallback'"}}` on `.context-routine-note > span`, `.story-bridge > span`, `.companion-context-title`); mono CTA = `ui-monospace, SFMono-Regular, Menlo, monospace`; Photoshop/Slack demo chrome = `-apple-system, system-ui, "Segoe UI", sans-serif`; mock browser pages = Arial (Georgia for "fresh market" logo).
- Preloaded: Open Runde 400, Exposure, caveat ttf. Loaded on homepage: Exposure, Open Runde 400/500/600, caveat. Open Runde 700 and `Caveat` are declared but not used.

### Root / body
- `:root{font-size:62.5%}` (10px). Media: `max-width:62.5em` → 56.25%, `max-width:56.25em` → 54%, `max-width:37.5em` → 51% (8.16px measured at 390), `min-width:112.5em` → 75%. Only the floating nav (rem-based) depends on this.
- `html{scroll-behavior:smooth;scroll-padding-top:35px}`; `body{background:#fff;-webkit-font-smoothing:antialiased}`; `::selection{background:#94d8ff;color:#fff}`.
- `.merlin-story`: `color:#2b3027 (--ink)`, `font: 15px/1.6 "Open Runde"` (computed 15px/24px), `overflow:clip`, `background:#fff`. `#top` overrides `--ink:#242424; --muted:#737373; --line:#ebebeb`. Product tokens: `--product-ink:#242424; --product-muted:#696969; --product-border:#e6e6e6; --product-surface:#f5f5f5; --product-paper:#fafaf9; --product-shadow:0 1px 3px #00000005,0 16px 36px -24px #00000024`.
- `.merlin-story em{font-style:normal}`; `.merlin-story img{display:block;max-width:100%}`; links inherit color, no underline; focus ring `2px solid #58959d` offset 5px.

### Container system
- `.site-layout{--site-content-width:83.333333%;--site-content-max:1440px}`; `.story-hero` and `.site-container`: `width:var(--site-content-width);max-width:1440px;margin-inline:auto`. `@media (max-width:1023px)` width becomes 91.666667%.
  - 1440: content 1200px at x=120. 1280: 1067px at x=107. 390: 358px at x=16.
- Story sections (`#routines`, `#meetings`, `#companion`): `max-width:1600px`, side margin 4% (57.6px at 1440, 51px at 1280, 9.75px at 390), `background:#fff`. `#routines` and `#companion` are 12-column grids, column-gap 24px (88.4px columns at 1440). Below 700px they become `display:block` with padding 80px 16px.
- Full-bleed bands: `#browser` (bg `#f6f6f6`), `#privacy` (bg `#000`), `#faq` (bg `#fff`, padding 180px 72px, at 1280 180px 64px, at 390 112px 24px), `footer.closing-footer` (bg `#e6e6e6`).

### Breakpoints used in the CSS
380, 399, 420, 430, 540, 560, 600, 640, 699/700, 760, 767/768, 800, 900, 999/1000, 1023/1024, 1050, 1100, 1400, 1450, 1600, 1700 px; plus `(hover:hover)` and `(prefers-reduced-motion:reduce)`. The most used: `max-width:699px` (20 blocks), `max-width:700px` (14), `min-width:1000px` (12), `max-width:767px` (11), `768–1023` (8).

### Color palette (computed)
| Role | Value |
|---|---|
| Ink primary | `#242424` rgb(36,36,36) |
| Muted heading line | `#858585` (hero), `#868682` (section em) |
| Body muted | `#737373`, `#747471`, `#85858b`, `#777777` |
| Story ink (meetings) | `#252922` |
| Companion heading ink | `#172d3b` |
| Accent cyan (handwriting, notes) | `#20b8cf` rgb(32,184,207) |
| CTA cyan fill | `#73e7f5` rgb(115,231,245) (also `.handoff-title-highlight-green` bg) |
| Orange highlight | `#ff9e53` |
| Hero nav dot | `#00c8e0` |
| Selection blue (companion) | bg `#c5e8fc`, handles `#079bea` |
| Privacy eyebrow | `#50c7d8` |
| Privacy text | heading `#f5f5f7`, accent line `#a1a1a8`, copy `#aaaab1`, card h3 `#d9d9df`, card p `#92929b` |
| FAQ | heading `#29292e`, accent `#85858b`, question `#333338`, answer `#666670`, divider `#e6e6e9`, chevron `#92929a` |
| Footer | bg `#e6e6e6`, ink `#292d27`, copyright `#74786e` |
| Notification badge | `#ff3b30` |
| Card borders | `#e4e4e7`, `#d5d5d5`, `#d6d6d6`, `#e9e9eb` |

## 2. Page structure (DOM order, 1440 boxes)

Document height: 11899 (1440), 11605 (1280), 12841 (390).

```
main#top.merlin-story.site-layout                         [0,0,1440,11899]
  a.skip-link[href=#routines] "Skip to product examples"  fixed, translateY(-180%) until :focus
  section.story-hero                                       [120,0,1200,554]
  section.hero-life.hero-landscape                         [120,554,1200,835]
  section.companies                                        [0,1429,1440,231]
  section#routines.story-section.routines-section.story-context [58,1660,1325,2173]
  section#browser.browser-showcase                         [0,3913,1440,1778]  (900 stage + 878 pin spacer)
  section#meetings.story-section.meetings-section.projects-section.story-handoff [58,5691,1325,1645]
  section#companion.story-section.companion-section       [58,7336,1325,1876]
  section#privacy.privacy-scene                            [0,9232,1440,957]
  section#faq.merlin-faq                                   [0,10189,1440,805]
  footer.closing-footer                                    [0,10994,1440,905]
  nav.floating-navigation_nav__y4vuM (conditional, fixed)  [535,804,370,46] viewport coords
```
Component order from source: `sd()` = Layout(v) > Hero(er) > Companies(el) > Routines/context(ex) > Browser(eA) > Meetings+Projects(e9) > Companion(e1) > Privacy(si) > FAQ(sl) > Footer(42077) > FloatingNav(f).

---

## 3. Section: Hero (`section.story-hero` + `section.hero-life`)

### Layout
- `.story-hero`: padding `160px 0 96px` (390: `136px 8px 64px`), relative, text centered.
- `nav.hero-corner-nav` (absolute, `top:36px; left:0`, flex column, gap 8px, 14px/1.5): `[120,36,157,84]`.
  - `a.hero-site-name.hero-site-brand` (inline-flex, gap 8px): `img.hero-site-icon` 20x20 (`/assets/merlin-dock.png`, object-fit contain) + `span.hero-site-name` "merlin.computer" (17px/25.5px, 600, letter-spacing -0.425px (-.025em), `#242424`).
  - `div.hero-corner-links` (flex column, gap 8px, color `#737373`): "Pricing" → `/pricing`, "Manifesto" → `/manifesto` (14px/21px 400). Hover/current: `#242424`.
  - `span.hero-nav-dot`: absolute 6x6, radius 50%, `#00c8e0`, sits 16px left of the active link, vertically centered on it (measured `[104,46,6,6]`). Hidden ≤767px. At 390: nav top 24px, 13px links, 16px site name.
- `h1` (aria-label "Your time. Yours again."): `max-width:920px; margin:0 auto; line-height:1.06`; Exposure 64px/67.84px, 400, letter-spacing -0.64px. Box `[260,160,920,148]`.
  - `span.hero-title-line` "Your time." color `#242424`; `span.hero-title-line.hero-title-muted` "Yours again." color `#858585`. Both `display:block; padding-bottom:.2em; margin-bottom:-.2em; text-wrap:balance`.
  - Sizes: 768–1023 `clamp(50px,6vw,56px)`; ≤767 `clamp(40px,12.5vw,64px)` (48.75px at 390, line-height 51.675px).
- `div.hero-bottom` (flex column, centered, gap 20px, margin-top 20px, max-width 549px) `[446,316,549,142]`:
  - `p` "Meet Merlin. Your AI assistant for the things you need to do, giving you time back for the things you’d love to." Open Runde 20px/27px, -0.2px, `#737373` (390: 17px/22.95px, -0.17px).
  - `a.download-button.download-button-primary[href="/download?start=1"]` 288x68 `[576,390,288,68]`.

### Download button (shared by hero and footer)
- `display:flex; align-items:center; justify-content:space-between; gap:26px; padding:0 0 0 26px; min-height:68px; border:6px solid #000; border-radius:22px; background:#000; color:#fff; font:700 14px/1.2 ui-monospace,SFMono-Regular,Menlo,monospace; letter-spacing:.065em (0.91px); text-transform:uppercase; overflow:hidden; isolation:isolate; position:relative; transition:color .36s ease`.
- Label `span` "Get Merlin for Mac" (z-index 1). `span.download-arrow`: 56x56 grid, `border-radius:0 16px 16px 0`, transparent bg, color `#000`, contains Feather arrow-right (`dyV` in icons.json) 24x24 stroke-width 2.
- `::before`: `content:""; position:absolute; inset:0; background:#73e7f5; transform:translateX(calc(100% - 56px)); transition:transform .55s cubic-bezier(.22,1,.36,1)`. So at rest only the right 56px (the arrow cell) is cyan.
- Hover/focus-visible: `::before` goes to `translateX(0)` (cyan wipe right→left across the whole pill), text color becomes `#000` (.36s). Focus ring `2px solid #000`, offset 4px.

### Hero landscape (`section.hero-life.hero-landscape`)
- `[120,554,1200,835]`; `height:clamp(740px,58vw,900px)` (835 at 1440, 742 at 1280, 800 fixed ≤767); `border-radius:36px` (24px ≤767); `background:#ece3c7`; `overflow:hidden; isolation:isolate`; margin-bottom 40px.
- `img.hero-photo` `/assets/quiet-lakeside.webp` (1774x887), `object-fit:cover; object-position:40% center` (24% ≤767), alt "A woven pastel lakeside landscape with a small sailboat, willow trees, and lavender hills at sunset". Rendered box `[78,509,1284,894]` because of the inline `scale(1.07)` parallax (see Motion).
- `div.hero-notifications` (absolute inset 0, z 3, white text):
  - `div.hn-workspace` absolute centered (grid, gap 28px, width 960px, `translateX(-50%)`), `div.hn-stack` 420px wide.
  - `button.hn-card` (notification): `width:100% - 4.5%*depth; left:2.25%*depth; top:12px*depth` for stacked ones. Style: `display:flex; gap:12px; padding:16px 18px; border:1px solid rgba(255,255,255,.24); border-radius:26px; background:linear-gradient(135deg,#ffffff14,#ffffff00 60%),rgba(32,33,28,.52); backdrop-filter:blur(36px) saturate(1.35); box-shadow:0 14px 36px -16px #0e181a66, inset 0 1px 0 #ffffff26`. Measured 401x75. Children: `.hn-icon` 40x40 radius 12px (merlin-dock.png), `.hn-title` 14px/19.6px 600 -0.35px white, `.hn-description` 13px/18.85px 400 -0.195px `rgba(255,255,255,.78)`, Feather chevron `.hn-open-arrow`.
  - Notification copy (in order): 1 "Your 10am meeting brief is ready." / "Sophie’s notes, in one place."; 2 "Your launch deck has a first draft." / "Six slides, ready to review."; 3 "I drafted your reply to Sophie." / "Launch dates and next steps, ready for review."
  - `span.hn-counter` red badge 26x26 `#ff3b30`, 13px 600, top -10px right -7px, shadow `0 2px 5px rgba(0,0,0,.08)`, opacity 0 when 0 unread.
  - `div.hn-controls` absolute `left:24px; right:24px; bottom:24px`, space-between: two pill buttons (`height 38px; padding:0 13px; gap 7px; border-radius:999px; background:rgba(248,248,245,.78); border:1px solid rgba(255,255,255,.5); backdrop-filter:blur(20px); 12px 500 #383c36`): left "Sound off"/"Sound on" (Feather volume-x / volume-2), right "Replay" (Feather rotate-ccw).
  - Clicking a card opens `div.hn-detail-shell` with a `section.notification-detail` (radius 26px, bg `rgba(255,255,253,.97)`), content per id: meeting brief, launch deck slider (6 PNG slides, see manifest), email draft with Send button. Full markup and copy in `page.split.js:21-31`.

### Motion
- **Headline chroma sweep (load):** both title lines get class `hero-title-chroma` on mount, removed after 1500ms (`setTimeout 1500`). CSS: `background-image:linear-gradient(90deg,var(--headline-ink) 0,var(--headline-ink) 33.33%,#c679c4 40%,#fa3d1d 45%,#ffb005 50%,#e1e1fe 55%,#0358f7 60%,var(--headline-ink) 66.67%,var(--headline-ink)); background-size:300% 100%; -webkit-background-clip:text; -webkit-text-fill-color:transparent; animation:hero-wordmark-sweep 1.5s cubic-bezier(.4,0,.2,1) forwards` with `@keyframes hero-wordmark-sweep{0%{background-position:100% 0}to{background-position:0 0}}`. `--headline-ink` is `#242424` / `#858585` (muted line).
- **Site-name sweep (hover/focus):** hovering the brand link adds `hero-site-sweep` to `span.hero-site-name` for 900ms; same gradient with `#242424`, `animation:hero-wordmark-sweep .9s cubic-bezier(.4,0,.2,1) forwards`. The footer wordmark does the same, cleared on `animationend`.
- **Nav dot:** framer springs `{stiffness:170, damping:15, mass:.8}`; moves along y to the center of the hovered/focused link, with a perpendicular "bend" offset of up to -8px (min(|bend|, 0.14*distance)) shaped as `4n(1-n)` over travel progress and scale `1 + .35*4n(1-n)`; returns to current-page link (`/` brand) on mouseleave. Lead offset 10px, size 6.
- **Hero photo parallax:** `useScroll({target: section.hero-life, offset:["start end","end start"]})`, `y = useTransform(progress,[0,1],["-3%","3%"])`, constant `scale:1.07` (inline `transform: translateY(-1.8%) scale(1.07)` at scrollY 0, reaching `translateY(3%)` by ~1700px).
- **Notifications sequence:** starts when the `.hero-notifications` region is ≥60% in view (`useInView amount .6`) and tab visible: first card after 180ms, next ones every 430ms (3 total). Each arrival is a FLIP animation via Web Animations API: new card starts 32px+2% height higher, at 96% size, and springs into place (critical-damped curve, stiffness 620, 480ms; 560ms for the detail panel; 500ms for counter), opacity 0→1 over 130ms ease-out; content counter-scales. Older cards slide behind (`hn-card-behind`, contents hidden, 12px offsets). Optional sound (button): two sine pings 880Hz and 1174.66Hz, 95ms apart, gain ramp to .055 in 12ms, decay to 0.0001 by 480ms. Replay resets. Exact engine: `page.split.js:31-44`. A simpler acceptable approximation is a framer `layout` spring `{stiffness:620,damping:~50}` with initial `{y:-32, scale:.96, opacity:0}`.

---

## 4. Section: Companies (`section.companies`)
- `[0,1429,1440,231]`, padding `58px 24px 72px` (390: `40px 24px 48px`).
- `p.companies-heading` "Used by professionals at": flex centered, gap 24px, margin-bottom 32px, Open Runde 16px/24px `#202124` (390: 14px/21px). `::before`/`::after` are 1px-high hairlines `#c6c6c3`, 64px wide, flanking the text.
- `div.companies-logos` `[160,1543,1120,45]`: flex, centered, `gap:28px 44px`, max-width 1120px, `opacity:.48; filter:grayscale(1)`, color `#000`. Logos in order: `img /assets/notion.svg` (width=160 height=56, rendered 96x36), inline SVG Salesforce (122x25 viewBox), `img /assets/harvard.svg` (164x48 attrs, rendered 96x36), inline SVG HubSpot (84x26), inline SVG McKinsey & Company (125x42). Inline SVG markup is in `reference/live-dom-1440.html` (search `aria-label="Salesforce"`). At 390 the row wraps (box `[24,1385,342,83]`).
- Motion: none.

---

## 5. Section: Context + Routines (`section#routines`)

Grid: 12 cols x 88.4px, column gap 24px, padding 130px 0, rows 228 / 554 / 1131px at 1440.

### 5a. Heading "First, a little [app tiles] context."
- `h2#context-heading` (aria-label "First, a little context.") `[170,1790,1212,164]`: Exposure 64px/65.92px, -1.28px, `#242424`, margin-bottom 64px. Line 1 text "First, a little".
- `span.context-heading-line` (flex, gap 24px, margin-top 18px): `span.context-apps` (flex, gap 10px) with 6 tiles, then `em` "context." color `#868682`.
- Each `span.context-app-tile > span`: 80x80 (78px grid), `background:#fff; border:1px solid #d5d5d5; border-radius:22px; box-shadow:0 5px 12px rgba(0,0,0,.016)`; img 25x25 nominal (rendered 42x42, notion 48x48). Order: gmail, calendar, slack, notion, granola, linear (title attrs = names). Tiles transition `background .18s, border-color .18s, transform .18s` (hover lift per CSS).
- At 390: heading 25.35px/27.885px (6.5vw), tiles 31x35, radius 9px.

### 5b. Copy column `div.portfolio-context-copy` `[1069,2062,313,510]` (margin-top 44px)
- `p` (16px/26.4px, `#747471`): "The conversation is in [slack icon 14px] Slack. The plan is in [notion icon 17px] Notion. [SH avatar] Sophie’s email is in your [gmail icon 18px] inbox." Inline identities are `span.context-inline-identity`. `span.context-inline-initials` "SH": 24x24 circle, `background:linear-gradient(145deg,#77777d,#444449 55%,#27272b)`, 9px 600 white, `box-shadow: inset 0 1px 1px rgba(255,255,255,.19), 0 1px 2px rgba(0,0,0,.082)`, margin-right 5px, top -1px.
- `p` "Connect the tools you use, and Merlin can help you bring it all together." (14px gap above).

### 5c. Gmail preview card `div.context-connections > div#context-source-preview.context-source` `[410,2053,620,519]`
- Card: `max-width:620px; background:#fff; border:1px solid #e4e4e7; border-radius:20px; box-shadow:3px 4px 0 #e4e4e7; overflow:hidden`.
- `header.context-source-header` (bg `#f5f5f6`, padding 10px 23px): gmail icon 20 + "Gmail" (12px 600 `#3f3f46`).
- `div.context-email-toolbar` (padding 12px 25px, color `#85858b`): "← Inbox" (12px 500 `#626269`), tool icons (archive, trash, more), divider, "Reply" pill (11px 500).
- `article.context-email`: subject `h3.context-email-title` "A quick catch-up before launch" (15px/21px 600 -0.525px `#303036`) + "Inbox" chip (10px `#8a8a92`); author row: 34x34 avatar "SH" (same gradient), "Sophie Hayes" (13px 600 `#303036`), "<sophie@commonground.example>" (11px `#98989f`), "9:41 AM" (10px). Body paragraphs 14px/24.5px `#52525b`: "Hi Amira," / "The launch is looking good. Can we talk through the deck before next Friday?" / "I’ve added my notes to the project page. It would be great to see the latest website direction alongside the slides, so we can make sure everything tells the same story." / "Does Monday at 10 work for you and Leo? We can use the time to agree on the last few details before October 9." / "Thanks!<br>Sophie".
- Motion: `.context-source-content{animation:context-source-arrive .18s cubic-bezier(.22,1,.36,1) both}`, keyframes `0%{opacity:0;transform:translateY(4px)} to{opacity:1;transform:translateY(0)}`.

### 5d. Routines row `div.routine-columns` `[58,2772,1325,931]` (3 cols x 403px, gap 57.6px, margin-top 200px)
- `div.story-section-label.story-section-label-routine` (absolute, top -144px): 36x36 SVG icon (purple clipboard-clock; SVG in `6950` chunk / live DOM) + "Routines" (17px/22.1px 600, letter-spacing .025em, `#27272b`, gap 11px). This label component is reused: Browser tasks (blue), Meetings (cyan), Projects (orange), Companion (pink).
- `div.context-routine-note` (absolute, top -88px, color `#20b8cf`): caveat 44px/50.6px 600 "Then, make it a routine." + 70x70 hand-drawn arrow SVG (viewBox 0 0 112 86, stroke currentColor).
- `p.routine-intro-copy` (max-width 280px, margin-top -12px) 15px/25.5px `#85858b`: "Tell Merlin what needs doing, and when. It’ll take it from there."
- `div.routines-workspace-wrap` (column 2, `transform:translate(-120px,40px)` at 1440 from CSS) containing `div.routine-timeline` (14px/21px `#66666b`, padding `20px 12px 24px 30px`):
  - Eyebrow "⏱ Every Friday · 4:00 pm" (11px `#8b8b92`) + right-aligned button "Pause" / "Resume" / "Replay" (11px, padding 6px 8px, radius 6px, `#77777f`).
  - `ol.rt-feed`: vertical line + nodes. Node `span.rt-node` 28x28 circle, padding 5px, `background:#faf7ff; color:#8655da; border:1px solid #e4e4e7; box-shadow:0 0 0 4px #fff`, left -43px. Entries (`li.rt-entry`, padding-bottom 22px):
    1. ⚡ "Weekly studio update started" (13px 500 `#38383e`) + "4:00 pm" (11px `#a0a0a6`).
    2. Gmail "Find this week’s project emails" → result "1 conversation found", 0.8s, result card "Launch review" / "Sophie Hayes → Amira" / "The website direction looks good. Let’s review the deck alongside the latest designs on Monday."
    3. Gmail "Read the launch review conversation" → "4 messages read", 0.4s.
    4. Notion "Find the Common Ground project" → "1 project found", 0.6s.
    5. Notion "Read the project notes" → "3 updates collected", 0.5s.
    6. Calendar "Check the next project meeting" → "1 meeting found", 0.3s.
    7. ⚡ "Pulling decisions and loose ends together" + "Working…" spinner → "Done".
    8. Final card (blue node) `article.rt-card.rt-final-update`: h4 "Your Friday update, ready." + badge "✓ Prepared for you"; p "The website direction is approved, and Leo’s first designs are ready for a look."; ul: "Review the deck with Sophie and Leo on Monday at 10." / "Give the final launch copy one more read." / "Choose a flight for the client visit on October 9."; sources row: gmail, notion, calendar 15px icons + "Based on the emails, project notes, and calendar above".
  - Tool label 13px/20.8px 500 `#494950`; status 11px `#9a9aa2`; `.rt-card`: padding 17px 19px, `border:1px solid #e9e9eb; border-radius:14px; box-shadow:0 2px 5px rgba(24,24,27,.024)`; h4 14px/20.3px 500 -0.21px `#28282d`; small 10px `#a0a0a6`; p 13px/21.45px `#77777f`.
- `figure.routine-intro-quote` (col 3) `[979,2772,403,500]`: `img /assets/studio.webp` 403x403 (`aspect-ratio:1/1; object-fit:cover`, margin-bottom 20px, lazy) + `figcaption` Exposure 17px/25.5px `#55554f`: "From morning briefings to Friday updates, set a routine once. [inline Merlin mark SVG] Merlin keeps it moving, so you have one less thing to remember."
- At 390 the columns stack: label, note, copy, timeline (339 wide), then the quote figure (264 wide, margin-left 74px).

### Motion (routine walkthrough, `page.split.js:48-51`)
- Plays only while `.routine-timeline` is ≥10% in view, tab visible, not paused. Step counter `r` from 0 to 12 (`2*5+2`). Delay before advancing: step 0 → 200ms; odd steps (tool "running") → that tool’s duration (800/400/600/500/300ms); even steps → 120ms; step 11 → 480ms. Tool i is `is-visible` once step ≥ 2i+1 (`is-running`, spinner) and `is-complete` at ≥ 2i+2 (check + duration text). Only the first tool shows its result card.
- CSS: `.rt-sequence{opacity:0;visibility:hidden;transform:translateY(5px);transition:opacity .18s ease-out, transform .22s cubic-bezier(.23,1,.32,1), visibility .18s}` → `.is-visible{opacity:1;visibility:visible;transform:none}`. Final card durations `.22s,.28s,.22s`. Status text swap: `.14s ease-out` opacity + `.18s` transform. Spinner `@keyframes rt-spin{to{transform:rotate(1turn)}}` `.8s linear infinite`, paused in `.rt-paused`.
- Measured: rtVisible went 0 → 1 → 2 → 3 → 4 as scroll passed 2100–3300px, and paused when it left view.

---

## 6. Section: Browser tasks (`section#browser.browser-showcase`, GSAP pinned)

### Layout
- `section` bg `#f6f6f6`, margin-top 80px, total height 1778 = 900 (stage) + 878 (pin spacing).
- `div.bs-boundary` (content width, 1200px) > `div.bs-stage`: `height:100svh; min-height:620px; display:grid; grid-template-columns:1fr 1fr; align-items:center; gap:8%; padding:60px 4% 80px; overflow:hidden` (live override: `width:100%; padding-left/right:4%`). At 1440: columns 507.8px each.
- `div.bs-copy` (z 4) `[168,4210,508,285]`: section label "Browser tasks" (blue icon), `h2#browser-showcase-heading` "If it happens in a browser,&nbsp;" + `span` "Merlin can help." — Exposure 46.08px/51.61px (3.2vw), -1.152px, `#202022`, span `#a0a0a3` (1280: 40.96px; 390: 30px/33.6px). `p[aria-live]` (margin-top 25px, max-width 340px) 14px/23.8px `#929296` (390: 12px/20.4px) with the active brand inline (`span.bs-inline-brand` `#505554`, logo 16px):
  - 0 Qatar Airways: "I can help you compare flights on [Qatar Airways] and find the right one for your trip."
  - 1 DoorDash: "I can help you find lunch on [DoorDash] and get an order ready that everyone will love."
  - 2 Instacart: "I can help you tick off your grocery list on [Instacart] and get your basket ready for checkout."
  - 3 Ashby: "I can help you fill out your application on [Ashby] so it’s ready for you to review and submit."
- `div.bs-deck` `[780,4115,476,476]`: `aspect-ratio:1/1; max-width:570px; position:relative`. Four `div.bs-card-slot` (absolute inset 0, `transform-style:preserve-3d`, `::after` = `linear-gradient(180deg,#f0f0f0,#e7e7e7)` with `opacity:var(--step-opacity)` and `translateZ(1px)` — this is the grey "folded" card face seen above/below the active card), each holding `article.bs-card.bs-card-N` (absolute inset 0, `padding:7%`, radius 32px (24px ≤999px), flex column space-between).
  - Card backgrounds: 0 Qatar `linear-gradient(165deg,#eadde5,#f0e4e6 55%,#dac0cf)`, brand color `#5c0632`; 1 DoorDash `#ffe9c0`, brand `#505554`; 2 Instacart `#cfeef2` (card text `#17474d`, brand img gets white bg radius 4px padding 2px), brand `#23727c`; 3 Ashby `linear-gradient(150deg,#ece5fc,#ded6f3)`, brand `#554383`.
  - `div.bs-card-brand` (12px 500, gap 8px, logo 21px) + `div.bs-preview-size` (height `0.77*width`) containing `div.bs-preview.browser-section` at fixed `width:800px` scaled `scale(width/800)` (0.5115 at 1440) → `div.browser-frame` (`background:#fff; border:1px solid #e6e6e6; border-radius:12px; box-shadow:0 1px 3px #00000005, 0 16px 36px -24px #00000024`) with `div.bs-mini-toolbar` (traffic lights, lock + url, more; 9px `#8d8d93`, bg `#fbfbfb`) and the mock site. Mock site markup/copy for Qatar (`ef`), DoorDash (`ey`), Instacart (`ew`), Ashby (`ek`) is in `page.split.js:53-57`; all are interactive (flight select, restaurant select/favorite/search, quantity steppers with subtotal, Overview/Application tabs and autofill). They use Arial.
- `div.bs-pagination` (absolute right 12px, vertically centered, column gap 4px): 4 buttons 20x20 with 3x3 dots `#353539`; active has `aria-current="step"` (CSS enlarges it). Click scrolls to that card’s label position (`window.scrollTo` instant).
- At 390: stage `min-height:650px; grid-template-columns:1fr; grid-template-rows:auto 1fr; gap:22px; padding:36px 9% 80px`, deck 317x317.

### Motion (GSAP, `page.split.js:60-64`)
- Under `matchMedia('(prefers-reduced-motion: no-preference)')`: timeline with `scrollTrigger:{trigger: section, pin: .bs-stage, start:"top top", end: "+=" + max(320, 0.325*innerHeight*3), scrub:true, anticipatePin:1, invalidateOnRefresh:true, snap:{snapTo:"labelsDirectional", inertia:false, delay:.1, duration:{min:.12,max:.25}}}` (end = +877.5px at 900px tall viewport). Labels `card-0..card-3` at t=0..3, default `{duration:1, ease:"none"}`.
- Slot pose for offset `d = slotIndex - activeIndex`:
  - `d=0`: `{yPercent:0, rotateX:0, scaleX:1, scaleY:1, opacity:1, zIndex:4, "--step-opacity":0}`
  - `d≠0`: `{yPercent: sign(d)*(63 + (|d|-1)*9), rotateX: 62*sign(d), scaleX: .94 - (|d|-1)*.06, scaleY: .26, opacity: |d|===1 ? 1 : .58, zIndex: 3-|d|, "--step-opacity":1}`, `transformOrigin:"50% 50%"`.
  - Each segment tweens every slot from pose(i, k-1) to pose(i, k).
- On landing exactly on a card (|progress - round| < .005) the active `.bs-card` gets a bump: `to {y: 9*direction, scale:.985, duration:.1, ease:"power2.out"}` then `to {y:0, scale:1, duration:.7, ease:"elastic.out(1, 0.5)"}`. The copy paragraph and pagination switch to `Math.round(progress*3)`.
- Measured: stage `position:fixed` between scrollY 3913 and 4791; snapping resolved scroll targets to 4206 (card 1), 4499 (card 2), 4791 (card 3). After the pin the stage has `translateY(878px)`.
- Inactive cards get `inert` + `aria-hidden`.
- Reduced motion: stage becomes auto height single column, cards stacked statically, pagination hidden.

---

## 7. Section: Meetings + Projects (`section#meetings`)

`padding:180px 0 130px` (390: 80px 16px), color `#252922`.

### 7a. Intro `div.story-pair-intro` (12-col grid, gap 24px, margin-bottom -140px)
- `h2#handoff-heading` `[395,5871,988,136]` Exposure 64px/67.84px -1.28px `#252922`: "One [google-meet.png 44x44, zoom-camera.svg 44x44 in span.story-meeting-logos (gap 7.68px, img radius 8.96px)] conversation.<br><em>Something to [3 artifact icons: pdf, spreadsheet, deck SVGs, each 49.9px] show for it.</em>" (em color `#868682`). Artifact icon SVGs: `77159` module in `6950` chunk (also in live DOM).
- `div.story-meeting-intro-copy` (max-width 460px, margin-top 100px) `[922,6131,460,152]`, 16px/26.4px `#747471`: "Focus on your call with [SH] Sophie. Merlin takes care of the notes and next steps." / "Then turn your ideas into [pdf icon] PDFs, [deck icon] decks, [sheet icon] spreadsheets, and [website icon] websites. All from the same conversation."

### 7b. Grid `div.story-pair-grid` (2 cols x 585px, gap 6%, padding 0 39.74px)
**Left `article.story-meeting-panel`** `[97,6143,585,1014]`
- `header` (margin-bottom 26px): label "Meetings" (cyan icon); `h3` Exposure 29px/34.8px -0.58px: "Be there for the call. " + `span.handoff-title-highlight.handoff-title-highlight-green` "Merlin handles the notes." (bg `#73e7f5`, white text, padding `0 .06em .03em`); `p` 15px/24px `#777777`, max-width 460px: "Record with Merlin. After the call, come back to what you decided and what happens next."
- `div.meeting-landscape` `[97,6358,585,798]`: padding `70px 24px 48px`, bg `#b5c6d8`, radius 24px, `::after` overlay `linear-gradient(rgba(225,232,239,.02), rgba(41,55,79,.07))`; `img.meeting-landscape-art` `/assets/meeting-scene.webp` absolute cover, `object-position:46% 50%`, z -2, lazy.
  - `div.transcript-window` `[121,6428,537,680]`: `padding:0 7px 7px; background:rgba(225,229,238,.4); border:1px solid rgba(255,255,255,.88); border-radius:23px; backdrop-filter:blur(16px); box-shadow:0 22px 44px -14px rgba(36,51,75,.35), inset 0 1px 0 rgba(255,255,255,.75)`. Chrome bar 46px with 3 window dots.
  - `div.transcript-paper` (bg #fff, radius 18px, padding 19px 22px 15px): toolbar with Meet icon 18px + avatars (meeting.webp "Sophie", companion.webp "Leo", 28px) and a segmented `div.transcript-switch` (196x37, bg `#f2f2f0`, border `#e9e9e7`, radius 11px, padding 3px; tabs "Transcript" / "Notes" 11px 500; white sliding pill radius 8px, shadow `0 1px 3px rgba(0,0,0,.07), 0 0 0 1px rgba(0,0,0,.016)`). Default tab: **Notes**.
  - Heading `h3` Exposure 28.8px/34.56px -0.8px `#46473f` "Launch catch-up" + span "Monday, October 5" (Exposure 16px `#afada5`); participants line "• Amira, Sophie & Leo · Google Meet" (12px, strong 600 `#464b42`).
  - Notes panel (`div.transcript-body`, 320px tall, overflow auto): h4 "Meeting summary" (16px 600 -0.32px `#353832`); paragraphs 15px/24px -0.15px `#74786f` (copy in `page.split.js:88`); h4 "Key decisions" + 3 bullets with bold leads ("Keep the scope small." / "Tell one story." / "Review before Friday."); "Action items" + "0 of 3 done" counter; 3 toggleable `button.transcript-task` (title 15px 500, detail 14px/22.4px, meta "Amira · Thu, Oct 8" 13px `#777e70`). Transcript tab: 3 lines (Amira 2:14, Sophie 2:23, Leo 2:31) with text in source.
  - `div.transcript-player` (margin-top 22px, padding 14px 16px, radius 16px, `linear-gradient(#fafaf9,#f5f5f3)`, border `#eaeae6`): 40px round play button (`linear-gradient(#414440,#2c2e2b)`, border `#282a28`), waveform of 64 bars 2px wide, heights `5 + (13*i+3) % 17` px, color `#d7d9d2` (played bars darker), playhead, range input, times "0:00" / "2:05" (11px 500 .165px). Plays `/assets/merlin-introduction.mp3` (125.8s).
**Right `article#projects.story-project-panel`** `[757,6408,585,798]`: margin-top 265px, padding `32px 28px 28px`, `background:#fff; border:1px solid #e4e4e7; border-radius:24px`, flex column.
- header: label "Projects" (orange icon); h3 "You bring the ideas. " + `span.handoff-title-highlight-orange` "Merlin brings them to life." (bg `#ff9e53`, white); p "Reports, spreadsheets, decks, and websites. Everything you need to move the project forward, together in one place."
- `div.project-folder-grid` (1 col, rows 106px, gap 16px), 4 `figure.project-folder-item` (`padding:14px 22px 14px 16px; border:1px solid #d6d6d6; border-radius:12px; box-shadow:2px 3px 0 #d6d6d6`, gap 14px): 54px capsule icon, figcaption strong 18px/27px 600 `#41423d` + span 13px/19.5px `#898275`, and a 96x76 `div.project-folder-art` with three tilted sheets (front sheet bg `#fafaf7`, border `#e0dfd9`, radius 9px, rotate ~14deg, small caps label 4px, title Exposure 12px `#646a5a`):
  1. Launch report.pdf · "6 pages · Edited 2 hours ago" · sheet "COMMON GROUND" / "Launch report" (rose)
  2. Launch budget.xlsx · "3 sheets · Edited 2 hours ago" · "BUDGET / OCTOBER" / "Launch budget" (green, 12-cell grid)
  3. Studio website.html · "Website · Edited yesterday" · "COMMON GROUND STUDIO" / "A fresh start." (blue)
  4. Launch deck.pptx · "12 slides · Edited yesterday" · "THE LAUNCH STORY" / "Good things ahead." (amber)
- At 390 the two panels stack (meeting panel 339 wide; landscape padding 40px 13px 28px, radius 18px; project panel padding 26px 18px, radius 18px).

### Motion
- Transcript tab pill: framer `animate={{x: tab===0 ? "0%" : "100%"}}`, spring `{stiffness:550, damping:38, mass:.7}`. Panel content enters `initial {opacity:.4, y:3}` → `{opacity:1,y:0}`, `.16s`, ease `[.23,1,.32,1]`.
- Play/pause icon crossfade: `.16s`, opacity + scale .6↔1 + `blur(3px)`. Play button `transition: transform .16s cubic-bezier(.23,1,.32,1), box-shadow .16s`. Wave bars `background .12s`.
- Project items hover (only `(hover:hover) and (prefers-reduced-motion:no-preference)`): front sheet `rotate(17deg) translate(18%,1%)`, back sheet `rotate(-16deg) translate(-10%,-9%)`, `transition: transform .3s ease`.
- Section sets `--meeting-card-height` from the landscape height (ResizeObserver).

---

## 8. Section: Companion (`section#companion`)

12-col grid, padding `160px 0 130px`, color `#2b3027`. Rows 436 / 227 / 923px at 1440.

### Layout
- `p.story-bridge.story-bridge-handwritten` (flex, gap 10px, color `#20b8cf`, translated to start at x=58): caveat 44px/50.6px 600 "And when you’re working somewhere else…" + 86x76 arrow SVG.
- Section label "Companion" (pink sparkle icon) at `[507,7600]`.
- `div.companion-selection-ui` `[507,7658,547,274]`:
  - `h2#companion-title.companion-selected-title` Exposure 64px/80px -0.64px `#172d3b` (390: 25.35px/31.69px): two `span.companion-selected-line` "No need to leave" / "what you’re doing." styled as a text selection: `display:inline-block; padding:0 .035em .12em; background:#c5e8fc`; `::before` = 2px-wide caret bar `#079bea` (radius 2px) on the start/end edges, `::after` = 10px round handle `#079bea`.
  - `div.companion-selection-popover` (margin-top 28px, centered): `padding:5px; background:linear-gradient(#35363b,#242529); border:1px solid rgba(255,255,255,.14); border-radius:999px; box-shadow:0 8px 30px rgba(20,22,29,.15), inset 0 1px 0 rgba(255,255,255,.05)`; buttons 16px/20.8px 500 `#f6f6f8`, padding 8px 13px: "[Merlin mark] Ask Merlin" | divider | "Rephrase word". Hover bg transition `.18s`.
- `div.companion-introduction` (max-width 460px, margin-top 55px) `[844,7987,460,172]` 16px/26.4px -0.16px `#737373`: "That sentence doesn’t sound quite like you. Highlight it and ask [Merlin icon] Merlin for another version. Put it back when it feels right." / "Or ask about a [chrome 22px] webpage, a file in [finder 22px] Finder, or what’s on your [screen icon] screen, with your permission." (`.companion-inline-icon` 22x22 radius 6px, margin-right 4px).
- `figure.portfolio-companion-person` `[58,7656,313,503]` margin-top 160px: `img /assets/companion.webp` (aspect 4/5, cover, 313x391, lazy) + figcaption Exposure 17px/25.5px `#55554f` "A second pair of eyes.<br>Right when you need one."
- `div.portfolio-companion-stage` (grid col 2/12, margin-top 75px) `[170,8254,1100,848]`:
  - `div.companion-context-note` (flex centered, gap 8px, color `#20b8cf`): `h3.companion-context-title` caveat 40px/50px 500 -0.6px, rotated -2deg (matrix .9994,-.0349), text per tab: Photoshop "Removing a background in Photoshop." / Slack "Rewriting a reply in your own words." / Chrome "Turning an article into ideas to try."; + 82x78 arrow SVG.
  - `div.companion-showcase` `[170,8342,1100,760]`: `padding:40px; background:#f5f5f7; border:1px solid #e5e5e7; border-radius:28px` (390: padding 16px, radius 20px).
    - `div.companion-example-panel[role=tabpanel]` > `button.companion-detail-toggle` ("See the details"/"Fit the screen", hidden at desktop, shown on mobile) + `div.companion-stage` > demo.
    - Demo viewport `.slack-demo-viewport`: 1018x606 at 1440 (`aspect-ratio:840/500`), bg `#282828`, radius 12px, `box-shadow:0 0 0 1px rgba(0,0,0,.08), 0 1px 3px rgba(0,0,0,.02), 0 16px 36px -24px rgba(0,0,0,.14)`. Inner scene is laid out at 840x500 and scaled by `clientWidth/840`.
    - `div.companion-switch` (margin-top 24px, flex centered gap 16px): tablist with 3 tabs (40px tall, padding 0 16px, radius 22px, 13px/20.8px 500; selected `#1d1d1f`, others `#6e6e73`; icon 20px): Photoshop, Slack, Chrome. White sliding indicator `span.companion-app-indicator` (radius 22px, shadow `0 1px 4px rgba(0,0,0,.05)`). Right: 40x40 round pause/play/replay button (`#e9e9ec`, icon `#515154`) portaled into `.companion-footer-playback`.
- Demos (full scene markup in `page.split.js:74-79`): Photoshop (menu bar, options bar, tools, rulers, artboard with `/assets/mark.webp`, contextual task bar, Properties/Layers panel, status bar), Slack (workspace "Common Ground", channels, 3 messages, composer), Chrome (tabs, omnibox `fieldnotes.example/journal/a-little-room-to-focus`, article "A little room to focus."). Each has a scripted cursor and a Companion overlay.

### Motion
- **Rephrase word:** cycles headline pairs `["No need to leave","what you’re doing."] → ["Stay in your flow.","Help is right here."] → ["Keep your focus.","Help comes to you."]`. After the first click every character is a `span.companion-typed-character` with `animation-delay: (index)*28ms` and CSS `opacity:0; white-space:pre; animation:companion-type-in 1ms step-end forwards` (`@keyframes companion-type-in{to{opacity:1}}`), so text types in at 28ms per char across both lines. "Ask Merlin" smooth-scrolls `.portfolio-companion-stage` to center.
- **Stage entrance (`eL` wrapper):** framer `initial {opacity:1, y:20}` → `whileInView {y:0}`, `viewport {once:true, amount:.15}`, `transition {duration:.75, ease:[.22,1,.36,1]}` (measured: translateY(20px) until ~7500px scroll, then none).
- **Context title:** each word `motion.span` `initial {opacity:0, y:8, rotate:-2}` → `{opacity:1,y:0,rotate:0}`, `duration .35, delay .055*wordIndex, ease "easeOut"`; arrow path `pathLength 0→1`, `duration .65, delay .2`. Re-runs on tab change (keyed).
- **Tab indicator:** framer `layoutId` spring `{stiffness:380, damping:32}`; tab text color `.18s ease`.
- **Demo engine `eR(duration)`:** a 40ms `setInterval` clock that only runs while the demo viewport is ≥15% in view and the tab is visible; `t` advances by real elapsed ms. When `t` reaches the duration the panel auto-advances to the next tab (cyclic). Durations: Photoshop 22000ms, Slack 17000ms, Chrome 18500ms. Shared spring for overlays `{type:"spring", stiffness:440, damping:34, mass:.8}`; cursor moves `.55–.6s` (ease `[.22,1,.36,1]` for Photoshop).
  - Photoshop: 2000ms hotkey hint "Open Companion ⌥ space" fades in (`.2s`); 3200ms Companion panel (`initial {opacity:0,y:12,scale:.96}`); prompt "how do i remove this background?" types from 3800ms at 65ms/char; 6700ms screen-permission card "Mind if I take a look at your screen?" / "I’ll capture the screen you’re looking at so I can answer properly. Nothing is captured unless you approve." / "Take a look" (pressed at 9900ms) / "Not now"; 10400ms screenshot chip + white capture flash (`opacity .14→0, .5s`); "taking a look…" (pulsing ellipsis `demo-pulse 1s ease-in-out infinite`, 50% opacity .4); answer types from 12200ms at 22ms/char: "click remove background in the bar below your artwork. photoshop adds a mask, so you can bring back any edges it misses."; 15800ms footer; 16200ms "Remove background" button gets `is-guided`; 18700ms background fades (`.75s`) and button reads "✓ Background removed". Captions: "Artwork open in Photoshop" / "Asking how to remove the background" / "Waiting for screen permission" / "Approved screenshot attached" / "Reviewing the tool instructions" / "Background removed in Photoshop". Cursor: (510,335) → 9600ms (520,311) → 11200ms (785,364) → 17200ms (357,424).
  - Slack: draft "hey sophie, the launch deck is ready for friday. can you take a look at the opening before our call?"; selection highlight grows from 1400ms at `(t-1400)/9`% ; 2900–4400ms pill "Ask Merlin | Make it clearer"; 4400ms Companion, prompt "make this a little warmer" types from 4900ms at 65ms/char; 6900ms thinking; 8200ms answer types at 10ms/char "Hi Sophie! The launch deck is ready for Friday. Could you take a look at the opening before our call? I’d love to hear what you think."; 10400ms footer "Insert in Slack ⌘⏎"; 12500ms draft replaced, hint "Draft ready. Nothing sent." Cursor waypoints in source.
  - Chrome: 1600ms article scrolls `y:-24` (`.8s`, `[.22,1,.36,1]`); 1800ms hotkey hint; 2700ms keys depress (`y:2`, bg `#57575d`); 3300ms Companion; 3850ms page chip fades in; prompt "what should i actually try from this?" from 4300ms at 58ms/char; 7000ms "reading this page…"; 8800ms answer "three small things worth trying:" with 3 list items typing from 9300ms + 1100ms*i at 15ms/char; 13900ms source line + footer.
- **Detail mode (mobile):** "See the details" sets `.companion-stage-detailed` and scrolls the stage horizontally to `focus` px (Photoshop 430, Slack 265, Chrome 380).

---

## 9. Section: Privacy (`section#privacy.privacy-scene`)

### Layout
- `[0,9232,1440,957]`, margin-top 20px, `display:flex; align-items:center; padding:160px 72px` (1280: 160px 64px; 390: 100px 24px 88px), `background:#000; color:#f5f5f7; overflow:hidden`.
- `::before`: dot grid `radial-gradient(circle,#b5c4ca45 1px,transparent 1.3px)` at `background-size:16px 16px`, masked `linear-gradient(90deg,#000,transparent 28%,transparent 72%,#000)` (dots only at left/right edges). `::after`: `linear-gradient(180deg,#0000,#0000 50%,#000 90%)`. Both z -1.
- `div.privacy-layout` grid `404px 834px`, gap 57.6px, max-width 1480px.
- `div.privacy-intro` (eL wrapper): `a.privacy-eyebrow[href=/privacy]` "Privacy and control ›" (ui-monospace 14px 700, .065em, uppercase, `#50c7d8`, margin-bottom 32px); `h2#privacy-heading` (aria-label "Personal work. Private by design.") Exposure 44.48px/45.37px, letter-spacing -2.446px (-.055em), line 1 `#f5f5f7`, line 2 `.privacy-headline-accent` `#a1a1a8` (1280: 39.54px; 390: 25.35px); `p.privacy-intro-copy` 17px/28.9px `#aaaab1`, max-width 530px, pushed to bottom (margin-top 360px + padding-top 48px at 1440): "Your work is personal. You choose what to share with Merlin and when to step in. We never sell your personal information."
- `div.privacy-trust-cards` (eL wrapper) 2x2 grid 380x318 (390: single column, each card a 100px/186px grid). `article.privacy-trust-card` padding `24px 22px 28px`, dividers: `:nth-child(2n){border-left:1px solid #ffffff12}`, `:nth-child(n+3){border-top:1px solid #ffffff12}` (mobile: `+ .privacy-trust-card{border-left:0;border-top:1px solid #ffffff12}`). Each: line-art SVG 336x145 (viewBox 0 0 200 200, stroke ~#f5f5f7 low alpha, accent `#50c7d8`), h3 16px/23.2px 500 -0.32px `#d9d9df`, p 14px/23.8px `#92929b`:
  1. "Independently audited security" / "Merlin’s security controls undergo independent assessment through a SOC 2 Type II audit." (stacked layers)
  2. "Your approval comes first" / "Merlin asks before sending emails or invites. You’re in control." (box with sliders)
  3. "No model training" / "Neither Merlin nor our AI providers use your data to train models." (shield + lock)
  4. "Protected in storage and transit" / "Your data is encrypted when stored and as it moves between systems." (two devices + lock + travelling signal)

### Motion
- **Headline decode:** when the section is ≥18% in view (once), a 55ms `setInterval` increments `frame` until `10 + 32 = 42`. Character at global index i is shown when `frame >= 10 + i` (spaces always shown); otherwise its letter is `opacity:0` and a `span.privacy-code-glyph` (ui-monospace, `#8a969b`) shows `"01A9F3C7#8E2B6D4"[(7*frame + 3*i) % 16]`. Total ~2.3s.
- **Entrance:** intro and cards use the eL wrapper (`y:20 → 0`, .75s, `[.22,1,.36,1]`, once, amount .15).
- **Card illustrations (hover only):** all `[class*=privacy-]` SVG animations are `animation-play-state:paused` and set to `running` on `.privacy-trust-card:hover`:
  - `.privacy-animated-layer` `privacy-layer-shift 4s ease-in-out infinite` (`0%,to{translate:0 0} 50%{translate:0 -5px}`), delays `-0.35s*i`.
  - `.privacy-slider` `privacy-slider-shift 4.5s ease-in-out infinite` (`50%{transform:translate(10px,-2.3px)}`); two: delay -1.5s reverse; three: delay -.75s.
  - `.privacy-shield-ring` `privacy-shield-pulse 4s ease-in-out infinite` (opacity .35↔1), delays `-0.65s*i`.
  - `.privacy-transit-signal` `privacy-signal-travel 3s ease-in-out infinite` (`0%{translateX(0);opacity:0} 15%,85%{opacity:1} to{translateX(40px);opacity:0}`).

---

## 10. Section: FAQ (`section#faq.merlin-faq`)
- `padding:180px clamp(24px,5vw,80px)` (72px at 1440); bg #fff; color `#29292e`.
- `div.merlin-faq-layout`: `grid-template-columns:minmax(0,.8fr) minmax(0,1.65fr); gap:clamp(40px,6vw,100px)` (395 / 815, gap 86.4 at 1440); max-width 1480px.
- `header.merlin-faq-intro`: `h2#faq-heading` `font:400 clamp(36px,3.5vw,52px)/1.08 Exposure`, letter-spacing -0.04em (-2.016px) → 50.4px/54.43px at 1440: "Good questions.<br><span>Clear answers.</span>" (span `#85858b`), margin-bottom 24px; `p` 16px/27.2px `#74747c`, max-width 300px: "Start with the essentials. For anything else, ask Merlin below."
- `div.merlin-faq-list`: 5 `div.merlin-faq-item` (border-bottom `1px solid #e6e6e9`), each `h3 > button` (flex, space-between, gap 24px, `padding:0 0 26px` + top padding from item, 17px/25.5px 400 `#333338`) with Feather chevron-down 17px `#92929a` (`transition: transform .18s ease`, rotate 180deg when open). Answer `div.merlin-faq-answer[hidden]` p 16px/29.6px `#666670`. Single-open accordion (clicking open item closes it). Questions/answers:
  1. "What can Merlin help me with?" — "Merlin is an AI chief of staff for your Mac. It helps with browser research and tasks, meetings, files, coding projects, connected services, and scheduled or event-driven routines. Companion brings that help into the apps you’re already using."
  2. "What do I need to get started?" — "Sign in, connect your email and calendar, tell Merlin about your priorities, and start your trial. The desktop setup then walks you through the permissions needed for Companion. Email and calendar connections are required in the current onboarding experience."
  3. "Can I use Merlin in my own browser?" — "Yes. Pair the browser extension to use your existing browser sessions, or work in Merlin’s built-in browser. You can follow a task, stop it, or take over."
  4. "How does Companion work?" — "Press Option + Space to open Companion over your current app. Ask about your work, use selected text as context, or approve a screen capture when Merlin needs to see what’s on screen."
  5. "Can Merlin help with meeting notes?" — "The Meetings tab brings recordings, speaker-labelled transcripts, and notes together. You can search meetings, organize them in folders, and use templates to refine your notes."
- `form.merlin-faq-form > div.merlin-faq-input-row` (padding 26px 0, bottom border, `transition:border-color .18s`): input (17px/25.5px `#333338`, placeholder "What else would you like to know?", maxLength 500) + 44x44 round submit (Feather arrow-right, `#92929a`, disabled until text; `transition: color .16s, transform .16s`). Live site POSTs `{question}` to `/api/faq` (not reachable from a static clone; mock it). Loading text "Reading the docs…" with `merlin-faq-shimmer 1.8s linear infinite` (`background-position 150% → -100%`), stop button, error text "Something went wrong. Please try again." / "Couldn’t connect. Please try again." / "Stopped. You can edit your question and ask again."
- At 390: single column, heading 36px/38.88px, questions 15px/22.5px, answers 14px/25.9px.

---

## 11. Footer (`footer.closing-footer`)
- `[0,10994,1440,905]`, `padding:0 6.5% 48px` (93.6px at 1440; 390: 0 28px 40px), bg `#e6e6e6`, color `#292d27`, overflow hidden, relative.
- `div.closing-sky` (absolute inset 0): 3 `div.closing-bird-track.closing-bird-track-{1,2,3}` (absolute, 100px tall, tops ~16/30/46px) each with `div.closing-bird` (absolute; ~60x41 / 52x35 / 48x32) > `div.closing-bird-drift` > `div.closing-bird-shape` (`background:url(/assets/footer-bird-ascii{,-slow,-fast}.svg) center/contain no-repeat; aspect-ratio:40/27`).
- `div.closing-main` (grid `538px 657px`, gap 57.6px, `padding:129.6px 0 64px`, z 1):
  - `div.closing-invitation` (flex column, align start): `h2` Exposure 64px/60.8px (line-height .95) -0.64px: "Your next free moment<br><span class=closing-start-time>starts at <span class=closing-clock-time>[Feather clock icon] <time>HH:MM</time></span></span>" (clock span inline-flex gap 7.68px); `p` 17px/27.2px `#676767` (max ~370px, margin 24px 0 32px-ish): "In just three minutes, Merlin starts handling your to-dos. You decide what comes after."; download button (same as hero) `[94,11525,288,68]`.
  - `div.closing-beach`: `background:url(/assets/footer-beach-ascii.svg) 100% 50%/contain no-repeat; transform:scaleX(-1); margin-right:-86.4px` `[689,11123,744,576]`.
- `div.closing-footer-links` (flex, gap 44px, padding-top 34px, top border hairline, z 1): `div.closing-brand` = `a.closing-wordmark.hero-site-name[href=#top]` "merlin.computer" (17px 600 -0.425px) + `span.closing-copyright` "© {currentYear} merlin computing inc" (12px/19.2px `#74786e`); `nav[aria-label=Footer]` (margin-left auto, gap 31px, 14px/22.4px): Pricing `/pricing`, Manifesto `/manifesto`, Blog `/blog`, Privacy `/privacy`, Terms `/terms`, Contact `mailto:team@merlin.computer` (+ Feather arrow-up-right).
- At 390: main single column (`padding:90px 0 28px`), h2 40px/38px, beach `[8,12338,374,234]` below the CTA, links wrap (nav 13px).

### Motion
- Clock text = now + 3 minutes, `HH:MM` 24h zero-padded, recomputed every 1000ms and on visibilitychange (SSR fallback text "starts in three minutes").
- Birds (CSS, infinite):
  - track 1: `.closing-bird{animation:closing-bird-cross 23s linear infinite; animation-delay:-4s}`; `@keyframes closing-bird-cross{0%{left:-120px}72%,to{left:calc(100% + 20px)}}`; drift `closing-bird-drift 4.7s ease-in-out infinite` (`0%,to{transform:translateY(0) rotate(-3deg)} 50%{transform:translateY(10px) rotate(3deg)}`).
  - track 2: `closing-bird-glide 37s`, delay -19s, `animation-direction:reverse` (`0%{left:-120px}90%,to{left:calc(100% + 20px)}`); drift 8.5s, delay -2s.
  - track 3: `closing-bird-dart 13s`, delay -8s (`0%{left:-120px}20%{left:18%}42%{left:64%}55%,to{left:calc(100% + 20px)}`); drift 3.2s, delay -1.3s.
- Wordmark hover/focus: chroma sweep (`.9s`) as in the hero.

---

## 12. Floating navigation (`nav.floating-navigation_nav__y4vuM`, conditional)
- Rendered (framer `AnimatePresence`) only when `scrollY > 100` AND `innerHeight + scrollY < scrollHeight - 100` AND `#privacy` is not intersecting the viewport (IntersectionObserver, default threshold). Measured: visible from 300px, hidden while the black privacy section is on screen (8700–9800), visible again over FAQ, hidden at page bottom.
- Enter/exit: `initial {opacity:0, y:100}` → `{opacity:1, y:0}`, exit back, `duration .25` (0 with reduced motion).
- Style: `position:fixed; z-index:9999; bottom:5rem (50px); left:0; right:0; margin:0 auto; width:37rem (370px); max-width:calc(100% - 24px); height 46px; padding:.5rem (5px); border-radius:1.5rem (15px); background:rgba(0,0,0,.7); backdrop-filter:blur(5px); display:flex; justify-content:space-between; align-items:center`; font family `"Inter", "Open Runde", sans-serif` (Inter not loaded, falls back to Open Runde).
  - Left group (gap 1.5rem): logo tile 35x35 `background:#fff; border-radius:10px; color:#666` with the Merlin face SVG at 38px (`t` component, `page.split.js:5`); links "Pricing", "Manifesto" using the hover-text effect: `.hover-text_hoverText__JouUr{display:inline-flex;overflow-y:hidden;height:1.8rem;letter-spacing:.5px;font-size:1.3rem;transition:all .2s ease-in-out;color:#ddd}` `:hover{color:#12a7ff}`; inner `span{transition:transform .3s}` with `span::before{content:attr(data-hover);position:absolute;top:100%}`; on hover the span translates -100% (text rolls up).
  - Right: CTA "Download" → `/download?start=1`: `padding:.75rem 1rem; border-radius:1rem; background:#fff; color:#333; font-size:1.3rem; font-weight:500; line-height:1.6; letter-spacing:.5px; transition:color .2s`, hover `#12a7ff`. Measured 86x36.
  - ≤640px: `bottom:max(16px, env(safe-area-inset-bottom)); border-radius:20px`; logo 42x42 radius 13px (svg 30px); links 14px; CTA 14px, padding 10px 13px, radius 13px. ≤380px: gap 9px, logo 36px, text 12px.

---

## 13. Things Playwright could not fully capture
- `/api/faq` responses (server-side LLM) — the clone should stub it.
- Exact pixel output of the WAAPI FLIP notification animation frames (the generator is in source; reproduce from code rather than measurement).
- Origin returns 404 for `/apple-touch-icon.png` and `/favicon.ico`; only `/merlin-app-icon.svg` exists.
- Head meta to copy: title "Merlin — Your AI assistant for Mac"; description "Work with Merlin across your apps and browser. Prepare for meetings, create projects, and automate recurring work."; og:image `/assets/hero-beach-reading.webp`; `<link rel=icon href=/assets/merlin-app-icon.svg>`.

## 14. 1280 / 390 quick reference (boxes)
| Element | 1280x800 | 390x844 |
|---|---|---|
| `.story-hero` | 107,0,1067,554 | 16,0,358,480 |
| hero h1 | 180,160,920,148 (64px) | 24,136,342,113 (48.75px) |
| `.hero-landscape` | 107,554,1067,742 r36 | 10,480,371,800 r24 |
| `.companies` | 0,1336,1280,231 | 0,1300,390,216 |
| `#routines` | 51,1567,1178,2259 | 10,1516,371,2772 |
| `#browser` | 0,3907,1280,1580 (stage 800) | 0,4368,390,1667 (stage 844) |
| bs h2 | 40.96px/45.88px | 30px/33.6px |
| `#meetings` | 51,5487,1178,1709 | 10,6035,371,2336 |
| `#companion` | 51,7195,1178,1802 | 10,8371,371,1504 |
| `#privacy` | 0,9017,1280,957 (h2 39.54px) | 0,9876,390,1151 (h2 25.35px) |
| `#faq` | 0,9974,1280,805 (h2 44.8px) | 0,11027,390,858 (h2 36px) |
| footer | 0,10779,1280,827 | 0,11885,390,956 |
| doc height | 11605 | 12841 |
