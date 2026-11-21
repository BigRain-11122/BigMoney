# 缓冲轴的第一个样本外点（r1355 bm-c）

面：`results/etf_book_buffer_floor_readback.json`｜脚本：`scripts/etf_book_phase_atlas_arms.py --readback`｜臂面 `etf_book_phase_atlas_buffer_k30.json`｜cutoff 2026-10-29

r1354 用五个臂拟合出 **%+.3fpp / 单位 k**，再沿这条线外推到 k=7.79。本轮任务池交给自动续批器的第一张票正是 k=0.30——拟合区间 0.20→0.40 的中点，这条线从没见过的点。

| 读数 | 值 |
|---|---|
| 拟合预测 (k=0.30) | +0.298pp |
| 实测中位 | +0.645pp |
| 差 | +0.347pp (容差 0.057pp) |
| 拟合自身最大样本内残差 | 0.019pp |

判决：**REFUTED**

| n | R | 中位 CAGR | 基线 | Δ |
|---|---|---|---|---|
| 3 | 10 | +12.16pp | +10.46pp | +1.705pp |
| 3 | 20 | +9.76pp | +8.32pp | +1.430pp |
| 3 | 40 | +6.06pp | +6.57pp | -0.505pp |
| 5 | 10 | +12.31pp | +11.28pp | +1.035pp |
| 5 | 20 | +9.79pp | +9.07pp | +0.715pp |
| 5 | 40 | +8.06pp | +7.66pp | +0.410pp |
| 8 | 10 | +12.22pp | +11.80pp | +0.420pp |
| 8 | 20 | +10.00pp | +10.01pp | -0.010pp |
| 8 | 40 | +8.60pp | +7.94pp | +0.660pp |
| 12 | 10 | +11.64pp | +11.25pp | +0.390pp |
| 12 | 20 | +9.82pp | +9.19pp | +0.630pp |
| 12 | 40 | +8.37pp | +7.45pp | +0.920pp |

- the fit says +0.298pp at k=0.30 (slope +1.047, intercept -0.016)
- the harvested arm's own 12 cells say +0.645pp (median)
- gap +0.347pp against tolerance 0.057pp = 3.0x the fit's largest in-sample residual (0.019pp, floored at 0.05)
- cell spread of the same arm: -0.505 .. +1.705pp (12 cells), i.e. the median is not the book
- the line misses the point it never saw by more than its own residual band: the k the floor reports is an extrapolation with no support
