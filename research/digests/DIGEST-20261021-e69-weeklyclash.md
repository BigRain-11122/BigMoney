# E69 — month-end is not a re-timed weekly book

> r1141 · bm-b · leg `weeklyclash` in `scripts/e39_panel_census.py` (selftest 105/105)
> faces: `results/e44_midmonth/WEEKLYCLASH-20261021.json` (+ `-s20130101`)
> descriptive census only — no gate, no verdict, no prereg, no trial count, zero ledger booking

## Question

E68 put the off-cycle cost plateau at "about the first week" off the month boundary — which is
exactly where a weekly rebalance sits. So: **is the month-end calendar a calendar of its own, or
only a re-timed weekly book?** And separately: does adopting month-end *add* turnover on top of a
weekly book, or replace it?

Two readings, one universe (1,265 names), one rank cache, one cost level (x1):

- `week` — the full ISO weekly grid (first trading session of each ISO week), the densest rule in
  the panel;
- `week_near_me` — **the same weekly grid cut to one decision per month**, taken at the weekly
  session nearest the month-end decision. Same names, same grid, same cost, 1/4.3 the decisions.

`me` (month-end) is the baseline; every number below is a gap against it.

## Answer

| calendar | decisions (2020 start) | turnover/yr | fee bp/yr | full-window gap | newest era (2024-now) |
|---|---|---|---|---|---|
| `me` (baseline) | 82 | 0.590 | 7.7 | 0 | 0 |
| `week` | 349 | 0.789 (**1.34x**) | 10.3 | **−55bp** | **−63bp** |
| `week_near_me` | 82 | 0.595 (**1.008x**) | 7.8 | **−11bp** | **−11bp** |

Start 2013: `week` −8bp full window / **−63bp newest era** (turnover 1.385x), `week_near_me`
−15bp / **−11bp newest era** (turnover 1.005x). The newest-era column is bit-identical between the
two windows — the same start-invariance E59/E63/E65/E67/E68 saw, and the only column quotable alone.

Three things follow:

1. **The boundary date carries the information.** Holding frequency fixed (82 decisions, turnover
   0.595 = 1.008x month-end), moving the same weekly grid onto the boundary recovers 44 of the 55
   full-window bp and 52 of the 63 newest-era bp. Month-end is not a sub-sample of the weekly rule.
2. **Month-end does not add turnover on top.** The monthly-cut weekly book trades 0.595 turns/yr
   against month-end's 0.590 — a 0.8% difference. The weekly *grid* trades 1.34x, but that is the
   extra decision count, not the calendar choice. Adopting month-end replaces a monthly weekly
   decision, it does not stack on it.
3. **The residual −11bp is the grid offset, not noise.** `week_near_me` decisions sit 1–3 sessions
   inside the boundary by construction; E67/E68 priced that offset at −19/−24bp early and
   −43/−52bp late at 1/2 sessions. Exact session coincidence between the two grids is 11/349,
   92/349 within two sessions — so the residual is bounded by the same shoulder E66–E68 measured.

The fee channel is closed a second time: the fee difference is 2.5bp/yr (10.3 vs 7.8) against a
55bp gap. E63's x0/x3 result on the sweep says the same thing from the other direction.

## Honest limits

- `week_near_me` is a *snap*, not a coincidence: only 11 of 349 weekly sessions land on the exact
  month-end session, so the residual −11bp is the price of being on the weekly grid at all.
- The weekly grid rebalances ~4.3x more often than month-end, so `week`'s gap mixes calendar with
  trading frequency. Only `week_near_me` holds frequency fixed; that is the row that answers the
  question and the other is context.
- x1 only. The fee parity is an inference (2.5bp/yr), not an x0 arm — E70 exists to burn it.
- Full-window numbers are start-bound (2020: −55bp, 2013: −8bp for `week`); era gaps carry their
  start date as in E59/E63/E65/E66/E67/E68.
- Descriptive census only: no gate, no verdict, no prereg, no trial count.

## Handoff

E70-WEEKLYCLASH-COSTFACE (seeded `ready`, cpu-only): `weeklyclash --costs 0,3` on both starts —
if the −55bp / −11bp gaps are unchanged at x0 both are price-path effects and the fee channel is
closed outright rather than inferred. After that the calendar family (E44/E59/E63/E65/E66/E67/E68/
E69) has priced both axes (date and frequency) and can be frozen for a judged unit.