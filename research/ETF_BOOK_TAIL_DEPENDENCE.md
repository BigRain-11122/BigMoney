# Does the book earn it on many days, or on a handful?

Generated 2026-11-01 08:21:03 · evidence cutoff 2026-10-30 · 1652 bars · payload `results/etf_book_tail_dependence.json`

## Verdict

**ROBUST_TO_TAILS** — the 10 best bars are only 6% of the up-move and the book keeps 57% of its cagr without its 10 best bars

## Baseline (the number every other face quotes)

| cagr | sharpe | maxdd | vol | years |
| --- | --- | --- | --- | --- |
| 9.12% | 0.955 | -13.26% | 10.05% | 6.83 |

Top 10 bars carry **6.3%** of all log growth.

## Drop-best arms vs random-drop placebo

| bars removed | cagr | sharpe | cagr delta | placebo pct | placebo p05 | placebo p50 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 8.54% | 0.908 | -0.58 pp | 0.0% | 9.36% | 9.51% |
| 5 | 6.86% | 0.760 | -2.26 pp | 0.0% | 9.13% | 9.48% |
| 10 | 5.20% | 0.603 | -3.92 pp | 0.0% | 8.94% | 9.45% |

Best month (2025-08) removed: cagr 8.10% (-1.02 pp).

## The book next door does not match bar for bar

`NAV-2026-10-29.json` publishes the same production book (1650 bars to 2026-10-29). Over 1650 overlapping bars the daily returns differ by up to **0.0431**, so these are not the same path: that face quotes **9.70%** cagr / 1.000 sharpe / -11.77% maxdd and this one quotes **9.12%** / 0.955 / -13.26% (**-0.58 pp**).

Both numbers are honest about their own path; the divergence is a second implementation of the same book, not a tail effect. Until it is resolved, quote neither as *the* production number without naming the face it came from.

Best month (2025-08) removed: cagr 8.10% (-1.02 pp).

## How to read this

- The drop-best arms are arithmetic on the book's own published bars, not a re-simulation.
- The placebo says what dropping *any* k bars usually costs, so the drop-best reading is
  compared against luck rather than against zero.
- A verdict of TAIL_DEPENDENT does not say the book is wrong; it says the headline CAGR is
  a statement about a few days, and no sizing rule can reproduce it ex ante.
