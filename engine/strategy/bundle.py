from __future__ import annotations

"""策略配置加载与策略工厂。

目标：让策略切换尽量只改 YAML，不改 runner 代码。
"""

from pathlib import Path
from typing import Any

import yaml

from .ma_cross import MovingAverageCrossStrategy
from .momentum import MomentumStrategy


def _build_ma_cross(params: dict[str, Any]):
    return MovingAverageCrossStrategy(
        short_window=int(params.get("short_window", 5)),
        long_window=int(params.get("long_window", 20)),
    )


def _build_momentum(params: dict[str, Any]):
    return MomentumStrategy(
        lookback=int(params.get("lookback", 5)),
    )


STRATEGY_REGISTRY = {
    "ma_cross": _build_ma_cross,
    "momentum": _build_momentum,
}


def load_strategy_bundle(path: Path) -> dict[str, Any]:
    """读取策略配置文件并补齐默认值。"""
    raw = yaml.safe_load(path.read_text()) or {}
    strategy = raw.get("strategy", {})
    portfolio = raw.get("portfolio", {})
    return {
        "strategy": {
            "name": strategy.get("name", "ma_cross"),
            "params": strategy.get("params", {"short_window": 5, "long_window": 20}),
        },
        "portfolio": {
            "max_pos": float(portfolio.get("max_pos", 0.2)),
            "gross_limit": float(portfolio.get("gross_limit", 1.0)),
        },
    }


def build_strategy(strategy_cfg: dict[str, Any]):
    """根据策略名从注册表构建实例。"""
    name = strategy_cfg.get("name", "ma_cross")
    params = strategy_cfg.get("params", {})
    builder = STRATEGY_REGISTRY.get(name)
    if builder is None:
        supported = ", ".join(sorted(STRATEGY_REGISTRY.keys()))
        raise ValueError(f"Unsupported strategy: {name}. Supported: {supported}")
    return builder(params)
