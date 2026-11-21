# The tail beta, with an interval

Cutoff 2026-11-20 | 1592 bar pairs (2020-01-06..2026-11-20) | 2000 resamples of 21-bar blocks, seed 20261115.

Unconditional beta 0.0748 (corr 0.142).

| slice | n | beta | 90% interval | share of draws above the average beta |
| --- | --- | --- | --- | --- |
| ih_le_-1 | 235 | 0.3179 | [0.0166, 0.5104] | 89% |
| ih_le_-2 | 52 | 0.6126 | [0.1183, 0.8303] | 96% |

## The correctly sized short (k = 1 x beta)

| reading | point | 90% interval |
| --- | --- | --- |
| sharpe change | -0.0205 | [-0.0976, +0.0724] |
| vol change | -0.0010 | [-0.0029, -0.0002] |
| maxdd change | -0.0006 | [-0.0061, +0.0289] |

## Verdict

- tail: **TAIL_BETA_IS_REAL**
- hedge: **HEDGE_NOT_MEASURABLE**

尾部 beta 0.613 建在 52 天上，90% 的抽样区间是 [0.118, 0.830]；按 beta 精确对冲的夏普变化 -0.020，区间 [-0.098, +0.072]。

