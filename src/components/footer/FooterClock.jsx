// Closing invitation with live clock (6950 chunk, module 42077 `o`): now + 3 minutes, HH:MM 24h.
import { useEffect, useState } from 'react'
import { FI } from '../../lib/companion-icons.js'
import DownloadButton from '../shared/DownloadButton.jsx'

function inThreeMinutes() {
  const d = new Date(Date.now() + 180000)
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

export default function FooterClock() {
  const [time, setTime] = useState(null)

  useEffect(() => {
    const update = () => setTime(inThreeMinutes())
    update()
    const id = window.setInterval(update, 1000)
    document.addEventListener('visibilitychange', update)
    return () => {
      window.clearInterval(id)
      document.removeEventListener('visibilitychange', update)
    }
  }, [])

  return (
    <div className="closing-invitation">
      <h2>
        Your next free moment
        <br />
        <span className="closing-start-time">
          {time ? (
            <>
              starts at{' '}
              <span className="closing-clock-time">
                <FI.Ohp aria-hidden="true" />
                <time dateTime={time}>{time}</time>
              </span>
            </>
          ) : (
            'starts in three minutes'
          )}
        </span>
      </h2>
      <p>In just three minutes, Merlin starts handling your to-dos. You decide what comes after.</p>
      <DownloadButton />
    </div>
  )
}
