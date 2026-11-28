# 商品 TSMOM 能吃多少钱（容量与冲击面）

generated 2026-11-28T17:51:53+08:00 | 判决 **CAPACITY_OK_FOR_THIS_BOOK**

规则：单日不超过该品种 120 日中位成交量的 1%；持仓不超过中位持仓量的 5%；名义=价格 x 合约乘数。需求侧按卡自己的配方（tsmom 250d、跳过 21d、目标波动 8%）重算毛名义，不是按书的本金 1M 硬比。

| 品种 | 中位日成交(手) | 中位持仓(手) | 每手名义(元) | 1%ADV | 5%OI | 容量(取小) | 今天该书要的名额 | 容量/名额 |
|---|---|---|---|---|---|---|---|---|
| AU | 225,952 | 171,276 | 901,750 | 2,037,526,669 | 7,722,406,650 | 2,037,526,669 | 202,605 | 10056.7x |
| RB | 704,573 | 1,742,068 | 30,760 | 216,726,809 | 2,679,301,353 | 216,726,809 | 427,837 | 506.6x |
| SC | 132,176 | 35,721 | 585,950 | 774,488,202 | 1,046,550,646 | 774,488,202 | 74,955 | 10332.6x |

今天 8% 目标下的毛名义 = **0.7054x 本书**（2026-11-27），合计需要 705,400 元名义；三品种合计容量 3,028,741,680 元 = **4293.7x 这本书**。

## 没有回答的问题

- impact is a fixed share of median volume, not a market-impact curve
- margin funding cost is not charged; the 8% vol target ignores the lot-size floor
- the commodity sleeve trades one continuous series per product, so roll slippage beyond the 1% ADV rule is not separately modelled
- median volume/OI over 120 bars hides crowded days; a squeezed session is smaller
