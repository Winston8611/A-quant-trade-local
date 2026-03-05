from __future__ import annotations

"""回测入口。

支持两种输入：
1) 直接传入 bars DataFrame（常用于测试）；
2) 从 DuckDB 读取（常用于真实运行）。
"""

import argparse
from pathlib import Path

import pandas as pd
import yaml

from engine.analytics.metrics import max_drawdown, simple_returns
from engine.datafeed.query import load_bars_from_duckdb
from engine.strategy.bundle import build_strategy, load_strategy_bundle


def run_backtest(
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
        raise ValueError("No bars available for backtest run")

    output_dir.mkdir(parents=True, exist_ok=True)
    strategy_bundle = strategy_bundle or {
        "strategy": {"name": "ma_cross", "params": {"short_window": 2, "long_window": 3}}
    }
    strategy = build_strategy(strategy_bundle["strategy"])
    signal_df = strategy.generate(bars)
    # 按日期回放：信号乘以当日收益，得到简化净值曲线。
    merged = bars.merge(signal_df, on=["date", "symbol"], how="left").fillna({"signal": 0})
    merged = merged.sort_values("date")
    ret = merged["close"].pct_change().fillna(0.0)
    equity = (1.0 + ret * merged["signal"]).cumprod()
    out = pd.DataFrame({"date": merged["date"], "equity": equity})
    out.to_csv(output_dir / "equity_curve.csv", index=False)
    summary = pd.DataFrame(
        {
            "metric": ["total_return", "max_drawdown"],
            "value": [float(equity.iloc[-1] - 1.0), max_drawdown(equity)],
        }
    )
    summary.to_csv(output_dir / "summary.csv", index=False)
    _ = simple_returns(equity)
    return output_dir


def main() -> None:
    """命令行入口：读取 YAML 后执行回测。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/backtest.yaml")
    args = parser.parse_args()
    cfg = yaml.safe_load(Path(args.config).read_text())
    data_cfg = cfg.get("data", {})
    date_cfg = cfg.get("date_range", {})
    strategy_cfg_path = Path(cfg.get("strategy_config", "configs/strategies/ma_cross.yaml"))
    strategy_bundle = load_strategy_bundle(strategy_cfg_path)
    run_backtest(
        output_dir=Path("reports/backtest"),
        bars=None,
        db_path=Path(data_cfg.get("db_path", "data/db/market.duckdb")),
        symbols=data_cfg.get("symbols"),
        start=date_cfg.get("start"),
        end=date_cfg.get("end"),
        strategy_bundle=strategy_bundle,
    )


if __name__ == "__main__":
    main()
