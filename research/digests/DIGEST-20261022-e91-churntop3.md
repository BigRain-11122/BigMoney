# E91 — every concentrated churn cell now names its transitions, and one of them is a split the screen cannot see

- date: 2026-10-22T23:4x (r1157 bm-b)
- evidence cutoff: 2026-10-22
- face: `results/e44_midmonth/CHURNTOP3-20261022-s2013.json`
- runner: `python scripts/e39_panel_census.py topnames --start 2013-01-01` (2 universes x 2 books, same `full_churn` burn as E82/E85/E86/E87)
- code: `scripts/e39_panel_census.py` (`_top_transitions`, `run_topnames`, selftest 223 -> 231)

## What the leg publishes

E87 said the two oldest churn eras have no centre of mass (top-3 carry 108.5% / 149.1%
of the signed total). A share is not auditable, so each of the 32 cells (2 books x
4 universes x 4 eras) now prints its three largest |churn_alpha_bp| transitions with:

- the decision window (`date -> next`),
- the swapped tickers (entrants in, exits out, truncated to 10 per side),
- both side means (`entrant_fwd_pct` / `exit_fwd_pct`),
- which side carried the sign (`carried_by`),
- the transition's share of the cell's signed total.

21 of 32 cells carry more than half of their signed total in three transitions;
every cell named. Newest-era cells ride along as the control.

## The load-bearing reading: one split, one transition, three separate findings

| cell | top-1 window | bp | carried by | in / out |
|---|---|---|---|---|
| mid15 2021_2023 unscreened | 2021-05-17 -> 2021-06-15 | +9424.4 | entrants | out: sh510150 (+2 more) |
| mid15 2021_2023 neutralise_int | 2021-05-17 -> 2021-06-15 | +9424.4 | entrants | out: sh510150 |
| mid15 2024_now unscreened | 2024-01-15 -> 2024-02-19 | -3365.2 | exits | out: sz159925 (+2) |
| me pre2017 unscreened | 2015-12-31 -> 2016-01-29 | +2402.2 | entrants | in: sz159937 |
| me 2017_2020 unscreened | 2020-07-31 -> 2020-08-31 | +8160.8 | entrants | in: sh510350/sh512670/sh512720 |

`sh510150` is the name E74 flagged as an unadjusted 12:1 split (10.414 -> 0.87).
The panel prints that step on 2021-05-31, and the 2021-05-17 -> 2021-06-15 exit
window straddles it, so the exit side mean is dragged toward -91.6% and the churn
alpha reads +9424bp. This is the SAME transition E83 identified as the sole owner
of the +318.8bp 2021_2023 churn gap (removing it leaves 18.9% of the gap).

**The screen never repairs it, and that is by design, not a bug in the screen:**
sh510150 has no bar on 2021-05-28 (a session that exists in the panel calendar,
verified against `data/daily/510300.csv`), so the print is classified *gapped*
rather than *adjacent*. E76's rule is "gapped prints are never repaired because a
resumption after suspension can be real", and `neutralise_int` / `neutralise`
both leave the cell at exactly +9424.4bp. The concentration E83/E85/E86 measured
is therefore structural to the panel: a split behind a one-session data gap
defeats the adjacency gate.

Cross-check that the join is right rather than merely plausible: E82 reported the
2024_now amplification as mid15 2024-01-15 with sz159925 among the moved names —
the same window and the same name appear here as the cell's top-1 (unscreened
-3365.2bp; under neutralise -9979.4bp, because repairing other names moves the
entrant side).

## The other cells

- `me pre2017` top-1 is a single entrant, sz159937, at +2402.2bp on a 9-transition
  cell (top-3 108.5%): an era whose whole mean is one name's forward window.
- `me 2017_2020` and `mid15 2017_2020` top-1 are the 2020-07 windows (+8160.8 /
  +8263.7bp) where four ETF entrants replaced one exit — a membership event of the
  panel's growth spurt, not a market signal.
- `mid15 2024_now` is the E82/E83 cell: top-3 151.6% unscreened, 118.6% under
  neutralise — still the least robust published cell in the chain.
- `drop` mode flips the 2024_now book's top-3 share to -80.7% (its signed total is
  small after removing 129 names), i.e. its "concentration" is not comparable
  cell-for-cell with the neutralise arms.

Descriptive census only: zero prereg, zero judgement, zero ledger booking,
trial_count 0.

## Pits

1. A share of a signed total can exceed 100% and can be negative when the cell's
   total nears zero — print the percentage only beside the bp values that produced
   it, never as a standalone ranking metric.
2. "Adjacent" is a panel-calendar property, not a wall-clock one (E76 already
   recorded this): the same test that correctly flags a Monday print will silently
   skip a Tuesday print when the Monday bar is missing. Gapped splits are a real
   unpriced channel, not a rounding of the adjacent channel.