from __future__ import annotations

"""绩效指标计算（基础版）。"""

import pandas as pd


def simple_returns(equity: pd.Series) -> pd.Series:
    """由净值序列计算逐期收益率。"""
    return equity.pct_change().fillna(0.0)


def max_drawdown(equity: pd.Series) -> float:
    """计算最大回撤。"""
    peak = equity.cummax()
    dd = (equity / peak) - 1.0
    return float(dd.min())
