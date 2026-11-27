# census_commodity

cell `census_commodity` · type `census` · rule `None` · cutoff 2026-11-26 · **CENSUS_LEANS_POSITIVE**

| 臂 | 全期年化 | 夏普 | 回撤 | 样本外年化 | 前后半 | 剔除最好一年 | MDE | 可分辨? | 超额vs同口径基准 | 判决 |
|---|---|---|---|---|---|---|---|---|---|---|
| tsmom|{'lookback': 60, 'skip': 21}|long | +2.76% | 0.450 | -20.15% | +5.22% | None/None | n/a | 2.95 | True | -1.04% (below MDE) | **NO_EDGE** |
| tsmom|{'lookback': 60, 'skip': 21}|ls | +1.52% | 0.219 | -20.51% | +1.38% | None/None | n/a | 3.86 | True | -2.28% (below MDE) | **NO_EDGE** |
| tsmom|{'lookback': 120, 'skip': 21}|long | +4.42% | 0.714 | -16.13% | +9.27% | None/None | n/a | 2.86 | True | +0.62% (below MDE) | **NO_EDGE** |
| tsmom|{'lookback': 120, 'skip': 21}|ls | +4.99% | 0.623 | -21.74% | +9.28% | None/None | n/a | 3.78 | True | +1.19% (below MDE) | **GO** |
| tsmom|{'lookback': 250, 'skip': 21}|long | +4.54% | 0.752 | -13.70% | +8.39% | None/None | n/a | 2.78 | True | +0.74% (below MDE) | **NO_EDGE** |
| tsmom|{'lookback': 250, 'skip': 21}|ls | +5.19% | 0.665 | -18.88% | +7.56% | None/None | n/a | 3.66 | True | +1.39% (below MDE) | **GO** |
| ma_cross|{'fast': 20, 'slow': 60}|long | +3.02% | 0.476 | -19.95% | +9.47% | None/None | n/a | 3.04 | True | -0.78% (below MDE) | **NO_EDGE** |
| ma_cross|{'fast': 20, 'slow': 60}|ls | +2.46% | 0.322 | -26.49% | +9.74% | None/None | n/a | 3.95 | True | -1.34% (below MDE) | **NO_EDGE** |
| ma_cross|{'fast': 50, 'slow': 200}|long | +4.35% | 0.691 | -22.28% | +6.27% | None/None | n/a | 2.92 | True | +0.55% (below MDE) | **NO_EDGE** |
| ma_cross|{'fast': 50, 'slow': 200}|ls | +4.09% | 0.502 | -21.50% | +3.38% | None/None | n/a | 3.95 | True | +0.29% (below MDE) | **NO_EDGE** |
| donchian|{'entry': 20, 'exit': 10}|long | +3.37% | 0.406 | -35.21% | +14.14% | None/None | n/a | 4.16 | True | -0.43% (below MDE) | **NO_EDGE** |
| donchian|{'entry': 20, 'exit': 10}|ls | +2.07% | 0.278 | -32.07% | +6.57% | None/None | n/a | 3.94 | True | -1.73% (below MDE) | **NO_EDGE** |
| donchian|{'entry': 55, 'exit': 20}|long | +2.08% | 0.270 | -30.41% | +11.26% | None/None | n/a | 4.15 | True | -1.72% (below MDE) | **NO_EDGE** |
| donchian|{'entry': 55, 'exit': 20}|ls | +1.82% | 0.248 | -29.82% | +6.03% | None/None | n/a | 4.0 | True | -1.98% (below MDE) | **NO_EDGE** |
| 同篮子买入持有 | +3.80% | 0.462 | -47.91% | +8.78% | — | — | — | — | — | BENCHMARK |

判据：{}

MDE = 1.96 × 年化波动 ÷ √年数；观测值落在这个范围内时，「没看见」不等于「不存在」。
