from __future__ import annotations

"""日常数据更新脚本。

支持主数据源 + 备用数据源回退，并可刷新 DuckDB 视图。
"""

import argparse
from pathlib import Path

from engine.datafeed.akshare_adapter import fetch_daily_bars as akshare_fetch
from engine.datafeed.baostock_adapter import fetch_daily_bars as baostock_fetch
from engine.datafeed.update import update_daily_bars


def _select_provider(source: str):
    """选择主数据源。"""
    if source == "akshare":
        return akshare_fetch
    if source == "baostock":
        return baostock_fetch
    raise ValueError(f"unknown source: {source}")


def _select_fallback(source: str):
    """主源失败时的备用源。"""
    if source == "akshare":
        return baostock_fetch
    if source == "baostock":
        return akshare_fetch
    return None


def main() -> None:
    """命令行入口。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="akshare", choices=["akshare", "baostock"])
    parser.add_argument("--start", default="2026-03-01")
    parser.add_argument("--end", default="2026-03-31")
    parser.add_argument("--symbols", nargs="+", default=["000001.SZ"])
    parser.add_argument("--retries", type=int, default=2)
    args = parser.parse_args()
    provider = _select_provider(args.source)
    fallback_provider = _select_fallback(args.source)

    out = update_daily_bars(
        symbols=args.symbols,
        start=args.start,
        end=args.end,
        warehouse_dir=Path("data/warehouse"),
        provider=provider,
        db_path=Path("data/db/market.duckdb"),
        fallback_provider=fallback_provider,
        retries=args.retries,
    )
    print(f"source={args.source}, updated files: {out}")


if __name__ == "__main__":
    main()
