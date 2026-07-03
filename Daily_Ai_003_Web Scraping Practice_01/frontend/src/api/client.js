const API_BASE = "http://127.0.0.1:8000/api";

async function request(path, params = {}) {
  const url = new URL(`${API_BASE}${path}`);
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.set(key, value);
    }
  });

  const response = await fetch(url);
  const payload = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(payload?.error?.message || `HTTP ${response.status}`);
  }

  return payload;
}

function normalizeImageUrl(value) {
  if (!value) return "";
  const url = String(value).trim();
  const imgurPageMatch = url.match(/^https?:\/\/(?:www\.)?imgur\.com\/([A-Za-z0-9]+)$/i);
  if (imgurPageMatch) return `https://i.imgur.com/${imgurPageMatch[1]}.jpg`;
  if (url.startsWith("//")) return `https:${url}`;
  return url;
}

export function normalizeImageItem(item = {}) {
  return {
    id: item.id,
    articleId: item.articleId ?? item.article_id,
    imageUrl: normalizeImageUrl(item.imageUrl ?? item.image_url),
    imageType: item.imageType ?? item.image_type,
    articleTitle: item.articleTitle ?? item.article_title ?? "",
    articleUrl: item.articleUrl ?? item.article_url ?? "",
    createdAt: item.createdAt ?? item.created_at,
  };
}

function normalizeImageList(payload) {
  return {
    ...payload,
    items: (payload.items || []).map(normalizeImageItem),
  };
}

function normalizeArticleDetail(payload) {
  return {
    ...payload,
    articleUrl: payload.articleUrl ?? payload.article_url,
    articleDate: payload.articleDate ?? payload.article_date,
    pushCount: payload.pushCount ?? payload.push_count,
    sourceBoard: payload.sourceBoard ?? payload.source_board,
    createdAt: payload.createdAt ?? payload.created_at,
    updatedAt: payload.updatedAt ?? payload.updated_at,
    images: (payload.images || []).map(normalizeImageItem),
  };
}

export function getHealth() {
  return request("/health");
}

export function getStatistics() {
  return request("/statistics");
}

export function getImages({ page = 1, pageSize = 30 } = {}) {
  return request("/images", { page, pageSize }).then(normalizeImageList);
}

export function getArticles({ page = 1, pageSize = 20, sortBy = "article_date", order = "desc" } = {}) {
  return request("/articles", { page, pageSize, sortBy, order });
}

export function getArticleDetail(id) {
  return request(`/articles/${id}`).then(normalizeArticleDetail);
}

export function searchArticles({ q, page = 1, pageSize = 20 } = {}) {
  return request("/search", { q, page, pageSize });
}

export function getPopularArticles({ page = 1, pageSize = 20 } = {}) {
  return request("/popular", { page, pageSize });
}

export { API_BASE };
