# reversal_commodity_5d

cell `reversal_commodity_5d` · type `pair` · rule `reversal` · cutoff 2026-11-24 · **NO_EDGE**

| 臂 | 全期年化 | 夏普 | 回撤 | 样本外年化 | 前后半 | 剔除最好一年 | MDE | 可分辨? | 判决 |
|---|---|---|---|---|---|---|---|---|---|
| arm | -4.22% | -0.454 | -59.71% | -1.70% | -5.53/-2.89 | -3.37% | 3.91 | False | **NO_EDGE** |
| 同篮子买入持有 | +4.62% | 0.460 | -56.00% | +10.82% | — | — | — | — | BENCHMARK |

判据：{"H1_full_pct": 3.0, "H2_oos_pct": 2.0, "H2_oos_sharpe": 0.3, "H4_drop_best_pct": 1.0, "H5_p": 0.05}

MDE = 1.96 × 年化波动 ÷ √年数；观测值落在这个范围内时，「没看见」不等于「不存在」。
