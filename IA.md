# Local clone of https://www.merlin.computer (src/ in this project)

Source: Local clone of https://www.merlin.computer (src/ in this project)
Status: **measured-from-clone-source** · production approved: **false**
27 routes · 7 templates · 34 unique sections

> Generated from `ia.json` by `build.mjs`. Edit the JSON, not this file.

## Shape of the site

The largest 3 templates (Blog post, Legal document, Home) account for 23 of 27 routes (85%). The remaining 4 routes span 4 templates.

| template | routes | share |
|---|---:|---:|
| Blog post | 20 | 74% |
| Legal document | 2 | 7% |
| Home | 1 | 4% |
| Pricing | 1 | 4% |
| Install | 1 | 4% |
| Manifesto | 1 | 4% |
| Blog index | 1 | 4% |

## Page chrome

**26 routes carry chrome = `full`** — Home, Pricing, Manifesto, Blog index, Blog post, Legal document.

**1 routes carry chrome = `minimal`** — Install.

## Sections by reuse

How widely a section is shared determines whether it belongs in a shared
component library or stays local to its page.

| section | category | templates | routes | implementation | scope |
|---|---|---:|---:|---|---|
| `shell.skip-link` | SHELL | 6 | 26 | `Inline a.skip-link in each page file (Home.jsx, Pricing.jsx, Manifesto.jsx, blog/BlogLayout.jsx, legal/LegalPage.jsx)` | Every route except the install page. |
| `shell.corner-nav` | SHELL | 6 | 26 | `src/components/hero/HeroNav.jsx` | Every route except the install page. |
| `shell.closing-footer` | SHELL | 6 | 26 | `src/components/Footer.jsx (clock in src/components/footer/FooterClock.jsx)` | Every route except the install page. |
| `content.article-header` | CONTENT | 1 | 20 | `src/pages/BlogPost.jsx` | Every blog post. |
| `content.article-body` | CONTENT | 1 | 20 | `src/components/blog/Prose.jsx` | Every blog post. |
| `content.article-end` | CONTENT | 1 | 20 | `src/pages/BlogPost.jsx` | Every blog post. |
| `content.legal-heading` | CONTENT | 1 | 2 | `src/components/legal/LegalPage.jsx` | Privacy and terms pages. |
| `content.legal-contents` | CONTENT | 1 | 2 | `src/components/legal/LegalPage.jsx` | Privacy and terms pages. |
| `content.legal-body` | CONTENT | 1 | 2 | `src/components/legal/LegalPage.jsx` | Privacy and terms pages. |
| `shell.floating-nav` | SHELL | 1 | 1 | `src/components/FloatingNav.jsx` | Home page only. |
| `shell.install-header` | SHELL | 1 | 1 | `src/pages/Download.jsx` | Install page only. |
| `hero.home-headline` | HERO | 1 | 1 | `src/components/Hero.jsx (section.story-hero)` | Home page only. |
| `hero.landscape-notifications` | HERO | 1 | 1 | `src/components/Hero.jsx (section.hero-landscape) with hero/HeroNotifications.jsx and hero/NotificationDetail.jsx` | Home page only. |
| `hero.pricing-headline` | HERO | 1 | 1 | `src/pages/Pricing.jsx` | Pricing page only. |
| `proof.company-logos` | PROOF | 1 | 1 | `src/components/Companies.jsx` | Home page only. |
| `product.context-routines` | PRODUCT | 1 | 1 | `src/components/Routines.jsx (routines/RoutineTimeline.jsx)` | Home page only. |
| `product.browser-tasks` | PRODUCT | 1 | 1 | `src/components/Browser.jsx (browser/MockSites.jsx)` | Home page only. |
| `product.meetings-projects` | PRODUCT | 1 | 1 | `src/components/Meetings.jsx (meetings/MeetingLandscape.jsx)` | Home page only. |
| `product.companion-demos` | PRODUCT | 1 | 1 | `src/components/Companion.jsx (companion/*)` | Home page only. |
| `product.privacy-trust` | PRODUCT | 1 | 1 | `src/components/Privacy.jsx (privacy/DecodingHeadline.jsx)` | Home page only. |
| `commerce.plan-cards` | COMMERCE | 1 | 1 | `src/components/pricing/PricingPlans.jsx` | Pricing page only. |
| `commerce.included-features` | COMMERCE | 1 | 1 | `src/components/pricing/PricingIncluded.jsx` | Pricing page only. |
| `support.home-faq` | SUPPORT | 1 | 1 | `src/components/Faq.jsx (faq/AskMerlinForm.jsx)` | Home page only. |
| `support.pricing-faq` | SUPPORT | 1 | 1 | `src/components/pricing/PricingFaq.jsx (faq/AskMerlinForm.jsx)` | Pricing page only. |
| `onboarding.install-intro` | ONBOARDING | 1 | 1 | `src/components/download/InstallIntro.jsx` | Install page only. |
| `onboarding.install-steps` | ONBOARDING | 1 | 1 | `src/pages/Download.jsx` | Install page only. |
| `content.manifesto-opening` | CONTENT | 1 | 1 | `src/pages/Manifesto.jsx (manifesto/TimeOfDayCopy.jsx)` | Manifesto page only. |
| `content.manifesto-understanding` | CONTENT | 1 | 1 | `src/pages/Manifesto.jsx (manifesto/Mention.jsx)` | Manifesto page only. |
| `content.manifesto-action` | CONTENT | 1 | 1 | `src/pages/Manifesto.jsx` | Manifesto page only. |
| `content.manifesto-ending` | CONTENT | 1 | 1 | `src/pages/Manifesto.jsx (manifesto/Signature.jsx)` | Manifesto page only. |
| `content.blog-intro` | CONTENT | 1 | 1 | `src/pages/Blog.jsx` | Blog index only. |
| `content.blog-featured-story` | CONTENT | 1 | 1 | `src/pages/Blog.jsx` | Blog index only. |
| `content.blog-story-list` | CONTENT | 1 | 1 | `src/pages/Blog.jsx` | Blog index only. |
| `content.blog-handwritten-aside` | CONTENT | 1 | 1 | `src/pages/Blog.jsx` | Blog index only. |

**3 shared sections** appear in more than one template and belong in a component library.

**31 single-use sections** appear in exactly one template. Building these
as "reusable" components up front would be speculative — keep them page-local
until a second caller actually appears.

## Templates

### Home — `template.home`

1 route · `/` · chrome: **full**

| # | category | section | |
|---:|---|---|---|
| 1 | SHELL | `shell.skip-link` | shared ×6 |
| 2 | SHELL | `shell.corner-nav` | shared ×6 |
| 3 | HERO | `hero.home-headline` | page-local |
| 4 | HERO | `hero.landscape-notifications` | page-local |
| 5 | PROOF | `proof.company-logos` | page-local |
| 6 | PRODUCT | `product.context-routines` | page-local |
| 7 | PRODUCT | `product.browser-tasks` | page-local |
| 8 | PRODUCT | `product.meetings-projects` | page-local |
| 9 | PRODUCT | `product.companion-demos` | page-local |
| 10 | PRODUCT | `product.privacy-trust` | page-local |
| 11 | SUPPORT | `support.home-faq` | page-local |
| 12 | SHELL | `shell.closing-footer` | shared ×6 |
| 13 | SHELL | `shell.floating-nav` | page-local |

### Pricing — `template.pricing`

1 route · `/pricing` · chrome: **full**

| # | category | section | |
|---:|---|---|---|
| 1 | SHELL | `shell.skip-link` | shared ×6 |
| 2 | SHELL | `shell.corner-nav` | shared ×6 |
| 3 | HERO | `hero.pricing-headline` | page-local |
| 4 | COMMERCE | `commerce.plan-cards` | page-local |
| 5 | COMMERCE | `commerce.included-features` | page-local |
| 6 | SUPPORT | `support.pricing-faq` | page-local |
| 7 | SHELL | `shell.closing-footer` | shared ×6 |

