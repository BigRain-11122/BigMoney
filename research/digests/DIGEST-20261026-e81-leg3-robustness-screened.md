# DIGEST 2026-10-26 — E81 leg 3: the robustness face's *sign* was a data artefact

Tool: `python scripts\e39_panel_census.py screenrob`
Face: `results/e43_neutral_robust/ROBUST-20261023-screened.json`
Twin (untouched, same cutoff, default path): `results/e43_neutral_robust/ROBUST-20261023.json`
Selftest: `python scripts\e39_panel_census.py selftest` → 257/257 (was 252, +5 legs)

## What E43 published

E43 (`neutralrob`) is the face that decides whether the size-neutral spread survives
twelve cells — four decision calendars (`me_m1`, `me`, `me_p1`, `mid15`) × two fee
levels (x1, x3) — in the newest era. On the as-traded panel it reads:

| cell | 2024_now size-neutral bp |
|---|---|
| cost_x1\|me | +18.0 |
| cost_x1\|me_m1 | +16.2 |
| cost_x1\|me_p1 | **-10.9** |
| cost_x1\|mid15 | **-15.4** |
| cost_x3\|me | +11.2 |
| cost_x3\|me_m1 | +9.3 |
| cost_x3\|me_p1 | **-17.6** |
| cost_x3\|mid15 | **-22.4** |

`newest_era_all_positive = false`, min -22.4, range 40.4 bp. The standing reading was
"the newest-era spread is decision-timing fragile: it only survives at month-end."

## What the split screen does to it

The whole cell grid is rebuilt per arm — engine curves *and* the member tilt regressor
together — from a universe whose integer-ratio split prints are repaired
(`panel_screen.screen_universe`).

| arm | all 8 cells positive | min cell bp | range bp | repaired prints |
|---|---|---|---|---|
| unscreened | **false** | -22.4 | 40.4 | 0 |
| `neutralise_int` (integer-ratio screen) | **true** | +164.4 | 36.6 | 65 (56 in 2024_now) |
| `neutralise` (all-adjacent screen) | **true** | +316.9 | 35.9 | 135 (109 in 2024_now) |

Sign flips vs unscreened, identical in both arms: `cost_x1|me_p1`, `cost_x1|mid15`,
`cost_x3|me_p1`, `cost_x3|mid15` — i.e. exactly the four non-month-end cells.

Widest single-cell move: `cost_x1|mid15` -15.4 → +171.5 (int) / +329.9 (full),
i.e. +186.9 / +345.3 bp.

## Reading

1. The "calendar fragility" verdict was carried entirely by the non-month-end cells, and
   those are the cells whose books turn over on the days where a repaired print sits.
   Repair them and the property inverts: every cell positive, in both screens.
2. Band 40.4 → 36.6 / 35.9 bp while the level rises ~10x — the third instance of the
   E81 band-blind-to-common-shift rule: a narrowing band is not evidence of stability.
3. The level itself is the least interesting number here. What changed is a *sign
   property*, which is the kind of claim the chain quotes as "survived".

## Honesty

- The screen cannot recover a print the source never published; it only removes the ones
  the panel shows as integer-ratio jumps.
- Cost x3 is the engine's own 13.041 bp/side constant scaled, not a measured schedule.
- The ladder leg is untouched by the screen (its five members are never the repaired
  names), so the arm moves only through the wide book — the same asymmetry E81 leg 2
  reported.
- Descriptive census: no gate, no verdict, no prereg, no trial count.

## Default-path proof

`neutralrob` was re-run through the untouched loader at the same cutoff and its eight
cells reproduce the new file's `unscreened` arm exactly (`default path identical: True`,
zero differing keys) — the new `raw_all` parameter is opt-in and the published face is
unchanged in behaviour.