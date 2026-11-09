"""robots.txt 合规检查。"""

from __future__ import annotations

import logging
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx

logger = logging.getLogger(__name__)


def robots_allowed(
    url: str,
    user_agent: str,
    client: "httpx.Client | None" = None,
) -> bool:
    """返回 True 表示 robots.txt 允许抓取；读取失败时保守地按允许处理。"""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return True

    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    parser = RobotFileParser()
    parser.set_url(robots_url)
    try:
        if client is not None:
            response = client.get(robots_url)
            if response.status_code >= 400:
                return True
            parser.parse(response.text.splitlines())
        else:
            parser.read()
    except (OSError, httpx.HTTPError) as exc:
        logger.warning("读取 robots.txt 失败，按允许处理：%s（%s）", robots_url, exc)
        return True
    return parser.can_fetch(user_agent, url)
