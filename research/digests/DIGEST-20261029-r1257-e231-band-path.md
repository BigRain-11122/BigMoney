# DIGEST 2026-10-29 r1257 bm-b -- E231: the one passing band is a full-sample effect

Card: `E231-PATH-TEST-THE-BAND`. Face: `results/state_tilt/BANDPATH-2026-10-29.json`
(`bandpath_latest.json` + `bandpath_by_cell_2026-10-29.csv`). Runner
`scripts/e231_band_path_test.py` (selftest 18/18). S6 leg `band_path_test`, smoke leg
`product: a band that passed on one path is path-tested before it is a finding`.

## The question

E230 ladders a hysteresis deadband on the volatility state and exactly one of thirty cells
clears its bar: `tilt_linear`, single panel, the narrowest rung `f=0.10`, t=4.04, +286 bp/yr.
The passing band was the *smallest* band in the grid -- the rung closest to the base arm --
and the point estimates were not monotone in the band. That is the shape E188 warns about,
so the rung had to be re-measured before anyone could call it a property of the rule.

## What was run

The same cell, same channels, same x2 cost level, on 25 panel-paths (12 single, 13 basket),
finer band grid (0.02..0.20, eight rungs centred on 0.10), two bars published:

* **lenient = 3.34**, E230's own frozen bar, reused verbatim and used for the survival test
  on purpose -- give the band every advantage;
* **strict = 4.10**, Bonferroni over this study's 600 cells, disclosed and not used to
  rescue anything.

Paths, three kinds: **split phase** (IS/OOS line moved -40/-20/-10/+10/+20/+40 sessions),
**decision lag** (weights delayed 1-3 sessions, both arms alike), **era** (calendar windows
re-derived end to end).

## Reading

Focus cell `primary_single / tilt_linear / f=0.10`, 12 paths: **positive on 12/12**, above
E230's bar on **8/12**.

| family | paths | range bp/yr | median | clears bar |
|---|---|---|---|---|
| structural (global + split + lag) | 10 | 145.2 .. 290.0 | 285.9 | 8 (the two misses are lag 2 and lag 3) |
| era (2015-2019, 2020-2026) | 2 | 77.1 .. 80.8 | 80.8 | 0 |

So the sign is robust and the **size is not**: the +286 is a full-sample number. Inside
either era the improvement survives in sign and shrinks ~3.5x, and neither era can resolve
it (t = 1.36 and 1.75). Across the whole fine grid **0 of 48 cells** survive every path
under the lenient bar; 7 cells are sign-unstable (mostly the basket, mostly the smallest
bands), 41 hold their sign but miss the bar somewhere, none collapse, none are under-powered.

Disclosed on both sides: the cell's *level* is a loss. At x2 costs on the global path the
base arm's pair is -878.7 bp/yr and the banded arm's own pair is -592.8 bp/yr. +286 bp/yr
is an improvement in a loss, not a positive return.

## Transferable

1. **A path test's answer is a share, not a cell.** "Positive on 12 of 12 paths" and "clears
   the bar on 8 of 12" are both true and they are different claims; a face that printed only
   the first would look like a confirmation.
2. **Split the paths into families before reporting a range.** Moving the split or the lag on
   one sample and re-deriving inside a calendar era are different experiments. Merged, the
   range is 77..290 and the median 285.9 -- a full-sample number standing in for a statement
   about a period. The families are separated in `focus_families` and a selftest leg keeps
   them apart.
3. **Give the arm the weaker bar on purpose.** Reusing E230's own 3.34 (rather than
   re-deriving a bar that fits this study) is what makes the rejection defensible: the band
   failed a line it had already been granted.
4. **A cross-face replay is the cheapest correctness gate in the chain.** The global path
   must reproduce E230's published cell to 1e-6 bp / 1e-9 t, and the smoke leg enforces it.
   A path study that cannot re-measure the thing it is testing is not testing it.