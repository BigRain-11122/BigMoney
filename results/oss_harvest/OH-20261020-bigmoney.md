# OH-20261020-bigmoney

- 窗: 2026-10-20（滚动窗；上一件 `cph4/oss-harvest/OH-20261008-bigmoney.md`，超窗 12.3 天，按 D-20261020-12 的 10-21 24:00 大限补办）
- 实体: BigMoney（执行=bm-b r1083 窗；工具=quant/bigmoney `scripts/oss_harvest_probe.py` selftest 20/20）
- 实搜面: GitHub search API 匿名检索 2 条查询（`quantitative trading backtest` / `technical indicators python`，sort=stars desc，各取前 6），共 12 个候选去重后 12 行
- 候选（名称·源URL·许可·契合点）: 见下表
- 采用→落点: akquant → 见下「采用登记」；其余 0 采用
- parked+理由: 见下表判定列（重复 / 许可 / 健康/成本）
- 下窗指针: 下一滚动窗沿用同一 P0（本实体 deadline 面已清）；akquant 适配评估为下一轮候选

## 一 候选与五门判定

| 仓库 | star | 许可 | 判定 | 契合点 |
|---|---|---|---|---|
| akfamily/akquant | 2,444 | MIT | **ADOPT_CANDIDATE** | 研究/策略：A 股原生回测引擎（akshare 同作者），替研究席省回测框架自建与桥接 |
| coding-kitties/investing-algorithm-framework | 2,186 | Apache-2.0 | **ADOPT_CANDIDATE** | 研究/策略：事件驱动投资框架，补策略执行抽象层 |
| fasiondog/hikyuu | 3,566 | Apache-2.0 | PARKED | 225MB C++ 库，超本地包络（成本门） |
| shashankvemuri/Finance | 4,332 | MIT | PARKED | 95MB，超本地包络（成本门） |
| peerchemist/finta | 2,265 | LGPL-3.0 | REJECT_GPL | LGPL 归禁入族（许可门硬拒） |
| VarunS2002/Python-NSE-Option-Chain-Analyzer | 668 | GPL-3.0 | REJECT_GPL | GPL 禁入产品交付链 |
| PyPatel/Options-Trading-Strategies-in-Python | 1,091 | NONE | PARKED | 许可未验（未验不用） |
| femtotrader/pandas_talib | 782 | MIT | DUPLICATE_IN_REPO | 与仓内既有指标面重复（反重复门） |
| 51bitquant/howtrader | 964 | MIT | PARKED | star 未达 1,000 健康线 |
| hummingbot/quants-lab | 300 | Apache-2.0 | PARKED | star 线 + 73.6MB 双门 |
| rsandx/AlphaSuite | 246 | MIT | PARKED | star 线 |
| kylejusticemagnuson/pyti | 667 | MIT | PARKED | star 线 |

计数: ADOPT_CANDIDATE=2 / REJECT_GPL=2 / DUPLICATE_IN_REPO=1 / PARKED_VERIFY_LICENSE=1 / PARKED_HEALTH_OR_COST=6

## 二 采用登记（落点一行律）

- **akfamily/akquant**（2,444★ · MIT · 10.4MB · Python · push 新鲜）——采用=**候选**，落点=①本实体寻源闸判据档（`scripts/oss_harvest_probe.py` 五门机械化，报告 `results/oss_harvest/OH-20261020-bigmoney.json`）②下一轮适配评估（隔离 venv 试装 + 与本仓 `trial_labor_w*` 回测面 API 对位）；**尚未进入生产依赖**，禁据此宣称已采用。契合点=akshare 同作者的 A 股回测引擎，替研究席省框架自建。
- **coding-kitties/investing-algorithm-framework**（2,186★ · Apache-2.0 · 59.7MB）——parked 至下一窗取舍：体积接近本地包络上限，优先级低于 akquant。

## 三 反重复与许可说明

- 反重复三面已查：本仓 `research/OSS_HARVEST_LEDGER.md`（S1..S5/E1..E3 已有 qlib/vnpy/backtrader 等登记，本窗 0 重复命中）、仓内依赖面（akshare/tushare/numpy/pandas/madmom 等 22 项词面）、既有工具清单（`scripts/` 回测引擎族）。
- 许可逐件取 GitHub `spdx_id` 字段；`NONE`/`NOASSERTION` 一律 parked（未验不用）；GPL/AGPL/LGPL 一律禁入。

## 四 机制自证

- 工具可复跑：`python scripts/oss_harvest_probe.py selftest` → `{"selftest":"PASS","legs":20}`；`scan` 每轮 ≤2 次匿名 API 调用、1.2s 间隔（礼貌节流）。
- 本件为 BigMoney 实体第 N 件 OSS 收获件（前序 2026-09-29 / 10-05 / 10-08），deadline 面（D-20261020-12）**本窗关闭**。