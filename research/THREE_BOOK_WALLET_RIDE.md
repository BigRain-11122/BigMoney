# 三书钱包：持有它到底是什么感觉

面：`results/three_book_wallet_ride.json` · 脚本：`scripts/three_book_wallet_ride.py` · 证据截止：2026-11-26

> On the last bar (2026-11-26) the book stands -6.72% below its own high of 1.6506 set on 2026-01-29 (301 days ago) -- which is the deepest hole in the whole window, so the worst day of this book's published life is today. Held for a year from every one of 1421 start dates on the parent's own window, the recommended wallet returns a median 6.44% and a middle 80% between 1.46% and 17.69% on a 1000000 seed (+64387 / +14560 / +176866 CNY); 4.2% of starts end below their own start, the worst ends at -4.67%. The path matters more than the average: the book sits below its previous high on 91% of days, its longest such spell runs 207 bars (307 calendar days, 2022-03-10 to 2023-01-11), and the deepest hole is -6.72% on 2026-11-26, never fully recovered inside this window. Over two years the median is 13.98% with 0.0% of starts losing.

## 1. 父面给了数，没给路

`three_book_wallet` 印的是 6.51%/年、夏普 1.060、最差年 -4.03%——三个都是「全窗平均」的函数。读者真正要问的是另一句：**我从今天开始拿，一年后最可能看到多少，最差呢，中间熬不熬得住。**本面不重算任何一本书，只把父面那三条已发布的序列按 65/35/0 拼起来，把路径量一遍。

窗口 2020-01-06 → 2026-11-26（1670 根 bar）。四条臂、同一批行、同一把尺。

## 2. 今天这只钱包站在哪里

| 量 | 值 |
|---|---|
| 最新 bar | 2026-11-26 |
| 净值（起点=1） | 1.5396 |
| 自身的最高点 | 1.6506（2026-01-29） |
| 现在离开前高 | **-6.72%**（301 个日历天、198 根 bar） |

**这一格是整窗最深的那一格**：这本书自 2020-01-06 发布以来的最大回撤，就是它今天的样子。读者不需要等到某个未来的坏日子才体会 -6.72%——它正在发生。

## 3. 持有一年，结果是区间不是数字

| 臂 | 权重 ETF/转债/carry | 年化 | 夏普 | 波动 | 1 年起数 | 中位 | p10 | p90 | 亏钱起点 | 最差 |
|---|---|---|---|---|---|---|---|---|---|---|
| wallet | 65% / 35% / 0% | 6.51% | 1.060 | 6.12% | 1421 | 6.44% | 1.46% | 17.69% | 4.2% | -4.67% |
| carry_alone | 0% / 0% / 100% | 11.89% | 1.445 | 8.00% | 1421 | 11.73% | 3.91% | 21.05% | 0.1% | -1.12% |
| etf_cb_equal | 50% / 50% / 0% | 5.99% | 1.015 | 5.91% | 1421 | 6.57% | 1.00% | 15.70% | 6.3% | -6.55% |
| ungated | 35% / 15% / 50% | 9.40% | 1.844 | 4.94% | 1421 | 9.58% | 3.93% | 17.01% | 0.2% | -0.64% |

**四条臂的波动不一样，所以上表的区间不能横向相减。** 唯一能横着读的是「区间宽度按各自年化波动折算成几个 sigma」——同一条风险单位下，谁的带子更窄：

| 臂 | 1 年区间宽度（自身 sigma） |
|---|---|
| wallet | 2.65 |
| carry_alone | 2.14 |
| etf_cb_equal | 2.49 |
| ungated | 2.65 |

## 4. 换一个持有期，带子怎么变

| 持有期 | 中位 | p10 | p90 | 亏钱起点 | 最差 | 最好 |
|---|---|---|---|---|---|---|
| 3m | 1.49% | -1.80% | 5.67% | 28.1% | -4.64% | 13.29% |
| 6m | 3.57% | -1.33% | 9.28% | 22.6% | -5.00% | 16.12% |
| 1y | 6.44% | 1.46% | 17.69% | 4.2% | -4.67% | 29.25% |
| 2y | 13.98% | 4.94% | 32.50% | 0.0% | 0.07% | 41.10% |

## 5. 一百万放进这只钱包，一年后大概看到什么

| 读数 | 金额（元，对 1,000,000 本金） |
|---|---|
| p10（十次里最差那次附近） | +14,560 |
| 中位 | +64,387 |
| p90（十次里最好那次附近） | +176,866 |

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

依据：1 年期 4.2% 的起点是亏的，p90/p10 = 12.15。这与父面「夏普 1.060」并不矛盾——夏普是对数收益的比值，区间是路径的形状；同一本书可以既有不错的夏普，又有很宽的带子。

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

