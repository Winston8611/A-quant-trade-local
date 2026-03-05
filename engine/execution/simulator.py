from __future__ import annotations

"""成交仿真器（A 股日频简化版）。"""

from dataclasses import dataclass

from .costs import calc_trade_cost


@dataclass
class FillResult:
    """一次模拟成交的结果快照。"""

    symbol: str
    side: str
    price: float
    quantity: int
    total_fee: float


class DailyExecutionSimulator:
    """通过滑点与费用模型模拟成交。"""

    def __init__(self, slippage_bps: float = 5.0) -> None:
        self.slippage_bps = slippage_bps

    def fill(self, symbol: str, side: str, price: float, quantity: int) -> FillResult:
        # 买单向上滑点、卖单向下滑点。
        slip_mult = 1.0 + (self.slippage_bps / 10000.0 if side.lower() == "buy" else -self.slippage_bps / 10000.0)
        exec_price = price * slip_mult
        fee = calc_trade_cost(exec_price, quantity, side)["total"]
        return FillResult(symbol=symbol, side=side, price=exec_price, quantity=quantity, total_fee=fee)