### Install — `template.install`

1 route · `/download` · chrome: **minimal**

| # | category | section | |
|---:|---|---|---|
| 1 | SHELL | `shell.install-header` | page-local |
| 2 | ONBOARDING | `onboarding.install-intro` | page-local |
| 3 | ONBOARDING | `onboarding.install-steps` | page-local |

### Manifesto — `template.manifesto`

1 route · `/manifesto` · chrome: **full**

| # | category | section | |
|---:|---|---|---|
| 1 | SHELL | `shell.skip-link` | shared ×6 |
| 2 | SHELL | `shell.corner-nav` | shared ×6 |
| 3 | CONTENT | `content.manifesto-opening` | page-local |
| 4 | CONTENT | `content.manifesto-understanding` | page-local |
| 5 | CONTENT | `content.manifesto-action` | page-local |
| 6 | CONTENT | `content.manifesto-ending` | page-local |
| 7 | SHELL | `shell.closing-footer` | shared ×6 |

### Blog index — `template.blog-index`

1 route · `/blog` · chrome: **full**

| # | category | section | |
|---:|---|---|---|
| 1 | SHELL | `shell.skip-link` | shared ×6 |
| 2 | SHELL | `shell.corner-nav` | shared ×6 |
| 3 | CONTENT | `content.blog-intro` | page-local |
| 4 | CONTENT | `content.blog-featured-story` | page-local |
| 5 | CONTENT | `content.blog-story-list` | page-local |
| 6 | CONTENT | `content.blog-handwritten-aside` | page-local |
| 7 | SHELL | `shell.closing-footer` | shared ×6 |

### Blog post — `template.blog-post`

20 routes · `/blog/{slug}` · chrome: **full**

| # | category | section | |
|---:|---|---|---|
| 1 | SHELL | `shell.skip-link` | shared ×6 |
| 2 | SHELL | `shell.corner-nav` | shared ×6 |
| 3 | CONTENT | `content.article-header` | page-local |
| 4 | CONTENT | `content.article-body` | page-local |
| 5 | CONTENT | `content.article-end` | page-local |
| 6 | SHELL | `shell.closing-footer` | shared ×6 |

### Legal document — `template.legal`

2 routes · `/privacy`, `/terms` · chrome: **full**

| # | category | section | |
|---:|---|---|---|
| 1 | SHELL | `shell.skip-link` | shared ×6 |
| 2 | SHELL | `shell.corner-nav` | shared ×6 |
| 3 | CONTENT | `content.legal-heading` | page-local |
| 4 | CONTENT | `content.legal-contents` | page-local |
| 5 | CONTENT | `content.legal-body` | page-local |
| 6 | SHELL | `shell.closing-footer` | shared ×6 |

## Section reference

### SHELL

_Page chrome shared across routes: skip link, navigation, footer, floating nav, install header._

**`shell.skip-link`** — Visually hidden link that becomes visible on keyboard focus and jumps past the navigation to the page's main content; its label and target are page-specific.

· Every route except the install page. · appears on 26 routes · implemented by `Inline a.skip-link in each page file (Home.jsx, Pricing.jsx, Manifesto.jsx, blog/BlogLayout.jsx, legal/LegalPage.jsx)`

**`shell.corner-nav`** — Top-left navigation with the brand link and page links and a spring-animated indicator dot that follows hover and focus and rests on the current page. Pages where no link matches show no dot until the first hover. On the home page it sits inside the hero section.

· Every route except the install page. · appears on 26 routes · implemented by `src/components/hero/HeroNav.jsx`

**`shell.closing-footer`** — Closing footer: live clock showing the current time plus three minutes, the Download button, drifting ASCII birds over an ASCII beach, and a single row of brand, copyright and page links (Pricing, Manifesto, Blog, Privacy, Terms, Contact).

