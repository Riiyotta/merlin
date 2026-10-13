import { useEffect, useRef, useState } from 'react'
import { motion, useScroll, useTransform } from 'framer-motion'
import { useReducedMotion } from '../lib/hero-reduced-motion.js'
import HeroNav from './hero/HeroNav.jsx'
import HeroNotifications from './hero/HeroNotifications.jsx'
import DownloadButton from './shared/DownloadButton.jsx'

// Port of `er` + `b` (page.split.js:18, 45-46): section.story-hero and section.hero-life landscape.
export default function Hero() {
  const landscapeRef = useRef(null)
  const [chroma, setChroma] = useState(true)
  useEffect(() => {
    const timer = window.setTimeout(() => setChroma(false), 1500)
    return () => window.clearTimeout(timer)
  }, [])
  const reduced = useReducedMotion()
  const { scrollYProgress } = useScroll({ target: landscapeRef, offset: ['start end', 'end start'] })
  const y = useTransform(scrollYProgress, [0, 1], ['-3%', '3%'])

  return (
    <>
      <section className="story-hero">
        <HeroNav />
        <h1 aria-label="Your time. Yours again.">
          <span className={`hero-title-line${chroma ? ' hero-title-chroma' : ''}`}>Your time.</span>
          <span className={`hero-title-line hero-title-muted${chroma ? ' hero-title-chroma' : ''}`}>Yours again.</span>
        </h1>
        <div className="hero-bottom">
          <p>
            Meet Merlin. Your AI assistant for the things you need to do, giving you time back for the things you’d love
            to.
          </p>
          <DownloadButton />
        </div>
      </section>
      <section ref={landscapeRef} className="hero-life hero-landscape" style={{ position: 'relative' }} aria-label="Merlin, in your everyday">
        <motion.img
          className="hero-photo"
          style={reduced ? undefined : { y, scale: 1.07 }}
          src="/assets/quiet-lakeside.webp"
          alt="A woven pastel lakeside landscape with a small sailboat, willow trees, and lavender hills at sunset"
          loading="eager"
        />
        <HeroNotifications />
      </section>
    </>
  )
}
