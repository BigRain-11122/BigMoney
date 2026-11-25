# 这些「负结论」到底有多硬（统计功效）

目标可下注边际：5.0pp/年 · 95% 双侧 · generated 2026-11-25T22:22:55+08:00

| 格子 | 臂 | 年数 | 年化波动 | 观测年化 | 可检出下限(MDE) | 检出 5pp 需要年数 | 读数 |
|---|---|---|---|---|---|---|---|
| fut_trend | tsmom | 9.68 | 13.65 | 6.21 | 8.6 | 28.6 | UNPOWERED_AT_OWN_NOISE |
| fut_trend | ma_cross | 9.68 | 13.63 | 13.43 | 8.58 | 28.5 | UNDERPOWERED_FOR_5PP |
| fut_trend | donchian | 9.68 | 14.51 | -13.35 | 9.14 | 32.4 | UNDERPOWERED_FOR_5PP |
| fut_trend | reversal | 9.68 | 13.68 | -0.58 | 8.62 | 28.8 | UNPOWERED_AT_OWN_NOISE |
| fut_trend | xs_mom | 9.68 | 15.33 | 3.79 | 9.66 | 36.1 | UNPOWERED_AT_OWN_NOISE |
| fut_trend | buy_and_hold | 9.68 | 14.53 | 12.67 | 9.15 | 32.4 | UNDERPOWERED_FOR_5PP |
| bond_curve | T-TF:zrev | 9.8 | 4.15 | 1.77 | 2.6 | 2.6 | UNPOWERED_AT_OWN_NOISE |
| bond_curve | T-TF:trend | 9.8 | 4.35 | -1.84 | 2.72 | 2.9 | UNPOWERED_AT_OWN_NOISE |
| bond_curve | T-TS:zrev | 8.22 | 5.48 | -1.06 | 3.75 | 4.6 | UNPOWERED_AT_OWN_NOISE |
| bond_curve | T-TS:trend | 8.22 | 5.52 | -1.97 | 3.77 | 4.7 | UNPOWERED_AT_OWN_NOISE |
| bond_curve | TF-TS:zrev | 8.22 | 3.88 | -0.74 | 2.65 | 2.3 | UNPOWERED_AT_OWN_NOISE |
| bond_curve | TF-TS:trend | 8.22 | 3.96 | -3.62 | 2.71 | 2.4 | POWERED |
| bond_curve | long_duration | 9.8 | 8.71 | 5.57 | 5.45 | 11.7 | UNDERPOWERED_FOR_5PP |
| astock_lowvol | lowvol | 10.19 | 17.29 | 6.12 | 10.62 | 45.9 | UNPOWERED_AT_OWN_NOISE |
| astock_lowvol | excess_vs_equal_weight | 10.19 | 10.06 | 0.93 | 6.18 | 15.6 | UNPOWERED_AT_OWN_NOISE |
| bond_defensive | bond_leg | 9.8 | 7.88 | 4.86 | 4.93 | 9.5 | UNPOWERED_AT_OWN_NOISE |

## 怎么读这张表

- **MDE** = 1.96 × 年化波动 ÷ √年数。它是这个样本能分辨的最小年化差。
- 若观测值落在 ±MDE 内（UNPOWERED_AT_OWN_NOISE），只能说「没看见」，不能说「不存在」。
- 若 MDE > 5pp（UNDERPOWERED_FOR_5PP），这条线要么换更长样本，要么这个样本永远回答不了。
- 这一条是本轮最重要的产出：它决定了下一格该不该排队，而不是「跑得多不多」。
