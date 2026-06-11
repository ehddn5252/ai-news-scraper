import time
from datetime import datetime

import feedparser

from .base import Article
from config import REQUEST_DELAY


class RssScraper:
    def fetch(self, sources: list[dict]) -> list[Article]:
        articles = []
        for source in sources:
            try:
                feed = feedparser.parse(source["url"])
                for entry in feed.entries[:15]:
                    article = self._parse_entry(entry, source["name"])
                    if article:
                        articles.append(article)
                print(f"  [OK] {source['name']}: {min(len(feed.entries), 15)}건")
            except Exception as e:
                print(f"  [FAIL] {source['name']}: {e}")
            time.sleep(REQUEST_DELAY)
        return articles

    def _parse_entry(self, entry, source_name: str) -> Article | None:
        title = getattr(entry, "title", "").strip()
        link = getattr(entry, "link", "").strip()
        if not title or not link:
            return None

        published = getattr(entry, "published_parsed", None)
        if published:
            date_str = datetime(*published[:6]).strftime("%Y-%m-%d")
        else:
            date_str = datetime.now().strftime("%Y-%m-%d")

        summary = getattr(entry, "summary", "")
        if hasattr(entry, "content"):
            summary = entry.content[0].get("value", summary)
        summary = self._strip_html(summary)[:500]

        return Article(
            title=title,
            url=link,
            date=date_str,
            source=source_name,
            summary_raw=summary,
        )

    @staticmethod
    def _strip_html(text: str) -> str:
        from bs4 import BeautifulSoup
        return BeautifulSoup(text, "html.parser").get_text(separator=" ", strip=True)
