import EmptyState from "./EmptyState.jsx";
import ErrorState from "./ErrorState.jsx";
import LoadingState from "./LoadingState.jsx";
import MemeCard from "./MemeCard.jsx";

export default function MemeGrid({ items, loading, error, onPreview }) {
  if (loading) return <LoadingState label="圖片載入中..." />;
  if (error) return <ErrorState message={error} />;
  if (!items?.length) return <EmptyState message="沒有圖片資料" />;

  return (
    <section className="image-grid" aria-live="polite">
      {items.map((item) => (
        <MemeCard key={item.id} meme={item} onPreview={onPreview} />
      ))}
    </section>
  );
}
