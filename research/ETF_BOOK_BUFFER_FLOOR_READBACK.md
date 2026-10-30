# 缓冲轴的第一个样本外点（r1355 bm-c）

面：`results/etf_book_buffer_floor_readback.json`｜脚本：`scripts/etf_book_phase_atlas_arms.py --readback`｜臂面 `etf_book_phase_atlas_buffer_k30.json`｜cutoff 2026-10-29

r1354 用五个臂拟合出 **%+.3fpp / 单位 k**，再沿这条线外推到 k=7.79。本轮任务池交给自动续批器的第一张票正是 k=0.30——拟合区间 0.20→0.40 的中点，这条线从没见过的点。

| 读数 | 值 |
|---|---|
| 拟合预测 (k=0.30) | +0.371pp |
| 实测中位 | +0.323pp |
| 差 | -0.048pp (容差 0.972pp) |
| 拟合自身最大样本内残差 | 0.324pp |

判决：**HOLDS**

| n | R | 中位 CAGR | 基线 | Δ |
|---|---|---|---|---|
| 3 | 10 | +12.16pp | +10.87pp | +1.300pp |
| 3 | 20 | +9.76pp | +8.58pp | +1.175pp |
| 3 | 40 | +6.06pp | +6.69pp | -0.630pp |
| 5 | 10 | +12.31pp | +11.51pp | +0.800pp |
| 5 | 20 | +9.79pp | +9.09pp | +0.705pp |
| 5 | 40 | +8.06pp | +8.22pp | -0.155pp |
| 8 | 10 | +12.22pp | +11.96pp | +0.265pp |
| 8 | 20 | +10.00pp | +10.12pp | -0.115pp |
| 8 | 40 | +8.60pp | +8.22pp | +0.380pp |
| 12 | 10 | +11.64pp | +11.61pp | +0.035pp |
| 12 | 20 | +9.82pp | +9.59pp | +0.230pp |
| 12 | 40 | +8.37pp | +7.55pp | +0.815pp |

- the fit says +0.371pp at k=0.30 (slope +1.266, intercept -0.009)
- the harvested arm's own 12 cells say +0.323pp (median)
- gap -0.048pp against tolerance 0.972pp = 3.0x the fit's largest in-sample residual (0.324pp, floored at 0.05)
- cell spread of the same arm: -0.630 .. +1.300pp (12 cells), i.e. the median is not the book
- the line predicts a point it never saw, on the widest gap it spans -- the extrapolated k is a continuation of a measured slope, not a guess
