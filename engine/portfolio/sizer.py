from __future__ import annotations

"""仓位分配模块（简化版）。

当前逻辑：对做多信号股票等权，再应用单票上限。
"""


def build_target_weights(
    signals: dict[str, int],
    max_pos: float = 0.2,
    gross_limit: float = 1.0,
) -> dict[str, float]:
    longs = [s for s, sig in signals.items() if sig > 0]
    if not longs:
        return {}
    eq = gross_limit / len(longs)
    clipped = min(eq, max_pos)
    return {s: clipped for s in longs}
