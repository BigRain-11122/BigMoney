# 缓冲轴的第一个样本外点（r1355 bm-c）

面：`results/etf_book_buffer_floor_readback.json`｜脚本：`scripts/etf_book_phase_atlas_arms.py --readback`｜臂面 `etf_book_phase_atlas_buffer_k30.json`｜cutoff 2026-10-29

r1354 用五个臂拟合出 **%+.3fpp / 单位 k**，再沿这条线外推到 k=7.79。本轮任务池交给自动续批器的第一张票正是 k=0.30——拟合区间 0.20→0.40 的中点，这条线从没见过的点。

| 读数 | 值 |
|---|---|
| 拟合预测 (k=0.30) | +0.246pp |
| 实测中位 | +0.487pp |
| 差 | +0.241pp (容差 0.287pp) |
| 拟合自身最大样本内残差 | 0.096pp |

判决：**HOLDS**

| n | R | 中位 CAGR | 基线 | Δ |
|---|---|---|---|---|
| 3 | 10 | +12.16pp | +10.77pp | +1.400pp |
| 3 | 20 | +9.76pp | +8.46pp | +1.295pp |
| 3 | 40 | +6.06pp | +6.66pp | -0.595pp |
| 5 | 10 | +12.31pp | +11.44pp | +0.875pp |
| 5 | 20 | +9.79pp | +9.07pp | +0.715pp |
| 5 | 40 | +8.06pp | +8.10pp | -0.035pp |
| 8 | 10 | +12.22pp | +11.94pp | +0.290pp |
| 8 | 20 | +10.00pp | +10.06pp | -0.060pp |
| 8 | 40 | +8.60pp | +8.03pp | +0.575pp |
| 12 | 10 | +11.64pp | +11.44pp | +0.200pp |
| 12 | 20 | +9.82pp | +9.42pp | +0.400pp |
| 12 | 40 | +8.37pp | +7.70pp | +0.665pp |

- the fit says +0.246pp at k=0.30 (slope +0.887, intercept -0.020)
- the harvested arm's own 12 cells say +0.487pp (median)
- gap +0.241pp against tolerance 0.287pp = 3.0x the fit's largest in-sample residual (0.096pp, floored at 0.05)
- cell spread of the same arm: -0.595 .. +1.400pp (12 cells), i.e. the median is not the book
- the line predicts a point it never saw, on the widest gap it spans -- the extrapolated k is a continuation of a measured slope, not a guess
