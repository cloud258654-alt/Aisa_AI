import SafeImage from "./SafeImage.jsx";

export default function ImageModal({ meme, onClose }) {
  if (!meme) return null;

  return (
    <div className="modal-backdrop" role="presentation" onClick={onClose}>
      <section
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-label={meme.articleTitle}
        onClick={(event) => event.stopPropagation()}
      >
        <div className="dialog-header">
          <h2>{meme.articleTitle}</h2>
          <button className="icon-button" type="button" title="關閉" onClick={onClose}>
            <span aria-hidden="true">×</span>
          </button>
        </div>
        <div className="dialog-body">
          <SafeImage
            className="preview-image"
            src={meme.imageUrl}
            alt={meme.articleTitle}
            fallbackHref={meme.articleUrl}
            fallbackAction="可改開啟原文"
          />
          <div className="article-meta">
            <span className="badge">{meme.imageType || "image"}</span>
            <span>{new Date(meme.createdAt).toLocaleString("zh-TW")}</span>
          </div>
          <div className="dialog-actions">
            <a href={meme.imageUrl} target="_blank" rel="noreferrer">
              開啟圖片
            </a>
            <a href={meme.articleUrl} target="_blank" rel="noreferrer">
              開啟 PTT 原文
            </a>
          </div>
        </div>
      </section>
    </div>
  );
}