· Every route except the install page. · appears on 26 routes · implemented by `src/components/Footer.jsx (clock in src/components/footer/FooterClock.jsx)`

**`shell.floating-nav`** — Fixed pill navigation that slides up after 100px of scroll and hides near the page bottom and while the dark privacy section is on screen.

· Home page only. · appears on 1 routes · implemented by `src/components/FloatingNav.jsx`

**`shell.install-header`** — Brand-only header of the install page: app icon and name linking home, with no navigation links.

· Install page only. · appears on 1 routes · implemented by `src/pages/Download.jsx`

### HERO

_Page-opening header block._

**`hero.home-headline`** — Two-line headline with a one-time colour sweep on load, a one-paragraph description and the primary Download button.

· Home page only. · appears on 1 routes · implemented by `src/components/Hero.jsx (section.story-hero)`

**`hero.landscape-notifications`** — Full-width landscape photo with a stack of animated notification cards that open into detail panels (meeting brief, launch deck, email draft), with a scroll parallax on the photo.

· Home page only. · appears on 1 routes · implemented by `src/components/Hero.jsx (section.hero-landscape) with hero/HeroNotifications.jsx and hero/NotificationDetail.jsx`

**`hero.pricing-headline`** — Two-line pricing headline and subtitle in the same hero shell as the home page, with no download button and no load animation.

· Pricing page only. · appears on 1 routes · implemented by `src/pages/Pricing.jsx`

### PROOF

_Social proof: customer or employer logos._

**`proof.company-logos`** — Single row of employer logos under a "Used by professionals at" label.

· Home page only. · appears on 1 routes · implemented by `src/components/Companies.jsx`

### PRODUCT

_Product explanation and capability modules on the home page._

**`product.context-routines`** — Heading with inline app tiles, a copy column, a Gmail preview card and a three-column routine walkthrough whose timeline plays step by step while in view.

· Home page only. · appears on 1 routes · implemented by `src/components/Routines.jsx (routines/RoutineTimeline.jsx)`

**`product.browser-tasks`** — Pinned scroll stage where four mock-site cards (flight booking, food delivery, grocery shopping, recruiting) flip in 3D with snapping and an elastic landing; each card is an interactive mock site.

· Home page only. · appears on 1 routes · implemented by `src/components/Browser.jsx (browser/MockSites.jsx)`

**`product.meetings-projects`** — Two panels under one heading: a meetings panel with a transcript/notes switch, action-item toggles and an audio player, and a projects panel of four file cards.

· Home page only. · appears on 1 routes · implemented by `src/components/Meetings.jsx (meetings/MeetingLandscape.jsx)`

**`product.companion-demos`** — Headline that retypes on "Rephrase word" followed by auto-advancing Photoshop, Slack and Chrome demos with a spring tab indicator.

· Home page only. · appears on 1 routes · implemented by `src/components/Companion.jsx (companion/*)`

**`product.privacy-trust`** — Black full-bleed section with a headline that decodes from code characters and four trust cards whose illustrations animate on hover.

· Home page only. · appears on 1 routes · implemented by `src/components/Privacy.jsx (privacy/DecodingHeadline.jsx)`

### COMMERCE

_Pricing plans and what they include._

**`commerce.plan-cards`** — Three monthly plan cards (name, price, credit allowance, feature list), each with its own download button.

· Pricing page only. · appears on 1 routes · implemented by `src/components/pricing/PricingPlans.jsx`

**`commerce.included-features`** — Six-item grid of the places Merlin works, each with a section icon, title and short description.

· Pricing page only. · appears on 1 routes · implemented by `src/components/pricing/PricingIncluded.jsx`

### SUPPORT

_Questions and answers._

**`support.home-faq`** — Five-item accordion on a white band plus an ask-Merlin input that shows a loading state, then a reply (a local mock in the clone).

· Home page only. · appears on 1 routes · implemented by `src/components/Faq.jsx (faq/AskMerlinForm.jsx)`

