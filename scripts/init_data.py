from __future__ import annotations

"""初始化本地目录结构。

首次拉取数据前建议先运行本脚本。
"""

from pathlib import Path


def main() -> None:
    # 原始数据、标准仓库、数据库和报告目录。
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    Path("data/warehouse").mkdir(parents=True, exist_ok=True)
    Path("data/db").mkdir(parents=True, exist_ok=True)
    Path("reports").mkdir(parents=True, exist_ok=True)
    print("Initialized local data/report directories.")
    print("Next: python scripts/daily_update.py")


if __name__ == "__main__":
    main()
