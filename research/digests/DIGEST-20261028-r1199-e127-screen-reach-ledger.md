# E127 — the cross-twin screen-reach ledger

Date: 2026-10-28 | round r1199 | machine bm-b | dept: research + engineering
Face: `results/e79/SCREENREACH-2026-10-27.json` | Tool: `scripts/e97_routing.py screenreach`
(selftest 29/29) | Pool card: `E127-SCREEN-REACH-LEDGER` (done)

## What this answers

E125 published one fact that all its siblings rely on and none of them repeat: the 67 names the
print screen neutralises contain none of the five ladder names, so every ladder row reading
"0 cells moved" is a **control arm**, not a measurement of the repair. E127 turns that fact into
a ledger over every published screened face, and adds the second question the family has been
answering informally since E122: **how big is the repair next to the data refresh, on that
face's own numbers, with both counts printed.**

Three columns per face, all read from the file itself:

1. `names_in` / `names_neutralised` / the ladder intersection from that face's own screen block;
2. `repair.cells_moved` (from `pair.summary`, else `answers.non_zero_delta_cells`, else the count
   of non-zero delta rows) beside `refresh.cells_moved` (from `cutoff_control.summary`), both with
   their `cells_compared` denominators, a ratio and a banded label;
3. a flag where the face carries no cutoff control at all.

## The table, in numbers

| | count |
|---|---|
| screened files carrying ledger content | 32 |
| declared twin faces (a `TWIN_FUNCS` glob claims it) | 14 |
| earlier sweeps (no pair block, no cutoff control) | 18 |
| rows with **no** cutoff control | **18** (every sweep row; no twin row) |
| rows where the ladder rows are controls | **29 of 29 rows that have a census** |
| rows that publish that ladder fact | **1** (`CASHLegSCREEN`) |
| rows with no screen census at all | 3 (`NEUTRAL` ×2, `ROBUST`) |
| rows with no repair count anywhere | 4 (`SCREENGAP` ×2, `SCREENGAPERA` 20261023, `SCREENGAPERA` 20261026) |
| rows whose repair/refresh compare different cell sets | 1 (`NEIGHBORHOODSCREEN`) |

Repair vs refresh on **matched denominators**: `repair_dominates` 5, `refresh_dominates` 5,
`tied` 3. On all 14 twins the naive count reads 6 / 5 / 3, and the sixth "repair dominates" is
the denominator artefact below.

The extremes are informative rather than decorative:

- `CUTCURVESCREEN` 126 moved of 330 vs refresh 68 of 330 (1.85×) — the biggest repair in the
  family, and it is the leg whose subject *is* the burn-in curve.
- `CHASESCREEN` 5 of 95 vs 16 of 95 (0.31×) — the smallest repair in the family, on the leg whose
  book re-picks weekly, i.e. the repair barely reaches the decisions that chase makes.
- `PANELSPLITSCREEN` 40 of 73 vs 9 of 73 (4.44×) and `EARLYDELAYSCREEN` 55 of 93 vs 27 of 93
  (2.04×): the two faces where quoting the raw number would be most wrong.
- `WARMSPREADSCREEN` 17 of 68 vs 17 of 68 and `PAIRSCREEN` 30 of 75 vs 28 of 75: tied, which is
  exactly the shape that forbids quoting either number alone.

## Two pits this leg hit

**P1 — a ratio is an ordering only when both counts sit on the same cells.** `NEIGHBORHOODSCREEN`
publishes 90 moved of 163 repair cells beside a cutoff control that only shares 9 cells (the face
says so itself: `one_sided_is_structural`). 90/3 = 30× is therefore not "a 30× repair", it is two
different experiments. The ledger now publishes both denominators, flags `denominators_differ`,
and keeps those rows out of the matched-denominator tally. First draft published the ratio without
the denominators and would have headlined a 30× that does not exist.

**P2 — "no census" is not "control".** `NEUTRAL-2026102x-screened.json` and
`ROBUST-20261023-screened.json` are declared twin faces that publish no per-name screen census at
all, so the ladder question cannot be answered on them. The first draft treated a missing census
as "zero neutralised names" and would have printed `ladder_row_is_a_control = true` for two faces
that never said which names they touched. The verdict is now `null` with a `no_screen_census`
flag, and the honest block says unknown ≠ true.

Sibling observation: the sweep generation has **no cutoff control at all**. Every repair number
published from those 18 faces (COST 37, SCREENWIDE 66→68, ROBUST 120, MIDSCREEN 39, …) can never
be ranked against data refresh on its own face. That is a defect of the faces, not a finding about
the repair, and the ledger says so per row rather than in prose.

## What changed

- `scripts/e97_routing.py`: `LADDER_NAMES` + `_screen_block` / `_nonzero_delta_rows` /
  `_ordering` / `_repair_count` / `ledger_row` / `screen_reach_ledger` / `run_screenreach`,
  new CLI mode `screenreach` (selftest 15 → 29 legs).
- `results/e79/SCREENREACH-2026-10-27.json`: the face (32 rows + totals + answers + skipped list).
- `results/runnable_pool.json`: E127 → done with `result_ref`.

## Verify

```
python scripts/e97_routing.py selftest        # 29/29
python scripts/e97_routing.py screenreach --publish
```

## Honest

- Faces are FILES: one leg at two cutoffs is two rows, so `sweeps` over-counts legs.
- `names_in` is 1271 on the sweeps and 1317 on the twins because the panel grew; the neutralised
  COUNT is not comparable across generations, the ladder intersection is.
- The ledger reports the E97-declared twins; 9 further screened faces (`SCREENGAP*`, older
  `MIDSCREEN`/`SCREENREG`/`WIDE`/`WEEKCLASH` copies) carry a census without being a twin of any
  runner. They are annotated `not_a_declared_twin`, not indicted.
- Ordering bands (1.25 / 0.8) are conventions; the ratio column lets a reader re-band the table.