# 年度线的可达性：冻结网格里有没有一个格子能过（etf_book_year_line_reach）

截至 2026-11-25，源面 results/etf_book_year_gate/YEAR-GATE.json（asof 2026-11-26T03:29:09+0800），线 = top-2 年份占年度收益之和 ≤ 70.00%。

**判词：REACHED_IN_SHAPE_NOT_IN_CAPACITY**（测了 12 个格子）

对照格（n=5, R=20, 10bp）重算得 top-2 = 73.37%、年化 10.96%，与已发布面逐位一致；网格只动选股宽度与调仓周期，成本与 8% 波动目标保持已采纳规则。

## 每一格

| 格 | 年化% | top-2% | 距线 pp | 相对对照年化 pp | 正年占比 | 最差年% | 容量亿 | 换手/边 |
|---|---|---|---|---|---|---|---|---|
| N3_R10_10bp | 11.15 | 67.97 | -2.03 | +0.19 | 0.71 | -5.65 | 0.14 | 0.99 |
| N3_R20_10bp | 10.29 | 74.70 | +4.70 | -0.67 | 0.71 | -1.87 | 0.14 | 1.09 |
| N3_R40_10bp | 5.67 | 99.52 | +29.52 | -5.29 | 0.57 | -7.09 | 0.14 | 1.15 |
| N5_R10_10bp | 11.64 | 70.54 | +0.54 | +0.68 | 0.71 | -3.31 | 0.21 | 0.95 |
| N5_R20_10bp | 10.96 | 73.37 | +3.37 | +0.00 | 0.86 | -0.64 | 0.21 | 1.08 |
| N5_R40_10bp | 6.39 | 78.82 | +8.82 | -4.57 | 0.71 | -4.87 | 0.21 | 1.13 |
| N8_R10_10bp | 12.39 | 73.45 | +3.45 | +1.43 | 0.71 | -2.73 | 0.86 | 0.91 |
| N8_R20_10bp | 10.13 | 78.44 | +8.44 | -0.83 | 0.86 | -1.55 | 0.86 | 1.02 |
| N8_R40_10bp | 6.07 | 81.35 | +11.35 | -4.89 | 0.57 | -3.17 | 0.86 | 1.11 |
| N12_R10_10bp | 12.02 | 73.98 | +3.98 | +1.06 | 0.71 | -0.74 | 1.11 | 0.83 |
| N12_R20_10bp | 8.98 | 79.29 | +9.29 | -1.98 | 0.71 | -1.99 | 1.11 | 0.94 |
| N12_R40_10bp | 6.11 | 82.83 | +12.83 | -4.85 | 0.57 | -6.96 | 1.11 | 1.04 |

**年度四面全过的格：N3_R10_10bp** —— top-2 67.97%（低于线 2.03 pp）、年化 11.15%，但一日容量 0.14 亿低于门的 0.20 亿：形状可达，尺寸不可达。

这不是「没路」，是两条路各自缺一样东西：**缩短持有能救年份形状**（n=3、10 日调仓，top-2 降到 67.97%），但三只票吃不下 0.20 亿的门；**保持五只票**容量够，却只能在 10 日调仓下把 top-2 压到 70.54%（差 -0.54 pp）。


## 差距的两种货币

同一句「差 3.37 pp 的年度之和」，换成年份就是：

- 让最好的一年（2025，+43.06%）退回 **8.82 pp**（相对砍 20.47%）其余年份不动；
- **或者**让未完成的一年（2026，-0.64%）多赚 **3.78 pp**（到 3.14%），其余年份不动。

第二把更小，而且那是唯一还能变的年份：2026 到截止日仍未收年，线其实是在给一个未走完的年份定价。

## 诚实边界

- the control must reproduce the published face within 5e-05 on the share and 0.05 pp on CAGR; a failure refuses the page rather than printing a new world
- the line reads the net sum with the unfinished year included (the gate's own published definition); the full-years-only reading is higher, never lower
- the current year is unfinished at the cutoff, so the lift it needs is measured against a return that will still move
- a cell that passes the share can still fail capacity: this page moves the selection width, and a 3-name book concentrates the same money into fewer slots -- capacity at 5%% participation is printed on the gate face, not here
