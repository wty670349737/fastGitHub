"""导出 CSV / JSON。"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable

FIELDS = [
    "site",
    "sku",
    "title",
    "price",
    "shop",
    "sales",
    "comments",
    "url",
    "keyword",
    "captured_at",
]


def export_json(rows: Iterable[dict], path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    data = list(rows)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return target


def export_csv(rows: Iterable[dict], path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    # utf-8-sig 让 Excel 打开中文不乱码
    with target.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return target
