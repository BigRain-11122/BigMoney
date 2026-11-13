# 缓冲轴的第一个样本外点（r1355 bm-c）

面：`results/etf_book_buffer_floor_readback.json`｜脚本：`scripts/etf_book_phase_atlas_arms.py --readback`｜臂面 `etf_book_phase_atlas_buffer_k30.json`｜cutoff 2026-10-29

r1354 用五个臂拟合出 **%+.3fpp / 单位 k**，再沿这条线外推到 k=7.79。本轮任务池交给自动续批器的第一张票正是 k=0.30——拟合区间 0.20→0.40 的中点，这条线从没见过的点。

| 读数 | 值 |
|---|---|
| 拟合预测 (k=0.30) | +0.227pp |
| 实测中位 | +0.318pp |
| 差 | +0.091pp (容差 0.077pp) |
| 拟合自身最大样本内残差 | 0.026pp |

判决：**REFUTED**

| n | R | 中位 CAGR | 基线 | Δ |
|---|---|---|---|---|
| 3 | 10 | +12.16pp | +10.82pp | +1.340pp |
| 3 | 20 | +9.76pp | +8.48pp | +1.275pp |
| 3 | 40 | +6.06pp | +6.74pp | -0.675pp |
| 5 | 10 | +12.31pp | +11.45pp | +0.865pp |
| 5 | 20 | +9.79pp | +9.06pp | +0.725pp |
| 5 | 40 | +8.06pp | +8.24pp | -0.175pp |
| 8 | 10 | +12.22pp | +11.92pp | +0.305pp |
| 8 | 20 | +10.00pp | +10.12pp | -0.115pp |
| 8 | 40 | +8.60pp | +8.27pp | +0.330pp |
| 12 | 10 | +11.64pp | +11.54pp | +0.100pp |
| 12 | 20 | +9.82pp | +9.61pp | +0.215pp |
| 12 | 40 | +8.37pp | +7.78pp | +0.585pp |

- the fit says +0.227pp at k=0.30 (slope +0.824, intercept -0.020)
- the harvested arm's own 12 cells say +0.318pp (median)
- gap +0.091pp against tolerance 0.077pp = 3.0x the fit's largest in-sample residual (0.026pp, floored at 0.05)
- cell spread of the same arm: -0.675 .. +1.340pp (12 cells), i.e. the median is not the book
- the line misses the point it never saw by more than its own residual band: the k the floor reports is an extrapolation with no support
