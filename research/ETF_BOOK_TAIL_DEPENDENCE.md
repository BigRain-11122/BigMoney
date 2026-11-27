# Does the book earn it on many days, or on a handful?

Generated 2026-11-27 09:38:55 · evidence cutoff 2026-11-26 · 1671 bars · payload `results/etf_book_tail_dependence.json`

## Verdict

**ROBUST_TO_TAILS** — the 10 best bars are only 6% of the up-move and the book keeps 54% of its cagr without its 10 best bars

## Baseline (the number every other face quotes)

| cagr | sharpe | maxdd | vol | years |
| --- | --- | --- | --- | --- |
| 8.47% | 0.890 | -13.26% | 10.07% | 6.90 |

Top 10 bars carry **6.3%** of the gross up-move.

## Drop-best arms vs random-drop placebo

| bars removed | cagr | sharpe | cagr delta | placebo pct | placebo p05 | placebo p50 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 7.90% | 0.843 | -0.57 pp | 0.0% | 8.67% | 8.81% |
| 5 | 6.24% | 0.696 | -2.23 pp | 0.0% | 8.45% | 8.79% |
| 10 | 4.61% | 0.539 | -3.86 pp | 0.0% | 8.24% | 8.76% |

Best month (2025-08) removed: cagr 7.44% (-1.03 pp).

## The book next door does not match bar for bar

`NAV-2026-11-26.json` publishes the same production book (1670 bars to 2026-11-26). Over 1670 overlapping bars the daily returns differ by up to **0.0431**, so these are not the same path: that face quotes **8.92%** cagr / 0.922 sharpe / -11.77% maxdd and this one quotes **8.47%** / 0.890 / -13.26% (**-0.45 pp**).

Both numbers are honest about their own path; the divergence is a second implementation of the same book, not a tail effect. Until it is resolved, quote neither as *the* production number without naming the face it came from.

Best month (2025-08) removed: cagr 7.44% (-1.03 pp).

## How to read this

- The drop-best arms are arithmetic on the book's own published bars, not a re-simulation.
- The placebo says what dropping *any* k bars usually costs, so the drop-best reading is
  compared against luck rather than against zero.
- A verdict of TAIL_DEPENDENT does not say the book is wrong; it says the headline CAGR is
  a statement about a few days, and no sizing rule can reproduce it ex ante.
