# 盘口的价差，收得回来吗（2026-11-16）

1050 对「价格上是同一个篮子」里，837 对今天这么宽的历史样本够厚：其中 218 对二十个交易日后价差收窄到付完四边成本还有剩，619 对收不回来；按一手 100,000 元算，捡得回来的合计 102,755 元（过物质线的 100 对、78,753 元）。

口径：候选=两普查面（同名族 results/etf_label_census.json 与异名族 results/etf_alias_census.json 里被判为同一篮子的对，去重后 1050 对）；窗 250 个交易日；持有 20 个交易日（一个调仓网格）；四边成本 0.32 pp；一手 100,000 元。

| 计数 | 对数 |
| --- | --- |
| 候选对 | 1050 |
| 样本够厚 | 837 |
| 收得回来 | 218 |
| 收不回来 | 619 |
| 今天这么宽的历史不足 8 次 | 213 |
| 没有本地日线 | 0 |

## 收得回来的（按净额排序，前 20）

| A | B | 同名 | 今日价差 pp | 今日分位 | 今日宽度 pp | 历史样本 | 收窄 pp | 净 pp | 一手净额 元 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 588450 | 588460 | 是 | -6.12 | 8.4 | +5.29 | 10 | +3.38 | +3.06 | 3,060 |
| 159601 | 515390 | 否 | -0.87 | 13.6 | +2.31 | 37 | +1.68 | +1.36 | 1,358 |
| 159362 | 510330 | 否 | +1.12 | 13.6 | +3.25 | 33 | +1.65 | +1.33 | 1,329 |
| 159356 | 515310 | 否 | +0.98 | 14.0 | +3.29 | 39 | +1.57 | +1.25 | 1,253 |
| 510180 | 515390 | 否 | +0.28 | 96.8 | +2.95 | 40 | +1.54 | +1.22 | 1,218 |
| 512070 | 515630 | 是 | +3.26 | 98.4 | +1.54 | 10 | +1.44 | +1.12 | 1,124 |
| 516650 | 561330 | 否 | +0.45 | 92.0 | +1.38 | 26 | +1.44 | +1.12 | 1,120 |
| 515310 | 563220 | 否 | -0.96 | 85.6 | +3.31 | 35 | +1.44 | +1.12 | 1,119 |
| 159320 | 159326 | 否 | -0.90 | 3.2 | +1.63 | 37 | +1.41 | +1.09 | 1,094 |
| 159356 | 159925 | 否 | -0.09 | 4.4 | +3.57 | 10 | +1.41 | +1.09 | 1,092 |
| 515390 | 563360 | 否 | -0.97 | 86.4 | +3.45 | 33 | +1.37 | +1.05 | 1,053 |
| 159925 | 512090 | 否 | +0.58 | 96.4 | +1.28 | 9 | +1.31 | +0.99 | 988 |
| 159352 | 515310 | 否 | +0.98 | 15.2 | +3.56 | 36 | +1.30 | +0.98 | 978 |
| 159330 | 159356 | 否 | -0.61 | 88.0 | +2.88 | 30 | +1.29 | +0.97 | 972 |
| 159330 | 563220 | 否 | -0.60 | 86.8 | +3.02 | 32 | +1.27 | +0.95 | 955 |
| 159105 | 513700 | 否 | -0.71 | 0.8 | +1.43 | 9 | +1.27 | +0.95 | 953 |
| 159300 | 515800 | 否 | +0.25 | 90.4 | +2.19 | 27 | +1.18 | +0.86 | 862 |
| 159353 | 159919 | 否 | +1.06 | 15.2 | +2.06 | 36 | +1.18 | +0.86 | 859 |
| 512080 | 515330 | 否 | +0.56 | 12.8 | +2.87 | 36 | +1.18 | +0.86 | 856 |
| 159925 | 512050 | 否 | -0.71 | 86.4 | +2.73 | 33 | +1.17 | +0.85 | 854 |

过物质线（净额 ≥ +0.50 pp）的 100 对合计 78,753 元。

## 收不回来的（前 10，按净额最差）

| A | B | 今日价差 pp | 历史样本 | 收窄 pp | 净 pp |
| --- | --- | --- | --- | --- | --- |
| 588290 | 588990 | -0.48 | 53 | -0.13 | -0.45 |
| 159102 | 520700 | -0.20 | 188 | -0.06 | -0.38 |
| 588990 | 589190 | +0.63 | 52 | -0.04 | -0.36 |
| 159632 | 159696 | +0.34 | 91 | -0.03 | -0.35 |
| 512560 | 512680 | +2.23 | 19 | -0.02 | -0.34 |
| 159929 | 159938 | +0.11 | 220 | -0.01 | -0.33 |
| 159696 | 513870 | +0.28 | 226 | -0.01 | -0.33 |
| 512050 | 563800 | -0.01 | 226 | -0.01 | -0.33 |
| 588710 | 589020 | +0.90 | 19 | -0.01 | -0.33 |
| 510360 | 515390 | -2.04 | 64 | -0.00 | -0.32 |

## 不许偷懒的三条

1. **今天这么宽一次都没出现过的对不进判词**：样本不足 8 次的对单列（213 对），不写成「收不回来」。
2. **没有溢价锚时量的是价格比，不是溢价**：长期漂移（费率/分红）的对已被普查的年门拒掉，这条前提写在这里而不是当成事实。
3. **钱是一手的名义额，不是这本书今天卖了多少**：100000 元一手让两对之间可比，但它不是这一单的实际规模。

## 限制条款（面的原文）

- this prices one exchange and one exchange back at the horizon; it is not a book backtest -- nothing else moves, and no other name is re-ranked inside the horizon
- the harvest is a better entry into the same basket, not a realised gain: what the pair hands back is what decides whether a second exchange pays for its own four sides
- with no premium anchor the path measured is the price ratio, not the premium; pairs whose ratio trends are refused upstream by the census year gate, and that premise is stated here rather than assumed
- the ticket size is a stated 100,000 CNY, not this book's traded notional -- the board's answer is per comparable ticket, so two pairs are comparable to each other
- the pairs are alternatives to one another, not a portfolio: the board total adds up the harvest of many pairs, and one ticket can only make one of those choices
- a cohort member whose forward window is not inside the panel is censored, never scored as a zero change
- width is measured from the pair's own window median, so the unknown NAV-base constant cancels; that also means the face never claims to know which of the two tickers is the expensive one on a pair with no premium anchor
