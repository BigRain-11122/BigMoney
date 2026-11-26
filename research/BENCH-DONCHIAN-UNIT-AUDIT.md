# The breakout arms never ran a breakout

`bench-donchian-unit-audit/1` · generated 2026-11-26T17:25:23+08:00 · evidence cutoff 2026-11-25 · **DONCHIAN_ARMS_ARE_A_CONSTANT_SHORT**

## What this page is

`bench_core.align_futures` gives every rule a **return index** as `closes` (cumprod of roll-adjusted returns, starting at 1.0) and leaves `high`/`low` in **raw price** units. Four of five rule families only compare `closes` with `closes`, so they cannot notice. `donchian` compares `closes` with `highs`/`lows`.

This page counts what that means for the arms already printed.

## Reading 1 — the two series are two units

| product | median(raw high / closes) |
| --- | --- |
| AU | 173.3× |
| IC | 4357.1× |
| IF | 2934.7× |
| IH | 2327.2× |
| IM | 6980.4× |
| RB | 3912.2× |
| SC | 421.4× |
| T | 96.2× |
| TF | 98.0× |
| TS | 98.6× |

A close near 1.0 against a high near 200-900: a close can never exceed the raw high, and is below the raw low on every usable bar.

## Reading 2 — so the state machine opens short once and never flips

| card | params | products | window | bars | live | short | long | long_only did anything? | ann on the card | ann here |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| census_commodity | 20/10 | AU+RB+SC | 2008-01-09 | 4598 | 10761 | 10761 | 0 | no | -4.54% | -4.52% |
| census_commodity | 55/20 | AU+RB+SC | 2008-01-09 | 4598 | 10472 | 10472 | 0 | no | -4.27% | -4.25% |
| census_index_futures, robust_donchian_index | 20/10 | IC+IF+IH+IM | 2017-01-17 | 2391 | 8146 | 8146 | 0 | no | -4.14% | -3.91% |
| census_index_futures, robust_donchian_index | 40/15 | IC+IF+IH+IM | 2017-01-17 | 2391 | 8066 | 8066 | 0 | no | -4.22% | -3.99% |
| census_index_futures, robust_donchian_index | 55/20 | IC+IF+IH+IM | 2017-01-17 | 2391 | 8006 | 8006 | 0 | no | -3.92% | -3.7% |
| fut_trend | 55/20 | AU+IC+IF+IH+IM+RB+SC+T+TF+TS | 2017-03-06 | 2363 | 20960 | 20960 | 0 | no | -13.35% | -13.58% |

**6 of 6 printed combos are 100% short**, and in **6 of 6** flipping `long_only` does not change a single bar. The `|long` and `|ls` rows of the same parameters are one measurement printed twice.

## Reading 3 — which card tokens those rows decided

| card | kind | arms | donchian arms | token printed | recomputed from all rows | without donchian | flips |
| --- | --- | --- | --- | --- | --- | --- | --- |
| census_commodity | census | 14 | 4 | CENSUS_SIGN_MIXED | CENSUS_SIGN_MIXED | CENSUS_LEANS_POSITIVE | yes |
| census_index_futures | census | 20 | 6 | CENSUS_UNPOWERED | CENSUS_UNPOWERED | CENSUS_UNPOWERED | no |
| fut_trend | styles | 5 | 1 | NO_EDGE | n/a | n/a | no |
| robust_donchian_index | robust | 3 | 3 | UNSTABLE_ACROSS_PARAMS | UNSTABLE_ACROSS_PARAMS | no other arms | no |

Dropping the artifact rows changes the card token for: **census_commodity** -- the negative powered rows that made it a two-sided census were the constant short.

`robust_donchian_index` has nothing left when its donchian rows are removed: the whole card is three start dates of the same constant short, and its `UNSTABLE_ACROSS_PARAMS` token was decided by MDE, not by a sign change.

## Reading 4 — what a breakout with one unit returns

Reference only: every series divided by that product's first close, the rule and its parameters untouched. Raw highs/lows still carry contract rolls, so this is the size of the error, not a new verdict on breakouts.

| products | params | reproduced ann / sharpe / mdd | unit-fixed long-only | unit-fixed long-short |
| --- | --- | --- | --- | --- |
| AU+RB+SC | 20/10 | -4.52% / -0.469 / -69.29% | 4.03% / 0.473 / -28.16% | 2.85% / 0.365 / -34.04% |
| AU+RB+SC | 55/20 | -4.25% / -0.431 / -69.41% | 1.65% / 0.224 / -39.59% | 1.96% / 0.263 / -33.92% |
| IC+IF+IH+IM | 20/10 | -3.91% / -0.211 / -46.89% | 0.01% / 0.063 / -35.3% | -3.88% / -0.259 / -50.53% |
| IC+IF+IH+IM | 40/15 | -3.99% / -0.218 / -47.33% | -1.08% / -0.023 / -32.54% | -2.69% / -0.154 / -40.91% |
| IC+IF+IH+IM | 55/20 | -3.7% / -0.198 / -47.06% | 1.65% / 0.193 / -21.63% | -0.44% / 0.027 / -30.98% |
| AU+IC+IF+IH+IM+RB+SC+T+TF+TS | 55/20 | -13.58% / -0.934 / -81.26% | -0.02% / 0.071 / -39.31% | -2.86% / -0.13 / -38.76% |

## What this does not say

- It does not say breakouts work. The printed arms run from -13.58%/yr and a unit-fixed reference reaches at most 4.03%/yr -- still one unlevered, roll-contaminated family with no control run. The honest statement is that **the printed number was a different position**, not that the rule is good.
- It does not re-open any card. The fix belongs in `bench_generic.build_signals` (hand `sig_donchian` one unit), which is a shared code face; this round was a contention window and only new-file faces were written.
- The cards' own numbers were computed on their own cutoffs and windows; reproduction here uses today's panel, so annualised returns move by up to a percentage point between vintages. The state histogram and the dead `long_only` flag do not move.
- Roll jumps are still inside the raw high/low series, so the unit-fixed reference is a size-of-error reading, not a clean re-run.

## Reproduction

```
python scripts/bench_donchian_unit_audit.py --check    # offline selftest
python scripts/bench_donchian_unit_audit.py --verify    # recompute and diff
```
