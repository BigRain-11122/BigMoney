# 年度线的可达性：冻结网格里有没有一个格子能过（etf_book_year_line_reach）

截至 2026-11-26，源面 results/etf_book_year_gate/YEAR-GATE.json（asof 2026-11-27T20:05:44+0800），线 = top-2 年份占年度收益之和 ≤ 70.00%。

**判词：REACHED_IN_SHAPE_NOT_IN_CAPACITY**（测了 12 个格子）

对照格（n=5, R=20, 10bp）重算得 top-2 = 73.78%、年化 10.89%，与已发布面逐位一致；网格只动选股宽度与调仓周期，成本与 8% 波动目标保持已采纳规则。

## 每一格

| 格 | 年化% | top-2% | 距线 pp | 相对对照年化 pp | 正年占比 | 最差年% | 容量亿 | 换手/边 |
|---|---|---|---|---|---|---|---|---|
| N3_R10_10bp | 11.10 | 68.21 | -1.79 | +0.21 | 0.71 | -5.65 | 0.14 | 1.00 |
| N3_R20_10bp | 10.23 | 75.07 | +5.07 | -0.66 | 0.71 | -1.87 | 0.14 | 1.09 |
| N3_R40_10bp | 5.65 | 99.79 | +29.79 | -5.24 | 0.57 | -7.20 | 0.14 | 1.15 |
| N5_R10_10bp | 11.61 | 70.69 | +0.69 | +0.72 | 0.71 | -3.48 | 0.22 | 0.95 |
| N5_R20_10bp | 10.89 | 73.78 | +3.78 | +0.00 | 0.86 | -1.08 | 0.22 | 1.08 |
| N5_R40_10bp | 6.36 | 79.14 | +9.14 | -4.53 | 0.71 | -5.05 | 0.22 | 1.13 |
| N8_R10_10bp | 12.35 | 73.59 | +3.59 | +1.46 | 0.71 | -2.90 | 0.35 | 0.91 |
| N8_R20_10bp | 10.06 | 78.87 | +8.87 | -0.83 | 0.86 | -1.96 | 0.35 | 1.02 |
| N8_R40_10bp | 6.05 | 81.56 | +11.55 | -4.84 | 0.57 | -3.28 | 0.35 | 1.11 |
| N12_R10_10bp | 11.97 | 74.21 | +4.21 | +1.08 | 0.71 | -1.01 | 0.68 | 0.83 |
| N12_R20_10bp | 8.92 | 79.76 | +9.76 | -1.97 | 0.71 | -1.99 | 0.68 | 0.94 |
| N12_R40_10bp | 6.09 | 83.11 | +13.11 | -4.80 | 0.57 | -6.96 | 0.68 | 1.04 |

**年度四面全过的格：N3_R10_10bp** —— top-2 68.21%（低于线 1.79 pp）、年化 11.10%，但一日容量 0.14 亿低于门的 0.20 亿：形状可达，尺寸不可达。

这不是「没路」，是两条路各自缺一样东西：**缩短持有能救年份形状**（n=3、10 日调仓，top-2 降到 68.21%），但三只票吃不下 0.20 亿的门；**保持五只票**容量够，却只能在 10 日调仓下把 top-2 压到 70.69%（差 -0.69 pp）。


## 差距的两种货币

同一句「差 3.78 pp 的年度之和」，换成年份就是：

- 让最好的一年（2025，+43.06%）退回 **9.84 pp**（相对砍 22.86%）其余年份不动；
- **或者**让未完成的一年（2026，-1.08%）多赚 **4.22 pp**（到 3.14%），其余年份不动。

第二把更小，而且那是唯一还能变的年份：2026 到截止日仍未收年，线其实是在给一个未走完的年份定价。

## 诚实边界

- the control must reproduce the published face within 5e-05 on the share and 0.05 pp on CAGR; a failure refuses the page rather than printing a new world
- the line reads the net sum with the unfinished year included (the gate's own published definition); the full-years-only reading is higher, never lower
- the current year is unfinished at the cutoff, so the lift it needs is measured against a return that will still move
- a cell that passes the share can still fail capacity: this page moves the selection width, and a 3-name book concentrates the same money into fewer slots -- capacity at 5%% participation is printed on the gate face, not here
