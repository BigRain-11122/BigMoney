# 股指基差能吃多少钱（bench cell 6）

generated 2026-11-26T23:22:58+08:00 | 判决 **CAPACITY_OK_AND_SIZED**

规则：单日不超过该合约中位成交量的 1%；持仓不超过中位持仓量的 5%；书规模按 1M 计。

| 品种 | 活跃合约 | 中位日成交(手) | 中位持仓(手) | 每手名义(元) | 1%ADV 容量 | 5%OI 容量 | 容量(取小) | 是书的几倍 | 净carry | 10M 下年收 |
|---|---|---|---|---|---|---|---|---|---|---|
| IC | IC2612 | 114734 | 170743 | 1,529,740 | 1,755,139,540 | 13,059,658,085 | 1,755,139,540 | 1755.1x | 4.15% | 415,000 |
| IM | IM2612 | 171858 | 247018 | 1,493,460 | 2,566,637,954 | 18,445,612,450 | 2,566,637,954 | 2566.6x | 5.982% | 598,200 |

合计容量 4,321,777,494 元 = 4321.8x 书规模。若每腿各买 10M（合计名义 20M、按 12% 保证金约占用 2.4M），两腿年收合计约 1,013,200 元（毛，未扣资金成本）。

## 没有回答的问题

- impact is modelled as a fixed share of median volume, not from a market-impact curve
- margin funding cost is not charged (futures margin earns nothing here)
- OI is taken as a 120-bar median; a crowded quarter would be smaller
