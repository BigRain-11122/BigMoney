# 年度线的可达性：冻结网格里有没有一个格子能过（etf_book_year_line_reach）

截至 2026-11-27，源面 results/etf_book_year_gate/YEAR-GATE.json（asof 2026-11-27T20:53:33+0800），线 = top-2 年份占年度收益之和 ≤ 70.00%。

**判词：REACHED_BY_A_CELL**（测了 12 个格子）

对照格（n=5, R=20, 10bp）重算得 top-2 = 73.45%、年化 10.94%，与已发布面逐位一致；网格只动选股宽度与调仓周期，成本与 8% 波动目标保持已采纳规则。

## 每一格

| 格 | 年化% | top-2% | 距线 pp | 相对对照年化 pp | 正年占比 | 最差年% | 容量亿 | 换手/边 |
|---|---|---|---|---|---|---|---|---|
| N3_R10_10bp | 11.11 | 68.12 | -1.88 | +0.17 | 0.71 | -5.65 | 0.21 | 1.00 |
| N3_R20_10bp | 10.22 | 75.10 | +5.10 | -0.72 | 0.71 | -1.87 | 0.21 | 1.09 |
| N3_R40_10bp | 5.76 | 98.18 | +28.18 | -5.18 | 0.57 | -6.54 | 0.21 | 1.15 |
| N5_R10_10bp | 11.61 | 70.67 | +0.67 | +0.67 | 0.71 | -3.45 | 0.33 | 0.95 |
| N5_R20_10bp | 10.94 | 73.45 | +3.45 | +0.00 | 0.86 | -0.72 | 0.33 | 1.08 |
| N5_R40_10bp | 6.45 | 78.12 | +8.12 | -4.49 | 0.71 | -4.48 | 0.33 | 1.13 |
| N8_R10_10bp | 12.36 | 73.54 | +3.54 | +1.42 | 0.71 | -2.84 | 1.07 | 0.91 |
| N8_R20_10bp | 10.09 | 78.66 | +8.66 | -0.85 | 0.86 | -1.77 | 1.07 | 1.02 |
| N8_R40_10bp | 6.18 | 80.07 | +10.07 | -4.76 | 0.57 | -2.48 | 1.07 | 1.11 |
| N12_R10_10bp | 12.00 | 74.03 | +4.03 | +1.06 | 0.71 | -0.80 | 1.68 | 0.83 |
| N12_R20_10bp | 8.94 | 79.54 | +9.54 | -2.00 | 0.71 | -1.99 | 1.68 | 0.94 |
| N12_R40_10bp | 6.22 | 81.52 | +11.52 | -4.72 | 0.71 | -6.96 | 1.68 | 1.04 |

**过线的格：N3_R10_10bp** —— 年化 11.11%（相对对照 +0.17 pp），top-2 68.12%（低于线 1.88 pp），容量 0.21 亿（门槛 0.20 亿），当前持仓 515020/512820/515290。


## 差距的两种货币

同一句「差 3.45 pp 的年度之和」，换成年份就是：

- 让最好的一年（2025，+43.06%）退回 **9.02 pp**（相对砍 20.95%）其余年份不动；
- **或者**让未完成的一年（2026，-0.72%）多赚 **3.87 pp**（到 3.14%），其余年份不动。

第二把更小，而且那是唯一还能变的年份：2026 到截止日仍未收年，线其实是在给一个未走完的年份定价。

## 诚实边界

- the control must reproduce the published face within 5e-05 on the share and 0.05 pp on CAGR; a failure refuses the page rather than printing a new world
- the line reads the net sum with the unfinished year included (the gate's own published definition); the full-years-only reading is higher, never lower
- the current year is unfinished at the cutoff, so the lift it needs is measured against a return that will still move
- a cell that passes the share can still fail capacity: this page moves the selection width, and a 3-name book concentrates the same money into fewer slots -- capacity at 5%% participation is printed on the gate face, not here
