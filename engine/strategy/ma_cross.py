from __future__ import annotations

"""均线交叉策略（示例策略）。"""

import pandas as pd

from .base import BaseStrategy


class MovingAverageCrossStrategy(BaseStrategy):
    """短均线上穿长均线时做多。"""

    def __init__(self, short_window: int = 5, long_window: int = 20) -> None:
        self.short_window = short_window
        self.long_window = long_window

    def generate(self, bars: pd.DataFrame) -> pd.DataFrame:
        data = bars.sort_values(["symbol", "date"]).copy()
        grouped = data.groupby("symbol")["close"]
        short_ma = grouped.transform(lambda s: s.rolling(self.short_window, min_periods=1).mean())
        long_ma = grouped.transform(lambda s: s.rolling(self.long_window, min_periods=1).mean())
        raw_signal = (short_ma > long_ma).astype(int)
        # 统一滞后一根 K 线，避免未来函数。
        data["signal"] = raw_signal.groupby(data["symbol"]).shift(1).fillna(0).astype(int)
        return data[["date", "symbol", "signal"]]
