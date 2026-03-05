from __future__ import annotations

"""AkShare 适配器。

职责：把 AkShare 返回的数据转成项目统一字段。
"""

import pandas as pd


def _to_ak_symbol(symbol: str) -> str:
    """将 `000001.SZ` 转为 AkShare 常用的 `000001`。"""
    return symbol.split(".")[0]


def fetch_daily_bars(symbol: str, start: str, end: str, client=None) -> pd.DataFrame:
    """抓取并标准化单只股票日线。

    参数 start/end 使用 `YYYY-MM-DD`，函数内部会转换为 AkShare 需要的格式。
    """
    if client is None:
        import akshare as ak

        client = ak
    raw = client.stock_zh_a_hist(
        symbol=_to_ak_symbol(symbol),
        period="daily",
        start_date=start.replace("-", ""),
        end_date=end.replace("-", ""),
        adjust="qfq",
    )
    rename_map = {
        "日期": "trade_date",
        "开盘": "open",
        "最高": "high",
        "最低": "low",
        "收盘": "close",
        "成交量": "vol",
    }
    out = raw.rename(columns=rename_map).copy()
    out["ts_code"] = symbol
    return out[["trade_date", "ts_code", "open", "high", "low", "close", "vol"]]
