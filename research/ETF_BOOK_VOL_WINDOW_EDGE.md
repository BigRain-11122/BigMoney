# 60 日窗口的冠军落在上一张网格的边上——把网格往下延，阶梯会拐弯吗？

证据面：`results/etf_book_vol_window_phase.json` 的下一张冻结面。证据截止 2026-11-25，1670 根 bar，7 个窗口 × 4 条相位，114.8 秒。

## 判决

**EDGE_AT_FLOOR —— 还在最边上（是方向，不是水平）**

- 最高平均夏普的窗口 = **20 日**（1.0802）；在册 60 日 = 0.9505；差 **+0.1297**。
- 冻结采用规则（**从上一张面继承，不是重写**）：ADOPT_WINDOW 在 **4/4** 条相位上赢过在册值。
- 配对裁决：**MIXED_ACROSS_PHASES**。
- 在册窗口留不留：**留** —— 冠军还是「覆盖真正能跑到的最小窗口」：这是方向、不是水平，方向不能直接外推成配置改动。真正能跑的窗口地板是 20d（发动机自己的最小估计史决定的）；低于它的 5d、10d、15d 跑的是「把覆盖关掉」，是同一个臂，不是 3 个网格点。

## 平均夏普曲线（跨相位）

| 窗口 | 平均夏普 | 最差相位 | 最好相位 | 跑得动吗 |
|---|---|---|---|---|
| 20d | 1.0802 | 0.9980 | 1.1560 | 是 |
| 25d | 1.0762 | 0.9890 | 1.1650 | 是 |
| 30d | 1.0475 | 0.9490 | 1.1850 | 是 |
| 60d | 0.9505 | 0.8400 | 1.1340 | 是 |
| 5d | — | — | — | **否（发动机不出估计，等于把覆盖关掉）** |
| 10d | — | — | — | **否（发动机不出估计，等于把覆盖关掉）** |
| 15d | — | — | — | **否（发动机不出估计，等于把覆盖关掉）** |

真正能跑的窗口地板是 20d（发动机自己的最小估计史决定的）；低于它的 5d、10d、15d 跑的是「把覆盖关掉」，是同一个臂，不是 3 个网格点

重复臂（同一批行 = 同一个臂，不是一个网格点）：5d、10d、15d。

在噪声带（0.02 夏普）之内的窗口：20d、25d —— 所以「拐点」如果是平台，结论要说平台，不能说成某个精确值。

## 逐相位

| 相位 | 5d | 10d | 15d | 20d | 25d | 30d | 60d |
|---|---|---|---|---|---|---|---|
| 0 | 0.938 | 0.938 | 0.938 | 1.044 | 1.061 | 1.009 | 0.928 |
| 1 | 0.885 | 0.885 | 0.885 | 1.123 | 1.090 | 1.047 | 0.900 |
| 2 | 0.848 | 0.848 | 0.848 | 0.998 | 0.989 | 0.949 | 0.840 |
| 3 | 1.114 | 1.114 | 1.114 | 1.156 | 1.165 | 1.185 | 1.134 |

## 配对尺子（最好窗口 vs 在册 60 日）

| 相位 | 配对均值 | 5%-95% 带 | 为正的份额 |
|---|---|---|---|
| 0 | +1.72 pp/yr | [+0.38, +3.19] | 98.6% |
| 1 | +2.65 pp/yr | [+1.16, +4.26] | 99.8% |
| 2 | +1.40 pp/yr | [+0.06, +2.86] | 95.6% |
| 3 | +0.53 pp/yr | [-0.67, +1.73] | 77.6% |

配对读：**MIXED_ACROSS_PHASES**（臂 20 日 vs 对照 60 日）。

## 规则（跑之前冻结、从上一张面逐字继承）

EDGE_AT_FLOOR iff the smallest window the overlay can actually price has the highest mean Sharpe across phases (the ladder is a direction, not a level -- do NOT extrapolate it into a config change); SHIPPED_IS_HIGHEST iff the shipped window tops the curve; EDGE_AT_CEILING iff the largest does; INTERIOR otherwise (the ladder turned inside the live range, so a candidate value exists). Windows whose diag shows no vol estimate never tested a shorter estimate and are excluded from the curve

继承校验：PASS（重叠窗口 30d、60d）。

身份门：60 日臂在出货口径那条相位上复现生产卡片 = **PASS**。

行数据：`results/etf_book_vol_window_edge.json::phase_rows`。
