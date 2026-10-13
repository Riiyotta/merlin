Source: https://www.merlin.computer/

# Merlin clone spec, pages B: /blog, /blog/:slug, /privacy, /terms

Measured live on 2026-10-07 with Playwright (Chromium 1.63, headless, DPR 1) at 1440x900, 1280x800 and 390x844. Every value is a computed style or a `getBoundingClientRect()` result. Boxes are `[x, y(document), w, h]` in CSS px, at 1440 unless stated otherwise. Read `CLONE_SPEC.md` §0–1 first: the approach (original CSS used verbatim, exact DOM and class names, Tailwind preflight off) and the global tokens (fonts, root font-size 62.5%, palette) apply here unchanged.

Companion files (all under `/Users/riyaghosh/V3/merlin/`):
- `reference/pages/{blog,blog-how-to-write-a-formal-email,blog-what-does-cc-and-bcc-mean-in-email,privacy,terms}.html`: hydrated `<body>.outerHTML` at 1440. Use these as **markup reference only**. They contain the full article and legal text, which must **not** be copied into the clone (see §7).
- `reference/pages/<route>-{1440,1280,390}-{full,viewport}.png`: screenshots.
- `reference/pages/measure-<route>-<w>.json`: raw measurement dumps (DOM tree with boxes, every distinct text style, block styles, images, network requests).
- `reference/source/pages/blog_layout-ab0ddbac4d8ccbc2.js` (blog layout: nav + footer + CSS-module class map), `blog_page-ab45e5459b818121.js` (blog index and `[slug]` page; same 527-byte chunk, which only mounts Sanity Live), `privacy_page-7b1943cd942f78a9.js` (also used by /terms; nav + footer only), `1490-b1a1d4765000dceb.js` (next-sanity Live / visual-editing runtime; not needed for the clone).
- `src/data/blog-posts.json`: metadata and body structure outline for all 20 posts (§3.6).
- `public/assets/blog/`: 19 cover images plus the author avatar (§3.5).

---

## 0. Cross-route facts

### 0.1 Stylesheets (live `<link>` order) and local status
| Route | Order | New |
|---|---|---|
| `/blog`, `/blog/:slug` | `357da7cf10d68108` → `437c25afc566ca52` → `a5f02e9d0c6db7af` → `f46c55d95248097e` → `e2e0ba86a6b0d559` → `ea3e27f6a69b5df4` | none (all already in `src/styles/original/`) |
| `/privacy`, `/terms` | same as above, plus `e261c04d0a2d5dfe` inserted **before** `ea3e27f6a69b5df4` | `e261c04d0a2d5dfe.css` (4275 B, legal page styles), **downloaded** to `src/styles/original/`. It contains no `url()`s, so nothing was rewritten. |

- I verified every file already in `src/styles/original/` against live by hash. All are byte-identical except `0a5b07db1896be06.css` and `ea3e27f6a69b5df4.css`, and those differ only in the intended `url()` rewrites (`/fonts/…`, `/assets/footer-*.svg`).
- **The blog styles are a CSS module inside `ea3e27f6a69b5df4.css`**: every rule is `#top.blog_page__bLGfe .blog_*__hash`. That is why the homepage already loads it.
- **Global loading is safe.** I injected every homepage/pricing/legal stylesheet that these routes do *not* load (`4a4d88…`, `6385c2…`, `401561…`, `922109…`, `0a5b07…`, `fc1769…`, `f7c0a2…`, `2abce9…`, `9168513…`, `ae725e…`, `e261c0…`) into the live /blog, /blog/how-to-write-a-formal-email and /privacy pages. Result: zero computed-style changes apart from bird-animation progress, and identical document heights. The clone can therefore import all original CSS once, globally, in the homepage order with `e261c04d0a2d5dfe.css` added anywhere before `ea3e27…`.
- The inline `:root{--mantine-font-family…}` style and the Mantine `.mantine-visible-from-*` style block are present on these routes too, as on the homepage.

### 0.2 Fonts and assets loaded
- Fonts: `Exposure.woff2`, `open-runde-{400,500,600}.woff2`, `Caveat.ttf` (blog index only, for `.blog_handwritten`), `3c6a8fcb177aeedf-s.p.ttf`. All are already in `public/fonts/`. **No new fonts.**
- Images: `/_next/image?url=/merlin-dock.png&w=32` (nav icon, local `/assets/merlin-dock-32.png`) and the footer `footer-bird-ascii{,-slow,-fast}.svg` + `footer-beach-ascii.svg` (already in `/assets/`). The blog index also loads `/story/handmade/hero-beach-reading.webp` (already at `/assets/hero-beach-reading.webp`). Posts load the Sanity CDN cover (`?w=1600&auto=format`, served as AVIF) and the avatar (`?w=88&h=88&fit=crop`). Both are now local (§3.5).
- No video, audio or icon fonts. All icons are inline Feather SVGs (`stroke-width:2`, `height/width:1em`):
  - arrow-up-right: `<line x1=7 y1=17 x2=17 y2=7/><polyline points="7 7 17 7 17 17"/>`
  - arrow-left: `<line x1=19 y1=12 x2=5 y2=12/><polyline points="12 19 5 12 12 5"/>`

