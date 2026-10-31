# r1324 bm-b -- E299: legs that compare a face value finer than the face prints it

**Card:** E299-ROUNDED-VS-TOLERANCE-CENSUS (ready -> done)
**Face:** `results/state_tilt/PRECISIONCENSUS-2026-10-30.json` (+ `precisioncensus_latest.json`)
**Producer:** `scripts/e299_rounded_vs_tolerance_census.py` (run / verify / selftest 32/32)

## What was asked

r1316 repaired one instance of a shape: a face published a 6-dp point set beside a full-precision
interval, and the smoke leg that read the pair compared them at 1e-9. The repair changed that leg.
The open question is the size of the class: which legs compare a rounded published value at a
full-precision tolerance (or at exact equality), how far apart are the copies, and does each face
declare the precision it prints.

## How it was measured

*Legs* are the blocks of `smoke_test.py` ending in one `check(...)`, attributed by that call's
name (320 legs). Inside a leg a *site* is a comparison that is either exact equality with a
numeric anchor (a float literal, a `float(...)` cast, or a key whose name says it holds a
measured quantity), a quantized equality (`round(a, d) == round(b, d)`), or an inequality whose
epsilon is a literal below 1e-5. Template and glob names a leg mentions (`BANDPATH-%s.json`) are
kept out of the face list and disclosed.

*Precision* is measured from the face itself, at the level of the key the leg actually reads: for
every leaf published under that key name, the smallest number of decimals `d` with
`round(v, d) == v`; the coarsest such `d` is the field's printed resolution. Integer-only keys can
never be at risk from a quantum, so they are dropped before any tolerance is compared. Where no key
of a site exists in the face, the face's coarsest quantum is used as an explicit upper bound and
the row is labelled `face_level`.

*Rule, declared before a number:* a site is AT-RISK when its tolerance is finer than half the
quantum the field is printed with. It is never called broken -- the leg may be reading a
full-precision sibling the face also publishes.

## The answer

| reading | value |
| --- | --- |
| legs in `smoke_test.py` | 318 |
| legs with a numeric comparison against a face | 42 |
| numeric comparison sites | 62 (epsilon 39, exact equality 21, quantized 2) |
| faces read by legs | 42 |
| faces that declare the precision they print | 5 |
| faces that do not | 37 |
| **at-risk sites** | **29** (21 on the field's own decimals, 8 on the face-level bound only) |
| measured rounded/full sibling pairs inside one face | 0 |
| sites naming one key in two faces | 5 |

Verdict: `legs_compare_face_values_finer_than_the_faces_print`.

Representative rows (full list on the face):

- `smoke_test.py:750` `abs(_px - _r['session_open']) > 1e-9` -- `session_open` is printed at 3
  decimals; the tolerance is 5x10^5 times finer than half its quantum.
- `smoke_test.py:2826` `abs(_r30b.get('band_frac') - _focus31.get('band_frac')) < 1e-12` -- two
  faces' `band_frac` compared at 1e-12 while both are printed at 6 dp; the same key in the two
  faces differs by 1.98, i.e. they are not one quantity, so the tolerance is not the problem -- the
  comparison is.
- `smoke_test.py:2553` `(_mo28.get('cost_bp_per_year_oos') or 0.0) != 0.0` -- a nonzero test on a
  value printed at 6 dp: a cost that rounds to zero reads as "no cost".

## Two readings that had to be kept apart

1. **A measured pair is not a near pair.** The first cut paired any two leaves within 1e-3 whose
   smaller was the larger rounded to `d`; it "found" `current_dd` vs `cumulative_ret` (gap 4e-8),
   which are two different quantities that happen to be close. A copy is the same leaf key
   published twice, so the same-key rule is now the only way a pair is reported. On the real
   directory that leaves **zero** measured pairs -- and that zero is a measurement, not an
   absence of effort: the r1316 repair removed the only one there was.
2. **The same key in two faces is not the same quantity.** Five sites name one key across two
   faces; their gaps (1.98 on `band_frac`, 0.22 on `share_taken_by_vol`, ...) are published as
   distances with a disclosure that a gap above the tolerance reads "same name, different
   quantity", never a defect count. Without that sentence the face would manufacture five false
   convictions out of a naming coincidence -- the E207 trap one level up.

## What this changes downstream

Nothing is re-measured by this face; it is a map. The next round has 29 named lines, of which the
eight `face_level` rows are the ones still waiting on evidence -- the key could not be located in
the face, so their quantum is an upper bound. Those eight are the natural head card.

## Evidence

- `scripts/e299_rounded_vs_tolerance_census.py -- run / verify (0 problems) / selftest 32/32`
- `results/state_tilt/PRECISIONCENSUS-2026-10-30.json` + `precisioncensus_latest.json`
- `Tools/s6_chain_bmb.py` leg `precision_census` (verify)
- `smoke_test.py` leg E299 (re-derives the face; fails on a non-numeric exact equality being
  counted, on an integer-only key being at risk, on a near pair being published as a copy, and on
  the disclosure sentence going missing)
- methodology card `E304`