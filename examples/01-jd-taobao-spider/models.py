"""统一数据模型：不同站点的商品最终都归一到 Product。"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime


@dataclass
class Product:
    site: str
    sku: str
    title: str
    price: float
    shop: str = ""
    sales: int = 0
    comments: int = 0
    url: str = ""
    image: str = ""
    keyword: str = ""
    captured_at: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )

    @property
    def key(self) -> str:
        """跨站点唯一键，用于去重。"""
        return f"{self.site}:{self.sku}"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CrawlResult:
    site: str
    keyword: str
    fetched: int
    parsed: int
    inserted: int
    skipped: int = 0
    errors: list[str] = field(default_factory=list)