### 0.3 Shared components on these routes
| Component | Used? | Identical to homepage? |
|---|---|---|
| Corner nav `nav.hero-corner-nav` (logo + "merlin.computer", Pricing, Manifesto) | Yes, all 4 routes | **Same component and CSS (`a5f02e…`), different wrapper.** On the homepage it sits inside `section.story-hero`. Here it is `div.site-container > header.blog_navigation__bQ9ND` (blog) or `header.legal-navigation` (legal), both `position:relative; height:160px` (`144px` at ≤760/≤640). Measured box `[120,36,157,84]` at 1440, `[107,36,157,84]` at 1280, `[16,24,150,79]` at 390. **Variant:** no link matches the current path (`/`, `/pricing`, `/manifesto` only), so `aria-current` is never set and `span.hero-nav-dot` is **not rendered at load**. It appears on the first hover/focus: 6x6, `#00c8e0`, radius 50%, absolute; framer `useSpring {stiffness:170, damping:15, mass:.8}`, axis y, bend -8, lead 10, size 6 (identical hook to the homepage). On mouse-leave with no current link the dot stays at the last hovered link. Logo hover triggers `hero-site-sweep` for 900ms. |
| Closing footer `footer.closing-footer` (birds, "Your next free moment…" clock, beach ASCII, Download button, footer links) | Yes, all 4 routes | **Identical.** Same component (`42077` in the layout chunk) and same markup. Height 905 at 1440, 827 at 1280, 956 at 390. Footer links: Pricing, Manifesto, Blog, Privacy, Terms, Contact ↗. |
| Download button `a.download-button.download-button-primary` | Only inside the footer | Identical ("Get Merlin for Mac", `/download?start=1`, 288x68). |
| Floating nav `nav.floating-navigation_nav__y4vuM` | **No.** Absent at every scroll position (checked at scrollY 0 and 1500). | n/a |
| Skip link `a.skip-link` | Yes (fixed, `top:12px`, translated -93.6px off-screen until focus) | Same CSS. Text/href per route: blog index and posts "Read the blog" → `#blog-content`; privacy "Read privacy and control" → `#legal-content`; terms "Read terms of service" → `#legal-content`. |

### 0.4 Root
- `<main id="top" class="merlin-story site-layout blog_page__bLGfe">` (blog index and posts) or `class="merlin-story site-layout legal-page"` (privacy/terms). Body background `#fff`; html font-size 10px at 1440 (62.5%). `main` has `position:relative; overflow:clip`.
- `div.site-container`: width 1200 / max 1440, margin `0 120px` at 1440; 1067 at 1280 (x 107); 358 at 390 (x 16). It wraps **only** the nav header. The page content block is a sibling of it.
- `html{scroll-behavior:smooth}` (from the existing CSS) is active, so TOC/anchor jumps animate.

### 0.5 Head / titles
| Route | `<title>` | meta description |
|---|---|---|
| /blog | `Blog — Merlin` | "Notes on building Merlin, finding focus, and making room for life." |
| /blog/:slug | `<post title> — Merlin` | the post title (description = title for every post); `og:type=article`, `article:published_time`, `article:author` "Adeola Adeoti" |
| /privacy | `Privacy and control — Merlin` | "How Merlin handles your information, what stays on your Mac, and how to manage access and your data." |
| /terms | `Terms of Service — Merlin` | "Terms governing access to and use of Merlin." |
Icon: `/assets/merlin-app-icon.svg`. Non-post routes reuse the homepage og/twitter tags.

---

## 1. Route `/blog` (index)

### 1.1 DOM (1440 boxes)
```
main#top.merlin-story.site-layout.blog_page__bLGfe [0,0,1440,4793]
  a.skip-link[href=#blog-content]
  div.site-container [120,0,1200,160]
    header.blog_navigation__bQ9ND [120,0,1200,160]
      nav.hero-corner-nav (shared, see 0.3)
  div#blog-content.blog_index__3_0oG [160,160,1120,3728]
    header.blog_intro__ggRFG [160,160,1120,421]          padding 58px 0 100px; text-align center
      h1 [160,242,1120,160]   "A little more<br>to think about."
      p  [160,426,1120,56]    "Notes on building Merlin, finding focus,<br> and making room for life."
    a.blog_featured__dQvxo[href=/blog/<featured slug>] [160,581,1120,420]   grid 560.5px 487.4px (1.15fr 1fr), gap 72px, align-items center
      div.blog_featuredImage__DhF7y [160,581,561,420]   aspect-ratio 4/3; radius 20px; bg #f2f2ef; overflow hidden
        img[src=/story/handmade/hero-beach-reading.webp width=1400 height=1050 fetchpriority=high alt=""]  object-fit cover; 100%x100%
      div.blog_featuredCopy__844eq [793,634,487,315]
        span.blog_eyebrow__0KDg5 [793,634,487,23]  "Others" + span.blog_latest__S4ifZ "Latest story" [844,634,79,23]
        h2 [793,675,487,187]   featured title (4 lines at 1440)
        div.blog_meta__jCSwR [793,880,487,19]  <span>Adeola Adeoti</span><time datetime=ISO>Jul 8, 2025</time>
        span.blog_readLink__2wa5U [793,927,112,21]  "Read the story" + arrow-up-right svg
    section.blog_stories__Dlir_ [160,1098,1120,2505]       margin-top 96px
      div.blog_sectionHeading__dCqQ1 [160,1098,1120,45]   flex, baseline, space-between, padding-bottom 24px
        h2#more-stories "More from Merlin" [160,1098,145,19]
        span "A few things worth sharing." [1111,1098,169,21]
      div.blog_storyList__M4Hb4 [160,1143,1120,2460]      border-top 1px #eaece6
        a.blog_story__uUvdL[href=/blog/<slug>] x19, each [160,y,1120,128] (pitch 127.6px)
          span.blog_storyCategory__LA7IY "Others" [160,1176,140,22]   padding-top 4px
          div.blog_storyCopy__ILI0m [330,1176,884,63]
            h3 title [330,1176,884,30]
            div.blog_meta__jCSwR [330,1219,884,19]  (margin-top 14px) span author + time
          span.blog_storyArrow__IWJ3c [1244,1176,32,32]  arrow-up-right svg 17x17
    aside.blog_manifesto__VgyoG [160,3603,1120,285]       padding 96px 0 100px; text-align center
      span.blog_handwritten__cIXLa "a little less busy. a little more life." [160,3670,1121,102] rotate(-3deg)
      a[href=/manifesto] "Why we’re building Merlin" + arrow-up-right [631,3766,177,21]  margin-top 24px
  footer.closing-footer [0,3888,1440,905]  (shared)
```
- There are **no thumbnails, excerpts, filters, tags, search or pagination**: one featured post, then a flat list of all 19 remaining posts. The story card has **no `<p>` excerpt** at all; the CSS rule for `.blog_storyCopy p` exists but is unused. The featured card has no `> p` either. `.blog_empty__vH0G_` (empty state: padding 48px 24px, radius 20px, bg `#f7f8f5`, h2 Exposure 32px/1.2) is defined but not rendered.
- The featured image is the static `hero-beach-reading.webp`, **not** the post's cover (the featured post has no Sanity cover).
- The list order is newest first and matches `src/data/blog-posts.json` `posts[1..19]`; `posts[0]` is the featured post.
- Reading width: the index column is `width:min(1120px, 83.333333%)`, centered.

