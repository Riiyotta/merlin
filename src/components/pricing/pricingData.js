// Copy for /pricing (CLONE_SPEC_PAGES_A.md §2.2). Plan copy, feature copy and FAQ questions are verbatim.
// FAQ answers are ORIGINAL placeholder text written for this clone (similar length to the live answers),
// not the live copy.

export const PLANS = [
  {
    tone: 'sage',
    name: 'Pro',
    description: 'For the replies, research, and little projects that fill your week.',
    price: '29',
    variant: 'secondary',
    credits: '25,000',
  },
  {
    tone: 'lavender',
    name: 'Ultra',
    description: 'For deeper research, bigger projects, and a fuller working day.',
    price: '99',
    variant: 'primary',
    credits: '85,000',
  },
  {
    tone: 'peach',
    name: 'Max',
    description: 'For ambitious work and an assistant you turn to throughout the day.',
    price: '299',
    variant: 'secondary',
    credits: '250,000',
  },
]

export const FEATURES = [
  {
    icon: 'context',
    title: 'A little more context.',
    body: 'Find an email, catch up on Slack, and prepare for your next calendar event.',
  },
  {
    icon: 'browser',
    title: 'A hand in your browser.',
    body: 'Book flights, order groceries, and fill out forms in your browser, with your approval.',
  },
  {
    icon: 'companion',
    title: 'Right where you are.',
    body: 'Rewrite a reply, explain selected text, or ask about what’s on your screen with Option + Space.',
  },
  {
    icon: 'meeting',
    title: 'Be there for the meeting.',
    body: 'Record meetings, get speaker-labelled transcripts, and turn the conversation into notes and next steps.',
  },
  {
    icon: 'project',
    title: 'From thought to a real thing.',
    body: 'Create slide decks, spreadsheets, PDFs, and websites you can preview, edit, and share.',
  },
  {
    icon: 'routine',
    title: 'One less thing to repeat.',
    body: 'Get a morning briefing, prepare for upcoming meetings, and receive a weekly summary on a schedule.',
  },
]

export const QUESTIONS = [
  {
    q: 'Which plan should I choose?',
    a: 'Placeholder answer. Think about a typical week: a handful of quick questions sits comfortably in the smallest tier, while long research sessions and larger builds suit the middle or top tier. Every tier unlocks the same tools; only the headroom differs.',
  },
  {
    q: 'What are credits?',
    a: 'Placeholder answer. Credits are a single unit that measures the work Merlin does for you. Quick questions draw a little, while tasks that browse several pages, call outside services or write long documents draw more. A running tally is always in the app.',
  },
  {
    q: 'Do unused credits roll over?',
    a: 'Placeholder answer. Each billing period starts with a full allowance, and leftover balance resets at that point, as shown in the app.',
  },
  {
    q: 'What happens if I run out?',
    a: 'Placeholder answer. Once the allowance is used up, Merlin pauses anything that would draw further credits until the next period begins. You can see when that happens and adjust your plan in the app.',
  },
  {
    q: 'Is there an annual option?',
    a: 'Placeholder answer. A yearly subscription is offered at a reduced overall cost compared with paying month by month. The credit allowance still arrives in monthly instalments, so the day-to-day experience stays the same. Full terms appear in the app.',
  },
  {
    q: 'How do I get started?',
    a: 'Placeholder answer. Install the Mac app, sign in, and a short welcome flow walks you through the basics. A starter balance lets you try things before picking a tier.',
  },
]
