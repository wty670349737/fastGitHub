"""Jinja2 模板渲染辅助：统一注入 request / csrf / 当前用户。"""

from __future__ import annotations

from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates

from .config import get_settings

BASE_DIR = Path(__file__).resolve().parent

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
templates.env.globals["shop_name"] = get_settings().shop_name
templates.env.globals["format_price"] = lambda value: f"¥{value:,.2f}"


def render(request: Request, name: str, **context):
    context.setdefault("request", request)
    context.setdefault("csrf_token", getattr(request.state, "csrf_token", ""))
    context.setdefault("current_user", getattr(request.state, "user", None))
    context.setdefault("flash", request.query_params.get("msg", ""))
    try:
        # Starlette >= 0.29 推荐签名
        return templates.TemplateResponse(request=request, name=name, context=context)
    except TypeError:  # 旧版本兜底
        return templates.TemplateResponse(name, context)
