# Do the bench's GO verdicts survive their own benchmark?

generated 2026-11-26T23:15:33+08:00 | faces audited 21 | arms audited 85

Read-only audit over `results/bench_*.json`. It never rewrites a verdict.

## Headline

- GO rows printed by the bench: **4**
- of those, distinct measurements after de-duplicating faces that ran the same rule on the same panel: **2**
- GO rows whose excess over the *aligned* benchmark clears the arm's own MDE: **0**
- GO rows whose excess cannot be seen at this sample size: **4**
- faces whose printed benchmark was sized at a different volatility target: **0 of 21**

## The two rulers

The gate asks one question: is the arm's **absolute** annualised return above 4.0% (and above the face's `target_edge_pp`), with an MDE small enough to resolve that target? It never asks what the money would have earned just sitting in the same products at the same size.

The second ruler subtracts the buy-and-hold book, **re-priced at the arm's own `target_vol`**, and compares that excess with the arm's own MDE. An excess smaller than the arm's MDE is not a small edge -- it is a quantity this sample cannot measure.

## Where the printed benchmark was a different size

A face whose arm already ran at the benchmark's own 0.10 target vol is a built-in control: its gap cannot be a sizing effect, only the noise from re-pricing today's panel against a banner computed on an earlier cutoff. That control puts the noise floor at **0.00 pp**. 0 face(s) exceed it.

| face | arm target vol | printed banner %/yr | same book at arm's vol %/yr | gap pp |
|---|---|---|---|---|
| (none) | | | | |

## Face by face

| face | arms | GO | GO unsupported | left behind | banner gap pp |
|---|---|---|---|---|---|
| _bond_curve | 6 | 0 | 0 | 0 | - |
| _cash_window_sensitivity | 4 | 0 | 0 | 0 | - |
| _census_bond_futures | 5 | 0 | 0 | 0 | +0.00 |
| _census_commodity | 14 | 2 | 2 | 0 | +0.00 |
| _census_index_futures | 20 | 0 | 0 | 0 | +0.00 |
| _fut_trend | 5 | 0 | 0 | 0 | - |
| _pair_all10_60d | 1 | 0 | 0 | 0 | +0.00 |
| _pair_bond_curve_60d | 1 | 0 | 0 | 0 | +0.00 |
| _pair_commodity_60d | 1 | 0 | 0 | 0 | +0.00 |
| _pair_index_60d | 1 | 0 | 0 | 0 | +0.00 |
| _repo_ladder | 11 | 0 | 0 | 0 | - |
| _reversal_commodity_5d | 1 | 0 | 0 | 0 | +0.00 |
| _reversal_index_5d | 1 | 0 | 0 | 0 | +0.00 |
| _robust_donchian_index | 3 | 0 | 0 | 0 | +0.00 |
| _robust_ma_index | 3 | 0 | 0 | 0 | +0.00 |
| _robust_tsmom_commodity | 3 | 2 | 2 | 0 | +0.00 |
| _trend_single_AU_long | 1 | 0 | 0 | 0 | +0.00 |
| _trend_single_IC_long | 1 | 0 | 0 | 0 | +0.00 |
| _trend_single_RB_long | 1 | 0 | 0 | 0 | +0.00 |
| _trend_single_SC_long | 1 | 0 | 0 | 0 | +0.00 |
| _trend_single_T_long | 1 | 0 | 0 | 0 | +0.00 |

## Every GO, with both readings

| face | variant | ann %/yr | bench @arm vol %/yr | excess pp | MDE pp | label |
|---|---|---|---|---|---|---|
| _census_commodity | tsmom|{'lookback': 120, 'skip': 21}|ls | 4.99 | 3.8 | 1.19 | 3.78 | GO_ON_A_RULER_THAT_CANNOT_SEE_ITS_EXCESS |
| _census_commodity | tsmom|{'lookback': 250, 'skip': 21}|ls | 5.19 | 3.8 | 1.39 | 3.66 | GO_ON_A_RULER_THAT_CANNOT_SEE_ITS_EXCESS |
| _robust_tsmom_commodity | 120d | 4.99 | 3.8 | 1.19 | 3.78 | GO_ON_A_RULER_THAT_CANNOT_SEE_ITS_EXCESS |
| _robust_tsmom_commodity | 250d | 5.19 | 3.8 | 1.39 | 3.66 | GO_ON_A_RULER_THAT_CANNOT_SEE_ITS_EXCESS |

The same measurement can appear on more than one face: `census_commodity` and `robust_tsmom_commodity` run the same (rule, lookback) on the same panel, so their rows share one ann/MDE. Grouped by measurement:

| ann %/yr | MDE pp | label | faces carrying it |
|---|---|---|---|
| 4.99 | 3.78 | GO_ON_A_RULER_THAT_CANNOT_SEE_ITS_EXCESS | _census_commodity, _robust_tsmom_commodity |
| 5.19 | 3.66 | GO_ON_A_RULER_THAT_CANNOT_SEE_ITS_EXCESS | _census_commodity, _robust_tsmom_commodity |

## What this face does not say

- it does not re-run a single arm, so it inherits whatever the bench measured; it only re-prices the benchmark at the arm's size and puts the two rulers side by side
- an `UNDECIDABLE` row means the face printed no MDE or no usable benchmark (missing products, missing config), not that the edge was zero
- `EXCESS_CLEARS_MDE_BUT_GATE_FAILED_ELSEWHERE` says the absolute gate said no while the excess ruler said it was visible: that is a disagreement about *which* question was asked, not evidence that the arm should have been promoted
- the aligned benchmark uses the face's own `cost_bp_side`; a face that printed no cost cannot be aligned and is listed under `errors`, not silently dropped