### 1.2 Typography (computed)
| Role | Family | Size / line-height | Weight | Letter-spacing | Color |
|---|---|---|---|---|---|
| intro h1 | Exposure, Georgia, serif | 76px / 79.8px (`clamp(48px,5.6vw,76px)/1.05`); 71.68/75.26 at 1280; 48/50.4 at 390 | 400 | -0.035em (-2.66px) | #343630 |
| intro p | Open Runde | 18px / 27.9px (16px/24.8 at ≤760) | 400 | -0.02em (-0.36px) | #85877f |
| eyebrow ("Others") | Open Runde | 12px / 18px | 500 | normal | #888b84 |
| "Latest story" pill | Open Runde | 11px / 16.5px | 500 | normal | #218c9b on #edf8f9, padding 3px 8px, radius 5px |
| featured h2 | Exposure | 40px / 46.8px (`clamp(28px,3vw,40px)/1.17`); 38.4/44.93 at 1280; 32/37.44 at 390 | 400 | -0.025em (-1px) | #3b3e36; margin 18px 0; `text-wrap:pretty` |
| meta author span | Open Runde | 12px / 19.2px | 400 | normal | #696e63 |
| meta time | Open Runde | 12px / 19.2px | 400 | normal | #92948e; gap 6px 16px |
| read link | Open Runde | 13px / 20.8px | 500 | normal | #343630; inline-flex gap 8px; margin-top 28px |
| section h2 "More from Merlin" | **Exposure** (inherited from a global h2 rule) | 18px / 18.54px | 500 | -0.025em (-0.45px) | #343630 |
| section span | Open Runde | 13px / 20.8px | 400 | normal | #9a9c95 (hidden ≤760) |
| story category | Open Runde | 12px / 18px | 400 | normal | #92968a |
| story h3 | Open Runde | 22px / 29.7px (20px/27 at ≤760) | 500 | -0.025em (-0.55px) | #45493f |
| handwritten | Caveat, cursive | 36px / 43.2px (28px at ≤760) | 500 | -0.02em (-0.72px) | #20b8cf |
| manifesto link | Open Runde | 13px / 20.8px | 400 | normal | #74796b; gap 8px |
| page base | Open Runde | — | — | — | color #343630, bg #fff, `-webkit-font-smoothing:antialiased`; links `color:inherit; text-decoration:none` |
Focus ring for all blog links: `outline:2px solid #20b8cf; outline-offset:6px; border-radius:6px`.

### 1.3 Story row geometry
- 1440/1280: `grid-template-columns:140px 1fr 36px; gap:30px; padding:32px 0; border-bottom:1px solid #eaece6; align-items:start`. The arrow is 32x32 at the right (x 1244 at 1440).
- ≤760px (390): `grid-template-columns:1fr 28px; gap:12px; padding:26px 0`. The category and copy sit in column 1 (category on row 1, copy on row 2); the arrow is at `grid-column:2; grid-row:2`. Row box `[20,1104,350,174]`, category `[20,1130,310,22]`, copy `[20,1164,310,87]`, arrow `[342,1164,32,32]`.

