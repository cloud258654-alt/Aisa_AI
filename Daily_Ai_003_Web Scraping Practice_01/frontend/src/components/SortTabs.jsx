export default function SortTabs({ view, sort, onViewChange, onSortChange }) {
  return (
    <>
      <div className="tabs" role="tablist" aria-label="資料類型">
        <button
          className={`tab ${view === "latest" ? "is-active" : ""}`}
          type="button"
          onClick={() => onViewChange("latest")}
        >
          最新
        </button>
        <button
          className={`tab ${view === "popular" ? "is-active" : ""}`}
          type="button"
          onClick={() => onViewChange("popular")}
        >
          熱門
        </button>
        <button
          className={`tab ${view === "images" ? "is-active" : ""}`}
          type="button"
          onClick={() => onViewChange("images")}
        >
          圖片
        </button>
      </div>
      <div className="sort-row">
        <label htmlFor="sortSelect">排序</label>
        <select id="sortSelect" value={sort} onChange={(event) => onSortChange(event.target.value)}>
          <option value="article_date:desc">文章日期新到舊</option>
          <option value="push_count:desc">推文數高到低</option>
          <option value="created_at:desc">收錄時間新到舊</option>
          <option value="article_date:asc">文章日期舊到新</option>
        </select>
      </div>
    </>
  );
}
