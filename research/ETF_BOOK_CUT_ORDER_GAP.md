# The size the permission refuses vs the size the desk orders

- 判定：**ORDER_WITHIN_PERMISSION**
- 决策日：2026-11-11 ｜ 票据：TICKET-2026-11-09.json ｜ 证据截止：2026-11-09

## 一句话

the ticket orders k=0.393073 (CNY 392,727) and the permission allows 0.393073 (CNY 392,727): no cut is owed on 2026-11-11

## 两侧的数

| 读数 | k | 风险腿金额 CNY |
|---|---|---|
| 票据将下单 | 0.393073 | 392,727 |
| 权限允许 | 0.393073 | 392,727 |
| 差额 | 0.000000（0.00pp） | 0 |

## 逐腿削减（）

| 代码 | 价 | 现手数 | 目标手数 | 卖出手数 | 卖出 CNY |
|---|---|---|---|---|---|

- 卖出手数合计 None 手，金额 CNY 0；整手取整后 k=0.000000（**超出权限**）

## 削减的代价

- 交易成本（8bp 单边 × 卖出额）：CNY 0.00
- 释放现金的回购收益：年化 CNY 0.00（GC001 1.185%，2026-11-06 收盘）
- 若风险腿维持 book_realized 的已实现年化：少赚 CNY 0/年
- 若风险腿维持 same_beta_benchmark 的已实现年化：少赚 CNY 0/年
- give-up is the sleeve's own realized CAGR minus the observed repo rate on the trimmed amount: an ex-post reading, not a forecast, and it is the price of obeying a gate that failed on concentration, not a return estimate

## 未测

- the year gate on the trimmed book: a smaller k is not automatically a passing book (r1438/r1450: the wrapper's yearly shape has never been through it)
- whether the 11-11 pick set changes names: the trim ratio holds at the sleeve level, the per-leg rows do not survive a re-pick
- the carry accrual path: one observed GC001 close is used for the annualised figure; a holiday gap accrues more days than the rate implies

