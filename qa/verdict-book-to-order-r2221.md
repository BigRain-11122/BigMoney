# QA — 判决簿「离下单还差什么」（r2221 bm-c）

问题：一页判词里 4 个「还活着的结论」只印判词，不印障碍；两张基差卡的数字列整排是「-」，
两张商品卡的行写 GO 而其证据面写着 CENSUS_LEANS_POSITIVE / UNSTABLE_ACROSS_PARAMS。

## 做了什么

1. `text` 层回退：`headline_of()` 在没有 arms / 顶层数字时读 `products[P].weighted`，
   按 `PRODUCT_ALIASES` 映射（carry_ann_pct→ann_pct、carry_mdd_pct→mdd_pct、
   difference_pp→excess_pp）。基差两行因此印出 10.16% / -1.89%。
2. 新增 `to_order_blockers()` 与 `TO_ORDER_FACES`：逐卡从**各自的证据面**取障碍，
   不在本脚本里重算任何数。
3. `_input_stamps()` 收进外部面的内容摘要 → 外部面动了说 STALE，算错了才说 FAILED。
4. 页面新增「## 离下单还差什么（每个活结论一行）」。

## 验收证据

| 项 | 命令 | 结果 |
|---|---|---|
| 自检 | `python scripts/bench_verdict_book.py --check` | **26/26 PASS**（20 旧 + 6 新） |
| 重出 | `python scripts/bench_verdict_book.py` | 96 行判词 / 6 候选 / 33 来源 |
| 漂移 | `python scripts/bench_verdict_book.py --verify` | **OK**（re-derives byte-for-byte） |
| 链腿 | `python Tools/s6_chain_bmc.py 2221 --only=bench_verdict_book` | **1/1 rc0** |
| 页面对照 | `research/BENCH-VERDICT-BOOK.md` §离下单还差什么 | 4 卡 12 行，每行带面路径与时点 |

新增 6 条行为腿：

- 面自己撤回了 GO（UNSTABLE_ACROSS_PARAMS）→ 必须点名，不许只印 GO；
- 没人量过的族必须印「未测」，不许印 0；
- 资本面不在盘上必须点名「没读到」；
- 资本线带差额与票面状态（￥159,599 / 15.96% / WITHDRAWN）；
- 面与行同向时不得误报冲突（负控）；
- 外部面摘要移动 → STALE（不是 CHECK FAILED）。

## 印出来的结论（2026-11-28）

- basis_timing_size / basis_timing_perm：脸判 GO / SIGNIFICANT；资本线 IC 差 ￥159,599（15.96%）、
  IM 差 ￥169,997（17.00%），可执行票 WITHDRAWN；容量 4321.8× 本书——**卡在钱，不在容量**。
- census_commodity：脸判 CENSUS_LEANS_POSITIVE，容量未测。
- robust_tsmom_commodity：脸判 UNSTABLE_ACROSS_PARAMS（60/120/250 三窗不稳定），容量未测。

## 未做

- 商品 TSMOM 的容量/冲击面仍不存在（本轮如实印「未测」）。
- 全量冒烟（~850s）未跑；本轮以判决簿 selftest 26/26、链腿 rc0、CEO 页自检 ALL PASS 为证。
- r2220 遗留的 NAV 口径披露（跨境基金 76% 历史行用前一场净值）本轮验证后入库，
  但未新增冒烟腿覆盖它——它已由 CEO 页自检的 r2220 腿覆盖。
