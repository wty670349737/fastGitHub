"""文本清洗与数字解析工具。"""

from __future__ import annotations

import re

_PRICE_RE = re.compile(r"\d+(?:\.\d+)?")
_INT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(万)?")


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value.replace("\xa0", " ")).strip()


def parse_price(value: str | None) -> float:
    """从 '￥3,999.00'、'3999元' 中提取浮点价格。"""
    if not value:
        return 0.0
    match = _PRICE_RE.search(value.replace(",", ""))
    return float(match.group()) if match else 0.0


def parse_int(value: str | None) -> int:
    """把 '1.2万+'、'3000+条评论' 这类文本转成整数。"""
    if not value:
        return 0
    text = value.replace(",", "").strip()
    match = _INT_RE.search(text)
    if not match:
        return 0
    number = float(match.group(1))
    if match.group(2):
        number *= 10000
    return int(number)
