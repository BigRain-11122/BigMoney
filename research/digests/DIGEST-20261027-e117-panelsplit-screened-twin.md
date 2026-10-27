# E117 — the split census on the screened arm: E75 was reading the prints it repairs

Face: `results/e44_midmonth/PANELSPLITSCREEN-20261027.json` (arms beside it as
`PANELSPLIT-arm-raw-20261027.json` / `PANELSPLIT-arm-neutralise_int-20261027.json`),
evidence_cutoff 2026-10-27. Leg: `scripts/e39_panel_census.py panelsplitscreen`
(selftest 362 → **371/371**). Pool row `E117-PANELSPLIT-SCREENED-TWIN`.

## Why this leg exists

After E116 the routing table (`scripts/e97_routing.py run`) leaves `run_panelsplit`
as the largest uncovered runner (234 numbers, one mode) — and it is the only census
leg whose *subject* is the repair. E75 counted the adjacent-session prints that
break the 30% screen and priced them at ~216bp/yr of equal-weight book cost; the
screen (`panel_screen`, `neutralise_int`) edits exactly those prints. So the hazard
is not hypothetical: the audit may be measuring the material it repairs.

Cost: a `raw=` seam on `_panel_inputs`/`run_panelsplit`, one harvest, one burn, two
arms off one load at start 2020-01-01.

## The measurement

73 joined cells (panel, summary, three eras, per-year event counts). Same-arm
control, plus a cutoff control against the previously published raw face
(`PANELSPLIT-20261021`).

| axis | moves | magnitude |
|---|---|---|
| repair (`neutralise_int`) | **40 of 73** (26 count, 14 value) | see below |
| refresh (`PANELSPLIT-20261021` raw vs today raw) | 9 of 73 | max Δ 183 (breadth_min 14 → 197) |
| identity (raw vs raw) | 0 of 73 | 0.0 |

### 1. Two fifths of the census disappears when the repair is switched on

| quantity | raw | screened | Δ |
|---|---|---|---|
| events | 161 | 96 | **−65** |
| names carrying an event | 152 | 90 | −62 |
| adjacent (single-session) | 135 | 70 | **−65** |
| gapped (resumption) | 26 | 26 | 0 |
| integer-ratio fingerprints | 74 | 9 | **−65** |
| non-integer prints | 87 | 87 | 0 |
| book cost, whole window | 1,468.23 bp | 1,058.25 bp | **−409.98** |
| book cost, per year | 215.37 bp/yr | 155.23 bp/yr | −60.14 |

The screen reports `names_in = names_out = 1317`, `names_touched = 67`,
`events_neutralised = 67`. The census loses 65, not 67, because two of the repaired
prints sit outside this window/breadth filter — a two-event reconciliation gap,
stated rather than smoothed.

Read the deltas by mechanism: **gapped and non-integer counts do not move at all**
(the repair targets adjacent integer prints only), while *every* adjacent and
*every* integer-ratio count moves by the same 65. So the repair's boundary is
visible in the numbers: it is adjacency, not "splits".

### 2. Where the repaired material lives

| era | events raw → scr | integer prints raw → scr | book bp raw → scr |
|---|---|---|---|
| pre2017 | 0 → 0 | 0 → 0 | 0 → 0 |
| 2017_2020 | 4 → 4 | 0 → 0 | 103.58 → 103.58 |
| 2021_2023 | 48 → 39 | 18 → **9** | 722.59 → 601.50 |
| 2024_now | 109 → 53 | 56 → **0** | 642.06 → 353.17 |

The newest era is where it bites: **52% of its events, and every one of its 56
integer-ratio prints, are repaired material** — it loses 289 of its 642 bp. The
`2017_2020` era is untouched (4 events, none integer-ratio), which is the cleanest
available proof that the difference between eras is the panel, not the code.

By year, 2025 loses 28 of 33 events and 2026 loses 23 of 65 — i.e. the recent
years are the ones whose published census levels were standing on repairs.

### 3. What is left is a *different claim*, not a cleaner one

After the repair the census still carries 96 events on 90 names: **87 non-integer,
9 integer, 70 adjacent, 26 gapped**. The residual is not noise that the screen
would remove with a better parameter — it is resumptions after suspension, ETFs
whose daily limits are not 10/20%, and prints whose implied ratio is not an
integer at all. E75's own honest lines said a flagged print "may be genuine"; this
burn says the *post-repair* set is where that caveat actually lives.

The 9 surviving integer prints all sit in 2021_2023 and are gapped prints
(`gapped_kept = 34` panel-wide, `neutralise_int` keeps gapped events), so the 9 are
the integer-ratio subset of the resumption class rather than a repair miss.

### 4. One column that moved for a reason that is not the panel

`by_era[*].years` moves (2024_now 2.6256 → 2.2012, 2021_2023 2.7077 → 2.4531)
because that column is derived from the *first and last surviving event date* in
the era. Removing events shortens the measured span, so the era's `bp_per_year`
denominator moves too (2024_now bp 642→353 is *more* than the per-year drop
84.1 × years). Any comparison of era `bp_per_year` across arms must divide by a
fixed span, not by this column.

## Controls

| control | isolates | result |
|---|---|---|
| identity (raw vs raw) | join machinery | 0 of 73, max Δ 0.0, top-event identity unmoved |
| cutoff (`PANELSPLIT-20261021` raw vs today raw) | panel refresh | 9 of 73, max Δ 183 |
| coverage | is the twin a twin? | 73 compared, 0 one-sided, 4 null-on-both (`era/pre2017` value columns, structurally empty) |
| headline identity | ranked top event | `sh510580` → `sh510230` (moved) |

The cutoff control's 183 bp sits on `panel.breadth_min` (14 → 197): the old face
had a session with only 14 priced names, today's minimum is 197. That is a panel
refresh artefact in a supporting column, not a census finding, and it is why the
repair's 40 cells had to be read against a 9-cell refresh footprint.

## What this does not say

* Descriptive census only: no gate, no verdict on the strategy, no prereg, no
  trial count, no ledger booking.
* This is the one twin where the counts are **expected** to move: the repair edits
  the panel the census counts. `face_survives_the_repair = false` here is the
  measurement, not a warning — the face's `honest_flag` says so in-line.
* The screened arm keeps every name (`names_in == names_out`), so `panel.names`
  and breadth can only move through the census' own filters; that is a property of
  the mode, not proof the panel is clean.
* "Repaired" never means "clean": the residual 96 events are disclosed as their own
  class, and E75's arithmetic-impossibility caveat (ETFs, resumptions) moves to the
  residual rather than vanishing.
* Scope quirk, disclosed on purpose: the headline identity flips between the two
  arms but the join's event dates are not harvested as a date face (only the
  headline is), so this face cannot say *which* events came and went. A per-event
  diff is the obvious next ticket if anyone needs the name-level receipt.