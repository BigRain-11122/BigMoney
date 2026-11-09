# ETF 复合书 · 一张单两段话，一本书

会话 `2026-11-09`｜票 `TICKET-2026-11-09.json`｜上游 `results/etf_book_swap_trigger.json`

**两段合成一笔**：换票在裁剪后手数上重算，整手取整剩下的零头留在现金腿。

## 你到底要下单的是什么（净额单）

| 方向 | 代码 | 价 | 手数 | 金额 | 为什么 |
|---|---|---|---|---|---|
| **SELL** | 159501 | 2.055 | 382 | ¥78,501 | swap 159501 → 159513 (r1466 verdict ACT_ON_THIS_BAR), sized on the trimmed 382 lots |
| **SELL** | 513100 | 2.142 | 367 | ¥78,611 | swap 513100 → 159513 (r1466 verdict WINDOW_ALWAYS_OPEN), sized on the trimmed 367 lots |

## 换票的钱是照着哪一版账算的（重算）

| 换出腿 | 换到 | 下单手数 | 裁剪后手数 | 占比 | 票面收益 | 裁剪后账面收益 | 高估 |
|---|---|---|---|---|---|---|---|
| 159501 | 159513 | 382 | 382 | 100.0% | ¥5,612 | ¥5,612 | **¥0** |
| 513100 | 159513 | 367 | 367 | 100.0% | ¥4,149 | ¥4,149 | **¥0** |

- 读法：换票面的收益按**下单量**定价，额度裁掉的那一部分不会再交易，所以它的收益也不会发生。合计高估 ¥0——这才是你这张单真能拿到的数。

## 执行完之后这本书长什么样

| 代码 | 手数 | 价 | 金额 | 占风险腿 |
|---|---|---|---|---|
| 159263 | 690 | 1.138 | ¥78,522 | 33.3% |
| 159577 | 487 | 1.612 | ¥78,504 | 33.3% |
| 513690 | 674 | 1.166 | ¥78,588 | 33.4% |

- 风险腿 ¥235,615（k=0.235615）；额度下限 k=0.393073 → **在额度内**；现金 ¥764,385
- 整手取整零头 ¥157,112 留在现金腿，不重分配。
- 最宽的一只是 **513690**，占风险腿 **33.4%**：这个数字看着刺眼，但它是把两只同一篮子的票合并的结果——独立篮子数 4 → 3（变了），集中度要用篮子数读，不是票数。

## 读这张面时要知道的

- 159513：没有同 bar 的收盘价，卖出款留在现金腿（不按旧价买）

- 没有同 bar 收盘价的兄弟票：159513（sibling panel ends at 2026-11-06, ticket is priced at 2026-11-09）

## 不能从这张面读出来的

- the merged name's share is a share of the risk book, not of NAV: it carries the same basket as the two legs it replaced, so the number of independent baskets is printed beside it and is what the concentration reading should use
- swap benefits are re-scaled linearly with notional (the gap face prices them as a percentage of the traded amount); fees, tracking difference and FX-hedge policy between the two tickers are still not priced
- the netted order is lot-rounded at the sibling's close on the priced bar; intraday execution will move both the proceeds and the bought lots

- 出处：`scripts/etf_book_swap_stack.py`；上游 `results/etf_book_swap_trigger.json`（换票面）与票面 permission 块（同一份裁剪算术，不另算一遍）。
