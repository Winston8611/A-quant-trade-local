"""回测入口测试。"""

from pathlib import Path

import duckdb
import pandas as pd

from engine.runner.run_backtest import run_backtest


def test_backtest_runner_produces_equity_curve(tmp_path: Path):
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
    out = run_backtest(output_dir=tmp_path, bars=bars)
    assert (out / "equity_curve.csv").exists()


def test_backtest_runner_loads_bars_from_duckdb(tmp_path: Path):
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
    out = run_backtest(
        output_dir=tmp_path / "rpt",
        bars=None,
        db_path=db_path,
        symbols=["000001.SZ"],
        start="2026-01-01",
        end="2026-01-31",
    )
    assert (out / "equity_curve.csv").exists()
