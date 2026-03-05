"""仓位分配测试。"""

from engine.portfolio.sizer import build_target_weights


def test_sizer_respects_single_position_cap():
    signals = {
        "000001.SZ": 1,
        "000002.SZ": 1,
        "000004.SZ": 1,
        "000005.SZ": 1,
    }
    weights = build_target_weights(signals, max_pos=0.2, gross_limit=1.0)
    assert max(weights.values()) <= 0.2
    assert sum(weights.values()) <= 1.0
