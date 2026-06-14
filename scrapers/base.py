from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Article:
    title: str
    url: str
    date: str
    source: str
    summary_raw: str
    category: str = ""
    importance: int = 0
    summary_ai: str = ""
    content: str = ""
    detail_summary: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "Article":
        return Article(**{k: v for k, v in data.items() if k in Article.__dataclass_fields__})
