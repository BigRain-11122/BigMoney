# trend_single_RB_long

cell `trend_single_RB_long` · type `single` · rule `ma_cross` · cutoff 2026-11-26 · **NO_EDGE**

| 臂 | 全期年化 | 夏普 | 回撤 | 样本外年化 | 前后半 | 剔除最好一年 | MDE | 可分辨? | 超额vs同口径基准 | 判决 |
|---|---|---|---|---|---|---|---|---|---|---|
| arm | +0.50% | 0.106 | -32.33% | -6.90% | 0.42/0.57 | -0.56% | 3.3 | True | +1.34% (below MDE) | **NO_EDGE** |
| 同篮子买入持有 | -0.84% | -0.028 | -62.57% | -6.51% | — | — | — | — | — | BENCHMARK |

判据：{"H1_full_pct": 4.0, "H2_oos_pct": 3.0, "H2_oos_sharpe": 0.4, "H4_drop_best_pct": 1.5, "H5_p": 0.05}

MDE = 1.96 × 年化波动 ÷ √年数；观测值落在这个范围内时，「没看见」不等于「不存在」。
