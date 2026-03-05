from __future__ import annotations

"""动量策略（示例策略）。"""

import pandas as pd

from .base import BaseStrategy


class MomentumStrategy(BaseStrategy):
    """回看 lookback 个交易日，动量为正则做多。"""

    def __init__(self, lookback: int = 5) -> None:
        self.lookback = lookback

    def generate(self, bars: pd.DataFrame) -> pd.DataFrame:
        data = bars.sort_values(["symbol", "date"]).copy()
        grouped = data.groupby("symbol")["close"]
        momentum = grouped.transform(lambda s: s.pct_change(self.lookback))
        raw_signal = (momentum > 0).astype(int)
        # 同样做信号滞后，防止使用未来数据。
        data["signal"] = raw_signal.groupby(data["symbol"]).shift(1).fillna(0).astype(int)
        return data[["date", "symbol", "signal"]]
