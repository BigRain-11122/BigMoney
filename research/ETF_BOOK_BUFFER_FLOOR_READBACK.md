# 缓冲轴的第一个样本外点（r1355 bm-c）

面：`results/etf_book_buffer_floor_readback.json`｜脚本：`scripts/etf_book_phase_atlas_arms.py --readback`｜臂面 `etf_book_phase_atlas_buffer_k30.json`｜cutoff 2026-10-29

r1354 用五个臂拟合出 **%+.3fpp / 单位 k**，再沿这条线外推到 k=7.79。本轮任务池交给自动续批器的第一张票正是 k=0.30——拟合区间 0.20→0.40 的中点，这条线从没见过的点。

| 读数 | 值 |
|---|---|
| 拟合预测 (k=0.30) | +0.327pp |
| 实测中位 | +0.407pp |
| 差 | +0.080pp (容差 0.976pp) |
| 拟合自身最大样本内残差 | 0.325pp |

判决：**HOLDS**

| n | R | 中位 CAGR | 基线 | Δ |
|---|---|---|---|---|
| 3 | 10 | +12.16pp | +10.61pp | +1.560pp |
| 3 | 20 | +9.76pp | +8.48pp | +1.270pp |
| 3 | 40 | +6.06pp | +6.67pp | -0.615pp |
| 5 | 10 | +12.31pp | +11.44pp | +0.870pp |
| 5 | 20 | +9.79pp | +9.18pp | +0.610pp |
| 5 | 40 | +8.06pp | +7.88pp | +0.185pp |
| 8 | 10 | +12.22pp | +11.96pp | +0.265pp |
| 8 | 20 | +10.00pp | +10.18pp | -0.180pp |
| 8 | 40 | +8.60pp | +8.17pp | +0.430pp |
| 12 | 10 | +11.64pp | +11.46pp | +0.185pp |
| 12 | 20 | +9.82pp | +9.44pp | +0.385pp |
| 12 | 40 | +8.37pp | +7.67pp | +0.700pp |

- the fit says +0.327pp at k=0.30 (slope +0.858, intercept +0.070)
- the harvested arm's own 12 cells say +0.407pp (median)
- gap +0.080pp against tolerance 0.976pp = 3.0x the fit's largest in-sample residual (0.325pp, floored at 0.05)
- cell spread of the same arm: -0.615 .. +1.560pp (12 cells), i.e. the median is not the book
- the line predicts a point it never saw, on the widest gap it spans -- the extrapolated k is a continuation of a measured slope, not a guess
