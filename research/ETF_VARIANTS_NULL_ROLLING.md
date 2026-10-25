# The bond-removed book: permutation null and rolling-origin pass (r1248, bm-c)

Answers the two items r1247 left open on `research/ETF_VARIANTS_OPEN_YEARLY.md`:

1. the "bond_removed beats its own equal weight in 6/7 years" headline had **no null** -- the
   only permutation null in the tree (`etf_composite_pf.null_test`) was written on the close
   basis and only for the all-class book, and r1245 showed the basis is not a rounding detail;
2. every number came from one fixed origin (2020-01-01), so the excess could be a start-date
   artefact.

Product: `results/etf_variants_null_rolling.json`, code
`scripts/etf_variants_null_rolling.py` (`--selftest` = offline 4/4). Panel cutoff **2026-10-23**,
subset `bond_removed` = 1,547 of 1,653 panel columns, top-5 equal weight, 20-session cadence,
8bp/side, next-open fill (decision at close t, fill at open t+1; overnight gap to the OLD book,
weight change charged at the fill open, new book earns open->close).

The fill engine is **not** re-implemented blindly: `fast_next_open` is pinned in `--selftest` to
`etf_composite_pf.run_next_open` to 1e-12 (levels, turnover and the open-gap counter), and again
on the real panel at runtime (max relative deviation 0.0e+00). The engine gained one deliberate
hook this round: `run_next_open(..., score=None)` -- a caller can hand in its own score face and
still ride the same leg chain, which is what makes a 300-iteration null affordable.

## Baseline (reproduces r1247 exactly)

| window | book | own equal weight | excess |
|---|---|---|---|
| full 2020-01..2026-10 (1,648 bars) | 14.30%/yr, Sharpe 0.99, maxDD -16.1% | 2.26%/yr, Sharpe 0.22, maxDD -42.2% | **+12.04pp** |
| OOS 2024+ (678 bars) | 22.06%/yr, Sharpe 1.36, maxDD -12.4% | 9.04%/yr, Sharpe 0.54, maxDD -20.6% | **+13.02pp** |

Turnover 1.405 per rebalance; 13 book-relative open gaps.

## Finding 1 -- the ranking beats the shuffle null, but only comfortably on the full window

300 shuffles, seed 7. Each iteration permutes every factor's cross-section date by date (killing
the factor->return link while keeping the per-date rank distribution), rebuilds the composite,
re-picks the top-5 and **re-runs the fill engine** -- so the null carries the same costs, the same
grid and the same fill model as the product. Statistic = the excess the product actually claims.

| statistic | real | null mean | null p95 | null max | p |
|---|---|---|---|---|---|
| full excess (pp) | **+12.04** | -1.67 | 4.23 | 8.62 | **0.0033** |
| OOS 2024+ excess (pp) | **+13.02** | -2.74 | 12.42 | 21.60 | **0.0465** |

The full-window excess sits above every one of the 300 shuffles. The OOS excess does **not**:
the 2024+ null is wide (p95 12.42pp, max 21.60pp) because 2.8 years of a 20-session cadence is
about 34 decisions -- that is simply not enough draws to separate +13pp from luck at a
comfortable level. Reading both rows together is the point: the longer window is the more
informative one, and the popular "OOS is what counts" instinct is backwards when the OOS window
carries a third of the decisions.

## Finding 2 -- the headline is one decision-grid phase, not a measured central tendency

The rebalance grid is `dates[::20]` measured from the run's own first bar, so shifting the origin
by one day re-times **every** fill for the whole run. Walking the origin across 20 consecutive
trading days:

| anchor | excess range (pp) | median | spread | phases positive | book CAGR range |
|---|---|---|---|---|---|
| 2020-01-01 | +1.95 .. **+12.04** | +7.11 | 10.09pp | **20/20** | 4.72% .. **14.30%** |
| 2024-01-01 | -6.48 .. **+10.73** | **+1.11** | **17.21pp** | **11/20** | 3.58% .. 22.48% |

Two different things are true and they must be published together:

* from 2020 the sign is robust -- **all twenty** phases beat their own equal weight, so the
  composite ranking does carry something real over six years;
* the **magnitude is a phase draw**: the published +12.04pp is the *best* of twenty phases and
  the median is +7.11pp; from 2024 the OOS headline (+13.02pp) is likewise near the top of a
  distribution whose median is **+1.11pp** and where 9 of 20 phases lose to equal weight.

So the honest statement is not "bond_removed earns +13pp out of sample". It is: *the ranking
beats its own equal weight in every phase tested over 2020-2026, by a median of +7.1pp/yr, while
the recent window is phase-dominated and its central estimate is about +1pp -- i.e. the edge has
decayed or gone quiet since 2024, and nothing in this book can yet distinguish those two.*

## Finding 3 -- origin also moves the book's own level path by factor of five

Restarting the same book at each January: 14.30% / 7.80% / 7.84% / 15.86% / 7.03% / 6.23% CAGR
for origins 2020..2025, with excess +12.04 / +9.93 / +8.84 / +12.57 / **-1.88** / **-1.02** pp
(4/6 origins beat). A high-turnover book (1.4 of a possible 2.0 per rebalance, i.e. nearly full
rotation) measured from a single origin is a single path, not an expectation -- the two most
recent origins are the negative ones, consistent with Finding 2 rather than contradicting it.

## What this changes

* r1247's headline should be quoted as **+7.1pp median across 20 grid phases over 2020-2026**,
  with the phase range (+1.95..+12.04pp) attached, never as a point estimate.
* The next-session live paper book (`results/etf_composite_live/`) is still the right instrument:
  it is a phase-fixed forward record, and the thing to watch is whether its realised excess
  lands near the phase median or near the published maximum.
* Any promotion candidate must fix the decision-grid phase **before** the run and report the
  phase sweep alongside -- a 20-session cadence with no phase declaration is not a testable claim.

## Caveats (unchanged, plus one)

Survivorship: the on-disk panel holds ETFs that still exist. 20M CNY liquidity screen is not a
fill model. Fixed weights inside a holding period. The null permutes factor ranks, so it tests
ranking skill, not the sleeve choice. Exploratory: no verdict, no ledger booking, no prereg.
**New:** the phase sweep shifts the origin, so each cell also has a slightly different window
(<=19 bars); the spread is far larger than that length difference.