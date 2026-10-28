# E180 - which published "levels" are books and which are sums

Round r1215 (2026-10-28, bm-b) | dept: research + engineering
Face: `results/e79/DECOMLEVELQUOTES-2026-10-27.json`
Tool: `scripts/e97_routing.py` mode `levelquotes` (selftest 14 -> 40 legs, 40/40)
Pool row: `E180-TILT3-DECOMP-LEVEL-QUOTES-AUDIT` (seeded r1211, burned here)

## The question the pool row asked

E177 closed the arithmetic: a decomposition level (a sum of daily `w*r` terms) and a book level
(each book compounded on its own) are different objects, and their gap is a book-specific number.
But six faces had been printing decomposition levels beside anchored ones and nobody had audited
**which published sentences still quote which arithmetic**. A derived level published without its
offset is the same class of defect as a verdict that lives only in a receipt: the number is there,
the reason to trust it is not.

## What the sweep covers

`results/e43_tilt_4member/*.json` (22 faces) plus `results/e79/*.json` (3 faces, no levels in
them -- measured, not omitted). Every numeric leaf outside a face's `/spec/` block is classified:

| class | rule | cells |
|---|---|---|
| anchored | level-shaped name, producer builds it off month-end book marks | 979 |
| derived_daily | `decomposition` / `arithmetic` / `unanchored`, E177 reading (a) | 50 |
| arithmetic_of_levels | a sum of LEVELS (`legs_sum_bp`), neither (a) nor (c) | 5 |
| offset | `offset` / `gap` in the name | 2041 |
| not a level | delta / sd / share / pct / deadband / sign / residual / tolerance ... | excluded |

The arithmetic class is not read off the name alone. For each face the leg finds the `def` whose
body holds the face's `study` literal in `scripts/e39_panel_census.py`, then walks that function's
own call graph and asks whether it reaches `_daily_rets` / `_month_daily_rets` /
`_tilt3decom_blocks`. Twelve of the family's thirteen producers never touch a daily return; only
`run_tilt3decompoffset` does. That split is what turns a name rule into a code fact.

## What the audit found

**No leak.** All four faces that quote a derived level (TILT3LEGS `legs_sum_bp`, TILT3SIGNBOOKSPLIT
`decomposition_engine_bp_*`, TILT3SIGNDECOMOFFSET, TILT3SIGNDROPSWEEP `unanchored_base_*`) also
publish an offset in the same file. 2041 offset cells across 18 faces.

**One collision.** `decomposition_engine_bp` is published from two arithmetics:

| era | arm | daily producer (E177) | monthly producer (E176) | diff |
|---|---|---|---|---|
| pre2017 | raw/screened | 258.8365 | 261.76 | -2.9235 |
| 2017_2020 | raw/screened | 301.2404 | 304.77 | -3.5296 |
| 2021_2023 | raw | 252.2442 | 255.87 | -3.6258 |
| 2021_2023 | screened | 282.4866 | 286.07 | -3.5834 |
| 2024_now | raw | 27.8998 | 31.30 | -3.4002 |
| 2024_now | screened | 77.5728 | 80.90 | -3.3272 |
| full | raw | 221.4675 | 224.82 | -3.3525 |
| full | screened | 238.6132 | 241.95 | -3.3368 |

Ten comparable cells, gap in **2.92..3.63 bp**, spread **0.7023 bp**. Read as a signal: four eras
of different volatility, two arms, one sign, and a spread under a basis point -- compounding would
scale with the era, so this is a **definitional wedge**, not a compounding artifact. What the wedge
IS has not been attributed; E177's spec is the only one of the two that declares its reading, and
the E176 side is a per-name monthly sum whose definition is not published. That is the honest
state: two objects under one label, one of them documented.

**Offsets are book-specific, and the family already disagrees with itself.** Where a face publishes
an offset that is the same construct as an E177 column (`level_offset_bp`, `raw_offset_bp`,
`screened_offset_bp`, wide/ladder variants), the two are differenced: 40 comparisons, max abs diff
**3.58 bp** (TILT3SIGNDROPSWEEP's engine offset 25.44 vs E177's 28.41 on pre2017). Same sign, same
order, ~3bp apart -- the same "two objects, one label" shape as the collision, at offset level.

The 2041 minus 40 remaining offset cells are inventoried with reason `not_the_same_construct`:
`offset_left_as_cross_term_bp` is a *decomposition* of an offset and `arithmetic_vs_geometric_gap_bp`
is a gap of the tilt legs, so differencing either against the offset itself would compare a part to
a whole.

## Controls

- Fixture legs prove the plumbing (anchored-only, derived-with-offset, derived-without-offset leak,
  monthly-producer sum, era/arm parsing, spec-block exclusion).
- L37 runs on the real disk: every quoting face resolves to a producer in the census source, the
  E177 face reads `quotes_derived_with_offset`, joins resolve, and the leak count is 0.
- The leg publishes into a directory it scans, so it excludes its own study: without that the
  sweep grew 25 -> 26 faces and 1034 -> 3274 cells by self-inclusion (L36d pins it).

## Honest limits

- Classification is name-based *within* the verified producer split: a cell renamed without
  re-burning this leg would be misread. Every cell is published with its path so a reader can
  re-classify.
- `derived_arith` is per face, not per cell: a producer that reaches the daily helpers may still
  mix arithmetics inside one face.
- Publishing an offset is not the same as subtracting it; this leg measures presence and value.
- The wedge's source is open. This face says the two numbers are different objects and that the
  difference is definitional in shape -- it does not say which definition is right.