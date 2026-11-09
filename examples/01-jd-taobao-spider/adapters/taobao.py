"""淘宝搜索页适配器。

淘宝搜索是前端渲染的，但历史页面会把首屏数据塞进
`g_page_config = {...}` 或 `window.__INIT_DATA__ = {...}` 脚本里。
本适配器优先解析内嵌 JSON，解析不到再退回 HTML 选择器，
覆盖两种常见页面形态，也方便面试时讲“为什么不用 Selenium”。
"""

from __future__ import annotations

import json
import re
from urllib.parse import quote

from bs4 import BeautifulSoup
from bs4.element import Tag

from adapters.base import BaseAdapter
from models import Product
from utils.text import clean_text, parse_int, parse_price


class TaobaoAdapter(BaseAdapter):
    site = "taobao"
    home = "https://www.taobao.com/"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        return f"https://s.taobao.com/search?q={quote(keyword)}&s={(page - 1) * 44}"

    def parse(self, html: str, keyword: str) -> list[Product]:
        auctions = self._parse_embedded_json(html)
        if auctions:
            products = [self._from_auction(a, keyword) for a in auctions]
            return [p for p in products if p is not None]
        return self._parse_html(html, keyword)

    # ---------- 内嵌 JSON ----------
    def _parse_embedded_json(self, html: str) -> list[dict]:
        for marker in ("g_page_config", "__INIT_DATA__"):
            config = self._extract_json(html, marker)
            if not config:
                continue
            data = config.get("mods", {}).get("itemlist", {}).get("data", {})
            auctions = data.get("auctions") or data.get("items") or []
            if isinstance(auctions, list) and auctions:
                return auctions
        return []

    @staticmethod
    def _extract_json(html: str, marker: str) -> dict | None:
        index = html.find(marker)
        if index == -1:
            return None
        start = html.find("{", index)
        if start == -1:
            return None

        depth = 0
        in_string = False
        escape = False
        for pos in range(start, len(html)):
            char = html[pos]
            if in_string:
                if escape:
                    escape = False
                elif char == "\\":
                    escape = True
                elif char == '"':
                    in_string = False
                continue
            if char == '"':
                in_string = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(html[start : pos + 1])
                    except json.JSONDecodeError:
                        return None
        return None

    def _from_auction(self, auction: dict, keyword: str) -> Product | None:
        sku = str(auction.get("nid") or auction.get("item_id") or "").strip()
        title = clean_text(auction.get("raw_title") or auction.get("title"))
        if not sku or not title:
            return None

        url = auction.get("detail_url") or ""
        if url.startswith("//"):
            url = "https:" + url
        elif not url:
            url = f"https://item.taobao.com/item.htm?id={sku}"

        return Product(
            site=self.site,
            sku=sku,
            title=title,
            price=parse_price(str(auction.get("view_price") or auction.get("price") or "")),
            shop=clean_text(auction.get("nick") or auction.get("shopName")),
            sales=parse_int(str(auction.get("view_sales") or "")),
            comments=parse_int(str(auction.get("comment_count") or "")),
            url=url,
            image=auction.get("pic_url") or "",
            keyword=keyword,
        )

    # ---------- HTML 兜底 ----------
    def _parse_html(self, html: str, keyword: str) -> list[Product]:
        soup = BeautifulSoup(html, "html.parser")
        products: list[Product] = []
        for item in soup.select(".items .item, .item.J_Item"):
            product = self._from_html_item(item, keyword)
            if product is not None:
                products.append(product)
        return products

    def _from_html_item(self, item: Tag, keyword: str) -> Product | None:
        sku = clean_text(item.get("data-nid") or item.get("data-id"))
        title_el = item.select_one(".title a") or item.select_one(".title")
        title = clean_text(title_el.get_text(" ", strip=True)) if title_el else ""
        if not title:
            return None

        href = title_el.get("href", "") if title_el else ""
        if not sku:
            match = re.search(r"id=(\d+)", href)
            sku = match.group(1) if match else ""
        if not sku:
            return None
        if href.startswith("//"):
            href = "https:" + href

        price_el = item.select_one(".price strong") or item.select_one(".price")
        shop_el = item.select_one(".shop a") or item.select_one(".shop")
        deal_el = item.select_one(".deal-cnt")
        img_el = item.select_one(".pic img")

        return Product(
            site=self.site,
            sku=sku,
            title=title,
            price=parse_price(price_el.get_text(" ", strip=True) if price_el else ""),
            shop=clean_text(shop_el.get_text(" ", strip=True)) if shop_el else "",
            sales=parse_int(deal_el.get_text(" ", strip=True) if deal_el else ""),
            url=href,
            image=(img_el.get("data-src") or img_el.get("src") or "") if img_el else "",
            keyword=keyword,
        )
