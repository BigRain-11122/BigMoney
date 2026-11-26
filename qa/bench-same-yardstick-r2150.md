# QA · 基准与臂同口径（r2150）

轮次 2150 · 机 bm-c · 2026-11-26 · 域=研究/策略（bench 判决面）

## 缺陷

`scripts/bench_generic.py::buy_and_hold()` 把基准的波动目标写死为 0.10，而 census/pair/robust 面上的臂用 `cfg.target_vol`（0.06/0.08）。两本书仓位规模不同，「臂年化 − 基准年化」这个减法在 13 张面上不成立。r2136 用 tv=0.10 的四面做对照组量出该口径差的噪声地板 0.18pp，9 张面 gap 0.64~0.98pp（超地板 3.5~5.4 倍）。

## 修法与证据

| 项 | 判据 | 结果 |
|---|---|---|
| 编译 | `py_compile scripts\bench_generic.py` | rc=0 |
| 单面复跑 | `bench_generic.py --config research\cells\census_commodity.json` | ok，6.5s，基准 4.62→3.80（tv 0.08） |
| 全量复跑 | 17 张 bench_generic 面（`results\_r2150_bench_rerun.py`） | 17/17 无报错 |
| 内建对照 | 本来就 tv=0.10 的四面（AU/IC/RB/SC）基准移动 | −0.05/−0.16/+0.07/+0.03pp，全在 0.18pp 地板内 |
| 审计面重算 | `scripts\bench_go_ruler_audit.py` | `size_mismatch` **9→0**，`n_go=4 / backed=0 / unsupported=4` 不变 |
| 判决书自洽 | `bench_verdict_book.py --verify` | 逐字节重导出 OK（modulo generated） |
| 面字段 | `results/bench_*.json` 新增 `benchmark_sizing` 与每臂 `excess_vs_bench_pp`/`excess_clears_mde` | 13 面已带 |

## GO 面的实际超额（同口径后）

| 臂 | 年化 | 基准 | 超额 | MDE | 过线 |
|---|---|---|---|---|---|
| tsmom 120/21 ls（census_commodity） | 4.99% | 3.80% | 1.19pp | 3.78pp | 否 |
| tsmom 250/21 ls（census_commodity） | 5.19% | 3.80% | 1.39pp | 3.66pp | 否 |
| 120d（robust_tsmom_commodity） | 4.99% | 3.80% | 1.19pp | 3.78pp | 否 |
| 250d（robust_tsmom_commodity） | 5.19% | 3.80% | 1.39pp | 3.66pp | 否 |

## 未做（如实）

1. **判决语义未改**：`verdict_of()` / `crit` 门未动，4 条 GO 仍标 GO，只是旁边多了一列超额与 `(below MDE)` 标注。改成「超额须过 MDE」会影响 21 面 85 臂，属翻案，需单独立案预注册。
2. **全量冒烟未收口**：`python -m smoke_test` 在同一轮以流式方式跑，套件墙钟超过单轮窗口（历史 >10min），本轮报告不宣称套件总数；已改动的 `bench_generic.py` 在面侧逐面实跑 17 次验证，未由冒烟腿覆盖。
3. `bench_verdict_book` 的 96 卡未逐卡复核是否有依赖旧基准年化的叙述句；本轮只核了自洽性（--verify）。
