from __future__ import annotations

"""模拟交易入口。

核心输出是 `orders.csv`，表示下一交易日目标仓位建议。
"""

import argparse
from pathlib import Path

import pandas as pd
import yaml

from engine.datafeed.query import load_bars_from_duckdb
from engine.portfolio.sizer import build_target_weights
from engine.strategy.bundle import build_strategy, load_strategy_bundle


def run_paper_trade(
    output_dir: Path,
    bars: pd.DataFrame | None = None,
    db_path: Path | None = None,
    symbols: list[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    strategy_bundle: dict | None = None,
) -> Path:
    if bars is None:
        if db_path is None:
            raise ValueError("db_path is required when bars is None")
        bars = load_bars_from_duckdb(db_path=db_path, symbols=symbols, start=start, end=end)
    if bars.empty:
        raise ValueError("No bars available for paper-trade run")

    output_dir.mkdir(parents=True, exist_ok=True)
    strategy_bundle = strategy_bundle or {
        "strategy": {"name": "ma_cross", "params": {"short_window": 2, "long_window": 3}},
        "portfolio": {"max_pos": 0.2, "gross_limit": 1.0},
    }
    strategy = build_strategy(strategy_bundle["strategy"])
    signals = strategy.generate(bars)
    # 只使用每只股票最新一天信号，模拟“今日收盘后生成明日目标仓位”。
    latest = signals.sort_values("date").groupby("symbol").tail(1)
    signal_map = dict(zip(latest["symbol"], latest["signal"]))
    portfolio_cfg = strategy_bundle.get("portfolio", {})
    weights = build_target_weights(
        signal_map,
        max_pos=float(portfolio_cfg.get("max_pos", 0.2)),
        gross_limit=float(portfolio_cfg.get("gross_limit", 1.0)),
    )
    orders = pd.DataFrame([{"symbol": k, "target_weight": v} for k, v in weights.items()])
    orders.to_csv(output_dir / "orders.csv", index=False)
    return output_dir


def main() -> None:
    """命令行入口：读取 YAML 后执行模拟交易。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/paper_trade.yaml")
    args = parser.parse_args()
    cfg = yaml.safe_load(Path(args.config).read_text())
    data_cfg = cfg.get("data", {})
    date_cfg = cfg.get("date_range", {})
    strategy_cfg_path = Path(cfg.get("strategy_config", "configs/strategies/ma_cross.yaml"))
    strategy_bundle = load_strategy_bundle(strategy_cfg_path)
    run_paper_trade(
        output_dir=Path("reports/paper_trade"),
        bars=None,
        db_path=Path(data_cfg.get("db_path", "data/db/market.duckdb")),
        symbols=data_cfg.get("symbols"),
        start=date_cfg.get("start"),
        end=date_cfg.get("end"),
        strategy_bundle=strategy_bundle,
    )


if __name__ == "__main__":
    main()
