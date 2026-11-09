# DIGEST 2026-11-10 r1658 bm-b -- E638: the two rulers on one expression, counted tree-wide

**Card** E638 `how many (line, column) sites carry two Subscripts at different depths`. Face
`results/state_tilt/TWODEPTHSUBS.json`. Script `scripts/e638_two_depth_subscripts.py`
(selftest 12/12, check/verify `problems=[]`).

## What was asked

E637 settled the fold on its own population but left a *definition* gap it named in one line: a
chained expression is two AST nodes in one place, so E633's depth fold and E636's "read one level
below the receiver" can describe the same text. E638 turns that sentence into a census: how often
does the form occur, and on the counted lines which member does each ruler count?

## What was measured

Corpus = E391's Python walk (13,076 files), minus this study's own files matched by basename prefix.

| reading | value |
| --- | --- |
| Python files scanned | 13,076 |
| over the 1MB cap / unreadable / does not parse | 4 / 0 / 304 |
| Subscript nodes in the corpus | 415,722 |
| **(line, column) sites with two Subscripts at different depths** | **45,391** |
| files carrying at least one such site | 4,365 |
| depth pairs 1->2 / 1->3 / 2->3 / 2->4 | 34,113 / 8,584 / 714 / 1,050 |
| E633 counted read lines | 13 |
| of those, carrying a two-depth site | 6 |
| sites whose deepest member names the row's counted key | **0** |
| sites E633 folds as `read_below_the_receiver` | 6 |
| sites E633 counts as a recognised read | 0 |

On the counted lines every site is a 1->3 pair: the intermediate member is the receiver's own key
read, the deepest member names `cutoff`, `eq_s`, or nothing.

## Verdict

`the_two_depth_form_is_ordinary_in_the_corpus_and_on_the_counted_lines_E633_folds_the_deepest_member_every_time_while_none_of_those_members_names_the_row's_counted_key,_so_the_fold_removes_no_same_key_read_and_the_line_level_coincidence_E637_reported_is_not_a_column_level_double_count`

The form is ordinary -- one in three files carries it -- so the depth argument is not about an edge
case. And on the population that E632/E633 count, the deepest member never names the row's key: the
fold removes no same-key read, and E637's "4 locations where both instruments count" is line-level
coexistence, not a column-level double count.

## Pits recorded

1. **One number under two names.** The first build published `python_files_unreadable = 308` and
   `python_files_over_the_size_cap = 308` from the same counter. Split, the holes are 4 (size cap),
   0 (unreadable), 304 (do not parse): a mechanical skip had been published as data damage.
2. **A census that does not exclude its own scratch files moves with its neighbours.** Excluding by a
   fixed filename list left two `_probe_*` files inside the walk and the site count moved
   45,391 -> 45,393 between two runs. Exclusion is now by basename prefix.
3. **`depth_2_member` was the wrong name for what the code matched.** The join matches
   `depth == max_depth`, but the counted-line sites are 1->3 pairs, so "depth 2" described nothing.
   Renamed to `deepest_member` everywhere (face fields, counts, verdict, smoke leg) before publishing;
   the misnomer was caught only by printing the real depth pairs.

## Delivery

Branch `machine/bm-b-r1658` (main is ~13 ahead / 14 behind on this promisor clone -- r1243 keeps
unattended rebases off). Smoke leg `E638` in `smoke_test.py`, S6 leg `two_depth_subscripts` in
`Tools/s6_chain_bmb.py`, pool E638 done + E639 seeded.
