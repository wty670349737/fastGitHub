"""站点适配器抽象基类。新增站点只需实现 build_search_url / parse。"""

from __future__ import annotations

from abc import ABC, abstractmethod

from models import Product


class BaseAdapter(ABC):
    site: str = ""
    home: str = ""

    @abstractmethod
    def build_search_url(self, keyword: str, page: int = 1) -> str:
        raise NotImplementedError

    @abstractmethod
    def parse(self, html: str, keyword: str) -> list[Product]:
        raise NotImplementedError
