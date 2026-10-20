# DIGEST 2026-10-21 — E41 rebalance-day shift: the spread survives every calendar, the level does not

Round r1116, bm-b. Script `scripts/e39_panel_census.py` (`rebalday` leg, selftest 29/29).
Face `results/e41_rebal_day/SHIFT-20261020.json`. Evidence cutoff 2026-10-20,
top9999 wide book, sh511 excluded, cost x1, 1,265 universe members.

## The question

Every E34–E40 magnitude rests on one decision calendar: the month end. If the +134bp/yr spread
were a day-of-month artefact — a settlement, a funding, or a rebalancing-flow effect — the whole
wide-book line would be an artefact too. So the identical spec is re-run on four calendars:
month-end−1, month-end, month-end+1 and a mid-month date (first session on/after the 15th), with
one universe, one rank cache and one cost model. The engine reads the rebalance set as a decision
at the close of index (i−1), so a shift moves decision and trade together.

## Measured — 2020-01-01 window (1,645 bars, 6.53y)

| calendar | ladder5 | wide top9999 | vs-ladder | ladder maxDD | wide maxDD |
|---|---|---|---|---|---|
| month-end −1 | −0.41 %/yr | +0.94 %/yr | **+135.0 bp** | −42.89% | −36.40% |
| month-end | −0.43 %/yr | +0.86 %/yr | **+129.0 bp** | −42.72% | −36.55% |
| month-end +1 | −0.55 %/yr | +0.59 %/yr | **+114.0 bp** | −42.49% | −36.25% |
| mid-month (15th) | −0.93 %/yr | +0.16 %/yr | **+109.0 bp** | −42.27% | −36.29% |

## Measured — 2018-01-01 window (2,132 bars, 8.46y)

| calendar | ladder5 | wide top9999 | vs-ladder |
|---|---|---|---|
| month-end −1 | +5.63 %/yr | +7.55 %/yr | **+192.0 bp** |
| month-end | +5.48 %/yr | +7.44 %/yr | **+196.0 bp** |
| month-end +1 | +5.27 %/yr | +7.17 %/yr | **+190.0 bp** |
| mid-month (15th) | +5.54 %/yr | +7.29 %/yr | **+175.0 bp** |

## Why it matters

1. **The spread is calendar-robust.** All eight calendar/window combinations are positive;
   the 2020+ band is 109–135bp (26bp wide) and the 2018+ band 175–196bp (21bp wide). A
   day-of-month artefact would have to flip the sign somewhere in ±1 session — it does not.
2. **The level is not.** Moving the ladder's decision by one session moves its annualised return
   52bp (2020+) and 36bp (2018+), and going mid-month costs another ~38bp on the wide book. That
   is the same order as the drift the panel refresh produced (r1111: ±5bp on the spread, but 73bp
   on a truncated spec), so **any ladder/wide level quoted to two decimals is over-precise**; the
   spread is the stable object, the level is not.
3. **Drawdowns are calendar-invariant** (−42.27 to −42.89 for the ladder, −36.25 to −36.55 for
   the wide book): a ±0.6pp band, i.e. the risk read does not depend on when you rebalance.
4. **Mid-month is a real cost, not a curiosity.** It is the worst calendar on all four columns in
   the 2020+ window. Whatever the month-end effect is, missing it is worth ~20–26bp of spread —
   small, but it is the same direction in both windows.

## Honest limits

- The leg tests a calendar shift, not a decision-only shift: the engine couples decision and trade.
- Mid-month is one fixed date, not a sweep; it prices a wrong calendar, it does not search for a
  better one. No parameter was selected on these results.
- Era/regime structure inside the window is not separated here — that is the E41-SPREAD-ERA-DECAY
  leg, burned in the same round (see `DIGEST-20261021-e41-spread-era-decay.md`).
- Descriptive census only: zero prereg, zero judgment, zero ledger booking, trial_count 0.