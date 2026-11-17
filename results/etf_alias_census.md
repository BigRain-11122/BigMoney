# Two names, one basket: who on this board is the same thing renamed

Session: 2026-11-17  |  window 2025-11-06 to 2026-11-17 (250 days)  |  gates: <= 20% of days move apart by > 0.50 pp AND the gap walks <= 1.0 pp

On this board's own prices, 867 pairs cannot be told apart for a year and do not walk apart; 464 of them are written under two different names. Those pairs gather into 12 families that span more than one name, and in 2 of them the dearest member carries more than 0.50 pp of extra premium over the cheapest -- on a 100,000 CNY ticket that is 1,311 CNY for nothing but picking the wrong name. A further 1344 pairs move together day to day but walk apart over the year (a swap is a bet), and 166,279 do not move together at all.

| reading | value |
|---|---|
| board rows / live / with panel | 1668 / 660 / 651 |
| tickers in the screen | 581 (short history excluded: 70) |
| pairs screened | 2211 |
| SAME_BASKET / WALKS_APART / DAYS_APART | 867 / 1344 / 166279 |
| accepted families (clique) / chains refused | 41 / 40 |
| families spanning more than one name | 12 |

## the line, measured on the board's own verdicts

Same-name pairs the prices accepted (r1804): n=320 -- this rule accepts 169 (53%) and refuses 151. Same-name pairs the prices refused: n=22 -- this rule accepts 0 and refuses 22. **KEEPS_THE_ACCEPTED_AND_REFUSES_EVERY_REFUSED_PAIR: of the 320 same-name pairs the prices accepted this rule accepts 169 (53%) and refuses 151; of the 22 pairs the prices refused it accepts none**

Which gate does the refusing: of the 151 accepted same-name pairs this rule refuses, **0 are refused by the day gate alone**, 148 by the year gate alone, 3 by both. The caveat below says the year gate costs recall; that line has to be read against this split.

**What the labelled negatives can and cannot police**: all 22 pairs the prices refused are refused by the year gate as well (day gate alone 0, year gate alone 1, both 21), and the least-drifted of them still sits at 2.8 pp -- so a drift line below that is not opposed by a single labelled negative on this board. Loosening 1.0 -> 3.0 recovers 294 same-name pairs and lets in 0 of them: this set polices the far side of the line, not the near side.

How far over the line the refusals sit (pp/yr of drift): 1.0-1.5: 43, 1.5-2.0: 45, 2.0-3.0: 39, 3.0+: 24.

Pairs the day gate let through and the year gate refused (drift descending) -- this is the "different dividends or fees make them drift" set, and the drift sizes are printed so the reader can judge the caveat rather than take it:

| a | b | drift pp/yr | share of days apart |
|---|---|---|---|
| 562660 | 563300 | 10.93 | 0.229 |
| 510760 | 510980 | 7.82 | 0.068 |
| 159995 | 516350 | 7.55 | 0.088 |
| 588830 | 589960 | 5.30 | 0.048 |
| 588150 | 588040 | 5.15 | 0.149 |
| 513110 | 513100 | 4.87 | 0.149 |
| 588940 | 588040 | 4.61 | 0.149 |
| 159995 | 512760 | 4.59 | 0.072 |
| 510880 | 515180 | 4.32 | 0.092 |
| 588050 | 588940 | 4.30 | 0.040 |

What moving the year line buys and what it also lets in (same labelled set, day gate held fixed):

| year line pp | accepted same-name pairs | price-refused pairs it would bless |
|---|---|---|
| 1.0 | 169 | 0 |
| 1.5 | 211 | 0 |
| 2.0 | 256 | 0 |
| 3.0 | 294 | 0 |

**The decision on the line is published, not left to each reader**: KEEP at 1.0 pp/yr -- no pair the board's own prices refused drifts less than 2.8 pp/yr, so the labelled set cannot place the line between 1.0 and there; the line is priced by what being wrong costs -- a swap made inside a 1.0 pp/yr band loses at most that band, while the 125 extra pairs a 3.0 pp line recovers each carry up to 3 pp/yr of drift. Cost: recall: 151 of the 320 same-name pairs the prices accepted are refused.

## what the year gate costs

The day gate is held fixed; only the drift line moves. Loosening it recovers same-basket pairs whose dividends differ and accepts swaps that are partly bets.

| drift line pp/yr | accepted pairs | across names | families | chains | over material | cost CNY |
|---|---|---|---|---|---|---|
| 0.5 | 483 | 266 | 7 | 30 | 2 | 1311 |
| 1.0 | 867 | 464 | 12 | 40 | 2 | 1311 |
| 2.0 | 1413 | 770 | 14 | 41 | 2 | 1601 |

## families a reader may switch inside

Families whose members are written under more than one name. Money is the dearest-vs-cheapest premium inside the family on a 100000 CNY ticket.

