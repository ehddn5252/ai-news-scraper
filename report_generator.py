import os
from datetime import datetime
from collections import defaultdict

from scrapers.base import Article
from config import REPORTS_DIR, CATEGORIES


def generate_report(articles: list[Article], trends: str) -> str:
    today = datetime.now().strftime("%Y-%m-%d")

    sorted_articles = sorted(articles, key=lambda a: a.importance, reverse=True)
    top5 = sorted_articles[:5]

    by_category = defaultdict(list)
    for a in sorted_articles:
        cat = a.category if a.category in CATEGORIES else "기타"
        by_category[cat].append(a)

    lines = [
        f"# AI 뉴스 데일리 리포트",
        f"",
        f"- **날짜**: {today}",
        f"- **수집 기사 수**: {len(articles)}건",
        f"- **소스**: {len(set(a.source for a in articles))}개 사이트",
        f"",
        f"---",
        f"",
        f"## 주요 뉴스 (상위 5건)",
        f"",
    ]

    for i, a in enumerate(top5, 1):
        summary = a.summary_ai or a.summary_raw[:60]
        lines.append(f"{i}. **[{a.title}]({a.url})**")
        lines.append(f"   - {summary} | {a.source} | {a.category} | 중요도: {'*' * a.importance}")
        lines.append(f"")

    lines.append(f"---")
    lines.append(f"")
    lines.append(f"## 카테고리별 정리")
    lines.append(f"")

    for cat in CATEGORIES:
        cat_articles = by_category.get(cat, [])
        if not cat_articles:
            continue
        lines.append(f"### {cat}")
        lines.append(f"")
        for a in cat_articles:
            summary = a.summary_ai or a.summary_raw[:60]
            lines.append(f"- [{a.title}]({a.url}) — {summary}")
        lines.append(f"")

    lines.append(f"---")
    lines.append(f"")
    lines.append(f"## 트렌드 키워드")
    lines.append(f"")
    lines.append(f"{trends}")
    lines.append(f"")

    report = "\n".join(lines)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    filepath = os.path.join(REPORTS_DIR, f"report_{today}.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report)

    return filepath
