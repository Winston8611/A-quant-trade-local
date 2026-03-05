# 本地 A 股量化系统（面向新手）

这是一个**完全本地运行**、**不依赖收费软件**的量化交易项目，目标是帮助你完成：

- 日频历史回测（Backtest）
- 日频模拟交易（Paper Trade）
- 本地行情更新与查询（AkShare / BaoStock + DuckDB）

如果你是量化小白，可以把它理解为一条可复用流水线：
**抓数据 -> 存本地 -> 读数据 -> 跑策略 -> 出结果**。

---

## 1. 项目整体功能

- **数据采集**：从免费数据源拉取 A 股日线行情（AkShare / BaoStock）
- **数据存储**：落地为 Parquet，并在 DuckDB 中建立统一视图 `daily_bars`
- **策略驱动**：策略参数独立在 `configs/strategies/*.yaml`，便于切换和维护
- **回测输出**：输出净值曲线与关键指标（如回撤）
- **模拟交易输出**：输出目标持仓（`orders.csv`）
- **测试保障**：通过 pytest 对关键模块做单元测试

---

## 2. 目录结构

```text
quant/
├─ engine/                     # 核心引擎代码
│  ├─ datafeed/                # 数据抓取、标准化、存储、查询
│  ├─ strategy/                # 策略实现 + 策略工厂/注册
│  ├─ portfolio/               # 仓位分配
│  ├─ risk/                    # 风控过滤（如停牌过滤）
│  ├─ execution/               # 交易成本与成交仿真
│  ├─ analytics/               # 指标计算
│  └─ runner/                  # 回测/模拟交易入口
├─ configs/
│  ├─ backtest.yaml            # 回测运行配置
│  ├─ paper_trade.yaml         # 模拟交易运行配置
│  ├─ base.yaml                # 通用参数模板
│  └─ strategies/              # 独立策略配置（推荐只改这里）
├─ scripts/
│  ├─ init_data.py             # 初始化数据目录
│  ├─ daily_update.py          # 更新行情并刷新 DuckDB 视图
│  └─ query_bars.py            # 查询本地行情
├─ tests/                      # 自动化测试
└─ reports/                    # 回测/模拟交易产出
```

---

## 3. 环境与安装

1. 安装依赖
   - `pip install -e .[dev]`
2. 初始化目录
   - `python scripts/init_data.py`

---

## 4. 运行方式

### 4.1 更新本地行情

```bash
python scripts/daily_update.py --source akshare --start 2025-01-01 --end 2025-03-01 --symbols 000001.SZ
```

说明：
- `--source` 支持 `akshare` / `baostock`
- 脚本会写入 `data/warehouse/*.parquet`，并刷新 `data/db/market.duckdb` 中的 `daily_bars` 视图
- 内置重试与备用数据源回退，网络波动时更稳

### 4.2 查询本地行情

```bash
python scripts/query_bars.py --symbols 000001.SZ --start 2025-01-01 --end 2025-01-31 --limit 20
```

### 4.3 运行回测

```bash
python -m engine.runner.run_backtest --config configs/backtest.yaml
```

产出目录：`reports/backtest/`

### 4.4 运行模拟交易

```bash
python -m engine.runner.run_paper_trade --config configs/paper_trade.yaml
```

产出目录：`reports/paper_trade/`

---

## 5. 新手最关心：如何改策略？

你现在只需要改一个地方：`configs/strategies/*.yaml`

例如：
- `configs/strategies/ma_cross.yaml`（均线策略）
- `configs/strategies/momentum.yaml`（动量策略）

再在运行配置里切换：
- `configs/backtest.yaml` 的 `strategy_config`
- `configs/paper_trade.yaml` 的 `strategy_config`

这样你后续更新项目时，策略逻辑与运行配置是解耦的，维护成本更低。

---

## 6. 已内置策略模板

- `ma_cross`：短均线与长均线交叉信号
- `momentum`：按回看窗口计算动量信号

---

## 7. 自检命令

```bash
pytest -q
```

如果测试全部通过，再跑回测/模拟交易，能显著降低改动引入问题的概率。
