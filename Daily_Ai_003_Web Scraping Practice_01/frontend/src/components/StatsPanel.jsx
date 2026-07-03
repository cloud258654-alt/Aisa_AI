import EmptyState from "./EmptyState.jsx";
import ErrorState from "./ErrorState.jsx";
import LoadingState from "./LoadingState.jsx";

function valueOrDash(value) {
  return value ?? "--";
}

export default function StatsPanel({ stats, loading, error }) {
  if (loading) return <LoadingState label="統計資料載入中..." />;
  if (error) return <ErrorState message={error} />;
  if (!stats) return <EmptyState message="尚無統計資料" />;

  return (
    <section className="dashboard" aria-label="統計資訊">
      <article>
        <span>Articles</span>
        <strong>{valueOrDash(stats.articles)}</strong>
      </article>
      <article>
        <span>Images</span>
        <strong>{valueOrDash(stats.images)}</strong>
      </article>
      <article>
        <span>Crawler Logs</span>
        <strong>{valueOrDash(stats.crawlerLogs)}</strong>
      </article>
      <article>
        <span>Last Status</span>
        <strong className="status-text">{valueOrDash(stats.lastCrawlerStatus)}</strong>
      </article>
      <article className="wide-stat">
        <span>Last Update</span>
        <strong className="status-text">{stats.lastUpdate ? new Date(stats.lastUpdate).toLocaleString("zh-TW") : "--"}</strong>
      </article>
    </section>
  );
}
