// Port of the section label (6950 chunk, module 17712: `n` icon + `a` label).
// All six section icons are included so other sections can import this unchanged.
const ICONS = {
  context: (
    <>
      <rect x="4" y="5" width="28" height="27" rx="8" fill="#32B98B" transform="rotate(-8 18 19)" />
      <path d="M10 18a7 7 0 0 1 7-7h13a7 7 0 0 1 7 7v9a7 7 0 0 1-7 7h-8l-7 4v-5a7 7 0 0 1-5-6Z" fill="#B9F3D9" />
      <path d="M17 20h13M17 26h8" stroke="#32B98B" strokeWidth="3" strokeLinecap="round" />
    </>
  ),
  routine: (
    <>
      <rect x="5" y="5" width="27" height="29" rx="8" fill="#8961F5" transform="rotate(-9 18 19)" />
      <rect x="9" y="10" width="27" height="26" rx="8" fill="#DACBFF" />
      <path d="M9 18h27v-1a7 7 0 0 0-7-7H16a7 7 0 0 0-7 7Z" fill="#B79AFB" />
      <circle cx="23" cy="26" r="7" fill="#8961F5" />
      <path d="M23 22v4l3 2" fill="none" stroke="#F4EEFF" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
    </>
  ),
  browser: (
    <>
      <rect x="4" y="6" width="29" height="26" rx="8" fill="#3E61FF" transform="rotate(-8 19 19)" />
      <rect x="7" y="12" width="30" height="23" rx="7" fill="#B7C7FF" />
      <path d="M7 21h30v-2a7 7 0 0 0-7-7H14a7 7 0 0 0-7 7Z" fill="#7795FF" />
      <circle cx="13" cy="16.5" r="1.5" fill="#E8EDFF" />
      <circle cx="18" cy="16.5" r="1.5" fill="#E8EDFF" />
      <rect x="13" y="26" width="16" height="3.5" rx="1.75" fill="#3E61FF" />
    </>
  ),
  meeting: (
    <>
      <path d="M5 12a8 8 0 0 1 8-8h12a8 8 0 0 1 8 8v9a8 8 0 0 1-8 8H13l-7 5v-9a8 8 0 0 1-1-4Z" fill="#38C9DD" transform="rotate(-8 19 19)" />
      <path d="M11 17a7 7 0 0 1 7-7h12a7 7 0 0 1 7 7v9a7 7 0 0 1-7 7h-3l-6 5v-5h-3a7 7 0 0 1-7-7Z" fill="#C7F3F8" />
      <circle cx="19" cy="22" r="2" fill="#20B6CD" />
      <circle cx="25" cy="22" r="2" fill="#20B6CD" />
      <circle cx="31" cy="22" r="2" fill="#20B6CD" />
    </>
  ),
  project: (
    <>
      <rect x="5" y="5" width="26" height="30" rx="7" fill="#FF9E53" transform="rotate(-8 18 20)" />
      <rect x="10" y="7" width="26" height="30" rx="7" fill="#FFD0A8" />
      <path d="M17 16h12M17 23h12M17 30h6" stroke="#FA8933" strokeWidth="3.5" strokeLinecap="round" />
    </>
  ),
  companion: (
    <>
      <path d="M4 13a8 8 0 0 1 8-8h13a8 8 0 0 1 8 8v11a8 8 0 0 1-8 8H14l-7 5v-8a8 8 0 0 1-3-6Z" fill="#FF48A5" transform="rotate(-7 19 20)" />
      <rect x="10" y="12" width="27" height="24" rx="8" fill="#FFB9DF" />
      <path d="m24 16 2.6 5.8L32 24l-5.4 2.2L24 32l-2.6-5.8L16 24l5.4-2.2Z" fill="#F93199" />
    </>
  ),
}

export function SectionIcon({ section }) {
  return (
    <svg viewBox="0 0 40 40" width="36" height="36" aria-hidden="true" focusable="false">
      {ICONS[section]}
    </svg>
  )
}

export default function SectionLabel({ section, label }) {
  return (
    <div className={`story-section-label story-section-label-${section}`}>
      <SectionIcon section={section} />
      <span>{label}</span>
    </div>
  )
}
