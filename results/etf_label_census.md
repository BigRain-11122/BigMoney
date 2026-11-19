# The board's own labels, adjudicated by its own prices

Session: 2026-11-18  |  ruler: median |day change| of the gap <= 0.30 pp on >= 120 common days

88 of 1187 labels are written on two or more live tickers; the price history calls 72 of those one basket, 6 a family and 10 none at all. 78 groups of true substitutes survive the clique test and 13 carry a premium spread over 0.50 pp (15704 CNY on a 100000 CNY swap)

| reading | value |
|---|---|
| board rows / labels | 1668 / 1187 |
| labels on >= 2 live tickers | 88 |
| pairs / priced pairs | 439 / 405 |
| ONE_BASKET / MIXED / NOT_A_BASKET / UNPRICED | 72 / 6 / 10 / 0 |
| groups of true substitutes (clique) | 78 |
| groups over the 0.50 pp line | 13 |
| their cost on a 100000 CNY swap | 15704 CNY |
| labels whose class rests on a subset of their pairs | 4 |

A class read off a subset is marked `*` below; the unpriced pairs are listed in the JSON under each family's `unpriced` key (short history or no panel), and a pair that could not be priced is never counted as a basket.

Partial: 科创50ETF (55/66 priced), 银行ETF (15/21 priced), 科创芯片设计ETF (1/6 priced), 港股通信息技术ETF (3/15 priced)

## where the name and the price disagree

| label | class | live | priced pairs | worst median pp |
|---|---|---|---|---|
| 有色ETF | NOT_A_BASKET | 2 | 1 | 1.321 |
| 通信ETF | NOT_A_BASKET | 3 | 3 | 0.523 |
| 港股通央企红利ETF | MIXED | 3 | 3 | 0.450 |
| 卫星ETF | MIXED | 5 | 10 | 0.434 |
| 创新药ETF | MIXED | 3 | 3 | 0.420 |
| 港股科技ETF | NOT_A_BASKET | 2 | 1 | 0.417 |
| 港股通科技ETF | NOT_A_BASKET | 2 | 1 | 0.402 |
| 港股通红利ETF | MIXED | 3 | 3 | 0.390 |
| 价值ETF | NOT_A_BASKET | 2 | 1 | 0.385 |
| 电池ETF | MIXED | 3 | 3 | 0.377 |
| 半导体设备ETF | MIXED | 3 | 3 | 0.365 |
| 港股通创新药ETF | NOT_A_BASKET | 2 | 1 | 0.353 |
| 港股通金融ETF | NOT_A_BASKET | 2 | 1 | 0.335 |
| 消费ETF | NOT_A_BASKET | 2 | 1 | 0.328 |
| 港股创新药ETF | NOT_A_BASKET | 2 | 1 | 0.327 |
| 医药ETF | NOT_A_BASKET | 2 | 1 | 0.307 |

## the groups a reader may switch inside

| label(s) | members | cheapest | dearest | spread pp | cost CNY |
|---|---|---|---|---|---|
| 纳指ETF | 159941, 513100, 513110, 513870 | 513110 (14.42%) | 513100 (19.01%) | 4.60 | 4598 |
| 芯片ETF | 159995, 512760, 516350, 516640, 516920 | 516640 (0.00%) | 516350 (1.98%) | 1.98 | 1980 |
| 恒生科技ETF | 513010, 513130, 513180, 513260, 513380, 513580, 520570 | 513130 (-2.18%) | 513180 (-0.95%) | 1.22 | 1224 |
| 标普500ETF | 513500, 513650 | 513650 (7.63%) | 513500 (8.76%) | 1.14 | 1136 |
| 德国ETF | 159561, 513030 | 159561 (-2.38%) | 513030 (-1.32%) | 1.06 | 1062 |
| 中证500增强ETF | 561550, 563030 | 563030 (-0.99%) | 561550 (0.03%) | 1.02 | 1017 |
| 科创50增强ETF | 588450, 588460 | 588460 (-0.57%) | 588450 (0.33%) | 0.90 | 902 |
| 恒生ETF | 159920, 513660 | 513660 (-1.80%) | 159920 (-1.03%) | 0.77 | 772 |
| 中证1000ETF | 512100, 560010 | 560010 (-0.73%) | 512100 (0.02%) | 0.75 | 748 |
| 电网设备ETF | 560390, 561380 | 561380 (-0.80%) | 560390 (-0.16%) | 0.64 | 644 |
| 影视ETF | 159855, 516620 | 516620 (-0.61%) | 159855 (-0.06%) | 0.55 | 549 |
| 券商ETF | 159842, 512000 | 159842 (-0.63%) | 512000 (-0.09%) | 0.54 | 541 |
| 科创芯片ETF | 588200, 588290, 588750, 588810, 588890, 588920, 588990, 589100, 589130, 589160, 589190 | 589130 (-0.07%) | 589100 (0.46%) | 0.53 | 530 |

65 further groups are one basket but their premium spread is under the 0.50 pp materiality line (A500, 电力ETF, 稀土ETF, 石化ETF, 传媒ETF, 农业ETF, 医疗ETF, 金ETF, 证券ETF, 软件ETF, 光伏ETF, 日经ETF, 游戏ETF, 化工ETF, 银行ETF, 黄金ETF, 家电ETF, 电子ETF, 上证50ETF, 上证指数ETF, 沪深300ETF, 中证500ETF, 红利ETF, A500ETF, 房地产ETF, 有色金属ETF, 军工ETF, 卫星ETF, 红利低波ETF, 日经225ETF, 港股通互联网ETF, 港股通消费ETF, 港股通医药ETF, 港股通信息技术ETF, 恒生生物科技ETF, 港股通红利ETF, 港股通央企红利ETF, 新能源车ETF, 创新药ETF, 食品饮料ETF, 中证800ETF, 工程机械ETF, 新能源ETF, 金融科技ETF, 云计算ETF, 港股通医疗ETF, 央企红利ETF, 半导体设备ETF, 消费电子ETF, 电池ETF, 绿色电力ETF, 中证2000ETF, 科创50ETF, 科创新材料ETF, 科创成长ETF, 科创100ETF, 科创医药ETF, 科创200ETF, 科创创业ETF, 科创半导体设备ETF, 科创人工智能ETF, 科创新能源ETF, 科创综指ETF, 科创芯片设计ETF, 科创创新药ETF).

## what this face does not say

- one session of premiums and one price history per pair: the group says these tickers hold the same basket, it does not say the basket is worth its price
- the money line is the dearest-vs-cheapest premium INSIDE an accepted group on a 100000 CNY swap; it is the cost of an avoidable choice, not a return
- a label with unpriced pairs carries n_priced < n_pairs; those pairs are unknown, never baskets
- the 0.30 pp line is the r1803 ruler; --check echoes it, so a refit is a new face and not a silent edit
- labels are the board's own residual names after the house prefix is stripped; two different words for one basket (alias families) are NOT merged here
