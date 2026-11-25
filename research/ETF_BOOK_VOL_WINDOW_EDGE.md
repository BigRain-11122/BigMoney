# 60 日窗口的冠军落在上一张网格的边上——把网格往下延，阶梯会拐弯吗？

证据面：`results/etf_book_vol_window_phase.json` 的下一张冻结面。证据截止 2026-11-24，1669 根 bar，7 个窗口 × 4 条相位，88.3 秒。

## 判决

**EDGE_AT_FLOOR —— 还在最边上（是方向，不是水平）**

- 最高平均夏普的窗口 = **20 日**（1.0873）；在册 60 日 = 0.9597；差 **+0.1276**。
- 冻结采用规则（**从上一张面继承，不是重写**）：ADOPT_WINDOW 在 **4/4** 条相位上赢过在册值。
- 配对裁决：**MIXED_ACROSS_PHASES**。
- 在册窗口留不留：**留** —— 冠军还是「覆盖真正能跑到的最小窗口」：这是方向、不是水平，方向不能直接外推成配置改动。真正能跑的窗口地板是 20d（发动机自己的最小估计史决定的）；低于它的 5d、10d、15d 跑的是「把覆盖关掉」，是同一个臂，不是 3 个网格点。

## 平均夏普曲线（跨相位）

| 窗口 | 平均夏普 | 最差相位 | 最好相位 | 跑得动吗 |
|---|---|---|---|---|
| 20d | 1.0873 | 1.0120 | 1.1550 | 是 |
| 25d | 1.0837 | 1.0040 | 1.1640 | 是 |
| 30d | 1.0555 | 0.9640 | 1.1840 | 是 |
| 60d | 0.9597 | 0.8570 | 1.1330 | 是 |
| 5d | — | — | — | **否（发动机不出估计，等于把覆盖关掉）** |
| 10d | — | — | — | **否（发动机不出估计，等于把覆盖关掉）** |
| 15d | — | — | — | **否（发动机不出估计，等于把覆盖关掉）** |

真正能跑的窗口地板是 20d（发动机自己的最小估计史决定的）；低于它的 5d、10d、15d 跑的是「把覆盖关掉」，是同一个臂，不是 3 个网格点

重复臂（同一批行 = 同一个臂，不是一个网格点）：5d、10d、15d。

在噪声带（0.02 夏普）之内的窗口：20d、25d —— 所以「拐点」如果是平台，结论要说平台，不能说成某个精确值。

## 逐相位

| 相位 | 5d | 10d | 15d | 20d | 25d | 30d | 60d |
|---|---|---|---|---|---|---|---|
| 0 | 0.949 | 0.949 | 0.949 | 1.054 | 1.072 | 1.021 | 0.943 |
| 1 | 0.889 | 0.889 | 0.889 | 1.128 | 1.095 | 1.053 | 0.906 |
| 2 | 0.859 | 0.859 | 0.859 | 1.012 | 1.004 | 0.964 | 0.857 |
| 3 | 1.113 | 1.113 | 1.113 | 1.155 | 1.164 | 1.184 | 1.133 |

## 配对尺子（最好窗口 vs 在册 60 日）

| 相位 | 配对均值 | 5%-95% 带 | 为正的份额 |
|---|---|---|---|
| 0 | +1.67 pp/yr | [+0.39, +3.16] | 98.5% |
| 1 | +2.63 pp/yr | [+1.14, +4.30] | 99.7% |
| 2 | +1.37 pp/yr | [+0.01, +2.88] | 95.1% |
| 3 | +0.53 pp/yr | [-0.66, +1.74] | 77.1% |

配对读：**MIXED_ACROSS_PHASES**（臂 20 日 vs 对照 60 日）。

## 规则（跑之前冻结、从上一张面逐字继承）

EDGE_AT_FLOOR iff the smallest window the overlay can actually price has the highest mean Sharpe across phases (the ladder is a direction, not a level -- do NOT extrapolate it into a config change); SHIPPED_IS_HIGHEST iff the shipped window tops the curve; EDGE_AT_CEILING iff the largest does; INTERIOR otherwise (the ladder turned inside the live range, so a candidate value exists). Windows whose diag shows no vol estimate never tested a shorter estimate and are excluded from the curve

继承校验：PASS（重叠窗口 30d、60d）。

身份门：60 日臂在出货口径那条相位上复现生产卡片 = **PASS**。

行数据：`results/etf_book_vol_window_edge.json::phase_rows`。
