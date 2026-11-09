"""项目级配置：全部从环境变量读取，方便在本地 / Docker / CI 中切换。"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def _float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


def _bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    db_path: Path = field(
        default_factory=lambda: Path(os.getenv("SPIDER_DB", BASE_DIR / "data" / "products.db"))
    )
    timeout: float = field(default_factory=lambda: _float("SPIDER_TIMEOUT", 15.0))
    max_retries: int = field(default_factory=lambda: _int("SPIDER_MAX_RETRIES", 3))
    delay_min: float = field(default_factory=lambda: _float("SPIDER_DELAY_MIN", 1.0))
    delay_max: float = field(default_factory=lambda: _float("SPIDER_DELAY_MAX", 3.0))
    user_agent: str = field(default_factory=lambda: os.getenv("SPIDER_UA", DEFAULT_UA))
    proxy: str | None = field(default_factory=lambda: os.getenv("SPIDER_PROXY") or None)
    respect_robots: bool = field(default_factory=lambda: _bool("SPIDER_RESPECT_ROBOTS", True))
    offline: bool = field(default_factory=lambda: _bool("SPIDER_OFFLINE", False))
