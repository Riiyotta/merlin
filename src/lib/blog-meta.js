import { useEffect } from 'react'

// Per-article head tags for /blog/:slug, matching the live <head> (CLONE_SPEC_PAGES_B.md §0.5): the
// description, og:title/og:description and twitter:title/twitter:description all equal the post
// title; og:type is "article" with article:published_time + article:author; and the site-wide
// og:site_name, og:image* and twitter:image* tags are absent. Every touched tag is restored on unmount,
// so client-side navigation back to other routes gets the site-wide tags again.
const SITE_ONLY = [
  'meta[property="og:site_name"]',
  'meta[property="og:image"]',
  'meta[property="og:image:width"]',
  'meta[property="og:image:height"]',
  'meta[property="og:image:alt"]',
  'meta[name="twitter:image"]',
  'meta[name="twitter:image:alt"]',
]

export function useArticleMeta(post) {
  useEffect(() => {
    const head = document.head
    const undo = []
    const prevTitle = document.title
    document.title = `${post.title} — Merlin`
    undo.push(() => (document.title = prevTitle))

    const set = (attr, key, content) => {
      let el = head.querySelector(`meta[${attr}="${key}"]`)
      if (el) {
        const prev = el.getAttribute('content')
        el.setAttribute('content', content)
        undo.push(() => el.setAttribute('content', prev))
      } else {
        el = document.createElement('meta')
        el.setAttribute(attr, key)
        el.setAttribute('content', content)
        head.appendChild(el)
        undo.push(() => el.remove())
      }
    }
    set('name', 'description', post.metaDescription)
    set('property', 'og:title', post.title)
    set('property', 'og:description', post.metaDescription)
    set('property', 'og:type', 'article')
    set('property', 'article:published_time', post.date)
    set('property', 'article:author', post.author)
    set('name', 'twitter:card', 'summary_large_image')
    set('name', 'twitter:title', post.title)
    set('name', 'twitter:description', post.metaDescription)

    for (const sel of SITE_ONLY) {
      const el = head.querySelector(sel)
      if (!el) continue
      const next = el.nextSibling
      el.remove()
      undo.push(() => head.insertBefore(el, next && next.parentNode === head ? next : null))
    }
    return () => undo.reverse().forEach((fn) => fn())
  }, [post])
}
