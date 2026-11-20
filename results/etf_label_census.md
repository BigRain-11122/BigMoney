# The board's own labels, adjudicated by its own prices

Session: 2026-11-20  |  ruler: median |day change| of the gap <= 0.30 pp on >= 120 common days

135 of 585 labels are written on two or more live tickers; the price history calls 99 of those one basket, 24 a family and 10 none at all. 121 groups of true substitutes survive the clique test and 27 carry a premium spread over 0.50 pp (30447 CNY on a 100000 CNY swap)

| reading | value |
|---|---|
| board rows / labels | 1670 / 585 |
| labels on >= 2 live tickers | 135 |
| pairs / priced pairs | 1219 / 1137 |
| ONE_BASKET / MIXED / NOT_A_BASKET / UNPRICED | 99 / 24 / 10 / 2 |
| groups of true substitutes (clique) | 121 |
| groups over the 0.50 pp line | 27 |
| their cost on a 100000 CNY swap | 30447 CNY |
| labels whose class rests on a subset of their pairs | 8 |

A class read off a subset is marked `*` below; the unpriced pairs are listed in the JSON under each family's `unpriced` key (short history or no panel), and a pair that could not be priced is never counted as a basket.

Partial: 机器人ETF (36/55 priced), 科创50ETF (78/91 priced), 银行ETF (21/28 priced), 粮食ETF (3/6 priced), 港股通信息技术ETF (21/28 priced), 创业板算力ETF (0/28 priced), 上证指数ETF (6/10 priced), 创业板电池ETF (0/1 priced)

## where the name and the price disagree

| label | class | live | priced pairs | worst median pp |
|---|---|---|---|---|
| 有色ETF | MIXED | 4 | 6 | 1.338 |
| 信创ETF | NOT_A_BASKET | 2 | 1 | 0.630 |
| 红利ETF | MIXED | 4 | 6 | 0.560 |
| 消费ETF | NOT_A_BASKET | 3 | 3 | 0.556 |
| 通信ETF | MIXED | 6 | 15 | 0.534 |
| 半导体ETF | MIXED | 3 | 3 | 0.516 |
| 电池ETF | MIXED | 6 | 15 | 0.491 |
| 红利质量ETF | NOT_A_BASKET | 2 | 1 | 0.462 |
| 港股科技ETF | MIXED | 4 | 6 | 0.451 |
| 港股通央企红利ETF | MIXED | 3 | 3 | 0.448 |
| 创新药ETF | MIXED | 7 | 21 | 0.434 |
| 卫星ETF | MIXED | 6 | 15 | 0.431 |
| 创业板成长ETF | NOT_A_BASKET | 2 | 1 | 0.430 |
| 港股通科技ETF | MIXED | 6 | 15 | 0.421 |
| 机器人ETF | MIXED | 11 | 36 | 0.398 |
| 价值ETF | NOT_A_BASKET | 2 | 1 | 0.392 |
| 港股通红利ETF | MIXED | 3 | 3 | 0.390 |
| 港股红利ETF | NOT_A_BASKET | 2 | 1 | 0.390 |
| 航空航天ETF | MIXED | 4 | 6 | 0.389 |
| 半导体设备ETF | MIXED | 6 | 15 | 0.388 |
| 石油ETF | MIXED | 3 | 3 | 0.386 |
| 房地产ETF | MIXED | 3 | 3 | 0.379 |
| 港股通创新药ETF | MIXED | 8 | 28 | 0.374 |
| 港股通互联网ETF | MIXED | 5 | 10 | 0.368 |
| 医药ETF | MIXED | 3 | 3 | 0.366 |
| 科技ETF | NOT_A_BASKET | 2 | 1 | 0.366 |
| 生物医药ETF | MIXED | 3 | 3 | 0.359 |
| 消费电子ETF | MIXED | 3 | 3 | 0.357 |
| 港股创新药ETF | MIXED | 4 | 6 | 0.334 |
| 港股通金融ETF | NOT_A_BASKET | 2 | 1 | 0.334 |
| 电网设备ETF | MIXED | 4 | 6 | 0.319 |
| 港股红利低波ETF | NOT_A_BASKET | 2 | 1 | 0.316 |
| 港股央企红利ETF | NOT_A_BASKET | 2 | 1 | 0.308 |
| 有色金属ETF | MIXED | 3 | 3 | 0.300 |

## the groups a reader may switch inside

