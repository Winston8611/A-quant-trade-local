"""数据更新流程测试（含重试、回退、DuckDB 刷新）。"""

from pathlib import Path

import duckdb
import pandas as pd

from engine.datafeed.update import update_daily_bars


def test_update_daily_bars_writes_parquet(tmp_path: Path):
    def fake_provider(symbol: str, start: str, end: str) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {
                    "trade_date": "2026-03-01",
                    "ts_code": symbol,
                    "open": 10.0,
                    "high": 11.0,
                    "low": 9.5,
                    "close": 10.3,
                    "vol": 1234,
                }
            ]
        )

    written = update_daily_bars(
        symbols=["000001.SZ"],
        start="2026-03-01",
        end="2026-03-05",
        warehouse_dir=tmp_path,
        provider=fake_provider,
    )
    assert len(written) == 1
    assert written[0].suffix == ".parquet"
    assert written[0].exists()


def test_update_daily_bars_refreshes_duckdb_view(tmp_path: Path):
    def fake_provider(symbol: str, start: str, end: str) -> pd.DataFrame:
        del start, end
        return pd.DataFrame(
            [
                {
                    "trade_date": "2026-03-01",
                    "ts_code": symbol,
                    "open": 10.0,
                    "high": 11.0,
                    "low": 9.5,
                    "close": 10.3,
                    "vol": 1234,
                }
            ]
        )

    db_path = tmp_path / "market.duckdb"
    update_daily_bars(
        symbols=["000001.SZ"],
        start="2026-03-01",
        end="2026-03-05",
        warehouse_dir=tmp_path,
        provider=fake_provider,
        db_path=db_path,
    )
    con = duckdb.connect(str(db_path))
    rows = con.execute("select count(*) from daily_bars where symbol='000001.SZ'").fetchone()[0]
    con.close()
    assert rows == 1


def test_update_daily_bars_retries_on_transient_failure(tmp_path: Path):
    state = {"n": 0}

    def flaky_provider(symbol: str, start: str, end: str) -> pd.DataFrame:
        del symbol, start, end
        state["n"] += 1
        if state["n"] == 1:
            raise ConnectionError("transient")
        return pd.DataFrame(
            [
                {
                    "trade_date": "2026-03-01",
                    "ts_code": "000001.SZ",
                    "open": 10.0,
                    "high": 11.0,
                    "low": 9.5,
                    "close": 10.3,
                    "vol": 1234,
                }
            ]
        )

    written = update_daily_bars(
        symbols=["000001.SZ"],
        start="2026-03-01",
        end="2026-03-05",
        warehouse_dir=tmp_path,
        provider=flaky_provider,
        retries=2,
    )
    assert len(written) == 1
    assert state["n"] == 2


def test_update_daily_bars_falls_back_to_secondary_provider(tmp_path: Path):
    def bad_provider(symbol: str, start: str, end: str) -> pd.DataFrame:
        del symbol, start, end
        raise RuntimeError("primary unavailable")

    def fallback_provider(symbol: str, start: str, end: str) -> pd.DataFrame:
        del start, end
        return pd.DataFrame(
            [
                {
                    "trade_date": "2026-03-01",
                    "ts_code": symbol,
                    "open": 10.0,
                    "high": 11.0,
                    "low": 9.5,
                    "close": 10.3,
                    "vol": 1234,
                }
            ]
        )

    written = update_daily_bars(
        symbols=["000001.SZ"],
        start="2026-03-01",
        end="2026-03-05",
        warehouse_dir=tmp_path,
        provider=bad_provider,
        fallback_provider=fallback_provider,
        retries=1,
    )
    assert len(written) == 1
