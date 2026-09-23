# Bigmoney 交接与成果收割指南（HANDOVER）

> 2026-09-23 11:35 整理。用户令：本机暂停自动化开发、转为「回测算力节点」；用户赴另一台机器开发系统；本机回测继续跑，成果随时可取。
> 本文件由循环每 5 轮核对更新一次产物清单（mandate 已写明）。

## 一、当前模式与怎么停/恢复

- **本机在跑什么**：Windows 计划任务 `Bigmoney-IterationLoop`（每 10 分钟一轮，无头静默），当前 mandate=`Tools\iteration_prompt.txt`（回测专用：只推进 research/BACKTEST_PLAN.md 及其派生与维护，不做任何新功能开发）。
- **停止本机循环**：`schtasks /change /tn "\Bigmoney-IterationLoop" /disable`；恢复把 `/disable` 换 `/enable`。只拷文件取数不用停（读文件不冲突）。
- **恢复全自动开发**（用户回本机时）：把 `Tools\iteration_prompt.DEV.txt` 内容拷回 `Tools\iteration_prompt.txt` 即可，其余零改动。
- **跨会话真账本**（任务板 job_list 是会话级的，不作为交接依据）：`logs\iteration-loop\state.json`（轮号/做了什么/下轮指针）＋ `round_reports.md`（每轮固定字段报告）＋ 根目录 `CODELY.md`（项目记忆）。轮活性另看 `logs\probe-heartbeat.txt`。

## 二、成果速览（截至 OS round 15，2026-09-23 12:15）

