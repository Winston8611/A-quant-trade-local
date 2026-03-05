from __future__ import annotations

"""交易成本模型（A 股简化版）。"""


def calc_trade_cost(
    price: float,
    quantity: int,
    side: str,
    commission_rate: float = 0.0003,
    stamp_tax_rate: float = 0.001,
) -> dict[str, float]:
    """返回佣金、印花税和总费用。"""
    notional = price * quantity
    commission = max(notional * commission_rate, 5.0)
    stamp_tax = notional * stamp_tax_rate if side.lower() == "sell" else 0.0
    return {"commission": commission, "stamp_tax": stamp_tax, "total": commission + stamp_tax}
