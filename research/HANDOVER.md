# Bigmoney 交接与成果收割指南（HANDOVER）

> 2026-09-23 11:35 整理。用户令：本机暂停自动化开发、转为「回测算力节点」；用户赴另一台机器开发系统；本机回测继续跑，成果随时可取。
> 本文件由循环每 5 轮核对更新一次产物清单（mandate 已写明）。

## 一、当前模式与怎么停/恢复

- **本机在跑什么**：Windows 计划任务 `Bigmoney-IterationLoop`（每 10 分钟一轮，无头静默），当前 mandate=`Tools\iteration_prompt.txt`（回测专用：只推进 research/BACKTEST_PLAN.md 及其派生与维护，不做任何新功能开发）。
- **停止本机循环**：`schtasks /change /tn "\Bigmoney-IterationLoop" /disable`；恢复把 `/disable` 换 `/enable`。只拷文件取数不用停（读文件不冲突）。
- **恢复全自动开发**（用户回本机时）：把 `Tools\iteration_prompt.DEV.txt` 内容拷回 `Tools\iteration_prompt.txt` 即可，其余零改动。
- **跨会话真账本**（任务板 job_list 是会话级的，不作为交接依据）：`logs\iteration-loop\state.json`（轮号/做了什么/下轮指针）＋ `round_reports.md`（每轮固定字段报告）＋ 根目录 `CODELY.md`（项目记忆）。轮活性另看 `logs\probe-heartbeat.txt`。

## 二、成果速览（截至 OS round 12，2026-09-23 11:27）

| 成果 | 位置 | 关键数字（样本外 2025+，×2 成本压力全过） |
|---|---|---|
| P1 策略海选（37 策略+20 随机基线） | `research/strategy_rank.csv`、`results/p1_screen.json`、`research/NULL_CALIBRATION.md` | 零假设基线标定完成（幸存者须超 95 分位） |
| P2 幸存者深化（G2 门） | `results/p2_survivors.json`、`research/G2_DEEPENING.md` | 支线：合并退出软化 `COMBINED_EXIT_SOFTENING.md`、低频族 `LOW_CHURN_FAMILY.md` |
| **幸存者 1：VOLATILITY-CE-01**（ce_c23_trail4） | `firm/traders/VOLATILITY-CE-01.json` | OOS Sharpe **2.0568**（锚点截断复现） |
| **幸存者 2：COMPOSITE-CE-01**（ct_ce_top5） | `firm/traders/COMPOSITE-CE-01.json` | full 0.811 / **OOS 1.609** / 474 笔 / 胜率 0.523 |
| **幸存者 3：COMPOSITE-CE-02**（ct_ce_top8） | `firm/traders/COMPOSITE-CE-02.json` | full 0.610 / **OOS 1.485** / 795 笔（×2 成本余量 +0.031 偏薄=纸盘期盯防对象） |
| CE 迁移实验（预注册范式） | `research/CE_TRANSFER.md`、`results/ce_transfer.json`、`scripts/ce_transfer.py` | 2/2 迁移 PASS，一次定稿 9 跑，试验总数 N=717 入档 |
| 纸盘（100 万虚拟本金） | `live/paper.py`、`results/paper/` | 锚定门禁=注册指标与实时重算逐位一致才记账；**2026-10-31 首月到期检查**（months_tracked=1 → `python -m firm.hr` 应自动 PROMOTE→TRAINEE，禁手工改数） |
| 日线数据增量管线 | `scripts/update_daily.py`、`results/update_status.json` | 交易日 15:30 后自动增量 48 池 → paper 自动记账；收盘守卫防半根 bar |
| 旧 432 网格（死信号存档） | `results/*.json`（432 份）、`ranking.csv` | 最好 Sharpe 0.44，已判淘汰，仅供复现 |
| 因子研究 | `results/factor_ic.json`、`composite_ic.json`、`research/FACTOR_RESEARCH.md`、`COMPOSITE_FACTOR.md` | 最强 vol_60 IC=-0.064；复合因子 IC 实测 0.061/0.023（95% 满仓口径） |

## 三、取数清单（两条路径）

1. **轻装收割（~105MB，推荐）**：整个 `Bigmoney\` 文件夹**排除 `Money02\`**——引擎+策略+数据（92MB）+全部成果（11.5MB）+研究文档+日志证据全在内。
2. **全量（~7.8GB）**：另含 `Money02\`（前代 A 股系统资产库：5221 只个股全史 parquet+复权因子、19 年龙虎榜、Gate.io 26 币全史，清单=`research/MONEY02_ASSETS.md`）。新机器只做 ETF 波段则不需要它。

## 四、新机器跑起来（PLAN.md 可拷贝迁移原则）

```powershell
# 1. 拷贝 Bigmoney/（轻装版）
# 2. Python 3.11+ 装依赖
python -m pip install -r requirements.txt
# 3. 一键自检（应 20/20 全绿）
python -m smoke_test
# 4. 刷总控数据并打开面板（读真实数据，双击可开）
python -m monitor.build_status
start bigmoney.html
# 5. 可选：复现关键实验
python scripts\ce_transfer.py     # CE 迁移（含 ×2 成本压力）
python -m screening.rank          # 432 组排名重建
```

注意：代码全用相对项目根路径；`Tools\register_loop_task.ps1` 内含本机绝对路径，新机器要用循环须先改路径再跑；`logs\` 下截图与轮日志为证据存档，可不带。

## 五、文件格式速查

- `results/<hash>.json`：`{hash, status, params, metrics{annual_return, sharpe, max_drawdown, win_rate, profit_factor, num_trades, avg_hold_days}, n_trades, equity_curve[], elapsed_sec}`
- `results/p1_screen.json` / `p2_survivors.json` / `p2_calibration.json`：海选/深化明细（含 OOS 指标与门禁判定）
- `results/paper/<交易员>_paper.json`：纸盘账本（bars/trades/months_tracked/equity）
- `results/update_status.json`：数据增量状态（per-symbol appended / data_cutoff）
- `research/*.csv`：`strategy_rank`（海选全表）、`p2_deepening`、`ce_transfer_results`、`combined_exit_results`、`lowchurn_results`
- `bigmoney.html` ← `results/dashboard_status.js`（`python -m monitor.build_status` 刷新）

## 六、本机将持续产出什么（你回来取时会有更多）

- 每个交易日 15:30 后：48 池日线增量 → 纸盘自动记账 → 成果/面板文件刷新（查 `results/update_status.json` 的 data_cutoff 与 total_new_rows）。
- 回测计划内剩余：P3 组合验证（3 员相关性/风险预算/合并回测）、低频族支线深化（`research/LOW_CHURN_FAMILY.md`）。
- 不会做（等你回来定）：总控 v2 公司小镇、本地 LLM 助理、dashboard.html 改造、数据源扩容等一切新功能。

## 七、诚实声明

- 所有样本外指标为 2025-2026 盲测窗、成本恒开、一次定稿跑数（预注册范式）；试验总数 N 已入档（多重检验可追溯）。
- 纸盘尚未有真实成交 bars（等待 15:30 后新交易日数据落账）；`dashboard_status.json` 的 trading.paper_started 由数据驱动，非写死。
- 3 名交易员均为 INTERN 级注册，晋升只走 `python -m firm.hr` 自动评审（2026-10-31 首查）。
