# The board's own labels, adjudicated by its own prices

Session: 2026-11-17  |  ruler: median |day change| of the gap <= 0.30 pp on >= 120 common days

137 of 584 labels are written on two or more live tickers; the price history calls 102 of those one basket, 23 a family and 9 none at all. 123 groups of true substitutes survive the clique test and 21 carry a premium spread over 0.50 pp (26022 CNY on a 100000 CNY swap)

| reading | value |
|---|---|
| board rows / labels | 1668 / 584 |
| labels on >= 2 live tickers | 137 |
| pairs / priced pairs | 1290 / 1160 |
| ONE_BASKET / MIXED / NOT_A_BASKET / UNPRICED | 102 / 23 / 9 / 3 |
| groups of true substitutes (clique) | 123 |
| groups over the 0.50 pp line | 21 |
| their cost on a 100000 CNY swap | 26022 CNY |
| labels whose class rests on a subset of their pairs | 12 |

A class read off a subset is marked `*` below; the unpriced pairs are listed in the JSON under each family's `unpriced` key (short history or no panel), and a pair that could not be priced is never counted as a basket.

Partial: 机器人ETF (45/66 priced), 科创50ETF (78/91 priced), 银行ETF (21/28 priced), 粮食ETF (1/3 priced), 稀有金属ETF (3/6 priced), 科创芯片设计ETF (3/15 priced), 有色ETF (15/21 priced), 港股通信息技术ETF (21/45 priced), 创业板算力ETF (0/36 priced), A股ETF (0/1 priced), 上证指数ETF (6/10 priced), 创业板电池ETF (0/1 priced)

## where the name and the price disagree

| label | class | live | priced pairs | worst median pp |
|---|---|---|---|---|
| 有色ETF | MIXED | 7 | 15 | 1.326 |
| 红利ETF | MIXED | 3 | 3 | 0.559 |
| 通信ETF | MIXED | 6 | 15 | 0.534 |
| 半导体ETF | MIXED | 3 | 3 | 0.516 |
| 红利质量ETF | NOT_A_BASKET | 2 | 1 | 0.462 |
| 电池ETF | MIXED | 5 | 10 | 0.456 |
| 港股通央企红利ETF | MIXED | 3 | 3 | 0.452 |
| 港股科技ETF | MIXED | 4 | 6 | 0.451 |
| 创新药ETF | MIXED | 7 | 21 | 0.435 |
| 卫星ETF | MIXED | 6 | 15 | 0.433 |
| 创业板成长ETF | NOT_A_BASKET | 2 | 1 | 0.429 |
| 港股通科技ETF | MIXED | 7 | 21 | 0.425 |
| 机器人ETF | MIXED | 12 | 45 | 0.397 |
| 港股红利ETF | NOT_A_BASKET | 2 | 1 | 0.390 |
| 港股通红利ETF | MIXED | 3 | 3 | 0.390 |
| 航空航天ETF | MIXED | 4 | 6 | 0.390 |
| 价值ETF | NOT_A_BASKET | 2 | 1 | 0.385 |
| 半导体设备ETF | MIXED | 6 | 15 | 0.385 |
| 房地产ETF | MIXED | 3 | 3 | 0.379 |
| 港股通创新药ETF | MIXED | 8 | 28 | 0.372 |
| 医药ETF | MIXED | 3 | 3 | 0.366 |
| 港股通互联网ETF | MIXED | 5 | 10 | 0.365 |
| 科技ETF | NOT_A_BASKET | 2 | 1 | 0.365 |
| 生物医药ETF | MIXED | 3 | 3 | 0.359 |
| 消费电子ETF | MIXED | 3 | 3 | 0.357 |
| 港股通金融ETF | NOT_A_BASKET | 2 | 1 | 0.335 |
| 消费ETF | NOT_A_BASKET | 2 | 1 | 0.328 |
| 港股创新药ETF | MIXED | 4 | 6 | 0.326 |
| 港股红利低波ETF | NOT_A_BASKET | 2 | 1 | 0.318 |
| 电网设备ETF | MIXED | 4 | 6 | 0.317 |
| 港股央企红利ETF | NOT_A_BASKET | 2 | 1 | 0.308 |
| 有色金属ETF | MIXED | 3 | 3 | 0.301 |

## the groups a reader may switch inside

