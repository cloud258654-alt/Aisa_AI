export default function EmptyState({ message = "目前沒有資料" }) {
  return <div className="state-box">{message}</div>;
}
