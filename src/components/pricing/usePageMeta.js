import { useEffect } from 'react'

// Sets <title>, meta description and (optionally) <link rel="canonical"> for routes that specify
// their own (CLONE_SPEC_PAGES_A.md §2, §3, §4). The og/twitter tags on these routes are the
// homepage's and come from index.html. On unmount the previous values are restored so client-side
// navigation back to a route without its own meta (e.g. /) does not inherit this page's tags.
export function usePageMeta(title, description, canonical) {
  useEffect(() => {
    const prevTitle = document.title
    document.title = title

    let meta = document.querySelector('meta[name="description"]')
    const createdMeta = !meta
    if (!meta) {
      meta = document.createElement('meta')
      meta.setAttribute('name', 'description')
      document.head.appendChild(meta)
    }
    const prevDescription = meta.getAttribute('content')
    meta.setAttribute('content', description)

    let link = null
    let createdLink = false
    let prevHref = null
    if (canonical) {
      link = document.querySelector('link[rel="canonical"]')
      createdLink = !link
      if (!link) {
        link = document.createElement('link')
        link.setAttribute('rel', 'canonical')
        document.head.appendChild(link)
      }
      prevHref = link.getAttribute('href')
      link.setAttribute('href', canonical)
    }

    return () => {
      document.title = prevTitle
      if (createdMeta) meta.remove()
      else if (prevDescription != null) meta.setAttribute('content', prevDescription)
      if (link) {
        if (createdLink) link.remove()
        else if (prevHref != null) link.setAttribute('href', prevHref)
      }
    }
  }, [title, description, canonical])
}
