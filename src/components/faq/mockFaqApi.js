// Local stand-in for the live site's POST /api/faq (server-side LLM, not reachable from a static clone).
// Resolves to `{ answer }` after a short delay, picking the closest FAQ answer by keyword overlap.
import { FAQ_ITEMS } from './faqData.js'

const FALLBACK =
  'This is a local preview, so I can’t look that up right now. The essentials above cover getting started, Companion, the browser, and meeting notes. For anything else, write to team@merlin.computer.'
const STOP = new Set(['what', 'how', 'can', 'does', 'the', 'and', 'with', 'for', 'you', 'your', 'merlin', 'about', 'use', 'help', 'need', 'work', 'is', 'do', 'my', 'me', 'i', 'a', 'to', 'in', 'of', 'it'])
const words = (s) => s.toLowerCase().match(/[a-z]+/g)?.filter((w) => w.length > 2 && !STOP.has(w)) ?? []

export function askFaq(question, signal) {
  return new Promise((resolve, reject) => {
    const q = new Set(words(question))
    let best = null
    let bestScore = 0
    for (const item of FAQ_ITEMS) {
      const score = words(`${item.question} ${item.answer}`).filter((w) => q.has(w)).length
      if (score > bestScore) {
        best = item
        bestScore = score
      }
    }
    const id = window.setTimeout(() => resolve({ answer: best ? best.answer : FALLBACK }), 1400)
    signal.addEventListener('abort', () => {
      window.clearTimeout(id)
      reject(new DOMException('Aborted', 'AbortError'))
    })
  })
}