**`support.pricing-faq`** — Six-item accordion built from native details elements with a rotating plus icon, followed by the shared ask-Merlin input.

· Pricing page only. · appears on 1 routes · implemented by `src/components/pricing/PricingFaq.jsx (faq/AskMerlinForm.jsx)`

### ONBOARDING

_Getting the app installed._

**`onboarding.install-intro`** — Install page introduction: heading, description, the "download again" action and an alternate-chip link, driven by Mac and chip detection that starts the download from a hidden frame.

· Install page only. · appears on 1 routes · implemented by `src/components/download/InstallIntro.jsx`

**`onboarding.install-steps`** — Numbered list of three install steps, each with a screenshot.

· Install page only. · appears on 1 routes · implemented by `src/pages/Download.jsx`

### CONTENT

_Editorial, article and legal body content._

**`content.manifesto-opening`** — Poster opening: time-of-day title copy with two large handwriting overlays behind it.

· Manifesto page only. · appears on 1 routes · implemented by `src/pages/Manifesto.jsx (manifesto/TimeOfDayCopy.jsx)`

**`content.manifesto-understanding`** — Full-width photo followed by the understanding passage with inline app mentions and a handwritten note.

· Manifesto page only. · appears on 1 routes · implemented by `src/pages/Manifesto.jsx (manifesto/Mention.jsx)`

**`content.manifesto-action`** — Full-width photo followed by the action passage with a time-of-day paragraph and a handwritten note.

· Manifesto page only. · appears on 1 routes · implemented by `src/pages/Manifesto.jsx`

**`content.manifesto-ending`** — Full-width photo followed by the closing heading, a time-of-day finish paragraph and the signature whose circle draws itself once at 50% in view.

· Manifesto page only. · appears on 1 routes · implemented by `src/pages/Manifesto.jsx (manifesto/Signature.jsx)`

**`content.blog-intro`** — Centred serif intro heading and a two-line standfirst of the blog index.

· Blog index only. · appears on 1 routes · implemented by `src/pages/Blog.jsx`

**`content.blog-featured-story`** — Two-column featured card with a 4:3 image, a "Latest story" pill, title and read link; the image zooms slightly on hover.

· Blog index only. · appears on 1 routes · implemented by `src/pages/Blog.jsx`

**`content.blog-story-list`** — "More from Merlin" list of 19 rows (category, title, arrow) separated by hairlines.

· Blog index only. · appears on 1 routes · implemented by `src/pages/Blog.jsx`

**`content.blog-handwritten-aside`** — Short rotated handwriting line that links to the manifesto.

· Blog index only. · appears on 1 routes · implemented by `src/pages/Blog.jsx`

**`content.article-header`** — Back link to all stories plus the header block: eyebrow, serif title, author row with date, and an optional cover image (absent on the featured post).

· Every blog post. · appears on 20 routes · implemented by `src/pages/BlogPost.jsx`

**`content.article-body`** — Reading column of paragraphs, headings, lists and blockquotes rendered from a structure outline (placeholder text in the clone).

· Every blog post. · appears on 20 routes · implemented by `src/components/blog/Prose.jsx`

**`content.article-end`** — Article footer with a thank-you line and a "Back to all stories" link.

· Every blog post. · appears on 20 routes · implemented by `src/pages/BlogPost.jsx`

**`content.legal-heading`** — Tab pill switching between Privacy and Terms, large serif title, optional intro paragraph and a last-updated line.

· Privacy and terms pages. · appears on 2 routes · implemented by `src/components/legal/LegalPage.jsx`

**`content.legal-contents`** — Sticky "On this page" table of contents with smooth-scroll links; becomes a horizontal scroll row below 640px.

· Privacy and terms pages. · appears on 2 routes · implemented by `src/components/legal/LegalPage.jsx`

**`content.legal-body`** — Numbered document sections with hairline rules and a document footer (contact link, back to top); the targeted section heading turns teal.

· Privacy and terms pages. · appears on 2 routes · implemented by `src/components/legal/LegalPage.jsx`
