# Nine ways to choose the hedge size, raced out of sample

Generated 2026-11-24T04:43:48+08:00 · evidence cutoff 2026-11-20 · machine bm-c

## Why this face exists

r2023 chose a hedge size from a drawdown budget and r2024 read the same budget on daily marks; both pickers were *return-maximisers wearing a budget constraint* — rule A takes the best in-sample return that fits, so it follows in-sample return noise wherever it goes. The open question is not which ruler is right, it is which **way of choosing** survives. Nine rules are frozen before the run, each sees 43 in-sample periods only, and all nine are read on 34 out-of-sample periods (680 marked days). Position is unchanged: k = 0 reproduces the parent's daily drawdown to 0.0e+00, and the k = 0.65 / 1.00 arms match the parent's own ``arm_series`` over 154 periods to 5.2e-15.

## The answer at the primary budget

**FITTING_HURTS** — one unit of beta held the 20% budget out of sample (19.89%) while 5 of 8 fitted pickers breached it.

The mechanical reference: **one unit of beta** (k = 1.00) lived a 12.25% in-sample drawdown and 8.32% annualised, and reads 19.89% / 9.82% out of sample. **No hedge** (k = 0) reads 25.90% with 16.44% annualised out of sample.

## The race, budget by budget

`p_hold` is the share of circular block-bootstrap draws over the same out-of-sample periods in which that size would still have fitted the budget (600 draws, block = 4 periods, seed 20261124) — a point drawdown on 34 periods is one observation, and this is the price of it.

| picker | 10% budget | 15% budget | 20% budget | 25% budget |
|---|---|---|---|---|
| **FIXED_ONE** | 1.00 → 19.89% over (p 0.09) | 1.00 → 19.89% over (p 0.13) | 1.00 → 19.89% ok (p 0.69) | 1.00 → 19.89% ok (p 0.87) |
| **A_PERIOD** | 0.85 → 18.72% over (p 0.08) | 0.65 → 18.74% over (p 0.12) | 0.65 → 18.74% ok (p 0.34) | 0.65 → 18.74% ok (p 0.77) |
| **A_DAILY** | — | 1.10 → 20.74% over (p 0.32) | 1.10 → 20.74% over (p 0.64) | 1.10 → 20.74% ok (p 0.87) |
| **B_PERIOD** | 0.85 → 18.72% over (p 0.08) | 0.35 → 21.71% over (p 0.06) | 0.15 → 23.72% over (p 0.10) | 0.00 → 25.90% over (p 0.17) |
| **B_DAILY** | — | 0.60 → 19.23% over (p 0.12) | 0.35 → 21.71% over (p 0.21) | 0.15 → 23.72% ok (p 0.24) |
| **B_MARGIN** | — | — | 0.50 → 20.22% over (p 0.26) | 0.35 → 21.71% ok (p 0.35) |
| **MID_DAILY** | — | 0.95 → 19.48% over (p 0.14) | 0.95 → 19.48% ok (p 0.68) | 0.95 → 19.48% ok (p 0.87) |
| **MIN_IS_DD** | 1.05 → 20.29% over (p 0.09) | 1.05 → 20.29% over (p 0.29) | 1.05 → 20.29% over (p 0.69) | 1.05 → 20.29% ok (p 0.88) |
| **MAX_SHARPE** | 0.95 → 19.48% over (p 0.09) | 0.95 → 19.48% over (p 0.14) | 0.95 → 19.48% ok (p 0.68) | 0.95 → 19.48% ok (p 0.87) |

What each rule means, so the table is readable without the code:

- **FIXED_ONE** — k = 1.00, no estimation
- **A_PERIOD** — max in-sample period return that fits (r2023's rule)
- **A_DAILY** — max in-sample daily return that fits (r2024's rule)
- **B_PERIOD** — smallest size the period ruler allows
- **B_DAILY** — smallest size the daily ruler allows
- **B_MARGIN** — smallest size that keeps 80% of the budget
- **MID_DAILY** — middle of the in-sample feasible daily band
- **MIN_IS_DD** — shallowest in-sample daily drawdown
- **MAX_SHARPE** — best in-sample daily Sharpe

## Per-budget verdicts

- **10%** — `NO_BUDGET_IS_HELD`: nothing on the grid held a 10% budget out of sample, fitted or mechanical; the shallowest drawdown any size produced was 18.07%
  - held: — · broke: A_PERIOD, B_PERIOD, MAX_SHARPE, MIN_IS_DD
- **15%** — `NO_BUDGET_IS_HELD`: nothing on the grid held a 15% budget out of sample, fitted or mechanical; the shallowest drawdown any size produced was 18.07%
  - held: — · broke: A_DAILY, A_PERIOD, B_DAILY, B_PERIOD, MAX_SHARPE, MID_DAILY, MIN_IS_DD
- **20%** — `FITTING_HURTS`: one unit of beta held the 20% budget out of sample (19.89%) while 5 of 8 fitted pickers breached it
  - held: A_PERIOD, MAX_SHARPE, MID_DAILY · broke: A_DAILY, B_DAILY, B_MARGIN, B_PERIOD, MIN_IS_DD
- **25%** — `FITTING_HELPS`: one unit of beta held the budget, and 5 fitted picker(s) held it with more out-of-sample return (A_PERIOD, B_DAILY, B_MARGIN, MAX_SHARPE, MID_DAILY)
  - held: A_DAILY, A_PERIOD, B_DAILY, B_MARGIN, MAX_SHARPE, MID_DAILY, MIN_IS_DD · broke: B_PERIOD

## Why the breakers broke

At the primary budget the sizes that held form a band, k ≈ 0.65–0.95, and the sizes that broke sit on **both** sides of it (below: 0.15, 0.35, 0.50) (above: 1.05, 1.10). Below the band the budget was being read as a ceiling to spend down: every rule that bought only the minimum the budget allowed (k = 0.15–0.50) landed 20.2–23.7%, because the drawdown is produced by the unhedged beta and buying less insurance stops cutting the thing it was bought for. Above the band the short leg's own volatility starts to be the drawdown — that is the over-hedge r2023 already priced. So the fitted family does not split on which ruler it uses; it splits on whether it lands inside a band it could not have known in advance.

Read the other way, this also says something unflattering about the pickers that survived: `MIN_IS_DD`, `MID_DAILY` and `MAX_SHARPE` all landed within a step or two of k = 1.00, i.e. they agree with the mechanical answer, and their agreement is not independent evidence — it is the same answer reached three ways.

## What this face does not do

- It does not search for a better picker. Nine rules were frozen, all nine are printed, and no threshold was moved after seeing the answer.
- The bootstrap resamples periods, not history: it re-orders the same 34 out-of-sample periods and cannot create a drawdown that never happened. It answers 'how much of this is the sample', not 'what will happen next'.
- Still not modelled: margin calls, borrow availability beyond a flat carry, as-traded prices without dividends, and the book's own survivorship (the same caveats the parents carry).
- This is a sizing study on one book, not a tradable strategy; the deliverable is which choices are robust, not a position to hold.
