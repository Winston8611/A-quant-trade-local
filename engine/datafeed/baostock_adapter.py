from __future__ import annotations

"""BaoStock 适配器。

职责：登录 -> 查询 -> 标准化 -> 登出，输出统一字段。
"""

import pandas as pd


def _to_bs_symbol(symbol: str) -> str:
    """将 `000001.SZ` 转为 BaoStock 形式 `sz.000001`。"""
    code, exch = symbol.split(".")
    return f"{exch.lower()}.{code}"


def fetch_daily_bars(symbol: str, start: str, end: str, client=None) -> pd.DataFrame:
    """抓取并标准化单只股票日线。"""
    if client is None:
        import baostock as bs

        client = bs

    login_result = client.login()
    if getattr(login_result, "error_code", "0") != "0":
        raise RuntimeError("baostock login failed")
    try:
        # `adjustflag=2` 表示前复权，和 AkShare 适配器保持一致口径。
        rs = client.query_history_k_data_plus(
            _to_bs_symbol(symbol),
            "date,open,high,low,close,volume",
            start_date=start,
            end_date=end,
            frequency="d",
            adjustflag="2",
        )
        if getattr(rs, "error_code", "0") != "0":
            raise RuntimeError("baostock query failed")
        rows = []
        while rs.next():
            rows.append(rs.get_row_data())
        out = pd.DataFrame(rows, columns=rs.fields)
    finally:
        client.logout()

    out = out.rename(columns={"date": "trade_date", "volume": "vol"})
    out["ts_code"] = symbol
    for col in ["open", "high", "low", "close", "vol"]:
        out[col] = out[col].astype(float)
    return out[["trade_date", "ts_code", "open", "high", "low", "close", "vol"]]
