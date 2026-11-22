# 股指基差能吃多少钱（bench cell 6）

generated 2026-11-22T23:19:39+08:00 | 判决 **CAPACITY_OK_AND_SIZED**

规则：单日不超过该合约中位成交量的 1%；持仓不超过中位持仓量的 5%；书规模按 1M 计。

| 品种 | 活跃合约 | 中位日成交(手) | 中位持仓(手) | 每手名义(元) | 1%ADV 容量 | 5%OI 容量 | 容量(取小) | 是书的几倍 | 净carry | 10M 下年收 |
|---|---|---|---|---|---|---|---|---|---|---|
| IC | IC2612 | 114214 | 170374 | 1,536,140 | 1,754,486,940 | 13,085,954,222 | 1,754,486,940 | 1754.5x | 4.145% | 414,500 |
| IM | IM2612 | 171858 | 245436 | 1,499,760 | 2,577,465,040 | 18,404,754,768 | 2,577,465,040 | 2577.5x | 5.889% | 588,900 |

合计容量 4,331,951,980 元 = 4332.0x 书规模。若每腿各买 10M（合计名义 20M、按 12% 保证金约占用 2.4M），两腿年收合计约 1,003,400 元（毛，未扣资金成本）。

## 没有回答的问题

- impact is modelled as a fixed share of median volume, not from a market-impact curve
- margin funding cost is not charged (futures margin earns nothing here)
- OI is taken as a 120-bar median; a crowded quarter would be smaller
