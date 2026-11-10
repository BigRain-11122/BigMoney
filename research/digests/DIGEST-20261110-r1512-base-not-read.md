# DIGEST 2026-11-10 r1512 -- 自己写下的行，自己没读

**产品面**：一张订单面里两个「写-读」错位，同轮修掉。

1. `etf_book_positions.next_order_base` 在 accrual 之前解析 → 面把 11-09 的执行行
   （392,587）当起算账，而它自己刚写下的 11-10 估值行（400,023）没人读。
   新增 `account_base_after_accrual()`：accrual 后重解析，标 kind/source +
   superseded_execution_bar。
2. 净额单面只在有换票时刷新，`latest.json` 每定一张票就动 → 安静的一天把
   11-10 的目标书与 11-09 的打印动作对账，印出 **-6,396 「打印行买得更多」**。
   新增 `pin_episode_ticket()`：票钉在净额单面自己声明的那张；钉不住就写出来。

**修后读数**：判词 OVERSELL(-6,396) → REBUILD(0)；票面基座 stale(11-09) → ok(11-10)，
执行账 k=0.397071 vs 引擎 k=0.460253，名义差 ¥63,652 首次进入执行者视野；
本单 k 不变（0.393073，规则 k，r1476 同 bar 结果不作输入）。

**证据**：`scripts/etf_book_positions.py` selftest **71/71** · `check` CHECK_OK ·
`etf_book_order.py --selftest` **148/148** · `etf_book_ceo_page selftest` **194/194** ·
`run` rc0 重写 `results/etf_book_positions.json` / `results/etf_book_order/{TICKET,ORDER}-2026-11-10.*` /
`docs/live_book/LIVE-BOOK-20261110.md`（账本块 11-09 → 11-10）· smoke 新腿
「the next sheet starts from the account as it stands, not its last trade」。
