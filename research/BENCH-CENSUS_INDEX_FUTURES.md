# census_index_futures

cell `census_index_futures` · type `census` · rule `None` · cutoff 2026-11-23 · **CENSUS_UNPOWERED**

| 臂 | 全期年化 | 夏普 | 回撤 | 样本外年化 | 前后半 | 剔除最好一年 | MDE | 可分辨? | 判决 |
|---|---|---|---|---|---|---|---|---|---|
| ma_cross|{'fast': 20, 'slow': 60}|long | +1.42% | 0.195 | -28.73% | +4.52% | None/None | n/a | 5.99 | False | **NO_EDGE** |
| ma_cross|{'fast': 20, 'slow': 60}|ls | -0.27% | 0.041 | -28.23% | +4.24% | None/None | n/a | 7.82 | False | **NO_EDGE** |
| ma_cross|{'fast': 50, 'slow': 100}|long | +4.12% | 0.461 | -29.96% | +8.61% | None/None | n/a | 6.14 | False | **NO_EDGE** |
| ma_cross|{'fast': 50, 'slow': 100}|ls | +5.31% | 0.479 | -25.51% | +12.67% | None/None | n/a | 7.77 | False | **UNINFORMATIVE_AT_TARGET** |
| ma_cross|{'fast': 50, 'slow': 200}|long | +3.98% | 0.454 | -22.69% | +7.98% | None/None | n/a | 6.04 | False | **NO_EDGE** |
| ma_cross|{'fast': 50, 'slow': 200}|ls | +6.58% | 0.586 | -17.60% | +11.42% | None/None | n/a | 7.61 | False | **UNINFORMATIVE_AT_TARGET** |
| ma_cross|{'fast': 100, 'slow': 200}|long | +2.48% | 0.300 | -22.84% | +7.64% | None/None | n/a | 6.13 | False | **NO_EDGE** |
| ma_cross|{'fast': 100, 'slow': 200}|ls | +3.58% | 0.353 | -23.36% | +10.81% | None/None | n/a | 7.51 | False | **NO_EDGE** |
| tsmom|{'lookback': 60, 'skip': 21}|long | +3.26% | 0.388 | -30.47% | +6.56% | None/None | n/a | 5.89 | False | **NO_EDGE** |
| tsmom|{'lookback': 60, 'skip': 21}|ls | +3.45% | 0.341 | -27.95% | +8.46% | None/None | n/a | 7.59 | False | **NO_EDGE** |
| tsmom|{'lookback': 120, 'skip': 21}|long | +2.76% | 0.333 | -30.45% | +4.76% | None/None | n/a | 5.96 | False | **NO_EDGE** |
| tsmom|{'lookback': 120, 'skip': 21}|ls | +3.37% | 0.333 | -26.02% | +4.82% | None/None | n/a | 7.62 | False | **NO_EDGE** |
| tsmom|{'lookback': 250, 'skip': 21}|long | +2.39% | 0.301 | -15.83% | +6.02% | None/None | n/a | 5.81 | False | **NO_EDGE** |
| tsmom|{'lookback': 250, 'skip': 21}|ls | +3.35% | 0.337 | -24.17% | +7.30% | None/None | n/a | 7.44 | False | **NO_EDGE** |
| donchian|{'entry': 20, 'exit': 10}|long | -4.14% | -0.227 | -46.89% | -5.82% | None/None | n/a | 8.88 | False | **NO_EDGE** |
| donchian|{'entry': 20, 'exit': 10}|ls | -4.14% | -0.227 | -46.89% | -5.82% | None/None | n/a | 8.88 | False | **NO_EDGE** |
| donchian|{'entry': 40, 'exit': 15}|long | -4.22% | -0.235 | -47.33% | -5.82% | None/None | n/a | 8.83 | False | **NO_EDGE** |
| donchian|{'entry': 40, 'exit': 15}|ls | -4.22% | -0.235 | -47.33% | -5.82% | None/None | n/a | 8.83 | False | **NO_EDGE** |
| donchian|{'entry': 55, 'exit': 20}|long | -3.92% | -0.215 | -47.06% | -5.82% | None/None | n/a | 8.8 | False | **NO_EDGE** |
| donchian|{'entry': 55, 'exit': 20}|ls | -3.92% | -0.215 | -47.06% | -5.82% | None/None | n/a | 8.8 | False | **NO_EDGE** |
| 同篮子买入持有 | +2.36% | 0.220 | -52.37% | +4.08% | — | — | — | — | BENCHMARK |

判据：{}

MDE = 1.96 × 年化波动 ÷ √年数；观测值落在这个范围内时，「没看见」不等于「不存在」。
