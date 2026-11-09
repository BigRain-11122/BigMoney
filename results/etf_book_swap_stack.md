# ETF 复合书 · 一张单两段话，一本书

会话 `2026-11-06`｜票 `TICKET-2026-11-06.json`｜上游 `results/etf_book_swap_trigger.json`

**两段合成一笔**：换票在裁剪后手数上重算，整手取整剩下的零头留在现金腿。

## 你到底要下单的是什么（净额单）

| 方向 | 代码 | 价 | 手数 | 金额 | 为什么 |
|---|---|---|---|---|---|
| **SELL** | 159501 | 2.069 | 379 | ¥78,415 | swap 159501 → 159513 (r1466 verdict ACT_ON_THIS_BAR), sized on the trimmed 379 lots |
| **SELL** | 513100 | 2.158 | 364 | ¥78,551 | swap 513100 → 159513 (r1466 verdict WINDOW_ALWAYS_OPEN), sized on the trimmed 364 lots |
| **BUY** | 159513 | 1.705 | 920 | ¥156,860 | merged buy for 159501 + 513100 |

## 换票的钱是照着哪一版账算的（重算）

| 换出腿 | 换到 | 下单手数 | 裁剪后手数 | 占比 | 票面收益 | 裁剪后账面收益 | 高估 |
|---|---|---|---|---|---|---|---|
| 159501 | 159513 | 379 | 379 | 100.0% | ¥5,612 | ¥5,612 | **¥0** |
| 513100 | 159513 | 364 | 364 | 100.0% | ¥4,149 | ¥4,149 | **¥0** |

- 读法：换票面的收益按**下单量**定价，额度裁掉的那一部分不会再交易，所以它的收益也不会发生。合计高估 ¥0——这才是你这张单真能拿到的数。

## 执行完之后这本书长什么样

| 代码 | 手数 | 价 | 金额 | 占风险腿 |
|---|---|---|---|---|
| 159263 | 687 | 1.143 | ¥78,524 | 20.0% |
| 159513 | 920 | 1.705 | ¥156,860 | 40.0% |
| 159577 | 487 | 1.612 | ¥78,504 | 20.0% |
| 513690 | 678 | 1.158 | ¥78,512 | 20.0% |

- 风险腿 ¥392,401（k=0.392401）；额度下限 k=0.393073 → **在额度内**；现金 ¥607,599
- 整手取整零头 ¥106 留在现金腿，不重分配。
- 最宽的一只是 **159513**，占风险腿 **40.0%**：这个数字看着刺眼，但它是把两只同一篮子的票合并的结果——独立篮子数 4 → 4（未变），集中度要用篮子数读，不是票数。

## 不能从这张面读出来的

- the merged name's share is a share of the risk book, not of NAV: it carries the same basket as the two legs it replaced, so the number of independent baskets is printed beside it and is what the concentration reading should use
- swap benefits are re-scaled linearly with notional (the gap face prices them as a percentage of the traded amount); fees, tracking difference and FX-hedge policy between the two tickers are still not priced
- the netted order is lot-rounded at the sibling's close on the priced bar; intraday execution will move both the proceeds and the bought lots

- 出处：`scripts/etf_book_swap_stack.py`；上游 `results/etf_book_swap_trigger.json`（换票面）与票面 permission 块（同一份裁剪算术，不另算一遍）。
