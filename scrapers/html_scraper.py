import time

import requests
from bs4 import BeautifulSoup

from .base import Article
from config import REQUEST_DELAY, REQUEST_TIMEOUT

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}


class HtmlScraper:
    """RSS가 없는 사이트용 HTML 스크래퍼. 사이트별 파서를 등록해서 사용한다."""

    def fetch(self, url: str, source_name: str, parse_fn) -> list[Article]:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            articles = parse_fn(soup, source_name)
            print(f"  [OK] {source_name}: {len(articles)}건")
            time.sleep(REQUEST_DELAY)
            return articles
        except Exception as e:
            print(f"  [FAIL] {source_name}: {e}")
            return []
