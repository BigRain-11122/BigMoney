# robust_ma_index

cell `robust_ma_index` · type `robust` · rule `ma_cross` · cutoff 2026-11-26 · **UNSTABLE_ACROSS_PARAMS**

| 臂 | 全期年化 | 夏普 | 回撤 | 样本外年化 | 前后半 | 剔除最好一年 | MDE | 可分辨? | 超额vs同口径基准 | 判决 |
|---|---|---|---|---|---|---|---|---|---|---|
| 20_50 | -0.96% | -0.016 | -32.65% | +6.67% | -3.66/1.81 | -2.45% | 7.76 | False | -2.89% (below MDE) | **NO_EDGE** |
| 50_100 | +5.50% | 0.494 | -25.51% | +13.35% | 5.87/5.14 | +3.11% | 7.77 | False | +3.57% (below MDE) | **UNINFORMATIVE_AT_TARGET** |
| 50_200 | +6.78% | 0.600 | -17.60% | +12.10% | 4.79/8.81 | +5.43% | 7.61 | False | +4.85% (below MDE) | **UNINFORMATIVE_AT_TARGET** |
| 同篮子买入持有 | +1.93% | 0.206 | -44.25% | +2.85% | — | — | — | — | — | BENCHMARK |

判据：{"H1_full_pct": 3.0, "H2_oos_pct": 2.0, "H2_oos_sharpe": 0.3, "H4_drop_best_pct": 1.0, "H5_p": 0.05}

MDE = 1.96 × 年化波动 ÷ √年数；观测值落在这个范围内时，「没看见」不等于「不存在」。
