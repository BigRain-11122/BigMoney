# 同指数换票面 · 2026-11-06

问题只有一个：**同一篮子在不同代码下卖，今天最便宜的那个要多少溢价？**

口径：溢价 = 价格 / IOPV − 1（同一时点快照，跨境腿继承 IOPV 误差）；节省以**篮子价值**计——同样的现金买 amount/(1+p) 的篮子。

## 本单逐腿

| 代码 | 名称 | 指数标签 | 溢价% | 家族最便宜 | 差(pp) | 同现金多买篮子(CNY) | 判 |
|---|---|---|---|---|---|---|---|
| 159501 | 纳指ETF | NDX100 | +23.640 | 159513 纳斯达克100ETF大成 +14.97% | 8.67 | 5,612 | SWAP_SAVES |
| 513100 | 纳指ETF | NDX100 | +21.256 | 159513 纳斯达克100ETF大成 +14.97% | 6.29 | 4,149 | SWAP_SAVES |
| 513690 | 港股红利ETF | — | +0.078 | — | — | — | CANNOT_VERIFY |
| 159577 | 美国50ETF | US50 | +9.667 | 513850 美国50ETF易方达 +9.48% | 0.19 | 146 | GAP_IMMATERIAL |
| 159263 | 价值ETF | — | -0.183 | — | — | — | CANNOT_VERIFY |

**合计：同现金可多买篮子 9,762 元，占本单 459,796 元 的 2.123%。**

另有 146 元落在 0.50pp 材料性线以内（换票能多买，但差值太小，不构成动作）。

## 同一指数在市场上卖几个价

| 指数 | 成员 | 可交易 | 最便宜 | 最贵 | 价差(pp) | 贴水成员 |
|---|---|---|---|---|---|---|
| NDX100 | 12 | 12 | 159513 +14.97% | 159501 +23.64% | 8.67 | 0 |
| US50 | 2 | 2 | 513850 +9.48% | 159577 +9.67% | 0.19 | 0 |

这些家族里**没有一只贴水**：最便宜的那一档就是**通道价**。书的错误只在「挑了家族里最贵的那只」，不在「买这个指数」——换票能省，但省不掉通道本身的溢价。

## 未验证

- 513690 无法核验：label 港股红利ETF names no other live ticker on this board (no sibling group)
- 159263 无法核验：label 价值ETF names no other live ticker on this board (no sibling group)
- 无法解析标签的名称 1652 个（不合并，只会低估节省）

## 诚实边界

- the label is read from the NAME, not from a fund document: two tickers that carry different words for the same basket are not merged, and under-merging can only understate the saving
- premium = price / IOPV - 1 on one session snapshot; IOPV is a real-time estimate, not a published NAV, so a cross-border leg's number inherits that error (it is the same ruler r1463 uses)
- a swap is a different ISIN holding the same index -- tracking difference, fee, size and quotation width are NOT priced here
- the basket gain assumes the cash stays the same; buying the cheaper sibling therefore buys more units, not the same units
- liquidity floor is a session turnover number, not a depth test: a 20M-turning ETF can still be thin at the moment of a 92k order
- this face says nothing about whether the index itself should be bought today
