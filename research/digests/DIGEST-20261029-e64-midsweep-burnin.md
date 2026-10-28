# E64 — the mid-sweep's "robust" era was a cash block (r1239 bm-b)

**Face:** `results/e44_midmonth/MIDSWEEP-20261028-burnin.json` (84 cells, 4 source faces)
**Code:** `scripts/e39_panel_census.py` mode `midsweepburnin` (selftest 717/717)
**Card:** knowledge/METHODOLOGY_ASSETS.md E212
**Status:** E64 pool card closed with result_ref; descriptive only, zero prereg, zero trial count

## What E59 published

Five off-cycle decision days (5/10/15/20/25) against month-end on one universe, one rank cache, one
cost level. At start 2020 the 2017_2020 column was **0.0bp on every off-cycle day**; at start 2013 the
same era read -26..+1bp. E59's own honest block flagged the 0.0 as suspicious but could not say why.

## What the burn-in leg found

An exact 0.0 on five different calendars is not agreement between calendars — it is the arithmetic of a
100% cash book. The engine buys only when `e27._rank` returns names, and at start 2020 that first
happens on **2021-01-29** (calendar index 262, twelve decision bars into the window). The entire
2017_2020 slice ends before that bar, so:

| reading | start 2020 | start 2013 |
|---|---|---|
| first invested bar | 2021-01-29 (idx 262) | 2014-01-30 (idx 258) |
| 2017_2020 pre-invested share | **100.0%** | 0.0% |
| 2017_2020 gaps (mid5..mid25) | 0,0,0,0,0 | +1,-2,-11,-7,-26 bp |
| classification | `degenerate_cash_slice` ×5 | `informative` ×5 |

Ten cells in the face carry `degenerate_cash_slice` — exactly the ten start-2020 off-cycle cells in
2017_2020 (x1 and x0.3 arms, five days each). 59 cells are informative. One exact zero survives with an
invested book (mid5 at start 2013 with the fee off) and is published as
`exact_zero_with_invested_bars` rather than being folded into the degenerate bucket.

## Why this matters

"A gap of zero" is the most quotable form of a negative result, and three different claims all print as
0.0: the arms genuinely agree, they cancel, or one arm never traded. The third one is the cheapest to
produce and the most convincing because it is exact. Publishing the pre-invested share beside the gap
turns that from a footnote into a number on the face.

## Method note

Nothing is re-simulated. The first invested decision comes from `e27._rank` — the same eligibility +
liquidity rule `e27.simulate` itself buys on — imported, not reimplemented, so the reported boundary is
the engine's. The classifier is a pure function of (gap, pre-invested share) with selftest legs pinning
all five branches.

## Not done this round

E60 (off-book liquidity terciles) and E61 (shared-subset book) remain `waiting`: both need new legs in
the same runner and E61 additionally needs per-session holdings out of the engine, which `e27.simulate`
does not expose (it returns only the last holdings). Supply floor is 0 ready / 2 waiting — recorded
honestly rather than papered over by seeding cards that cannot be ignited.