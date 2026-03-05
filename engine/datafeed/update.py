from __future__ import annotations

"""数据更新主流程。

给定股票列表和时间区间，依次：
1) 调用数据源抓取原始行情；
2) 标准化字段；
3) 写入本地 Parquet；
4) 可选刷新 DuckDB 视图，供回测/模拟统一读取。
"""

from pathlib import Path
from typing import Callable

import pandas as pd

from .duckdb_store import refresh_daily_bars_view, write_parquet
from .storage import normalize_daily_bars


def update_daily_bars(
    symbols: list[str],
    start: str,
    end: str,
    warehouse_dir: Path,
    provider: Callable[[str, str, str], pd.DataFrame],
    db_path: Path | None = None,
    fallback_provider: Callable[[str, str, str], pd.DataFrame] | None = None,
    retries: int = 1,
) -> list[Path]:
    # 确保本地仓库目录存在。
    warehouse_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for symbol in symbols:
        last_error: Exception | None = None
        raw: pd.DataFrame | None = None
        # 遇到临时网络波动时按 retries 重试。
        for _ in range(max(retries, 1)):
            try:
                raw = provider(symbol, start, end)
                break
            except Exception as exc:  # pragma: no cover - exercised through tests
                last_error = exc
        # 主数据源失败后，尝试备用数据源。
        if raw is None and fallback_provider is not None:
            raw = fallback_provider(symbol, start, end)
        if raw is None:
            raise RuntimeError(f"Failed to fetch bars for {symbol}") from last_error
        norm = normalize_daily_bars(raw)
        out_path = warehouse_dir / f"{symbol}.parquet"
        write_parquet(norm, out_path)
        written.append(out_path)
    # 刷新视图后，runner 可直接从 daily_bars 查询到最新数据。
    if db_path is not None:
        refresh_daily_bars_view(db_path, warehouse_dir)
    return written
