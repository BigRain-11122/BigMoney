# DIGEST 2026-10-28 r1204 bm-b — E170: the three-member tilt on the split-event-repaired arm

**Product**: `results/e43_tilt_4member/TILT3SCREEN-20261027.json` (82.9 KB) + new mode
`python scripts\e39_panel_census.py tilt3screened` (selftest 526/526 PASS).
Per-arm checkpoints: `TILT3-arm-raw-20261027.json`, `TILT3-arm-neutralise_int-20261027.json`.

## Why this burn

E126 (r1201) read the pre-2017 era for the first time — and read it on the RAW panel, while every
other skin in this family (E112–E127) had already been re-read on the split-event-repaired arm. So
"pre-2017 reads +1186bp/yr" and "this family was screened" had never been in the same sentence.

## What the twin says (one load, both arms, 137 cells joined)

| era | tilt (raw) | tilt (screened) | Δtilt | raw spread | neutral leg |
|---|---|---|---|---|---|
| pre2017 | +1186.4 bp | +1186.4 bp | **0.0** | 287.2 → 287.2 (0.0) | 134.4 → 134.4 |
| 2017_2020 | −923.9 | −923.9 | 0.0 | — | — |
| 2021_2023 | +609.9 | +609.9 | 0.0 | 251.1 → 280.4 (+29.3) | 350.6 → 378.1 |
| 2024_now | +252.8 | +252.8 | 0.0 | **−21.6 → +25.1 (+46.7)** | 58.8 → 105.9 |
| full | +237.1 | +237.1 | 0.0 | 227.6 → 243.9 (+16.3) | 236.1 → 252.4 |

- **The tilt series is identical on both arms** (`era_tilt_bp_cells_moved = 0`). The tilt is a ratio of
  member monthly returns; the repair touches the *engine's* own wide-vs-ladder path, not the regressor.
- 18 of 137 cells move (17 era / 0 skin / 1 answer), max |Δ| = **57.0 bp**, worst cell
  `era/2024_now · engine_ann_diff_bp` 106.0 → 163.0.
- **One published arrow flips**: `2024_now · spread_raw_sign` goes −1 → +1. On the raw arm the wide
  book *lost* that era (−21.6 bp/yr); on the repaired arm it won it (+25.1 bp/yr). The size-neutral
  leg goes 58.8 → 105.9 bp, so the flip is a real re-pricing of members, not a leak through the tilt.
- **pre2017 is untouched by the repair** (all four columns delta 0.0): the headline E126 number is
  arm-insensitive, which is the one thing a reader needed to know before quoting it.
- Decomposition still adds up on both arms (max |gap| 0.1 bp ≤ 0.2 tolerance).
- Same-arm control: 0 cells moved, 0 ordering claims moved (join completeness is not a verdict).
- Cutoff control: **null with a reason** — the only published `TILT3REACH-*` face carries this same
  cutoff, so a stale-face control has nothing to compare against yet. Null means "not measurable",
  not "clean" (E164 family).

## Reusable reading

1. **"The repair moved the family" is a per-cell claim, not a family-wide one.** Here it moved
   2021_2023, 2024_now and the full window by 17–57 bp and moved pre2017 by exactly nothing. A
   summary max-delta would have said "57 bp moved" and left the reader unable to tell which era's
   headline was safe to quote.
2. **A sign that flips under the repair must be published as a sign.** The magnitude table shows
   +46.7 bp; only the arrow list shows that "the wide book lost 2024_now" was an artefact of the
   unscreened panel.
3. **A regressor identical on both arms is a result, not a no-op.** Publishing `tilt_bp_delta = 0`
   for every era is what separates "the tilt is a ratio of member returns" from "the twin failed to
   burn one arm".

## Wiring

- mode `tilt3screened` added beside `tilt3reach` / `tilt3legs`; reuses `_tilt3_arm_cells`,
  `_tilt3_arm_dates`, `_burnin_pair_rows`, `_tilt4_arrows`, `_tilt4_decomposition_gap` — no second
  implementation of the join.
- selftest +5 legs (526/526) pinning: one moved engine cell moves exactly one harvested cell, the
  tilt cell stays put, the same-arm control reads zero, and the harvest keys stay in their buckets.
- card: `knowledge/METHODOLOGY_ASSETS.md` **E169**.