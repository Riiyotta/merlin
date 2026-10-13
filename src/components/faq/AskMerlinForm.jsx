// Ask-Merlin form (module 2292 `o`, page.split.js:2-4). The fetch to /api/faq is replaced by askFaq().
import { useEffect, useId, useRef, useState } from 'react'
import { FI, IO } from '../../lib/companion-icons.js'
import { askFaq } from './mockFaqApi.js'

export default function AskMerlinForm() {
  const id = useId()
  const [question, setQuestion] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const controllerRef = useRef(null)

  async function onSubmit(e) {
    e.preventDefault()
    const q = question.trim()
    if (!q || controllerRef.current) return
    const controller = new AbortController()
    controllerRef.current = controller
    setResult(null)
    setError('')
    setLoading(true)
    try {
      const data = await askFaq(q, controller.signal)
      if (typeof data.answer !== 'string') throw Error('The answer couldn’t be read. Please try again.')
      if (!controller.signal.aborted) setResult({ answer: data.answer })
    } catch (err) {
      if (!controller.signal.aborted) {
        setError(err instanceof Error ? err.message : 'Couldn’t connect. Please try again.')
      }
    } finally {
      if (controllerRef.current === controller) {
        controllerRef.current = null
        setLoading(false)
      }
    }
  }

  function onStop() {
    controllerRef.current?.abort()
    controllerRef.current = null
    setLoading(false)
    setError('Stopped. You can edit your question and ask again.')
  }

  useEffect(() => () => controllerRef.current?.abort(), [])

  return (
    <>
      <form className="merlin-faq-form ph-no-capture" onSubmit={onSubmit}>
        <div className="merlin-faq-input-row">
          <input
            id={id}
            aria-label="Your question about Merlin"
            placeholder="What else would you like to know?"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            maxLength={500}
            required
            disabled={loading}
            autoComplete="off"
          />
          {loading ? (
            <button type="button" onClick={onStop} aria-label="Stop answering">
              <IO.jpF aria-hidden="true" />
            </button>
          ) : (
            <button type="submit" disabled={!question.trim()} aria-label="Ask Merlin">
              <FI.dyV aria-hidden="true" />
            </button>
          )}
        </div>
      </form>
      <div className="merlin-faq-response ph-no-capture" aria-busy={loading}>
        {loading && (
          <p className="merlin-faq-loading" role="status">
            <span className="merlin-faq-shimmer">Reading the docs…</span>
          </p>
        )}
        {error && (
          <p className="merlin-faq-error" role="alert">
            {error}
          </p>
        )}
        {result && (
          <div aria-live="polite" aria-atomic="true">
            <p className="merlin-faq-generated">{result.answer}</p>
          </div>
        )}
      </div>
    </>
  )
}
