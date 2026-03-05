from __future__ import annotations

"""DuckDB 行情查询工具。

给 runner 和脚本提供统一入口：
按股票、日期区间读取 `daily_bars`，返回 pandas DataFrame。
"""

from pathlib import Path

import duckdb
import pandas as pd


def _sql_quote(value: str) -> str:
    """最小化 SQL 注入风险的转义（用于拼接简单条件）。"""
    return value.replace("'", "''")


def load_bars_from_duckdb(
    db_path: Path,
    symbols: list[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    limit: int | None = None,
) -> pd.DataFrame:
    # 逐步拼接 where 条件，便于按需过滤。
    clauses: list[str] = []
    if symbols:
        quoted = ", ".join(f"'{_sql_quote(sym)}'" for sym in symbols)
        clauses.append(f"symbol in ({quoted})")
    if start:
        clauses.append(f"date >= date '{_sql_quote(start)}'")
    if end:
        clauses.append(f"date <= date '{_sql_quote(end)}'")

    where = f" where {' and '.join(clauses)}" if clauses else ""
    limit_clause = f" limit {int(limit)}" if limit is not None else ""
    sql = (
        "select date, symbol, open, high, low, close, volume "
        "from daily_bars"
        f"{where} "
        "order by date, symbol"
        f"{limit_clause}"
    )

    con = duckdb.connect(str(db_path))
    try:
        out = con.execute(sql).fetchdf()
    finally:
        con.close()
    # 统一日期类型，避免后续策略计算类型不一致。
    if not out.empty:
        out["date"] = pd.to_datetime(out["date"])
    return out