| names | members | cheapest | dearest | spread pp | cost CNY |
|---|---|---|---|---|---|
| 半导体ETF, 芯片ETF | 159813, 159995 | 159995 (0.12%) | 159813 (0.82%) | 0.69 | 694 |
| 中概互联ETF, 中概互联网ETF | 159605, 159607 | 159607 (-2.16%) | 159605 (-1.54%) | 0.62 | 617 |
| 港股通科技30ETF, 港股通科技ETF | 159101, 159636 | 159636 (-0.30%) | 159101 (0.05%) | 0.35 | 347 |
| 电池ETF, 锂电池ETF | 159755, 159840 | 159840 (-0.09%) | 159755 (0.21%) | 0.29 | 292 |
| 港股央企红利ETF, 港股通红利ETF | 520900, 520990 | 520990 (-0.13%) | 520900 (0.09%) | 0.23 | 227 |
| 地产ETF, 房地产ETF | 159707, 159768 | 159707 (-0.37%) | 159768 (-0.15%) | 0.22 | 225 |
| 日经225ETF, 日经ETF | 159866, 513000 | 159866 (3.13%) | 513000 (3.30%) | 0.17 | 168 |
| 港股科技ETF, 港股通科技ETF | 513160, 520980 | 520980 (-0.07%) | 513160 (0.07%) | 0.14 | 138 |
| 中证红利ETF, 红利ETF | 515080, 515180 | 515180 (-0.21%) | 515080 (-0.10%) | 0.12 | 115 |
| 港股医疗ETF, 港股通医疗ETF | 159366, 520510 | 520510 (-0.73%) | 159366 (-0.63%) | 0.10 | 104 |
| 深成ETF, 深证成指ETF | 159903, 159943 | 159903 (-0.06%) | 159943 (-0.06%) | 0.00 | 2 |
| 华宝添益ETF, 招商财富宝ETF, 货币ETF | 159001, 511620, 511660, 511700, 511850, 511990 | - | - | - | premium unobservable |

Single-name accepted families (the label census's own ground, re-derived here with the two-gate ruler): 29.

## chains: pairs that agree pairwise but not all together (no money inside)

- 恒生医药ETF, 恒生生物科技ETF, 港股创新药ETF, 港股医药ETF, 港股通创新药ETF, 港股通医药ETF -- 159102, 159105, 159615, 159718, 159776, 159892, 513120, 513200 (13 members, 51 pairs not accepted)
- 创业板ETF -- 159205, 159908, 159915, 159948, 159952, 159957, 159971, 159977 (8 members, 16 pairs not accepted)
- 机器人ETF -- 159213, 159258, 159526, 159770, 560770, 562500 (6 members, 7 pairs not accepted)
- 港股创新药ETF, 港股通创新药ETF -- 159217, 159286, 159297, 159316, 159567, 159570, 520880 (7 members, 11 pairs not accepted)
- 中证现金流ETF, 现金流ETF, 现金流ETF中银, 自由现金流ETF -- 159232, 159233, 159235, 563390, 563760 (5 members, 5 pairs not accepted)
- 创业板人工智能ETF -- 159242, 159246, 159279, 159363, 159381, 159382, 159388 (7 members, 8 pairs not accepted)
- 港股消费ETF, 港股通消费ETF -- 159245, 159265, 159268, 513070, 513230 (5 members, 5 pairs not accepted)
- 港股科技ETF, 港股通科技ETF, 港股通科技ETF海富通, 香港科技ETF, 香港科技ETF兴银 -- 159269, 159747, 513020, 513150, 513560, 513860, 513980 (7 members, 9 pairs not accepted)
- 机器人ETF -- 159272, 159278, 159530, 159559 (4 members, 3 pairs not accepted)
- A500ETF, A500ETF中金, A50ETF, A股ETF, MSCIA股ETF, 上证180ETF -- 159300, 159330, 159338, 159339, 159351, 159352, 159353, 159356 (51 members, 919 pairs not accepted)
- 红利低波100ETF, 红利低波ETF -- 159307, 159549, 515100 (3 members, 1 pairs not accepted)
- 黄金股ETF -- 159321, 159562, 517400, 517520 (4 members, 2 pairs not accepted)
- 半导体设备ETF -- 159327, 159516, 159558, 560780 (4 members, 2 pairs not accepted)
- 300红利低波ETF, 800红利低波ETF, 红利低波50ETF, 红利低波ETF -- 159355, 159525, 159547, 512890, 515300, 515450, 563020 (7 members, 14 pairs not accepted)
- 创业大盘ETF西部利得, 创业板50ETF -- 159369, 159371, 159681, 159682, 159814, 159949 (6 members, 7 pairs not accepted)
- 纳指100ETF, 纳指ETF, 纳斯达克100ETF, 纳斯达克ETF -- 159513, 159632, 159659, 159696, 159941, 513100, 513110, 513300 (10 members, 28 pairs not accepted)
- 中证2000ETF -- 159531, 159532, 563300 (3 members, 1 pairs not accepted)
- 芯片ETF -- 159560, 159599, 512760, 516350, 516640, 516920 (6 members, 9 pairs not accepted)
- 港股互联网ETF, 港股通互联网ETF -- 159568, 159792, 513770 (3 members, 1 pairs not accepted)
- 电力ETF, 绿电ETF, 绿色电力ETF -- 159611, 159625, 561170, 561560, 562550, 562960 (6 members, 9 pairs not accepted)
- ... and 20 more in the JSON

## what this face does not say

- two gates, both on PRICE only: a pair that passes is one the prices cannot tell apart for a year minus event days -- it is not a statement about the holdings
- the line is calibrated on the board's own SAME-NAME families (r1804); applying it across names is an extrapolation, and the calibration block is republished each run
- distribution policy is invisible here: two same-basket tickers that pay different dividends drift in price and are refused by gate 2 (a false refusal, not a risk)
- the money line is the dearest-vs-cheapest premium INSIDE an accepted family on a 100000 CNY ticket; it is the price of picking the wrong name, not a return
- one session of premiums: the family membership rests on a year of closes, the money on one day's board
- the screen drops tickers that did not trade every day of the window (70 here); they are counted, never filled with zeros
