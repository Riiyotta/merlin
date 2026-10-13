// Inline mention (module 10256, `l`): section icon for browser/meeting, artifact icon otherwise
// (`document` maps to the `pdf` artifact type).
import { SectionIcon } from '../routines/SectionLabel.jsx'
import { ArtifactIcons } from '../meetings/ArtifactIcons.jsx'

export default function Mention({ kind, children }) {
  return (
    <span className="manifesto-mention">
      {kind === 'browser' || kind === 'meeting' ? (
        <SectionIcon section={kind} />
      ) : (
        <ArtifactIcons type={kind === 'document' ? 'pdf' : kind} />
      )}
      {children}
    </span>
  )
}