### 1.4 Responsive boxes
| Element | 1280x800 | 390x844 |
|---|---|---|
| page height | 4717 | 5739 |
| nav header | 107,0,1067,160 | 16,0,358,144 |
| `.blog_index` | 107,160,1067,3731 | 20,144,350,4639 (`calc(100% - 40px)`) |
| intro header | 107,160,1067,412 | 20,144,350,290 (padding 36px 0 56px) |
| intro h1 | 107,242,1067,151 | 20,204,350,101 |
| featured | 107,572,1067,402 | 20,434,350,566, single column, gap 26px |
| featured image | 107,572,536,402 | 20,434,350,263 (4/3, radius 16px) |
| featured copy | 707,620,466,307 | 20,723,350,277 |
| stories section | 107,1071,1067,2535 | 20,1060,350,3515 (margin-top 60px) |
| manifesto aside | 107,3605,1067,285 | 20,4575,350,208 (padding 64px 0) |
| footer | 0,3891,1280,827 | 0,4783,390,956 |
Breakpoint for the blog module: `@media (max-width:760px)` only (plus `prefers-reduced-motion`).

### 1.5 Motion (CSS only; the page chunk has no entrance animation, IntersectionObserver or scroll listener)
- No load or scroll entrance animations. `document.getAnimations()` at load returns only the 6 footer bird animations. No elements start at opacity 0.
- Featured card hover (`a.blog_featured:hover`): image `transform:scale(1.025)`, `transition:transform .45s cubic-bezier(.23,1,.32,1)`; read-link svg `translate(2px,-2px)`, `.18s cubic-bezier(.23,1,.32,1)`.
- Story row hover: h3 color #45493f → **#12889a** (`color .16s ease`); arrow bg transparent → **#eef8f8**, color #8f9487 → **#12889a**, `transform:translate(2px,-2px)` (`background .16s ease, color .16s ease, transform .18s cubic-bezier(.23,1,.32,1)`). All measured on hover.
- Manifesto link hover: svg `translate(2px,-2px)` .18s.
- Handwritten text: static `rotate(-3deg)` (matrix measured).
- Reduced motion: all transitions/transforms on these elements are set to `none`.
- Nav dot spring and footer birds/clock: see 0.3 and `CLONE_SPEC.md` §11.

---

## 2. Route `/blog/:slug` (post template)

I measured `/blog/how-to-write-a-formal-email` and confirmed the template on `/blog/what-does-cc-and-bcc-mean-in-email` (same nodes, same classes, same x/width at all 3 widths; only the h1 line count and body length differ). All 20 posts render with this template (checked by `posts.js`).

### 2.1 DOM (1440, formal-email)
```
main#top.merlin-story.site-layout.blog_page__bLGfe [0,0,1440,22677]
  a.skip-link[href=#blog-content] "Read the blog"
  div.site-container > header.blog_navigation__bQ9ND [120,0,1200,160] > nav.hero-corner-nav
  article#blog-content.blog_article__Uk9MF [320,184,800,21487]     width min(800px,83.333333%); margin 24px auto 100px
    a.blog_back__4b1m9[href=/blog] [320,184,81,21]  arrow-left svg + " All stories"
    header.blog_articleHeader__3w7of [320,208,800,271]               padding 56px 0 40px
      span.blog_eyebrow__0KDg5 [320,264,800,18]  "Others" (category only; no read time anywhere on the site)
      h1 [320,302,800,67]   (1 line; cc-bcc post wraps to 2 lines, h 134)   margin 20px 0 24px
      (no dek: header > p is styled (20px/1.55 #858b7d) but no post has one)
      div.blog_author__UxA6e [320,399,800,40]   flex, gap 12px, margin-top 30px
        img[width=36 height=36 alt=""] 36x36, radius 50%, object-fit cover (Sanity avatar, 88x88 crop)
        div (flex column) [368,399,86,40]
          span "Adeola Adeoti"       13px/20.8 #343630
          time[datetime=ISO] "May 13, 2025"   12px/19.2 #92978b
    img.blog_articleImage__wj3kN[alt=<post title>] [320,479,800,534]  width 100%; max-height 600px; object-fit cover; radius 18px; margin-bottom 48px
    div.blog_prose__r_2py [380,1061,680,20512]   max-width 680px; margin 0 auto
      …portable-text blocks (p, h2, h3, h4, ul, ol, blockquote; direct children)…
    footer.blog_articleEnd__zI6hK [380,21622,680,50]  max-width 680; margin 48px auto 0; padding-top 28px; border-top 1px #e7ebe1; flex wrap, space-between, gap 20px
      span "Thanks for spending a little time with us."   13px #969c8e
      a.blog_back__4b1m9[href=/blog] arrow-left + " Back to all stories"
  footer.closing-footer [0,21771…] (shared)
```
- **Reading column:** article (header, cover) 800px; **prose and article-end max-width 680px**, centered (x 380 at 1440, 300 at 1280, 20 at 390, where the width is 350).
- The featured post (`the-future-of-work-is-autonomous-…`) has **no cover**, so the `img.blog_articleImage` is omitted and the prose follows the header directly.
- Dates: the article uses the long month ("July 8, 2025"); the index uses the short month ("Jul 8, 2025"). Use `toLocaleDateString('en-US',{month:'long'|'short',day:'numeric',year:'numeric',timeZone:'UTC'})`. Midnight-UTC posts (May 14 00:26Z) display as May 14, so the server renders in UTC.

