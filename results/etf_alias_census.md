# Two names, one basket: who on this board is the same thing renamed

Session: 2026-11-16  |  window 2025-11-06 to 2026-11-17 (250 days)  |  gates: <= 20% of days move apart by > 0.50 pp AND the gap walks <= 1.0 pp

On this board's own prices, 830 pairs cannot be told apart for a year and do not walk apart; 661 of them are written under two different names. Those pairs gather into 26 families that span more than one name, and in 5 of them the dearest member carries more than 0.50 pp of extra premium over the cheapest -- on a 100,000 CNY ticket that is 8,477 CNY for nothing but picking the wrong name. A further 1257 pairs move together day to day but walk apart over the year (a swap is a bet), and 164,089 do not move together at all.

| reading | value |
|---|---|
| board rows / live / with panel | 1667 / 649 / 642 |
| tickers in the screen | 577 (short history excluded: 65) |
| pairs screened | 2087 |
| SAME_BASKET / WALKS_APART / DAYS_APART | 830 / 1257 / 164089 |
| accepted families (clique) / chains refused | 43 / 38 |
| families spanning more than one name | 26 |

## the line, measured on the board's own verdicts

Same-name pairs the prices accepted (r1804): n=322 -- this rule accepts 169 (52%) and refuses 153. Same-name pairs the prices refused: n=24 -- this rule accepts 0 and refuses 24. **KEEPS_THE_ACCEPTED_AND_REFUSES_EVERY_REFUSED_PAIR: of the 322 same-name pairs the prices accepted this rule accepts 169 (52%) and refuses 153; of the 24 pairs the prices refused it accepts none**

Which gate does the refusing: of the 153 accepted same-name pairs this rule refuses, **0 are refused by the day gate alone**, 149 by the year gate alone, 4 by both. The caveat below says the year gate costs recall; that line has to be read against this split.

**What the labelled negatives can and cannot police**: all 24 pairs the prices refused are refused by the year gate as well (day gate alone 0, year gate alone 1, both 23), and the least-drifted of them still sits at 2.8 pp -- so a drift line below that is not opposed by a single labelled negative on this board. Loosening 1.0 -> 3.0 recovers 295 same-name pairs and lets in 0 of them: this set polices the far side of the line, not the near side.

How far over the line the refusals sit (pp/yr of drift): 1.0-1.5: 44, 1.5-2.0: 45, 2.0-3.0: 39, 3.0+: 25.

Pairs the day gate let through and the year gate refused (drift descending) -- this is the "different dividends or fees make them drift" set, and the drift sizes are printed so the reader can judge the caveat rather than take it:

| a | b | drift pp/yr | share of days apart |
|---|---|---|---|
| 562660 | 563300 | 10.93 | 0.229 |
| 510760 | 510980 | 7.82 | 0.068 |
| 159995 | 516350 | 7.55 | 0.088 |
| 588450 | 588460 | 6.19 | 0.345 |
| 588830 | 589960 | 5.30 | 0.048 |
| 588150 | 588040 | 5.15 | 0.149 |
| 513110 | 513100 | 4.87 | 0.149 |
| 588940 | 588040 | 4.61 | 0.149 |
| 159995 | 512760 | 4.59 | 0.072 |
| 510880 | 515180 | 4.32 | 0.092 |

What moving the year line buys and what it also lets in (same labelled set, day gate held fixed):

| year line pp | accepted same-name pairs | price-refused pairs it would bless |
|---|---|---|
| 1.0 | 169 | 0 |
| 1.5 | 212 | 0 |
| 2.0 | 257 | 0 |
| 3.0 | 295 | 0 |

**The decision on the line is published, not left to each reader**: KEEP at 1.0 pp/yr -- no pair the board's own prices refused drifts less than 2.8 pp/yr, so the labelled set cannot place the line between 1.0 and there; the line is priced by what being wrong costs -- a swap made inside a 1.0 pp/yr band loses at most that band, while the 126 extra pairs a 3.0 pp line recovers each carry up to 3 pp/yr of drift. Cost: recall: 153 of the 322 same-name pairs the prices accepted are refused.

## what the year gate costs

The day gate is held fixed; only the drift line moves. Loosening it recovers same-basket pairs whose dividends differ and accepts swaps that are partly bets.

| drift line pp/yr | accepted pairs | across names | families | chains | over material | cost CNY |
|---|---|---|---|---|---|---|
| 0.5 | 468 | 378 | 24 | 28 | 5 | 9098 |
| 1.0 | 830 | 661 | 26 | 38 | 5 | 8477 |
| 2.0 | 1357 | 1100 | 31 | 44 | 4 | 6202 |

