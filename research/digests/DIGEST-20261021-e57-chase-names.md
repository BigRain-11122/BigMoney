# DIGEST 2026-10-21 — E57: the mid-month swaps, named (r1134 bm-b)

Face: `results/e44_midmonth/CHASE-20261020.json` (evidence_cutoff 2026-10-20)
Runner: `scripts/e39_panel_census.py chase --start 2020-01-01` (selftest 85/85)
Pool row: E57-MIDMONTH-CHASE-NAMES (closed)

## What r1132 left open

The mid-month calendar turns over the same amount as month-end (0.591 vs 0.594
turns/yr, fee gap ~2bp) yet its swaps earned −123.7bp each against +95.6bp at
month-end in the newest era. Counts cannot say why. The candidate reading was
*chase*: the mid-month book buys names the month-end book is about to drop.

## What the names say

Every entrant of both calendars is bucketed against the **other** calendar's
next book (the only counterfactual available without re-pricing a portfolio):

| bucket | meaning |
|---|---|
| `other_drops_next` | the other book sheds the name at its very next rebalance (chase) |
| `other_still_holds` | the other book still holds it (early, not wrong) |
| `disjoint` | in neither the other book's next holdings nor its next drop set |

Newest era (2024_now, 33 transitions each, ~660 entrant slots per calendar):

| bucket | mid share | mid fwd | me share | me fwd |
|---|---|---|---|---|
| `other_drops_next` | 0.15% (1 name) | −4.18% | 0.15% (1 name) | −2.04% |
| `other_still_holds` | 50.45% | +0.96% | 49.31% | +0.89% |
| `disjoint` | 49.39% | +0.67% | 50.53% | **+2.30%** |

Three readings, in order of strength:

1. **The chase hypothesis is dead.** One name out of 660 entrants per calendar
   lands in the other book's next drop set. The two calendars are not trading
   against each other's exits.
2. **Shared names are not where the gap is.** When both books pick the same
   name (`other_still_holds`, half of all entrants), mid earns +0.96% and
   month-end +0.89% per window — flat, with mid marginally ahead.
3. **The gap is entirely in the off-book slice.** Excluding the shared half,
   mid's off-book picks earn +0.67% while month-end's off-book picks earn
   +2.30% — a 163bp per-swap spread in the newest era, and one whose negative
   share is 51.5% for mid against 39.9% for month-end.

The effect is era-local again, exactly as E44 found: in 2021_2023 the same
disjoint bucket reads −0.59% for mid against −0.87% for month-end, i.e. mid is
the *better* off-book picker in that era. The sign flips with the era, not with
the calendar.

Also visible: only ~2% of entrant slots are repeats of an earlier entrant
(2.3% mid, 2.1% me, 645/641 unique names over 33 transitions). The churn is
one-shot names, not the same set rotating back in.

## Honest limits

- Bucket membership is decided on the other calendar's book, not on a re-priced
  counterfactual: it says what the other book did with the name, not what the
  money would have done in it.
- `fwd_pct` is the raw decision-to-decision name return, before weighting, cost
  or the cash leg.
- One mid-month date (day 15) against one month-end date; the calendars are
  fixed, not swept. 2020+ window only, so `pre2017` and `2017_2020` have no rows.
- Descriptive census: no gate, no verdict, no prereg, no trial count.