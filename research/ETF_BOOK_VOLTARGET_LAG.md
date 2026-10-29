# The 8% vol target is late in two different ways

Face: `results/etf_book_voltarget_lag.json` (evidence cutoff 2026-10-28). Control: `vol_window=60`, n12/r20, 10bp/side.

## Arms (only `vol_window` differs)

| vol_window | CAGR | Sharpe | maxDD | vol | turnover | OOS CAGR | OOS maxDD |
|---|---|---|---|---|---|---|---|
| 20 | 11.30% | 1.093 | -11.87% | 10.73% | 1.029 | 20.52% | -11.87% |
| 40 | 10.28% | 1.057 | -11.40% | 10.13% | 0.952 | 18.86% | -11.40% |
| 60 (control) | 9.70% | 1.000 | -11.77% | 10.17% | 0.934 | 18.64% | -10.70% |
| 120 | 7.31% | 0.837 | -12.19% | 9.30% | 0.894 | 13.51% | -10.37% |

## What the frozen scale was actually wrong by

79 slots measured (decision to decision). Median realised/estimated = **1.06**, p90 = 1.90, 20.2% of slots ran past 1.5x their estimate and 8.9% past 2x; 87.3% of slots were delevered (scale < 1).

Mean estimate 12.29% vs mean realised 13.57% per slot; the median delivered vol was 8.31% against a 8% target, and 20.2% of slots delivered more than 1.5x the target.

Worst five slots (realised / estimated): 2020-02-07 3.66x (scale 0.75), 2025-09-10 2.68x (scale 0.76), 2025-04-17 2.53x (scale 0.85), 2024-02-21 2.27x (scale 1.00), 2025-10-16 2.24x (scale 0.94)

## The deepest drawdown, and whether the overlay was there for it

2021-09-14 -> 2022-11-01, depth -11.77% over 271 bars; the book was at full size on 31.4% of those bars (mean scale 0.83) and **42% of the fall accumulated on exactly those bars**.

## What the two lags actually cost

Depth is nearly invariant across the four estimators (maxDD -12.19%..-11.40%, a spread of 0.79pp) while return is not (CAGR 7.31%..11.30%, a spread of 3.99pp). So the lateness is not a drawdown problem -- the overlay is not what sets the depth at these vol levels -- it is a RETURN problem: a stale high estimate keeps the book de-levered while the rebound happens. That matches the slot census: 87.3% of slots were delevered and the median delivered vol was 8.31% against a 8% target.

## Verdict

**KEEP** -- no window buys 1.0pp of depth inside the -0.5pp return floor.

Read this as a bound on the overlay, not an invitation: a shorter window is a faster estimator, and the frozen rule asks it to buy DEPTH, not return. If it cannot, the lateness stays as the price of not trading on noise -- the same trade the decision-margin census found (E187 family) -- and the return it gives up should be quoted beside the headline rather than assumed to be free insurance.

## Caveats

- one panel, one cost model (10bp/side, next-open), survivor-pool caveat unchanged
- the arms differ ONLY in vol_window; selection, holdings and the cost model are shared, so a difference is the estimator's, not the book's
- a sizing overlay is not an alpha: KEEP is the expected verdict and a CANDIDATE is a risk-shape proposal, not a return claim
- scale is recomputed at decisions by construction; this face measures the delivered consequence of that, it does not change the engine
