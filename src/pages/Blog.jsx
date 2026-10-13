// /blog index (CLONE_SPEC_PAGES_B.md §1). Titles, dates and labels are verbatim; no body copy appears here.
// Hover motion (row title/arrow, featured image scale, read-link arrow) is pure CSS in ea3e27….
import data from '../data/blog-posts.json'
import BlogLayout, { useDocumentMeta } from '../components/blog/BlogLayout.jsx'
import { ArrowUpRight } from '../components/blog/Icons.jsx'

// Original phrase with the same word count (8) as the live handwritten aside; the live line is not reproduced.
const MANIFESTO_NOTE = 'less to juggle. more room to just be.'

function Meta({ post }) {
  return (
    <div className="blog_meta__jCSwR">
      <span>{post.author}</span>
      <time dateTime={post.date}>{post.dateDisplayIndex}</time>
    </div>
  )
}

export default function BlogPage() {
  useDocumentMeta('Blog — Merlin', 'Notes on building Merlin, finding focus, and making room for life.')
  const [featured, ...stories] = data.posts

  return (
    <BlogLayout>
      <div id="blog-content" className="blog_index__3_0oG">
        <header className="blog_intro__ggRFG">
          <h1>
            A little more
            <br />
            to think about.
          </h1>
          <p>
            Notes on building Merlin, finding focus,
            <br /> and making room for life.
          </p>
        </header>
        <a className="blog_featured__dQvxo" href={`/blog/${featured.slug}`}>
          <div className="blog_featuredImage__DhF7y">
            <img src={featured.indexImage} alt="" width={1400} height={1050} fetchpriority="high" />
          </div>
          <div className="blog_featuredCopy__844eq">
            <span className="blog_eyebrow__0KDg5">
              {featured.category}
              <span className="blog_latest__S4ifZ">Latest story</span>
            </span>
            <h2>{featured.title}</h2>
            <Meta post={featured} />
            <span className="blog_readLink__2wa5U">
              Read the story <ArrowUpRight />
            </span>
          </div>
        </a>
        <section className="blog_stories__Dlir_" aria-labelledby="more-stories">
          <div className="blog_sectionHeading__dCqQ1">
            <h2 id="more-stories">More from Merlin</h2>
            <span>A few things worth sharing.</span>
          </div>
          <div className="blog_storyList__M4Hb4">
            {stories.map((post) => (
              <a key={post.slug} className="blog_story__uUvdL" href={`/blog/${post.slug}`}>
                <span className="blog_storyCategory__LA7IY">{post.category}</span>
                <div className="blog_storyCopy__ILI0m">
                  <h3>{post.title}</h3>
                  <Meta post={post} />
                </div>
                <span className="blog_storyArrow__IWJ3c">
                  <ArrowUpRight />
                </span>
              </a>
            ))}
          </div>
        </section>
        <aside className="blog_manifesto__VgyoG">
          <span className="blog_handwritten__cIXLa">{MANIFESTO_NOTE}</span>
          <a href="/manifesto">
            Why we’re building Merlin <ArrowUpRight />
          </a>
        </aside>
      </div>
    </BlogLayout>
  )
}
