"""可选的 AI 文案服务。

配置了 LLM_API_KEY 时调用大模型；未配置或调用失败时退化为内置模板，
保证离线也能演示。
"""

from __future__ import annotations

import logging

from ..config import get_settings

logger = logging.getLogger(__name__)


def generate_product_pitch(name: str, description: str, price: float) -> str:
    settings = get_settings()
    if settings.llm_api_key:
        try:
            from openai import OpenAI

            client = OpenAI(
                api_key=settings.llm_api_key,
                base_url=settings.llm_base_url,
            )
            response = client.chat.completions.create(
                model=settings.llm_model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "你是电商文案专家。请用中文输出 3 条卖点和 1 段推荐语，"
                            "不要编造不存在的参数。"
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"商品：{name}\n价格：{price}\n描述：{description}",
                    },
                ],
                temperature=0.7,
                timeout=20,
            )
            content = response.choices[0].message.content
            if content:
                return content
        except Exception as exc:  # noqa: BLE001
            logger.warning("调用大模型失败，使用内置文案：%s", exc)

    return _fallback_pitch(name, description, price)


def _fallback_pitch(name: str, description: str, price: float) -> str:
    desc = description.strip() or "暂无详细描述"
    return (
        f"【{name}】\n"
        f"- 价格：¥{price:,.2f}\n"
        f"- 卖点：{desc}\n"
        "- 适合日常使用与送礼，下单后快速发货。\n"
        "- 支持 7 天无理由退换（演示文案）。"
    )
