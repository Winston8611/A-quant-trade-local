"""均线策略测试。"""

import pandas as pd

from engine.strategy.ma_cross import MovingAverageCrossStrategy


def test_ma_cross_signal_uses_previous_bar_only():
    bars = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=8, freq="D"),
            "symbol": ["000001.SZ"] * 8,
            "close": [10, 10, 10, 10, 10, 10, 20, 20],
        }
    )
    strategy = MovingAverageCrossStrategy(short_window=2, long_window=3)
    signals = strategy.generate(bars)
    # Cross happens on day 7 with jump, but signal must appear on day 8 due to shift(1).
    assert signals.iloc[6]["signal"] == 0
    assert signals.iloc[7]["signal"] == 1
