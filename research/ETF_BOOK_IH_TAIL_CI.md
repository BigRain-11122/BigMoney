# The tail beta, with an interval

Cutoff 2026-11-24 | 1594 bar pairs (2020-01-06..2026-11-24) | 2000 resamples of 21-bar blocks, seed 20261115.

Unconditional beta 0.0748 (corr 0.141).

| slice | n | beta | 90% interval | share of draws above the average beta |
| --- | --- | --- | --- | --- |
| ih_le_-1 | 235 | 0.3179 | [0.0232, 0.5149] | 90% |
| ih_le_-2 | 52 | 0.6126 | [0.1323, 0.8348] | 97% |

## The correctly sized short (k = 1 x beta)

| reading | point | 90% interval |
| --- | --- | --- |
| sharpe change | -0.0214 | [-0.1001, +0.0675] |
| vol change | -0.0010 | [-0.0029, -0.0001] |
| maxdd change | -0.0006 | [-0.0064, +0.0271] |

## Verdict

- tail: **TAIL_BETA_IS_REAL**
- hedge: **HEDGE_NOT_MEASURABLE**

尾部 beta 0.613 建在 52 天上，90% 的抽样区间是 [0.132, 0.835]；按 beta 精确对冲的夏普变化 -0.021，区间 [-0.100, +0.067]。

