// Shared blog shell (blog_layout chunk): main#top + skip link + corner nav, page content, closing footer.
import { useEffect } from 'react'
import '../../styles/blog.css'
import HeroNav from '../hero/HeroNav.jsx'
import Footer from '../Footer.jsx'

export function useDocumentMeta(title, description) {
  useEffect(() => {
    document.title = title
    const meta = document.querySelector('meta[name="description"]')
    if (meta && description) meta.setAttribute('content', description)
  }, [title, description])
}

export default function BlogLayout({ children }) {
  return (
    <main className="merlin-story site-layout blog_page__bLGfe" id="top">
      <a href="#blog-content" className="skip-link">
        Read the blog
      </a>
      <div className="site-container">
        <header className="blog_navigation__bQ9ND">
          <HeroNav />
        </header>
      </div>
      {children}
      <Footer />
    </main>
  )
}