### 2.2 Prose styles (from CSS, confirmed by computed values at 1440)
| Element | Rule (computed) |
|---|---|
| `.blog_prose` | Open Runde 17px / 30.6px (1.8), color **#686e60**, `overflow-wrap:anywhere`; ≤760: 16px / 28.8px |
| `p` | margin 0 0 24px; inherits font. `<p><br></p>` spacer paragraphs are 30.6px tall; `<p></p>` is 0 tall (margins collapse) |
| `h1–h6` | margin 40px 0 16px; Open Runde **500** 24px/1.3 (31.2px), color #363d2f, letter-spacing -0.025em (-0.6px) |
| `h3–h6` | font-size 20px (line 26px, -0.5px) |
| heading text | Sanity wraps heading text in `<strong>`, so the **rendered** heading weight is 600 and color #454d3d (h2 strong: 24px/31.2 600 #454d3d; h3/h4 strong: 20px/26 600 #454d3d) |
| `strong` | weight 600, color #454d3d |
| `em` | italic, inherits |
| `ul, ol` | margin 0 0 24px; padding-left 24px. `li` margin 8px 0, padding-left 4px (li box 656 wide at 1440) |
| `a` | color #12889a; underline, `text-underline-offset:4px` |
| `blockquote` | margin 32px 0; padding 8px 0 8px 24px; **border-left 2px solid #20b8cf**; Exposure 400 24px/1.5 (36px), color #4e5945; `strong` inside → 600 #454d3d; `blockquote p:last-child{margin-bottom:0}`. The source puts **each line of an email template in its own `<blockquote>`** (consecutive blockquotes collapse to 32px gaps, each with its own cyan bar segment; empty `<blockquote><br></blockquote>`-style lines are 0 words). |
| `code` | 14px/1.6 ui-monospace, bg #f1f3ee, radius 4px, padding 3px 5px (CSS only; no post uses it) |
| `pre` | padding 20px, bg #f1f3ee, radius 12px, overflow-x auto (unused) |
| `img` | block, max-width 100%, radius 14px, margin 32px 0 (unused: no post has inline images) |
| `hr` | margin 40px 0; border-top 1px #e7ebe1 (unused) |
| tables / figures | **None in any of the 20 posts.** No CSS exists for them. |

### 2.3 Header typography
| Role | Value |
|---|---|
| back link | Open Runde 13px/20.8 400, #878c80; inline-flex gap 8px; hover **#12889a** (`color .16s ease`) |
| eyebrow | 12px/18 500 #888b84 |
| h1 | Exposure 400 60px/67.2px (`clamp(36px,4.8vw,60px)/1.12`), -0.03em (-1.8px), #343930, `text-wrap:pretty`; 60px at 1280; 36px/40.32 (-1.08px) at 390 |
| author name / time | 13px/20.8 #343630 / 12px/19.2 #92978b |
| article end span | 13px/20.8 #969c8e |

### 2.4 Responsive boxes (formal-email)
| Element | 1280 | 390 |
|---|---|---|
| page height | 22598 | 29760 |
| article | 240,184,800,21487 | 20,168,350,28535 |
| header | 240,208,800,271 | 20,192,350,265 (padding-top 36px) |
| h1 | 240,302,800,67 | 20,266,350,81 |
| cover | 240,479,800,534 | 20,457,350,234 (margin-bottom 32px) |
| prose | 300,1061,680,20512 | 20,722,350,27843 |
| article end | 300,21622,680,50 | 20,28613,350,91 (wraps; back link on its own row) |
Breakpoint: `max-width:760px` (nav 144px tall, article `calc(100% - 40px)`, header padding-top 36px, dek 18px, cover margin-bottom 32px, prose 16px).

### 2.5 Motion
- **None at load or on scroll.** There is no progress bar, no sticky TOC, no related-posts block, no share buttons and no IntersectionObserver usage in the route chunks. The only client code is the nav (dot spring), the footer, and Sanity Live (data revalidation, no UI).
- Hover: back links → #12889a (.16s ease). Prose links have no hover rule.

---

## 3. Blog data (`src/data/blog-posts.json`)

### 3.1 Shape
`{ _note, posts: [ {slug, title, date (ISO), dateDisplayIndex, dateDisplayArticle, author, authorAvatar, category, readTime:null, cover, coverSize, coverAlt, coverOriginal, indexImage, featured, inSitemap, excerpt, metaDescription, bodyStats:{totalWords, blockCounts, liveDocumentHeight1440}, structure:[…]} ] }`
- `structure[]` lists the direct children of `.blog_prose`, in order: `{type:'p'|'h2'|'h3'|'h4'|'ul'|'ol'|'blockquote', words:N}`. Headings carry `text` (allowed) instead of words; lists add `items:N` (and `nested` when sub-lists exist); `inline:[…]` lists descendant tags (`strong`, `em`, `a`, `br`); `links:N` counts anchors. **No paragraph text is stored.** The builder should generate placeholder text of `words` length per block. Keep the 0-word spacer `<p>`s (with `inline:['br']` they render 30.6px tall).
- **20 posts:** the 19 in `sitemap.xml` plus the featured post `the-future-of-work-is-autonomous-why-your-next-hire-might-be-an-ai-chief-of-staff` (on the index and live at its URL, but **not in the sitemap**; `inSitemap:false`, `featured:true`, `cover:null`, `indexImage:/assets/hero-beach-reading.webp`).
- Author is "Adeola Adeoti" and category is "Others" for all posts. The site shows no read time (`readTime:null`). No post has an excerpt/dek; `excerpt` = meta description = title.

