# trend_single_T_long

cell `trend_single_T_long` · type `single` · rule `ma_cross` · cutoff 2026-11-26 · **NO_EDGE**

| 臂 | 全期年化 | 夏普 | 回撤 | 样本外年化 | 前后半 | 剔除最好一年 | MDE | 可分辨? | 超额vs同口径基准 | 判决 |
|---|---|---|---|---|---|---|---|---|---|---|
| arm | +3.09% | 0.706 | -5.65% | +4.79% | 2.5/3.68 | +2.04% | 2.79 | True | -0.18% (below MDE) | **NO_EDGE** |
| 同篮子买入持有 | +3.27% | 0.641 | -8.98% | +5.37% | — | — | — | — | — | BENCHMARK |

判据：{"H1_full_pct": 3.0, "H2_oos_pct": 2.0, "H2_oos_sharpe": 0.3, "H4_drop_best_pct": 1.0, "H5_p": 0.05}

MDE = 1.96 × 年化波动 ÷ √年数；观测值落在这个范围内时，「没看见」不等于「不存在」。
