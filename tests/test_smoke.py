"""冒烟测试：检查关键配置文件是否可读取。"""

from pathlib import Path

import yaml


def test_backtest_config_loadable():
    cfg = yaml.safe_load(Path("configs/backtest.yaml").read_text())
    assert cfg["market"] == "CN_A_SHARE"