### 3.2 Index metadata (verbatim, newest first)
| # | Title | Date |
|---|---|---|
| F | The Future of Work is Autonomous: Why Your Next ‘Hire’ Might Be an AI Chief of Staff | Jul 8, 2025 |
| 1 | How to Share a Google Calendar on iPhone in 2025 | May 14, 2025 |
| 2 | How to Use Google Calendar: The Complete 2025 Guide | May 14, 2025 |
| 3 | How to schedule Slack messages with ease | May 13, 2025 |
| 4 | Microsoft Teams vs Slack (2025): Pros, cons, and what's best | May 13, 2025 |
| 5 | How to Email a Professor: Updated Guide With Templates and Real-World Tips | May 13, 2025 |
| 6 | How to Set an Out of Office in Microsoft Teams | May 13, 2025 |
| 7 | How to Write a Formal Email | May 13, 2025 |
| 8 | How to Create a Professional Email Address (2025 Guide) | May 13, 2025 |
| 9 | How to End an Email: Ultimate Guide to Professional and Friendly Sign-Offs in 2025 | May 13, 2025 |
| 10 | What does CC and BCC mean in email? | May 13, 2025 |
| 11 | Best Free Transcription Software Tools in 2025: Top Speech-to-Text Picks | May 13, 2025 |
| 12 | Summary of Best 100 ChatGPT-4 Prompts | May 13, 2025 |
| 13 | AI Note-Taking Tools in 2025: Top Picks, Trends & Tips | May 13, 2025 |
| 14 | Sam Altman: The Startup Prodigy Steering OpenAI’s Quest for AGI and AI Leadership | May 13, 2025 |
| 15 | Mastering Gmail Out-of-Office Replies in 2025 | May 13, 2025 |
| 16 | Throwaway Email Addresses in 2025: The Complete Guide to Disposable Emails for Privacy and Spam Control | May 13, 2025 |
| 17 | Why Is My Email Queued and How to Fix It | May 13, 2025 |
| 18 | How to Write a Resignation Email in 2025: The Ultimate Guide for Professionals | May 13, 2025 |
| 19 | How to Unsend an Email (Updated 2025 Guide) | May 5, 2025 |

### 3.3 Outline of the two measured posts (compressed; `p:N` = words, `x2` = repeated)
- **how-to-write-a-formal-email** (243 blocks, 2698 words; p 124, h2 4, h3 7, h4 7, ul 7, blockquote 94): p:142 · h2 "Why Formal Email Etiquette Matters" · 3 p (94/66/98) · h2 "Anatomy of a Formal Email" · p:14 · seven h3 steps ("1. Subject Line – Be Clear and Specific" … "7. Final Checks"), each 1–3 p of 35–134 words, with ul[3] and ul[5] · h2 "Example Formal Email Templates" · seven h4 templates (Job Application, Formal Complaint, Meeting Follow-Up, Project Update, Networking/Introduction, Thank You, Vacation Request), each a ~12-word intro p plus a run of 8–17 single-line blockquotes (0–83 words each) · h2 "Conclusion" · 3 p (64/58/16). Spacer `p:0` (×2) sits around every heading.
- **what-does-cc-and-bcc-mean-in-email** (133 blocks, 2516 words; p 83, h2 8, h3 1, ul 12, blockquote 29): p:98 · h2 "What Are CC and BCC?" (ul[2], blockquote:57, h3 "Why “Carbon” Copy?") · h2 "Key Differences: Transparency vs. Privacy" (ul[3]:198) · h2 "When to Use CC (Carbon Copy)" (ul[4]) · h2 "When to Use BCC (Blind Carbon Copy)" (ul[4]) · h2 "Pros and Cons of CC and BCC" (ul[4]) · h2 "Common Mistakes and Etiquette Tips" (ul[6]:302) · h2 "Real-World Examples and Use Cases" (6 single-item ul labels, each followed by a run of 5–7 blockquote lines) · h2 "Conclusion" (ul[3], p:66, p:8).
- Other posts' block counts are in `bodyStats.blockCounts`. Overall the bodies use p, h2, h3, h4, ul, ol, blockquote only, with no images, tables, code or figures.

### 3.4 Clone note on heights
Live document heights at 1440 are in `bodyStats.liveDocumentHeight1440` (e.g. formal-email 22677, cc-bcc 14941). Placeholder text with matching word counts at 17px/30.6 in 680px should land within a few percent.

### 3.5 Downloaded images (`/Users/riyaghosh/V3/merlin/public/assets/blog/`)
- `<slug>.webp` for the 19 sitemap posts: the Sanity original requested as `?w=1600&fm=webp` (the live page uses `?w=1600&auto=format`, which is AVIF in Chromium, at the same 1600 width). Sizes are 1600 x 900–2400; e.g. `how-to-use-google-calendar-the-complete-2025-guide.webp` is portrait 1600x2400 and is cropped by `max-height:600px; object-fit:cover`. Rendered at 800x534 for 3:2 covers.
- `author-adeola-adeoti.jpg`: 88x88 JPEG (rendered 36x36 round).
- The featured post has no cover; the index uses the existing `/assets/hero-beach-reading.webp` (1536x1024 natural, rendered 561x420).
- Nothing was overwritten. `public/assets/blog/` was empty before this run.

---

## 4. Route `/privacy`

