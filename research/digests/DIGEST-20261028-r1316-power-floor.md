# The horizon a reader can wait for (r1316, bm-c, 2026-10-28)

## What was published before

`results/etf_book_forward/LEDGER.json` carried one horizon for the book-vs-basket
spread: `bars_needed_for_edge`, the bars at which a t=2 test of an edge E would be
significant.

    N = (T * BARS_PER_YEAR * sd / E)^2

Measured on the live face (excess daily sd 0.5415%, 8.46%/yr, 1,649 bars):

| edge | bars needed | in years |
|---|---|---|
| 3pp/yr | 7,758 | 31.8 |
| 5pp/yr | 2,793 | 11.4 |
| 10pp/yr | 699 | 2.9 |

The two edges this book actually published are 2.03pp/yr (pre-2020 single arm) and
5.85pp/yr (in-window single arm). For the smaller one the table has no row at all,
because it would be "N = infinity" in practice. A holder reading that table learns
only that the answer is "never".

## What this round adds

`power_table()` in `scripts/etf_book_forward.py` answers the reverse question, the
one a holder actually asks about a horizon they will keep:

    smallest edge resolvable at 80% power inside H bars
        E = z_power * sd_annual / sqrt(H / BARS_PER_YEAR)      z_power = 2.802
    years until a candidate edge E reaches 80% power
        Y = (z_power * sd_annual / E)^2

Published on the live ledger (`benchmark.significance.power`, printed as a second
line beside SIGNIFICANCE):

| horizon | smallest resolvable edge (80% power, 5% two-sided) |
|---|---|
| 6m | 33.5pp/yr |
| 1y | 23.7pp/yr |
| 2y | 16.8pp/yr |
| 3y | 13.7pp/yr |

| candidate edge (read from this repo's studies) | years for 80% power |
|---|---|
| pre-2020 measured alpha 2.03pp/yr | 136.3 y |
| in-window measured alpha 5.85pp/yr | 16.4 y |

## The verdict this publishes

The forward ledger cannot adjudicate the alpha it was built to track. With an
excess dispersion of 8.46%/yr -- almost the book's own vol, because the four-ETF
basket is highly correlated with it -- a 2pp edge needs 136 years of daily data
and a 6pp edge needs 16. So:

* the forward face is a **health check** (does the tracked book drift from its
  card, do fills/lag/repairs break the record, is the benchmark arm alive), not a
  verdict source;
* any statement about whether the book beats buy-and-hold must come from the
  out-of-sample spanning study (r1310/r1312), which uses 1,217+ daily observations
  over a fixed window rather than waiting for new ones;
* the spread printed on the page (+0.75pp on 3 bars) will keep looking either way
  for years, which is why it must always be printed beside the horizon table.

## Candidate edges are read, not typed

Both candidate numbers come from the studies' own files via
`POWER_CANDIDATES`: `results/etf_book_spanning_pre2020.json`
(`arms.single.full.alpha_annual`) and `results/etf_book_spanning.json`
(`arms.book.full.alpha_annual`). The stored field is a FRACTION (0.0203); the table
converts to pp/yr and labels the unit (`units` block) -- the r1292 class where a
fraction read as a percent is silently 100x. A study that is not on disk is omitted
with `{"omitted": "unreadable:FileNotFoundError"}`, never filled in; selftest leg.

## Defects caught while verifying this window

1. The r1315 window (dead before commit) left `Tools/machine_health_face.read_face`
   returning a 3-tuple while its own smoke leg unpacked 2 -- the leg reported
   `'tuple' object has no attribute 'items'` as a FAIL. Fixed by unpacking all three;
   the lesson is the standing one: a dead window's "smoke green" in its digest is
   not evidence, the tree is.
2. `fleet/machine-health.json` had gone thin again (bm-c missing `cpu`) from the
   hourly deployed writer; `rebuild` restored 3/3 entries, `check` OK fields=8/8,
   and the panel (stale by 251 min, took over per the O-2100 stale rule) now carries
   `health_face=ok, health_unknown=false`.

Evidence: `scripts/etf_book_forward.py --selftest` (43 legs), live run lines
(SIGNIFICANCE + POWER), smoke 113/113, methodology card E162.