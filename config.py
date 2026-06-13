import os
from dotenv import load_dotenv

load_dotenv()

# ─── Claude (Anthropic) 설정 ────────────────────────
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")
CLAUDE_MODEL = "claude-3-5-sonnet-20241022"

# ─── Telegram 설정 ────────────────────────────────
TELEGRAM_NOTIFY_ENABLED = os.getenv("TELEGRAM_NOTIFY_ENABLED", "false").lower() in ("true", "1", "yes")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ─── Instagram 설정 ────────────────────────────────
INSTAGRAM_ENABLED = os.getenv("INSTAGRAM_ENABLED", "false").lower() in ("true", "1", "yes")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")
INSTAGRAM_HASHTAGS = os.getenv("INSTAGRAM_HASHTAGS", "#AI #News #TechNews")
INSTAGRAM_POST_ENABLED = INSTAGRAM_ENABLED and bool(INSTAGRAM_ACCESS_TOKEN) and bool(INSTAGRAM_BUSINESS_ACCOUNT_ID)

# ─── 일반 설정 ─────────────────────────────────────
REQUEST_DELAY = 2
REQUEST_TIMEOUT = 15
DATA_DIR = os.getenv("DATA_DIR", "data")

RSS_SOURCES = [
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "category_hint": "general",
    },
    {
        "name": "The Verge AI",
        "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        "category_hint": "general",
    },
    {
        "name": "MIT Technology Review AI",
        "url": "https://www.technologyreview.com/feed/",
        "category_hint": "research",
    },
    {
        "name": "Ars Technica AI",
        "url": "https://feeds.arstechnica.com/arstechnica/features",
        "category_hint": "general",
    },
    {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/category/ai/feed/",
        "category_hint": "business",
    },
    {
        "name": "OpenAI Blog",
        "url": "https://openai.com/blog/rss.xml",
        "category_hint": "llm",
    },
    {
        "name": "Google AI Blog",
        "url": "https://blog.google/technology/ai/rss/",
        "category_hint": "llm",
    },
    {
        "name": "Hugging Face Blog",
        "url": "https://huggingface.co/blog/feed.xml",
        "category_hint": "llm",
    },
]

CATEGORIES = [
    "LLM/생성형 AI",
    "컴퓨터비전",
    "로보틱스/자율주행",
    "정책/규제",
    "비즈니스/산업",
    "연구/논문",
    "기타",
]

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
