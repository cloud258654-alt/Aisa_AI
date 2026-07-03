export default function ErrorState({ message = "資料讀取失敗" }) {
  return <div className="state-box error-box">{message}</div>;
}
