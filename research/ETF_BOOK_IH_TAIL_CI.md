# The tail beta, with an interval

Cutoff 2026-11-19 | 1590 bar pairs (2020-01-06..2026-11-18) | 2000 resamples of 21-bar blocks, seed 20261115.

Unconditional beta 0.0746 (corr 0.142).

| slice | n | beta | 90% interval | share of draws above the average beta |
| --- | --- | --- | --- | --- |
| ih_le_-1 | 235 | 0.3179 | [0.0218, 0.5152] | 89% |
| ih_le_-2 | 52 | 0.6126 | [0.1251, 0.8361] | 97% |

## The correctly sized short (k = 1 x beta)

| reading | point | 90% interval |
| --- | --- | --- |
| sharpe change | -0.0206 | [-0.1000, +0.0732] |
| vol change | -0.0010 | [-0.0029, -0.0001] |
| maxdd change | -0.0005 | [-0.0055, +0.0299] |

## Verdict

- tail: **TAIL_BETA_IS_REAL**
- hedge: **HEDGE_NOT_MEASURABLE**

尾部 beta 0.613 建在 52 天上，90% 的抽样区间是 [0.125, 0.836]；按 beta 精确对冲的夏普变化 -0.021，区间 [-0.100, +0.073]。

