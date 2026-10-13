// section.pricing-faq (CLONE_SPEC_PAGES_A.md §2.1/§2.5). Native <details>; the plus-icon 45deg rotation
// (transition transform .2s) is in 2abce9a6dc03269b.css. The ask form is the shared homepage component.
import AskMerlinForm from '../faq/AskMerlinForm.jsx'
import { QUESTIONS } from './pricingData.js'

function FiPlus() {
  return (
    <svg
      stroke="currentColor"
      fill="none"
      strokeWidth="2"
      viewBox="0 0 24 24"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      height="1em"
      width="1em"
      xmlns="http://www.w3.org/2000/svg"
    >
      <line x1="12" y1="5" x2="12" y2="19" />
      <line x1="5" y1="12" x2="19" y2="12" />
    </svg>
  )
}

export default function PricingFaq() {
  return (
    <section className="pricing-faq" aria-labelledby="pricing-faq-title">
      <div>
        <h2 id="pricing-faq-title">
          A few things
          <br />
          <span>you might be wondering.</span>
        </h2>
      </div>
      <div className="pricing-questions">
        {QUESTIONS.map(({ q, a }) => (
          <details key={q}>
            <summary>
              {q}
              <FiPlus />
            </summary>
            <p>{a}</p>
          </details>
        ))}
        <AskMerlinForm />
      </div>
    </section>
  )
}
