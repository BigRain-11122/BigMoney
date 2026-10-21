# DIGEST 2026-10-21 — E44 mid-month churn: the calendar gap is membership, not fees

Round r1132 (bm-b). Product faces: `results/e44_midmonth/MID-20261020.json` (window 2020-01-01)
and `MID-20261020-s20180101.json` (window 2018-01-01). Runner: `scripts/e39_panel_census.py midmonth`
(selftest 73/73). Pool unit `E44-MIDMONTH-WEAKNESS` closed with result_ref.

## Question

E43's robustness grid put the **mid-month** decision calendar at the bottom of every cost column
(newest-era size-neutral +3.8bp at x1, −3.3bp at x3, against +38.5bp for month-end). Two candidate
mechanisms were separated on one universe, one rank cache and one calendar:

- (a) the mid-month book simply turns over more, so fees eat the difference;
- (b) it turns over the same amount but swaps into worse names inside each held window.

## Answer

**Mechanism (a) is refuted. Turnover is identical.**

| | month-end | mid-15 |
|---|---|---|
| turnover / year | 0.591 | 0.594 |
| implied fee gap | — | **≈2 bp/yr** |
| full-window gap x1 | — | **−70 bp/yr** |
| newest-era gap x1 | — | **−87 bp/yr** |

A 2bp fee difference cannot produce an 87bp gap. The swap *count* is the same; the swap *quality*
differs. Churn sleeve (mean forward return of names entering minus names leaving, per swap):

| era | month-end churn alpha | mid-15 churn alpha | gap |
|---|---|---|---|
| 2017_2020 | +1830.0 bp | +1405.0 bp | −425.0 |
| 2021_2023 | +1866.5 bp | +2185.4 bp | **+318.9** |
| 2024_now | **+95.6 bp** | **−123.7 bp** | **−219.3** |

Negative-swap share in the newest era: 42.9% (month-end) vs 48.1% (mid-15).

## The finding that matters

The newest era is the only era where the mid-month book's *entrants lose to the names they replace*
(−123.7bp per swap). At month-end the same sleeve is modestly positive (+95.6bp). So the calendar
weakness is a **membership-quality effect concentrated in 2024-now**, not a fee effect and not a
general property of mid-month calendars.

The 2018-window run makes the locality sharper: at that start, 2017_2020 mid-month actually *wins*
(+50bp) and 2021_2023 is a wash (−8bp). Only 2024-now carries the −87bp. A single full-window number
(−70bp at the 2020 start, −15bp at the 2018 start) therefore mixes three eras with three different
signs of effect; the honest quote is the newest-era number with its window.

## What this does not say

- 2021_2023 has a *better* mid-month churn sleeve yet a worse P&L (−77bp/yr at the 2020 start): the
  churn sleeve is not a full attribution, so in that era something outside the swap sleeve (holding
  path / decision timing inside the month) drives the gap. Recorded, not explained.
- The churn sleeve is an equal-weight mean over swapped names, not a portfolio return.
- Mid-15 is a single fixed date, not a sweep: this prices a wrong-calendar cost, it does not search
  for a better calendar.
- Descriptive census only: no gate, no verdict, no prereg, no trial count.

## Follow-ups seeded

- `E57-MIDMONTH-CHASE-NAMES` (waiting, needs a `--detail` leg): name the swaps, and test whether
  mid-month's entrants are symbols month-end later drops (chase) or a disjoint slice.
- `E58-PARTS-CUT-CURVE` (waiting): one face sweeping parts 2..12 so the E46 band series can be quoted
  with its own cut error bar or closed.

## Pit recorded

Era bounds compared as plain strings silently drop every era's first month: a bare month (`2024-01`)
is a **prefix** of its own first day (`2024-01-01`), so `month >= lo` is false for exactly the first
month and `_era_of("2024-01-02")` returned `None`. Truncate both bounds to `YYYY-MM` before
comparing. The selftest leg caught it before any face was written (72/73 on first run).