# census_bond_futures

cell `census_bond_futures` · type `census` · rule `None` · cutoff 2026-11-26 · **CENSUS_LEANS_POSITIVE**

| 臂 | 全期年化 | 夏普 | 回撤 | 样本外年化 | 前后半 | 剔除最好一年 | MDE | 可分辨? | 超额vs同口径基准 | 判决 |
|---|---|---|---|---|---|---|---|---|---|---|
| tsmom|{'lookback': 60, 'skip': 21}|long | +3.21% | 0.525 | -11.64% | +6.80% | None/None | n/a | 4.02 | True | -1.65% (below MDE) | **NO_EDGE** |
| tsmom|{'lookback': 120, 'skip': 21}|long | +3.21% | 0.512 | -13.59% | +6.69% | None/None | n/a | 4.13 | True | -1.65% (below MDE) | **NO_EDGE** |
| tsmom|{'lookback': 250, 'skip': 21}|long | +2.84% | 0.455 | -14.48% | +6.62% | None/None | n/a | 4.16 | True | -2.02% (below MDE) | **NO_EDGE** |
| ma_cross|{'fast': 20, 'slow': 60}|long | +1.92% | 0.342 | -17.89% | +5.96% | None/None | n/a | 3.84 | True | -2.94% (below MDE) | **NO_EDGE** |
| ma_cross|{'fast': 50, 'slow': 200}|long | +4.02% | 0.629 | -11.22% | +6.45% | None/None | n/a | 4.14 | True | -0.84% (below MDE) | **NO_EDGE** |
| 同篮子买入持有 | +4.86% | 0.642 | -13.86% | +7.66% | — | — | — | — | — | BENCHMARK |

判据：{}

MDE = 1.96 × 年化波动 ÷ √年数；观测值落在这个范围内时，「没看见」不等于「不存在」。