| label(s) | members | cheapest | dearest | spread pp | cost CNY |
|---|---|---|---|---|---|
| 纳指ETF | 159501, 159660, 159696, 159941, 513100, 513110, 513870 | 513110 (13.73%) | 159501 (19.81%) | 6.08 | 6084 |
| 德国ETF | 159561, 513030 | 159561 (-0.45%) | 513030 (2.47%) | 2.92 | 2921 |
| 纳斯达克100ETF | 159513, 159659 | 159513 (13.94%) | 159659 (16.67%) | 2.72 | 2722 |
| 标普500ETF | 159655, 513500, 513650 | 159655 (7.52%) | 513500 (9.24%) | 1.72 | 1723 |
| 日经225ETF | 513000, 513880 | 513000 (3.30%) | 513880 (4.54%) | 1.24 | 1238 |
| 港股通消费ETF | 159245, 159268, 513070, 513230 | 159268 (-0.58%) | 513070 (0.48%) | 1.06 | 1055 |
| 恒生科技ETF | 159740, 159741, 159742, 513010, 513130, 513180, 513260, 513380, 513580, 520570, 520920 | 159741 (-0.53%) | 513180 (0.47%) | 1.00 | 1001 |
| 纳斯达克ETF | 159632, 513300 | 159632 (14.52%) | 513300 (15.50%) | 0.98 | 978 |
| 日经ETF | 159866, 513520 | 159866 (3.13%) | 513520 (4.01%) | 0.87 | 875 |
| 巴西ETF | 159100, 520870 | 159100 (-0.78%) | 520870 (0.02%) | 0.80 | 797 |
| 恒生医疗ETF | 159303, 159557, 513060 | 159557 (-0.98%) | 159303 (-0.26%) | 0.72 | 724 |
| 中概互联网ETF | 159607, 513050 | 513050 (-2.82%) | 159607 (-2.16%) | 0.66 | 662 |
| 机器人ETF | 159272, 159278, 159530, 159559 | 159272 (-0.31%) | 159278 (0.32%) | 0.64 | 638 |
| 中概互联ETF | 159605, 513220 | 513220 (-2.18%) | 159605 (-1.54%) | 0.64 | 637 |
| 稀土ETF | 159713, 159715, 516150, 516780 | 516150 (-0.37%) | 159715 (0.24%) | 0.62 | 616 |
| 中证500增强ETF | 561550, 563030 | 563030 (-0.81%) | 561550 (-0.21%) | 0.60 | 601 |
| 港股通医疗ETF | 159137, 520510 | 520510 (-0.73%) | 159137 (-0.15%) | 0.58 | 578 |
| 中证2000ETF | 159531, 159532, 562660, 563300 | 159531 (-0.48%) | 563300 (0.09%) | 0.58 | 575 |
| 影视ETF | 159855, 516620 | 516620 (-0.73%) | 159855 (-0.16%) | 0.57 | 573 |
| 港股通科技ETF | 159101, 159125, 159269, 513150, 520530 | 159125 (-0.03%) | 520530 (0.49%) | 0.53 | 525 |
| 中证1000ETF | 159629, 159633, 159845, 512100, 560010, 560110 | 159629 (-0.50%) | 560110 (0.00%) | 0.50 | 501 |

102 further groups are one basket but their premium spread is under the 0.50 pp materiality line (货币ETF, 粮食ETF, 恒生生物科技ETF, 创业板软件ETF, 港股科技ETF, 港股通信息技术ETF, 化工ETF, 科创创业人工智能ETF, 电池ETF, 自由现金流ETF, 恒生互联网ETF, 创业板ETF, 机器人ETF, 卫星ETF, 航空航天ETF, 创业板人工智能ETF, 港股通科技ETF, 港股消费ETF, 沪深300ETF, 储能电池ETF, 红利低波100ETF, 黄金股ETF, 港股通汽车ETF, 半导体ETF, 半导体设备ETF, 中证A500ETF, A500ETF, 港股医疗ETF, 创业板50ETF, 创业板新能源ETF, 现金流ETF, 通信ETF, 标普油气ETF, 红利低波ETF, 芯片ETF, 港股互联网ETF, 创业板200ETF, 美国50ETF, 软件ETF, A50ETF, 中证A50ETF, 稀有金属ETF, 电力ETF, 绿色电力ETF, 有色ETF, 证券ETF, 石油ETF, 恒生消费ETF, 港股医药ETF, 石化ETF, 食品饮料ETF, 旅游ETF, 科创创业50ETF, 科创创业ETF, 双创50ETF, 传媒ETF, 人工智能ETF, 农业ETF, 医疗ETF, 金ETF, 生物医药ETF, 券商ETF, 金融科技ETF, 光伏ETF, 养殖ETF, 游戏ETF, 新能源ETF, 银行ETF, 恒生ETF, 中证500ETF, 医药ETF, 黄金ETF, 创新药ETF, 通信ETF, 电子ETF, 上证50ETF, 上证指数ETF, 红利ETF, 证券保险ETF, 房地产ETF, 军工ETF, 港股通医药ETF, 港股通红利ETF, 港股通央企红利ETF, 新能源车ETF, 中证800ETF, 工程机械ETF, 云计算ETF, 消费电子ETF, 科创50ETF, 科创新材料ETF, 科创成长ETF, 科创100ETF, 科创医药ETF, 科创芯片ETF, 科创200ETF, 科创半导体设备ETF, 科创人工智能ETF, 科创新能源ETF, 科创综指ETF, 科创芯片设计ETF, 科创创新药ETF).

## chains that are not cliques (no money priced inside them)

- 有色金属ETF: 159157, 512400, 516650 -- A~B and B~C is not A~C; not every pair inside was accepted
- 港股通互联网ETF: 159170, 159792, 513040, 520650, 520910 -- A~B and B~C is not A~C; not every pair inside was accepted
- 港股通创新药ETF: 159217, 159286, 159297, 159316, 159570, 520700, 520880, 520970 -- A~B and B~C is not A~C; not every pair inside was accepted
- 电网设备ETF: 159320, 159326, 560390, 561380 -- A~B and B~C is not A~C; not every pair inside was accepted
- 港股创新药ETF: 159567, 513120, 513780, 520690 -- A~B and B~C is not A~C; not every pair inside was accepted
- 创新药ETF: 159622, 159748, 517110, 517380 -- A~B and B~C is not A~C; not every pair inside was accepted

## what this face does not say

- one session of premiums and one price history per pair: the group says these tickers hold the same basket, it does not say the basket is worth its price
- the money line is the dearest-vs-cheapest premium INSIDE an accepted group on a 100000 CNY swap; it is the cost of an avoidable choice, not a return
- a label with unpriced pairs carries n_priced < n_pairs; those pairs are unknown, never baskets
- the 0.30 pp line is the r1803 ruler; --check echoes it, so a refit is a new face and not a silent edit
- labels are the board's own residual names after the house prefix is stripped; two different words for one basket (alias families) are NOT merged here
