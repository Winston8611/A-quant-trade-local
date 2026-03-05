from __future__ import annotations

"""风险过滤规则（简化版）。"""


def apply_tradeable_filter(
    targets: dict[str, float],
    suspended_symbols: set[str] | None = None,
) -> dict[str, float]:
    """过滤不可交易标的（如停牌）。"""
    suspended_symbols = suspended_symbols or set()
    return {symbol: w for symbol, w in targets.items() if symbol not in suspended_symbols}
