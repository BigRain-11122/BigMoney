# census_bond_futures

cell `census_bond_futures` · type `census` · rule `None` · cutoff 2026-11-23 · **CENSUS_LEANS_POSITIVE**

| 臂 | 全期年化 | 夏普 | 回撤 | 样本外年化 | 前后半 | 剔除最好一年 | MDE | 可分辨? | 判决 |
|---|---|---|---|---|---|---|---|---|---|
| tsmom|{'lookback': 60, 'skip': 21}|long | +3.20% | 0.523 | -11.64% | +6.79% | None/None | n/a | 4.02 | True | **NO_EDGE** |
| tsmom|{'lookback': 120, 'skip': 21}|long | +3.20% | 0.511 | -13.59% | +6.68% | None/None | n/a | 4.13 | True | **NO_EDGE** |
| tsmom|{'lookback': 250, 'skip': 21}|long | +2.83% | 0.453 | -14.48% | +6.61% | None/None | n/a | 4.17 | True | **NO_EDGE** |
| ma_cross|{'fast': 20, 'slow': 60}|long | +1.92% | 0.340 | -17.89% | +5.95% | None/None | n/a | 3.84 | True | **NO_EDGE** |
| ma_cross|{'fast': 50, 'slow': 200}|long | +4.01% | 0.627 | -11.22% | +6.43% | None/None | n/a | 4.15 | True | **NO_EDGE** |
| 同篮子买入持有 | +5.50% | 0.584 | -19.27% | +9.11% | — | — | — | — | BENCHMARK |

判据：{}

MDE = 1.96 × 年化波动 ÷ √年数；观测值落在这个范围内时，「没看见」不等于「不存在」。
