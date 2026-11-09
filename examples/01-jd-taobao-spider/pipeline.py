"""采集流水线：取页面 -> 适配器解析 -> 统一入库。"""

from __future__ import annotations

import logging

from adapters import ADAPTERS
from config import BASE_DIR, Settings
from models import CrawlResult
from net.http_client import HttpClient
from net.robots import robots_allowed
from storage import ProductStore

logger = logging.getLogger(__name__)

FIXTURES = BASE_DIR / "fixtures"


class Crawler:
    def __init__(
        self,
        settings: Settings | None = None,
        client: HttpClient | None = None,
    ) -> None:
        self.settings = settings or Settings()
        self.store = ProductStore(self.settings.db_path)
        self._client = client
        self._owns_client = client is None

    @property
    def client(self) -> HttpClient:
        if self._client is None:
            self._client = HttpClient(
                timeout=self.settings.timeout,
                max_retries=self.settings.max_retries,
                delay_min=self.settings.delay_min,
                delay_max=self.settings.delay_max,
                user_agent=self.settings.user_agent,
                proxy=self.settings.proxy,
            )
        return self._client

    def crawl(
        self,
        site: str,
        keyword: str,
        pages: int = 1,
        offline: bool = False,
    ) -> CrawlResult:
        if site not in ADAPTERS:
            raise ValueError(f"不支持的站点：{site}（可选：{', '.join(ADAPTERS)}）")

        adapter = ADAPTERS[site]()
        result = CrawlResult(site=site, keyword=keyword, fetched=0, parsed=0, inserted=0)
        collected = []

        for page in range(1, pages + 1):
            url = adapter.build_search_url(keyword, page)
            try:
                if offline:
                    html = self._load_fixture(site)
                else:
                    if self.settings.respect_robots and not robots_allowed(
                        url, self.settings.user_agent, self.client
                    ):
                        result.skipped += 1
                        result.errors.append(f"robots.txt 禁止抓取：{url}")
                        logger.warning("robots.txt 禁止抓取：%s", url)
                        continue
                    html = self.client.get(url).text
            except Exception as exc:  # noqa: BLE001 - 单页失败不影响整体
                result.errors.append(f"抓取失败：{url}：{exc}")
                logger.exception("抓取失败：%s", url)
                continue

            result.fetched += 1
            products = adapter.parse(html, keyword)
            result.parsed += len(products)
            collected.extend(products)

        result.inserted = self.store.save_many(collected)
        return result

    @staticmethod
    def _load_fixture(site: str) -> str:
        path = FIXTURES / f"{site}_search.html"
        if not path.exists():
            raise FileNotFoundError(f"离线样例不存在：{path}")
        return path.read_text(encoding="utf-8")

    def close(self) -> None:
        if self._client is not None and self._owns_client:
            self._client.close()
        self.store.close()

    def __enter__(self) -> "Crawler":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
