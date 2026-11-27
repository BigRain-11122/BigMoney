# census_index_futures

cell `census_index_futures` · type `census` · rule `None` · cutoff 2026-11-26 · **CENSUS_UNPOWERED**

| 臂 | 全期年化 | 夏普 | 回撤 | 样本外年化 | 前后半 | 剔除最好一年 | MDE | 可分辨? | 超额vs同口径基准 | 判决 |
|---|---|---|---|---|---|---|---|---|---|---|
| ma_cross|{'fast': 20, 'slow': 60}|long | +1.42% | 0.195 | -28.73% | +4.50% | None/None | n/a | 5.98 | False | -0.51% (below MDE) | **NO_EDGE** |
| ma_cross|{'fast': 20, 'slow': 60}|ls | -0.08% | 0.056 | -28.23% | +4.90% | None/None | n/a | 7.82 | False | -2.01% (below MDE) | **NO_EDGE** |
| ma_cross|{'fast': 50, 'slow': 100}|long | +4.12% | 0.461 | -29.96% | +8.57% | None/None | n/a | 6.13 | False | +2.19% (below MDE) | **NO_EDGE** |
| ma_cross|{'fast': 50, 'slow': 100}|ls | +5.50% | 0.494 | -25.51% | +13.35% | None/None | n/a | 7.77 | False | +3.57% (below MDE) | **UNINFORMATIVE_AT_TARGET** |
| ma_cross|{'fast': 50, 'slow': 200}|long | +3.98% | 0.453 | -22.69% | +7.95% | None/None | n/a | 6.03 | False | +2.05% (below MDE) | **NO_EDGE** |
| ma_cross|{'fast': 50, 'slow': 200}|ls | +6.78% | 0.600 | -17.60% | +12.10% | None/None | n/a | 7.61 | False | +4.85% (below MDE) | **UNINFORMATIVE_AT_TARGET** |
| ma_cross|{'fast': 100, 'slow': 200}|long | +2.48% | 0.299 | -22.84% | +7.60% | None/None | n/a | 6.12 | False | +0.55% (below MDE) | **NO_EDGE** |
| ma_cross|{'fast': 100, 'slow': 200}|ls | +3.77% | 0.368 | -23.36% | +11.49% | None/None | n/a | 7.52 | False | +1.84% (below MDE) | **NO_EDGE** |
| tsmom|{'lookback': 60, 'skip': 21}|long | +3.25% | 0.387 | -30.47% | +6.53% | None/None | n/a | 5.89 | False | +1.32% (below MDE) | **NO_EDGE** |
| tsmom|{'lookback': 60, 'skip': 21}|ls | +3.64% | 0.356 | -27.95% | +9.13% | None/None | n/a | 7.59 | False | +1.71% (below MDE) | **NO_EDGE** |
| tsmom|{'lookback': 120, 'skip': 21}|long | +2.75% | 0.333 | -30.45% | +4.74% | None/None | n/a | 5.95 | False | +0.82% (below MDE) | **NO_EDGE** |
| tsmom|{'lookback': 120, 'skip': 21}|ls | +3.56% | 0.348 | -26.02% | +5.48% | None/None | n/a | 7.62 | False | +1.63% (below MDE) | **NO_EDGE** |
| tsmom|{'lookback': 250, 'skip': 21}|long | +2.39% | 0.301 | -15.83% | +6.00% | None/None | n/a | 5.8 | False | +0.46% (below MDE) | **NO_EDGE** |
| tsmom|{'lookback': 250, 'skip': 21}|ls | +3.54% | 0.352 | -24.17% | +7.97% | None/None | n/a | 7.44 | False | +1.61% (below MDE) | **NO_EDGE** |
| donchian|{'entry': 20, 'exit': 10}|long | +0.75% | 0.122 | -30.44% | +5.80% | None/None | n/a | 7.73 | False | -1.18% (below MDE) | **NO_EDGE** |
| donchian|{'entry': 20, 'exit': 10}|ls | -2.93% | -0.185 | -44.43% | +3.63% | None/None | n/a | 7.58 | False | -4.86% (below MDE) | **NO_EDGE** |
| donchian|{'entry': 40, 'exit': 15}|long | +0.06% | 0.067 | -29.63% | +6.44% | None/None | n/a | 7.86 | False | -1.87% (below MDE) | **NO_EDGE** |
| donchian|{'entry': 40, 'exit': 15}|ls | -1.20% | -0.035 | -34.48% | +3.32% | None/None | n/a | 7.79 | False | -3.13% (below MDE) | **NO_EDGE** |
| donchian|{'entry': 55, 'exit': 20}|long | +1.40% | 0.174 | -25.53% | +5.96% | None/None | n/a | 7.7 | False | -0.53% (below MDE) | **NO_EDGE** |
| donchian|{'entry': 55, 'exit': 20}|ls | -0.11% | 0.052 | -26.41% | +1.44% | None/None | n/a | 7.58 | False | -2.04% (below MDE) | **NO_EDGE** |
| 同篮子买入持有 | +1.93% | 0.206 | -44.25% | +2.85% | — | — | — | — | — | BENCHMARK |

判据：{}

MDE = 1.96 × 年化波动 ÷ √年数；观测值落在这个范围内时，「没看见」不等于「不存在」。
