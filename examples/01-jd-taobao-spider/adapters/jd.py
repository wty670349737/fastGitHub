"""京东搜索页适配器。

京东搜索结果长期为服务端渲染的 <li class="gl-item" data-sku="..."> 列表，
核心字段：标题 .p-name em、价格 .p-price i、评价 .p-commit、店铺 .p-shop。
站点改版时只需要修改这里的 CSS 选择器。
"""

from __future__ import annotations

from urllib.parse import quote

from bs4 import BeautifulSoup
from bs4.element import Tag

from adapters.base import BaseAdapter
from models import Product
from utils.text import clean_text, parse_int, parse_price


class JdAdapter(BaseAdapter):
    site = "jd"
    home = "https://www.jd.com/"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        # 京东搜索页页码按奇数递增：1、3、5……
        jd_page = 2 * page - 1
        return (
            "https://search.jd.com/Search?"
            f"keyword={quote(keyword)}&page={jd_page}&enc=utf-8"
        )

    def parse(self, html: str, keyword: str) -> list[Product]:
        soup = BeautifulSoup(html, "html.parser")
        products: list[Product] = []
        for item in soup.select("li.gl-item"):
            product = self._parse_item(item, keyword)
            if product is not None:
                products.append(product)
        return products

    def _parse_item(self, item: Tag, keyword: str) -> Product | None:
        sku = clean_text(item.get("data-sku"))
        link = item.select_one(".p-name a[href]")
        href = link.get("href", "") if link else ""
        if not sku:
            sku = self._sku_from_href(href)
        if not sku:
            return None

        title_el = item.select_one(".p-name em") or item.select_one(".p-name")
        price_el = item.select_one(".p-price i") or item.select_one(".p-price strong")
        shop_el = item.select_one(".p-shop a") or item.select_one(".p-shop")
        commit_el = item.select_one(".p-commit a") or item.select_one(".p-commit")
        img_el = item.select_one(".p-img img")

        image = ""
        if img_el is not None:
            image = img_el.get("data-lazy-img") or img_el.get("src") or ""

        title = clean_text(title_el.get_text(" ", strip=True)) if title_el else ""
        if not title:
            return None

        if href.startswith("//"):
            href = "https:" + href
        elif href.startswith("/"):
            href = "https://item.jd.com" + href

        return Product(
            site=self.site,
            sku=sku,
            title=title,
            price=parse_price(price_el.get_text(" ", strip=True) if price_el else ""),
            shop=clean_text(shop_el.get_text(" ", strip=True)) if shop_el else "",
            comments=parse_int(commit_el.get_text(" ", strip=True) if commit_el else ""),
            url=href,
            image=image,
            keyword=keyword,
        )

    @staticmethod
    def _sku_from_href(href: str) -> str:
        digits = "".join(ch for ch in href if ch.isdigit())
        return digits[-12:] if len(digits) >= 6 else ""
