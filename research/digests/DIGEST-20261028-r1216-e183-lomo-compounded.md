# DIGEST 2026-10-28 r1216 bm-b — E183: the ladder survival sweep re-read on the compounded level

Face: `results/e43_tilt_4member/LADDERLOMOCOMPOUND-20261027.json`
Leg: `python scripts/e39_panel_census.py tilt3ladderlomocomp`
Spec: inside the face (`spec.arith_def` / `spec.comp_def`), selftest 617/617.
Method card: E183 in `knowledge/METHODOLOGY_ASSETS.md`.

## Why

E181 dropped each of the four ladder members in turn and reported that every era's LEVEL keeps its
sign. That verdict was computed on the arithmetic reading — the mean monthly contribution summed
and annualised as `mean x 12 x 1e4`. E177 had already established that the summed level and the
compounded level are different objects with a non-zero cross term. So "every era survives every
drop" was a statement about one arithmetic, and a robustness result that depends on which
arithmetic the reader assumes is not a robustness result.

## What was run

The identical drop set (same four members, survivors re-weighted to stay fully invested, months
that the dropped name alone could hold excluded from both sides), re-read on the geometric
annualisation of the same monthly book returns:

- `arith` = `mean(r_m) x 12 x 1e4` (the published object; must reproduce E181 exactly)
- `comp`  = `(prod(1+r_m) ** (12/n) - 1) x 1e4`

The cash residual (`__cash__`) is part of the book's return and is included on both sides; without
it the arithmetic reading disagreed with E181 by 30.5 bp on pre2017 (three cash-only months), which
is how the omission was caught.

## Readings

| era | arith bp | comp bp | offset (comp − arith) | survival | E181 join |
|---|---|---|---|---|---|
| pre2017 | 1018.215 | 762.597 | −255.618 | survives_every_drop_both | 0.0 |
| 2017_2020 | 1004.754 | 905.251 | −99.503 | survives_every_drop_both | 0.0 |
| 2021_2023 | −923.546 | −992.841 | −69.295 | survives_every_drop_both | 0.0 |
| 2024_now | 1088.647 | 770.224 | −318.423 | survives_every_drop_both | 0.0 |
| full | 597.506 | 387.039 | −210.467 | survives_every_drop_both | 0.0 |

- **The level verdict is arithmetic-independent.** No era flips under any drop on either
  arithmetic (`eras_arithmetic_dependent = []`). E181's conclusion holds and now covers both.
- **The offset is large and one-signed.** 69–318 bp per era, up to 425.6 bp on a single dropped
  book (2024_now without sh510050). Every one of the 22 drop rows is ≤ 0: that sign is AM ≥ GM, a
  theorem, so only the magnitude is informative — the level you quote moves by hundreds of bp on
  the choice of annualisation alone.
- **The DROP EFFECT is where the arithmetic bites.** 4 of 22 drops reverse the sign of their own
  effect between the two readings while the level itself keeps its sign: pre2017 sh510300,
  pre2017 sh510500, 2024_now sh510050, full (all eras) sh510050. The sharpest is 2024_now without
  sh510050: +73.2 bp on the sum, −34.0 bp compounded. "Dropping this holding helps" and "dropping
  this holding hurts" are both defensible from the same 34 months.

## Honest limits

- The two readings are the same monthly returns under two annualisations; the offset is a
  definitional wedge and does not shrink with more data.
- This offset (geometric vs arithmetic annualisation across months) is a different object from
  E177's `ladder_book_level_offset_bp` (compounding inside the month). They are published side by
  side and never added.
- Descriptive census: no gate, no prereg, no trial count, no portfolio claim.

## Next

E184 (wide-book cancellation location: monthly gross vs monthly net for the repaired names) is the
next ready head on this lane.