import { useState } from "react";

export default function SearchBar({ onSearch, onClear }) {
  const [keyword, setKeyword] = useState("");

  function handleSubmit(event) {
    event.preventDefault();
    onSearch(keyword.trim());
  }

  function handleClear() {
    setKeyword("");
    onClear();
  }

  return (
    <form className="search-form" onSubmit={handleSubmit}>
      <label htmlFor="searchInput">搜尋</label>
      <div className="search-row">
        <input
          id="searchInput"
          type="search"
          value={keyword}
          placeholder="標題或作者"
          autoComplete="off"
          onChange={(event) => setKeyword(event.target.value)}
        />
        <button type="submit">搜尋</button>
        <button type="button" className="secondary-button" onClick={handleClear}>
          清除
        </button>
      </div>
    </form>
  );
}
