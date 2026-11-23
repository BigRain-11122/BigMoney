# The default hedge size, and what would have to be true to stop using it

Generated 2026-11-24T05:08:39+08:00 · evidence cutoff 2026-11-20 · machine bm-c

## Why this face exists

r2023 priced the hedging decision, r2024 re-read it on daily marks and r2025 raced nine ways of choosing; none of them said which size a book should hold by default, or what would have to be true to stop holding it.

Nothing is re-fitted here. Every reading below is the parent's published cell, quoted; the parent's content digest is recorded so a moved parent is visible as a moved parent and not as this face being wrong.

## The default

**ONE_UNIT_OF_BETA_IS_THE_DEFAULT** — k = 1.00, i.e. **90.13% of the book** goes to the hedge at beta = 0.9013.

a mechanical size nobody estimated: r2025 showed it holds the 20% and 25% budgets out of sample while 5 of 8 fitted pickers breached the 20% one.

## What the default costs, budget by budget

`headroom` is the budget minus the default's own out-of-sample drawdown, in percentage points; negative means the default is already over. `shallowest` is the smallest out-of-sample drawdown anywhere on the grid, picked after the fact — the number you would need to have known in advance.

| budget | default holds | default OOS dd | headroom | shallowest on the grid | p(default holds) | what the race said |
|---|---|---|---|---|---|---|
| 10% | **no** | 19.89% | -9.89 pp | 18.07% (k=0.75) | 0.09 | NO_BUDGET_IS_HELD |
| 15% | **no** | 19.89% | -4.89 pp | 18.07% (k=0.75) | 0.13 | NO_BUDGET_IS_HELD |
| 20% | yes | 19.89% | +0.11 pp | 18.07% (k=0.75) | 0.69 | FITTING_HURTS |
| 25% | yes | 19.89% | +5.11 pp | 18.07% (k=0.75) | 0.87 | FITTING_HELPS |

At 10% and 15% the default does not fit, and neither does anything else on the grid: the constraint is the budget, not the size. Tightening the size to fit a budget that no size fits is not risk control, it is arithmetic on a number that cannot be paid.

Where it does fit, read the headroom and the hold-probability together: 20% leaves +0.11 pp of headroom and a 0.69 chance of still fitting on a resample; 25% leaves +5.11 pp of headroom and a 0.87 chance of still fitting on a resample. The 20% budget is the one to stare at: 0.11 pp is not safety, it is the narrowest gap on the table, and the default is only the better bet because the alternatives are less predictable, not because it is comfortable.

## The nine rules, standing

`RETIRED` holds on none of the budgets where anything holds; `CONDITIONAL` holds on some; `ROBUST` holds on all of them; `DEFAULT` is the default. `p` is the bootstrap hold-probability at that budget — on 34 out-of-sample periods a point drawdown is one observation, and this is what one observation is worth. A rule reading `over` at 10% or 15% is not being marked down for it: no rule holds those budgets, so a size is not what is failing there.

| rule | standing | 10% | 15% | 20% | 25% |
|---|---|---|---|---|---|
| **FIXED_ONE** | DEFAULT | 1.00 → 19.89% over (p 0.09) | 1.00 → 19.89% over (p 0.13) | 1.00 → 19.89% ok (p 0.69) | 1.00 → 19.89% ok (p 0.87) |
| **A_DAILY** | CONDITIONAL | — | 1.10 → 20.74% over (p 0.32) | 1.10 → 20.74% over (p 0.64) | 1.10 → 20.74% ok (p 0.87) |
| **A_PERIOD** | ROBUST | 0.85 → 18.72% over (p 0.08) | 0.65 → 18.74% over (p 0.12) | 0.65 → 18.74% ok (p 0.34) | 0.65 → 18.74% ok (p 0.77) |
| **B_DAILY** | CONDITIONAL | — | 0.60 → 19.23% over (p 0.12) | 0.35 → 21.71% over (p 0.21) | 0.15 → 23.72% ok (p 0.24) |
| **B_MARGIN** | CONDITIONAL | — | — | 0.50 → 20.22% over (p 0.26) | 0.35 → 21.71% ok (p 0.35) |
| **B_PERIOD** | RETIRED | 0.85 → 18.72% over (p 0.08) | 0.35 → 21.71% over (p 0.06) | 0.15 → 23.72% over (p 0.10) | 0.00 → 25.90% over (p 0.17) |
| **MAX_SHARPE** | ROBUST | 0.95 → 19.48% over (p 0.09) | 0.95 → 19.48% over (p 0.14) | 0.95 → 19.48% ok (p 0.68) | 0.95 → 19.48% ok (p 0.87) |
| **MID_DAILY** | ROBUST | — | 0.95 → 19.48% over (p 0.14) | 0.95 → 19.48% ok (p 0.68) | 0.95 → 19.48% ok (p 0.87) |
| **MIN_IS_DD** | CONDITIONAL | 1.05 → 20.29% over (p 0.09) | 1.05 → 20.29% over (p 0.29) | 1.05 → 20.29% over (p 0.69) | 1.05 → 20.29% ok (p 0.88) |

## The swap test

A fitted rule may replace the default at the 25% budget only if it holds there, its bootstrap hold-probability is no worse than the default's, and it earns strictly more out of sample. All three, or nothing.

**NO SWAP EARNED** — no fitted rule met all three conditions at the loosest budget

This is the tension worth reading twice: at 25% the parent's own race says FITTING_HELPS — B_DAILY earns 15.87% out of sample against the default's 9.82%, 6.05 pp more — and the swap test still says no, because its hold-probability there is 0.242 against the default's 0.873. Fitting at this budget did not buy a worse number, it bought a number you can predict less: the point reading improved while the share of resamples that still fit the budget fell. A holder who cannot tell, in advance, which of the nine picks survives is holding the distribution, not the pick.

| rule | k | holds | p | p no worse | OOS CAGR | earns more | failed |
|---|---|---|---|---|---|---|---|
| A_DAILY | 1.10 | yes | 0.873 | yes | 8.79% | **no** | earns_more |
| A_PERIOD | 0.65 | yes | 0.768 | **no** | 12.88% | yes | p_hold_no_worse |
| B_DAILY | 0.15 | yes | 0.242 | **no** | 15.87% | yes | p_hold_no_worse |
| B_MARGIN | 0.35 | yes | 0.353 | **no** | 14.87% | yes | p_hold_no_worse |
| B_PERIOD | 0.00 | no | 0.167 | **no** | 16.44% | yes | holds, p_hold_no_worse |
| MAX_SHARPE | 0.95 | yes | 0.872 | **no** | 10.30% | yes | p_hold_no_worse |
| MID_DAILY | 0.95 | yes | 0.872 | **no** | 10.30% | yes | p_hold_no_worse |
| MIN_IS_DD | 1.05 | yes | 0.878 | yes | 9.31% | **no** | earns_more |

## Today

With the default at the latest bar (evidence cutoff 2026-11-20): hedge notional = k x beta = **90.13%** of the book, at beta = 0.9013.

the hedge leg is sized as k x beta of the book's value at the latest bar; margin, borrow availability and recall are not modelled here.

## The answer

**ONE_UNIT_IS_THE_ONLY_HONEST_DEFAULT** — one unit of beta held the 20% budget out of sample (19.89%) while 5 of 8 fitted pickers breached it
