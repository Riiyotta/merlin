// Shared /privacy + /terms template (page chunk privacy_page-7b1943cd942f78a9; markup from
// reference/pages/{privacy,terms}.html; CLONE_SPEC_PAGES_B.md §4–5). Styles come verbatim from
// e261c04d0a2d5dfe.css via src/styles/legal.css. No JS motion: TOC jumps use native anchors with
// html{scroll-behavior:smooth}, the active heading is CSS :target, and there is no scroll-spy.
import { useLayoutEffect } from 'react'
import '../../styles/legal.css'
import HeroNav from '../hero/HeroNav.jsx'
import Footer from '../Footer.jsx'
import { usePageMeta } from '../pricing/usePageMeta.js'

const TABS = [
  { href: '/privacy', label: 'Privacy' },
  { href: '/terms', label: 'Terms' },
]

function Block({ block }) {
  if (block.type === 'h3') return <h3>{block.text}</h3>
  if (block.type === 'ul')
    return (
      <ul>
        {block.items.map((item, i) => (
          <li key={i}>{item}</li>
        ))}
      </ul>
    )
  if (block.type === 'email')
    return (
      <p>
        {block.label} <a href={`mailto:${block.email}`}>{block.email}</a>
      </p>
    )
  return <p>{block.text}</p>
}

// Deep links (/privacy#security, /terms#governing-law). Live is server-rendered, so the browser's
// load-time fragment jump lands the section at scroll-padding-top 35 + scroll-margin-top 40 = 75px
// (35 + 24 = 59px at <=640) and sets :target. Here the sections only exist after the lazy route chunk
// mounts, so the native jump already missed. Re-running the fragment navigation (same URL, so it
// replaces rather than pushes a history entry) applies the same scroll-padding/scroll-margin and :target;
// scroll-behavior is forced to auto for that one jump so it is instant like the native load-time jump.
function useInitialHashJump() {
  useLayoutEffect(() => {
    const { hash } = window.location
    if (!hash || hash.length < 2) return
    let id
    try {
      id = decodeURIComponent(hash.slice(1))
    } catch {
      return
    }
    if (!document.getElementById(id)) return
    const root = document.documentElement
    let jumpedTo = null
    let cancelled = false
    const jump = () => {
      if (cancelled) return
      const prev = root.style.scrollBehavior
      root.style.scrollBehavior = 'auto'
      window.location.replace(hash)
      root.style.scrollBehavior = prev
      jumpedTo = window.scrollY
    }
    jump()
    // Re-align once webfonts settle, unless the reader has already scrolled away.
    document.fonts?.ready.then(() => {
      if (jumpedTo !== null && Math.abs(window.scrollY - jumpedTo) < 2) jump()
    })
    return () => {
      cancelled = true
    }
  }, [])
}

export default function LegalPage({ page, current, metaTitle, metaDescription }) {
  usePageMeta(metaTitle, metaDescription)
  useInitialHashJump()

  return (
    <main className="merlin-story site-layout legal-page" id="top">
      <a href="#legal-content" className="skip-link">
        {page.skipLabel}
      </a>
      <div className="site-container">
        <header className="legal-navigation">
          <HeroNav />
        </header>
      </div>
      <div className="legal-document" id="legal-content">
        <header className="legal-heading">
          <nav className="legal-tabs" aria-label="Legal documents">
            {TABS.map((tab) => (
              <a key={tab.href} href={tab.href} aria-current={tab.href === current ? 'page' : undefined}>
                {tab.label}
              </a>
            ))}
          </nav>
          <h1>{page.title}</h1>
          {page.intro && <p className="legal-intro">{page.intro}</p>}
          <p className="legal-date">
            Last updated <span aria-hidden="true">·</span> {page.date}
          </p>
        </header>
        <div className="legal-columns">
          <aside className="legal-sidebar">
            <nav className="legal-contents" aria-label="On this page">
              <span className="legal-contents-label">On this page</span>
              {page.sections.map((s) => (
                <a key={s.id} href={`#${s.id}`}>
                  {s.title}
                </a>
              ))}
            </nav>
          </aside>
          <article className="legal-prose" aria-label={page.title}>
            {page.sections.map((s) => (
              <section key={s.id} className="legal-section" id={s.id} aria-labelledby={`${s.id}-title`}>
                <h2 id={`${s.id}-title`}>{s.title}</h2>
                {s.blocks.map((block, i) => (
                  <Block key={i} block={block} />
                ))}
              </section>
            ))}
            <footer className="legal-document-footer">
              <a href="mailto:team@merlin.computer">
                Contact our team <span aria-hidden="true">↗</span>
              </a>
              <a href="#legal-content">
                Back to top <span aria-hidden="true">↑</span>
              </a>
            </footer>
          </article>
        </div>
      </div>
      <Footer />
    </main>
  )
}