| 成果 | 位置 | 关键数字（样本外 2025+，×2 成本压力全过） |
|---|---|---|
| P1 策略海选（37 策略+20 随机基线） | `research/strategy_rank.csv`、`results/p1_screen.json`、`research/NULL_CALIBRATION.md` | 零假设基线标定完成（幸存者须超 95 分位） |
| P2 幸存者深化（G2 门） | `results/p2_survivors.json`、`research/G2_DEEPENING.md` | 支线：合并退出软化 `COMBINED_EXIT_SOFTENING.md`、低频族 `LOW_CHURN_FAMILY.md` |
| **幸存者 1：VOLATILITY-CE-01**（ce_c23_trail4） | `firm/traders/VOLATILITY-CE-01.json` | OOS Sharpe **2.0568**（锚点截断复现） |
| **幸存者 2：COMPOSITE-CE-01**（ct_ce_top5） | `firm/traders/COMPOSITE-CE-01.json` | full 0.811 / **OOS 1.609** / 474 笔 / 胜率 0.523 |
| **幸存者 3：COMPOSITE-CE-02**（ct_ce_top8） | `firm/traders/COMPOSITE-CE-02.json` | full 0.610 / **OOS 1.485** / 795 笔（×2 成本余量 +0.031 偏薄=纸盘期盯防对象） |
| CE 迁移实验（预注册范式） | `research/CE_TRANSFER.md`、`results/ce_transfer.json`、`scripts/ce_transfer.py` | 2/2 迁移 PASS，一次定稿 9 跑 |
| **P3 组合验证（round 13）** | `research/portfolio_report.md`、`results/p3_portfolio.json`、`research/p3_portfolio_results.csv` | **EW 组合 validated**：全期 0.9229 / OOS 1.7334 / 回撤 -12.5% / ×2 0.5754 存活；IV 同判稳健；全期平均两两相关 0.36 低档但 OOS 抬至 0.58=盯防点 |
| **J9a 数据池审计（round 14）** | `research/POOL_AUDIT.md`、`results/pool_audit.json`、`research/pool_audit.csv` | unique 1676 对账、前缀池=09-22 一次性快照无续命、孪生 48/48 一致、扩池候选 517（启用前逐只核名） |
| **LFC 低频低成本品种族 mini 海选（round 15）** | `research/LFC_P1_SCREEN.md`、`results/lfc_p1.json`、`research/lfc_p1_results.csv` | **0 员幸存 0 袖珍（诚实判负）**：core5 债金池技能线 1.285=权益池 3 倍；low_vol 全负=成本厚度是资产 carry 刻度的；tsmom/donchian CE 最佳 0.917 未达线；袖珍相关线 0.30 因素材⊂交易员池结构不可达 |
| 纸盘（100 万虚拟本金） | `live/paper.py`、`results/paper/` | 锚定门禁=注册指标与实时重算逐位一致才记账；**2026-10-31 首月到期检查**（months_tracked=1 → `python -m firm.hr` 应自动 PROMOTE→TRAINEE，禁手工改数） |
| 日线数据增量管线 | `scripts/update_daily.py`、`results/update_status.json` | 交易日 15:30 后自动增量 48 池 → paper 自动记账；收盘守卫防半根 bar |
| 旧 432 网格（死信号存档） | `results/*.json`（432 份）、`ranking.csv` | 最好 Sharpe 0.44，已判淘汰，仅供复现 |
| 因子研究 | `results/factor_ic.json`、`composite_ic.json`、`research/FACTOR_RESEARCH.md`、`COMPOSITE_FACTOR.md` | 最强 vol_60 IC=-0.064；复合因子 IC 实测 0.061/0.023（95% 满仓口径） |
| **试验账本累计 N=872**（432+30+59+122+27+26+12+9+10+145） | 各批 results/*.json 的 trials_ledger 累计链 | 多重检验可追溯；面板「策略簿」实时显示 |

## 三、取数清单（两条路径）

1. **轻装收割（~105MB，推荐）**：整个 `Bigmoney\` 文件夹**排除 `Money02\`**——引擎+策略+数据（92MB）+全部成果（11.5MB）+研究文档+日志证据全在内。
2. **全量（~7.8GB）**：另含 `Money02\`（前代 A 股系统资产库：5221 只个股全史 parquet+复权因子、19 年龙虎榜、Gate.io 26 币全史，清单=`research/MONEY02_ASSETS.md`）。新机器只做 ETF 波段则不需要它。

## 四、新机器跑起来（PLAN.md 可拷贝迁移原则）

```powershell
# 1. 取项目：**铁律=git clone（禁文件夹直接复制**——防携带锁文件/临时态；Biggame 08号传输铁律同源）
#    git clone git@github.com:BigRain-11122/bigmoney.git
#    （Money02/、logs/、.codely-cli/、fleet/machine.json 为各机局部，clone 不含、也禁手拷）
#    新机器接入 5 步与机队协议（身份/心跳/任务认领/借算/写域）= fleet\README.md
# 2. 一条命令自举：依赖自装（清华镜像回退）→ 20 项自检 → 总控数据生成
python bootstrap.py
# 3. 打开总控（读真实数据，双击可开）
start bigmoney.html
# 4. （可选，Windows）装 10 分钟 AI 自迭代循环——路径自适应，零改动
powershell -NoProfile -ExecutionPolicy Bypass -File Tools\register_loop_task.ps1
# 5. 可选：复现关键实验
python scripts\ce_transfer.py     # CE 迁移（含 ×2 成本压力）
python -m screening.rank          # 432 组排名重建
```

- 机器要求：Python 3.10+（3.11 实测）；AI 循环需装 **Codely CLI 并登录**（循环用 `codely -y -p` 无头模式）；GPU 非必需（回测=CPU 任务，GPU 启用条件见 `research/BACKTEST_PLAN.md` §四）。
- **git 同步（并行开发唯一通道）**：远端已预设 = `git@github.com:BigRain-11122/bigmoney.git`（SSH/Clash 链路实测认证通过）。**唯一待办：在 GitHub 建空私库 `BigRain-11122/bigmoney`（不勾选任何初始化文件）**——建好后循环下一轮（≤10 分钟）自动 push 接上；此后本机每批成果在任何机器 `git pull` 即得。主分支=main，并行开发协议=PLAN.md §8（节点侧遇冲突只读避让）。
- 规则与记忆随仓库走：`PLAN.md`（契约+接手清单 §6）、根 `CODELY.md`（项目记忆）、`Tools/iteration_prompt.txt`（循环 mandate）——任何机器上的任何 AI 会话打开本项目即自动继承全部规则。

## 五、文件格式速查

- `results/<hash>.json`：`{hash, status, params, metrics{annual_return, sharpe, max_drawdown, win_rate, profit_factor, num_trades, avg_hold_days}, n_trades, equity_curve[], elapsed_sec}`
- `results/p1_screen.json` / `p2_survivors.json` / `p2_calibration.json`：海选/深化明细（含 OOS 指标与门禁判定）
- `results/paper/<交易员>_paper.json`：纸盘账本（bars/trades/months_tracked/equity）
- `results/update_status.json`：数据增量状态（per-symbol appended / data_cutoff）
- `research/*.csv`：`strategy_rank`（海选全表）、`p2_deepening`、`ce_transfer_results`、`combined_exit_results`、`lowchurn_results`、`p3_portfolio_results`、`pool_audit`(1676 行)、`lfc_p1_results`
- `bigmoney.html` ← `results/dashboard_status.js`（`python -m monitor.build_status` 刷新；门禁链 7 步数据驱动、试验账本 N 实时聚合）

## 六、本机将持续产出什么（你回来取时会有更多）

- 每个交易日 15:30 后：48 池日线增量 → 纸盘自动记账 → 成果/面板文件刷新（查 `results/update_status.json` 的 data_cutoff 与 total_new_rows）。
- 回测计划内现状：P1/P2/P3 与 J14/J15/J19 迁移、J9a 审计、LFC 品族 mini 海选**均已闭环**（P3 组合 validated、LFC 0 员诚实判负）；策略线续作候选（须另开预注册）：货币现金腿（exit-to-asset 引擎特性+511880/511990 池外零相关素材）或新信号设计；扩素材启用前逐只核名。
- 长线自动检查：2026-10-31 三员首月到期（months_tracked 应=1、`python -m firm.hr` 应 PROMOTE→TRAINEE，禁手工改数）；盯防 COMPOSITE-CE-02 ×2 薄余量与组合 OOS 相关抬升。
- 不会做（等你回来定）：总控 v2 公司小镇、本地 LLM 助理、dashboard.html 改造、数据源扩容等一切新功能。

## 七、诚实声明

- 所有样本外指标为 2025-2026 盲测窗、成本恒开、一次定稿跑数（预注册范式）；试验总数 N 已入档（多重检验可追溯）。
- 纸盘尚未有真实成交 bars（等待 15:30 后新交易日数据落账）；`dashboard_status.json` 的 trading.paper_started 由数据驱动，非写死。
- 3 名交易员均为 INTERN 级注册，晋升只走 `python -m firm.hr` 自动评审（2026-10-31 首查）。
