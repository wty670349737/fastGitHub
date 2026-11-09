"""应用配置：全部从环境变量 / .env 读取。"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
BASE_DIR = APP_DIR.parent
DATA_DIR = BASE_DIR / "data"

try:
    from dotenv import load_dotenv

    load_dotenv(BASE_DIR / ".env")
except ImportError:  # python-dotenv 未安装时忽略
    pass


@dataclass(frozen=True)
class Settings:
    secret_key: str
    database_url: str
    shop_name: str
    admin_email: str
    admin_password: str
    llm_api_key: str | None
    llm_base_url: str
    llm_model: str


def get_settings() -> Settings:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return Settings(
        secret_key=os.getenv("SECRET_KEY", "dev-only-change-me-please-32-chars"),
        database_url=os.getenv(
            "DATABASE_URL", f"sqlite:///{(DATA_DIR / 'shop.db').as_posix()}"
        ),
        shop_name=os.getenv("SHOP_NAME", "PyShop 商城"),
        admin_email=os.getenv("ADMIN_EMAIL", "admin@example.com").strip().lower(),
        admin_password=os.getenv("ADMIN_PASSWORD", "admin123"),
        llm_api_key=os.getenv("LLM_API_KEY") or None,
        llm_base_url=os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1"),
        llm_model=os.getenv("LLM_MODEL", "deepseek-chat"),
    )
