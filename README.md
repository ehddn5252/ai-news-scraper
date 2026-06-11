# AI News Scraper

AI 관련 뉴스를 자동으로 수집하고, LLM으로 요약/분류하여 데일리 리포트를 생성하는 도구.

## 구조

```
ai-news-scraper/
├── main.py              # 실행 진입점
├── config.py            # RSS 소스, API 키, 설정
├── report_generator.py  # 마크다운 리포트 생성
├── scrapers/
│   ├── base.py          # Article 데이터 클래스
│   ├── rss_scraper.py   # RSS 피드 수집
│   └── html_scraper.py  # HTML 직접 스크래핑 (확장용)
├── summarizer/
│   └── ai_summarizer.py # OpenAI API로 요약/분류/트렌드 추출
├── data/                # 수집 원본 JSON
└── reports/             # 생성된 마크다운 리포트
```

## 실행 방법

```bash
# 1. 가상환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 환경변수 설정
copy .env.example .env
# .env 파일에서 OPENAI_API_KEY 입력

# 4. 실행
python main.py
```

> OpenAI API 키가 없어도 실행 가능 — AI 요약이 스킵되고 원문 앞부분으로 대체됩니다.

## 수집 소스

| 소스 | 수집 방식 |
|------|-----------|
| TechCrunch AI | RSS |
| The Verge AI | RSS |
| MIT Technology Review | RSS |
| Ars Technica | RSS |
| VentureBeat AI | RSS |
| OpenAI Blog | RSS |
| Google AI Blog | RSS |
| Hugging Face Blog | RSS |

## 출력 예시

`reports/report_2026-06-11.md`:

```
# AI 뉴스 데일리 리포트

- 날짜: 2026-06-11
- 수집 기사 수: 47건

## 주요 뉴스 (상위 5건)
1. [Claude 5 발표...](url) — 한줄요약 | 출처 | LLM/생성형 AI | 중요도: *****

## 카테고리별 정리
### LLM/생성형 AI
- [기사 제목](url) — 한줄요약

## 트렌드 키워드
멀티모달, 에이전트, 오픈소스 LLM, AI 규제, 로보틱스
```

## 확장

- **HTML 스크래퍼**: `scrapers/html_scraper.py`에 사이트별 파서 함수를 작성해서 RSS 미지원 사이트 추가
- **알림**: 슬랙 웹훅, 이메일 등으로 리포트 전송
- **스케줄링**: Windows 작업 스케줄러 또는 cron으로 매일 자동 실행
