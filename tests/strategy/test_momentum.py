"""动量策略测试。"""

import pandas as pd

from engine.strategy.momentum import MomentumStrategy


def test_momentum_strategy_generates_lagged_signal():
    bars = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=6, freq="D"),
            "symbol": ["000001.SZ"] * 6,
            "close": [10, 10, 11, 12, 12, 13],
        }
    )
    signals = MomentumStrategy(lookback=2).generate(bars)
    assert signals.iloc[0]["signal"] == 0
    assert signals.iloc[-1]["signal"] in (0, 1)
