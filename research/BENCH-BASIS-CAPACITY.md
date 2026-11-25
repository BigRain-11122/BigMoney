# 股指基差能吃多少钱（bench cell 6）

generated 2026-11-25T22:22:38+08:00 | 判决 **CAPACITY_OK_AND_SIZED**

规则：单日不超过该合约中位成交量的 1%；持仓不超过中位持仓量的 5%；书规模按 1M 计。

| 品种 | 活跃合约 | 中位日成交(手) | 中位持仓(手) | 每手名义(元) | 1%ADV 容量 | 5%OI 容量 | 容量(取小) | 是书的几倍 | 净carry | 10M 下年收 |
|---|---|---|---|---|---|---|---|---|---|---|
| IC | IC2612 | 114423 | 170651 | 1,532,140 | 1,753,128,213 | 13,073,099,461 | 1,753,128,213 | 1753.1x | 4.131% | 413,100 |
| IM | IM2612 | 171858 | 246248 | 1,493,700 | 2,567,050,414 | 18,391,069,222 | 2,567,050,414 | 2567.1x | 5.887% | 588,700 |

合计容量 4,320,178,627 元 = 4320.2x 书规模。若每腿各买 10M（合计名义 20M、按 12% 保证金约占用 2.4M），两腿年收合计约 1,001,800 元（毛，未扣资金成本）。

## 没有回答的问题

- impact is modelled as a fixed share of median volume, not from a market-impact curve
- margin funding cost is not charged (futures margin earns nothing here)
- OI is taken as a 120-bar median; a crowded quarter would be smaller
