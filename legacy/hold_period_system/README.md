# hold_period_system

多策略分布式回测 / 实盘共用的**持仓周期顶层铁律**模块。
纯 Python 标准库，零第三方依赖，整包复制即可在主控机器上运行。

---

## 一、规则速查（焊死的优先级链）

每日收盘按顺序判定，**先命中先执行**：

| 优先级 | 触发条件 | 动作 |
|---|---|---|
| P1 | 全局市场熔断（外部置位） | 全仓清仓 |
| P2 | 个股 `pnl_rate <= -8%` | 立即清仓 |
| P3 | 动态时间：浮亏持仓满 8 天 / 浮盈持仓满 15 天 | 时间平仓 |
| P4 | 全局硬天花板：持仓满 15 天 | 强制平仓（兜底） |
| — | 以上都不命中 | 继续持有 |

核心数值（`config/default_config.py`）：

```
global_hard_limit_days = 15
max_hold_days_loss     = 8
max_hold_days_profit  = 15
stop_loss_rate         = -0.08
```

---

## 二、目录结构

```
hold_period_system/
├── config/
│   └── default_config.py     # 所有可调参数（dataclass）
├── core/
│   ├── enums.py              # ExitReason / PnlState
│   ├── position_state.py     # 持仓快照数据结构
│   ├── time_manager.py       # 动态 max_hold 计算
│   ├── risk_rules.py         # 优先级链 evaluate_position()
│   └── evaluator.py          # DailyEvaluator：每日收盘统一入口
├── adapters/
│   ├── backtest_adapter.py   # 回测：吃 bar feed，吐 trade log
│   └── live_adapter.py       # 实盘：接 broker 回调
├── examples/
│   ├── demo_backtest.py      # 端到端回测示例
│   └── demo_live.py          # 实盘接线示例
├── tests/                    # 14 个单元测试
├── run_tests.py              # 零依赖测试运行器
└── requirements.txt          # （空，纯标准库）
```

---

## 三、快速开始

### 1. 跑测试

```
cd hold_period_system
python run_tests.py
```

预期：`14 passed, 0 failed, 0 errors`。

### 2. 跑回测 demo

```
python examples/demo_backtest.py
```

输出（三种典型场景）：

```
2026-01-08  LOSS_STOP   individual_stop_loss   -8.40%   7   <- P2 止损
2026-01-09  LOSS_TIME   dynamic_time_exit      -1.60%   8   <- P3 亏损 8 天
2026-01-16  PROFIT_RUN  dynamic_time_exit     +15.00%  15   <- P3 盈利 15 天
```

### 3. 实盘接线

```python
from adapters import LiveHoldingGuard
from config import HoldPeriodConfig
from core import PositionState, CloseCommand

guard = LiveHoldingGuard(cfg=HoldPeriodConfig())
guard.set_providers(
    positions_provider=lambda: my_broker.get_positions_as_state(),
    close_executor=lambda cmd: my_broker.sell(cmd.symbol, cmd.quantity),
)

# 每个交易日收盘调用一次
guard.on_daily_close(market_circuit_break=False)
```

---

## 四、迁移到主控机器（关键）

本模块**自包含、无外部依赖**，迁移步骤：

1. 整包复制 `hold_period_system/` 整个文件夹到主控机器任意路径。
2. 主控机器上只需 Python 3.8+，**不需要 pip install 任何东西**。
3. 在主控项目里把该目录加入 `sys.path`，或直接把它作为子目录：
   ```python
   import sys, os
   sys.path.insert(0, "/path/to/hold_period_system")
   from adapters import run_backtest, LiveHoldingGuard
   from config import HoldPeriodConfig
   ```
4. 回测和实盘**共用同一份 `core/` 代码**，不会出现"回测好看实盘拉胯"的规则漂移。

---

## 五、分布式参数迭代接口

`HoldPeriodConfig` 是一个 frozen dataclass，所有字段都是数值，可直接喂给分布式进化器做网格 / 贝叶斯搜索：

```python
from config import HoldPeriodConfig

for loss_days in [5, 6, 7, 8, 9, 10]:
    for profit_days in [10, 12, 15, 18]:
        for sl in [-0.05, -0.07, -0.08, -0.10]:
            cfg = HoldPeriodConfig(
                max_hold_days_loss=loss_days,
                max_hold_days_profit=profit_days,
                stop_loss_rate=sl,
                global_hard_limit_days=15,   # 焊死，不参与迭代
            )
            # 传给 run_backtest(..., cfg=cfg)
```

`global_hard_limit_days=15` 是顶层铁律，**不建议参与迭代**，否则策略会漂移成长线。

---

## 六、多策略并行接入

每个策略只需要：

1. 自己维护入场信号和仓位大小。
2. 把当前持仓包装成 `core.PositionState`（必填：`symbol / strategy_id / cost_price / current_price / hold_days / quantity`）。
3. 每个交易日收盘把所有策略的持仓合并成一个 `Dict[symbol, PositionState]`，丢给 `DailyEvaluator.evaluate()`。
4. 平仓命令统一走同一个 `close_executor`，日志里带 `strategy_id` 即可归因。

所有策略共用同一套时间规则，风格统一在 3–15 天短波段。

---

## 七、设计约束（不要破坏）

- `hold_days` 在**收盘评估之后**再 `+1`，保证"满 N 根 K 线平仓"语义正确。
- 优先级顺序写死在 `core/risk_rules.py::evaluate_position`，不要调换。
- `ExitReason` 是 closed enum，新增平仓原因时追加，不要改已有字符串值（影响历史日志归因）。
- 代码内注释与字符串均为英文，避免跨机器编码乱码。
