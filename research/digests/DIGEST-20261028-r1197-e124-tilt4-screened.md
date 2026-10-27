# E124 the four-member tilt keeps its totals and loses part of its per-era attribution (r1197 bm-b)

Face: `results/e43_tilt_4member/TILT4SCREEN-20261027.json` (new), per-arm checkpoints
`TILT4-arm-raw-20261027.json` / `TILT4-arm-neutralise_int-20261027.json`.
Base face: E43 `run_tilt4` (per-era four-member tilt = 2 broad-cap vs 510500/512100, plus a
spread decomposition into a size-neutral alpha and a size beta term).
Screen arm: `panel_screen.screen_universe(mode=neutralise_int)`. Cutoff 2026-10-27.
Selftest `e39` 442 -> 459; `e97` routing re-derived: covered_twin 20 -> 21, uncovered 4 -> 3.

Note on where it publishes: the pool card named `results/e43_neutral_robust/` for the
deliverable, which is the ROBUST leg's directory. The tilt4 raw face publishes into
`results/e43_tilt_4member/`, so the twin is written beside it -- the cutoff control reads the
raw face's own history and a reader finds the two arms in one place. Deviation is recorded
here rather than silently.

## What moved

93 cells compared, 17 move, max |delta| 57 (bp). Attribution, complete:
16 era / 0 skin / 1 derived answer / 0 other.

The zero on `skin/` is the licence to attribute: the 4-vs-5-member rows price the STAR leg on
shared months, and a move there would name a different effect than the repair. Every moved
cell is inside the per-era block that the face exists to publish.

## The repair lands on ONE component of the decomposition

| era | spread raw | size-neutral alpha | size component |
|---|---|---|---|
| 2021_2023 raw | +251.1 | +394.1 | -143.0 |
| 2021_2023 screened | +280.4 | +420.3 | -139.9 |
| 2024_now raw | -21.6 | +17.3 | -38.9 |
| 2024_now screened | +25.1 | +64.3 | -39.2 |
| full raw | +219.7 | +208.4 | +11.3 |
| full screened | +241.9 | +230.7 | +11.2 |

The size base term moves by at most 3.1bp across all three eras (+3.1 / -0.3 / -0.1) while the
size-neutral alpha moves +26.2 / +47.0 / +22.3. So the repaired prints change what the book
earns *after* the size tilt is removed; the size tilt itself is essentially untouched. That is
a per-component reading, and the total (`spread raw`) cannot distinguish it from "everything
moved a bit".

## The repair is also era-specific

`2017_2020` moves **0 of its 24 cells**; `2021_2023`, `2024_now` and `full` move. Same panel,
same repair, one era unaffected -- so a single "the face moved by N cells" sentence would
average a touched era with an untouched one.

The newest era's spread **changes sign**: -21.6 -> +25.1 bp. That is one of the 20 arrow claims
(`spread_raw_sign -1 -> +1`) and the only one that moved. The cell delta is 46.7bp and the sign
threshold was 21.6bp away, so this is not a rounding accident.

## Was the sign flip the repair or the refresh?

The cutoff control (published `HIST-20261020` raw vs today's raw, arm held fixed) moves the
same cell -35.1 -> -21.6: **13.5bp in the same direction, and it cannot cross zero on its own**.
The repair supplies the remaining +46.7. So the flip is repair-attributable; the refresh only
narrows the gap.

But the era's tilt LEVEL is refresh-dominated: `2024_now` `tilt_annualised_bp` moves
246.5 -> 132.1 across the seven-day refresh (-114.4bp), which is twice the largest repair
delta (57bp) anywhere on the face. Same law as r1162: a level on this face is not quotable
without its cutoff, while a sign or an ordering can be.

## Controls

- same arm vs itself: **0 of 93** cells, 0 claims -- the harness is arm-invariant.
- cutoff control: **29 cells, max 131bp** (the worst is `skin/2024_now` five-member tilt
  748.1 -> 617.1). Here the refresh is LARGER than the repair in both cell count (29 vs 17)
  and magnitude (131 vs 57).

That makes three orderings in three consecutive twins: E122 repair dominated the refresh 3.6x,
E123 they were the same size, E124 the refresh dominates 1.7x/2.3x. The lesson is not "which
one is bigger" but "each face ships both controls and neither number is quoted alone".

## The defect this leg found in an older face's own docstring

`run_tilt4`'s docstring claimed the four-member skin "reaches back to 2013". The published
face says otherwise on both arms: `pre2017` has 1 usable month, and `months4` starts 2016-12.
The binding member is no longer the STAR leg (sh588000, first bar 2020-11-13) but `sh512100`
(first bar 2016-11-04), so the reach-back the leg actually delivers is **2017-01** -- 48
months of 2017-2020 recovered against 1 month on the five-member skin. Corrected in-window
alongside the `raw=` seam. This is the E94 family again from the prose side: a claim wider
than the face it describes.

## Method card

E163 in `knowledge/METHODOLOGY_ASSETS.md`.

## Honest

Descriptive census only: no gate, no verdict on the strategy, no prereg, no trial count, no
ledger booking. Eras are calendar partitions of one continuous monthly series and do not add
up. The screened arm repairs prints inside the panel it is handed and does not add or remove
bars, so an unchanged `months` cell is a property of the repair, not evidence the panel is
clean. The decomposition is published per era and verified to sum on both arms
(`incomplete_eras: []`, tolerance 0.2bp) rather than assumed.