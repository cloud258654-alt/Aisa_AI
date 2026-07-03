import logging
import re
import time
from datetime import datetime, timezone
from typing import Optional

import requests
from bs4 import BeautifulSoup

from app.crawler.image_extractor import extract_image_urls

logger = logging.getLogger("crawler")

PTT_BASE = "https://www.ptt.cc"
BOARD_URL = f"{PTT_BASE}/bbs/joke/index.html"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}
COOKIES = {"over18": "1"}
DELAY = 2
MAX_PAGES = 3


def _fetch(url: str) -> Optional[str]:
    try:
        resp = requests.get(url, headers=HEADERS, cookies=COOKIES, timeout=30)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as e:
        logger.warning("HTTP request failed: %s — %s", url, e)
        return None


def _parse_push_count(push_span) -> int:
    if not push_span:
        return 0
    text = push_span.get_text(strip=True)
    if text == "爆":
        return 100
    if text.startswith("X"):
        try:
            return -int(text[1:])
        except ValueError:
            return 0
    try:
        return int(text)
    except ValueError:
        return 0


def _parse_article_date(article_soup: BeautifulSoup) -> Optional[datetime]:
    metalines = article_soup.find_all("div", class_="article-metaline")
    for ml in metalines:
        tag = ml.find("span", class_="article-meta-tag")
        val = ml.find("span", class_="article-meta-value")
        if tag and val and "時間" in tag.get_text():
            date_str = val.get_text(strip=True)
            try:
                dt = datetime.strptime(date_str, "%a %b %d %H:%M:%S %Y")
                return dt.replace(tzinfo=timezone.utc)
            except ValueError:
                pass
    return None


def _parse_article_author(article_soup: BeautifulSoup) -> Optional[str]:
    metalines = article_soup.find_all("div", class_="article-metaline")
    for ml in metalines:
        tag = ml.find("span", class_="article-meta-tag")
        val = ml.find("span", class_="article-meta-value")
        if tag and val and "作者" in tag.get_text():
            author = val.get_text(strip=True)
            match = re.match(r"(.+?)\s*\(", author)
            if match:
                return match.group(1).strip()
            return author
    return None


def crawl_board_page(page_url: str) -> list[dict]:
    html = _fetch(page_url)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    entries = soup.find_all("div", class_="r-ent")
    articles: list[dict] = []
    for entry in entries:
        title_div = entry.find("div", class_="title")
        if not title_div:
            continue
        link = title_div.find("a")
        if not link:
            continue
        href = link.get("href", "")
        if not href:
            continue

        meta_div = entry.find("div", class_="meta")
        author = ""
        date_str = ""
        if meta_div:
            author_div = meta_div.find("div", class_="author")
            if author_div:
                author = author_div.get_text(strip=True)
            date_div = meta_div.find("div", class_="date")
            if date_div:
                date_str = date_div.get_text(strip=True)

        nrec_div = entry.find("div", class_="nrec")
        push_span = nrec_div.find("span") if nrec_div else None
        push_count = _parse_push_count(push_span)

        articles.append(
            {
                "title": link.get_text(strip=True),
                "author": author,
                "article_url": f"{PTT_BASE}{href}",
                "date_str": date_str,
                "push_count": push_count,
            }
        )
    return articles


def get_next_page_url(html: str) -> Optional[str]:
    soup = BeautifulSoup(html, "html.parser")
    for btn in soup.find_all("a", class_="btn"):
        if "上頁" in btn.get_text(strip=True) or "‹ 上頁" in btn.get_text(strip=True):
            href = btn.get("href", "")
            if href:
                return f"{PTT_BASE}{href}"
    return None


def fetch_article_detail(article_url: str) -> Optional[dict]:
    html = _fetch(article_url)
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")
    main_content = soup.find(id="main-content")
    if not main_content:
        return None

    author = _parse_article_author(soup)
    article_date = _parse_article_date(soup)
    images = extract_image_urls(html, article_url)

    return {
        "author": author,
        "article_date": article_date,
        "images": images,
    }


def crawl_joke_board(pages: int = 1, delay: float = DELAY) -> list[dict]:
    page_url = BOARD_URL
    all_articles: list[dict] = []
    for page_num in range(min(pages, MAX_PAGES)):
        logger.info("Fetching board page %d: %s", page_num + 1, page_url)
        html = _fetch(page_url)
        if not html:
            logger.warning("Failed to fetch board page %d, stopping", page_num + 1)
            break

        articles = crawl_board_page(page_url)
        logger.info("Found %d articles on page %d", len(articles), page_num + 1)

        for art in articles:
            time.sleep(delay)
            detail = fetch_article_detail(art["article_url"])
            if detail:
                art["author"] = detail["author"] or art["author"]
                art["article_date"] = detail["article_date"]
                art["images"] = detail["images"]
            else:
                art["images"] = []
            all_articles.append(art)

        if page_num < pages - 1:
            next_url = get_next_page_url(html)
            if not next_url:
                logger.info("No next page available, stopping")
                break
            page_url = next_url
            if page_num < pages - 1:
                time.sleep(delay)

    return all_articles
