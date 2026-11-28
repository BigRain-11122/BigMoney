# Does the book earn it on many days, or on a handful?

Generated 2026-11-28 10:52:36 · evidence cutoff 2026-11-27 · 1672 bars · payload `results/etf_book_tail_dependence.json`

## Verdict

**ROBUST_TO_TAILS** — the 10 best bars are only 6% of the up-move and the book keeps 56% of its cagr without its 10 best bars

## Baseline (the number every other face quotes)

| cagr | sharpe | maxdd | vol | years |
| --- | --- | --- | --- | --- |
| 8.70% | 0.911 | -13.26% | 10.09% | 6.90 |

Top 10 bars carry **6.2%** of the gross up-move.

## Drop-best arms vs random-drop placebo

| bars removed | cagr | sharpe | cagr delta | placebo pct | placebo p05 | placebo p50 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 8.13% | 0.865 | -0.57 pp | 0.0% | 8.92% | 9.06% |
| 5 | 6.47% | 0.718 | -2.23 pp | 0.0% | 8.70% | 9.04% |
| 10 | 4.84% | 0.562 | -3.86 pp | 0.0% | 8.51% | 8.98% |

Best month (2025-08) removed: cagr 7.68% (-1.02 pp).

## The book next door does not match bar for bar

`NAV-2026-11-27.json` publishes the same production book (1671 bars to 2026-11-27). Over 1671 overlapping bars the daily returns differ by up to **0.0431**, so these are not the same path: that face quotes **8.94%** cagr / 0.925 sharpe / -11.77% maxdd and this one quotes **8.70%** / 0.911 / -13.26% (**-0.24 pp**).

Both numbers are honest about their own path; the divergence is a second implementation of the same book, not a tail effect. Until it is resolved, quote neither as *the* production number without naming the face it came from.

Best month (2025-08) removed: cagr 7.68% (-1.02 pp).

## How to read this

- The drop-best arms are arithmetic on the book's own published bars, not a re-simulation.
- The placebo says what dropping *any* k bars usually costs, so the drop-best reading is
  compared against luck rather than against zero.
- A verdict of TAIL_DEPENDENT does not say the book is wrong; it says the headline CAGR is
  a statement about a few days, and no sizing rule can reproduce it ex ante.
