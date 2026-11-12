# 同指数换票面 · 2026-11-11

问题只有一个：**同一篮子在不同代码下卖，今天最便宜的那个要多少溢价？**

口径：溢价 = 价格 / IOPV − 1（同一时点快照，跨境腿继承 IOPV 误差）；节省以**篮子价值**计——同样的现金买 amount/(1+p) 的篮子。

## 本单逐腿

| 代码 | 名称 | 指数标签 | 溢价% | 家族最便宜 | 差(pp) | 同现金多买篮子(CNY) | 判 |
|---|---|---|---|---|---|---|---|
| 510760 | 上证指数ETF | — | +0.109 | — | — | — | CANNOT_VERIFY |
| 512040 | 价值ETF | — | -0.017 | — | — | — | CANNOT_VERIFY |
| 159655 | 标普500ETF | — | +9.542 | — | — | — | CANNOT_VERIFY |
| 513690 | 港股红利ETF | — | +0.173 | — | — | — | CANNOT_VERIFY |
| 159519 | 港股国企ETF | — | -0.221 | — | — | — | CANNOT_VERIFY |

**合计：同现金可多买篮子 0 元，占本单 431,876 元 的 0.0%。**

## 同一指数在市场上卖几个价

| 指数 | 成员 | 可交易 | 最便宜 | 最贵 | 价差(pp) | 贴水成员 |
|---|---|---|---|---|---|---|
| NDX100 | 12 | 12 | 513110 +15.92% | 159501 +21.79% | 5.87 | 0 |
| US50 | 2 | 2 | 159577 +12.03% | 513850 +12.32% | 0.29 | 0 |

这些家族里**没有一只贴水**：最便宜的那一档就是**通道价**。书的错误只在「挑了家族里最贵的那只」，不在「买这个指数」——换票能省，但省不掉通道本身的溢价。

## 未验证

- 510760 无法核验：label 上证指数ETF names no other live ticker on this board (no sibling group)
- 512040 无法核验：label 价值ETF names no other live ticker on this board (no sibling group)
- 159655 无法核验：label 标普500ETF names no other live ticker on this board (no sibling group)
- 513690 无法核验：label 港股红利ETF names no other live ticker on this board (no sibling group)
- 159519 无法核验：label 港股国企ETF names no other live ticker on this board (no sibling group)
- 无法解析标签的名称 1653 个（不合并，只会低估节省）

## 诚实边界

- the label is read from the NAME, not from a fund document: two tickers that carry different words for the same basket are not merged, and under-merging can only understate the saving
- premium = price / IOPV - 1 on one session snapshot; IOPV is a real-time estimate, not a published NAV, so a cross-border leg's number inherits that error (it is the same ruler r1463 uses)
- a swap is a different ISIN holding the same index -- tracking difference, fee, size and quotation width are NOT priced here
- the basket gain assumes the cash stays the same; buying the cheaper sibling therefore buys more units, not the same units
- liquidity floor is a session turnover number, not a depth test: a 20M-turning ETF can still be thin at the moment of a 92k order
- this face says nothing about whether the index itself should be bought today
