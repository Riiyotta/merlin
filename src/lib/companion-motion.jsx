// Shared motion helpers ported from the original bundle.
// useReducedMotion = module 82830 (`u.I`), Reveal = `eL` (page.split.js:65-66).
import { useSyncExternalStore } from 'react'
import { motion } from 'framer-motion'

const QUERY = '(prefers-reduced-motion: reduce)'

function subscribe(callback) {
  const mql = window.matchMedia(QUERY)
  mql.addEventListener('change', callback)
  return () => mql.removeEventListener('change', callback)
}
const getSnapshot = () => window.matchMedia(QUERY).matches
const getServerSnapshot = () => false

export function useReducedMotion() {
  return useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot)
}

export const EASE_OUT_EXPO = [0.22, 1, 0.36, 1]

// Slide-up entrance: y 20 -> 0 when 15% in view, 0.75s, once.
export function Reveal({ children, className = '' }) {
  const reduced = useReducedMotion()
  return (
    <motion.div
      className={className}
      initial={{ opacity: 1, y: reduced ? 0 : 20 }}
      whileInView={{ y: 0 }}
      viewport={{ once: true, amount: 0.15 }}
      transition={{ duration: 0.75, ease: EASE_OUT_EXPO }}
    >
      {children}
    </motion.div>
  )
}
