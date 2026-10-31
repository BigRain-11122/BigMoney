# E300 window-local margin census -- a margin belongs to the window that owns it (r1320 bm-b)

**Face:** `results/state_tilt/BANDMARGINWINDOW-2026-10-29.json` (+ `bandmarginwindow_latest.json`)
**Producer:** `scripts/e300_window_local_margin_census.py` (run / verify 0 problems / selftest 27/27)
**Wired:** chain leg `window_local_margin_census` (verify, rc=0) + smoke leg E300
**Upstream:** E285 (twelve demand rows + their cells), E258 (per-window multiplier at each row's own
base draws), E287 (the borrowed caps E295 had to reuse), E295 (the published margins this reproduces),
BANDFLOOR (the only sub-1.0 instrument the family publishes), E256 (the one window with a ladder)

## The question E295 left open

E295 could grade 2 of the 12 published demand rows because only `era_2025_now` owns a published draw
ladder, and the nine others were published as `not_graded` with the reason "no published draw ladder
for this window". Two numbers came out of that round and neither is a property of the band: 5.98 pct
(the margin read inside the ladder's window) and E287's 3.80 pct headline (the same demand priced
against a cap written at `early_three|60`).

"Unreachable" was never the right word for the nine. They are **un-laddered**, not un-referenced:
E258 rebuilt the shuffled band inside every measured cell and published that window's own draw
multiplier at the row's own base draw count. A ladder is a per-rung grid; a multiplier is one
reference. Only one window has the first; all four have the second.

## What happens when the denominator moves home

Every demand row was priced twice with the same arithmetic (`widen: flip/cap - 1`,
`narrow: (cap - flip)/cap`), once against the borrowed cap and once against its own window's
multiplier at its own base draws:

| row | cell | class | flip | own-window | borrowed cap |
| --- | --- | --- | --- | --- | --- |
| cross\|200\|1 | all_five | above_ceiling | 2.70458 | **105.41 pct** | 20.43 pct |
| star_lag1_residual\|200\|12 | all_five | above_ceiling | 3.25438 | **147.17 pct** | 44.91 pct |
| self\|200\|0 | all_five | above_ceiling | 2.33105 | **77.04 pct** | 3.80 pct |
| cross\|60\|7 | era_2023_2024 | above_ceiling | 2.45871 | **66.90 pct** | 9.48 pct |
| self\|60\|6 | era_2023_2024 | above_ceiling | 2.66760 | **81.08 pct** | 18.79 pct |
| star_lag1_residual\|60\|13 | era_2023_2024 | reachable_wide | 2.13838 | **45.15 pct** (`reached` under the borrowed cap) | -4.78 pct |
| cross\|60\|9 | era_2025_now | reachable_wide | 2.19650 | **33.60 pct** (`reached` under the borrowed cap) | -2.19 pct |
| star_lag1_residual\|60\|14 | era_2025_now | above_ceiling | 2.38009 | **44.76 pct** | 5.98 pct |
| cross\|60\|11 | early_three | in_gap | 1.80298 | **-1.92 pct** (reached) | -19.72 pct |
| star_lag1_residual\|60\|15 | early_three | in_gap | 1.88431 | **2.51 pct** | -16.09 pct |
| self\|60\|8 | era_2025_now | below_floor | 0.88939 | **no face** | 3.54 pct |
| self\|60\|10 | early_three | below_floor | 0.63039 | **no face** | 31.63 pct |

Three measurements fall out:

1. **10 of 12 rows are gradable on their own window** -- the nine `not_graded` rows were a statement
   about ladders, not about references.
2. **3 reach verdicts flip.** `cross|60|9`, `star_lag1_residual|60|13` and `self|200|0` looked
   reachable only under a cap written at another window; priced at home nothing reaches. So the
   borrowed cap made demands look satisfiable by supply they cannot buy.
3. **The borrowed denominator understates the margin on every widening row, by up to 147 pct.**
   `self|200|0` -- the row behind E287's 3.80 pct headline -- is 77.04 pct short of what its own
   window buys, i.e. a factor of 20 away from the headline reading.

`cross|60|11` is the one row that reaches on its own window (-1.92 pct) while E285 published it as
`in_gap`: the "gap" was between two borrowed numbers, not between the demand and its own supply.

## The narrowing side is a different failure

Both below-floor rows stay `not_graded`, and not for want of a ladder: the family publishes **no
window-local narrowing instrument at all**. Every BANDFLOOR `narrowing_readings` entry except one is
a widening multiplier (>1.0, so it cannot reach a sub-floor demand on the narrow polarity), and the
single sub-1.0 value (0.922022) is a synthetic counterfactual on one frozen seed (20261031) -- it
demonstrates that the floor *can* be broken, not what this window buys. Each ungraded row therefore
carries `needs_face`: a per-window narrowing ladder of BANDDRAW's shape. That is a named piece of
work, which is a better deliverable than a borrowed number.

## Witness and verdict

The cross-window column reproduces E295's two published margins exactly (5.982761 and 3.539468,
abs diff 0.0), which is what makes the own-window column comparable arithmetic rather than a rival
one. Verdict: `every_widening_demand_is_graded_against_its_own_window_and_no_narrowing_one_is`.

Evidence: `scripts/e300_window_local_margin_census.py` (selftest 27/27, `verify` 0 problems),
`results/state_tilt/BANDMARGINWINDOW-2026-10-29.json`, `Tools/s6_chain_bmb.py` leg
`window_local_margin_census`, smoke leg E300.