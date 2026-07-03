import EmptyState from "../components/EmptyState.jsx";
import ErrorState from "../components/ErrorState.jsx";
import LoadingState from "../components/LoadingState.jsx";

export default function ArticleList({ title, items, loading, error, onOpenArticle }) {
  if (loading) return <LoadingState label="文章載入中..." />;
  if (error) return <ErrorState message={error} />;
  if (!items?.length) return <EmptyState message="沒有符合條件的文章" />;

  return (
    <section className="content-list" aria-label={title} aria-live="polite">
      {items.map((item) => (
        <article className="article-card" key={item.id}>
          <div>
            <h3>
              <a className="article-title-link" href={item.articleUrl} target="_blank" rel="noreferrer">
                {item.title}
              </a>
            </h3>
            <div className="article-meta">
              <span className="badge hot">推 {item.pushCount}</span>
              <span className="badge">{item.imageCount} 圖</span>
              <span>{item.author || "匿名"}</span>
              <span>{item.articleDate || item.createdAt}</span>
            </div>
          </div>
          <div className="card-actions">
            <button type="button" onClick={() => onOpenArticle(item)}>
              詳情
            </button>
            <a href={item.articleUrl} target="_blank" rel="noreferrer">
              PTT
            </a>
          </div>
        </article>
      ))}
    </section>
  );
}
