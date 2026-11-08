# The size the permission refuses vs the size the desk orders

- 判定：**ORDER_EXCEEDS_PERMISSION_NOBODY_READS_IT**
- 决策日：2026-11-11 ｜ 票据：TICKET-2026-11-06.json ｜ 证据截止：2026-11-06

## 一句话

the ticket path will order k=0.460253 (CNY 459,796) on 2026-11-11 while the permission allows 0.393073 (CNY 392,616): CNY 67,180 (6.72pp) is refused on paper and NO module reads the permission receipt, so nothing in the order path will trim it

## 两侧的数

| 读数 | k | 风险腿金额 CNY |
|---|---|---|
| 票据将下单 | 0.460253 | 459,796 |
| 权限允许 | 0.393073 | 392,616 |
| 差额 | 0.067180（6.72pp） | 67,180 |

## 逐腿削减（the 11-06 pick set; the 11-11 decision bar re-derives the names, so these rows are illustrative while the sleeve total is exact）

| 代码 | 价 | 现手数 | 目标手数 | 卖出手数 | 卖出 CNY |
|---|---|---|---|---|---|
| 159501 | 2.069 | 444 | 379 | 65 | 13,448 |
| 513100 | 2.158 | 426 | 364 | 62 | 13,380 |
| 513690 | 1.158 | 794 | 678 | 116 | 13,433 |
| 159577 | 1.612 | 571 | 487 | 84 | 13,541 |
| 159263 | 1.143 | 805 | 687 | 118 | 13,487 |

- 卖出手数合计 445 手，金额 CNY 67,289；整手取整后 k=0.392964（不超过权限）

## 削减的代价

- 交易成本（8bp 单边 × 卖出额）：CNY 53.83
- 释放现金的回购收益：年化 CNY 796.08（GC001 1.185%，2026-11-06 收盘）
- 若风险腿维持 book_realized 的已实现年化：少赚 CNY 7,575/年
- 若风险腿维持 same_beta_benchmark 的已实现年化：少赚 CNY 1,132/年
- give-up is the sleeve's own realized CAGR minus the observed repo rate on the trimmed amount: an ex-post reading, not a forecast, and it is the price of obeying a gate that failed on concentration, not a return estimate

## 未测

- the year gate on the trimmed book: a smaller k is not automatically a passing book (r1438/r1450: the wrapper's yearly shape has never been through it)
- whether the 11-11 pick set changes names: the trim ratio holds at the sleeve level, the per-leg rows do not survive a re-pick
- the carry accrual path: one observed GC001 close is used for the annualised figure; a holiday gap accrues more days than the rate implies

