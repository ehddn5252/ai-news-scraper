import os
import tempfile

from scrapers.base import Article
from report_generator import generate_report
from config import REPORTS_DIR


def _make_articles(n: int) -> list[Article]:
    articles = []
    for i in range(n):
        articles.append(Article(
            title=f"Article {i}",
            url=f"https://example.com/{i}",
            date="2026-01-01",
            source="TestSource",
            summary_raw=f"Raw summary {i}",
            category="LLM/생성형 AI",
            importance=5 - (i % 5),
            summary_ai=f"AI 요약 {i}",
        ))
    return articles


def test_report_contains_header():
    articles = _make_articles(3)
    path = generate_report(articles, "AI, LLM, 로봇")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "# AI 뉴스 데일리 리포트" in content
    assert "수집 기사 수" in content
    os.remove(path)


def test_report_contains_top5():
    articles = _make_articles(10)
    path = generate_report(articles, "AI")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "## 주요 뉴스 (상위 5건)" in content
    assert "Article 0" in content
    os.remove(path)


def test_report_includes_detail_summary():
    articles = _make_articles(3)
    articles[0].detail_summary = "상세 요약 테스트 문장입니다."
    path = generate_report(articles, "AI")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "상세 요약 테스트 문장입니다." in content
    os.remove(path)


def test_report_includes_trends():
    articles = _make_articles(3)
    path = generate_report(articles, "트렌드1, 트렌드2")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "트렌드1" in content
    assert "## 트렌드 키워드" in content
    os.remove(path)
