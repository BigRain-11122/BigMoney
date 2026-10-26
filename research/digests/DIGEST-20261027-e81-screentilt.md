# DIGEST 2026-10-27 · E81 leg 5: the tilt decomposer is flagged exposed and is immune

**Leg**: `python scripts\e39_panel_census.py screentilt` (mode added this round)
**Face**: `results/e42_tilt_era/TILT-ERA-20261026-screened.json` (20 delta cells, 0 non-zero)
**Untouched twin**: `results/e42_tilt_era/TILT-ERA-20261020.json` (published face, never rewritten)
**Selftest**: `python scripts\e39_panel_census.py selftest` → 262/262 (was 257, +5 legs)

## Why this leg exists

E79's matrix (`FACESCREEN-20261022.md`) marks 33 census modes as *exposed*: they read the
per-name loader with no raw hook, so an equal-weight number they publish still charges
unadjusted share-split prints at weight `1/n`. The pool item asked for the
highest-consumption ones first — `era`, `calcost`, `neutralrob`. Two of those now have
screened twins (`screenreg`/`screencalc`/`screenrob`); this leg covers the remaining
member-tilt decomposer, the face behind "how much of the ladder's monthly return is a size
tilt, and what is left over".

## What the screen actually repairs

`panel_screen.screen_universe` over the 1,317-name panel, using the **panel calendar** for
gap detection (not the ISO day-distance fallback — that under-counts by 2.5x on this panel):

| arm | names touched | events repaired | of which integer-ratio |
|---|---|---|---|
| `neutralise_int` | 67 | 67 | 67 |
| `neutralise` | 131 | 137 | 67 |

## What moved: nothing, on every cell

All 20 cells (5 rows × tilt level / beta / alpha / R²) reproduce to the last digit:
`non_zero_delta_cells = 0`, `sign_flips_vs_unscreened = []`, `widest_correction = null`.

The reason is structural, not statistical: **none of the 131 repaired names is one of the
five ladder members** (`sh510300 / sh510050 / sh510500 / sh512100 / sh588000`). This face is
computed entirely from the ladder members' monthly marks and the ladder's own engine curve,
so the wide book it screens never enters the arithmetic.

Baseline check that the leg is faithful and not silently empty:

| era | published (cutoff 10-20) | unscreened arm (cutoff 10-26) |
|---|---|---|
| 2021_2023 tilt | +609.2 bp | +609.2 bp (identical) |
| 2024_now tilt | +748.1 bp | +697.6 bp |

The newest-era number moves because six more sessions entered the window, not because of the
screen; the `2021_2023` cell pins the replay as bit-identical.

## The reading to carry forward

E79's exposure flag is necessary and **not sufficient**. A mode is only contaminated if the
equal-weight book it reads *contains* the flagged names. Two of the four named legs turned out
to matter a lot (`screencalc` moved 37 of 72 cells, `screenrob` flipped the robustness sign);
this one cannot move at all. Triage for the remaining exposed modes should therefore ask
"does this mode's read set intersect the repaired set?" before asking "how much does it
consume?" — the first question is answerable from the code, the second only after a burn.

## Honest limits

- the screen repairs arithmetic impossibility only: a flagged ETF print may be genuine (ETF
  daily limits differ from the 10%/20% stock band), so every arm is a sensitivity face
- `pre2017` and `2017_2020` are empty on both twins (the monthly core needs a wide book that
  only exists from 2020-12), so this leg says nothing about the two oldest eras
- descriptive census only: no gate, no verdict, no ledger booking, trial 0