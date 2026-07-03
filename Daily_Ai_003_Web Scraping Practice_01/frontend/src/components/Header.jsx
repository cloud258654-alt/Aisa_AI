export default function Header({ apiStatus, onRefresh }) {
  return (
    <header className="topbar">
      <div>
        <p className="eyebrow">PTT Joke Board</p>
        <h1>Joke Meme</h1>
      </div>
      <div className="status-group">
        <span className={`status-pill status-${apiStatus.type}`}>{apiStatus.label}</span>
        <button className="icon-button" type="button" onClick={onRefresh} title="重新整理">
          <span aria-hidden="true">↻</span>
        </button>
      </div>
    </header>
  );
}
