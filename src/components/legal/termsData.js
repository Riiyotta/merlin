// /terms section outline (CLONE_SPEC_PAGES_B.md §5). h2/h3 text and ids are verbatim from the spec;
// every paragraph and list item is original placeholder text at the recorded word count
// (list-item counts measured from reference/pages/terms.html).
import { placeholder, PLACEHOLDER_NOTE, LONG_POOL, POOL } from './placeholder.js'

// Each paragraph's wording variant ('L<n>' = LONG_POOL from sentence n, 'S<n>' = POOL from sentence n,
// '+k' = skip k words) was picked by measuring candidate filler in the real layout so the paragraph wraps
// to the same number of lines as the live one at 720px (1440/1280) and 350px (390).
const v = (variant) => {
  const [, pool, seed, skip] = variant.match(/^([LS])(\d+)(?:\+(\d+))?$/)
  return [Number(seed), pool === 'L' ? LONG_POOL : POOL, Number(skip || 0)]
}
const text = (words, variant, prefix = '') => {
  const [seed, pool, skip] = v(variant)
  return placeholder(words, seed, prefix, pool, skip)
}
const p = (words, variant) => ({ type: 'p', text: text(words, variant) })
const h3 = (text) => ({ type: 'h3', text })
// items: [words, variant] pairs
const ul = (...items) => ({ type: 'ul', items: items.map(([n, variant]) => text(n, variant)) })

export const termsPage = {
  skipLabel: 'Read terms of service',
  title: 'Terms of Service',
  intro: null,
  date: 'April 30, 2025',
  sections: [
    {
      id: 'introduction',
      title: 'Introduction',
      // First paragraph on the page carries the placeholder note.
      blocks: [{ type: 'p', text: text(30, 'S2', PLACEHOLDER_NOTE) }, p(29, 'S1')],
    },
    { id: 'service-description', title: 'Service Description', blocks: [p(31, 'S2')] },
    {
      id: 'user-accounts',
      title: 'User Accounts',
      blocks: [h3('Account Creation'), p(37, 'S3'), h3('Account Eligibility'), p(26, 'S4'), h3('Account Termination'), p(39, 'S9')],
    },
    {
      id: 'user-responsibilities',
      title: 'User Responsibilities',
      blocks: [
        h3('Accurate Information'), p(23, 'S6'),
        h3('Authorized Access'), p(40, 'S9'),
        h3('Prohibited Uses'), p(7, 'S8'),
        ul([10, 'S9'], [11, 'L4'], [16, 'S2'], [16, 'S8'], [17, 'S3'], [9, 'S4']),
      ],
    },
    {
      id: 'connected-services',
      title: 'Connected Services',
      blocks: [h3('Third-Party Accounts'), p(44, 'S5'), h3('Authorization'), p(28, 'S7'), h3('Revocation'), p(38, 'S1')],
    },
    {
      id: 'intellectual-property',
      title: 'Intellectual Property',
      blocks: [h3('Merlin Content'), p(26, 'S2'), h3('User Content'), p(51, 'S1'), h3('Feedback'), p(31, 'S2')],
    },
    {
      id: 'subscription-and-billing',
      title: 'Subscription and Billing',
      blocks: [h3('Pricing'), p(31, 'S5'), h3('Free Trial'), p(32, 'S8'), h3('Payment'), p(28, 'S3'), h3('Cancellation'), p(35, 'S4')],
    },
    {
      id: 'limitation-of-liability',
      title: 'Limitation of Liability',
      blocks: [
        h3('Disclaimer of Warranties'), p(37, 'S5'),
        h3('Limitation of Liability'), p(48, 'S5'),
        ul([14, 'S8'], [11, 'S9'], [6, 'S1'], [10, 'S0']),
        h3('Service Interruptions'), p(29, 'S2'),
      ],
    },
    { id: 'indemnification', title: 'Indemnification', blocks: [p(52, 'S3')] },
    { id: 'modifications-to-terms', title: 'Modifications to Terms', blocks: [p(45, 'S7'), p(40, 'S9')] },
    { id: 'governing-law', title: 'Governing Law', blocks: [p(38, 'S8')] },
    { id: 'severability', title: 'Severability', blocks: [p(25, 'S6')] },
    { id: 'entire-agreement', title: 'Entire Agreement', blocks: [p(31, 'S2')] },
    {
      id: 'contact-us',
      title: 'Contact Us',
      // Second paragraph is the live "Email: <mailto link>" line (2 words, contact detail only).
      blocks: [p(11, 'S8'), { type: 'email', label: 'Email:', email: 'team@merlin.computer' }],
    },
  ],
}
