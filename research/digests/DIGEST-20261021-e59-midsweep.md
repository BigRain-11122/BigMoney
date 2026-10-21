# E59 — the off-cycle penalty belongs to the month boundary, not to day 15

Round r1135 · evidence cutoff 2026-10-20 · descriptive census, no gate, no prereg, no trial count

## Question

E44 priced one mid-month date (day 15) against month-end and found -70bp full window /
-87bp in the newest era, with turnover identical (0.591 vs 0.594 turns/yr) so fees could
not explain it. E57 then showed both calendars buy the *same kind* of name (0.15% of
entrants are names the other book sheds next). The open question was whether the penalty
is a property of the 15th, or a property of deciding away from the month boundary at all.

## Method

One universe, one rank cache, one cost level, five decision dates swept on the identical
spec: mid-day 5 / 10 / 15 / 20 / 25 against month-end (`me`). Each decision date is also
tagged with its **calendar offset** — the mean number of sessions between that decision
and the next month-end decision — so a gap can be read against distance from the boundary
instead of against one chosen day. Two windows are burned: the E44 window (start
2020-01-01) and full history (start 2013-01-01).

New runner leg: `python scripts/e39_panel_census.py midsweep [--start YYYY-MM-DD]`
(selftest 90/90, +5 hermetic legs). Faces:
`results/e44_midmonth/MIDSWEEP-20261020.json` and `MIDSWEEP-20261020-s20130101.json`.

## Results — start 2020-01-01 (x1)

| date | offset (sessions to month-end) | turnover/yr | full-window gap | newest era (2024-now) gap |
|---|---|---|---|---|
| me  | 0    | 0.594 | 0 | 0 |
| mid5  | 16.85 | 0.589 | -26.0bp | -71.0bp |
| mid10 | 13.65 | 0.581 | -84.0bp | -85.0bp |
| mid15 | 10.18 | 0.594 | -70.0bp | -87.0bp |
| mid20 | 6.77  | 0.588 | -80.0bp | -55.0bp |
| mid25 | 3.41  | 0.586 | -61.0bp | -64.0bp |

Every off-cycle date loses. The newest-era spread across the five dates is only **32bp**
(-55 to -87) while the full-window spread is 58bp (-26 to -84), and there is **no monotone
relation to the offset** (mid5, the farthest from the boundary at 16.85 sessions, is the
mildest at -71bp; mid20, only 6.77 sessions out, is the deepest at -80/-55).

## Results — start 2013-01-01 (x1)

| date | full-window gap | pre2017 | 2017_2020 | 2021_2023 | 2024_now |
|---|---|---|---|---|---|
| mid5  | -14.0bp | -36.0 | +1.0 | +36.0 | -71.0 |
| mid10 | -44.0bp | -125.0 | -2.0 | +26.0 | -85.0 |
| mid15 | -53.0bp | -113.0 | -11.0 | -8.0 | -87.0 |
| mid20 | -10.0bp | +19.0 | -7.0 | -11.0 | -55.0 |
| mid25 | -25.0bp | -6.0 | -26.0 | -13.0 | -64.0 |

Full-window gaps shrink to -10..-53bp and the middle eras change sign (2021_2023 is
*favourable* to mid10 and mid5 at this start), which is the same era-locality E44 and E57
found. The 2024-now column is **bit-identical between the two windows** (-71/-85/-87/-55/
-64), i.e. that era's path is start-invariant: by 2024 both simulations hold the same book
and make the same decisions, so the newest-era read is the one number that can be quoted
without naming the window.

## Reading

1. **The penalty is a boundary effect, not a day-15 effect.** Five independent off-cycle
   dates, all negative in the newest era, spread 32bp. Day 15 was never special; it was
   simply the date E41/E43/E44 happened to test.
2. **Cost is excluded a second time.** Turnover across the five dates spans 0.565-0.594
   turns/yr — the same band month-end sits in — so no fee story survives; the follow-up
   unit (E63) burns the sweep at x0 to close the cost channel directly.
3. **Era gaps are window-bound; the newest era is not.** The 2021_2023 sign flips between
   windows, so any quoted era gap must carry its start date. The 2024-now column is
   invariant and is the only gap that can be read alone.
4. **Degenerate-slice trap (new).** At start 2020 the 2017_2020 era prints an **exact
   0.0bp** gap for all five dates. That is not calendar robustness: the whole slice sits
   inside the eligibility burn-in cash block (first invested ≈ 2021-02), so every calendar
   holds the same 100% cash book. An exact-zero era gap is the signature of a cash-only
   slice and must never be read as evidence of calendar neutrality. Unit E64 exists to
   print the cash share beside the gap.

## Honest limits

- One cost level by default (x1); the x0/x3 face is the seeded E63 unit, not measured here.
- Five fixed dates, not a fitted optimum: no date is searched for and none is a
  recommendation.
- Gap spread is a range over five points, not a test.
- Both windows share one universe and one rank cache; only the decision sessions move.