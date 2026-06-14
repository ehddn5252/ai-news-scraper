import time
import trafilatura

from .base import Article
from config import REQUEST_DELAY


def fetch_article_content(articles: list[Article], max_chars: int = 3000) -> list[Article]:
    for i, article in enumerate(articles):
        try:
            downloaded = trafilatura.fetch_url(article.url)
            if downloaded:
                text = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
                if text:
                    article.content = text[:max_chars]
                    print(f"  [{i+1}/{len(articles)}] OK: {article.title[:50]}")
                else:
                    print(f"  [{i+1}/{len(articles)}] SKIP (본문 추출 실패): {article.title[:50]}")
            else:
                print(f"  [{i+1}/{len(articles)}] SKIP (다운로드 실패): {article.title[:50]}")
        except Exception as e:
            print(f"  [{i+1}/{len(articles)}] FAIL: {article.title[:50]} - {e}")
        time.sleep(REQUEST_DELAY)
    fetched = sum(1 for a in articles if a.content)
    print(f"  본문 추출 완료: {fetched}/{len(articles)}건")
    return articles
