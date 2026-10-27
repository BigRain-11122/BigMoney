# E116 — the EARLY ladder on the screened arm: the levels move (one flips sign), the gaps do not

Face: `results/e44_midmonth/EARLYDELAYSCREEN-20261026.json` (arms beside it as
`EARLYDLY-arm-raw-20261026.json` / `EARLYDLY-arm-neutralise_int-20261026.json`),
evidence_cutoff 2026-10-26. Leg: `scripts/e39_panel_census.py earlydelayscreen`
(selftest 353 → **362/362**). Pool row `E116-EARLYDELAY-SCREENED-TWIN`.

## Why this leg exists

E97 row 5 after the burn-in / cut-curve / livespan / chase twins. The early side
of the month-end boundary is the one place where a repaired print can also
reorder *eligibility*: the early decision re-ranks on a date when fewer names have
published, so an arm that changes a print can change which name is picked, not
just what it earned. E66's reading — both sides of the boundary pay, so the month
boundary is a publication deadline and not a price path — therefore had to be
priced on the repaired panel before it could be quoted.

Cost: a `raw=` seam on `run_earlydelay` (it already passed everything through to
`run_midsweep`, which has carried `raw=` since E78), one harvest, one burn. Both
arms re-derive at start 2020-01-01 with the fixed early ladder 1/3/5/10 sessions,
cost x1; screen = `neutralise_int`, names in = names out.

## The measurement

93 joined cells: five calendars (`me` plus the four early ones) each contributing
their own annual return, era returns, turnover and cost, plus the eight ladder
gaps and the E66 asymmetry answers. Same-arm control, and a cutoff control on the
previous published raw face (`EARLYDELAY-20261020`).

| axis | moves | magnitude |
|---|---|---|
| repair (`neutralise_int`) | **55 of 93** (20 book, 35 gap-address) | book ≤0.61 pp/yr, gaps ≤15 bp |
| refresh (`EARLYDELAY-20261020` vs today raw) | 27 of 93 | ≤6 |
| identity (raw vs raw) | 0 of 93 | 0.0 |

### 1. The repair lifts every calendar by the same amount — a level shift, not a reordering

All five books move **up** in both live eras, by almost exactly the same amount:

| calendar | 2024_now raw → scr | 2021_2023 raw → scr | full window raw → scr |
|---|---|---|---|
| `me` | 11.26 → 11.84 (**+0.58**) | −8.60 → −8.31 (+0.29) | 0.62 → 0.97 (+0.35) |
| `me_lag-1` | 11.08 → 11.65 (+0.57) | −8.28 → −7.99 (+0.29) | 0.70 → 1.06 (+0.36) |
| `me_lag-3` | 10.76 → 11.33 (+0.57) | −9.54 → −9.11 (+0.43) | −0.03 → 0.40 (+0.43) |
| `me_lag-5` | 10.62 → 11.21 (+0.59) | −9.90 → −9.46 (+0.44) | −0.25 → 0.18 (+0.43) |
| `me_lag-10` | 10.52 → 11.13 (+0.61) | −9.41 → −8.97 (+0.44) | −0.05 → 0.39 (+0.44) |

Two things follow, and the second is the sharp one:

* the spread between the five calendars is untouched (they all move together), so
  no ordering claim in E65/E66 depends on the arm;
* **three of the five full-window annualised levels change sign across zero**
  (−0.05 → +0.39, −0.03 → +0.40, −0.25 → +0.18). A published "this book earns
  roughly nothing over the window" is an arm statement, not a panel fact. This is
  the strongest version yet of the E99/E102 family: there the level moved; here it
  crosses zero.

### 2. The early-side verdict is arm-free to within 3 bp

Newest era (`2024_now`), gap versus the month-end book:

| early ladder | raw | screened | Δ | sign held |
|---|---|---|---|---|
| 1 session early | −18 bp | −19 bp | −1 | yes |
| 3 sessions early | −50 bp | −51 bp | −1 | yes |
| 5 sessions early | −64 bp | −63 bp | +1 | yes |
| 10 sessions early | −74 bp | −71 bp | +3 | yes |

Monotone in distance, negative at every step, on both arms. E66's conclusion — the
boundary pays on the early side too, and pays more the further you move — survives
the repair with a 3 bp worst case. Full-window gaps move a little more but keep
sign for three of four ladders (8 → 9, −65 → −57, −87 → −79, −67 → −58).

### 3. The 15 bp outlier is where the repaired prints actually live

Every gap move of 14–15 bp sits in **2021_2023**, and every one of them makes the
loss *smaller*: `me_lag-5` / `me_lag-10` read −130 / −81 raw and −115 / −66
screened; `me_lag-3` −94 → −80. That is the same era E93/E103 flagged as the one
carrying the integer-gap prints, and the same direction as E114/E115 (the raw arm
makes a losing arm look worse). Outside 2021_2023 the largest gap move is 3 bp.

### 4. The cell count is not a count of findings

The ladder gaps are published at two addresses (`gaps[x1][me_mK]` and
`answers.early_rows`) and a third time inside the answers summary, so the 55
moved cells are **21 distinct gap readings and 17 distinct book readings**. Stated
because a "55 of 93 moved" headline over a face with copied addresses is exactly
the inflation E116's own sibling tickets have been catching.

## Two controls, plus coverage

| control | isolates | result |
|---|---|---|
| identity (raw vs raw) | join machinery | 0 of 93, max Δ 0.0 |
| cutoff (`EARLYDELAY-20261020` raw vs today raw) | panel refresh | 27 of 93, max Δ 6 |
| coverage | is the twin a twin? | 93 compared, 0 one-sided, 13 null-on-both (all `pre2017`, structurally empty at start 2020-01-01) |

The refresh axis moving 27 cells is why the repair number had to be read against
it: 55 is not "55 because the panel is inflated", it is roughly twice the
refresh's footprint and concentrated in one era.

## The defect this burn caught in its own machinery

The first burn published `counts_survive_the_repair: true` on a face where 55 of
93 cells had moved. `survives` had been defined as *"the join is complete and the
control is silent"* (E112–E115 inherit the same expression) — it never tested the
numbers. Two facts, one boolean, and the boolean won the wording. Fixed by
extracting `_twin_survives(summary, control)`, which now requires
`cells_moved == 0`, applied to the chase twin as well; three selftest legs pin it
(complete-join-with-55-moved must read False, silent-control must read True,
moved-control must read False). The published E115 face reads `true` with
`cells_moved: 0`, so no earlier face needs a re-burn.

## What this does not say

* Not a strategy verdict: descriptive census, no gate, no prereg, no trial count,
  no ledger booking.
* The early decision re-ranks on an earlier date; a stable gap therefore means the
  repair did not reorder the picked set *enough to matter*, not that the set is
  identical.
* The late column of the asymmetry block is read from the E65 face on disk in both
  arms identically, so it cannot contribute a delta; it is context only.
* `pre2017` cells are null on both arms at start 2020-01-01 — structural, not
  one-sided.
* The summary `max_abs_delta` mixes units (bp for gaps, pp/yr for returns,
  turns/yr for turnover). It is a screen, not a quantity; each moved cell is
  quoted in its own column units.