import json

from anthropic import Anthropic

from scrapers.base import Article
from config import CLAUDE_API_KEY, CLAUDE_MODEL, CATEGORIES

SYSTEM_PROMPT = f"""너는 AI 뉴스 분석 전문가야.
주어진 뉴스 기사 목록을 분석해서 JSON으로 결과를 반환해.

각 기사에 대해:
1. summary_ai: 한국어 1줄 요약 (30자 이내)
2. category: 다음 중 하나 — {', '.join(CATEGORIES)}
3. importance: 1~5 점수 (산업 영향력, 기술 혁신성, 화제성 기준)

반드시 유효한 JSON 배열만 출력해. 설명 텍스트 없이 JSON만."""

TREND_PROMPT = """다음 AI 뉴스 기사 제목들을 보고, 이번 수집분의 핵심 트렌드 키워드를 한국어로 5개 추출해.
쉼표로 구분해서 키워드만 출력해. 설명 없이 키워드만.

제목 목록:
{titles}"""


class AiSummarizer:
    def __init__(self):
        self.client = Anthropic(api_key=CLAUDE_API_KEY) if CLAUDE_API_KEY else None

    def summarize(self, articles: list[Article]) -> list[Article]:
        if not self.client:
            print("  [SKIP] CLAUDE_API_KEY가 설정되지 않아 AI 요약을 건너뜁니다.")
            for a in articles:
                a.summary_ai = a.summary_raw[:60]
                a.category = "기타"
                a.importance = 3
            return articles

        batch_size = 10
        for i in range(0, len(articles), batch_size):
            batch = articles[i:i + batch_size]
            self._summarize_batch(batch)
        return articles

    def extract_trends(self, articles: list[Article]) -> str:
        if not self.client:
            return "AI, LLM, 자동화, 로봇, 규제"

        titles = "\n".join(f"- {a.title}" for a in articles)
        resp = self.client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=100,
            messages=[
                {"role": "user", "content": TREND_PROMPT.format(titles=titles)},
            ],
            temperature=0.3,
        )
        return resp.content[0].text.strip()

    def _summarize_batch(self, batch: list[Article]):
        input_data = [
            {"index": i, "title": a.title, "source": a.source, "summary_raw": a.summary_raw[:300]}
            for i, a in enumerate(batch)
        ]
        try:
            resp = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=2000,
                system=SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": json.dumps(input_data, ensure_ascii=False)},
                ],
                temperature=0.2,
            )
            results = json.loads(resp.content[0].text)
            for item in results:
                idx = item.get("index", -1)
                if 0 <= idx < len(batch):
                    batch[idx].summary_ai = item.get("summary_ai", "")
                    batch[idx].category = item.get("category", "기타")
                    batch[idx].importance = item.get("importance", 3)
            print(f"  [OK] AI 요약 완료: {len(results)}건")
        except Exception as e:
            print(f"  [FAIL] AI 요약 실패: {e}")
            for a in batch:
                a.summary_ai = a.summary_raw[:60]
                a.category = "기타"
                a.importance = 3
