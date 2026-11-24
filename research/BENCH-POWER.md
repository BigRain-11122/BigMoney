# 这些「负结论」到底有多硬（统计功效）

目标可下注边际：5.0pp/年 · 95% 双侧 · generated 2026-11-24T21:29:19+08:00

| 格子 | 臂 | 年数 | 年化波动 | 观测年化 | 可检出下限(MDE) | 检出 5pp 需要年数 | 读数 |
|---|---|---|---|---|---|---|---|
| fut_trend | tsmom | 9.67 | 13.65 | 6.26 | 8.6 | 28.6 | UNPOWERED_AT_OWN_NOISE |
| fut_trend | ma_cross | 9.67 | 13.62 | 13.44 | 8.58 | 28.5 | UNDERPOWERED_FOR_5PP |
| fut_trend | donchian | 9.67 | 14.5 | -13.42 | 9.14 | 32.3 | UNDERPOWERED_FOR_5PP |
| fut_trend | reversal | 9.67 | 13.67 | -0.54 | 8.62 | 28.7 | UNPOWERED_AT_OWN_NOISE |
| fut_trend | xs_mom | 9.67 | 15.3 | 3.63 | 9.64 | 36.0 | UNPOWERED_AT_OWN_NOISE |
| fut_trend | buy_and_hold | 9.67 | 14.51 | 12.76 | 9.14 | 32.4 | UNDERPOWERED_FOR_5PP |
| bond_curve | T-TF:zrev | 9.79 | 4.15 | 1.74 | 2.6 | 2.6 | UNPOWERED_AT_OWN_NOISE |
| bond_curve | T-TF:trend | 9.79 | 4.35 | -1.81 | 2.73 | 2.9 | UNPOWERED_AT_OWN_NOISE |
| bond_curve | T-TS:zrev | 8.2 | 5.49 | -1.11 | 3.76 | 4.6 | UNPOWERED_AT_OWN_NOISE |
| bond_curve | T-TS:trend | 8.2 | 5.52 | -1.92 | 3.78 | 4.7 | UNPOWERED_AT_OWN_NOISE |
| bond_curve | TF-TS:zrev | 8.2 | 3.88 | -0.75 | 2.65 | 2.3 | UNPOWERED_AT_OWN_NOISE |
| bond_curve | TF-TS:trend | 8.2 | 3.96 | -3.61 | 2.71 | 2.4 | POWERED |
| bond_curve | long_duration | 9.79 | 8.72 | 5.59 | 5.46 | 11.7 | UNDERPOWERED_FOR_5PP |
| astock_lowvol | lowvol | 10.19 | 17.29 | 6.12 | 10.62 | 45.9 | UNPOWERED_AT_OWN_NOISE |
| astock_lowvol | excess_vs_equal_weight | 10.19 | 10.06 | 0.93 | 6.18 | 15.6 | UNPOWERED_AT_OWN_NOISE |
| bond_defensive | bond_leg | 9.79 | 7.88 | 4.88 | 4.94 | 9.5 | UNPOWERED_AT_OWN_NOISE |

## 怎么读这张表

- **MDE** = 1.96 × 年化波动 ÷ √年数。它是这个样本能分辨的最小年化差。
- 若观测值落在 ±MDE 内（UNPOWERED_AT_OWN_NOISE），只能说「没看见」，不能说「不存在」。
- 若 MDE > 5pp（UNDERPOWERED_FOR_5PP），这条线要么换更长样本，要么这个样本永远回答不了。
- 这一条是本轮最重要的产出：它决定了下一格该不该排队，而不是「跑得多不多」。
