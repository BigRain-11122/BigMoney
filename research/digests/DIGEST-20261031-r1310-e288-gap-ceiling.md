# DIGEST 2026-10-31 r1310 bm-b -- E288: the inter-range gap is not the whole unresolvable set

Pool card `E285-INTERRANGE-GAP-CEILING` (pool E285 -> methodology card E288).
Runner `scripts/e285_interrange_gap_ceiling.py` (selftest 23/23, run/verify green),
face `results/state_tilt/BANDGAPCEILING-2026-10-29.json` (+ `bandgapceiling_latest.json`),
S6 leg `interrange_gap_ceiling` (verify, 0.17s), smoke leg
`product: the inter-range gap is a smaller widening target than the area beyond the published ceiling -- both must be counted, not added`.

## What was asked

E282 showed the two tails disagree because their RANGES differ, not because of a rounding tie. E283
showed a degenerate tail can only reach a row when the flip equals its single multiplier. Neither
had measured the space BETWEEN the two published ranges: a flip landing in that gap is reachable by
NEITHER tail, so widening is the only instrument that could ever pick it up. The question a reader
needs answered: how much of the unresolvable set does that gap actually account for, and where does
the family's published headroom run out?

## What was measured (source: E272's `BANDFLIPBUDGET-2026-10-29`, 4 arms / 12 rows)

| class | rows | detail |
|---|---|---|
| reachable_tight | 0 | no row's flip lands in a tight interval |
| reachable_wide | 2 | cross\|60\|9 2.1965, star_lag1_residual\|60\|13 2.1384 |
| **in_gap** | **2** | cross\|60\|11 flip 1.8030; star_lag1_residual\|60\|15 flip 1.8843 |
| **above_ceiling** | **6** | up to 3.2544 = **1.417x** the family's published p95 ceiling 2.2963 |
| below_floor | 2 | self\|60\|8 0.8894, self\|60\|10 0.6304 (floor 1.0) |

Unresolvable = 10 rows: **20 pct in the gap, 60 pct above the published ceiling, 20 pct below the
floor**. Any widening that stays inside the evidence this family published can add **at most the 2
gap rows**; the other 6 would need a multiplier range that no face here ever published.

Gap widths, priced in each tail's own spread (the only ruler the family publishes):

| arm | gap | in tight spreads | in wide spreads |
|---|---|---|---|
| cross:200 | 0.5255 | n/a (tight is degenerate, spread 0) | 2.05x |
| cross:60 | 0.8670 | 8.60x | 2.64x |
| self:200 | 0.5068 | 7.37x | 3.54x |
| self:60 | 0.8816 | 9.09x | 4.58x |

So covering a gap costs 2-5 wide-tail spreads -- the gap is wider than the wide tail it must
approach. Per gap row the required relative moves are asymmetric and published: to reach
cross|60|11 the wide floor must drop 8.37 pct (or the tight ceiling rise 38.94 pct); for
star_lag1_residual|60|15 it is 4.24 pct / 41.58 pct.

## Verdict

`the_gap_holds_fewer_rows_than_the_area_beyond_the_published_ceiling`. The substitution's widening
headroom is not the dominant unresolvable mass; the extrapolation zone above the published ceiling
is 3x larger than it (6 vs 2 rows), and no widening inside the published evidence touches it.

## Identity (why the counts are believable)

- rows censused 12 == source `rows_measured` 12; reachable wide 2 / tight 0 == source
  `rows_reachable_wide` 2 / `rows_reachable_tight` 0.
- each row takes exactly one class and the classes sum to the rows censused (asserted per arm).
- every gap row is published unreachable by BOTH tails on its own face and sits inside a POSITIVE
  gap on its own arm (asserted, not inferred).

## Pits recorded

1. **A selftest leg that cannot fail is a decoration.** My first version of the ceiling leg read
   `... is not None or True` -- always green, exercising nothing. Deleted; the flagging behaviour
   (an arm whose wide ceiling exceeds the family's) is now pinned by a real assertion. Count legs
   by what they can catch, not by how many there are.
2. **The family's ruler is not always available.** cross:200's tight tail is degenerate (spread 0),
   so the gap cannot be priced in tight spreads there. `_ratio` returns None on a zero spread and
   the face publishes null -- dividing by the spread would have invented an infinity exactly on the
   arm whose tight tail E283 already flagged as degenerate.
3. **Different instruments, same-looking rows.** "above_ceiling" and "in_gap" are both
   "unreachable at publication"; they differ in whether any published widening could help. Adding
   them (8 of 12) would answer a different question than the card asked, so the face publishes them
   as separate blocks and the summary keeps `share_of_unresolvable_in_gap` distinct from
   `share_above_ceiling`.

## Next

Pool `E286-COUNT-FIELD-SCOPE` (1338 integer count fields left unjudged by E287's sweep/family check).
New seeded cards: `E287-ABOVE-CEILING-CROSS-FACE` (is the ceiling family-wide or only this face's?)
and `E288-BELOW-FLOOR-NARROWING` (the 2 below-floor rows need a narrower range, not a wider one).