| label(s) | members | cheapest | dearest | spread pp | cost CNY |
|---|---|---|---|---|---|
| 纳指ETF | 159501, 159660, 159696, 159941, 513100, 513110, 513870 | 513110 (12.22%) | 159501 (18.04%) | 5.82 | 5824 |
| 纳斯达克100ETF | 159513, 159659 | 159513 (12.20%) | 159659 (15.75%) | 3.56 | 3558 |
| 标普500ETF | 159612, 159655, 513500, 513650 | 513650 (6.41%) | 513500 (8.57%) | 2.16 | 2164 |
| 纳斯达克ETF | 159632, 513300 | 159632 (13.32%) | 513300 (14.78%) | 1.46 | 1458 |
| 中概互联网ETF | 159607, 513050 | 159607 (-3.76%) | 513050 (-2.34%) | 1.42 | 1417 |
| 日经225ETF | 513000, 513880 | 513000 (2.83%) | 513880 (4.25%) | 1.41 | 1413 |
| 恒生科技ETF | 159740, 159741, 159742, 513010, 513130, 513180, 513260, 513380, 513580, 520570, 520920 | 513580 (-1.25%) | 513180 (0.11%) | 1.37 | 1368 |
| 港股通医疗ETF | 159137, 520510 | 520510 (-1.29%) | 159137 (-0.23%) | 1.06 | 1063 |
| 日经ETF | 159866, 513520 | 159866 (2.34%) | 513520 (3.39%) | 1.05 | 1053 |
| 科创50ETF | 588000, 588040, 588050, 588060, 588080, 588090, 588150, 588280, 588870, 588940, 588950, 589150, 589850 | 588000 (-0.46%) | 589150 (0.40%) | 0.86 | 864 |
| 港股通科技ETF | 159262, 520980 | 520980 (-0.83%) | 159262 (-0.07%) | 0.77 | 768 |
| 恒生医疗ETF | 159303, 159557, 513060 | 159557 (-1.21%) | 159303 (-0.45%) | 0.76 | 762 |
| 港股通红利低波ETF | 159118, 159220, 159545 | 159220 (-0.23%) | 159118 (0.48%) | 0.71 | 706 |
| 恒生生物科技ETF | 159105, 159615, 513280, 513930, 520930 | 513280 (-1.09%) | 159615 (-0.39%) | 0.70 | 701 |
| 中证800ETF | 515800, 515810 | 515810 (-0.46%) | 515800 (0.21%) | 0.67 | 671 |
| 巴西ETF | 159100, 520870 | 159100 (-1.17%) | 520870 (-0.53%) | 0.64 | 641 |
| 港股科技ETF | 159128, 513020, 513980 | 513980 (-0.70%) | 159128 (-0.07%) | 0.63 | 627 |
| 沪深300ETF | 159300, 159330, 159393, 159673, 159919, 159925, 510300, 510310, 510330, 510360, 510390, 515310, 515330, 515390 | 159330 (-0.46%) | 510390 (0.14%) | 0.59 | 594 |
| 科创创业50ETF | 159780, 159783, 588300 | 159780 (-0.76%) | 159783 (-0.19%) | 0.58 | 576 |
| 芯片ETF | 159599, 159801, 159995, 512760, 516350, 516640, 516920 | 159801 (-0.50%) | 159599 (0.06%) | 0.57 | 569 |
| 创业板人工智能ETF | 159242, 159246, 159279, 159363, 159381, 159382, 159388 | 159381 (-0.23%) | 159279 (0.34%) | 0.57 | 567 |
| 软件ETF | 159590, 159852, 159899, 515230, 562930 | 159590 (-0.33%) | 159899 (0.20%) | 0.53 | 528 |
| 证券ETF | 159692, 159841, 159993, 512570, 512880, 512900, 515010, 515850, 560090, 560400 | 159692 (-0.30%) | 560400 (0.22%) | 0.52 | 522 |
| 科创芯片ETF | 588200, 588290, 588750, 588810, 588890, 588920, 588990, 589100, 589130, 589160, 589190 | 588200 (-0.67%) | 588920 (-0.15%) | 0.52 | 519 |
| 标普油气ETF | 159518, 513350 | 159518 (0.84%) | 513350 (1.35%) | 0.51 | 505 |
| 港股互联网ETF | 159568, 513770 | 513770 (-0.75%) | 159568 (-0.25%) | 0.51 | 505 |
| 游戏ETF | 159869, 516010, 516770 | 159869 (-0.27%) | 516010 (0.23%) | 0.50 | 504 |

94 further groups are one basket but their premium spread is under the 0.50 pp materiality line (货币ETF, 粮食ETF, 港股通科技ETF, 创业板软件ETF, 化工ETF, 港股通信息技术ETF, 科创创业人工智能ETF, 电力ETF, 电池ETF, 自由现金流ETF, 恒生互联网ETF, 创业板ETF, 机器人ETF, 卫星ETF, 现金流ETF, 航空航天ETF, 港股通消费ETF, 机器人ETF, 储能电池ETF, 红利低波100ETF, 黄金股ETF, 港股通汽车ETF, 半导体ETF, 半导体设备ETF, 中证A500ETF, A500ETF, 港股医疗ETF, 创业板50ETF, 创业板新能源ETF, 通信ETF, 港股国企ETF, 红利低波ETF, 中证2000ETF, 德国ETF, 创业板200ETF, 美国50ETF, 红利ETF, A50ETF, 中概互联ETF, 稀有金属ETF, 绿色电力ETF, 中证1000ETF, 有色ETF, 恒生消费ETF, 稀土ETF, 石化ETF, 食品饮料ETF, 电池ETF, 旅游ETF, 科创创业ETF, 双创50ETF, 传媒ETF, 人工智能ETF, 农业ETF, 医疗ETF, 金ETF, 生物医药ETF, 券商ETF, 金融科技ETF, 影视ETF, 光伏ETF, 养殖ETF, 新能源ETF, 银行ETF, 恒生ETF, 中证500ETF, 医药ETF, 黄金ETF, 创新药ETF, 通信ETF, 电子ETF, 上证50ETF, 上证指数ETF, 证券保险ETF, 房地产ETF, 军工ETF, 港股通医药ETF, 港股通红利ETF, 港股通央企红利ETF, 新能源车ETF, 工程机械ETF, 云计算ETF, 消费电子ETF, 科创新材料ETF, 科创成长ETF, 科创100ETF, 科创医药ETF, 科创200ETF, 科创半导体设备ETF, 科创人工智能ETF, 科创新能源ETF, 科创综指ETF, 科创芯片设计ETF, 科创创新药ETF).

## chains that are not cliques (no money priced inside them)

- 有色金属ETF: 159157, 512400, 516650 -- A~B and B~C is not A~C; not every pair inside was accepted
- 港股通互联网ETF: 159170, 159792, 513040, 520650, 520910 -- A~B and B~C is not A~C; not every pair inside was accepted
- 石油ETF: 159189, 159697, 561360 -- A~B and B~C is not A~C; not every pair inside was accepted
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
