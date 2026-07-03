import re
from urllib.parse import urlparse

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


def _is_allowed_image_url(url: str) -> bool:
    parsed = urlparse(url)
    path = parsed.path.lower()
    for ext in ALLOWED_EXTENSIONS:
        if path.endswith(ext):
            return True
    return False


def _normalize_imgur_url(url: str) -> str:
    parsed = urlparse(url)
    if "imgur.com" not in parsed.netloc:
        return url
    match = re.search(r"/([a-zA-Z0-9]+)(?:\.[a-z]+)?$", parsed.path)
    if not match:
        return url
    img_id = match.group(1)
    return f"https://i.imgur.com/{img_id}.jpg"


def extract_image_urls(html: str, article_url: str) -> list[str]:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    main_content = soup.find(id="main-content")
    if not main_content:
        return []

    for tag in main_content.find_all(["div", "span"]):
        classes = tag.attrs.get("class", []) if tag.attrs else []
        if "push" in classes or "article-metaline" in classes:
            tag.decompose()
        elif tag.name == "div" and tag.find("span", class_="hl"):
            tag.decompose()

    urls: list[str] = []
    for a_tag in main_content.find_all("a"):
        href = a_tag.get("href", "")
        if not href:
            continue
        normalized = _normalize_imgur_url(href)
        if _is_allowed_image_url(normalized):
            urls.append(normalized)

    for img_tag in main_content.find_all("img"):
        src = img_tag.get("src", "")
        if _is_allowed_image_url(src):
            urls.append(src)

    seen: set[str] = set()
    unique: list[str] = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            unique.append(url)
    return unique
