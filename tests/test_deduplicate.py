from scrapers.base import Article
from main import deduplicate


def _article(url: str, title: str = "test") -> Article:
    return Article(title=title, url=url, date="2026-01-01", source="test", summary_raw="raw")


def test_removes_duplicate_urls():
    articles = [_article("https://a.com"), _article("https://a.com"), _article("https://b.com")]
    result = deduplicate(articles)
    assert len(result) == 2
    assert [a.url for a in result] == ["https://a.com", "https://b.com"]


def test_preserves_order():
    articles = [_article("https://c.com"), _article("https://a.com"), _article("https://b.com")]
    result = deduplicate(articles)
    assert [a.url for a in result] == ["https://c.com", "https://a.com", "https://b.com"]


def test_empty_list():
    assert deduplicate([]) == []


def test_all_unique():
    articles = [_article(f"https://{i}.com") for i in range(5)]
    result = deduplicate(articles)
    assert len(result) == 5
