"""交易费用/成交仿真测试。"""

from engine.execution.costs import calc_trade_cost


def test_sell_applies_stamp_tax_and_commission():
    fees = calc_trade_cost(price=10.0, quantity=1000, side="sell", commission_rate=0.0003, stamp_tax_rate=0.001)
    assert fees["commission"] > 0
    assert fees["stamp_tax"] > 0
