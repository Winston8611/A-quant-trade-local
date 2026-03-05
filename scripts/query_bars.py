from __future__ import annotations

"""命令行查询脚本：快速查看本地 DuckDB 行情。"""

import argparse
from pathlib import Path

from engine.datafeed.query import load_bars_from_duckdb


def main() -> None:
    """命令行入口。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--db-path", default="data/db/market.duckdb")
    parser.add_argument("--symbols", nargs="*", default=None)
    parser.add_argument("--start", default=None)
    parser.add_argument("--end", default=None)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    bars = load_bars_from_duckdb(
        db_path=Path(args.db_path),
        symbols=args.symbols,
        start=args.start,
        end=args.end,
        limit=args.limit,
    )
    if bars.empty:
        print("No rows matched.")
        return
    print(bars.to_string(index=False))
    print(f"\nrows={len(bars)}")


if __name__ == "__main__":
    main()
