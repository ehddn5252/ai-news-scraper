import json
import os
from datetime import datetime

from config import RSS_SOURCES, DATA_DIR
from scrapers import RssScraper
from scrapers.base import Article
from summarizer import AiSummarizer
from report_generator import generate_report


def deduplicate(articles: list[Article]) -> list[Article]:
    seen_urls = set()
    unique = []
    for a in articles:
        if a.url not in seen_urls:
            seen_urls.add(a.url)
            unique.append(a)
    return unique


def save_data(articles: list[Article], filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump([a.to_dict() for a in articles], f, ensure_ascii=False, indent=2)


def main():
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"=== AI 뉴스 스크래핑 시작 ({today}) ===\n")

    # 1. RSS 수집
    print("[1/4] RSS 피드 수집 중...")
    rss = RssScraper()
    articles = rss.fetch(RSS_SOURCES)
    print(f"  총 {len(articles)}건 수집\n")

    # 2. 중복 제거
    print("[2/4] 중복 제거 중...")
    articles = deduplicate(articles)
    print(f"  중복 제거 후 {len(articles)}건\n")

    # 3. AI 요약 + 분류
    print("[3/4] AI 요약 및 분류 중...")
    summarizer = AiSummarizer()
    articles = summarizer.summarize(articles)
    trends = summarizer.extract_trends(articles)
    print()

    # 4. 리포트 생성
    print("[4/4] 리포트 생성 중...")
    report_path = generate_report(articles, trends)
    print(f"  리포트 저장: {report_path}")

    # 원본 데이터 저장
    data_path = os.path.join(DATA_DIR, f"articles_{today}.json")
    save_data(articles, data_path)
    print(f"  데이터 저장: {data_path}")

    print(f"\n=== 완료! 총 {len(articles)}건 처리 ===")


if __name__ == "__main__":
    main()
