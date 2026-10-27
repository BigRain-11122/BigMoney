# DIGEST 2026-10-27 — E120: the month-boundary bracket on the repaired panel

Face: `results/e44_midmonth/NEIGHBORHOODSCREEN-20261027.json`
Code: `scripts/e39_panel_census.py` `run_neighborhoodscreen` / `_neighborhood_arm_cells` /
`_neighborhood_cell_role` / `_neighborhood_shift_verdict` (selftest 393 -> 403);
`scripts/e97_routing.py` TWIN_FUNCS + re-derived routing face (selftest 15/15)
Pool: `E120-NEIGHBORHOOD-SCREENED-TWIN` done; `E122-WARMSPREAD`, `E123-PAIR` seeded
Method card: E158

## What was asked

E97 ranked `run_neighborhood` second on the uncovered list (139 published numbers, one
mode). Its published reading is a three-point bracket — what the month-end decision would
have earned a session either side of the calendar — and it is a SHAPE claim ("ramp" vs
"spike"), so the seed asked for the inside/outside split of the moved cells rather than a
total: a repair can move the centre while the shoulders hold (bending the shape) or move
all three together (shifting the level), and one number cannot tell those apart.

## Two design facts that made the twin non-trivial

1. **The published shoulders are frozen.** `run_neighborhood` burns only the k arms it was
   asked for and then brackets them against the E65/E66 faces **on disk**. No repair can
   move a bound read off a static file, so a same-spec twin would have published a
   guaranteed zero shoulder count — a measurement that always agrees. The twin therefore
   burns the shoulders itself (`neighbors=(1,2,3)`), so all three rungs are re-derived on
   both arms. **Its bracket is not comparable cell-by-cell with the published E67 face.**
2. **The seam is one level down.** `run_neighborhood` delegates to `run_midsweep`, which
   already carried `raw=`; the twin's seam is the one added here.

## Readings (cutoff 2026-10-27)

163 cells joined, **90 move** — 28 centre / 36 shoulder / 26 book / 0 other, max 15.0 bp.
Same-arm control: **0 moved** (the join machinery did not move the numbers).
Cutoff control: `NEIGHBORHOOD-20261021` raw arm vs today's raw arm → **3 cells, max 6.0 bp**,
so the repair dominates the panel-refresh axis here by roughly 30× in cell count (the
reverse of E118, where the refresh was an order of magnitude larger than the repair).

Verdict: **centre and shoulders move together — the repair shifts the level, it does not
bend the shape.** All four brackets keep the same label on both arms:

| bracket | raw | screened | shape |
|---|---|---|---|
| early, full window | 9 / −17 / −65 | 8 / −11 / −59 | ramp → ramp |
| early, newest era | −18 / −24 / −52 | −18 / −25 / −52 | ramp → ramp |
| late, full window | −26 / −16 / −17 | −27 / −17 / −17 | ramp → ramp |
| late, newest era | −42 / −52 / −74 | −41 / −50 / −70 | ramp → ramp |

The sharpest single contrast: the early full-window bracket gains **6 bp at every rung**
(a pure level shift, proportional in k), while its newest-era counterpart moves **0 / −1 / 0**
(nothing). So on this panel the repair touches the boundary's level in the oldest sample and
leaves the newest era alone — the opposite of what a "the repair changes the book" story
would predict, and consistent with E108's finding that the repair is a split-print factor,
not a selection change. Book columns move ≤ 0.61.

## Defect found in-window (the reason the routing face was wrong)

`run_entrydelayscreen` (E119, r1190) was **never declared** in `TWIN_FUNCS`, so the routing
face still called `run_entrydelay` uncovered while its twin sat on disk. `L15` ("every
`run_*screen*` twin in the census source is declared") was **red at the open of this round**
and is exactly the leg built for this. Both new twins are now declared; the face re-derives
`covered_twin 14 → 16, uncovered 10 → 8 (runners 7 → 5)`.

This is the third recurrence of the registry-as-range pit (E115 → E118 → E119/E120). The
durable form is the selftest leg, not the habit: the table is only a census of what was
remembered to be declared.

## Honest limits

- Descriptive census only: no gate, no verdict on the strategy, no prereg, no trials.
- Shape labels come from a ±2 bp tolerance on three points; they describe one centre and
  its two neighbours, not a fitted curve.
- The published routine emits a bracket for **every** burned magnitude, so its k=1 and k=3
  brackets reach k=0 and k=4 — four cells that read null on both arms by construction. Only
  the centre bracket is complete.
- The screened arm repairs prints inside the panel it is handed; an unchanged
  `universe_members` count is a property of the repair, not evidence the panel is clean.