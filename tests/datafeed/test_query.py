"""DuckDB 查询层测试。"""

from pathlib import Path

import duckdb

from engine.datafeed.query import load_bars_from_duckdb


def test_load_bars_from_duckdb_filters_symbol_and_date(tmp_path: Path):
    db_path = tmp_path / "market.duckdb"
    con = duckdb.connect(str(db_path))
    con.execute(
        """
        create table daily_bars as
        select * from (
            values
            ('2026-01-01'::date, '000001.SZ', 10.0, 10.0, 10.0, 10.0, 1000.0),
            ('2026-01-02'::date, '000001.SZ', 10.0, 10.5, 9.9, 10.2, 1200.0),
            ('2026-01-02'::date, '000002.SZ', 20.0, 20.5, 19.9, 20.2, 2200.0)
        ) t(date, symbol, open, high, low, close, volume)
        """
    )
    con.close()
    out = load_bars_from_duckdb(db_path, symbols=["000001.SZ"], start="2026-01-02", end="2026-01-03")
    assert len(out) == 1
    assert out.iloc[0]["symbol"] == "000001.SZ"
