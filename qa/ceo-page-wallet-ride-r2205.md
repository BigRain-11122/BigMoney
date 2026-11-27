# QA · CEO 一页纸 ⑩c「这本书拿到手里，一年是什么感觉」（r2205 bm-c）

日期：2026-11-28 ｜ 轮号：2205 ｜ 机器：bm-c ｜ 表：behavioural + numeric
正身：`docs/live_usage/LIVE-2026-11-28.md` §⑩c ／ `.json` 孪生的 `wallet_ride` 块

## 1. 判据（本司清单）

| # | 判据 | 结果 | 证据 |
|---|---|---|---|
| 1 | CEO 一页纸有这一节，且在 ⑪ 诚实免责之前 | PASS | `LIVE-2026-11-28.md` 章节序 ⑩c < ⑪ |
| 2 | 节内每个数都来自 `results/three_book_wallet_ride.json`（不是手抄） | PASS | 冒烟谓词 `ceo_page_wallet_ride_problems()` = []；负控（hole −0.31）报 `section does not print today's hole 31.00%` |
| 3 | 节自印来源的 generated/cutoff（r1781） | PASS | 页面行：`cutoff 2026-11-26｜generated 2026-11-28T05:27:28+08:00` |
| 4 | 不重复印同一测量（r1911 page_repeat_guard） | PASS | `page_repeat_guard scan` = 4 faces / 0 repeated |
| 5 | 面在页面之后重建时有腿把它拉回来 | PASS | `Tools/probe_ceo_page_wallet_ride.py check` rc0（1158s margin）+ selftest 5/5；链腿 `ceo_page_wallet_ride` 单跑 rc0 0.1s |
| 6 | 页面脚本自检全绿 | PASS | `python scripts/ceo_live_usage.py selftest` = ALL PASS（修红后） |

## 2. 本轮修掉的红（13 条 → 0，全部是「面落后一档」而非代码错）

`ceo_live_usage selftest` 13 条红，根因三处生产者停在旧票面/旧盘口，渲染器按同代闸诚实 withheld：

- `etf_book_capacity_edge` check 自报 `STALE FACE_BEHIND_GATE`（面 11-26 / 闸 11-27）→ 重建 → reading 0.2027%、60/60 过线
- `etf_book_capacity_at_size` SAME_INPUTS no-op → 随上一条同步到 11-27
- `etf_book_premium_choice` check `STALE the ticket moved to 2026-11-27` → 重建 → RULERS_AGREE_SWAP
- `etf_book_premium_leak` 面仍挂在 `TICKET-2026-11-26.json`（其自身 check 只比自己那张票，查不出落后）→ 按最新票面重建 → ENTRY_PREMIUM_SMALL / session_match true

修后：`ceo_live_usage.py selftest` ALL PASS。

## 3. 未做 / 不宣称

- 全量 `python -m smoke_test` 在本轮修复**之前**跑过一轮：761/806 PASS、45 FAIL（880.3s）。这些红多为同一「面代差」族，S6 全链已在本轮启动自愈（逐腿 check→STALE 才重建），**本轮不宣称全绿**——以链实际 rc 为准。
- ⑩c 是 2020-2026 一个窗口的路径形状，不是预测；三本书全部 import 父面，本页零重算。
