# E122 — the warm-spread ordering survives the print repair; every 2024-now level does not

**Face:** `results/e44_midmonth/WARMSPREADSCREEN-20261027.json`
**Base leg:** `run_warmspread` (E45) · **Twin:** `run_warmspreadscreened` · **Card:** E160
**Cutoff:** 2026-10-27 · selftest 393 → 427/427

## What this leg is

E97 traced 25 charged runners and found 13 twins; E122 adds the fourteenth — a
screened twin of the E45 warm-spread ordering leg. E45 publishes a **pair of
orders** (era thinnest→widest on the warm curve and on the cold curve) plus a
warm-vs-cold difference per era. That is a claim about ORDER, not about cells, so
the twin has to publish both layers.

## Seam

`run_warmspread` had no `raw=` parameter: it called `e27.load_universe()` itself,
so a twin could not burn raw and screened off one load. This round it grew one
(the same shape `run_entrydelay` got in E119), and `_panel_inputs`-style threading
was not needed because E45 loads its own universe rather than through a helper.

## The numbers

| | |
|---|---|
| cells compared | 68 |
| cells moved | 17 |
| max abs delta | 133.0 (mixed units — a screen, not a quantity) |
| wide curve cells moved | 8 |
| spread cells moved | 4 |
| ladder cells moved | **0** |
| other cells moved | 5 |
| ordering claims moved | **0** |
| same-arm control | 0 of 68, 0 ordering |
| cutoff control (raw 2026-10-20 vs raw today) | 17 cells, max 37.0 bp, 0 ordering |
| repair events | 67 of 1,317 names, all integer-like (30% threshold) |

**Worst cell:** `era/2024_now · warm_live_spread_bp` −92.0 → **+41.0** (Δ133 bp).

**Sign flips inside the newest era:**

| cell | raw | screened |
|---|---|---|
| 2024_now cold spread_bp | −55.0 | **+25.0** |
| 2024_now warm_live_spread_bp | −92.0 | **+41.0** |
| answers.cold_minus_live_bp | 37.0 | **−16.0** |
| 2024_now warm_minus_cold_bp | 161.0 | 138.0 |

**What did not move:** both orders. Warm order `2024_now > pre2017 > 2021_2023 >
2017_2020` and cold order `2024_now > 2021_2023 > pre2017 > 2017_2020` are
identical on both arms, so `ordering_survives_the_repair=true` while
`counts_survive_the_repair=false`.

**The zero that carries information:** the ladder book is a fixed five-name list,
so a repaired print cannot enter it. 0 of its cells moved. That is the control
that says the repair reached the WIDE book only, and it is why the 8 wide moves
are attributed to the repair rather than to the join.

**The cutoff control disagrees with the repair, and that is the useful part.** The
previously published raw face (`results/e45_warm_spread/WARMSPREAD-20261020.json`,
five sessions earlier) compares against today's raw arm at 17 cells / max 37.0 bp.
So the panel refresh and the print repair are the same size in cell count and the
repair is 3.6x larger in magnitude — this family is repair-dominated, like
E119/E120/E121 and unlike E118. The split differs too: the refresh moves the
**ladder** cells (2024-now warm ann −1.69 pp / dd −2.74 pp on 675→680 bars, pure
annualisation) while the repair moves **zero** ladder cells and only the wide book.
Two different mechanisms, two different fingerprints, and neither flips an order.

## Reading

Same shape as E95/E157 in a different family: **the ordering claim is
repair-robust, the level is not.** Two of the newest era's three headline levels
change sign under 67 neutralised prints — 67 events out of 1,317 names, 5% of the
universe, enough to flip the 2024-now cold spread from −55 bp to +25 bp. Anyone
quoting "the newest era is the thinnest" keeps their claim; anyone quoting "the
newest era's live window is −92 bp" does not.

## Pit found in-window (E94 family, third recurrence)

The first live run reported `0 wide / 4 spread / 0 ladder / 13 other`, which
contradicted its own worst-cell reading (a wide-derived cell moving 133 bp). Cause:
the attribution test was `"/wide/" in start`, but the harvest keys END with the leg
name (`era/2021_2023/warm/wide`) and carry no trailing slash, so every wide cell
fell through into `other`. Fixed to `startswith`-free `endswith("/wide")`, and the
face now publishes `moved_attribution_complete` so a bucket that does not sum to
`cells_moved` is visible to the reader instead of only to the code author.

Two selftest legs pin it: one asserts that the infixed test matches nothing, the
other that the suffix test finds both the warm and the cold wide face.

## Honest limits

- descriptive census only: no gate, no verdict on the strategy, no prereg, no
  trial-count consumption;
- the repair does not add or remove bars — `universe_members` is 1,317 on both arms;
- the warm curve pays its burn-in before the measured span by construction, so a
  warm spread move can be a slightly different weight path rather than a
  different decision;
- `cutoff_control` is measured but only against a 5-session refresh
  (`WARMSPREAD-20261020`, 2026-10-20), so it sizes five days of panel movement, not
  a long window; it is a comparison of two cutoffs of this leg, not an independent
  series.