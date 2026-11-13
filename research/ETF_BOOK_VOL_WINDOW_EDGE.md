# 60 日窗口的冠军落在上一张网格的边上——把网格往下延，阶梯会拐弯吗？

证据面：`results/etf_book_vol_window_phase.json` 的下一张冻结面。证据截止 2026-11-12，1661 根 bar，7 个窗口 × 4 条相位，105.7 秒。

## 判决

**EDGE_AT_FLOOR —— 还在最边上（是方向，不是水平）**

- 最高平均夏普的窗口 = **20 日**（1.1133）；在册 60 日 = 0.9930；差 **+0.1203**。
- 冻结采用规则（**从上一张面继承，不是重写**）：ADOPT_WINDOW 在 **4/4** 条相位上赢过在册值。
- 配对裁决：**MIXED_ACROSS_PHASES**。
- 在册窗口留不留：**留** —— 冠军还是「覆盖真正能跑到的最小窗口」：这是方向、不是水平，方向不能直接外推成配置改动。真正能跑的窗口地板是 20d（发动机自己的最小估计史决定的）；低于它的 5d、10d、15d 跑的是「把覆盖关掉」，是同一个臂，不是 3 个网格点。

## 平均夏普曲线（跨相位）

| 窗口 | 平均夏普 | 最差相位 | 最好相位 | 跑得动吗 |
|---|---|---|---|---|
| 20d | 1.1133 | 1.0540 | 1.1570 | 是 |
| 25d | 1.1105 | 1.0460 | 1.1660 | 是 |
| 30d | 1.0840 | 1.0090 | 1.1860 | 是 |
| 60d | 0.9930 | 0.9060 | 1.1350 | 是 |
| 5d | — | — | — | **否（发动机不出估计，等于把覆盖关掉）** |
| 10d | — | — | — | **否（发动机不出估计，等于把覆盖关掉）** |
| 15d | — | — | — | **否（发动机不出估计，等于把覆盖关掉）** |

真正能跑的窗口地板是 20d（发动机自己的最小估计史决定的）；低于它的 5d、10d、15d 跑的是「把覆盖关掉」，是同一个臂，不是 3 个网格点

重复臂（同一批行 = 同一个臂，不是一个网格点）：5d、10d、15d。

在噪声带（0.02 夏普）之内的窗口：20d、25d —— 所以「拐点」如果是平台，结论要说平台，不能说成某个精确值。

## 逐相位

| 相位 | 5d | 10d | 15d | 20d | 25d | 30d | 60d |
|---|---|---|---|---|---|---|---|
| 0 | 0.985 | 0.985 | 0.985 | 1.087 | 1.108 | 1.060 | 0.993 |
| 1 | 0.911 | 0.911 | 0.911 | 1.155 | 1.122 | 1.081 | 0.938 |
| 2 | 0.889 | 0.889 | 0.889 | 1.054 | 1.046 | 1.009 | 0.906 |
| 3 | 1.115 | 1.115 | 1.115 | 1.157 | 1.166 | 1.186 | 1.135 |

## 配对尺子（最好窗口 vs 在册 60 日）

| 相位 | 配对均值 | 5%-95% 带 | 为正的份额 |
|---|---|---|---|
| 0 | +1.55 pp/yr | [+0.28, +3.00] | 98.1% |
| 1 | +2.60 pp/yr | [+1.11, +4.19] | 99.9% |
| 2 | +1.30 pp/yr | [-0.13, +2.73] | 94.1% |
| 3 | +0.53 pp/yr | [-0.68, +1.70] | 76.8% |

配对读：**MIXED_ACROSS_PHASES**（臂 20 日 vs 对照 60 日）。

## 规则（跑之前冻结、从上一张面逐字继承）

EDGE_AT_FLOOR iff the smallest window the overlay can actually price has the highest mean Sharpe across phases (the ladder is a direction, not a level -- do NOT extrapolate it into a config change); SHIPPED_IS_HIGHEST iff the shipped window tops the curve; EDGE_AT_CEILING iff the largest does; INTERIOR otherwise (the ladder turned inside the live range, so a candidate value exists). Windows whose diag shows no vol estimate never tested a shorter estimate and are excluded from the curve

继承校验：PASS（重叠窗口 30d、60d）。

身份门：60 日臂在出货口径那条相位上复现生产卡片 = **PASS**。

行数据：`results/etf_book_vol_window_edge.json::phase_rows`。
