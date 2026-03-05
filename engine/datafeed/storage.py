from __future__ import annotations

"""数据标准化逻辑。

不同数据源字段命名不一致，本模块统一成项目内部标准字段。
"""

import pandas as pd

from .schema import DAILY_BAR_COLUMNS


def normalize_daily_bars(df: pd.DataFrame) -> pd.DataFrame:
    """将原始日线数据转为标准列并排序。"""
    rename_map = {
        "trade_date": "date",
        "ts_code": "symbol",
        "vol": "volume",
    }
    out = df.rename(columns=rename_map).copy()
    out["date"] = pd.to_datetime(out["date"])
    return out[DAILY_BAR_COLUMNS].sort_values(["date", "symbol"]).reset_index(drop=True)
