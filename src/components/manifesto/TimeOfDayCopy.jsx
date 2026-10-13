// Port of module 10256 (`s({part})`). Renders time-neutral fallback copy until mounted, then picks the
// variant set for the current hour, re-checking every 60 000 ms and on visibilitychange.
// All prose is placeholder (see ./copy.js).
import { useEffect, useState } from 'react'
import Mention from './Mention.jsx'
import { FALLBACK, P2_LEAD, P7, copyForHour } from './copy.js'

function useTimeOfDayCopy() {
  const [copy, setCopy] = useState(null)
  useEffect(() => {
    const update = () => setCopy(copyForHour(new Date().getHours()))
    update()
    const id = window.setInterval(update, 60000)
    document.addEventListener('visibilitychange', update)
    return () => {
      window.clearInterval(id)
      document.removeEventListener('visibilitychange', update)
    }
  }, [])
  return copy
}

export default function TimeOfDayCopy({ part }) {
  const copy = useTimeOfDayCopy()

  if (part === 'opening') {
    return (
      <>
        <p>{copy?.opening ?? FALLBACK.opening}</p>
        <p>
          {P2_LEAD[0]}
          <Mention kind="meeting">meeting</Mention>
          {P2_LEAD[1]}
          <Mention kind="document">document</Mention>
          {P2_LEAD[2]}
          {copy?.interruption ?? FALLBACK.interruption}
        </p>
      </>
    )
  }

  if (part === 'return') {
    return (
      <p>
        {copy?.returnToIdea ?? FALLBACK.returnToIdea}
        {P7[0]}
        <Mention kind="deck">deck</Mention>
        {P7[1]}
        <Mention kind="spreadsheet">spreadsheet</Mention>
        {P7[2]}
        <Mention kind="website">website</Mention>
        {P7[3]}
      </p>
    )
  }

  return <p>{copy?.finish ?? FALLBACK.finish}</p>
}
