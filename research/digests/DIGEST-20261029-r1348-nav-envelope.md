# E246 — the book has one history: publish the distribution, then price the ruler

r1348 · bm-c · 2026-10-29 · face `results/etf_book_bootstrap/ENVELOPE-2026-10-29.json`
series `results/etf_book_series/NAV-2026-10-29.json` · card E246 · chain leg + smoke leg

> **CORRECTION (same window, later in r1348).** The numbers below were produced by a seeding scheme that
> depended on `--procs`, so they are not reproducible on another host: the same face re-run at
> default worker count gave CAGR p5 3.66 / point pctile 49.8, and with `--procs 2`, 3.43 / 50.1.
> The seed now belongs to the resample index (E247) and the face was republished — read the live
> readings from `results/etf_book_bootstrap/ENVELOPE-2026-10-29.json` and
> `BLOCKS-2026-10-29.json`, not from this page. The block-length sensitivity is now measured in
> E248: the point percentile survives every block, the drawdown tail does not. This page is kept
> because it records what the dead r1348 window actually measured, not as the current answer.

## Why

Every ETF-book number in this repo — 9.70% CAGR here, 13.50% on the executable ticket,
−0.145pp for the buffer, +0.07pp for a phase — is a point estimate over **one** ordering of
1,651 trading days. r1325 showed a phase change alone moves the same book by an IQR of
0.53pp, yet the repository kept comparing arms that differ by less than that with no
statement about how much of any number is the book and how much is *this* history.

## What

`scripts/etf_book_nav_envelope.py` (selftest 11/11, `--check` recomputes every percentile
from the published rows):

1. `derive` — reuses `etf_book_production.prep_panel` + `backtest` (the production cell:
   N12 / R20 / 8% vol target / 10bp per side) and publishes the book's own daily NAV path
   as a face, so every later study can replay the book without loading the 1,503-symbol
   panel. 1,651 bars to 2026-10-29, CAGR 9.70%, Sharpe 1.000 — reproduces the card.
2. `run` — circular block bootstrap of that return path, block = 20 bars (one rebalance
   cycle), 2,000 resamples across a `ProcessPoolExecutor`, shardable (`--shard k/N`). The
   pool gate's law-1 check reads `multiproc` on this file, so the row can be ignited.

## Reading (2,000 resamples, block = 20)

| | p5 | p25 | p50 | p75 | p95 |
|---|---|---|---|---|---|
| CAGR %/yr | 3.79 | 7.09 | **9.60** | 12.35 | 16.23 |
| Sharpe | 0.42 | 0.74 | **0.98** | 1.22 | 1.56 |
| maxDD % | −20.86 | −15.70 | **−12.93** | −11.05 | −9.08 |

* The published point estimate **9.70% sits at the 51.0 pctile** of its own distribution —
  the headline is not a lucky path (its maxDD sits at the 64.8 pctile: the realised drawdown was
  worse than the median resample, i.e. the published +9.70%/−12.5% pair is not a cherry-pick).
* 0.4% of resamples lose money; 6.6% break a −20% drawdown — i.e. the book's advertised
  drawdown band (−12.5% on the card) is the *median* of the ruler, not a tail.
* The tail is wide in a way no arm-level verdict in this repo can resolve: p5 (3.79%) to
  p95 (16.23%) is a 12.4pp band, seven times the largest single-arm effect published today
  (the buffer's −0.145pp median, E237).

## Two things the operator should take away

1. **Arms priced inside ±1pp are inside the sampling noise of the book itself**, and the
   face now says how big that noise is instead of asserting it.
2. **The drawdown line is the honest risk number.** −20.86% at p5 is 8pp worse than the
   card's headline maxDD, and it costs nothing to know.

## Honest limits (published on the face, not buried)

* Block bootstrap keeps dependence *inside* a block and destroys it *between* blocks: it is
  a ruler for sampling noise, not a market simulator.
* Resampling returns keeps turnover/cost drag as an average, so a resample is not a re-run
  of the strategy on a new price path. It answers "how much does the ordering of the same
  days matter" — exactly what the phase tests kept asking.
* Block length is a free parameter nobody had priced: pool rows **E247/E248/E249** (block 5 / 60
  / 250) are registered in the pool to bound it. Until they land, 20 bars is a choice, and
  the face says so on its own criteria block.
* One panel (survivor pool), one window, one cost assumption — all inherited from the card.