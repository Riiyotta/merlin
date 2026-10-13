// §12 Floating navigation (`f`, page.split.js:15-16). Class names are the original CSS-module hashes.
import { useEffect, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { useReducedMotion } from '../lib/companion-motion.jsx'
import MerlinMark from './companion/MerlinMark.jsx'

const styles = {
  nav: 'floating-navigation_nav__y4vuM',
  group: 'floating-navigation_group__6DAXd',
  logo: 'floating-navigation_logo__9D2J_',
  cta: 'floating-navigation_cta__iovhA',
  link: 'floating-navigation_link__X_y7K',
}

function HoverText({ href, text, className, color = '#ddd' }) {
  return (
    <a href={href} style={{ color }} className={`hover-text_hoverText__JouUr ${className}`}>
      <span data-hover={text}>{text}</span>
    </a>
  )
}

export default function FloatingNav() {
  const [scrolledIn, setScrolledIn] = useState(false)
  const [privacyVisible, setPrivacyVisible] = useState(false)
  const reduced = useReducedMotion()

  useEffect(() => {
    const privacy = document.getElementById('privacy')
    if (!privacy) return
    const rect = privacy.getBoundingClientRect()
    setPrivacyVisible(rect.top < window.innerHeight && rect.bottom > 0)
    const observer = new IntersectionObserver(([entry]) => setPrivacyVisible(entry.isIntersecting))
    observer.observe(privacy)
    return () => observer.disconnect()
  }, [])

  useEffect(() => {
    const update = () =>
      setScrolledIn(
        window.scrollY > 100 &&
          window.innerHeight + window.scrollY < document.documentElement.scrollHeight - 100,
      )
    update()
    window.addEventListener('scroll', update, { passive: true })
    window.addEventListener('resize', update)
    return () => {
      window.removeEventListener('scroll', update)
      window.removeEventListener('resize', update)
    }
  }, [])

  const offset = reduced ? 0 : 100
  return (
    <AnimatePresence>
      {scrolledIn && !privacyVisible && (
        <motion.nav
          className={styles.nav}
          aria-label="Main navigation"
          initial={{ opacity: 0, y: offset }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: offset }}
          transition={{ duration: reduced ? 0 : 0.25 }}
        >
          <div className={styles.group}>
            <a href="/" className={styles.logo} aria-label="Merlin home">
              <span aria-hidden="true">
                <MerlinMark style={{ width: 38, height: 38 }} />
              </span>
            </a>
            <HoverText href="/pricing" text="Pricing" className={styles.link} />
            <HoverText href="/manifesto" text="Manifesto" className={styles.link} />
          </div>
          <div className={styles.group}>
            <a href="/download?start=1" className={styles.cta}>
              Download
            </a>
          </div>
        </motion.nav>
      )}
    </AnimatePresence>
  )
}
