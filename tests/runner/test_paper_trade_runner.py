"""模拟交易入口测试。"""

"""模拟交易入口测试。"""

from pathlib import Path

import duckdb
import pandas as pd

from engine.runner.run_paper_trade import run_paper_trade


def test_paper_trade_generates_next_day_orders(tmp_path: Path):
    bars = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=5, freq="D"),
            "symbol": ["000001.SZ"] * 5,
            "open": [10, 10, 10, 10, 10],
            "high": [10, 10, 10, 10, 10],
            "low": [10, 10, 10, 10, 10],
            "close": [10, 11, 12, 11, 13],
            "volume": [1000, 1000, 1000, 1000, 1000],
        }
    )
    out = run_paper_trade(output_dir=tmp_path, bars=bars)
    assert (out / "orders.csv").exists()


def test_paper_trade_uses_strategy_bundle_for_position_cap(tmp_path: Path):
    bars = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=6, freq="D"),
            "symbol": ["000001.SZ"] * 6,
            "open": [10, 10, 10, 10, 10, 10],
            "high": [10, 10, 10, 10, 10, 10],
            "low": [10, 10, 10, 10, 10, 10],
            "close": [10, 10, 11, 12, 13, 14],
            "volume": [1000, 1000, 1000, 1000, 1000, 1000],
        }
    )
    out = run_paper_trade(
        output_dir=tmp_path,
        bars=bars,
        strategy_bundle={
            "strategy": {"name": "ma_cross", "params": {"short_window": 2, "long_window": 3}},
            "portfolio": {"max_pos": 0.05, "gross_limit": 1.0},
        },
    )
    orders = pd.read_csv(out / "orders.csv")
    assert float(orders.iloc[0]["target_weight"]) <= 0.05


def test_paper_trade_loads_bars_from_duckdb(tmp_path: Path):
    db_path = tmp_path / "market.duckdb"
    con = duckdb.connect(str(db_path))
    con.execute(
        """
        create table daily_bars as
        select * from (
            values
            ('2026-01-01'::date, '000001.SZ', 10.0, 10.0, 10.0, 10.0, 1000.0),
            ('2026-01-02'::date, '000001.SZ', 10.0, 10.5, 9.9, 10.2, 1200.0),
            ('2026-01-03'::date, '000001.SZ', 10.2, 10.7, 10.1, 10.6, 1300.0)
        ) t(date, symbol, open, high, low, close, volume)
        """
    )
    con.close()
    out = run_paper_trade(
        output_dir=tmp_path / "rpt",
        bars=None,
        db_path=db_path,
        symbols=["000001.SZ"],
        start="2026-01-01",
        end="2026-01-31",
    )
    assert (out / "orders.csv").exists()
