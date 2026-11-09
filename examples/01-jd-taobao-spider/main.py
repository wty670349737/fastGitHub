"""命令行入口。

用法：
    python main.py                                  # 离线演示（京东 + 淘宝）
    python main.py crawl --site jd --keyword 手机 --pages 1 --offline
    python main.py crawl --site taobao --keyword 手机 --pages 1
    python main.py export --format csv --site jd
    python main.py stats
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime

from config import Settings
from export import export_csv, export_json
from pipeline import Crawler
from storage import ProductStore


def configure_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def cmd_crawl(args: argparse.Namespace) -> int:
    settings = Settings()
    with Crawler(settings) as crawler:
        result = crawler.crawl(
            args.site, args.keyword, pages=args.pages, offline=args.offline
        )
        print(
            f"[{result.site}] 关键词={result.keyword} 抓取页={result.fetched} "
            f"解析={result.parsed} 新增入库={result.inserted} 跳过={result.skipped}"
        )
        for error in result.errors:
            print(f"  - {error}", file=sys.stderr)
        print(
            f"数据库累计 {crawler.store.count()} 条，"
            f"其中 {args.site} {crawler.store.count(args.site)} 条"
        )
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    settings = Settings()
    store = ProductStore(settings.db_path)
    try:
        rows = store.all(args.site, limit=args.limit)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        if args.format == "csv":
            path = export_csv(rows, args.output or f"data/products-{stamp}.csv")
        else:
            path = export_json(rows, args.output or f"data/products-{stamp}.json")
        print(f"已导出 {len(rows)} 条到 {path}")
    finally:
        store.close()
    return 0


def cmd_stats(_: argparse.Namespace) -> int:
    settings = Settings()
    store = ProductStore(settings.db_path)
    try:
        print(f"数据库：{settings.db_path}")
        print(f"总数：{store.count()}")
        print(f"京东：{store.count('jd')}")
        print(f"淘宝：{store.count('taobao')}")
    finally:
        store.close()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="京东 / 淘宝商品数据采集示例（仅用于学习与授权数据）"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="输出调试日志")
    sub = parser.add_subparsers(dest="command")

    crawl = sub.add_parser("crawl", help="采集商品")
    crawl.add_argument("--site", choices=["jd", "taobao", "all"], default="all")
    crawl.add_argument("--keyword", default="手机")
    crawl.add_argument("--pages", type=int, default=1)
    crawl.add_argument(
        "--offline", action="store_true", help="使用内置 HTML 样例，不访问真实网站"
    )
    crawl.set_defaults(func=cmd_crawl)

    export = sub.add_parser("export", help="导出数据")
    export.add_argument("--format", choices=["csv", "json"], default="csv")
    export.add_argument("--site", choices=["jd", "taobao"], default=None)
    export.add_argument("--limit", type=int, default=500)
    export.add_argument("--output", default=None)
    export.set_defaults(func=cmd_export)

    stats = sub.add_parser("stats", help="查看数据库统计")
    stats.set_defaults(func=cmd_stats)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(getattr(args, "verbose", False))

    if not getattr(args, "command", None):
        # 不带参数时跑一遍离线演示，保证零配置可运行
        args.command = "crawl"
        args.site = "all"
        args.keyword = "手机"
        args.pages = 1
        args.offline = True

    if args.command == "crawl":
        if args.site == "all":
            code = 0
            for site in ("jd", "taobao"):
                args.site = site
                code = max(code, cmd_crawl(args))
            return code
        return cmd_crawl(args)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
