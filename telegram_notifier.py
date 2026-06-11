"""Telegram 알림 모듈 — ai-news-scraper 전용

설계 원칙:
- **Fail-safe**: 알림 실패가 스크래핑을 막으면 안 된다. 모든 예외는 로깅 후 삼킨다.
- **Non-blocking**: 알림은 별도 스레드로 발송하여 메인 루프를 막지 않는다.
- **No new deps**: 표준 라이브러리(urllib)만 사용.
- **Off by default**: TELEGRAM_NOTIFY_ENABLED=true + BOT_TOKEN + CHAT_ID 모두 설정돼야 발송.

사용법:
    from telegram_notifier import notify, notify_async, get_notifier

    notify("새로운 AI 뉴스 3건 수집 완료")              # 동기 (테스트/스케줄용)
    notify_async("📰 TechCrunch: GPT-5 출시...")      # 비동기 (메인용)
"""

from __future__ import annotations

import html
import json
import os
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional

__all__ = [
    "TelegramNotifier",
    "get_notifier",
    "reset_notifier",
    "notify",
    "notify_async",
]

_API_BASE = "https://api.telegram.org"
_TIMEOUT = 5.0
_MAX_RETRIES = 2


class TelegramNotifier:
    """Telegram Bot API 래퍼 (fail-safe).

    환경 변수:
        TELEGRAM_BOT_TOKEN       — BotFather 발급 토큰
        TELEGRAM_CHAT_ID         — 수신자 chat_id
        TELEGRAM_NOTIFY_ENABLED  — "true"/"1"/"yes"일 때만 활성화
    """

    def __init__(
        self,
        token: Optional[str] = None,
        chat_id: Optional[str] = None,
        enabled: Optional[bool] = None,
    ):
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID", "").strip()
        if enabled is None:
            flag = os.getenv("TELEGRAM_NOTIFY_ENABLED", "false").strip().lower()
            enabled = flag in ("true", "1", "yes", "on")
        self.enabled = enabled and bool(self.token) and bool(self.chat_id)

        if not self.enabled:
            reason = []
            if not (os.getenv("TELEGRAM_NOTIFY_ENABLED", "false").strip().lower()
                    in ("true", "1", "yes", "on")):
                reason.append("disabled by env")
            if not self.token:
                reason.append("no token")
            if not self.chat_id:
                reason.append("no chat_id")
            print(f"[Telegram] 알림 비활성: {', '.join(reason) or 'unknown'}")

    def is_enabled(self) -> bool:
        return self.enabled

    def send(self, text: str, parse_mode: str = "HTML",
             disable_web_page_preview: bool = True) -> bool:
        """동기 발송. 실패 시 False 반환 (예외는 던지지 않음)."""
        if not self.enabled:
            return False
        if not text:
            return False

        url = f"{_API_BASE}/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text[:4000],  # Telegram limit 4096, 여유 둠
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview,
        }
        data = json.dumps(payload).encode("utf-8")

        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                req = urllib.request.Request(
                    url, data=data,
                    headers={"Content-Type": "application/json; charset=utf-8"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
                    body = resp.read().decode("utf-8", errors="replace")
                    payload_resp = json.loads(body)
                    if payload_resp.get("ok"):
                        return True
                    print(
                        f"[Telegram] API ok=false: {payload_resp.get('description', body)[:200]}"
                    )
                    return False
            except urllib.error.HTTPError as e:
                err_body = ""
                try:
                    err_body = e.read().decode("utf-8", errors="replace")[:200]
                except Exception:
                    pass
                print(
                    f"[Telegram] HTTP {e.code} ({attempt}/{_MAX_RETRIES}): {err_body}"
                )
                # 4xx는 재시도해도 의미 없음
                if 400 <= e.code < 500:
                    return False
            except (urllib.error.URLError, TimeoutError) as e:
                print(f"[Telegram] 네트워크 오류 ({attempt}/{_MAX_RETRIES}): {e}")
            except Exception as e:
                print(f"[Telegram] 예외: {e}")
                return False

            if attempt < _MAX_RETRIES:
                time.sleep(0.5 * attempt)

        return False

    def send_async(self, text: str, **kwargs) -> None:
        """비동기 발송 (fire-and-forget). 메인 루프를 블록하지 않는다."""
        if not self.enabled or not text:
            return
        t = threading.Thread(
            target=self.send,
            args=(text,),
            kwargs=kwargs,
            daemon=True,
            name="tg-notify",
        )
        t.start()


# ── 글로벌 싱글톤 ──────────────────────────────────────────────
_default_notifier: Optional[TelegramNotifier] = None
_lock = threading.Lock()


def get_notifier() -> TelegramNotifier:
    """글로벌 노티파이어 인스턴스 (lazy init)."""
    global _default_notifier
    if _default_notifier is None:
        with _lock:
            if _default_notifier is None:
                _default_notifier = TelegramNotifier()
    return _default_notifier


def reset_notifier() -> None:
    """주로 테스트용 — 환경변수 변경 후 재로드."""
    global _default_notifier
    with _lock:
        _default_notifier = None


def notify(text: str, **kwargs) -> bool:
    """동기 발송 단축함수."""
    return get_notifier().send(text, **kwargs)


def notify_async(text: str, **kwargs) -> None:
    """비동기 발송 단축함수 (메인용)."""
    get_notifier().send_async(text, **kwargs)


# ── 메시지 빌더 ────────────────────────────────────────────────
def esc(s) -> str:
    """HTML 이스케이프 (parse_mode=HTML 사용 시)."""
    return html.escape(str(s), quote=False)


def build_scraping_message(
    total_articles: int,
    unique_articles: int,
    summarized_articles: int,
    top_trends: Optional[list[str]] = None,
) -> str:
    """스크래핑 완료 알림 메시지."""
    lines = [
        "📰 <b>AI 뉴스 스크래핑 완료</b>",
        "",
        f"📊 통계:",
        f"  • 수집: {total_articles}건",
        f"  • 중복 제거: {unique_articles}건",
        f"  • 요약: {summarized_articles}건",
    ]

    if top_trends:
        lines.append("")
        lines.append("🔥 주요 트렌드:")
        for trend in top_trends[:5]:
            lines.append(f"  • {esc(trend)}")

    return "\n".join(lines)


def build_article_message(
    title: str,
    summary: str,
    source: str = "",
    category: str = "",
    url: str = "",
) -> str:
    """기사 알림 메시지."""
    lines = []

    # 카테고리별 아이콘
    icons = {
        "llm": "🤖",
        "research": "🔬",
        "business": "💼",
        "general": "📰",
    }
    icon = icons.get(category, "📰")

    lines.append(f"{icon} <b>{esc(title[:80])}</b>")

    if summary:
        lines.append("")
        lines.append(f"📝 {esc(summary[:200])}")

    if source or url:
        lines.append("")
        if source:
            lines.append(f"📌 출처: {esc(source)}")
        if url:
            lines.append(f"🔗 <a href=\"{url}\">Read More</a>")

    return "\n".join(lines)


def build_trend_message(
    trends: list[dict],
    date: str = "",
) -> str:
    """트렌드 요약 메시지."""
    lines = ["🔥 <b>오늘의 AI 트렌드</b>"]

    if date:
        lines.append(f"📅 {date}")

    lines.append("")

    for i, trend in enumerate(trends[:10], 1):
        trend_text = trend if isinstance(trend, str) else trend.get("name", str(trend))
        lines.append(f"{i}. {esc(trend_text[:100])}")

    return "\n".join(lines)


if __name__ == "__main__":
    # 테스트
    msg1 = build_scraping_message(45, 42, 42, ["GPT-5", "AI Agents", "Vision"])
    print(msg1)
    print("\n" + "="*50 + "\n")

    msg2 = build_article_message(
        "새로운 AI 모델이 벤치마크 갱신",
        "최신 연구팀이 개발한 모델이 여러 벤치마크에서 SOTA 달성...",
        "MIT Tech Review",
        "research",
        "https://example.com"
    )
    print(msg2)
