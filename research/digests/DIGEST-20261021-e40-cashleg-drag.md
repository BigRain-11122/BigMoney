# DIGEST 2026-10-21 — E40 cash-leg drag: 16% of the 2020+ ladder is repo, and it pays 36bp/yr

Round r1114, bm-b. Script `scripts/e39_panel_census.py` (`cashdrag` leg, selftest 18/18).
Face `results/e40_cashleg_drag/CASHLeg-20261020.json`. Evidence cutoff 2026-10-20, window
2020-01-01 (1,645 bars, 82 month-end decisions), top9999, sh511 excluded, cost x1.

## The mechanism, measured instead of assumed

`e27.simulate` holds cash for the un-invested weight `1 - sum(weights)`. Two things follow that
the earlier digests got wrong in opposite directions:

- **The first month end is not the first investment.** The first trading rebalance is index 262
  (2021-02-01) because eligibility needs a burn-in; every earlier month end finds an empty live
  set and the book stays 100% in repo. **263 bars — 16.0% of the window — are pure cash.**
- **A missing member price does not park money.** The equal weight is taken over the live names
  only, so 12.71% of bars having ≥1 missing member (the E39 ladder digest's "cash leg") creates
  **zero** cash weight. That field name invited the misreading; this leg pins the mechanism.

## Measured

| scheme | x0 repo (0%) | x1 repo (1.98%) | x3 repo (5.94%) | cash-attributable (x1-x0) | maxDD move |
|---|---|---|---|---|---|
| ladder5 | -0.79 %/yr | -0.43 %/yr | +0.31 %/yr | **+36.0 bp/yr** | 0.00 pp |
| wide top9999 | +0.49 %/yr | +0.86 %/yr | +1.60 %/yr | **+37.0 bp/yr** | 0.00 pp |

Repo panel covers 1,645/1,645 bars (1 ffilled day), mean 0.7875 bp/day = 1.98%/yr,
2011-05-13 .. 2026-10-19. Cumulative cash accrual on the ladder: curve starts at 1.000122 after
one bar and the whole x1/x0 ratio ends at 1.0244 after 1,645 bars — consistent with ~263 bars at
repo plus the higher year-end funding rates inside them.

## Why it matters

1. **16% of the 2020+ window is a bank account.** Every annualised figure quoted on this window
   mixes a repo year with 5.5 years of equity. It is not a defect (the engine is honest about the
   un-invested weight) but it means the ladder's -0.43%/yr is measured on 84% exposure, and a
   "0% cash" convention would read -0.79%/yr.
2. **The cash leg is not a cushion.** maxDD is byte-identical at x0 and x1 for both schemes
   (delta 0.00pp): the ladder's -42.72% drawdown runs 2021-09 → 2024-02, entirely after the book
   went in. Any claim that repo softened the drawdown is false.
3. **It is second-order but not negligible.** 36–37 bp/yr is about a quarter of the +134bp/yr
   wide-book spread, and sensitivity is near linear (x3 ≈ 2.9× the x1 delta), so this is a rate
   effect, not an interaction with the equity leg.

## Honest limits

- Multipliers are counterfactual rates, not rates that ever existed; x0 reproduces the historical
  zero-cash convention (`cash=None`), not a separate model.
- One window (2020+). The 2018 window would move the invested date to 2019-02-01 (265 cash bars)
  but the drawdown path is what the repo rate cannot touch (0.00pp at x1 vs x0).
- Descriptive census only: zero prereg, zero judgement, zero ledger booking, trial_count 0.

## Pool / next

E40-CASHLEG-DRAG closed with `result_ref`. Ready units: E40-LADDER-STYLE-EXPOSURE,
E41-REBAL-DAY-SENSITIVITY (does the verdict survive a rebalance-day shift?), E41-SPREAD-ERA-DECAY
(is the spread a regime or a constant?) — supply floor 3/3 restored.