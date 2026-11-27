# Does a census headline agree with the arms inside it?

generated 2026-11-27T03:04:31+08:00 · cutoff 2026-11-26 · **HEADLINE_OVERSTATES_MERIT**

3 census faces read · 50 skipped (non-census or unreadable) · **1 flagged**

## The defect

`bench_generic.run_census()` picks its headline from `powered` -- a
*resolution* statement (MDE ≤ target_edge) -- and the **sign** of that arm.
It never asks whether any arm passed a gate. So an arm at +1.2% with MDE 3.8
and an arm at +9% that cleared all five checks produce the same headline word.

## Faces

| face | headline | arms | GO | NO_EDGE | UNINFORM | clears H1 | best | worst | verdict |
|---|---|---|---|---|---|---|---|---|---|
| `census_bond_futures` | CENSUS_LEANS_POSITIVE | 5 | 0 | 5 | 0 | 1/5 | 4.02% | 1.92% | **LEANS_WITHOUT_A_PASS** |
| `census_commodity` | CENSUS_LEANS_POSITIVE | 14 | 2 | 12 | 0 | 6/14 | 5.19% | 1.52% | **AGREES** |
| `census_index_futures` | CENSUS_UNPOWERED | 20 | 0 | 18 | 2 | 3/20 | 6.78% | -2.93% | **AGREES** |

## Flagged

* `census_bond_futures` — **LEANS_WITHOUT_A_PASS**: headline says the space leans positive, but 0/5 arms passed every gate (1/5 cleared only the 4.0% H1 line; best arm 4.02%)

## What this does not do

* it does not re-issue any arm or face verdict (frozen set untouched)
* it does not reload panels; every number is read off published faces
* it does not decide whether a census space is worth another burn -- it only says whether its headline is supported by its own arms

inputs digest `4d6907c4dab3b498…`
