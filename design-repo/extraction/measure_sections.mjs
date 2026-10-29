#!/usr/bin/env node
// Re-measure section heights at 1440px from a running build of the clone (R9 evidence).
//
//   npx vite build --outDir <dist> && npx vite preview --outDir <dist> --port 5708
//   NODE_PATH="$(npm root -g)" node extraction/measure_sections.mjs [--base http://localhost:5708] [--write]
//
// Playwright is resolved at RUNTIME (env PLAYWRIGHT_MODULE, else NODE_PATH entries, else `npm root -g`);
// no machine path is stored in this repo. Without --write the JSON is printed; with --write it replaces the
// "sectionHeights" key of extraction/measured-values.json (every other key is preserved).
import fs from 'node:fs'
import path from 'node:path'
import { execSync } from 'node:child_process'
import { fileURLToPath, pathToFileURL } from 'node:url'

const HERE = path.dirname(fileURLToPath(import.meta.url))
const REPO = path.dirname(HERE)
const args = process.argv.slice(2)
const BASE = (args.includes('--base') ? args[args.indexOf('--base') + 1] : process.env.MEASURE_BASE_URL) || 'http://localhost:5708'
const WRITE = args.includes('--write')
const VIEWPORT = { width: 1440, height: 900 }
// One real slug from src/data/blog-posts.json (the first post that is in the sitemap).
const BLOG_SLUG = 'how-to-share-a-google-calendar-on-iphone-in-2025'

async function loadPlaywright() {
  const cands = []
  if (process.env.PLAYWRIGHT_MODULE) cands.push(process.env.PLAYWRIGHT_MODULE)
  for (const p of (process.env.NODE_PATH || '').split(path.delimiter).filter(Boolean)) cands.push(path.join(p, 'playwright', 'index.mjs'))
  try { cands.push(path.join(execSync('npm root -g').toString().trim(), 'playwright', 'index.mjs')) } catch {}
  for (const c of cands) {
    if (fs.existsSync(c)) return (await import(pathToFileURL(c).href)).default ?? (await import(pathToFileURL(c).href))
  }
  return await import('playwright')
}

const jl = (rel) => JSON.parse(fs.readFileSync(path.join(REPO, rel), 'utf8'))
const templates = jl('templates/templates.json').templates
const routes = jl('templates/routes.json').routes
const sections = {}
for (const f of fs.readdirSync(path.join(REPO, 'sections')).filter((f) => f.endsWith('.json'))) {
  const s = jl(path.join('sections', f)); sections[s.id] = s
}

const pw = await loadPlaywright()
const browser = await pw.chromium.launch()
const page = await browser.newPage({ viewport: VIEWPORT, reducedMotion: 'no-preference' })
const out = {
  _note: 'Measured from a LOCAL vite preview of the BUILT clone (not the live site) at 1440x900 by extraction/measure_sections.mjs. heightPx = getBoundingClientRect().height of the section contract domAnchor after a full scroll pass; position fixed/sticky elements are inFlow:false and take no page height. Consumed by extraction/wrapper_gate.py.',
  viewport: VIEWPORT,
  measuredAt: new Date().toISOString().slice(0, 10),
  tool: 'playwright chromium (headless), extraction/measure_sections.mjs',
  baseUrl: 'local vite preview of the built clone',
  blogSlugMeasured: BLOG_SLUG,
  routes: {},
  candidateParts: {},
}

