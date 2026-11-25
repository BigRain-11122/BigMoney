# The board's own labels, adjudicated by its own prices

Session: 2026-11-24  |  ruler: median |day change| of the gap <= 0.30 pp on >= 120 common days

86 of 1172 labels are written on two or more live tickers; the price history calls 70 of those one basket, 6 a family and 10 none at all. 76 groups of true substitutes survive the clique test and 8 carry a premium spread over 0.50 pp (15804 CNY on a 100000 CNY swap)

| reading | value |
|---|---|
| board rows / labels | 1670 / 1172 |
| labels on >= 2 live tickers | 86 |
| pairs / priced pairs | 478 / 446 |
| ONE_BASKET / MIXED / NOT_A_BASKET / UNPRICED | 70 / 6 / 10 / 0 |
| groups of true substitutes (clique) | 76 |
| groups over the 0.50 pp line | 8 |
| their cost on a 100000 CNY swap | 15804 CNY |
| labels whose class rests on a subset of their pairs | 4 |

A class read off a subset is marked `*` below; the unpriced pairs are listed in the JSON under each family's `unpriced` key (short history or no panel), and a pair that could not be priced is never counted as a basket.

Partial: 银行ETF (28/36 priced), 科创50ETF (55/66 priced), 港股通信息技术ETF (6/15 priced), 上证指数ETF (6/10 priced)

## where the name and the price disagree

| label | class | live | priced pairs | worst median pp |
|---|---|---|---|---|
| 有色ETF | NOT_A_BASKET | 2 | 1 | 1.371 |
| 通信ETF | NOT_A_BASKET | 3 | 3 | 0.523 |
| 港股通央企红利ETF | MIXED | 3 | 3 | 0.448 |
| 创新药ETF | MIXED | 4 | 6 | 0.434 |
| 卫星ETF | MIXED | 5 | 10 | 0.434 |
| 港股科技ETF | NOT_A_BASKET | 2 | 1 | 0.415 |
| 港股通科技ETF | NOT_A_BASKET | 2 | 1 | 0.405 |
| 价值ETF | NOT_A_BASKET | 2 | 1 | 0.392 |
| 港股通红利ETF | MIXED | 3 | 3 | 0.390 |
| 电池ETF | MIXED | 3 | 3 | 0.380 |
| 半导体设备ETF | MIXED | 3 | 3 | 0.367 |
| 港股通创新药ETF | NOT_A_BASKET | 2 | 1 | 0.359 |
| 港股创新药ETF | NOT_A_BASKET | 2 | 1 | 0.334 |
| 港股通金融ETF | NOT_A_BASKET | 2 | 1 | 0.333 |
| 消费ETF | NOT_A_BASKET | 2 | 1 | 0.328 |
| 医药ETF | NOT_A_BASKET | 2 | 1 | 0.307 |

## the groups a reader may switch inside

| label(s) | members | cheapest | dearest | spread pp | cost CNY |
|---|---|---|---|---|---|
| 纳指ETF | 159941, 513100, 513110, 513870 | 513110 (11.00%) | 513100 (16.94%) | 5.94 | 5940 |
| 科创芯片ETF | 588200, 588290, 588750, 588810, 588890, 588920, 588990, 589100, 589130, 589160, 589190 | 588920 (-0.34%) | 588290 (2.41%) | 2.75 | 2750 |
| 标普500ETF | 513500, 513650 | 513650 (5.42%) | 513500 (7.50%) | 2.07 | 2072 |
| 日经ETF | 159866, 513520 | 159866 (6.74%) | 513520 (8.18%) | 1.44 | 1440 |
| 日经225ETF | 513000, 513880 | 513000 (7.28%) | 513880 (8.56%) | 1.28 | 1284 |
| 化工ETF | 159870, 516020, 516120 | 516120 (-1.27%) | 159870 (-0.24%) | 1.03 | 1031 |
| 恒生科技ETF | 513010, 513130, 513180, 513260, 513380, 513580, 520570, 520920 | 513380 (-1.52%) | 520920 (-0.76%) | 0.75 | 754 |
| 港股通红利ETF | 513530, 513820 | 513820 (-0.87%) | 513530 (-0.33%) | 0.53 | 534 |

68 further groups are one basket but their premium spread is under the 0.50 pp materiality line (A500, 德国ETF, 电力ETF, 稀土ETF, 石化ETF, 旅游ETF, 传媒ETF, 农业ETF, 医疗ETF, 金ETF, 证券ETF, 券商ETF, 软件ETF, 影视ETF, 光伏ETF, 游戏ETF, 银行ETF, 恒生ETF, 黄金ETF, 芯片ETF, 电子ETF, 上证50ETF, 上证指数ETF, 沪深300ETF, 中证500ETF, 红利ETF, 货币ETF, A500ETF, 中证1000ETF, 房地产ETF, 有色金属ETF, 军工ETF, 卫星ETF, 红利低波ETF, 港股通互联网ETF, 港股通消费ETF, 港股通医药ETF, 港股通信息技术ETF, 恒生生物科技ETF, 港股通央企红利ETF, 新能源车ETF, 创新药ETF, 中证800ETF, 工程机械ETF, 新能源ETF, 金融科技ETF, 云计算ETF, 电网设备ETF, 央企红利ETF, 机器人ETF, 半导体设备ETF, 消费电子ETF, 电池ETF, 绿色电力ETF, 中证2000ETF, 科创50ETF, 科创新材料ETF, 科创成长ETF, 科创100ETF, 科创200ETF, 科创创业ETF, 科创50增强ETF, 科创半导体设备ETF, 科创人工智能ETF, 科创新能源ETF, 科创综指ETF, 科创芯片设计ETF, 科创创新药ETF).

## what this face does not say

- one session of premiums and one price history per pair: the group says these tickers hold the same basket, it does not say the basket is worth its price
- the money line is the dearest-vs-cheapest premium INSIDE an accepted group on a 100000 CNY swap; it is the cost of an avoidable choice, not a return
- a label with unpriced pairs carries n_priced < n_pairs; those pairs are unknown, never baskets
- the 0.30 pp line is the r1803 ruler; --check echoes it, so a refit is a new face and not a silent edit
- labels are the board's own residual names after the house prefix is stripped; two different words for one basket (alias families) are NOT merged here
