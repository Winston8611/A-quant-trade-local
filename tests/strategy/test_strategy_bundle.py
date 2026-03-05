"""策略配置加载与工厂注册测试。"""

from pathlib import Path

import yaml

from engine.strategy.bundle import build_strategy, load_strategy_bundle


def test_load_strategy_bundle_from_yaml(tmp_path: Path):
    bundle_path = tmp_path / "ma_cross.yaml"
    bundle_path.write_text(
        yaml.safe_dump(
            {
                "strategy": {"name": "ma_cross", "params": {"short_window": 3, "long_window": 8}},
                "portfolio": {"max_pos": 0.15, "gross_limit": 0.9},
            }
        )
    )
    bundle = load_strategy_bundle(bundle_path)
    assert bundle["strategy"]["name"] == "ma_cross"
    assert bundle["strategy"]["params"]["short_window"] == 3
    assert bundle["portfolio"]["max_pos"] == 0.15


def test_build_strategy_from_bundle():
    strategy = build_strategy({"name": "ma_cross", "params": {"short_window": 2, "long_window": 3}})
    assert strategy.short_window == 2
    assert strategy.long_window == 3


def test_build_momentum_strategy_from_bundle():
    strategy = build_strategy({"name": "momentum", "params": {"lookback": 4}})
    assert strategy.lookback == 4