for (const r of routes) {
  const url = BASE + r.path.replace(':slug', BLOG_SLUG)
  await page.goto(url, { waitUntil: 'networkidle' })
  await page.evaluate(() => document.fonts.ready)
  // scroll pass to trigger reveal/lazy content, then back to top
  await page.evaluate(async () => {
    const step = 600
    for (let y = 0; y < document.documentElement.scrollHeight; y += step) { window.scrollTo(0, y); await new Promise((res) => setTimeout(res, 60)) }
    window.scrollTo(0, 0); await new Promise((res) => setTimeout(res, 300))
  })
  const tmpl = templates[r.template]
  const nodes = tmpl.nodes.map((n) => ({ section: n.section, variant: n.variant || null, domAnchor: sections[n.section].domAnchor, repeatable: !!n.repeatable }))
  const res = await page.evaluate((nodes) => {
    const used = new Set()
    const flow = (el) => { const pos = getComputedStyle(el).position; return { position: pos, inFlow: !(pos === 'fixed' || pos === 'sticky') } }
    const out = []
    for (const n of nodes) {
      const base = { section: n.section, variant: n.variant, domAnchor: n.domAnchor }
      let els = []
      try { els = [...document.querySelectorAll(n.domAnchor)].filter((e) => !used.has(e)) } catch (e) { els = [] }
      if (!els.length) { out.push({ ...base, heightPx: null, position: null, inFlow: null, missing: true }); continue }
      if (!n.repeatable) {
        const el = els[0]; used.add(el)
        out.push({ ...base, heightPx: Math.round(el.getBoundingClientRect().height), ...flow(el) })
        continue
      }
      if (n.section === 'blog.prose') {
        // one instance per h2-bounded chapter: lead = blocks before the first h2; each chapter = its h2 .. the
        // block before the next h2. Height = top of first block (minus margin-top) to bottom of last block
        // (plus margin-bottom), so collapsed margins between chapters are counted on both sides at most once each.
        const prose = els[0]; used.add(prose)
        const groups = []
        for (const c of prose.children) {
          if (c.tagName === 'H2' || !groups.length) groups.push({ title: c.tagName === 'H2' ? c.textContent.trim().slice(0, 60) : '(lead before first h2)', blocks: [] })
          groups[groups.length - 1].blocks.push(c)
        }
        groups.forEach((g, i) => {
          const f = g.blocks[0], l = g.blocks[g.blocks.length - 1]
          const top = f.getBoundingClientRect().top - parseFloat(getComputedStyle(f).marginTop || 0)
          const bot = l.getBoundingClientRect().bottom + parseFloat(getComputedStyle(l).marginBottom || 0)
          out.push({ ...base, instance: i, instanceLabel: g.title, blocks: g.blocks.length, heightPx: Math.round(bot - top), ...flow(prose), measuredAs: 'h2-bounded DOM range inside the domAnchor' })
        })
        continue
      }
      els.forEach((el, i) => { used.add(el); out.push({ ...base, instance: i, instanceLabel: el.id || null, heightPx: Math.round(el.getBoundingClientRect().height), ...flow(el) }) })
    }
    return { pageHeight: document.documentElement.scrollHeight, sections: out }
  }, nodes)
  // Scroll-mounted elements (the home floating nav only mounts after scrollY > 100): retry mid-page.
  if (res.sections.some((s) => s.missing)) {
    await page.evaluate(async () => { window.scrollTo(0, 1500); await new Promise((r) => setTimeout(r, 800)) })
    const retry = await page.evaluate((nodes) => nodes.map((n) => {
      const el = n.missing ? document.querySelector(n.domAnchor) : null
      if (!el) return n
      const pos = getComputedStyle(el).position
      return { ...n, heightPx: Math.round(el.getBoundingClientRect().height), position: pos, inFlow: !(pos === 'fixed' || pos === 'sticky'), missing: undefined, measuredAfterScrollY: 1500 }
    }), res.sections)
    res.sections = retry
    await page.evaluate(() => window.scrollTo(0, 0))
  }
  out.routes[r.path] = { template: r.template, url: r.path.replace(':slug', BLOG_SLUG), ...res }

  // candidate sub-parts for decomposition evidence (legal article, blog prose)
  if (r.template === 'legal' || r.template === 'blog-post') {
    out.candidateParts[r.path] = await page.evaluate((tmpl) => {
      const parts = []
      const h = (el) => (el ? Math.round(el.getBoundingClientRect().height) : null)
      if (tmpl === 'legal') {
        parts.push({ part: 'legal.sidebar (TOC aside)', heightPx: h(document.querySelector('aside.legal-sidebar')) })
        for (const s of document.querySelectorAll('article.legal-prose section.legal-section')) parts.push({ part: 'legal.section#' + s.id, heightPx: h(s) })
        parts.push({ part: 'legal.document-footer', heightPx: h(document.querySelector('footer.legal-document-footer')) })
      } else {
        const prose = document.querySelector('div.blog_prose__r_2py')
        const top = prose.getBoundingClientRect().top + window.scrollY
        const bottom = top + prose.getBoundingClientRect().height
        const h2s = [...prose.querySelectorAll('h2')].map((e) => ({ text: e.textContent.trim().slice(0, 60), y: e.getBoundingClientRect().top + window.scrollY }))
        let prev = { text: '(lead before first h2)', y: top }
        for (const x of [...h2s, { text: null, y: bottom }]) {
          parts.push({ part: 'prose chapter: ' + prev.text, heightPx: Math.round(x.y - prev.y) })
          prev = x
        }
      }
      return parts
    }, r.template)
  }
}
await browser.close()

if (WRITE) {
  const file = path.join(HERE, 'measured-values.json')
  const mv = JSON.parse(fs.readFileSync(file, 'utf8'))
  mv.sectionHeights = out
  fs.writeFileSync(file, JSON.stringify(mv, null, 2) + '\n') // same layout as Python json.dump(indent=2, ensure_ascii=False)
  console.log('wrote sectionHeights for', Object.keys(out.routes).length, 'routes')
} else {
  console.log(JSON.stringify(out, null, 2))
}
