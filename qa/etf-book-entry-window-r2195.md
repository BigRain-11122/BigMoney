# 验收：ETF 书入场窗口分布面（r2195 · bm-c）

日期 2026-11-28 00:5x · 宿主 bm-c · 竞争窗（`repo_write_contention` rc=3 CONTENTION）

## 本轮新增件

| 件 | 路径 | 状态 |
|---|---|---|
| 脚本 | `scripts/etf_book_entry_window_yield.py` | 新建 · selftest 13 腿 · check rc0 |
| 证据面 | `results/etf_book_entry_window_yield.json` | 新建 · cutoff 2026-11-27 |
| 读者面 | `research/ETF_BOOK_ENTRY_WINDOW_YIELD.md` | 新建 |
| 本文件 | `qa/etf-book-entry-window-r2195.md` | 新建 |

未改动任何既有面（本轮 CONTENTION，禁改共享面）。

## 验收项

| 项 | 判据 | 实况 |
|---|---|---|
| 自检 | 离线算术 13 腿 | `selftest ok (13 legs)` rc0 |
| 外部锚检查 | 面 cutoff 必须等于 `data/daily/sh510300.csv` 尾 bar | `check ok: cutoff=2026-11-27 arms=2` rc0 |
| 行为腿（假的绿） | 手工把面 cutoff 改一格，check 必须报 STALE 且 rc≠0 | `check FAIL: STALE: face cutoff 2026-11-26 != panel last bar 2026-11-27` rc1 |
| 行为腿（复原） | 还原后必须回绿 | `check ok: cutoff=2026-11-27 arms=2` rc0 |
| 判词可派生 | headline 与 dial 判词必须由自身分布算出，不是手写 | `spread_over_median_x=3.56` → `THE_DAY_YOU_START_MOVES_THE_ANSWER_MORE_THAN_THE_STRATEGY_DOES`；回撤中位 +3.89pp 且收益中位 −1.77pp → `THE_DIAL_BUYS_THE_PATH_NOT_THE_YIELD` |
| 重叠样本的诚实 | 必须并列印不重叠整年块，且不作 p 值 | 面内 `independent_full_years` 六块 + `not_measured` 首条 |
| 最差起点不许读成散点 | 必须印最差十分位的起始月份分布 | `worst_decile_start_months`：2021-09=20 / 2021-05=18 / 2021-04=16 / 2020-07=16 / 2021-10=14 |
| 不重实现 | 面板/打分/执行/统计全部 import 既有模块 | 与 `etf_nobond_vt.py` 同一调用链（`E.build_panel` / `A.repair_flips` / `E.build_score` / `R.open_to_open_equity` / `A.stats2`） |

## 关键读数（备查）

- vt08：1420 个起点，中位 9.08% / p10 1.41% / p90 33.75% / 最差 −6.62% / 亏钱起点 5.6% / 路径回撤中位 −6.71%
- base：中位 10.85% / p10 1.28% / p90 42.46% / 最差 −7.19% / 路径回撤中位 −10.60%
- 波动目标代价：收益中位 −1.77pp，路径回撤中位 +3.89pp、最深 +6.12pp
- 最近一整年（2025-11-13 → 2026-11-27）vt08：**−0.28%**

## 未做（如实）

1. **链腿未接**：`Tools/s6_chain_bmc.py` 属共享面，本轮 CONTENTION 禁改（r1282 孤儿类风险 —— 下一无竞争轮补一条 (check, run) 对腿）。
2. **冒烟腿未接**：`smoke_test.py` 同上。
3. **CEO 一页纸小节未接**：`scripts/ceo_live_usage.py` + 页面属共享面（r1782 要求产品落在读者那一页），下一无竞争轮补。
4. 转债书与 carry 臂没有上这把尺子（面内 `not_measured` 已声明）。

## 竞争窗证据

`results/_repo_write_contention.bm-c.json`：verdict=CONTENTION，rc=3，对端 pid 30500（interactive，2026-11-27T21:54:41 起），本轮开始后重叠写入 0。
