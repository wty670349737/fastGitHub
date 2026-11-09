"""SQLite 存储：以 (site, sku) 唯一约束实现天然去重。"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from models import Product

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site TEXT NOT NULL,
    sku TEXT NOT NULL,
    title TEXT NOT NULL,
    price REAL NOT NULL DEFAULT 0,
    shop TEXT NOT NULL DEFAULT '',
    sales INTEGER NOT NULL DEFAULT 0,
    comments INTEGER NOT NULL DEFAULT 0,
    url TEXT NOT NULL DEFAULT '',
    image TEXT NOT NULL DEFAULT '',
    keyword TEXT NOT NULL DEFAULT '',
    captured_at TEXT NOT NULL,
    UNIQUE(site, sku)
);
CREATE INDEX IF NOT EXISTS idx_products_site ON products(site);
CREATE INDEX IF NOT EXISTS idx_products_price ON products(price);
"""

COLUMNS = (
    "site",
    "sku",
    "title",
    "price",
    "shop",
    "sales",
    "comments",
    "url",
    "image",
    "keyword",
    "captured_at",
)


class ProductStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def save_many(self, products: list[Product]) -> int:
        """批量写入，返回真正新增的条数（重复的会被忽略）。"""
        if not products:
            return 0
        rows = []
        for product in products:
            if not product.captured_at:
                product.captured_at = datetime.now().isoformat(timespec="seconds")
            rows.append(tuple(getattr(product, column) for column in COLUMNS))

        placeholders = ", ".join("?" for _ in COLUMNS)
        sql = (
            f"INSERT OR IGNORE INTO products ({', '.join(COLUMNS)}) "
            f"VALUES ({placeholders})"
        )
        inserted = 0
        with self.conn:
            for row in rows:
                inserted += self.conn.execute(sql, row).rowcount
        return inserted

    def count(self, site: str | None = None) -> int:
        if site:
            row = self.conn.execute(
                "SELECT COUNT(*) FROM products WHERE site = ?", (site,)
            ).fetchone()
        else:
            row = self.conn.execute("SELECT COUNT(*) FROM products").fetchone()
        return int(row[0])

    def all(self, site: str | None = None, limit: int = 1000) -> list[dict]:
        if site:
            rows = self.conn.execute(
                "SELECT * FROM products WHERE site = ? ORDER BY price ASC LIMIT ?",
                (site, limit),
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM products ORDER BY price ASC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(row) for row in rows]

    def close(self) -> None:
        self.conn.close()

    def __enter__(self) -> "ProductStore":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
