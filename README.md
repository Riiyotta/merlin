# Merlin clone: information architecture

Local clone of the merlin.computer site (React 18 + Vite). This README covers the IA files in the project root.

**Hand-edit only `ia.json`.** `IA.md` and `matrix.csv` are generated from it and get overwritten.

```bash
node validate.mjs   # hard checks: route sum, template count, section references, categories
node build.mjs      # regenerates IA.md and matrix.csv
```

Run both after any change to routes or sections. `validate.mjs` must say "All hard invariants reconcile" before you trust the generated files.

## What the data shows

- **27 routes, 7 templates, 34 sections.** 20 of the routes are blog posts that share one template. The other 7 routes use 6 templates (privacy and terms share one).
- **Only 3 sections are shared across templates:** the skip link, the corner nav and the closing footer. They appear on 26 routes, every route except the install page. The other 31 sections each belong to one template, so they should stay page-local until a second page needs them.
- **The home page is the large build.** It carries 13 of the 34 sections, 10 of them used nowhere else (hero, notification landscape, logo row, five product sections, FAQ, floating nav).
- **The install page is the only route without full chrome.** It has a brand-only header and no nav or footer, so it is the one `minimal` template.
- **The ask-Merlin form is shared below the section level.** `support.home-faq` and `support.pricing-faq` are separate sections (different markup and question counts) that both embed `src/components/faq/AskMerlinForm.jsx`. The reuse table does not show this.

## Routing notes that are not routes

- `/download?start=1` is the same page as `/download`: it starts the download, then removes the query. In the clone the download goes to a local stub file, not the real installer.
- An unknown top-level path falls back to the home page. An unknown `/blog/<slug>` redirects to `/blog`.
- The 20 blog posts are 19 posts from the live sitemap plus one featured post that is not in the sitemap and has no cover image.
- Long-form text on the manifesto, privacy, terms and blog post pages, and the pricing FAQ answers, is placeholder text written for the clone.

## Sections linked to code

Every section has an `implementedBy` field naming the component that renders it. The paths were checked against the files on disk.
