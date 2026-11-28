# 三书钱包：持有它到底是什么感觉

面：`results/three_book_wallet_ride.json` · 脚本：`scripts/three_book_wallet_ride.py` · 证据截止：2026-11-27

> On the last bar (2026-11-27) the book stands -6.31% below its own high of 1.6506 set on 2026-01-29 (302 days ago). Held for a year from every one of 1422 start dates on the parent's own window, the recommended wallet returns a median 6.44% and a middle 80% between 1.44% and 17.69% on a 1000000 seed (+64364 / +14406 / +176889 CNY); 4.2% of starts end below their own start, the worst ends at -4.67%. The path matters more than the average: the book sits below its previous high on 91% of days, its longest such spell runs 207 bars (307 calendar days, 2022-03-10 to 2023-01-11), and the deepest hole is -6.72% on 2026-11-26, never fully recovered inside this window. Over two years the median is 13.99% with 0.0% of starts losing.

## 1. 父面给了数，没给路

`three_book_wallet` 印的是 6.51%/年、夏普 1.060、最差年 -4.03%——三个都是「全窗平均」的函数。读者真正要问的是另一句：**我从今天开始拿，一年后最可能看到多少，最差呢，中间熬不熬得住。**本面不重算任何一本书，只把父面那三条已发布的序列按 65/35/0 拼起来，把路径量一遍。

窗口 2020-01-06 → 2026-11-27（1671 根 bar）。四条臂、同一批行、同一把尺。

## 2. 今天这只钱包站在哪里

| 量 | 值 |
|---|---|
| 最新 bar | 2026-11-27 |
| 净值（起点=1） | 1.5464 |
| 自身的最高点 | 1.6506（2026-01-29） |
| 现在离开前高 | **-6.31%**（302 个日历天、199 根 bar） |

今天不是最深的一格（整窗最深 -6.72% 在 2026-11-26）。

## 3. 持有一年，结果是区间不是数字

| 臂 | 权重 ETF/转债/carry | 年化 | 夏普 | 波动 | 1 年起数 | 中位 | p10 | p90 | 亏钱起点 | 最差 |
|---|---|---|---|---|---|---|---|---|---|---|
| wallet | 65% / 35% / 0% | 6.57% | 1.070 | 6.12% | 1422 | 6.44% | 1.44% | 17.69% | 4.2% | -4.67% |
| carry_alone | 0% / 0% / 100% | 12.16% | 1.475 | 8.00% | 1422 | 11.69% | 3.90% | 20.96% | 0.1% | -1.12% |
| etf_cb_equal | 50% / 50% / 0% | 6.06% | 1.027 | 5.91% | 1422 | 6.56% | 0.99% | 15.70% | 6.4% | -6.55% |
| ungated | 30% / 20% / 50% | 9.39% | 1.873 | 4.86% | 1422 | 9.89% | 3.53% | 16.17% | 0.4% | -0.96% |

**四条臂的波动不一样，所以上表的区间不能横向相减。** 唯一能横着读的是「区间宽度按各自年化波动折算成几个 sigma」——同一条风险单位下，谁的带子更窄：

| 臂 | 1 年区间宽度（自身 sigma） |
|---|---|
| wallet | 2.65 |
| carry_alone | 2.13 |
| etf_cb_equal | 2.49 |
| ungated | 2.60 |

## 4. 换一个持有期，带子怎么变

| 持有期 | 中位 | p10 | p90 | 亏钱起点 | 最差 | 最好 |
|---|---|---|---|---|---|---|
| 3m | 1.49% | -1.83% | 5.67% | 28.2% | -4.64% | 13.29% |
| 6m | 3.56% | -1.34% | 9.28% | 22.7% | -5.00% | 16.12% |
| 1y | 6.44% | 1.44% | 17.69% | 4.2% | -4.67% | 29.25% |
| 2y | 13.99% | 4.94% | 32.49% | 0.0% | 0.07% | 41.10% |

## 5. 一百万放进这只钱包，一年后大概看到什么

| 读数 | 金额（元，对 1,000,000 本金） |
|---|---|
| p10（十次里最差那次附近） | +14,406 |
| 中位 | +64,364 |
| p90（十次里最好那次附近） | +176,889 |

## 6. 路有多长：水下时间与爬坑

| 量 | 值 |
|---|---|
| 处于前高之下的日子占比 | 90.8% |
| 最长一段水下 | 207 根 bar（307 个日历天） |
| 那一段 | 2022-03-10 → 2023-01-11 |
| 最深的坑 | -6.72%（2026-11-26） |
| 从坑底爬回前高 | 本窗内没有再回前高 |

## 7. 判词

`A_YEAR_IS_A_RANGE_NOT_A_NUMBER`

依据：1 年期 4.2% 的起点是亏的，p90/p10 = 12.28。这与父面「夏普 1.060」并不矛盾——夏普是对数收益的比值，区间是路径的形状；同一本书可以既有不错的夏普，又有很宽的带子。

## 8. 本面不证明什么

- the distribution of a past window is not a forecast: this is the shape a person would have sat through, 2020-2026
- no strategy is recomputed here -- all three books come from three_book_wallet.load_books(), same primitives the parent uses
- the arms carry different realised vol, so their absolute ranges are not comparable; range_in_own_sigmas is the only cross-arm reading printed
- carry is the hedged excess, gross of the hedge leg's cost; a real hedge needs a second account (parent caliber, not re-estimated)
- no rebalancing cost beyond what each book already books; the wallet's weights are held, not traded

## 9. 复跑与守卫

```
python scripts\three_book_wallet_ride.py run       # 重算并写面
python scripts\three_book_wallet_ride.py check     # 上游动了=STALE(rc3)；自相矛盾=CHECK FAILED(rc2)
python scripts\three_book_wallet_ride.py selftest  # 离线自检
```

`check` 的三件事：①任何上游面（父面 / 三本书 / 面板）字节或 mtime 变了 → `STALE`；②钱包臂必须逐位复现父面 `best_inside_gate`（cagr/sharpe/vol/maxdd 容差 5e-6）——不等说明引用了另一把尺子，=`CHECK FAILED`（不带 STALE 字样）；③bar 数必须等于父面窗口 bar 数。

