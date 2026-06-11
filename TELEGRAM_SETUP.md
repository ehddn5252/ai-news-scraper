# Telegram Integration Guide

이 가이드는 ai-news-scraper에서 수집한 뉴스 스크래핑 결과를 Telegram으로 실시간 알림받는 방법을 설명합니다.

## 📋 사전 요구사항

1. **Telegram 계정** (개인 또는 채팅방)
2. **Telegram Bot** (BotFather가 생성)
3. **Bot Token** (BotFather 발급)
4. **Chat ID** (메시지를 받을 채팅 또는 사용자 ID)

## 🔧 설정 단계

### 1단계: Bot 생성 (BotFather 사용)

1. Telegram에서 **@BotFather** 검색
2. `/start` 또는 아무 메시지 전송
3. `/newbot` 명령 입력
4. 봇 이름과 사용자명(username) 입력
   ```
   이름: AI News Scraper
   사용자명: ai_news_bot
   ```
5. BotFather가 **Bot Token** 제공 (예: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

### 2단계: Chat ID 확인

#### 방법 1: 직접 확인 (권장)

```bash
# Bot Token 설정
BOT_TOKEN=your_bot_token_here
8786491898:AAGuV3Y_2J_GCzWPmwQA-wJjEo3tR_85ZJY
# 브라우저에서 다음 URL 방문
# https://api.telegram.org/bot8786491898:AAGuV3Y_2J_GCzWPmwQA-wJjEo3tR_85ZJY/getUpdates

# 처음에는 아무것도 없을 것입니다.
# 봇에 임의의 메시지 전송 후 다시 접속하면 chat_id가 보입니다.
```

응답 예시:
```json
{
  "ok": true,
  "result": [
    {
      "update_id": 123456789,
      "message": {
        "message_id": 1,
        "from": {
          "id": 987654321,
          "first_name": "User"
        },
        "chat": {
          "id": 987654321
        },
        "date": 1234567890
      }
    }
  ]
}
```

여기서 `chat.id`가 바로 **Chat ID** (예: `987654321`)

#### 방법 2: Python 스크립트로 확인

```python
import urllib.request
import json

BOT_TOKEN = "your_bot_token_here"
url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

with urllib.request.urlopen(url) as response:
    data = json.loads(response.read().decode())
    for update in data.get("result", []):
        chat_id = update.get("message", {}).get("chat", {}).get("id")
        if chat_id:
            print(f"Chat ID: {chat_id}")
```

### 3단계: 환경 변수 설정

`.env` 파일 생성:

```bash
OPENAI_API_KEY=sk-your-api-key-here

# Telegram 알림 활성화
TELEGRAM_NOTIFY_ENABLED=true
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID=987654321
```

### 4단계: 테스트

```bash
# 간단한 테스트
python -c "
from telegram_notifier import notify
result = notify('📰 Telegram 연동 테스트 완료!')
print(f'발송 성공' if result else '발송 실패')
"
```

또는 Python에서:

```python
from telegram_notifier import notify, notify_async, build_scraping_message

# 동기 발송 (대기)
notify("🔥 새로운 AI 뉴스 5건 수집됨!")

# 비동기 발송 (fire-and-forget)
notify_async("📰 스크래핑이 완료되었습니다.")

# 메시지 빌더 사용
msg = build_scraping_message(
    total_articles=50,
    unique_articles=48,
    summarized_articles=48,
    top_trends=["GPT-5", "AI Agents", "Vision"]
)
notify(msg)
```

## 🚀 사용법

### 자동 알림

스크립트 실행 시 자동으로 Telegram 알림이 전송됩니다:

```bash
python main.py
```

알림 종류:
1. **시작 알림**: 스크래핑 시작
2. **완료 알림**: 수집 통계 (총 건수, 중복 제거, 요약 완료)
3. **트렌드 알림**: 주요 트렌드 TOP 10

### 수동 알림

```python
from telegram_notifier import notify, notify_async, build_article_message

# 단순 텍스트 알림
notify("⚠️ 에러 발생: API 연결 실패")

# 기사 알림
msg = build_article_message(
    title="AI가 의료를 혁신하다",
    summary="새로운 모델이 의료 진단을 개선했습니다.",
    category="research",
    source="MIT Tech Review",
    url="https://example.com"
)
notify(msg)

# 비동기 알림 (메인 루프 영향 없음)
notify_async("📰 백그라운드에서 알림을 발송합니다...")
```

## 📝 메시지 형식

### 스크래핑 완료 알림

```
📰 AI 뉴스 스크래핑 완료

📊 통계:
  • 수집: 50건
  • 중복 제거: 48건
  • 요약: 48건

🔥 주요 트렌드:
  • GPT-5 출시
  • AI Agents 활성화
  • Vision 기술 발전
  • 규제 강화
  • 오픈소스 AI
```

### 트렌드 알림

```
🔥 오늘의 AI 트렌드
📅 2026-06-12

1. GPT-5 출시 예정
2. AI Agents 시장 확대
3. Vision 기술 발전
...
```

### 기사 알림

```
🤖 새로운 AI 모델이 벤치마크 갱신

📝 최신 연구팀이 개발한 모델이 여러 벤치마크에서 SOTA 달성...

📌 출처: MIT Tech Review
🔗 Read More
```

## ⚙️ 기능

| 기능 | 설명 | 기본값 |
|------|------|--------|
| 동기 발송 | `notify()` - 응답 대기 | - |
| 비동기 발송 | `notify_async()` - fire-and-forget | - |
| 재시도 | 네트워크 오류 시 자동 재시도 | 2회 |
| 타임아웃 | API 응답 대기 시간 | 5초 |
| 메시지 길이 | 최대 메시지 크기 | 4,000자 |
| 파싱 모드 | HTML 태그 지원 | HTML |

## 🐛 문제 해결

### "Invalid Token"
```
오류: TelegramError: Invalid bot token
해결: 토큰을 올바르게 복사했는지 확인하세요.
     BotFather에서 새 토큰을 생성할 수도 있습니다.
```

### "Chat not found"
```
오류: Bad Request: chat not found
해결: Chat ID를 올바르게 입력했는지 확인하세요.
     getUpdates로 다시 확인하세요.
```

### "Telegram 알림 비활성"
```
상황: [Telegram] 알림 비활성: disabled by env
해결: .env에서 TELEGRAM_NOTIFY_ENABLED=true로 설정하세요.
```

### 알림을 받지 못함
1. Bot Token과 Chat ID가 올바른지 확인
2. `.env` 파일이 프로젝트 루트에 있는지 확인
3. `TELEGRAM_NOTIFY_ENABLED=true` 설정 확인
4. Bot에 메시지 권한이 있는지 확인 (채팅방의 경우 Bot 추가 필요)

## 🔐 보안 주의사항

⚠️ **절대 하지 말 것**:
- `.env` 파일을 Git에 커밋
- Bot Token을 소스 코드에 하드코딩
- Token을 공개 저장소에 공개
- Chat ID를 무분별하게 공유

✅ **추천**:
- `.env.example`만 버전 관리
- `.env` 파일을 `.gitignore`에 추가 (이미 설정됨)
- 정기적으로 Token 갱신 (BotFather에서 `/revoketoken` 후 재생성)

## 📚 참고

- [Telegram Bot API 문서](https://core.telegram.org/bots/api)
- [BotFather 가이드](https://core.telegram.org/bots)
- [Message Types](https://core.telegram.org/bots/api#message)
- [Chat ID 찾기](https://core.telegram.org/bots/faq#how-do-i-get-my-group-chat-id)

## 💡 팁

### 그룹 채팅으로 알림 받기

1. Telegram에서 그룹 생성
2. Bot을 그룹에 추가
3. 그룹에 메시지 전송
4. `getUpdates`로 Chat ID 확인 (음수로 표시됨, 예: `-123456789`)
5. Chat ID를 `.env`에 입력

### 채널로 알림 받기

1. Telegram에서 채널 생성 (공개 또는 비공개)
2. Bot을 채널의 관리자로 추가
3. 채널에 메시지 전송
4. `getUpdates`로 Chat ID 확인 (음수, 예: `-100123456789`)
5. Chat ID를 `.env`에 입력

### 여러 위치로 알림 받기

```python
# 수동으로 여러 Chat ID에 발송
from telegram_notifier import TelegramNotifier

notifier = TelegramNotifier(
    token="YOUR_TOKEN",
    chat_id="CHAT_ID_1"
)
notifier.send("알림 1")

# Chat ID를 바꾸면 다른 채팅으로도 가능
notifier.chat_id = "CHAT_ID_2"
notifier.send("알림 2")
```
