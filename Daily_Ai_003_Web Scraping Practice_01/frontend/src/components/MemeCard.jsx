import SafeImage from "./SafeImage.jsx";

export default function MemeCard({ meme, onPreview }) {
  return (
    <article className="image-card">
      <button type="button" className="image-button" onClick={() => onPreview(meme)}>
        <SafeImage
          src={meme.imageUrl}
          alt={meme.articleTitle}
          fallbackHref={meme.articleUrl}
          fallbackAction="下方可開啟原文"
        />
      </button>
      <div>
        <h3>
          <a className="title-link" href={meme.articleUrl} target="_blank" rel="noreferrer">
            {meme.articleTitle}
          </a>
        </h3>
        <p>
          {meme.imageType || "image"} · {new Date(meme.createdAt).toLocaleDateString("zh-TW")}
        </p>
        <a className="primary-link" href={meme.articleUrl} target="_blank" rel="noreferrer">
          開啟原文
        </a>
      </div>
    </article>
  );
}
