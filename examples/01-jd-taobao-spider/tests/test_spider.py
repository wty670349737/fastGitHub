from __future__ import annotations

from adapters.jd import JdAdapter
from adapters.taobao import TaobaoAdapter
from config import BASE_DIR, Settings
from models import Product
from pipeline import Crawler
from storage import ProductStore
from utils.text import parse_int, parse_price


def test_parse_price_and_int() -> None:
    assert parse_price("￥3,999.00") == 3999.0
    assert parse_price("暂无") == 0.0
    assert parse_int("10万+条评价") == 100000
    assert parse_int("2.5万+人付款") == 25000
    assert parse_int("3000+") == 3000


def test_jd_parse_fixture() -> None:
    html = (BASE_DIR / "fixtures" / "jd_search.html").read_text(encoding="utf-8")
    products = JdAdapter().parse(html, "手机")

    assert len(products) == 3
    first = products[0]
    assert first.site == "jd"
    assert first.sku == "100012043978"
    assert first.price == 3999.0
    assert first.comments == 100000
    assert first.title.startswith("Apple")
    assert first.url.startswith("https://item.jd.com/")


def test_taobao_parse_embedded_json() -> None:
    html = (BASE_DIR / "fixtures" / "taobao_search.html").read_text(encoding="utf-8")
    products = TaobaoAdapter().parse(html, "手机")

    assert len(products) == 3
    assert products[0].sku == "665432100001"
    assert products[0].sales == 25000
    assert products[0].price == 1899.0


def test_taobao_parse_html_fallback() -> None:
    html = """
    <div class="items">
      <div class="item J_Item" data-nid="123456">
        <div class="title"><a href="//item.taobao.com/item.htm?id=123456">测试商品</a></div>
        <div class="price"><strong>88.50</strong></div>
        <div class="shop"><a>测试店铺</a></div>
        <div class="deal-cnt">100人付款</div>
      </div>
    </div>
    """
    products = TaobaoAdapter().parse(html, "测试")

    assert len(products) == 1
    assert products[0].price == 88.5
    assert products[0].sales == 100


def test_store_dedup(tmp_path) -> None:
    store = ProductStore(tmp_path / "products.db")
    product = Product(site="jd", sku="1", title="A", price=1.0)

    assert store.save_many([product]) == 1
    assert store.save_many([product]) == 0
    assert store.count("jd") == 1

    rows = store.all("jd")
    assert rows[0]["title"] == "A"
    store.close()


def test_crawler_offline(tmp_path) -> None:
    settings = Settings(db_path=tmp_path / "crawl.db", delay_min=0, delay_max=0)

    with Crawler(settings) as crawler:
        first = crawler.crawl("jd", "手机", pages=1, offline=True)
        assert first.inserted == 3
        assert first.parsed == 3

        second = crawler.crawl("jd", "手机", pages=1, offline=True)
        assert second.parsed == 3
        assert second.inserted == 0
