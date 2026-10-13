// PLACEHOLDER COPY. Merlin's article bodies are copyrighted and are intentionally NOT reproduced.
// Each prose block is filled with neutral filler text from the generic sentence bank below, cut to
// the block's recorded word count (src/data/blog-posts.json structure[].words) so line counts and
// heights roughly match the live site. Output is deterministic per (slug, block index).

const SENTENCES = [
  'A steady routine makes the rest of the week feel lighter and easier to organise.',
  'Small habits tend to add up when they are repeated with some care.',
  'Most people discover that clear notes save effort when they return to a project later.',
  'It helps to decide what matters first and leave the smaller details for afterwards.',
  'A short pause before replying often leads to a calmer and more useful answer.',
  'Simple tools work best when they stay out of the way until they are needed.',
  'Thoughtful planning leaves a little breathing space for the things nobody expected.',
  'Writing down the next step turns a vague idea into something you can finish.',
  'Shared calendars and tidy folders keep everyone pointed in the same general direction.',
  'The goal is not to do more, but to spend attention where it counts.',
  'When the basics are handled reliably, there is more room for meaningful, focused work.',
  'Every team settles on its own rhythm, and that rhythm can change over time.',
  'A friendly tone and a specific request usually travel further than a lengthy message.',
  'Checking the details once more can prevent a surprising number of small problems.',
  'Reviewing the week on Friday afternoon makes Monday morning feel considerably less crowded.',
  'Keeping related items together means less searching and fewer missed updates.',
  'Colleagues appreciate messages that respect their schedules and get directly to the point.',
  'It is worth trying a few approaches before settling on the one that fits.',
  'Clear labels, brief summaries and sensible defaults make most systems easier to navigate.',
  'Over time, these practices become second nature and free up the afternoon.',
]

// mulberry32 seeded by a string hash, so the same slug always yields the same filler.
function hash(str) {
  let h = 2166136261
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i)
    h = Math.imul(h, 16777619)
  }
  return h >>> 0
}

function rng(seed) {
  let a = seed
  return () => {
    a = (a + 0x6d2b79f5) | 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

const BANK = SENTENCES.map((s) => {
  const words = s.split(' ')
  return { words, cpw: words.join('').length / words.length }
})

// Returns an array of exactly `count` words of placeholder text, ending with a period.
// `targetCpw` (optional, characters per word excluding spaces) steers sentence choice so the filler's
// average word length tracks the live post's (a per-post statistic in bodyStats.fillerCharsPerWord),
// which keeps line counts, and therefore section heights, close to the original.
export function placeholderWords(seedKey, count, targetCpw) {
  if (!count) return []
  const rand = rng(hash(seedKey))
  const words = []
  let chars = 0
  while (words.length < count) {
    let pool = BANK
    if (targetCpw) {
      const avg = words.length ? chars / words.length : targetCpw
      const want = avg <= targetCpw ? (x) => x.cpw >= targetCpw : (x) => x.cpw < targetCpw
      const filtered = BANK.filter(want)
      if (filtered.length) pool = filtered
    }
    const sentence = pool[Math.floor(rand() * pool.length)]
    const take = sentence.words.slice(0, count - words.length)
    words.push(...take)
    chars += take.join('').length
  }
  words.length = count
  const last = words[count - 1].replace(/[.,]$/, '')
  words[count - 1] = `${last}.`
  words[0] = words[0][0].toUpperCase() + words[0].slice(1)
  return words
}
