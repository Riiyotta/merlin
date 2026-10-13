// /privacy section outline (CLONE_SPEC_PAGES_B.md §4.1–4.2). Headings and ids are verbatim from the spec;
// every paragraph is original placeholder text at the recorded word count.
import { placeholder, PLACEHOLDER_NOTE, LONG_POOL, POOL } from './placeholder.js'

// Each paragraph's wording variant ('L<n>' = LONG_POOL from sentence n, 'S<n>' = POOL from sentence n,
// '+k' = skip k words) was picked by measuring candidate filler in the real layout so the paragraph wraps
// to the same number of lines as the live one at 720px (1440/1280) and 350px (390).
const v = (variant) => {
  const [, pool, seed, skip] = variant.match(/^([LS])(\d+)(?:\+(\d+))?$/)
  return [Number(seed), pool === 'L' ? LONG_POOL : POOL, Number(skip || 0)]
}
const p = (words, variant) => {
  const [seed, pool, skip] = v(variant)
  return { type: 'p', text: placeholder(words, seed, '', pool, skip) }
}

export const privacyPage = {
  skipLabel: 'Read privacy and control',
  title: 'Privacy and control',
  // Live intro is 19 words; it is the first paragraph on the page, so it carries the placeholder note.
  intro: placeholder(19, 0, PLACEHOLDER_NOTE, LONG_POOL),
  date: 'September 28, 2026',
  sections: [
    { id: 'local-and-cloud', title: 'On your Mac. Connected when needed.', blocks: [p(48, 'S1'), p(42, 'L8')] },
    { id: 'information', title: 'The information Merlin works with.', blocks: [p(35, 'L5'), p(37, 'L6')] },
    { id: 'permissions', title: 'You choose the access.', blocks: [p(41, 'L7'), p(46, 'L9'), p(31, 'L7')] },
    { id: 'providers', title: 'AI and service providers.', blocks: [p(41, 'L0'), p(30, 'L1')] },
    { id: 'security', title: 'Security, with care.', blocks: [p(15, 'L2'), p(39, 'L6')] },
    { id: 'retention', title: 'Managing and deleting your data.', blocks: [p(30, 'L5'), p(35, 'L3')] },
    { id: 'website', title: 'When you use this website.', blocks: [p(82, 'L4'), p(63, 'S7')] },
    { id: 'contact', title: 'Questions about your privacy?', blocks: [p(16, 'L6+10'), p(18, 'L8')] },
  ],
}
