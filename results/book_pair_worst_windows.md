# The books at their worst: does the split hold where the ETF book actually hurts?

- generated: 2026-11-27T17:05:16+08:00 · evidence cutoff: **2026-11-26** · window 2020-01-06..2026-11-26 (1670 bars)
- sleeve: 30% convertible / 70% ETF (parent's own choice, not re-chosen)
- verdict: **CUSHION_PARTIAL**

## A. The ETF book's worst 252 bars

| column | worst window | return |
|---|---|---|
| ETF | 2021-09-10 .. 2022-09-27 | **-6.62%** |
| blend 30/70, same bars | 2021-09-10 .. 2022-09-27 | **-4.97%** |
| convertible, same bars | 2021-09-10 .. 2022-09-27 | -1.83% |

The ETF book had **78** negative 252-bar windows out of 1419.

For reference the blend's own worst 252 bars: 2025-11-12 .. 2026-11-26 = **-6.20%** (ETF -0.13%, cb -19.43%).

## B. The ETF book's losing months — the bars that do exist

Months the ETF book ended down: **32**. The blend was better in **16** of them.

| on those same months | mean |
|---|---|
| ETF | -1.41% |
| blend 30/70 | **-0.98%** |
| convertible | +0.01% |

Worst of those months for the blend: **2026-11** — ETF -3.10%, blend -3.70%, cb -5.12%.

## What this does and does not settle

- a bad month is not a bad year: the month test says how the split behaves on the ETF's losing months, not on a sustained year-long drawdown it has never had
- rolling 252-bar windows overlap (1670 windows over 7 years), so the worst-window quantile is a description of this path, not an estimate of a distribution
- the 30/70 weight is the parent's in-sample optimum, inherited here without re-testing

Cross-check against the published blend face: CAGR matches / Sharpe matches (tolerance 1e-6).
