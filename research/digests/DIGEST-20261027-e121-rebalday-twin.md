# DIGEST 2026-10-27 — E121: the rebalance-calendar face on the repaired panel

Face: `results/e44_midmonth/REBALDAYSCREEN-20261027.json`
Code: `scripts/e39_panel_census.py` `run_rebaldayscreen` / `_rebalday_arm_cells` /
`_rebalday_cell_role` / `_rebalday_shift_verdict` / `_rebalday_older_raw` (selftest 403 -> 416);
`run_rebalday` gained the `raw=` seam; `scripts/e97_routing.py` TWIN_FUNCS + re-derived
routing face (selftest green)
Pool: `E121-REBALDAY-SCREENED-TWIN` done; `E124-TILT4` seeded
Method card: E159

## What was asked

E97 ranked `run_rebalday` third on the uncovered list (132 published numbers, in the
`rebalday` mode). This runner prices the CALENDAR itself — month-end-1 / month-end /
month-end+1 / mid-month — which is the one axis every other twin holds fixed. So the seed
predicted the interesting control: *if the calendar face moves on a repaired panel while
every calendar's own return holds, the repair changed WHEN the book traded rather than WHAT
it earned.* The twin therefore has to publish a SPLIT of the moved cells (calendar vs
returns vs spread) instead of a total.

## Readings (cutoff 2026-10-27)

**114 cells joined, 33 moved — and zero of them are calendar cells.**

| role | cells moved | max abs delta |
|---|---|---|
| calendar (rebalances, turnover) | **0** | — |
| returns (ann return, drawdown, win rate) | 17 | 10.0 bp |
| spread (ladder-vs-wide) | 16 | 45.0 bp |

- **The trade schedule is untouched.** All four calendars in both windows keep identical
  rebalance counts (82 at start-2020, 106 at start-2018) and identical `ladder5`
  annualised returns (-1.00 / -1.03 / -1.15 / -1.53 % at start-2020; 5.13 % and siblings
  at start-2018, bit-identical on both arms). A repair that moved the calendar would have
  changed these first.
- **Only the wide book moves.** Every returns cell that moved is a `wide_top9999` cell:
  ann return +0.29…+0.45 pp, max drawdown 0.32…0.42 pp less negative. The ladder side is
  bit-identical on all eight calendar rows.
- **Which is why the spread widens.** All 16 moved spread cells move the same direction:
  `vs_ladder_spread_bp` +29…+45 bp (worst: mid-month at start-2020, 115.0 → 160.0). The
  dispersion across calendars narrows (`wide_ann_range_bp` 79 → 69), so the calendar mix
  is *more* forgiving on the repaired panel, not less. `spread_all_positive` is true on
  both arms.
- **Verdict published by the face:** *the repair moves the returns while the trade calendar
  is untouched — the calendars disagree by the same schedule, what moved is the level.*

## Controls

- **Same-arm control: 0 of 114.** The join machinery is sound.
- **Cutoff control: 40 of 114 cells, max 7.0 bp** (`results/e41_rebal_day/SHIFT-20261020.json`
  raw arm vs today's raw arm, arm held fixed). The repair's 45 bp therefore dominates the
  four-session panel refresh by ~6x — the same direction as E119 (repair dominates) and the
  opposite of E118 (cutoff dominated). Every family carries its own controls.
- **Panel screen report:** mode `neutralise_int`, 67 events neutralised of 1,317 names,
  integer-like 67/67, 0 reverting / 0 undecided adjacency.

## Two defects caught in the round

1. **The cutoff control searched the wrong directory and returned `null`.** The runner's
   published raw face is written by the `rebalday` CLI to
   `results/e41_rebal_day/SHIFT-<cutoff>.json` — not into this leg's own directory and not
   under a `REBALDAY-` name. A lookup in the obvious place finds nothing, and a `null`
   control reads exactly like "no older face exists", i.e. like a clean twin. Fixed by
   factoring the lookup into `_rebalday_older_raw` and adding three selftest legs that
   point it at a temp dir: it must find a real `SHIFT-` face, it must refuse to join
   today's own cutoff against itself, and a missing leg directory must not silently lose
   the fallback. Without those legs this defect would have shipped as an honest-looking
   absence.
2. **A boolean was nearly harvested as a numeric cell.** `spread_all_positive` sits in the
   same `answers` block as the bp columns; `True - False` is a legal subtraction in Python,
   so it would have booked a "delta" with no units. `_rebalday_arm_cells` now skips booleans
   explicitly and the face publishes the flag per arm as a verdict; a selftest leg pins that
   it is absent from the harvest.

## What this does not say

Descriptive census only: no gate, no verdict on the strategy, no prereg, no trial count, no
ledger booking. The role split classifies moved cells; it does not decompose the change into
how much each role caused. And the screened arm repairs prints inside the panel it is handed
— an unchanged `universe_members` count is a property of the repair, not evidence the panel
is clean.