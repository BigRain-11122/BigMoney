# The tail beta, with an interval

Cutoff 2026-11-26 | 1596 bar pairs (2020-01-06..2026-11-26) | 2000 resamples of 21-bar blocks, seed 20261115.

Unconditional beta 0.0752 (corr 0.142).

| slice | n | beta | 90% interval | share of draws above the average beta |
| --- | --- | --- | --- | --- |
| ih_le_-1 | 236 | 0.3162 | [0.0193, 0.5031] | 90% |
| ih_le_-2 | 52 | 0.6126 | [0.1228, 0.8365] | 97% |

## The correctly sized short (k = 1 x beta)

| reading | point | 90% interval |
| --- | --- | --- |
| sharpe change | -0.0205 | [-0.0984, +0.0670] |
| vol change | -0.0010 | [-0.0029, -0.0002] |
| maxdd change | -0.0006 | [-0.0057, +0.0288] |

## Verdict

- tail: **TAIL_BETA_IS_REAL**
- hedge: **HEDGE_NOT_MEASURABLE**

尾部 beta 0.613 建在 52 天上，90% 的抽样区间是 [0.123, 0.836]；按 beta 精确对冲的夏普变化 -0.020，区间 [-0.098, +0.067]。

