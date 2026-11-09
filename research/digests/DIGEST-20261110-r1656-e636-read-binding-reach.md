# DIGEST 2026-11-10 r1656 bm-b -- E636: reachability, not union, and the reads the census folds out

**Card** E636 `whether a computed-key read resolves once binding reachability decides which binding
reaches it`. Face `results/state_tilt/READBINDINGREACH.json`. Script `scripts/e636_read_binding_reach.py`
(selftest 20/20, run/verify `problems=[]`).

## What was asked

E635 resolved the 12 computed-key reads E634 found and left 6 unresolved, all of them in
`scripts/ew6_portfolio.py::write_outputs` and all of them bound by a `for` target. E635's resolver
unioned every binding of the name in the scope, so a second, non-literal loop over the same name
poisoned the first, literal one. Unioning is a property of the instrument.

## What was measured

| reading | value |
| --- | --- |
| rows re-decided | 12 |
| rows that change class vs E635 | 1 (line 392, proven along the iteration that binds `x1`, 1 of 2) |
| unresolved after the change | 6 (all of them reads of `tid`, the member id) |
| after-side proven / could / other / unresolved | 0 / 0 / 1 / 5 |
| after-side unresolved locations that DO read `x1` one level below the receiver | 4 of 5 |
| enumerated iterations carrying the key | 1 of 2 |

## Verdict

`the_after_side_stays_unresolved_and_at_least_one_of_those_locations_carries_no_read_of_the_counted_key_below_the_receiver`

E634/E635's "0 reads of the key after the dead line" survives **as a statement about the census**, and
part of the reason it holds is that the reads which do name the key at those locations were never in
the census: `sleeves[tid]["x1"]` is classified `read_below_the_receiver` and folded out. One of the
five after-side locations (line 441) genuinely reads `x2`/a computed key below, not `x1`.

## Pits recorded

1. Union is not reachability. A single non-literal sibling binding decides the whole row.
2. A chained subscript puts two read sites on one `(line, column)`; neither E634 nor E635 could tell
   them apart by that signature. Both are resolved now and the tie-break is published
   (`sites_at_this_location`, `key_expressions_at_this_location`).
3. "Unresolved" and "another key" are different classes. Folding the 5 unresolved rows into "another
   key" would have made the zero stronger than it is; the gate now separates them and four selftest
   legs pin the four verdict branches.
4. My own first fixture put the read **after** the loop, so reachability correctly said
   "no binding reaches it" and three legs failed for the right reason. The fixture was wrong, not the
   instrument -- a leg that cannot fail is worse than a leg that fails.

## Successor

**E637** -- do the `below_the_receiver` reads at those four locations name the counted key on a
published path, i.e. exactly how much of the after-side read set the census folded out.
