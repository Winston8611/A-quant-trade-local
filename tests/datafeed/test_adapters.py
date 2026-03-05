"""免费数据源适配器测试（使用假客户端，避免联网）。"""

import pandas as pd

from engine.datafeed.akshare_adapter import fetch_daily_bars as fetch_akshare_daily_bars
from engine.datafeed.baostock_adapter import fetch_daily_bars as fetch_baostock_daily_bars


class FakeAkClient:
    def stock_zh_a_hist(self, **kwargs):
        del kwargs
        return pd.DataFrame(
            [
                {"日期": "2026-03-01", "开盘": 10.0, "最高": 11.0, "最低": 9.5, "收盘": 10.3, "成交量": 1234},
            ]
        )


def test_akshare_adapter_normalizes_columns():
    out = fetch_akshare_daily_bars("000001.SZ", "2026-03-01", "2026-03-31", client=FakeAkClient())
    assert list(out.columns) == ["trade_date", "ts_code", "open", "high", "low", "close", "vol"]
    assert out.iloc[0]["ts_code"] == "000001.SZ"


class FakeBsQueryResult:
    def __init__(self):
        self.error_code = "0"
        self.fields = ["date", "open", "high", "low", "close", "volume"]
        self._rows = [["2026-03-01", "10", "11", "9.5", "10.3", "1234"]]
        self._idx = -1

    def next(self):
        self._idx += 1
        return self._idx < len(self._rows)

    def get_row_data(self):
        return self._rows[self._idx]


class FakeBsClient:
    def login(self):
        class R:
            error_code = "0"

        return R()

    def logout(self):
        return None

    def query_history_k_data_plus(self, *args, **kwargs):
        del args, kwargs
        return FakeBsQueryResult()


def test_baostock_adapter_normalizes_columns():
    out = fetch_baostock_daily_bars("000001.SZ", "2026-03-01", "2026-03-31", client=FakeBsClient())
    assert list(out.columns) == ["trade_date", "ts_code", "open", "high", "low", "close", "vol"]
    assert out.iloc[0]["ts_code"] == "000001.SZ"
