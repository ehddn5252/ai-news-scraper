# Instagram Integration Guide

이 가이드는 ai-news-scraper에서 수집한 뉴스를 Instagram 비즈니스 계정으로 자동 포스팅하는 방법을 설명합니다.

## 📋 사전 요구사항

1. **Instagram 비즈니스 계정** (Personal 계정은 API 지원 안 함)
2. **Meta for Developers 앱** (Instagram Graph API 접근권)
3. **Long-lived Access Token** (최대 60일 유효)
4. **Business Account ID**

## 🔧 설정 단계

### 1단계: Instagram 계정을 비즈니스 계정으로 변경

```
Instagram 앱 → 설정 → 계정 → 계정 유형 및 연락처 → 비즈니스 계정으로 변경
```

### 2단계: Meta for Developers에서 앱 생성

1. https://developers.facebook.com 접속
2. 내 앱 → 앱 만들기
3. 앱 유형: **Business** 선택
4. 기본 정보 입력 후 앱 생성

### 3단계: Instagram Graph API 설정

1. 앱 대시보드에서 **제품 추가** 클릭
2. **Instagram Graph API** 검색 및 추가
3. 설정 → 기본 정보에서 **앱 ID**와 **앱 시크릿** 확인

### 4단계: 액세스 토큰 발급

```bash
# Graph API Explorer 사용
# https://developers.facebook.com/tools/explorer

# 1. Graph API Explorer 접속
# 2. 앱 선택 (우측 상단)
# 3. 액세스 토큰 생성 → Instagram Business → 권한 설정
#    필요한 권한:
#    - instagram_basic
#    - instagram_content_publish
#    - pages_read_engagement

# 4. 생성된 토큰 복사
```

또는 터미널에서:

```bash
# 임시 토큰 생성
curl -i -X GET "https://graph.instagram.com/v18.0/me/accounts?access_token=USER_ACCESS_TOKEN"

# 장기 토큰으로 변환 (60일)
curl -i -X POST "https://graph.instagram.com/v18.0/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&access_token=SHORT_LIVED_TOKEN"
```

### 5단계: Business Account ID 확인

```bash
curl -X GET "https://graph.instagram.com/v18.0/me/accounts?access_token=LONG_LIVED_TOKEN"
```

응답에서 `id` 필드 확인 (예: `123456789`)

### 6단계: 환경 변수 설정

`.env` 파일 생성:

```bash
OPENAI_API_KEY=sk-your-api-key-here

# Instagram 포스팅 활성화
INSTAGRAM_ENABLED=true
INSTAGRAM_ACCESS_TOKEN=your_long_lived_access_token_here
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_business_account_id_here
INSTAGRAM_HASHTAGS=#AI #News #TechNews #ArtificialIntelligence
```

## 🚀 사용법

### 자동 포스팅

스크립트 실행 시 자동으로 상위 3개 기사가 Instagram에 포스팅됩니다:

```bash
python main.py
```

### 수동 포스팅

```python
from instagram_poster import post_news, post_news_async, build_news_caption

# 동기 포스팅 (대기)
success = post_news(
    caption="새로운 AI 뉴스\n\n요약 텍스트...",
    image_url="https://example.com/image.jpg"
)

# 비동기 포스팅 (fire-and-forget)
post_news_async(
    caption="새로운 기사...",
    image_url="https://example.com/image.jpg"
)

# 캡션 빌더 사용
caption = build_news_caption(
    title="AI가 의료를 혁신하다",
    summary="새로운 모델이 의료 진단을 개선했습니다.",
    category="research",
    source="MIT Tech Review",
    url="https://example.com"
)
post_news_async(caption, "https://example.com/image.jpg")
```

## 📝 포스팅 형식

기사 포스팅 시 다음과 같은 형식으로 전송됩니다:

```
📰 NEWS
<b>기사 제목</b>

기사 요약 (최대 500자)...

📌 출처: TechCrunch
🔗 https://example.com/article

#AI #News #TechNews
```

## ⚙️ API 제한사항

- **포스트당 최대 크기**: 2,200자
- **이미지 형식**: JPG, PNG, GIF, BMP, WEBP
- **최대 이미지 크기**: 8MB
- **요청 제한**: 일반적으로 200건/시간

## 🐛 문제 해결

### 토큰 만료
```
오류: "Invalid OAuth Token"
해결: 새로운 Long-lived Token 발급 후 .env 업데이트
```

### 비즈니스 계정 아님
```
오류: "Invalid Business Account"
해결: Instagram 설정에서 비즈니스 계정으로 변경
```

### 이미지 없음
```
오류: "Image URL not found"
해결: 기사에 이미지가 있는지 확인 (image_url 필드)
```

## 🔐 보안 주의사항

⚠️ **절대 하지 말 것**:
- `.env` 파일을 Git에 커밋
- 토큰을 소스 코드에 하드코딩
- 토큰을 공개 저장소에 공개

✅ **추천**:
- `.env.example`만 버전 관리
- `.env` 파일을 `.gitignore`에 추가 (이미 설정됨)
- 정기적으로 토큰 갱신

## 📚 참고

- [Instagram Graph API 문서](https://developers.facebook.com/docs/instagram-api)
- [Graph API Reference](https://developers.facebook.com/docs/graph-api/reference/ig-user)
- [Posting Media Guide](https://developers.facebook.com/docs/instagram-api/guides/content-publishing)
