# ETF composite factor book — which sleeve actually carries the edge (r1244, bm-c)

Follow-up to `research/ETF_COMPOSITE_DECOMP.md` (r1243). That window decomposed the
published book by asset class and reported that roughly half the 9.04%/yr headline sat in
the defensive (bond) sleeve, and that the equity-only book loses to its own equal-weight
control out of sample. The natural next question is the one that decides whether the
thing is tradeable: **does any sleeve subset keep a control-beating book, or was the whole
result one bond carry trade?**

Product: `results/etf_composite_decomp_variants.json` (code
`scripts/etf_composite_decomp_variants.py`, same score / cost / cadence as the published
module: 6-factor cross-sectional rank, top-5 equal weight, 20-session cadence, 8bp per
side on turnover, close-to-close from the decision close, panel cutoff **2026-10-23**).

## Answer: the edge is not bonds — it is equity + gold. Bars, not bonds.

Each row is that subset's own book versus an equal-weight control built on **the same
columns**, so the excess is not a universe-size artefact.

| subset (universe) | full CAGR | full Sharpe | full maxDD | IS 2020-23 | **OOS 2024+ CAGR** | OOS Sharpe | OOS maxDD | OOS excess vs own EW |
|---|---|---|---|---|---|---|---|---|
| all classes (1,653) | 9.04% | 0.898 | -12.8% | 4.92% | 15.30% | 1.466 | -10.2% | +5.65pp |
| **bond removed** (1,547) | **13.47%** | 0.950 | -14.5% | 8.76% | **20.81%** | 1.300 | -13.5% | **+11.77pp** |
| commodity removed (1,633) | 8.60% | 0.893 | -12.8% | 7.51% | 10.27% | 1.102 | -10.2% | +0.78pp |
| crossborder removed (1,413) | 8.01% | 0.838 | -15.8% | 2.57% | 16.27% | **1.658** | -10.2% | +6.83pp |
| equity + gold only (1,309) | 8.52% | 0.660 | -15.8% | 3.58% | 16.02% | 1.074 | -14.3% | +7.41pp |
| equity only (1,291, r1243) | 4.24% | 0.375 | -26.7% | 2.18% | 7.11% | 0.552 | -14.8% | -1.21pp |

Controls in the full window: all-class EW 2.44%/yr (maxDD -40.0%), equity-only EW 1.90%
(maxDD -44.3%).

## Reading (three findings, in order of how much they change the picture)

1. **Bonds were a drag, not the alpha.** Deleting bonds from the universe lifts the book
   from 9.04% to 13.47%/yr and OOS from 15.30% to 20.81%. The r1243 arithmetic
   contribution of the bond leg (+8.57pp of gross return) was real but not additive: a
   bond slot consumes one of five top-5 places during equity drawdowns, and the book is
   then paid carry instead of the rebound. Standalone contribution ≠ marginal value.
2. **Gold is the load-bearing diversifier.** Removing commodity (gold/silver) collapses
   OOS excess from +11.77pp to +0.78pp — the smallest effect in the table. Equity + gold
   alone still earns 16.02% OOS (+7.41pp) while carrying only two asset classes, i.e. the
   mechanism is *a switch between equity ETFs and gold*, not a broad cross-asset rotation.
3. **Bonds buy volatility, not return.** OOS vol 16.23% without bonds vs 10.53% with them;
   OOS Sharpe is 1.30 without vs 1.466 with. If the objective is risk-adjusted rather
   than absolute, "crossborder removed" (equity+bond+commodity) is the best cell at OOS
   Sharpe 1.658 / maxDD -10.2% / CAGR 16.27%. Choose the objective before choosing a book.

## What this does **not** say

- Exploratory, not preregistered. No verdict, no ledger booking, no promotion.
- Survivorship: the on-disk panel holds ETFs that still exist.
- Subsets are **static**: the book cannot rotate *into* a removed sleeve, so "bond
  removed" is a different strategy, not the published book minus one leg.
- Close-to-close from the decision close; no open-fill model, so slippage is not in the
  numbers (only turnover cost). The r1243 follow-up (next-open fill pass on the loaded
  openp panel) is still open.
- 2024+ is 2.8 years of one regime (equity up, gold up). A gold rally flatters any book
  that is allowed to hold gold; the IS window is the only stress sample here.

## Next

- Next-open fill pass on the bond-removed and equity+gold books (the two candidates that
  survive every window), so the headline is not a close-to-close artefact.
- Yearly return table per variant, to see whether the OOS excess is one year or six.