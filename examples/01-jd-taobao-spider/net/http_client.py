"""带重试、限速、超时的简易 HTTP 客户端。"""

from __future__ import annotations

import logging
import random
import time

import httpx

logger = logging.getLogger(__name__)

RETRY_STATUS = {408, 425, 429, 500, 502, 503, 504}


class HttpClient:
    def __init__(
        self,
        *,
        timeout: float = 15.0,
        max_retries: int = 3,
        delay_min: float = 1.0,
        delay_max: float = 3.0,
        user_agent: str = "Mozilla/5.0",
        proxy: str | None = None,
    ) -> None:
        self.max_retries = max(1, max_retries)
        self.delay_min = max(0.0, delay_min)
        self.delay_max = max(self.delay_min, delay_max)
        headers = {
            "User-Agent": user_agent,
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
        }
        kwargs: dict = {
            "timeout": timeout,
            "follow_redirects": True,
            "headers": headers,
        }
        if proxy:
            try:
                self._client = httpx.Client(proxy=proxy, **kwargs)
            except TypeError:  # httpx < 0.26 用 proxies
                self._client = httpx.Client(proxies=proxy, **kwargs)
        else:
            self._client = httpx.Client(**kwargs)

    def _sleep(self) -> None:
        if self.delay_max <= 0:
            return
        time.sleep(random.uniform(self.delay_min, self.delay_max))

    def get(self, url: str, **kwargs) -> httpx.Response:
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                self._sleep()
                response = self._client.get(url, **kwargs)
                if response.status_code in RETRY_STATUS:
                    raise httpx.HTTPStatusError(
                        f"HTTP {response.status_code}",
                        request=response.request,
                        response=response,
                    )
                response.raise_for_status()
                return response
            except httpx.HTTPError as exc:
                last_error = exc
                backoff = min(2 ** attempt, 30)
                logger.warning(
                    "请求失败（第 %d/%d 次）：%s，%ss 后重试",
                    attempt,
                    self.max_retries,
                    url,
                    backoff,
                )
                if attempt < self.max_retries:
                    time.sleep(backoff)
        assert last_error is not None
        raise last_error

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