### 4.1 DOM (1440)
```
main#top.merlin-story.site-layout.legal-page [0,0,1440,4297]      bg #fff; color #41463c
  a.skip-link[href=#legal-content] "Read privacy and control"
  div.site-container > header.legal-navigation [120,0,1200,160] > nav.hero-corner-nav
  div#legal-content.legal-document [180,204,1080,3075]   width min(1080px,83.333333%); margin 44px auto 112px
    header.legal-heading [460,204,720,270]               max-width 720; margin 0 0 72px 280px
      nav.legal-tabs [460,204,164,42]   flex gap 6px; padding 4px; border 1px #eceee8; radius 24px; bg #f5f6f3; width fit-content
        a[href=/privacy][aria-current=page] "Privacy" [465,209,78,32]   bg #fff; color #353c2e; shadow 0 1px 3px #242b1810 (rgba(36,43,24,.063)); padding 7px 16px; radius 20px
        a[href=/terms] "Terms" [549,209,71,32]   transparent; color #878e7e
      h1 "Privacy and control" [460,278,720,69]   margin 32px 0 24px
      p.legal-intro [460,371,720,59]   (19 words, 2 lines at 1440)
      p.legal-date [460,455,720,19]   "Last updated <span aria-hidden>·</span> September 28, 2026"; flex gap 8px; margin-top 24px
    div.legal-columns [180,546,1080,2734]   grid 220px minmax(0,1fr); gap 60px; align-items start
      aside.legal-sidebar [180,546,220,312]   position sticky; top 32px; max-height calc(100dvh - 64px); overflow auto; scrollbar-width thin
        nav.legal-contents[aria-label="On this page"]   flex column; align flex-start; gap 5px; padding-right 16px
          span.legal-contents-label "On this page"   margin-bottom 12px
          a[href=#<id>] x8 (5px 0 padding)
      article.legal-prose [460,546,720,2734]   max-width 720
        section#<id>.legal-section x8     padding-bottom 36px; margin-bottom 36px (0 for last); border-bottom 1px #eceee8; scroll-margin-top 40px
          h2#<id>-title
          p …
        footer.legal-document-footer   flex wrap; space-between; gap 20px; padding-top 28px
          a[href=mailto:team@merlin.computer] "Contact our team <span aria-hidden>↗</span>"
          a[href=#legal-content] "Back to top <span aria-hidden>↑</span>"
  footer.closing-footer (shared)
```

### 4.2 Section outline (headings verbatim; body as word counts only)
| id | h2 (= TOC label) | Body |
|---|---|---|
| `local-and-cloud` | On your Mac. Connected when needed. | p 48, p 42 |
| `information` | The information Merlin works with. | p 35, p 37 |
| `permissions` | You choose the access. | p 41, p 46, p 31 |
| `providers` | AI and service providers. | p 41, p 30 |
| `security` | Security, with care. | p 15, p 39 |
| `retention` | Managing and deleting your data. | p 30, p 35 |
| `website` | When you use this website. | p 82, p 63 |
| `contact` | Questions about your privacy? | p 16, p 18 |
17 paragraphs, about 650 words. There are no lists, tables or h3s. Each h2 has `id="<section id>-title"`.

### 4.3 Typography (legal, shared with /terms)
| Role | Value |
|---|---|
| tabs | Open Runde 500 13px/18.2px; active #353c2e, inactive #878e7e |
| h1 | Exposure 400 64px/69.12px (`clamp(44px,5vw,64px)/1.08`), -0.035em (-2.24px), #363c30, `text-wrap:balance`; 64px at 1280; 44px/47.52 at ≤640 |
| intro | Open Runde 400 18px/29.7px (1.65), #818879, `text-wrap:pretty`; 16px/26.4 at ≤640 |
| date | 12px/19.2px #929889 |
| TOC label | 500 12px/18px #464e3d |
| TOC links | 400 12px/18px #8b9281 (link box 28px tall single-line, 46px two-line) |
| section h2 | 500 22px/29.7px, -0.025em (-0.55px), #414a36; margin 0 0 18px; 21px at ≤640 |
| section h3 | 500 16px/24px, -0.01em (-0.16px), #505a44; margin 28px 0 10px |
| p / li | 400 16px/28.8px, #777f6d; p margin 0 0 16px (last 0); `overflow-wrap:anywhere` |
| ul | margin 16px 0; padding-left 22px; li margin 8px 0, padding-left 4px; `li::marker` #a0aa94 |
| section links | #12889a underline, offset 4px |
| doc-footer links | 500 13px/19.5px #78836b, flex gap 8px |
| focus | `outline:2px solid #20b8cf; outline-offset:5px; radius 4px` |

### 4.4 Responsive
- Breakpoints (from `e261c04d0a2d5dfe.css`): **≤900px**: heading margin-left 0; columns `170px minmax(0,1fr)`, gap 32px. **≤640px**: nav 144px; document `calc(100% - 40px)`, margin 24px auto 72px; heading margin-bottom 36px; h1 44px; intro 16px; columns become block; the sidebar becomes static, `border-block:1px solid #eceee8`, padding 16px 0, margin-bottom 36px; TOC becomes a **horizontal scroll row** (gap 20px, label hidden, links `white-space:nowrap; min-height:44px; display:flex; align-items:center`); sections padding/margin-bottom 28px, scroll-margin-top 24px.
- 1280: document `[107,204,1067,3075]`, heading `[387,204,720,270]`, sidebar `[107,546,220,312]`, prose `[387,546,720,2734]`, height 4218.
- 390: document `[20,168,350,4569]`, tabs `[20,168,164,42]`, h1 `[20,242,350,95]`, intro `[20,361,350,79]`, sidebar `[20,520,350,82]` (contents row `[20,537,350,48]`), prose `[20,638,350,4100]`, first section `[20,638,350,494]`, height 5766.

