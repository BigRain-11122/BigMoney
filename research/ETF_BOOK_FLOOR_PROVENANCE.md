# What issued the floor of k=0.393073

> the floor is not a version of the rule: k*beta == 0.2000 on all 5 cells, so the floor is the target divided by the largest beta measured -- issued by `window_x_universe` (306 bars). Of the 6.72pp between the widest floor (k=0.460253) and the narrowest (k=0.393073), 3.91pp (58%) comes from shrinking the window from the full panel to 306 bars and only 1.96pp from grading the universe on that same short stretch (2.81pp if the universe is graded on the full panel); the two knobs interact by 0.85pp. Read as money on CNY 1,000,000 NAV: the window alone accounts for CNY 39,122 of the gap.

## The identity

| cell | beta | k | k x beta | err vs target |
|---|---|---|---|---|
| baseline_published | 0.434543 | 0.460253 | 0.200000000 | 0.00e+00 |
| window | 0.484650 | 0.412669 | 0.200000000 | 0.00e+00 |
| universe | 0.462754 | 0.432195 | 0.200000000 | 0.00e+00 |
| window_x_universe | 0.508811 | 0.393073 | 0.200000000 | 0.00e+00 |
| denominator | 0.367361 | 0.544424 | 0.200000000 | 2.78e-17 |

If the right column is all zeros this is not a fit: **k = beta_target / beta**.

## The 2x2 and what each knob costs

| corner | cell | k | bars |
|---|---|---|---|
| common|all | window | 0.412669 | 306 |
| common|graded | window_x_universe | 0.393073 | 306 |
| full|all | baseline_published | 0.460253 | 1658 |
| full|graded | universe | 0.432195 | 1658 |

| effect | k | pp | CNY on 1,000,000 |
|---|---|---|---|
| window (full -> common) | 0.039122 | 3.91 | 39,122 |
| universe (all -> graded, at the 306-bar window) | 0.019595 | 1.96 | 19,595 |
| universe (all -> graded, at the full panel) | - | 2.81 | - |
| interaction | - | 0.85 | - |
| total gap | 0.06718 | 6.72 | 67,180 |

- share of the gap explained by the window alone: **58%**
- share explained by grading the universe: **29%**

## What this does to the sheet

- The floor is a **measuring tape**, not a rule: it is the beta target divided by whichever beta the table measured as largest.
- The issuing cell is `window_x_universe` (306 bars) -- the shortest evidence in the table.
- So "the floor" is a statement about the last ~306 bars of volatility, re-issued as that window slides; it is not a bound the rule was designed against.

## Not measured

- the short window is one calendar stretch (2025-07..2026-10), not a sample of stretches: a rolling 306-bar beta path would say whether the window knob is a level shift or a phase effect, and this face does not compute it
- whether a longer window is the RIGHT window: this face only prices the knob, it does not elect one (r1446's caliber prereg)
- the floor's own drift as the window slides: today's 306 bars end 2026-10-14, so the floor will be re-issued on a different stretch next month

_evidence cutoff 2026-11-06_
