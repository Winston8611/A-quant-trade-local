from __future__ import annotations

"""DuckDB 与 Parquet 存储桥接层。"""

from pathlib import Path

import duckdb
import pandas as pd


def write_parquet(df: pd.DataFrame, path: Path) -> None:
    """使用 DuckDB 写 Parquet，避免环境差异导致的写出兼容问题。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.register("bars_df", df)
    escaped = str(path).replace("'", "''")
    con.execute(f"COPY bars_df TO '{escaped}' (FORMAT PARQUET)")
    con.close()


def refresh_daily_bars_view(db_path: Path, warehouse_dir: Path) -> None:
    """将目录下所有 Parquet 统一映射为 DuckDB 视图 `daily_bars`。"""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    warehouse_dir.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db_path))
    parquet_glob = str(warehouse_dir / "*.parquet").replace("'", "''")
    con.execute(
        "CREATE OR REPLACE VIEW daily_bars AS "
        f"SELECT * FROM read_parquet('{parquet_glob}', union_by_name=true)"
    )
    con.close()
