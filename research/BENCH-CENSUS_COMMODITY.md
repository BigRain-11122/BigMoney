# census_commodity

cell `census_commodity` · type `census` · rule `None` · cutoff 2026-11-24 · **CENSUS_SIGN_MIXED**

| 臂 | 全期年化 | 夏普 | 回撤 | 样本外年化 | 前后半 | 剔除最好一年 | MDE | 可分辨? | 判决 |
|---|---|---|---|---|---|---|---|---|---|
| tsmom|{'lookback': 60, 'skip': 21}|long | +2.76% | 0.450 | -20.15% | +5.23% | None/None | n/a | 2.95 | True | **NO_EDGE** |
| tsmom|{'lookback': 60, 'skip': 21}|ls | +1.53% | 0.221 | -20.51% | +1.51% | None/None | n/a | 3.86 | True | **NO_EDGE** |
| tsmom|{'lookback': 120, 'skip': 21}|long | +4.42% | 0.714 | -16.13% | +9.30% | None/None | n/a | 2.86 | True | **NO_EDGE** |
| tsmom|{'lookback': 120, 'skip': 21}|ls | +5.01% | 0.626 | -21.74% | +9.44% | None/None | n/a | 3.78 | True | **GO** |
| tsmom|{'lookback': 250, 'skip': 21}|long | +4.56% | 0.754 | -13.70% | +8.51% | None/None | n/a | 2.78 | True | **NO_EDGE** |
| tsmom|{'lookback': 250, 'skip': 21}|ls | +5.24% | 0.671 | -18.88% | +7.90% | None/None | n/a | 3.66 | True | **GO** |
| ma_cross|{'fast': 20, 'slow': 60}|long | +3.03% | 0.476 | -19.95% | +9.50% | None/None | n/a | 3.04 | True | **NO_EDGE** |
| ma_cross|{'fast': 20, 'slow': 60}|ls | +2.48% | 0.324 | -26.49% | +9.90% | None/None | n/a | 3.95 | True | **NO_EDGE** |
| ma_cross|{'fast': 50, 'slow': 200}|long | +4.35% | 0.690 | -22.28% | +6.25% | None/None | n/a | 2.92 | True | **NO_EDGE** |
| ma_cross|{'fast': 50, 'slow': 200}|ls | +4.09% | 0.503 | -21.50% | +3.43% | None/None | n/a | 3.95 | True | **NO_EDGE** |
| donchian|{'entry': 20, 'exit': 10}|long | -4.54% | -0.471 | -69.29% | -8.85% | None/None | n/a | 4.07 | True | **NO_EDGE** |
| donchian|{'entry': 20, 'exit': 10}|ls | -4.54% | -0.471 | -69.29% | -8.85% | None/None | n/a | 4.07 | True | **NO_EDGE** |
| donchian|{'entry': 55, 'exit': 20}|long | -4.27% | -0.433 | -69.41% | -8.85% | None/None | n/a | 4.11 | True | **NO_EDGE** |
| donchian|{'entry': 55, 'exit': 20}|ls | -4.27% | -0.433 | -69.41% | -8.85% | None/None | n/a | 4.11 | True | **NO_EDGE** |
| 同篮子买入持有 | +4.62% | 0.460 | -56.00% | +10.82% | — | — | — | — | BENCHMARK |

判据：{}

MDE = 1.96 × 年化波动 ÷ √年数；观测值落在这个范围内时，「没看见」不等于「不存在」。
