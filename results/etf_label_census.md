# The board's own labels, adjudicated by its own prices

Session: 2026-11-19  |  ruler: median |day change| of the gap <= 0.30 pp on >= 120 common days

84 of 1187 labels are written on two or more live tickers; the price history calls 68 of those one basket, 6 a family and 10 none at all. 74 groups of true substitutes survive the clique test and 12 carry a premium spread over 0.50 pp (21297 CNY on a 100000 CNY swap)

| reading | value |
|---|---|
| board rows / labels | 1668 / 1187 |
| labels on >= 2 live tickers | 84 |
| pairs / priced pairs | 412 / 390 |
| ONE_BASKET / MIXED / NOT_A_BASKET / UNPRICED | 68 / 6 / 10 / 0 |
| groups of true substitutes (clique) | 74 |
| groups over the 0.50 pp line | 12 |
| their cost on a 100000 CNY swap | 21297 CNY |
| labels whose class rests on a subset of their pairs | 3 |

A class read off a subset is marked `*` below; the unpriced pairs are listed in the JSON under each family's `unpriced` key (short history or no panel), and a pair that could not be priced is never counted as a basket.

Partial: 科创50ETF (55/66 priced), 港股通信息技术ETF (3/10 priced), 上证指数ETF (6/10 priced)

## where the name and the price disagree

| label | class | live | priced pairs | worst median pp |
|---|---|---|---|---|
| 有色ETF | NOT_A_BASKET | 2 | 1 | 1.326 |
| 通信ETF | NOT_A_BASKET | 3 | 3 | 0.522 |
| 港股通央企红利ETF | MIXED | 3 | 3 | 0.449 |
| 卫星ETF | MIXED | 5 | 10 | 0.433 |
| 创新药ETF | MIXED | 3 | 3 | 0.420 |
| 港股科技ETF | NOT_A_BASKET | 2 | 1 | 0.416 |
| 港股通科技ETF | NOT_A_BASKET | 2 | 1 | 0.402 |
| 港股通红利ETF | MIXED | 3 | 3 | 0.390 |
| 价值ETF | NOT_A_BASKET | 2 | 1 | 0.388 |
| 电池ETF | MIXED | 3 | 3 | 0.378 |
| 半导体设备ETF | MIXED | 3 | 3 | 0.365 |
| 港股通创新药ETF | NOT_A_BASKET | 2 | 1 | 0.354 |
| 港股通金融ETF | NOT_A_BASKET | 2 | 1 | 0.335 |
| 港股创新药ETF | NOT_A_BASKET | 2 | 1 | 0.331 |
| 消费ETF | NOT_A_BASKET | 2 | 1 | 0.328 |
| 医药ETF | NOT_A_BASKET | 2 | 1 | 0.307 |

## the groups a reader may switch inside

| label(s) | members | cheapest | dearest | spread pp | cost CNY |
|---|---|---|---|---|---|
| 纳指ETF | 159941, 513100, 513110, 513870 | 513110 (16.20%) | 513100 (20.45%) | 4.26 | 4257 |
| 港股通互联网ETF | 513040, 520650, 520910 | 513040 (-4.73%) | 520910 (-0.75%) | 3.98 | 3985 |
| 科创人工智能ETF | 588730, 588760, 588930, 589010, 589520 | 589520 (-2.15%) | 588730 (0.13%) | 2.28 | 2279 |
| 中证1000ETF | 512100, 560010, 560110 | 560010 (-1.95%) | 512100 (-0.03%) | 1.92 | 1924 |
| 科创芯片ETF | 588200, 588290, 588750, 588810, 588890, 588920, 588990, 589100, 589130, 589160, 589190 | 588920 (-0.18%) | 589190 (1.46%) | 1.64 | 1638 |
| 标普500ETF | 513500, 513650 | 513650 (8.70%) | 513500 (10.22%) | 1.53 | 1528 |
| 恒生科技ETF | 513010, 513130, 513180, 513260, 513380, 513580, 520570 | 513130 (-1.45%) | 513180 (0.07%) | 1.52 | 1518 |
| 日经225ETF | 513000, 513880 | 513000 (4.24%) | 513880 (5.65%) | 1.41 | 1412 |
| 港股通央企红利ETF | 513910, 513920 | 513920 (-1.71%) | 513910 (-0.78%) | 0.93 | 931 |
| 日经ETF | 159866, 513520 | 159866 (3.94%) | 513520 (4.70%) | 0.76 | 764 |
| 港股通红利ETF | 513530, 513820 | 513820 (-1.32%) | 513530 (-0.76%) | 0.55 | 555 |
| 光伏ETF | 159857, 515370, 515790 | 515370 (-0.37%) | 159857 (0.14%) | 0.51 | 508 |

62 further groups are one basket but their premium spread is under the 0.50 pp materiality line (德国ETF, 电力ETF, 矿业ETF, 稀土ETF, 石化ETF, 传媒ETF, 农业ETF, 医疗ETF, 金ETF, 证券ETF, 券商ETF, 软件ETF, 影视ETF, 游戏ETF, 化工ETF, 银行ETF, 恒生ETF, 黄金ETF, 芯片ETF, 电子ETF, 上证50ETF, 上证指数ETF, 沪深300ETF, 中证500ETF, 红利ETF, A500ETF, 证券保险ETF, 房地产ETF, 有色金属ETF, 军工ETF, 卫星ETF, 红利低波ETF, 港股通消费ETF, 港股通医药ETF, 港股通信息技术ETF, 恒生生物科技ETF, 新能源车ETF, 创新药ETF, 食品饮料ETF, 大数据ETF, 工程机械ETF, 新能源ETF, 金融科技ETF, 云计算ETF, 电网设备ETF, 半导体设备ETF, 消费电子ETF, 电池ETF, 绿色电力ETF, 中证2000ETF, 科创50ETF, 科创新材料ETF, 科创成长ETF, 科创100ETF, 科创医药ETF, 科创200ETF, 科创创业ETF, 科创半导体设备ETF, 科创新能源ETF, 科创综指ETF, 科创芯片设计ETF, 科创创新药ETF).

## what this face does not say

- one session of premiums and one price history per pair: the group says these tickers hold the same basket, it does not say the basket is worth its price
- the money line is the dearest-vs-cheapest premium INSIDE an accepted group on a 100000 CNY swap; it is the cost of an avoidable choice, not a return
- a label with unpriced pairs carries n_priced < n_pairs; those pairs are unknown, never baskets
- the 0.30 pp line is the r1803 ruler; --check echoes it, so a refit is a new face and not a silent edit
- labels are the board's own residual names after the house prefix is stripped; two different words for one basket (alias families) are NOT merged here
