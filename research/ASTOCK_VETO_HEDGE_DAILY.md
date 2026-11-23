# The drawdown budget, marked every day

Generated 2026-11-24T04:20:25+08:00 · evidence cutoff 2026-11-20 · machine bm-c

## What was wrong with the last number

r2023 sized the hedge against a budget the account sits through, but read the drawdown off the book's own 20-bar period curve. A period that ends flat can still have spent six weeks underwater, and a real account is not marked every 20 bars. This face marks the same book on every trading day between rebalances (77 periods, 1,540 marked days; 0 name-periods had no entry or exit print and were left out of the marks exactly as the parent's own ``nanmean(fwd)`` leaves them out; the daily path lands on 1 + net in every period, largest gap 5.1e-15)

## The answer

**DAILY_MARKS_BREACH_THE_BUDGET** — the size chosen on the in-sample daily budget let the out-of-sample daily drawdown reach 20.74% against a 20% budget.

The two rulers: **DAILY_MARK_IS_STRICTER** — the daily ruler reads a median 1.335x the period ruler (worst 1.511x).

| budget | daily rule A (k) | A out-of-sample dd | period rule A (k) | daily rule B (k) | B out-of-sample dd | IS daily floor | verdict |
|---|---|---|---|---|---|---|---|
| 10.00% | n/a | n/a | 0.85 | n/a | n/a | 12.07% | BUDGET_UNREACHABLE_ON_DAILY_MARKS |
| 15.00% | 1.10 | 20.74% | 0.65 | 0.60 | 19.23% | 12.07% | DAILY_MARKS_BREACH_THE_BUDGET |
| 20.00% | 1.10 | 20.74% | 0.65 | 0.35 | 21.71% | 12.07% | DAILY_MARKS_BREACH_THE_BUDGET |
| 25.00% | 1.10 | 20.74% | 0.65 | 0.15 | 23.72% | 12.07% | DAILY_MARKS_KEEP_THE_BUDGET |

## Which rule survives the finer ruler

Rule A buys the most return the budget allows, and on daily marks it buys a bigger hedge than the period ruler did — which is the honest size for the in-sample window and the wrong size out of it. Rule B (the smallest size the budget requires) is the risk-first answer; it holds out-of-sample in 1 of 4 budgets on daily marks.

What the budget could actually have bought out-of-sample, across every size on the grid: **the best a size could have done out-of-sample is 18.07% at k=0.75, chosen with hindsight; the worst is 51.05% at k=2.00**. Neither rule picks that size in advance, which is the point — the number a reader can rely on is the floor, not the pick.

## The same hedge, read on both rulers

| k | period drawdown (full) | daily drawdown (full) | daily / period | daily drawdown OOS |
|---|---|---|---|---|
| 0.00 | 25.92% | 34.17% | 1.318 | 25.90% |
| 0.25 | 19.95% | 28.04% | 1.406 | 22.71% |
| 0.50 | 15.36% | 23.21% | 1.511 | 20.22% |
| 0.65 | 14.64% | 20.66% | 1.411 | 18.74% |
| 0.75 | 14.49% | 19.12% | 1.319 | 18.07% |
| 1.00 | 14.17% | 19.89% | 1.403 | 19.89% |
| 1.50 | 24.05% | 30.26% | 1.258 | 30.26% |
| 2.00 | 47.26% | 51.05% | 1.080 | 51.05% |

## What this face does not do

- It does not re-price the hedge: the period ruler here reproduces r2023's numbers because it is the same book through the same code path; if it did not, the face would be wrong, not different.
- A name with no print on an interior day is carried at its last print rather than dropped from that day's mean: dropping it makes the book's value jump whenever a handful of names miss a print, which reads as a drawdown that never happened. Names missing either the entry or the exit print (0 name-periods) are left out, exactly as the parent's ``nanmean(fwd)`` leaves them out.
- The daily marks still do not model a margin call. This face says how deep the marks went, not at what depth a broker would have closed the position.
