import { FiArrowRight } from '../hero/icons.jsx'

// Port of the shared download CTA (6950 chunk, module 13669). Styling lives in the original CSS
// (`.download-button`, `::before` cyan wipe, hover/focus-visible states).
export default function DownloadButton({ light = false, variant = 'primary', className = '', ariaLabel }) {
  return (
    <a
      className={`download-button ${light ? 'light' : ''} download-button-${variant} ${className}`}
      href="/download?start=1"
      aria-label={ariaLabel}
    >
      <span>Get Merlin for Mac</span>
      <span className="download-arrow" aria-hidden="true">
        <FiArrowRight />
      </span>
    </a>
  )
}
