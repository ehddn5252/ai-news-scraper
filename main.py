import json
import os
from datetime import datetime

from config import RSS_SOURCES, DATA_DIR, INSTAGRAM_POST_ENABLED, TELEGRAM_NOTIFY_ENABLED, WP_POST_ENABLED
from scrapers import RssScraper
from scrapers.base import Article
from scrapers.content_fetcher import fetch_article_content
from summarizer import AiSummarizer
from report_generator import generate_report

# Telegram 알림 (선택사항)
if TELEGRAM_NOTIFY_ENABLED:
    from telegram_notifier import notify_async, build_scraping_message, build_trend_message
else:
    notify_async = None

# Instagram 포스팅 (선택사항)
if INSTAGRAM_POST_ENABLED:
    from instagram_poster import post_news_async, build_news_caption
else:
    post_news_async = None


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

    # Telegram 시작 알림
    if TELEGRAM_NOTIFY_ENABLED and notify_async:
        notify_async("📰 AI 뉴스 스크래핑을 시작합니다...")

    # 1. RSS 수집
    print("[1/6] RSS 피드 수집 중...")
    rss = RssScraper()
    articles = rss.fetch(RSS_SOURCES)
    print(f"  총 {len(articles)}건 수집\n")

    # 2. 중복 제거
    print("[2/6] 중복 제거 중...")
    articles = deduplicate(articles)
    print(f"  중복 제거 후 {len(articles)}건\n")

    # 3. AI 요약 + 분류
    print("[3/6] AI 요약 및 분류 중...")
    summarizer = AiSummarizer()
    articles = summarizer.summarize(articles)
    trends = summarizer.extract_trends(articles)
    print()

    # 4. 기사 본문 추출 (상위 기사)
    print("[4/6] 주요 기사 본문 추출 중...")
    top_articles = sorted(articles, key=lambda a: a.importance, reverse=True)[:10]
    fetch_article_content(top_articles)
    print()

    # 5. 상세 요약 생성
    print("[5/6] 상세 요약 생성 중...")
    summarizer.summarize_detail(articles)
    print()

    # 6. 리포트 생성
    print("[6/6] 리포트 생성 중...")
    report_path = generate_report(articles, trends)
    print(f"  리포트 저장: {report_path}")

    # 원본 데이터 저장
    data_path = os.path.join(DATA_DIR, f"articles_{today}.json")
    save_data(articles, data_path)
    print(f"  데이터 저장: {data_path}")

    # WordPress 블로그 포스팅
    if WP_POST_ENABLED:
        print("\n[Blog] WordPress 블로그 포스팅 중...")
        try:
            from blog_poster import post_report_to_blog
            with open(report_path, "r", encoding="utf-8") as f:
                report_content = f.read()
            title = f"{today} AI 뉴스 데일리 리포트"
            success, result = post_report_to_blog(title, report_content)
            if success:
                print(f"  블로그 포스팅 성공 (ID: {result})")
            else:
                print(f"  블로그 포스팅 실패: {result}")
        except Exception as e:
            print(f"  블로그 포스팅 오류 (계속 진행): {e}")

    # Instagram 포스팅 (비활성화 시 스킵)
    if INSTAGRAM_POST_ENABLED and post_news_async and len(articles) > 0:
        print("\n[5/5] Instagram 포스팅 중...")
        # 상위 트렌드 기사를 Instagram에 포스팅
        try:
            top_articles = articles[:3]  # 상위 3개 기사
            for article in top_articles:
                # 이미지가 있는 경우에만 포스팅
                if hasattr(article, "image_url") and article.image_url:
                    caption = build_news_caption(
                        title=article.title[:100],
                        summary=article.summary[:200] if article.summary else "",
                        category=article.category if hasattr(article, "category") else "",
                        source=article.source,
                        url=article.url,
                    )
                    # 비동기 포스팅 (메인 루프를 블록하지 않음)
                    post_news_async(caption, article.image_url)
                    print(f"  ✓ Instagram 포스팅 예약됨: {article.title[:50]}")
        except Exception as e:
            print(f"  ⚠ Instagram 포스팅 오류 (계속 진행): {e}")

    # 6. Telegram 알림 (비활성화 시 스킵)
    if TELEGRAM_NOTIFY_ENABLED and notify_async:
        try:
            # 스크래핑 완료 알림
            total_before = len(articles) + len(set(a.url for a in articles))  # 대략적 계산
            msg = build_scraping_message(
                total_articles=total_before,
                unique_articles=len(articles),
                summarized_articles=len(articles),
                top_trends=[t.get("name", str(t))[:50] if isinstance(t, dict) else str(t)[:50] for t in (trends or [])],
            )
            notify_async(msg)

            # 주요 트렌드 알림
            if trends and len(trends) > 0:
                trend_msg = build_trend_message(trends, today)
                notify_async(trend_msg)
        except Exception as e:
            print(f"  ⚠ Telegram 알림 오류 (계속 진행): {e}")

    print(f"\n=== 완료! 총 {len(articles)}건 처리 ===")


if __name__ == "__main__":
    main()
