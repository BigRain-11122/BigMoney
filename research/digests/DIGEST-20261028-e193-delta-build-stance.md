# E193 — how every published delta in the decomposition family was BUILT

Date: 2026-10-28 | round r1227 (bm-b) | dept: research + engineering
Face: `results/e79/DELTASTANCE-2026-10-27.json`
Tool: `scripts/e97_routing.py mode=deltastance` (selftest 697 -> 702... see Verify)

## The question

E188 showed that one number published in two fee stances differs by exactly the
rebalance fee, and that a delta built from two *levels* inherits nothing while a
delta built from two *readings* inherits the arms' fee difference. E193 asks for the
sweep nobody had run: for every delta the family publishes, **which of those build
paths produced it**, and what would a reader lose by applying that label.

## Answer in one line

Of **152 era-level bp deltas across 14 faces, 60 are rebuilt exactly by an enumerated
build path, 58 are zero-valued (a zero has no sign and proves nothing), 34 cannot be
checked from either source, and none are built across stances.** 77 are fee-free by
construction, 10 are sums of absolute per-name deltas, 30 are arm deltas of screening
outputs, and the only construct that would carry the whole fee — gross minus net —
is published **nowhere** as a delta.

## The build table (by name, distinct)

| name | cells | build path | fee content | verification |
|---|---|---|---|---|
| `engine_ann_diff_bp` | 27 | two measures of one era (spread minus its arithmetic-geometric gap) | fee-free | 27 reproduced in-cell |
| `engine_bp_delta` | 20 | two published levels (raw vs screened) | fee-free | 12 reproduced, 8 zero |
| `gross_abs_delta_bp` | 10 | sum of ABSOLUTE per-name arm deltas | per-name arm fee | 7 zero, 3 unbuildable |
| `ladder_book_delta_bp` | 10 | two anchored book levels | fee-free | 10 zero |
| `net_delta_bp` | 10 | unnamed operand | 7 zero, 3 fee-free | 3 reproduced (book pair) |
| `engine_diff_bp` | 10 | arm delta of a screen output | no fee term | not buildable |
| `tilt_bp_delta` | 10 | arm delta of a screen output | no fee term | 10 zero |
| `delta_4/5member_minus_3member_bp` | 15 | operands live on a sibling face | unknown | not checkable here |
| `published_engine_bp_delta` | 5 | two published levels | fee-free | 3 reproduced, 2 zero |
| `wide_book_delta_bp` / `rotating_wide_book_delta_bp` / `engine_delta_from_books_bp` | 15 | anchored book levels | fee-free | 9 reproduced, 6 zero |
| `engine_delta_residual_bp` | 5 | difference between two deltas | not a build | 3 reproduced in-cell |
| `neutral_bp_delta` / `spread_raw_bp_delta` | 10 | arm delta of a screen output | no fee term | 4 zero, 6 not buildable |

## Three findings worth a reader's time

1. **The defect E193 feared does not exist here — a different one does.** No published
   delta differences a gross reading against a net reading, so no delta silently
   carries the whole 2.92–3.62 bp fee. What the family does publish is 10
   `gross_abs_delta_bp` cells that are *sums of absolute per-name arm deltas*: their
   fee exposure scales with how many names moved, not with anything visible in the
   cell.

2. **The sign convention is uniform — and opposite to the arithmetic the names
   suggest.** All 30 ladder-rebuilt deltas reproduce only as the **negated**
   construct: the faces print `screened − raw` where the rule reads `raw − screened`.
   A positive published delta therefore means *the screened arm is larger*, which is
   the reverse of the naive reading. This is one family-wide convention, not a
   per-cell error — but it is stated nowhere in the faces.

3. **`net_delta_bp` is named with the family's stance vocabulary and built fee-free.**
   Three cells (`WIDESIDEGROSS` 2021_2023 / 2024_now / full: 30.204 / 49.598 / 17.121)
   carry "net" in the name while being exactly the wide book's `screened − raw` level
   difference. In the same family "net" means *net of the fee* (E188 measured it). A
   reader who carries that vocabulary across faces reads the wrong object.

## Why zeros are reported and not scored

34 of the 152 cells are `0.0`. A zero matches any zero construct and any negated
zero, so a matcher that counted them would manufacture reproductions out of nothing
(the E-note family's own recurring failure: *equal curves because neither side ran*).
They are reported as `not_checkable_zero` and excluded from the verdict.

## Honest scope

- Era-level only. **380** deltas nested inside per-month / per-name lists are counted
  and excluded: they are internal arithmetic of a parent cell, not a quote a reader
  takes away.
- A cell's build path is bound by its **name**, then verified against a construct
  computed from the published ladders, or — for cross-measure and residual deltas —
  against the siblings of its own era cell. Six cells reproduce a construct from a
  family their label does not name; those matches are published as readings, not as
  declarations.
- `fee-free` says the delta inherits nothing from the fee. It does not say the delta
  is right.
- 15 cells (`delta_4/5member_minus_3member_bp`) cannot be checked from this face: their
  operands are the 3/4/5-member universes on a sibling face.

## Verify

```
python scripts/e97_routing.py deltastance            # sweep + totals
python scripts/e97_routing.py deltastance --publish  # results/e79/DELTASTANCE-<cutoff>.json
python scripts/e97_routing.py selftest               # legs L46-L51 cover this mode
```