from __future__ import annotations

"""策略抽象基类。

所有策略都应输出统一格式：`date, symbol, signal`。
"""

from abc import ABC, abstractmethod

import pandas as pd


class BaseStrategy(ABC):
    """策略接口定义。"""

    @abstractmethod
    def generate(self, bars: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError
