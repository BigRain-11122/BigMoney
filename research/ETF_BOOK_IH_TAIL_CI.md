# The tail beta, with an interval

Cutoff 2026-11-17 | 1662 bar pairs (2020-01-06..2026-11-17) | 2000 resamples of 21-bar blocks, seed 20261115.

Unconditional beta 0.0719 (corr 0.137).

| slice | n | beta | 90% interval | share of draws above the average beta |
| --- | --- | --- | --- | --- |
| ih_le_-1 | 254 | 0.3105 | [0.0243, 0.5042] | 90% |
| ih_le_-2 | 57 | 0.6116 | [0.1267, 0.8343] | 97% |

## The correctly sized short (k = 1 x beta)

| reading | point | 90% interval |
| --- | --- | --- |
| sharpe change | 0.0057 | [-0.0637, +0.0945] |
| vol change | -0.0009 | [-0.0026, -0.0001] |
| maxdd change | 0.0155 | [-0.0009, +0.0300] |

## Verdict

- tail: **TAIL_BETA_IS_REAL**
- hedge: **HEDGE_NOT_MEASURABLE**

尾部 beta 0.612 建在 57 天上，90% 的抽样区间是 [0.127, 0.834]；按 beta 精确对冲的夏普变化 0.006，区间 [-0.064, +0.094]。

