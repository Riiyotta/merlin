// PLACEHOLDER COPY. The original manifesto essay is Merlin's copyrighted writing and is intentionally
// not reproduced. Every paragraph, time-of-day variant and handwriting overlay below is original
// placeholder prose written to the same paragraph structure and per-paragraph word counts
// (CLONE_SPEC_PAGES_A.md §4) so the layout matches. Headings and the signature are from the spec.

export const HANDWRITING = {
  time: 'First tea',
  back: 'Breathe out',
  noteUnderstanding: 'an hour all yours',
  noteAction: 'let the day run on',
}

// Time-of-day sets (module 10256). `returnToIdea` is the same sentence in every set.
const RETURN = 'Your own plan gets a turn.'

export const FALLBACK = {
  opening: 'Every day begins with a short list you care about and a longer one that keeps asking for you.',
  interruption: 'Each one is small alone. Together they quietly push your own plans to the bottom of the pile.',
  returnToIdea: RETURN,
  finish:
    'Then the screen goes dark and the rest of the day is yours. Cook something slow, write a letter, wander without any destination. That is the time Merlin is here to give back.',
}

export const VARIANTS = {
  morning: {
    opening: 'The kettle is on, the light is soft, and today’s whole plan still looks small enough to fit inside one cup.',
    interruption: 'By the time you look up, the coffee is cold and the morning has filled itself in already.',
    returnToIdea: RETURN,
    finish:
      'Then the screen goes dark before noon and the morning is yours. Visit the farmers’ market, linger over a second breakfast, open the novel beside your bed. That is what Merlin is for.',
  },
  afternoon: {
    opening: 'Lunch is done and sunlight has crept across your desk. Half the list still waits, and so does the work you love.',
    interruption: 'By the time you look up, it is nearly four and the afternoon has gone to someone else’s list.',
    returnToIdea: RETURN,
    finish:
      'Then the screen goes dark while it is still bright out. Sit in the garden, write a letter, wander somewhere without any destination, or let your thoughts drift. Merlin is here to give you that afternoon.',
  },
  evening: {
    opening: 'The sky turns pink over the roofs. You promised yourself one calm hour tonight, the kind that is just for you alone.',
    interruption: 'By the time you look up, dinner is waiting and the evening has been handed to somebody else’s list.',
    returnToIdea: RETURN,
    finish:
      'Then the screen goes dark and the evening opens up. Cook something unhurried, sit with people you love, watch the last light fade over the rooftops. Merlin is here to give you that.',
  },
  night: {
    openingLate: 'The house is quiet now and the lamps are low. One stubborn thought keeps circling, asking when there will finally be room for it.',
    openingEarly:
      'It is very late, or very early, and every room is quiet. You are awake anyway, turning one thought over, wondering when there will be room for it.',
    interruption: 'By the time you look up, the monitor is the only light left and your hour has vanished.',
    returnToIdea: RETURN,
    finish:
      'Then the screen goes dark and the night is yours. Make a warm drink, read one more chapter, listen to the rain, or simply get some sleep. Tomorrow will be lighter. Merlin is for that.',
  },
}

// Hour ranges from the original: 5–11 morning, 12–16 afternoon, 17–21 evening, otherwise night
// (separate opening before 5am).
export function copyForHour(h) {
  if (h >= 5 && h < 12) return VARIANTS.morning
  if (h >= 12 && h < 17) return VARIANTS.afternoon
  if (h >= 17 && h < 22) return VARIANTS.evening
  const { openingLate, openingEarly, ...rest } = VARIANTS.night
  return { ...rest, opening: h < 5 ? openingEarly : openingLate }
}

export const P2_LEAD = ['Then the day shifts and a sudden ', ' appears. Then a ', ' wants your eyes today. ']

export const P3 =
  'Most of us know this feeling. The work we choose gets pushed aside by the work that chooses us, one small request at a time, until the week is over.'
export const P4 =
  'Nobody plans to spend an afternoon copying figures between two tabs, chasing replies, or looking for that one lost file. It just happens, quietly, one tab and then the next.'
export const P5 = [
  'Even after every ',
  ', someone still has to write up the minutes, send the follow-ups, update the tracker and remind everybody what was agreed. Most of the time that someone is you, late in the evening.',
]
export const P6 = [
  'We built a helper that sits beside you on your Mac and works in your ',
  ', your calendar and your favourite apps, taking on the busywork so you can keep the parts that matter.',
]
export const P7 = [
  ' Ask in everyday language and all the tedious steps get done, whether that means a beautiful ',
  ', a ',
  ', or a simple ',
  '. Merlin handles the small chores you always postponed.',
]
export const P8 =
  'What is left is the part only you can do. The thinking, the choosing, the small kind gestures, and the ideas that need a clear head and a little bit of quiet to grow.'
