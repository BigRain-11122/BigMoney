# DIGEST 2026-10-21 · E35: the broad-book screens, and the panel hole they exposed

Source faces (descriptive census, zero prereg, zero judgment, trial_count 0):

* `results/e35_broad_eq_2018/UNIV-4170ac-s20180101-xsh511-20261021.json` — E35-BROAD-EQ-2018
* `results/e35_broad_eq_x3/UNIV-4170ac-xsh511-x3-20261021.json` — E35-BROAD-EQ-X3
* `results/e34_cadence_rolling/CADENCE-ROLLING-3Y-X3.json` — E35-CADENCE-ROLLING-X3
* `results/e36_broad_eq_trunc_0930/UNIV-4170ac-s20180101-e20260930-xsh511-20261021.json` — E36-BROAD-EQ-TRUNC-0930
* `results/e36_broad_eq_trunc_2024/UNIV-4170ac-s20180101-e20241231-xsh511-20261021.json` — E36-PANEL-DECAY
* Runner: `scripts/e27_universe_expansion.py`, `scripts/e34_cadence_rolling.py` (both deterministic offline, in-repo panel)

Cutoff 2026-10-20. Accounting imported from E33/E27/E34 — no re-implementation.

## Q-A · Does the broad book survive a recent window? (2018-01-02 start, 8.46y, 2,130 bars)

| book | ann % | vol % | Sharpe | cost bp/yr | rebalances |
|---|---|---|---|---|---|
| frozen five (ladder) | 5.48 | 19.64 | 0.370 | 4.1 | 93 |
| all eligible equity ETFs (equal w, 1,231) | **8.04** | 17.40 | **0.532** | 9.1 | 93 |

Delta **+265.9bp/yr, monthly-rel t = 1.29**. The sign survives (the full sample was
+338.7bp at t = 1.97) but the recent window alone does **not** clear a t = 2 bar.
Honest reading: the broad book is still ahead on both return and vol since 2018, but
the edge is not statistically established inside that window — it is carried partly by
the 2012-2017 leg.

## Q-B · Is the gap a fee artefact? (cost x3, full sample)

| book | ann % | vol % | Sharpe | cost bp/yr |
|---|---|---|---|---|
| ladder x1 | 5.27 | 21.54 | 0.347 | 4.2 |
| ladder x3 | 5.19 | 21.54 | 0.343 | 12.6 |
| broad x1 | 8.24 | 18.77 | 0.516 | 8.3 |
| broad x3 | **8.06** | 18.76 | **0.507** | 25.0 |

Delta moves −338.7 → **+326.6bp/yr, t 1.97 → 1.92**. Tripling costs on both legs costs
the comparison 12bp/yr out of 339. Fees are irrelevant to this read; turnover is 0.64×/yr,
so no plausible fee assumption closes a 3-point annual-return gap.

## Q-C · Does the cadence coin-flip survive cost x3? (rolling 3y, monthly vs quarterly)

| era | mean bp/yr (x1) | mean bp/yr (x3) | positive n / n |
|---|---|---|---|
| 2021-2023 | −18.5 | −20.2 | 7 / 36 |
| 2024+ | +5.8 | **+3.7** | 17 / 34 |

Same verdict at x3: the sign flips era to era, the 2024+ read is +3.7bp/yr with 17 of 34
positive 3-year windows — a coin flip, not an edge. Cadence is a non-question; stop
spending units on it.

## Q-D · The panel hole (found while checking Q-A's live marks)

The 2018+ run reports `live_marks: 2026-10-20 eligible 15` against `2023-01-03 eligible 491`.
That is not a strategy property — it is **data staleness**:

| last bar date across `data/daily/*.csv` | files |
|---|---|
| 2026-10-20 (current) | 53 |
| 2026-09-22 | 1,671 |
| 2026-09-04 | 1 |
| total | 1,725 |

The 53 live panels are exactly the 48 core-ETF codes plus the five `sh`-prefixed codes
that `update_etf_daily.py` refreshes. The 1,231-code broad universe has **no refresh leg
at all** — its panels were bulk-pulled once on 2026-09-22 and have not moved since.
Consequence: every turnover-liquidity screen built on that panel silently loses coverage
as the calendar advances (the trailing-60d filter needs bars the panel no longer has), and
the last month-end book is 15 names instead of ~490.

## Q-E · Is the thin tail what drags Q-A down? (fixed ends on the 2018 start)

| window | eligible at end | ladder ann % | broad ann % | delta bp/yr | t |
|---|---|---|---|---|---|
| 2018+ to 2026-10-20 | 15 | 5.48 | 8.04 | +265.9 | 1.29 |
| 2018+ to 2026-09-30 | 15 | 6.41 | 8.65 | +227.8 | 1.14 |
| 2018+ to 2024-12-31 (clean coverage) | **763** | 4.43 | 6.86 | **+248.9** | **1.68** |

Reading: the decayed tail *dilutes* the measured delta rather than manufacturing it. On
fully covered data (763 names alive at the last month-end) the 2018-2024 broad book is
+248.9bp/yr at t = 1.68. So Q-A's weak recent t is not a data-tail illusion — the edge is
real in sign and size, but six to nine years of recent data is still not enough to clear
t = 2 on a single non-overlapping test.

This does not invalidate Q-A/Q-B/Q-C (the sample is 13.9y and the monthly books are
built where data exists), but it does mean **every further recent-window read on the ETF
universe is confounded by panel decay until the refresh leg exists**. Building
`scripts/update_etf_universe.py` (E29) is therefore load-bearing, not housekeeping.

## Verdict

* Broad book: survives cost x3 (fees irrelevant), survives as a sign in 2018+, but the
  recent-window t is 1.29 (1.14 truncated) — carry it as a *candidate*, not an edge.
* Cadence: closed as a non-question (coin flip at x1 and at x3).
* Panel coverage: 53/1,725 panels current; 1,671 frozen at 2026-09-22 — E29 refresh leg is
  the next unit, and until it exists no recent-window ETF read is trustworthy at the tail.