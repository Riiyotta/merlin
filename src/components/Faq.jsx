// §10 FAQ (`sl`, page.split.js:93).
import { useState } from 'react'
import { FI } from '../lib/companion-icons.js'
import { FAQ_ITEMS } from './faq/faqData.js'
import AskMerlinForm from './faq/AskMerlinForm.jsx'

export default function Faq() {
  const [open, setOpen] = useState(null)
  return (
    <section className="merlin-faq" id="faq" aria-labelledby="faq-heading">
      <div className="merlin-faq-layout">
        <header className="merlin-faq-intro">
          <h2 id="faq-heading">
            Good questions.
            <br />
            <span>Clear answers.</span>
          </h2>
          <p>Start with the essentials. For anything else, ask Merlin below.</p>
        </header>
        <div className="merlin-faq-content">
          <div className="merlin-faq-list">
            {FAQ_ITEMS.map((item, i) => (
              <div key={item.question} className="merlin-faq-item">
                <h3>
                  <button
                    type="button"
                    id={`faq-question-${i}`}
                    aria-expanded={open === i}
                    aria-controls={`faq-answer-${i}`}
                    onClick={() => setOpen(open === i ? null : i)}
                  >
                    <span>{item.question}</span>
                    <FI.fK4 className={open === i ? 'is-open' : undefined} aria-hidden="true" />
                  </button>
                </h3>
                <div
                  id={`faq-answer-${i}`}
                  className="merlin-faq-answer"
                  aria-labelledby={`faq-question-${i}`}
                  hidden={open !== i}
                >
                  <p>{item.answer}</p>
                </div>
              </div>
            ))}
          </div>
          <AskMerlinForm />
        </div>
      </div>
    </section>
  )
}
