# The board's own labels, adjudicated by its own prices

Session: 2026-11-16  |  ruler: median |day change| of the gap <= 0.30 pp on >= 120 common days

88 of 1190 labels are written on two or more live tickers; the price history calls 71 of those one basket, 5 a family and 11 none at all. 76 groups of true substitutes survive the clique test and 14 carry a premium spread over 0.50 pp (33763 CNY on a 100000 CNY swap)

| reading | value |
|---|---|
| board rows / labels | 1667 / 1190 |
| labels on >= 2 live tickers | 88 |
| pairs / priced pairs | 452 / 416 |
| ONE_BASKET / MIXED / NOT_A_BASKET / UNPRICED | 71 / 5 / 11 / 1 |
| groups of true substitutes (clique) | 76 |
| groups over the 0.50 pp line | 14 |
| their cost on a 100000 CNY swap | 33763 CNY |
| labels whose class rests on a subset of their pairs | 6 |

A class read off a subset is marked `*` below; the unpriced pairs are listed in the JSON under each family's `unpriced` key (short history or no panel), and a pair that could not be priced is never counted as a basket.

Partial: 科创50ETF (55/66 priced), 银行ETF (15/28 priced), 科创芯片设计ETF (1/3 priced), 卫星ETF (10/15 priced), A股ETF (0/1 priced), 上证指数ETF (6/10 priced)

## where the name and the price disagree

| label | class | live | priced pairs | worst median pp |
|---|---|---|---|---|
| 有色ETF | NOT_A_BASKET | 2 | 1 | 1.338 |
| 消费ETF | NOT_A_BASKET | 3 | 3 | 0.556 |
| 通信ETF | NOT_A_BASKET | 3 | 3 | 0.523 |
| 港股通央企红利ETF | MIXED | 3 | 3 | 0.450 |
| 卫星ETF | MIXED | 6 | 10 | 0.431 |
| 创新药ETF | MIXED | 3 | 3 | 0.420 |
| 港股科技ETF | NOT_A_BASKET | 2 | 1 | 0.417 |
| 港股通科技ETF | NOT_A_BASKET | 2 | 1 | 0.400 |
| 价值ETF | NOT_A_BASKET | 2 | 1 | 0.385 |
| 电池ETF | MIXED | 3 | 3 | 0.377 |
| 半导体设备ETF | MIXED | 3 | 3 | 0.364 |
| 港股通创新药ETF | NOT_A_BASKET | 2 | 1 | 0.355 |
| XD港股通红利ETF | NOT_A_BASKET | 2 | 1 | 0.341 |
| 港股通金融ETF | NOT_A_BASKET | 2 | 1 | 0.336 |
| 港股创新药ETF | NOT_A_BASKET | 2 | 1 | 0.327 |
| 医药ETF | NOT_A_BASKET | 2 | 1 | 0.307 |

## the groups a reader may switch inside

| label(s) | members | cheapest | dearest | spread pp | cost CNY |
|---|---|---|---|---|---|
| 科创芯片ETF | 588200, 588290, 588750, 588810, 588890, 588920, 588990, 589100, 589130, 589160, 589190 | 589130 (-6.66%) | 589160 (0.02%) | 6.69 | 6686 |
| 芯片ETF | 159995, 512760, 516350, 516640, 516920 | 516640 (-5.51%) | 516350 (-0.05%) | 5.46 | 5463 |
| 纳指ETF | 159941, 513100, 513110, 513870 | 513110 (10.76%) | 513100 (15.61%) | 4.85 | 4854 |
| 机器人ETF | 560770, 562500 | 562500 (-3.10%) | 560770 (-0.02%) | 3.07 | 3074 |
| 中证1000ETF | 512100, 560010, 560110 | 560010 (-3.12%) | 512100 (-0.08%) | 3.03 | 3031 |
| 日经ETF | 159866, 513520 | 159866 (0.99%) | 513520 (2.99%) | 2.00 | 2002 |
| 德国ETF | 159561, 513030 | 159561 (-0.06%) | 513030 (1.75%) | 1.81 | 1807 |
| 标普500ETF | 513500, 513650 | 513650 (6.27%) | 513500 (7.85%) | 1.58 | 1581 |
| 日经225ETF | 513000, 513880 | 513000 (2.10%) | 513880 (3.65%) | 1.56 | 1556 |
| 恒生科技ETF | 513010, 513130, 513180, 513260, 513380, 513580, 520570 | 513130 (-1.01%) | 513180 (0.10%) | 1.12 | 1118 |
| 电网设备ETF | 560390, 561380 | 560390 (0.73%) | 561380 (1.57%) | 0.84 | 841 |
| 中证2000ETF | 562660, 563300 | 562660 (-0.70%) | 563300 (-0.07%) | 0.63 | 633 |
| 科创200ETF | 588230, 588240, 588270, 589220 | 588240 (-0.33%) | 589220 (0.26%) | 0.59 | 587 |
| 电池ETF | 561160, 561910 | 561160 (-0.32%) | 561910 (0.21%) | 0.53 | 531 |

62 further groups are one basket but their premium spread is under the 0.50 pp materiality line (电力ETF, 矿业ETF, 稀土ETF, 石化ETF, 旅游ETF, 传媒ETF, 农业ETF, 医疗ETF, 金ETF, 证券ETF, 券商ETF, 软件ETF, 影视ETF, 光伏ETF, 游戏ETF, 化工ETF, 银行ETF, 恒生ETF, 黄金ETF, 电子ETF, 上证50ETF, 上证指数ETF, 沪深300ETF, 中证500ETF, 红利ETF, 货币ETF, A500ETF, 证券保险ETF, 房地产ETF, 有色金属ETF, 军工ETF, 卫星ETF, 红利低波ETF, 港股通互联网ETF, 港股通消费ETF, 港股通医药ETF, 港股通信息技术ETF, 恒生生物科技ETF, 港股通央企红利ETF, 新能源车ETF, 创新药ETF, 食品饮料ETF, 大数据ETF, 工程机械ETF, 新能源ETF, 云计算ETF, 半导体设备ETF, 消费电子ETF, 绿色电力ETF, 科创50ETF, 科创新材料ETF, 科创成长ETF, 科创100ETF, 科创医药ETF, 科创创业ETF, 科创50增强ETF, 科创半导体设备ETF, 科创人工智能ETF, 科创新能源ETF, 科创综指ETF, 科创芯片设计ETF, 科创创新药ETF).

## what this face does not say

- one session of premiums and one price history per pair: the group says these tickers hold the same basket, it does not say the basket is worth its price
- the money line is the dearest-vs-cheapest premium INSIDE an accepted group on a 100000 CNY swap; it is the cost of an avoidable choice, not a return
- a label with unpriced pairs carries n_priced < n_pairs; those pairs are unknown, never baskets
- the 0.30 pp line is the r1803 ruler; --check echoes it, so a refit is a new face and not a silent edit
- labels are the board's own residual names after the house prefix is stripped; two different words for one basket (alias families) are NOT merged here
