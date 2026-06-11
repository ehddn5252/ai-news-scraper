"""Instagram 포스팅 모듈 — ai-news-scraper 전용

설계 원칙:
- **Fail-safe**: 포스팅 실패가 스크래핑을 막으면 안 된다. 모든 예외는 로깅 후 삼킨다.
- **Non-blocking**: 포스팅은 별도 스레드로 발송하여 메인 루프를 막지 않는다.
- **No heavy deps**: requests 사용 (이미 설치됨).
- **Off by default**: INSTAGRAM_ENABLED=true + ACCESS_TOKEN + BUSINESS_ACCOUNT_ID 모두 설정돼야 발송.

사용법:
    from instagram_poster import post_news, post_news_async, get_poster

    post_news("🔥 새로운 AI 뉴스\n[제목]\n링크", hashtags="#AI #뉴스")  # 동기
    post_news_async("새 기사 요약...", caption="트렌드")  # 비동기 (권장)
"""

from __future__ import annotations

import json
import os
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional
from datetime import datetime

__all__ = [
    "InstagramPoster",
    "get_poster",
    "reset_poster",
    "post_news",
    "post_news_async",
]

_API_BASE = "https://graph.instagram.com"
_TIMEOUT = 10.0
_MAX_RETRIES = 2


class InstagramPoster:
    """Instagram Graph API 래퍼 (fail-safe).

    환경 변수:
        INSTAGRAM_ENABLED           — "true"일 때만 활성화
        INSTAGRAM_ACCESS_TOKEN      — Instagram Graph API 액세스 토큰
        INSTAGRAM_BUSINESS_ACCOUNT_ID — 비즈니스 계정 ID
        INSTAGRAM_HASHTAGS          — 기본 해시태그 (선택사항)
    """

    def __init__(
        self,
        access_token: Optional[str] = None,
        business_account_id: Optional[str] = None,
        enabled: Optional[bool] = None,
    ):
        self.access_token = access_token or os.getenv("INSTAGRAM_ACCESS_TOKEN", "").strip()
        self.business_account_id = business_account_id or os.getenv(
            "INSTAGRAM_BUSINESS_ACCOUNT_ID", ""
        ).strip()
        self.default_hashtags = os.getenv("INSTAGRAM_HASHTAGS", "#AI #News").strip()

        if enabled is None:
            flag = os.getenv("INSTAGRAM_ENABLED", "false").strip().lower()
            enabled = flag in ("true", "1", "yes", "on")

        self.enabled = enabled and bool(self.access_token) and bool(self.business_account_id)

        if not self.enabled:
            reason = []
            if not (os.getenv("INSTAGRAM_ENABLED", "false").strip().lower()
                    in ("true", "1", "yes", "on")):
                reason.append("disabled by env")
            if not self.access_token:
                reason.append("no access_token")
            if not self.business_account_id:
                reason.append("no business_account_id")
            print(f"[Instagram] 포스팅 비활성: {', '.join(reason) or 'unknown'}")

    def is_enabled(self) -> bool:
        return self.enabled

    def _post_carousel(
        self,
        caption: str,
        image_urls: list[str],
    ) -> bool:
        """캐러셀(여러 이미지) 포스팅."""
        if not image_urls:
            return False

        # Step 1: 각 이미지를 미디어 객체로 등록
        media_ids = []
        for idx, img_url in enumerate(image_urls[:10]):  # Instagram limit: 10 images
            try:
                payload = {
                    "image_url": img_url,
                    "access_token": self.access_token,
                }
                data = urllib.parse.urlencode(payload).encode("utf-8")
                url = f"{_API_BASE}/v18.0/{self.business_account_id}/media"

                req = urllib.request.Request(url, data=data, method="POST")
                with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
                    result = json.loads(resp.read().decode("utf-8"))
                    if result.get("id"):
                        media_ids.append(result["id"])
                    else:
                        print(f"[Instagram] 이미지 {idx + 1} 등록 실패: {result}")
            except Exception as e:
                print(f"[Instagram] 이미지 {idx + 1} 업로드 오류: {e}")

        if not media_ids:
            return False

        # Step 2: 캐러셀 생성
        try:
            carousel_items = [{"id": media_id} for media_id in media_ids]
            payload = {
                "media_type": "CAROUSEL",
                "children": json.dumps(carousel_items),
                "caption": caption[:2200],  # Instagram limit
                "access_token": self.access_token,
            }
            data = urllib.parse.urlencode(payload).encode("utf-8")
            url = f"{_API_BASE}/v18.0/{self.business_account_id}/media"

            req = urllib.request.Request(url, data=data, method="POST")
            with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                carousel_id = result.get("id")
                if not carousel_id:
                    print(f"[Instagram] 캐러셀 생성 실패: {result}")
                    return False

                # Step 3: 공개
                return self._publish_media(carousel_id)
        except Exception as e:
            print(f"[Instagram] 캐러셀 포스팅 오류: {e}")
            return False

    def _publish_media(self, media_id: str) -> bool:
        """미디어 공개."""
        try:
            payload = {
                "creation_id": media_id,
                "access_token": self.access_token,
            }
            data = urllib.parse.urlencode(payload).encode("utf-8")
            url = f"{_API_BASE}/v18.0/{self.business_account_id}/media_publish"

            req = urllib.request.Request(url, data=data, method="POST")
            with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                if result.get("success"):
                    return True
                print(f"[Instagram] 미디어 공개 실패: {result}")
                return False
        except urllib.error.HTTPError as e:
            err_body = ""
            try:
                err_body = e.read().decode("utf-8", errors="replace")[:200]
            except Exception:
                pass
            print(f"[Instagram] HTTP {e.code}: {err_body}")
            return False
        except Exception as e:
            print(f"[Instagram] 미디어 공개 오류: {e}")
            return False

    def post_text(
        self,
        caption: str,
    ) -> bool:
        """텍스트 포스팅 (텍스트만 지원하는 비즈니스 계정용).
        
        Note: Instagram 비즈니스 계정은 API를 통한 순수 텍스트 포스팅을 지원하지 않습니다.
        적어도 하나의 이미지가 필요합니다.
        """
        print("[Instagram] 주의: 비즈니스 계정은 텍스트만 포스팅할 수 없습니다. 이미지가 필요합니다.")
        return False

    def post_image(
        self,
        image_url: str,
        caption: str = "",
    ) -> bool:
        """단일 이미지 포스팅."""
        if not self.enabled:
            return False
        if not image_url or not caption:
            return False

        try:
            payload = {
                "image_url": image_url,
                "caption": caption[:2200],  # Instagram limit
                "access_token": self.access_token,
            }
            data = urllib.parse.urlencode(payload).encode("utf-8")
            url = f"{_API_BASE}/v18.0/{self.business_account_id}/media"

            req = urllib.request.Request(url, data=data, method="POST")
            with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                media_id = result.get("id")
                if not media_id:
                    print(f"[Instagram] 이미지 등록 실패: {result}")
                    return False

                return self._publish_media(media_id)

        except urllib.error.HTTPError as e:
            err_body = ""
            try:
                err_body = e.read().decode("utf-8", errors="replace")[:200]
            except Exception:
                pass
            print(f"[Instagram] HTTP {e.code}: {err_body}")
            return False
        except Exception as e:
            print(f"[Instagram] 이미지 포스팅 오류: {e}")
            return False

    def post_carousel(
        self,
        image_urls: list[str],
        caption: str = "",
    ) -> bool:
        """캐러셀(여러 이미지) 포스팅."""
        if not self.enabled:
            return False
        if not image_urls or not caption:
            return False

        return self._post_carousel(caption, image_urls)

    def post_async(self, image_url: str, caption: str = "", use_carousel: bool = False) -> None:
        """비동기 포스팅 (fire-and-forget)."""
        if not self.enabled or not caption:
            return

        def _post():
            try:
                if use_carousel and isinstance(image_url, list):
                    self.post_carousel(image_url, caption)
                else:
                    self.post_image(image_url, caption)
            except Exception as e:
                print(f"[Instagram] 비동기 포스팅 오류: {e}")

        t = threading.Thread(
            target=_post,
            daemon=True,
            name="ig-post",
        )
        t.start()


