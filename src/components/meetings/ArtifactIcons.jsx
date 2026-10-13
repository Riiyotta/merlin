// e2.n (module 77159): with no type renders pdf + spreadsheet + deck; with a type renders that one.
import { ARTIFACT_SVGS } from './icons.jsx'

export function ArtifactIcons({ type }) {
  const types = type ? [type] : ['pdf', 'spreadsheet', 'deck']
  return (
    <span className="story-artifact-icons" aria-hidden="true">
      {types.map((t) => {
        const Svg = ARTIFACT_SVGS[t]
        return <Svg key={t} />
      })}
    </span>
  )
}
