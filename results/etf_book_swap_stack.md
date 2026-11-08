# ETF 复合书 · 一张单两段话，一本书

会话 `2026-11-06`｜票 `TICKET-2026-11-06.json`｜上游 `results/etf_book_swap_trigger.json`

**这张单两段话卖同一只票**：额度表卖一部分、换票线卖整只腿，两段相加超过账面手数。按顺序执行（先裁后换）是对的，但纸面没说顺序，照着两段一起下单就是超卖。

## 你到底要下单的是什么（净额单）

| 方向 | 代码 | 价 | 手数 | 金额 | 为什么 |
|---|---|---|---|---|---|
| **SELL** | 159501 | 2.069 | 379 | ¥78,415 | swap 159501 → 159513 (r1466 verdict ACT_ON_THIS_BAR), sized on the trimmed 379 lots |
| **SELL** | 513100 | 2.158 | 364 | ¥78,551 | swap 513100 → 159513 (r1466 verdict WINDOW_ALWAYS_OPEN), sized on the trimmed 364 lots |
| **BUY** | 159513 | 1.705 | 920 | ¥156,860 | merged buy for 159501 + 513100 |

## 两段话卖同一只票，加到多少

| 代码 | 账面手数 | 额度表卖 | 换票线卖 | 两段相加 | 照两段下单会多卖 |
|---|---|---|---|---|---|
| 159263 | 805 | 118 | — | — | —（这只腿只有额度表卖，与换票无关） |
| 159501 | 444 | 65 | 444 | 509 | **+65 手** |
| 159577 | 571 | 84 | — | — | —（这只腿只有额度表卖，与换票无关） |
| 513100 | 426 | 62 | 426 | 488 | **+62 手** |
| 513690 | 794 | 116 | — | — | —（这只腿只有额度表卖，与换票无关） |

- 读法：额度表的「卖出手数」是按**裁剪后**的账算的，换票线的金额是按**未裁剪**的账算的；两张纸各说各的，谁也没错，但一起念就是超卖。顺序只有一种：先按额度裁，再拿剩下的整只腿去换。

## 换票的钱是照着哪一版账算的（重算）

| 换出腿 | 换到 | 下单手数 | 裁剪后手数 | 占比 | 票面收益 | 裁剪后账面收益 | 高估 |
|---|---|---|---|---|---|---|---|
| 159501 | 159513 | 444 | 379 | 85.4% | ¥5,612 | ¥4,791 | **¥822** |
| 513100 | 159513 | 426 | 364 | 85.5% | ¥4,149 | ¥3,545 | **¥604** |

- 读法：换票面的收益按**下单量**定价，额度裁掉的那一部分不会再交易，所以它的收益也不会发生。合计高估 ¥1,426——这才是你这张单真能拿到的数。

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