# ── 글로벌 싱글톤 ──────────────────────────────────────────────
_default_poster: Optional[InstagramPoster] = None
_lock = threading.Lock()


def get_poster() -> InstagramPoster:
    """글로벌 포스터 인스턴스 (lazy init)."""
    global _default_poster
    if _default_poster is None:
        with _lock:
            if _default_poster is None:
                _default_poster = InstagramPoster()
    return _default_poster


def reset_poster() -> None:
    """테스트용 — 환경변수 변경 후 재로드."""
    global _default_poster
    with _lock:
        _default_poster = None


def post_news(
    caption: str,
    image_url: str = "",
    hashtags: str = "",
) -> bool:
    """동기 포스팅 단축함수."""
    poster = get_poster()
    if hashtags:
        caption = f"{caption}\n\n{hashtags}"
    else:
        caption = f"{caption}\n\n{poster.default_hashtags}"

    if not image_url:
        print("[Instagram] 이미지 URL이 필요합니다.")
        return False

    return poster.post_image(image_url, caption)


def post_news_async(
    caption: str,
    image_url: str = "",
    hashtags: str = "",
) -> None:
    """비동기 포스팅 단축함수 (권장)."""
    poster = get_poster()
    if hashtags:
        caption = f"{caption}\n\n{hashtags}"
    else:
        caption = f"{caption}\n\n{poster.default_hashtags}"

    poster.post_async(image_url, caption)


# ── 메시지 빌더 ────────────────────────────────────────────────
def build_news_caption(
    title: str,
    summary: str,
    category: str = "",
    source: str = "",
    url: str = "",
) -> str:
    """뉴스 포스팅용 캡션 빌더."""
    lines = []

    # 헤더
    icon = "📰" if category != "research" else "🔬"
    lines.append(f"{icon} {category.upper() if category else 'NEWS'}")
    lines.append("")

    # 제목
    lines.append(f"<b>{title}</b>" if len(title) < 50 else title)
    lines.append("")

    # 요약
    if summary:
        lines.append(summary[:500])
    if len(summary) > 500:
        lines.append("...")
    lines.append("")

    # 출처
    if source:
        lines.append(f"📌 출처: {source}")
    if url:
        lines.append(f"🔗 {url}")

    return "\n".join(lines)


if __name__ == "__main__":
    # 테스트
    caption = build_news_caption(
        "AI 성능 혁신",
        "새로운 모델이 벤치마크를 갱신했습니다.",
        "research",
        "MIT Tech Review",
        "https://example.com",
    )
    print(caption)
