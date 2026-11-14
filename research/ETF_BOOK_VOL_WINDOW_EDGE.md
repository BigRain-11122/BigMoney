# 60 日窗口的冠军落在上一张网格的边上——把网格往下延，阶梯会拐弯吗？

证据面：`results/etf_book_vol_window_phase.json` 的下一张冻结面。证据截止 2026-11-13，1662 根 bar，7 个窗口 × 4 条相位，117.8 秒。

## 判决

**EDGE_AT_FLOOR —— 还在最边上（是方向，不是水平）**

- 最高平均夏普的窗口 = **20 日**（1.1098）；在册 60 日 = 0.9888；差 **+0.1210**。
- 冻结采用规则（**从上一张面继承，不是重写**）：ADOPT_WINDOW 在 **4/4** 条相位上赢过在册值。
- 配对裁决：**MIXED_ACROSS_PHASES**。
- 在册窗口留不留：**留** —— 冠军还是「覆盖真正能跑到的最小窗口」：这是方向、不是水平，方向不能直接外推成配置改动。真正能跑的窗口地板是 20d（发动机自己的最小估计史决定的）；低于它的 5d、10d、15d 跑的是「把覆盖关掉」，是同一个臂，不是 3 个网格点。

## 平均夏普曲线（跨相位）

| 窗口 | 平均夏普 | 最差相位 | 最好相位 | 跑得动吗 |
|---|---|---|---|---|
| 20d | 1.1098 | 1.0510 | 1.1540 | 是 |
| 25d | 1.1062 | 1.0430 | 1.1620 | 是 |
| 30d | 1.0795 | 1.0050 | 1.1820 | 是 |
| 60d | 0.9888 | 0.9030 | 1.1310 | 是 |
| 5d | — | — | — | **否（发动机不出估计，等于把覆盖关掉）** |
| 10d | — | — | — | **否（发动机不出估计，等于把覆盖关掉）** |
| 15d | — | — | — | **否（发动机不出估计，等于把覆盖关掉）** |

真正能跑的窗口地板是 20d（发动机自己的最小估计史决定的）；低于它的 5d、10d、15d 跑的是「把覆盖关掉」，是同一个臂，不是 3 个网格点

重复臂（同一批行 = 同一个臂，不是一个网格点）：5d、10d、15d。

在噪声带（0.02 夏普）之内的窗口：20d、25d —— 所以「拐点」如果是平台，结论要说平台，不能说成某个精确值。

## 逐相位

| 相位 | 5d | 10d | 15d | 20d | 25d | 30d | 60d |
|---|---|---|---|---|---|---|---|
| 0 | 0.980 | 0.980 | 0.980 | 1.083 | 1.103 | 1.055 | 0.987 |
| 1 | 0.908 | 0.908 | 0.908 | 1.151 | 1.117 | 1.076 | 0.934 |
| 2 | 0.887 | 0.887 | 0.887 | 1.051 | 1.043 | 1.005 | 0.903 |
| 3 | 1.112 | 1.112 | 1.112 | 1.154 | 1.162 | 1.182 | 1.131 |

## 配对尺子（最好窗口 vs 在册 60 日）

| 相位 | 配对均值 | 5%-95% 带 | 为正的份额 |
|---|---|---|---|
| 0 | +1.57 pp/yr | [+0.32, +3.04] | 98.2% |
| 1 | +2.60 pp/yr | [+1.14, +4.23] | 99.8% |
| 2 | +1.30 pp/yr | [-0.08, +2.75] | 93.4% |
| 3 | +0.54 pp/yr | [-0.69, +1.76] | 77.7% |

配对读：**MIXED_ACROSS_PHASES**（臂 20 日 vs 对照 60 日）。

## 规则（跑之前冻结、从上一张面逐字继承）

EDGE_AT_FLOOR iff the smallest window the overlay can actually price has the highest mean Sharpe across phases (the ladder is a direction, not a level -- do NOT extrapolate it into a config change); SHIPPED_IS_HIGHEST iff the shipped window tops the curve; EDGE_AT_CEILING iff the largest does; INTERIOR otherwise (the ladder turned inside the live range, so a candidate value exists). Windows whose diag shows no vol estimate never tested a shorter estimate and are excluded from the curve

继承校验：PASS（重叠窗口 30d、60d）。

身份门：60 日臂在出货口径那条相位上复现生产卡片 = **PASS**。

行数据：`results/etf_book_vol_window_edge.json::phase_rows`。
