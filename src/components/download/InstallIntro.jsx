// Port of download-page module 3991 (CLONE_SPEC_PAGES_A.md §3.4).
// Clone deviation (by design): every installer URL points at the local stub /download-stub.txt instead of
// https://download.merlin.computer/mac/latest, so nothing real is downloaded. The arch is kept as a query
// param so the arm64/x64 branches stay observable. Analytics (website_download_requested) is not ported.
import { useEffect, useRef, useState } from 'react'

function isMac(nav) {
  return (
    !/iPhone|iPad|iPod|Android/i.test(nav.userAgent) &&
    !((nav.maxTouchPoints ?? 0) > 1) &&
    (nav.userAgentData?.platform === 'macOS' || /Macintosh|Mac OS X/i.test(nav.userAgent))
  )
}

async function detectArch(nav, timeout = 600) {
  const fallback = { arch: 'arm64', detected: false }
  if (!isMac(nav) || !nav.userAgentData?.getHighEntropyValues) return fallback
  let timer
  try {
    const values = await Promise.race([
      nav.userAgentData.getHighEntropyValues(['architecture']),
      new Promise((resolve) => {
        timer = setTimeout(() => resolve(undefined), timeout)
      }),
    ])
    if (values?.architecture === 'arm') return { arch: 'arm64', detected: true }
    if (values?.architecture === 'x86') return { arch: 'x64', detected: true }
    return fallback
  } catch {
    return fallback
  } finally {
    clearTimeout(timer)
  }
}

const installerUrl = (arch) => `/download-stub.txt?arch=${arch}`

export default function InstallIntro() {
  const [arch, setArch] = useState('arm64')
  const [status, setStatus] = useState('ready')
  const iframeRef = useRef(null)
  const started = useRef(false)

  useEffect(() => {
    let cancelled = false
    const url = new URL(window.location.href)
    const start = url.searchParams.get('start') === '1'
    if (!isMac(navigator)) {
      setStatus('other-device')
      return
    }
    detectArch(navigator).then((result) => {
      if (cancelled) return
      setArch(result.arch)
      if (start && !started.current && iframeRef.current) {
        started.current = true
        url.searchParams.delete('start')
        window.history.replaceState(window.history.state, '', url.pathname + url.search + url.hash)
        iframeRef.current.src = installerUrl(result.arch)
        setStatus('requested')
      }
    })
    return () => {
      cancelled = true
    }
  }, [])

  const requestManual = (nextArch) => {
    started.current = true
    setArch(nextArch)
    setStatus('requested')
  }

  const other = arch === 'arm64' ? 'x64' : 'arm64'

  return (
    <>
      <h1 id="install-title">
        Thanks for choosing Merlin.
        <br />
        <span>Here’s how to get started.</span>
      </h1>
      <p className="install-description">
        {status === 'other-device'
          ? 'Merlin is made for Mac. Open this page on your Mac to get started.'
          : 'Your download will start automatically. Follow these steps to finish installing Merlin.'}
      </p>
      <p className="install-retry">
        Download not starting?{' '}
        <a href={installerUrl(arch)} target="merlin-installer" onClick={() => requestManual(arch)}>
          Download Merlin again
        </a>
      </p>
      <p className="install-alternative">
        <a href={installerUrl(other)} target="merlin-installer" onClick={() => requestManual(other)}>
          {other === 'x64' ? 'Download for Intel Macs' : 'Download for Apple Silicon'}
        </a>
      </p>
      <iframe ref={iframeRef} name="merlin-installer" title="Merlin installer download" className="install-download-frame" />
      <noscript>
        <p>
          Choose <a href={installerUrl('arm64')}>Apple Silicon</a> or <a href={installerUrl('x64')}>Intel</a> to
          download Merlin.
        </p>
      </noscript>
    </>
  )
}