## families a reader may switch inside

Families whose members are written under more than one name. Money is the dearest-vs-cheapest premium inside the family on a 100000 CNY ticket.

| names | members | cheapest | dearest | spread pp | cost CNY |
|---|---|---|---|---|---|
| 稀有金属, 稀有金属ETF | 159608, 562800 | 159608 (-4.16%) | 562800 (-0.04%) | 4.12 | 4119 |
| 电网ETF, 电网设备 | 159320, 159326 | 159326 (-0.09%) | 159320 (1.44%) | 1.53 | 1532 |
| 日经225ETF, 日经ETF | 159866, 513000 | 159866 (0.99%) | 513000 (2.10%) | 1.11 | 1111 |
| 现金流E, 自由现金 | 159201, 159222 | 159201 (0.05%) | 159222 (1.03%) | 0.97 | 974 |
| 恒生红利ETF, 港股红利 | 159545, 513950 | 513950 (-0.74%) | 159545 (0.00%) | 0.74 | 741 |
| 标普500ETF, 标普ETF | 159655, 513650 | 513650 (6.27%) | 159655 (6.75%) | 0.48 | 475 |
| 计算机, 计算机ETF | 159998, 512720 | 512720 (-0.21%) | 159998 (0.11%) | 0.32 | 319 |
| XD港股通红利ETF, 港股央企红利ETF景顺 | 520900, 520990 | 520990 (-0.52%) | 520900 (-0.20%) | 0.32 | 317 |
| 新能源, 新能源ETF | 159875, 516160 | 159875 (-0.11%) | 516160 (0.16%) | 0.26 | 264 |
| 港股科技ETF, 港股通科技ETF | 513160, 520980 | 520980 (-0.54%) | 513160 (-0.28%) | 0.26 | 259 |
| HS医疗, 恒生医疗ETF | 159303, 513060 | 513060 (-1.34%) | 159303 (-1.08%) | 0.26 | 255 |
| 医疗港股, 港股通医疗ETF | 159366, 520510 | 520510 (-1.54%) | 159366 (-1.30%) | 0.24 | 240 |
| 中概互联, 互联中概 | 159605, 159607 | 159607 (-2.48%) | 159605 (-2.28%) | 0.20 | 196 |
| AH创新药, 创新药AH, 创新药ETF | 159622, 159748, 517110 | 159748 (-0.82%) | 159622 (-0.64%) | 0.18 | 184 |
| 深成ETF, 深证ETF | 159903, 159943 | 159943 (-0.11%) | 159903 (0.07%) | 0.18 | 178 |
| 地产ETF, 地产龙头 | 159707, 159768 | 159768 (-0.24%) | 159707 (-0.07%) | 0.18 | 177 |
| 电池ETF, 锂电池50 | 159755, 159840 | 159840 (-0.19%) | 159755 (-0.03%) | 0.16 | 159 |
| 金科ETF, 金融科技ETF | 159851, 516860 | 159851 (-0.02%) | 516860 (0.13%) | 0.15 | 148 |
| 中证红利ETF, 红利ETF | 515080, 515180 | 515080 (-0.22%) | 515180 (-0.08%) | 0.14 | 142 |
| 港科ETF, 港科技30 | 159101, 159636 | 159101 (-0.95%) | 159636 (-0.81%) | 0.14 | 138 |
| 医药, 医药ETF | 159929, 159938 | 159929 (-0.15%) | 159938 (-0.03%) | 0.11 | 114 |
| 恒指互联, 恒生互联 | 159202, 159688 | 159688 (-0.59%) | 159202 (-0.48%) | 0.11 | 109 |
| 创业新能, 创新能源 | 159368, 159387 | 159387 (-0.16%) | 159368 (-0.08%) | 0.08 | 83 |
| 芯片, 芯片ETF | 159813, 159995 | 159995 (-0.09%) | 159813 (-0.04%) | 0.05 | 48 |
| 软件50, 软件ETF | 159590, 159852, 515230 | 159590 (-0.05%) | 515230 (-0.02%) | 0.03 | 35 |
| 保证金, 华宝添益ETF, 招商财富宝ETF, 货币ETF, 货币ETF建信 | 159001, 511620, 511660, 511700, 511850, 511990 | - | - | - | premium unobservable |

