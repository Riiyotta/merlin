// /blog/:slug template (CLONE_SPEC_PAGES_B.md §2). Header metadata is verbatim; the body is
// PLACEHOLDER text generated from the post's structure outline (see components/blog/Prose.jsx).
import { Navigate, useParams } from 'react-router-dom'
import data from '../data/blog-posts.json'
import BlogLayout from '../components/blog/BlogLayout.jsx'
import { useArticleMeta } from '../lib/blog-meta.js'
import Prose from '../components/blog/Prose.jsx'
import { ArrowLeft } from '../components/blog/Icons.jsx'

function Article({ post }) {
  useArticleMeta(post)
  return (
    <BlogLayout>
      <article id="blog-content" className="blog_article__Uk9MF">
        <a className="blog_back__4b1m9" href="/blog">
          <ArrowLeft /> All stories
        </a>
        <header className="blog_articleHeader__3w7of">
          <span className="blog_eyebrow__0KDg5">{post.category}</span>
          <h1>{post.title}</h1>
          <div className="blog_author__UxA6e">
            <img src={post.authorAvatar} alt="" width={36} height={36} />
            <div>
              <span>{post.author}</span>
              <time dateTime={post.date}>{post.dateDisplayArticle}</time>
            </div>
          </div>
        </header>
        {post.cover && <img className="blog_articleImage__wj3kN" src={post.cover} alt={post.coverAlt} />}
        <Prose slug={post.slug} structure={post.structure} cpw={post.bodyStats?.fillerCharsPerWord} />
        <footer className="blog_articleEnd__zI6hK">
          <span>Thanks for spending a little time with us.</span>
          <a className="blog_back__4b1m9" href="/blog">
            <ArrowLeft /> Back to all stories
          </a>
        </footer>
      </article>
    </BlogLayout>
  )
}

export default function BlogPostPage() {
  const { slug } = useParams()
  const post = data.posts.find((p) => p.slug === slug)
  if (!post) return <Navigate to="/blog" replace />
  return <Article post={post} />
}
