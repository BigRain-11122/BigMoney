# ETF 复合书 · 一张单两段话，一本书

会话 `2026-11-13`｜票 `TICKET-2026-11-13.json`｜上游 `results/etf_book_swap_trigger.json`

**今天没有要合并的动作**：换票面没有 actionable 的对，本单只有额度裁剪。

## 执行完之后这本书长什么样

| 代码 | 手数 | 价 | 金额 | 占风险腿 |
|---|---|---|---|---|
| 159519 | 496 | 1.741 | ¥86,354 | 20.0% |
| 159655 | 431 | 2.004 | ¥86,372 | 20.0% |
| 510760 | 684 | 1.263 | ¥86,389 | 20.0% |
| 512040 | 726 | 1.189 | ¥86,321 | 20.0% |
| 513690 | 754 | 1.145 | ¥86,333 | 20.0% |

- 风险腿 ¥431,770（k=0.431770）；额度下限 k=0.432195 → **在额度内**；现金 ¥568,230
- 整手取整零头 ¥0 留在现金腿，不重分配。
- 最宽的一只是 **510760**，占风险腿 **20.0%**：这个数字看着刺眼，但它是把两只同一篮子的票合并的结果——独立篮子数 5 → 5（未变），集中度要用篮子数读，不是票数。

## 不能从这张面读出来的

- the merged name's share is a share of the risk book, not of NAV: it carries the same basket as the two legs it replaced, so the number of independent baskets is printed beside it and is what the concentration reading should use
- swap benefits are re-scaled linearly with notional (the gap face prices them as a percentage of the traded amount); fees, tracking difference and FX-hedge policy between the two tickers are still not priced
- the netted order is lot-rounded at the sibling's close on the priced bar; intraday execution will move both the proceeds and the bought lots

- 出处：`scripts/etf_book_swap_stack.py`；上游 `results/etf_book_swap_trigger.json`（换票面）与票面 permission 块（同一份裁剪算术，不另算一遍）。
