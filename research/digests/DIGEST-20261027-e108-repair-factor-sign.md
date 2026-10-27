# E108 — the repair factor was mirrored on upward prints (fixed, every consumer re-derived)

Date: 2026-10-27 · round r1172 · dept: research+engineering
Face: `results/e44_midmonth/REPAIRFIX-20261026.json` (before/after per consuming face)
Tool: `scripts/e108_repairfix.py` (legacy control runner + generic face differ)

## The defect

`panel_screen.implied_ratio()` folds the implied share ratio to `>= 1` so that an
integer test can recognise a reverse split. `split_events` then used that folded
number as the forward-adjustment factor. On a downward print that is correct
(`1/(1+r) > 1`); on an UPWARD print it multiplies by `1+r` instead of dividing, so
a print of `+r` came out as `(1+r)^2-1`. E106 found the signature (8 of 16 flagged
windows stepped the wrong way) but could not fix it in-round.

Fix: the factor is now the cancelling value `1/(1+r)` for every event. The integer
test still reads the folded ratio — the fold is evidence, not a factor. Downward
prints are bit-identical (`1/(1+r)` already), so only reverse-split windows move.
`panel_screen` selftest 31 -> 35 legs (upward print cancels; factor `< 1` on an
upward print; downward factor unchanged at 12.0; upward gapped print repairable).

## Control: the diff is the factor, not the panel

`e108_repairfix.py legacy repairstep` re-runs the E106 leg with the OLD factor
monkeypatched back and reproduces the published `REPAIRSTEP-20261026.json` with
**0 of 966 numeric leaves moved**. Panel cutoff unchanged (2026-10-26). So every
delta below is the sign fix.

## Readings (before -> after)

| face | reading | before | after |
|---|---|---|---|
| REPAIRSTEP | class tally | 8 `step_amplifies_print` | 8 `step_cancels_print` |
| REPAIRSTEP | `fabricating_windows` | 8 | **0** |
| REPAIRSTEP | witness sh510580 repaired one-session read | +1464.09% | **+28.05%** |
| HELDSPLIT | 2024_now me / mid sh510580 arm read | +1902.84% / +1418.07% | **+28.05% / −2.94%** |
| HELDSPLIT | era-cell verdict tally | 4 one-window | 2 one-window + 2 few-windows |
| MID armed | 2024_now mid level, every gap arm | −364.7bp | **+4.9bp** |
| MID armed | sign flips across arms | none | **`2024_now/mid`** |
| GAPARM-ENDGRID | 2024_now mid delta span | 107.1bp | 48.5bp |
| GAPARM-ENDGRID | 2024_now mid published delta | −241.0bp | **+128.6bp** |
| GAPTOP3 | large moves named | 3 | 4 (`2024_now/mid +128.6`, 100% one window) |
| GAPTOP3 | price-read drivers | sh510580 only | sh510130 (3 windows), +8 more |

Untouched, as designed: 2017_2020 me (−745.9bp) and 2021_2023 me/mid (−1098.3 /
−1117.2bp), i.e. every downward-print window keeps its published level. That is
the strongest available check that the fix is directional and not a re-burn.

Numeric movement per face: GAPARM-ENDGRID 45/1141 leaves, GAPARM-FAMILY 226/4515,
GAPTOP3 27/1282, HELDSPLIT 569/5393, MID armed 84/3514, REPAIRSTEP 45/951,
SCREENGAPERA 166/4945.

## What this retracts or corrects

1. **E104's "the repaired arm is not automatically the plausible side" does not
   survive on its own witness.** The +1464% "repaired" read that motivated the
   warning was the sign bug; with the fix the same window reads +28.05% and the
   raw arm reads +406.42%. The general warning still stands as a habit, but the
   specific number must not be cited against the repair.
2. **Any published newest-era mid level of −364.7bp is superseded by +4.9bp.** The
   E99/r1164 line "unscreened −123.7 vs every arm −364.7" inverts: the repair now
   lifts the newest-era mid level by +128.6bp instead of cutting it by 241bp. This
   also flips the newest-era mid cell into the "sign flips across arms" list.
3. `2017_2020 me −745.9bp` and the 2021_2023 pair are unchanged and may be cited
   as before.

## Confound, stated

`SCREENGAPERA` was re-derived at cutoff 2026-10-26 against a published twin at
2026-10-23, so its diff (2024_now unscreened spread 100 -> 83bp, gap arm 300 ->
141bp, delta vs unscreened 200 -> 58bp) mixes the factor with two days of panel
arrival. Direction only; do not quote the delta.

## Remaining scope (seeded as E109)

Seven of the ~20 screened consumers were re-derived here (the gap-arm/E99-E106
lineage). The other screened legs — `midscreen`, `churngap`, `robustchurn`,
`churnse`, `singleprint`, `topnames`, `loodist`, `screenspread`, `screentilt`,
`screenwide`, `screenweek`, `screenreg`, `gapsplit`, `burncontrol` — each read a
`neutralise`/`neutralise_int` arm and are still carrying the old factor. They are
seeded as one sweep unit rather than silently left.