### 4.5 Motion
- **Sticky TOC:** `aside.legal-sidebar` is `position:sticky; top:32px` (measured at viewport top 32 while scrolled to 1500). There is **no scroll-spy**: no active-link state is set by JS and the route chunk has no observers. The only state is CSS `:target`, which turns `.legal-section:target h2` **#12889a** after a TOC click (verified). Clicking a TOC link smooth-scrolls (`html{scroll-behavior:smooth}`) to the section with `scroll-margin-top:40px` and sets the hash.
- TOC link hover: color → #12889a and `translateX(2px)`, `transition: color .16s ease, transform .16s cubic-bezier(.23,1,.32,1)`.
- Tab hover: color → #12889a (`color .16s ease, background .16s ease`). Doc-footer link hover: #12889a.
- Reduced motion: TOC/tab transitions and transforms are `none`.
- No entrance animations; only the footer birds run.

---

## 5. Route `/terms`
Same template and CSS as /privacy (same page chunk `7b1943cd942f78a9`), with these differences:
- Skip link "Read terms of service". Tabs: "Terms" is `aria-current=page` (white pill), "Privacy" is inactive.
- h1 **"Terms of Service"**. **No `p.legal-intro`**, so the heading is `[460,204,720,186]` and the date is "Last updated · April 30, 2025" at y 371.
- Columns start at y 462. Sidebar `[180,462,220,492]` with 14 TOC links. Page height 7031 (1280: 6953; 390: 9107).
- Section outline (ids, h2/h3 verbatim; body as word counts):

| id | h2 | Content |
|---|---|---|
| `introduction` | Introduction | p 30, p 29 |
| `service-description` | Service Description | p 31 |
| `user-accounts` | User Accounts | h3 "Account Creation" p 37 · h3 "Account Eligibility" p 26 · h3 "Account Termination" p 39 |
| `user-responsibilities` | User Responsibilities | h3 "Accurate Information" p 23 · h3 "Authorized Access" p 40 · h3 "Prohibited Uses" p 7 + ul[6 items, 79 words] |
| `connected-services` | Connected Services | h3 "Third-Party Accounts" p 44 · h3 "Authorization" p 28 · h3 "Revocation" p 38 |
| `intellectual-property` | Intellectual Property | h3 "Merlin Content" p 26 · h3 "User Content" p 51 · h3 "Feedback" p 31 |
| `subscription-and-billing` | Subscription and Billing | h3 "Pricing" p 31 · h3 "Free Trial" p 32 · h3 "Payment" p 28 · h3 "Cancellation" p 35 |
| `limitation-of-liability` | Limitation of Liability | h3 "Disclaimer of Warranties" p 37 · h3 "Limitation of Liability" p 48 + ul[4 items, 41 words] · h3 "Service Interruptions" p 29 |
| `indemnification` | Indemnification | p 52 |
| `modifications-to-terms` | Modifications to Terms | p 45, p 40 |
| `governing-law` | Governing Law | p 38 |
| `severability` | Severability | p 25 |
| `entire-agreement` | Entire Agreement | p 31 |
| `contact-us` | Contact Us | p 11, p 2 containing a `mailto:team@merlin.computer` link (rendered #12889a underlined) |
The TOC labels equal the h2 texts. 40 p, 19 h3 (rendered 16px/24 500 #505a44), 2 ul.

---

## 6. Color tokens used on these routes (hex from CSS, matching computed rgb)
`#343630` page text/blog h1 · `#3b3e36` featured h2 · `#45493f` story h3 · `#12889a` hover accent / prose links · `#20b8cf` focus ring, blockquote bar, handwritten · `#218c9b` / `#edf8f9` "Latest story" pill · `#eef8f8` story-arrow hover bg · `#eaece6` story dividers · `#e7ebe1` article-end/hr rule · `#f2f2ef` image placeholder · `#686e60` prose body · `#454d3d` strong/headings rendered · `#363d2f` heading base · `#4e5945` blockquote · `#85877f` intro p · `#888b84` eyebrow · `#92948e` meta time · `#696e63` meta author · `#92968a` story category · `#8f9487` story arrow · `#9a9c95` section span · `#74796b` manifesto link · `#878c80` back link · `#92978b` author time · `#969c8e` article end · legal: `#41463c` base, `#363c30` h1, `#414a36` h2, `#505a44` h3, `#777f6d` body, `#818879` intro, `#929889` date, `#464e3d` TOC label, `#8b9281` TOC links, `#eceee8` borders, `#f5f6f3` tab track, `#353c2e` / `#878e7e` tabs, `#78836b` doc-footer links, `#a0aa94` list markers · nav dot `#00c8e0`.

## 7. Things not captured / constraints
- **Copy policy:** article bodies and the privacy/terms body text were deliberately **not transcribed**. Only headings, metadata and word counts are recorded. `reference/pages/*.html` contains the live text for markup reference only; the builder must generate placeholder paragraphs of matching length (`structure[].words`).
- The privacy intro sentence (19 words) is treated as legal body text and was not transcribed; use the meta description or a placeholder of 19 words.
- Sanity Live (`SanityLiveStream`, visual editing) is CMS plumbing with no visual output; omit it.
- Sanity serves AVIF via `auto=format`; local covers are WebP at the same 1600px width, which is visually equivalent but not byte-identical.
- No blog filters, categories UI, pagination, search, TOC or reading-progress bar exist on the live site, so there is nothing to build for them.
