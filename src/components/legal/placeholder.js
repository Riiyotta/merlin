// Original neutral filler used in place of Merlin's legal text (CLONE_SPEC_PAGES_B.md §7: body text was
// deliberately not transcribed). Each paragraph is cut to the word count recorded in the spec so section
// heights stay close to the live page.
export const POOL = [
  'This paragraph is placeholder copy written for a local clone of the website, so the layout can be tested.',
  'It fills roughly the same space as the original section on the live page and says nothing of substance.',
  'None of these words describe how any product handles personal data, files, or connected accounts.',
  'Replace this block with approved wording before publishing a page that resembles a legal document.',
  'Sentences are kept fairly plain so each line wraps much as the original text does at every width.',
  'Anyone looking for the actual terms should read the version published on the official website.',
  'Designers can use this filler to check rhythm, spacing, contrast, and column width at each breakpoint.',
  'The headings and links are reproduced, while the underlying statements are intentionally left out.',
  'Every word in this region is neutral sample text and carries no legal or factual meaning at all.',
  'More filler continues here so the height of the section stays close to what was measured.',
]

// Slightly longer vocabulary for /privacy, whose original text averages longer words than /terms
// (about 6.6 vs 6.2 characters per word including the space), so its section heights stay comparable.
export const LONG_POOL = [
  'This paragraph is placeholder material written for a local development clone of the website.',
  'It occupies roughly the same space as the original section and communicates nothing of substance.',
  'Nothing written here describes how any application collects, stores, or processes information.',
  'Replace this block with approved wording before publishing a page resembling a genuine document.',
  'Sentence length was chosen to approximate typical paragraph measurements and line wrapping.',
  'Readers looking for real commitments should consult the official published version instead.',
  'Designers can use this filler to check spacing, contrast, and column width across breakpoints.',
  'Headings and navigation are reproduced, while the underlying statements are deliberately omitted.',
  'Every word in this region is neutral sample text with no legal or descriptive meaning at all.',
  'Additional filler continues here so the height of the section stays close to what was measured.',
]

export const PLACEHOLDER_NOTE = 'Placeholder text in a local clone, not a real legal document.'

// Returns exactly `words` words, ending with a period. `seed` rotates the starting sentence so
// neighbouring paragraphs do not read identically. `prefix` (optional) counts toward the total.
// `pool` selects the sentence set; `skip` drops that many words from the start of the stream. The
// (seed, pool, skip) per paragraph is chosen so each paragraph wraps to the same number of lines as
// the live paragraph at both the 720px desktop and 350px mobile column widths.
export function placeholder(words, seed = 0, prefix = '', pool = POOL, skip = 0) {
  const out = prefix ? prefix.split(' ') : []
  const stream = []
  let i = seed
  while (stream.length < words + skip) {
    stream.push(...pool[i % pool.length].split(' '))
    i += 1
  }
  out.push(...stream.slice(skip))
  let text = out.slice(0, words).join(' ').replace(/[.,]$/, '')
  text = text[0].toUpperCase() + text.slice(1)
  return `${text}.`
}
