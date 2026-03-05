"""数据标准化模块测试。"""

import pandas as pd

from engine.datafeed.storage import normalize_daily_bars


def test_normalize_daily_bars_columns_and_order():
    raw = pd.DataFrame(
        [
            {
                "trade_date": "2026-03-01",
                "ts_code": "000001.SZ",
                "open": 10,
                "high": 11,
                "low": 9,
                "close": 10.5,
                "vol": 1000,
            }
        ]
    )
    out = normalize_daily_bars(raw)
    assert list(out.columns) == ["date", "symbol", "open", "high", "low", "close", "volume"]
    assert out.iloc[0]["symbol"] == "000001.SZ"
