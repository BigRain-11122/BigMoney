# The board's own labels, adjudicated by its own prices

Session: 2026-11-25  |  ruler: median |day change| of the gap <= 0.30 pp on >= 120 common days

89 of 1173 labels are written on two or more live tickers; the price history calls 73 of those one basket, 5 a family and 11 none at all. 78 groups of true substitutes survive the clique test and 17 carry a premium spread over 0.50 pp (35717 CNY on a 100000 CNY swap)

| reading | value |
|---|---|
| board rows / labels | 1670 / 1173 |
| labels on >= 2 live tickers | 89 |
| pairs / priced pairs | 473 / 441 |
| ONE_BASKET / MIXED / NOT_A_BASKET / UNPRICED | 73 / 5 / 11 / 0 |
| groups of true substitutes (clique) | 78 |
| groups over the 0.50 pp line | 17 |
| their cost on a 100000 CNY swap | 35717 CNY |
| labels whose class rests on a subset of their pairs | 4 |

A class read off a subset is marked `*` below; the unpriced pairs are listed in the JSON under each family's `unpriced` key (short history or no panel), and a pair that could not be priced is never counted as a basket.

Partial: 银行ETF (28/36 priced), 科创50ETF (55/66 priced), 港股通信息技术ETF (6/15 priced), 上证指数ETF (6/10 priced)

## where the name and the price disagree

| label | class | live | priced pairs | worst median pp |
|---|---|---|---|---|
| 有色ETF | NOT_A_BASKET | 2 | 1 | 1.392 |
| 通信ETF | NOT_A_BASKET | 3 | 3 | 0.525 |
| 港股通央企红利ETF | MIXED | 3 | 3 | 0.447 |
| 卫星ETF | MIXED | 5 | 10 | 0.435 |
| 创新药ETF | MIXED | 4 | 6 | 0.434 |
| 港股科技ETF | NOT_A_BASKET | 2 | 1 | 0.414 |
| 港股通科技ETF | NOT_A_BASKET | 2 | 1 | 0.403 |
| 价值ETF | NOT_A_BASKET | 2 | 1 | 0.388 |
| 电池ETF | MIXED | 3 | 3 | 0.381 |
| 半导体设备ETF | MIXED | 3 | 3 | 0.368 |
| 港股通创新药ETF | NOT_A_BASKET | 2 | 1 | 0.361 |
| 港股通红利ETF | NOT_A_BASKET | 2 | 1 | 0.339 |
| 港股创新药ETF | NOT_A_BASKET | 2 | 1 | 0.335 |
| 港股通金融ETF | NOT_A_BASKET | 2 | 1 | 0.333 |
| 消费ETF | NOT_A_BASKET | 2 | 1 | 0.328 |
| 医药ETF | NOT_A_BASKET | 2 | 1 | 0.307 |

## the groups a reader may switch inside

| label(s) | members | cheapest | dearest | spread pp | cost CNY |
|---|---|---|---|---|---|
| 芯片ETF | 159995, 512760, 516350, 516640, 516920 | 516350 (-6.99%) | 159995 (0.04%) | 7.03 | 7025 |
| 纳指ETF | 159941, 513100, 513110, 513870 | 513110 (11.65%) | 513100 (17.55%) | 5.89 | 5895 |
| 机器人ETF | 560770, 562500 | 560770 (-5.21%) | 562500 (0.14%) | 5.35 | 5352 |
| 恒生科技ETF | 513010, 513130, 513180, 513260, 513380, 513580, 520570, 520920 | 513130 (-1.16%) | 520920 (1.64%) | 2.80 | 2795 |
| 标普500ETF | 513500, 513650 | 513650 (6.91%) | 513500 (9.25%) | 2.34 | 2339 |
| 黄金ETF | 159934, 518660, 518800, 518850, 518880 | 518880 (-3.54%) | 159934 (-1.27%) | 2.26 | 2263 |
| 金ETF | 159834, 518600, 518680 | 518680 (-3.31%) | 159834 (-1.08%) | 2.23 | 2227 |
| 日经ETF | 159866, 513520 | 159866 (1.05%) | 513520 (2.51%) | 1.46 | 1459 |
| 日经225ETF | 513000, 513880 | 513000 (1.40%) | 513880 (2.48%) | 1.08 | 1079 |
| 科创芯片ETF | 588200, 588290, 588750, 588810, 588890, 588920, 588990, 589100, 589130, 589160, 589190 | 588890 (-0.29%) | 589190 (0.63%) | 0.92 | 920 |
| 港股通央企红利ETF | 513910, 513920 | 513920 (-1.15%) | 513910 (-0.44%) | 0.71 | 711 |
| 科创综指ETF | 589000, 589080, 589630, 589660, 589680, 589800, 589900 | 589900 (-0.28%) | 589630 (0.40%) | 0.68 | 678 |
| 港股通信息技术ETF | 513240, 520710, 526000, 526050 | 520710 (-0.60%) | 526050 (0.07%) | 0.67 | 669 |
| 中证1000ETF | 512100, 560010, 560110 | 560010 (-0.33%) | 560110 (0.29%) | 0.62 | 619 |
| 科创200ETF | 588230, 588240, 588270, 588820, 589220 | 588270 (-0.41%) | 588240 (0.18%) | 0.59 | 587 |
| 科创100ETF | 588030, 588120, 588190, 588220, 588800 | 588220 (-0.31%) | 588120 (0.26%) | 0.56 | 564 |
| 港股通互联网ETF | 513040, 520630, 520650, 520910 | 520650 (-0.39%) | 520910 (0.14%) | 0.53 | 534 |

61 further groups are one basket but their premium spread is under the 0.50 pp materiality line (A500, 德国ETF, 电力ETF, 稀土ETF, 石化ETF, 旅游ETF, 传媒ETF, 农业ETF, 医疗ETF, 证券ETF, 券商ETF, 软件ETF, 影视ETF, 光伏ETF, 游戏ETF, 化工ETF, 银行ETF, 恒生ETF, 电子ETF, 上证50ETF, 上证指数ETF, 沪深300ETF, 中证500ETF, 红利ETF, 货币ETF, A500ETF, 房地产ETF, 有色金属ETF, 军工ETF, 卫星ETF, 红利低波ETF, 港股通消费ETF, 港股通医药ETF, 恒生生物科技ETF, 港股互联网ETF, 新能源车ETF, 创新药ETF, 食品饮料ETF, 大数据ETF, 工程机械ETF, 新能源ETF, 金融科技ETF, 云计算ETF, 中国A50ETF, 电网设备ETF, 半导体设备ETF, 消费电子ETF, 电池ETF, 绿色电力ETF, 沪深300增强ETF, 中证2000ETF, 科创50ETF, 科创新材料ETF, 科创成长ETF, 科创医药ETF, 科创创业ETF, 科创半导体设备ETF, 科创人工智能ETF, 科创新能源ETF, 科创芯片设计ETF, 科创创新药ETF).

## what this face does not say

- one session of premiums and one price history per pair: the group says these tickers hold the same basket, it does not say the basket is worth its price
- the money line is the dearest-vs-cheapest premium INSIDE an accepted group on a 100000 CNY swap; it is the cost of an avoidable choice, not a return
- a label with unpriced pairs carries n_priced < n_pairs; those pairs are unknown, never baskets
- the 0.30 pp line is the r1803 ruler; --check echoes it, so a refit is a new face and not a silent edit
- labels are the board's own residual names after the house prefix is stripped; two different words for one basket (alias families) are NOT merged here
