# DIGEST 2026-11-10 r1657 bm-b -- E637: pricing the below-the-receiver fold on both populations

**Card** E637 `what E633's "read below the receiver" fold actually removes`. Face
`results/state_tilt/BELOWFOLDPRICE.json`. Script `scripts/e637_below_fold_price.py` (selftest 10/10,
run/verify `problems=[]`).

## What was asked

E636 published a sentence about E633: 4 of its 5 after-side unresolved locations *do* read the counted
key, one level below the receiver, "where E633's classifier folds the read out of the census instead
of counting it". Read as written, that is a population limit of E633 -- reads of the counted key that
never entered the same-key count.

## What was measured

Both populations were re-derived from the tree (`e633.measure`, `e636.measure`; neither published face
was written) and joined on `(module, read line)`.

| reading | value |
| --- | --- |
| E633 counted read lines | 13 |
| folded-out (`read_below_the_receiver`) accesses | 9, across 7 lines |
| by depth | 2 x3 / 3 x6 |
| with a literal inner key | 3 (`cutoff`, `eq_s`) |
| with no inner key | 6 |
| **naming the counted key of its own row** | **0** |
| E633 lines also in E636's population | 5 |
| E636 locations reporting the counted key below the receiver | 4 |
| of those, where E633 also counts a recognised read of that key | **4** |
| of those, where E633 counts nothing | 0 |

## Verdict

`the_fold_removes_N_accesses_and_none_of_them_names_the_counted_key_of_its_own_row_so_it_hides_no_read;_but_K_of_the_locations_E636_reports_as_reading_the_counted_key_below_the_receiver_are_the_same_locations_where_E633_counts_a_recognised_read,_so_the_two_instruments_draw_the_boundary_at_different_depths_and_neither_lost_a_read`

E633's fold is free at its own population: nothing it removed names the counted key of the row it
belongs to. And the 4 locations E636 named are exactly the 4 where E633 already counts the key at
depth 2 as a recognised read -- the read was never folded out, it was labelled by a different ruler.

## Pits recorded

1. One word, two rulers. E633's "below the receiver" is `depth > 1` relative to the receiver root, so
   `sleeves[tid]["x1"]`'s `x1` sits at depth 2 and is counted; E636's "below" is *the other Subscripts
   at the same (line, column)*, so the same `x1` also appears in its below list. Quoting an upstream
   "it folds that out" without re-reading the upstream's own population produced a limit claim that
   the upstream's own rows contradict.
2. "A folded-out read" and "no read of the key" are different sentences. The only admissible test is
   the row's own counted key, published per row as `names_the_counted_key`; inferring from "has an
   inner key" would have been a proxy for the measurement.
3. Two populations join on `(module, read line)` and the join count must be published
   (`e636_rows_at_this_line`): equal totals are not evidence of the same population (E366 family).

## Successor

**E638** -- the same question one turn out: E636's `# the same (line, column) can also carry a read
the classifier shelves as "below the receiver"` is a claim about *coincidence of columns*, not about
depth. Census, across the tree, how many `(line, column)` signatures carry two Subscripts at different
depths, so the two instruments' boundaries can be stated as a difference of definitions on a measured
count instead of on one example.