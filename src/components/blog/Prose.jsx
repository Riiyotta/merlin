// Renders a post body from its structure outline (src/data/blog-posts.json structure[]).
// BODY TEXT IS PLACEHOLDER: headings use the recorded heading text, but every p/li/blockquote is
// neutral filler from src/lib/blog-placeholder.js with the recorded word count. Merlin's article
// copy is intentionally not reproduced. Inline strong/em/br/a placement is approximated from the
// block's `inline` tag list (the live positions were not recorded).
import { placeholderWords } from '../../lib/blog-placeholder.js'

function Inline({ words, inline = [], link = false }) {
  if (!words.length) return inline.includes('br') ? <br /> : null
  const n = words.length
  const strongN = inline.includes('strong') ? Math.min(3, n) : 0
  const rest = words.slice(strongN)
  const emN = inline.includes('em') && rest.length > 4 ? Math.min(4, rest.length - 1) : 0
  const plain = rest.slice(0, rest.length - emN)
  const em = rest.slice(rest.length - emN)
  const brAfterStrong = inline.includes('br') && strongN > 0 && plain.length > 0
  let plainNode = plain.join(' ')
  if (link && plain.length > 3) {
    const mid = Math.floor(plain.length / 2)
    plainNode = (
      <>
        {plain.slice(0, mid).join(' ')} <a>{plain.slice(mid, mid + 2).join(' ')}</a> {plain.slice(mid + 2).join(' ')}
      </>
    )
  }
  return (
    <>
      {strongN > 0 && <strong>{words.slice(0, strongN).join(' ')}</strong>}
      {strongN > 0 && (brAfterStrong ? <br /> : plain.length || em.length ? ' ' : null)}
      {plainNode}
      {em.length > 0 && (
        <>
          {plain.length ? ' ' : null}
          <em>{em.join(' ')}</em>
        </>
      )}
    </>
  )
}

function List({ block, seed, cpw }) {
  const Tag = block.type
  const top = block.items || 0
  const nested = block.nested || 0
  const total = top + nested
  const base = total ? Math.floor(block.words / total) : 0
  let extra = total ? block.words - base * total : 0
  let k = 0
  const next = () => {
    const count = base + (extra > 0 ? 1 : 0)
    if (extra > 0) extra--
    const w = placeholderWords(`${seed}:${k}`, count, cpw)
    k++
    return w
  }
  const childInline = (block.inline || []).filter((t) => t !== 'li' && t !== 'ul' && t !== 'ol')
  const items = Array.from({ length: top }, (_, i) => ({
    words: next(),
    subs: [],
    link: i === 0 && block.links > 0,
  }))
  for (let j = 0; j < nested; j++) items[j % Math.max(top, 1)]?.subs.push(next())
  return (
    <Tag>
      {items.map((item, i) => (
        <li key={i}>
          <Inline words={item.words} inline={childInline} link={item.link} />
          {item.subs.length > 0 && (
            <ul>
              {item.subs.map((w, j) => (
                <li key={j}>
                  <Inline words={w} inline={childInline.filter((t) => t !== 'br')} />
                </li>
              ))}
            </ul>
          )}
        </li>
      ))}
    </Tag>
  )
}

export default function Prose({ slug, structure, cpw }) {
  return (
    <div className="blog_prose__r_2py">
      {structure.map((block, i) => {
        const seed = `${slug}:${i}`
        const inline = block.inline || []
        switch (block.type) {
          case 'h2':
          case 'h3':
          case 'h4': {
            const H = block.type
            return <H key={i}>{inline.includes('strong') ? <strong>{block.text}</strong> : block.text}</H>
          }
          case 'ul':
          case 'ol':
            return <List key={i} block={block} seed={seed} cpw={cpw} />
          case 'blockquote':
            return (
              <blockquote key={i}>
                <Inline words={placeholderWords(seed, block.words, cpw)} inline={inline} />
              </blockquote>
            )
          default:
            return (
              <p key={i}>
                <Inline words={placeholderWords(seed, block.words, cpw)} inline={inline} link={block.links > 0} />
              </p>
            )
        }
      })}
    </div>
  )
}
