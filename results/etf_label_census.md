# The board's own labels, adjudicated by its own prices

Session: 2026-11-26  |  ruler: median |day change| of the gap <= 0.30 pp on >= 120 common days

82 of 1172 labels are written on two or more live tickers; the price history calls 66 of those one basket, 6 a family and 10 none at all. 72 groups of true substitutes survive the clique test and 8 carry a premium spread over 0.50 pp (11575 CNY on a 100000 CNY swap)

| reading | value |
|---|---|
| board rows / labels | 1670 / 1172 |
| labels on >= 2 live tickers | 82 |
| pairs / priced pairs | 433 / 411 |
| ONE_BASKET / MIXED / NOT_A_BASKET / UNPRICED | 66 / 6 / 10 / 0 |
| groups of true substitutes (clique) | 72 |
| groups over the 0.50 pp line | 8 |
| their cost on a 100000 CNY swap | 11575 CNY |
| labels whose class rests on a subset of their pairs | 3 |

A class read off a subset is marked `*` below; the unpriced pairs are listed in the JSON under each family's `unpriced` key (short history or no panel), and a pair that could not be priced is never counted as a basket.

Partial: 银行ETF (21/28 priced), 科创50ETF (55/66 priced), 港股通信息技术ETF (6/10 priced)

## where the name and the price disagree

| label | class | live | priced pairs | worst median pp |
|---|---|---|---|---|
| 有色ETF | NOT_A_BASKET | 2 | 1 | 1.392 |
| 通信ETF | NOT_A_BASKET | 3 | 3 | 0.522 |
| 港股通央企红利ETF | MIXED | 3 | 3 | 0.447 |
| 卫星ETF | MIXED | 5 | 10 | 0.437 |
| 创新药ETF | MIXED | 4 | 6 | 0.434 |
| 港股科技ETF | NOT_A_BASKET | 2 | 1 | 0.414 |
| 港股通科技ETF | NOT_A_BASKET | 2 | 1 | 0.403 |
| 港股通红利ETF | MIXED | 3 | 3 | 0.388 |
| 价值ETF | NOT_A_BASKET | 2 | 1 | 0.388 |
| 电池ETF | MIXED | 3 | 3 | 0.383 |
| 半导体设备ETF | MIXED | 3 | 3 | 0.368 |
| 港股通创新药ETF | NOT_A_BASKET | 2 | 1 | 0.361 |
| 港股创新药ETF | NOT_A_BASKET | 2 | 1 | 0.335 |
| 港股通金融ETF | NOT_A_BASKET | 2 | 1 | 0.334 |
| 消费ETF | NOT_A_BASKET | 2 | 1 | 0.328 |
| 医药ETF | NOT_A_BASKET | 2 | 1 | 0.307 |

## the groups a reader may switch inside

| label(s) | members | cheapest | dearest | spread pp | cost CNY |
|---|---|---|---|---|---|
| 纳指ETF | 159941, 513100, 513110, 513870 | 513110 (13.62%) | 513100 (18.48%) | 4.86 | 4857 |
| 标普500ETF | 513500, 513650 | 513650 (7.16%) | 513500 (9.03%) | 1.87 | 1869 |
| 科创人工智能ETF | 588730, 588760, 588930, 589010, 589520 | 588760 (-1.42%) | 588930 (-0.22%) | 1.20 | 1202 |
| 红利ETF | 510880, 515180 | 510880 (-0.16%) | 515180 (0.97%) | 1.14 | 1136 |
| 中证2000ETF | 562660, 563300 | 562660 (-0.35%) | 563300 (0.31%) | 0.67 | 668 |
| 红利低波ETF | 512890, 563020 | 512890 (-0.19%) | 563020 (0.44%) | 0.63 | 629 |
| 日经225ETF | 513000, 513880 | 513000 (4.21%) | 513880 (4.84%) | 0.63 | 627 |
| 恒生科技ETF | 513010, 513130, 513180, 513260, 513380, 513580, 520570, 520920 | 513380 (-0.13%) | 520920 (0.46%) | 0.59 | 587 |

64 further groups are one basket but their premium spread is under the 0.50 pp materiality line (A500, 德国ETF, 电力ETF, 稀土ETF, 石化ETF, 旅游ETF, 传媒ETF, 农业ETF, 医疗ETF, 金ETF, 证券ETF, 券商ETF, 软件ETF, 影视ETF, 光伏ETF, 日经ETF, 游戏ETF, 化工ETF, 银行ETF, 恒生ETF, 黄金ETF, 芯片ETF, 电子ETF, 上证50ETF, 上证指数ETF, 沪深300ETF, 中证500ETF, A500ETF, 中证1000ETF, 房地产ETF, 有色金属ETF, 军工ETF, 卫星ETF, 港股通互联网ETF, 港股通消费ETF, 港股通医药ETF, 港股通信息技术ETF, 恒生生物科技ETF, 港股通红利ETF, 港股互联网ETF, 港股通央企红利ETF, 新能源车ETF, 创新药ETF, 中证800ETF, 工程机械ETF, 新能源ETF, 云计算ETF, 电网设备ETF, 机器人ETF, 半导体设备ETF, 消费电子ETF, 电池ETF, 沪深300增强ETF, 科创50ETF, 科创新材料ETF, 科创成长ETF, 科创100ETF, 科创芯片ETF, 科创200ETF, 科创创业ETF, 科创半导体设备ETF, 科创综指ETF, 科创芯片设计ETF, 科创创新药ETF).

## what this face does not say

- one session of premiums and one price history per pair: the group says these tickers hold the same basket, it does not say the basket is worth its price
- the money line is the dearest-vs-cheapest premium INSIDE an accepted group on a 100000 CNY swap; it is the cost of an avoidable choice, not a return
- a label with unpriced pairs carries n_priced < n_pairs; those pairs are unknown, never baskets
- the 0.30 pp line is the r1803 ruler; --check echoes it, so a refit is a new face and not a silent edit
- labels are the board's own residual names after the house prefix is stripped; two different words for one basket (alias families) are NOT merged here
