import { useEffect, useMemo, useState } from "react";
import { API_BASE, getArticleDetail, getArticles, getImages, getPopularArticles, getStatistics, searchArticles } from "../api/client.js";
import EmptyState from "../components/EmptyState.jsx";
import ErrorState from "../components/ErrorState.jsx";
import Header from "../components/Header.jsx";
import ImageModal from "../components/ImageModal.jsx";
import LoadingState from "../components/LoadingState.jsx";
import MemeGrid from "../components/MemeGrid.jsx";
import SearchBar from "../components/SearchBar.jsx";
import SafeImage from "../components/SafeImage.jsx";
import SortTabs from "../components/SortTabs.jsx";
import StatsPanel from "../components/StatsPanel.jsx";
import useApi from "../hooks/useApi.js";
import ArticleList from "./_ArticleList.jsx";
import PopularPage from "./PopularPage.jsx";

const PAGE_SIZE = 30;

export default function HomePage() {
  const [view, setView] = useState("latest");
  const [sort, setSort] = useState("article_date:desc");
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(1);
  const [previewMeme, setPreviewMeme] = useState(null);
  const [articleDetail, setArticleDetail] = useState(null);
  const [articleLoading, setArticleLoading] = useState(false);
  const [articleError, setArticleError] = useState("");

  const [sortBy, order] = sort.split(":");

  const statsApi = useApi(() => getStatistics(), []);
  const listApi = useApi(() => {
    if (query) return searchArticles({ q: query, page, pageSize: PAGE_SIZE });
    if (view === "popular") return getPopularArticles({ page, pageSize: PAGE_SIZE });
    if (view === "images") return getImages({ page, pageSize: PAGE_SIZE });
    return getArticles({ page, pageSize: PAGE_SIZE, sortBy, order });
  }, [view, sortBy, order, query, page]);

  const apiStatus = useMemo(() => {
    if (statsApi.error || listApi.error) return { label: "API issue", type: "error" };
    if (statsApi.loading || listApi.loading) return { label: "API checking", type: "muted" };
    return { label: "API online", type: "ok" };
  }, [statsApi.error, statsApi.loading, listApi.error, listApi.loading]);

  const items = listApi.data?.items || [];
  const pagination = listApi.data?.pagination || { page: 1, totalPages: 1 };

  useEffect(() => {
    if (import.meta.env.DEV && view === "images" && items.length) {
      console.log(
        "Sample image URLs:",
        items.slice(0, 3).map((item) => item.imageUrl)
      );
    }
  }, [items, view]);

  const apiErrorMessage =
    statsApi.error || listApi.error
      ? `無法連線到 ${API_BASE}。若 backend 已啟動，可能是瀏覽器 CORS 限制；依 Sprint 原則請回報後由 backend 任務處理。`
      : "";

  function refreshAll() {
    statsApi.reload();
    listApi.reload();
  }

  function changeView(nextView) {
    setView(nextView);
    setQuery("");
    setPage(1);
  }

  async function openArticle(article) {
    setArticleLoading(true);
    setArticleError("");
    setArticleDetail(null);
    try {
      setArticleDetail(await getArticleDetail(article.id));
    } catch (error) {
      setArticleError(error.message || "文章詳情讀取失敗");
    } finally {
      setArticleLoading(false);
    }
  }

  function closeArticleModal() {
    setArticleLoading(false);
    setArticleError("");
    setArticleDetail(null);
  }

  return (
    <div className="app-shell">
      <Header apiStatus={apiStatus} onRefresh={refreshAll} />
      <main>
        <StatsPanel stats={statsApi.data} loading={statsApi.loading} error={statsApi.error} />

        <section className="controls" aria-label="瀏覽控制">
          <SortTabs
            view={view}
            sort={sort}
            onViewChange={changeView}
            onSortChange={(nextSort) => {
              setSort(nextSort);
              setPage(1);
            }}
          />
          <SearchBar
            onSearch={(keyword) => {
              setQuery(keyword);
              setPage(1);
            }}
            onClear={() => {
              setQuery("");
              setPage(1);
            }}
          />
        </section>

        {apiErrorMessage ? <ErrorState message={apiErrorMessage} /> : null}

        {query || view === "latest" ? (
          <ArticleList title="文章列表" items={items} loading={listApi.loading} error={listApi.error} onOpenArticle={openArticle} />
        ) : view === "popular" ? (
          <PopularPage items={items} loading={listApi.loading} error={listApi.error} onOpenArticle={openArticle} />
        ) : (
          <MemeGrid items={items} loading={listApi.loading} error={listApi.error} onPreview={setPreviewMeme} />
        )}

        <nav className="pager" aria-label="分頁">
          <button className="secondary-button" type="button" disabled={page <= 1} onClick={() => setPage((current) => current - 1)}>
            上一頁
          </button>
          <span>第 {pagination.page || page} / {pagination.totalPages || 1} 頁</span>
          <button
            className="secondary-button"
            type="button"
            disabled={page >= (pagination.totalPages || 1)}
            onClick={() => setPage((current) => current + 1)}
          >
            下一頁
          </button>
        </nav>
      </main>

      <ImageModal meme={previewMeme} onClose={() => setPreviewMeme(null)} />

      {articleLoading || articleError || articleDetail ? (
        <div className="modal-backdrop" role="presentation" onClick={closeArticleModal}>
          <section className="modal" role="dialog" aria-modal="true" onClick={(event) => event.stopPropagation()}>
            <div className="dialog-header">
              <h2>{articleDetail?.title || "文章詳情"}</h2>
              <button className="icon-button" type="button" title="關閉" onClick={closeArticleModal}>
                <span aria-hidden="true">×</span>
              </button>
            </div>
            <div className="dialog-body">
              {articleLoading ? <LoadingState /> : null}
              {articleError ? <ErrorState message={articleError} /> : null}
              {articleDetail ? (
                <>
                  <div className="article-meta">
                    <span className="badge hot">推 {articleDetail.pushCount}</span>
                    <span className="badge">{articleDetail.images?.length || 0} 圖</span>
                    <span>{articleDetail.author || "匿名"}</span>
                  </div>
                  <div className="dialog-actions">
                    <a href={articleDetail.articleUrl} target="_blank" rel="noreferrer">開啟 PTT 原文</a>
                  </div>
                  {articleDetail.images?.length ? (
                    <div className="dialog-images">
                      {articleDetail.images.map((image) => (
                        <SafeImage
                          key={image.id}
                          src={image.imageUrl}
                          alt={articleDetail.title}
                          fallbackHref={articleDetail.articleUrl}
                          fallbackAction="可改開啟原文"
                        />
                      ))}
                    </div>
                  ) : (
                    <EmptyState message="此文章沒有圖片" />
                  )}
                </>
              ) : null}
            </div>
          </section>
        </div>
      ) : null}
    </div>
  );
}