Single-name accepted families (the label census's own ground, re-derived here with the two-gate ruler): 17.

## chains: pairs that agree pairwise but not all together (no money inside)

- 恒生生物, 恒生生物科技ETF, 恒生生科, 港生物, 港股创新药ETF, 港股创新药ETF景顺 -- 159102, 159105, 159615, 159718, 159892, 513120, 513200, 513280 (12 members, 42 pairs not accepted)
- 创业100, 创业ETF, 创业东财, 创业板, 创业板BS, 创业板EF -- 159205, 159908, 159915, 159948, 159952, 159957, 159958, 159971 (9 members, 20 pairs not accepted)
- 机器人, 机器人AI, 机器人ETF, 机器人NF, 机器人TF -- 159213, 159258, 159526, 159770, 560770, 562500 (6 members, 7 pairs not accepted)
- HK创新药, 创新药E, 创新药HK, 创新药港, 港创新药, 港股新药 -- 159217, 159286, 159297, 159316, 159567, 159570, 520880 (7 members, 11 pairs not accepted)
- 现金流DC, 现金流ETF, 现金流ETF中银, 现金流NF, 现金流PA -- 159232, 159233, 159235, 563390, 563760 (5 members, 5 pairs not accepted)
- AI创业, AI创业板, 创AI, 创AI富国, 创业AI, 创业AIDC -- 159242, 159246, 159279, 159363, 159381, 159382, 159388 (7 members, 8 pairs not accepted)
- HK消费, 港股通消费ETF -- 159268, 513070, 513230 (3 members, 1 pairs not accepted)
- 港科技, 港科技NF, 港股科技ETF, 港股科技ETF景顺, 港股通科技ETF, 港股通科技ETF海富通 -- 159269, 159750, 159751, 513020, 513150, 513860, 513980 (7 members, 12 pairs not accepted)
- 机器人E, 机器人FG, 机器人PH, 机器人基 -- 159272, 159278, 159530, 159559 (4 members, 3 pairs not accepted)
- 300ETF, 300万家, 300基金, A50, A500, A500DC -- 159300, 159330, 159338, 159339, 159351, 159352, 159353, 159356 (47 members, 746 pairs not accepted)
- 100红利, 红利100, 红利低波100ETF景顺 -- 159307, 159549, 515100 (3 members, 1 pairs not accepted)
- 黄金产业, 黄金股, 黄金股ETF, 黄金股ETF永赢 -- 159321, 159562, 517400, 517520 (4 members, 2 pairs not accepted)
- 半导体E, 半导体设备ETF, 半导材料, 半导设备 -- 159327, 159516, 159558, 560780 (4 members, 2 pairs not accepted)
- 300红利低波ETF, 800红利, 低波红利, 红利低波, 红利低波50ETF, 红利低波ETF -- 159355, 159525, 159547, 512890, 515300, 515450, 563020 (7 members, 14 pairs not accepted)
- 创50E, 创50ETF, 创50国泰, 创50指数, 创业五零, 创业大盘 -- 159369, 159371, 159375, 159681, 159682, 159814, 159949 (7 members, 10 pairs not accepted)
- 纳100ETF, 纳指, 纳指100ETF, 纳指ETF, 纳指大成, 纳斯达克 -- 159513, 159632, 159659, 159696, 159941, 513100, 513110, 513300 (10 members, 28 pairs not accepted)
- 2000E, 中证2000, 中证2000ETF -- 159531, 159532, 563300 (3 members, 1 pairs not accepted)
- 芯片50, 芯片ETF, 芯片指数 -- 159560, 159599, 512760, 516350, 516640, 516920 (6 members, 9 pairs not accepted)
- 互联网, 港股互联, 港股互联网ETF -- 159568, 159792, 513770 (3 members, 1 pairs not accepted)
- 电力ETF, 绿电ETF, 绿色电力, 绿色电力ETF -- 159611, 159625, 561170, 561560, 562550, 562960 (6 members, 9 pairs not accepted)
- ... and 18 more in the JSON

## what this face does not say

- two gates, both on PRICE only: a pair that passes is one the prices cannot tell apart for a year minus event days -- it is not a statement about the holdings
- the line is calibrated on the board's own SAME-NAME families (r1804); applying it across names is an extrapolation, and the calibration block is republished each run
- distribution policy is invisible here: two same-basket tickers that pay different dividends drift in price and are refused by gate 2 (a false refusal, not a risk)
- the money line is the dearest-vs-cheapest premium INSIDE an accepted family on a 100000 CNY ticket; it is the price of picking the wrong name, not a return
- one session of premiums: the family membership rests on a year of closes, the money on one day's board
- the screen drops tickers that did not trade every day of the window (65 here); they are counted, never filled with zeros
