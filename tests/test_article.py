from scrapers.base import Article


def test_to_dict_and_from_dict():
    original = Article(
        title="Test Title",
        url="https://example.com",
        date="2026-01-01",
        source="TestSource",
        summary_raw="raw summary",
        category="LLM/생성형 AI",
        importance=5,
        summary_ai="AI 요약",
        content="본문 내용",
        detail_summary="상세 요약",
    )
    d = original.to_dict()
    restored = Article.from_dict(d)
    assert restored.title == original.title
    assert restored.url == original.url
    assert restored.category == original.category
    assert restored.importance == original.importance
    assert restored.content == original.content
    assert restored.detail_summary == original.detail_summary


def test_from_dict_ignores_extra_keys():
    d = {"title": "t", "url": "u", "date": "d", "source": "s", "summary_raw": "r", "extra_field": "x"}
    article = Article.from_dict(d)
    assert article.title == "t"
    assert not hasattr(article, "extra_field") or "extra_field" not in article.__dataclass_fields__


def test_default_values():
    article = Article(title="t", url="u", date="d", source="s", summary_raw="r")
    assert article.category == ""
    assert article.importance == 0
    assert article.summary_ai == ""
    assert article.content == ""
    assert article.detail_summary == ""
