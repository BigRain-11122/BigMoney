# 缓冲轴的第一个样本外点（r1355 bm-c）

面：`results/etf_book_buffer_floor_readback.json`｜脚本：`scripts/etf_book_phase_atlas_arms.py --readback`｜臂面 `etf_book_phase_atlas_buffer_k30.json`｜cutoff 2026-10-29

r1354 用五个臂拟合出 **%+.3fpp / 单位 k**，再沿这条线外推到 k=7.79。本轮任务池交给自动续批器的第一张票正是 k=0.30——拟合区间 0.20→0.40 的中点，这条线从没见过的点。

| 读数 | 值 |
|---|---|
| 拟合预测 (k=0.30) | +0.319pp |
| 实测中位 | +0.770pp |
| 差 | +0.451pp (容差 0.209pp) |
| 拟合自身最大样本内残差 | 0.070pp |

判决：**REFUTED**

| n | R | 中位 CAGR | 基线 | Δ |
|---|---|---|---|---|
| 3 | 10 | +12.16pp | +10.22pp | +1.945pp |
| 3 | 20 | +9.76pp | +8.24pp | +1.510pp |
| 3 | 40 | +6.06pp | +6.26pp | -0.205pp |
| 5 | 10 | +12.31pp | +11.04pp | +1.265pp |
| 5 | 20 | +9.79pp | +8.82pp | +0.965pp |
| 5 | 40 | +8.06pp | +7.45pp | +0.620pp |
| 8 | 10 | +12.22pp | +11.53pp | +0.700pp |
| 8 | 20 | +10.00pp | +9.79pp | +0.210pp |
| 8 | 40 | +8.60pp | +7.84pp | +0.755pp |
| 12 | 10 | +11.64pp | +11.05pp | +0.585pp |
| 12 | 20 | +9.82pp | +9.04pp | +0.785pp |
| 12 | 40 | +8.37pp | +7.16pp | +1.205pp |

- the fit says +0.319pp at k=0.30 (slope +1.217, intercept -0.046)
- the harvested arm's own 12 cells say +0.770pp (median)
- gap +0.451pp against tolerance 0.209pp = 3.0x the fit's largest in-sample residual (0.070pp, floored at 0.05)
- cell spread of the same arm: -0.205 .. +1.945pp (12 cells), i.e. the median is not the book
- the line misses the point it never saw by more than its own residual band: the k the floor reports is an extrapolation with no support
