# Does the cash benchmark answer depend on how far back you look?

Window of the arms: 2005-02-23 -> 2026-11-20 (5285 bars). Cash vehicle: results/bench_repo_ladder.json, 3772 points, 2011-05-13 -> 2026-11-20.

## The cash vehicle's own ladder (nothing to do with any book)

| lookback | GC001 roll, net | on 1,000,000 CNY |
|---|---|---|
| 21 bars | 0.9200% | 9,200 CNY |
| 63 bars | 0.9762% | 9,762 CNY |
| 126 bars | 0.9858% | 9,858 CNY |
| 252 bars | 1.0659% | 10,659 CNY |
| 504 bars | 1.2614% | 12,614 CNY |
| 1008 bars | 1.6197% | 16,197 CNY |
| full | 2.4938% | 24,938 CNY |

Full-sample roll 2.4938% against the published vehicle 2.4947% (gap -0.001pp); the constant the older faces used is 1.7770% from `results/capital_placement.json`.

## Excess over cash, per arm and per lookback

| arm | 21 | 63 | 126 | 252 | 504 | 1008 | full | verdict | flip between |
|---|---|---|---|---|---|---|---|---|
| tuned_composite_6 | -33.93pp | -17.27pp | -4.44pp | 0.50pp | 18.47pp | 14.34pp | 8.66pp | FLIPS_WITH_LOOKBACK | 126 -> 252 |
| single_mom_12_1 | -36.98pp | -23.77pp | -15.33pp | -5.48pp | 0.51pp | 0.34pp | 1.26pp | FLIPS_WITH_LOOKBACK | 252 -> 504 |
| single_vol_60_low | 8.96pp | -17.69pp | -14.76pp | -10.36pp | 1.86pp | 7.59pp | 4.55pp | FLIPS_WITH_LOOKBACK | 21 -> 63 |
| random_pick_5 | -38.46pp | -25.05pp | -15.93pp | -6.76pp | 0.96pp | -1.66pp | -2.88pp | FLIPS_WITH_LOOKBACK | 252 -> 504 |

Full-sample daily excess t (no overlap correction): tuned_composite_6 2.39, single_mom_12_1 0.71, single_vol_60_low 1.35, random_pick_5 -0.52

## What each rung actually reads

| lookback | cash window | cash | tuned_composite_6 | single_mom_12_1 | single_vol_60_low | random_pick_5 |
|---|---|---|---|---|---|---|
| 21 | 2026-10-22 -> 2026-11-20 | 0.9200% | -33.93pp | -36.98pp | 8.96pp | -38.46pp |
| 63 | 2026-08-17 -> 2026-11-20 | 0.9762% | -17.27pp | -23.77pp | -17.69pp | -25.05pp |
| 126 | 2026-05-19 -> 2026-11-20 | 0.9858% | -4.44pp | -15.33pp | -14.76pp | -15.93pp |
| 252 | 2025-11-06 -> 2026-11-20 | 1.0659% | 0.50pp | -5.48pp | -10.36pp | -6.76pp |
| 504 | 2024-10-24 -> 2026-11-20 | 1.2614% | 18.47pp | 0.51pp | 1.86pp | 0.96pp |
| 1008 | 2022-09-20 -> 2026-11-20 | 1.6197% | 14.34pp | 0.34pp | 7.59pp | -1.66pp |
| full | 2011-05-13 -> 2026-11-20 | 2.4938% | 8.66pp | 1.26pp | 4.55pp | -2.88pp |

## If the decision is taken today (1-year and 2-year rungs only)

**one-year (lookback 252 bars)** -- arms above cash: tuned_composite_6

| arm | excess | on 1,000,000 CNY |
|---|---|---|
| tuned_composite_6 | 0.50pp | 5,046 CNY |
| single_mom_12_1 | -5.48pp | -54,772 CNY |
| random_pick_5 | -6.76pp | -67,584 CNY |
| single_vol_60_low | -10.36pp | -103,604 CNY |

**two-year (lookback 504 bars)** -- arms above cash: tuned_composite_6, single_vol_60_low, random_pick_5, single_mom_12_1

| arm | excess | on 1,000,000 CNY |
|---|---|---|
| tuned_composite_6 | 18.47pp | 184,678 CNY |
| single_vol_60_low | 1.86pp | 18,632 CNY |
| random_pick_5 | 0.96pp | 9,635 CNY |
| single_mom_12_1 | 0.51pp | 5,102 CNY |

**Today's reading: SOME_ARMS_CLEAR_CASH_ON_A_HORIZON_READER_CAN_DEFEND.** judged on the 1-year and 2-year rungs only: these are the horizons whose cash rate is still the rate you can get today; the longer rungs answer a different question, namely what this book did when cash paid 2.5%

**Headline: LOOKBACK_DECIDES_THE_ANSWER.**

Why: the sign of excess-over-cash flips inside the frozen ladder

Arms whose sign flips inside the ladder: tuned_composite_6, single_mom_12_1, single_vol_60_low, random_pick_5

What this face does not claim: the daily excess t does not correct for overlapping 20-bar holding periods; it is a scale reference, not a significance claim; a short lookback's CAGR is that many days' return annualised, so the 21- and 63-bar rungs are noisier by construction than the 1008-bar and full rungs; they are printed so the flip is visible, not as comparable long-run returns; arms are priced on a surviving-ETF universe; the lookback ladder cannot remove that bias; cash is one vehicle (SSE GC001 net of commission); other liquid legs may carry a different window profile; no lookback was added after seeing a result; the ladder is the frozen question

Generated 2026-11-23T05:38:29+0800 by `scripts/bench_cash_window_sensitivity.py`.
