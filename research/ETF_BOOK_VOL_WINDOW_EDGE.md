# 60 日窗口的冠军落在上一张网格的边上——把网格往下延，阶梯会拐弯吗？

证据面：`results/etf_book_vol_window_phase.json` 的下一张冻结面。证据截止 2026-11-19，1666 根 bar，7 个窗口 × 4 条相位，92.6 秒。

## 判决

**EDGE_AT_FLOOR —— 还在最边上（是方向，不是水平）**

- 最高平均夏普的窗口 = **20 日**（1.1055）；在册 60 日 = 0.9835；差 **+0.1220**。
- 冻结采用规则（**从上一张面继承，不是重写**）：ADOPT_WINDOW 在 **4/4** 条相位上赢过在册值。
- 配对裁决：**MIXED_ACROSS_PHASES**。
- 在册窗口留不留：**留** —— 冠军还是「覆盖真正能跑到的最小窗口」：这是方向、不是水平，方向不能直接外推成配置改动。真正能跑的窗口地板是 20d（发动机自己的最小估计史决定的）；低于它的 5d、10d、15d 跑的是「把覆盖关掉」，是同一个臂，不是 3 个网格点。

## 平均夏普曲线（跨相位）

| 窗口 | 平均夏普 | 最差相位 | 最好相位 | 跑得动吗 |
|---|---|---|---|---|
| 20d | 1.1055 | 1.0260 | 1.1760 | 是 |
| 25d | 1.1030 | 1.0180 | 1.1880 | 是 |
| 30d | 1.0760 | 0.9790 | 1.2090 | 是 |
| 60d | 0.9835 | 0.8740 | 1.1590 | 是 |
| 5d | — | — | — | **否（发动机不出估计，等于把覆盖关掉）** |
| 10d | — | — | — | **否（发动机不出估计，等于把覆盖关掉）** |
| 15d | — | — | — | **否（发动机不出估计，等于把覆盖关掉）** |

真正能跑的窗口地板是 20d（发动机自己的最小估计史决定的）；低于它的 5d、10d、15d 跑的是「把覆盖关掉」，是同一个臂，不是 3 个网格点

重复臂（同一批行 = 同一个臂，不是一个网格点）：5d、10d、15d。

在噪声带（0.02 夏普）之内的窗口：20d、25d —— 所以「拐点」如果是平台，结论要说平台，不能说成某个精确值。

## 逐相位

| 相位 | 5d | 10d | 15d | 20d | 25d | 30d | 60d |
|---|---|---|---|---|---|---|---|
| 0 | 0.967 | 0.967 | 0.967 | 1.071 | 1.090 | 1.041 | 0.969 |
| 1 | 0.907 | 0.907 | 0.907 | 1.149 | 1.116 | 1.075 | 0.932 |
| 2 | 0.868 | 0.868 | 0.868 | 1.026 | 1.018 | 0.979 | 0.874 |
| 3 | 1.134 | 1.134 | 1.134 | 1.176 | 1.188 | 1.209 | 1.159 |

## 配对尺子（最好窗口 vs 在册 60 日）

| 相位 | 配对均值 | 5%-95% 带 | 为正的份额 |
|---|---|---|---|
| 0 | +1.61 pp/yr | [+0.33, +3.03] | 98.3% |
| 1 | +2.59 pp/yr | [+1.07, +4.17] | 99.9% |
| 2 | +1.35 pp/yr | [+0.03, +2.75] | 95.2% |
| 3 | +0.49 pp/yr | [-0.69, +1.72] | 75.8% |

配对读：**MIXED_ACROSS_PHASES**（臂 20 日 vs 对照 60 日）。

## 规则（跑之前冻结、从上一张面逐字继承）

EDGE_AT_FLOOR iff the smallest window the overlay can actually price has the highest mean Sharpe across phases (the ladder is a direction, not a level -- do NOT extrapolate it into a config change); SHIPPED_IS_HIGHEST iff the shipped window tops the curve; EDGE_AT_CEILING iff the largest does; INTERIOR otherwise (the ladder turned inside the live range, so a candidate value exists). Windows whose diag shows no vol estimate never tested a shorter estimate and are excluded from the curve

继承校验：PASS（重叠窗口 30d、60d）。

身份门：60 日臂在出货口径那条相位上复现生产卡片 = **PASS**。

行数据：`results/etf_book_vol_window_edge.json::phase_rows`。
