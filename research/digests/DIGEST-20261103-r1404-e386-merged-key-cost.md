# r1404 / E386 -- a merged key costs the trial-labor family a schema, not a number a reader reads

Date: 2026-11-03 11:56 +08:00. Node: bm-b. Study: E386_merged_key_cost.
Face: `results/state_tilt/MERGEDCOST-2026-11-03.json` (+ `mergedcost_latest.json`,
`mergedcost_crossread.csv`). Card: `knowledge/METHODOLOGY_ASSETS.md` E386.

## Why this study

E383 (`results/state_tilt/COLLISIONKEY-2026-11-03.json`) published the collision count: 878 keys, 24
with more than one value, 3 merging 40 identified files, `prep_state.json` naming 20 and
`judge_state.json` 18. A file count is not a bill. The pool card E386 (seeded by r1402) asked for the
cost inside the family where the merge is widest: `results/trial_labor_w*/`.

## What was measured

| Question | How |
| --- | --- |
| What would the merge lose? | field census per top-level field: distinct values across members, split constant / one-value-per-member / varies |
| Does one key hold one shape? | distinct top-level key sets per basename ("schema variants") |
| What numbers are there? | cross-read CSV of the answer-bearing scalars per member, `present`/`absent` published, never dropped |
| Who actually reads it? | AST census of every string literal equal to a merged basename in the in-repo `.py` corpus, classified by the expression it is joined to |

Reader classes (frozen): `wave_expr`, `wave_scoped_constant`, `constant_dir_unresolved`, `bare_key`,
`label_beside_a_path`, `file_name_list`, `key_lookup`, `comment_or_self`.

## Readings

* 22 wave directories, 2 merged keys, 39 members, 53 fields measured.
* **2 of 2 keys carry more than one schema** -- 31 distinct key sets total: `judge_state.json`
  15 variants (8..21 fields), `prep_state.json` 16 variants (6..24 fields). Each wave accreted fields.
* `n_survivors` is absent from **5 of 19** `judge_state.json` members (W1's old prep shape;
  W17/W18/W19/W21 carry the block shape with `blocks`/`cap`); `n_distinct` absent from **6 of 20**
  `prep_state.json` members. Where present, `n_survivors` takes 14 distinct values (40..513).
* Reader census: 134 literal sites in 34 files. **0 read the basename bare.** 60 name their wave
  (56 wave-scoped constant, 4 wave expression), 57 carry a display label beside the path, 7 iterate
  a file-name list inside their own wave script, 1 is E383's own keying dict.
* Verdict (re-derived): `the_members_of_one_key_do_not_share_a_schema_so_the_merge_hides_a_shape_change_even_though_every_reader_names_its_wave`.

## Pits

1. **The wave token excluded underscore as a separator.** `(?:^|[^A-Za-z0-9_])w\d+` does not match
   `results/trial_labor_w11`, so 62 wave-scoped constants were published as unresolved joins.
   Widening to `[^A-Za-z0-9]` moved them to `wave_scoped_constant`.
2. **A literal beside a path is a label, not a read.** `("PREP_FILE", "prep_state.json")` names the
   file read through `PREP_FILE`. Without the tuple rule, 58 display labels entered the bill.
3. **`ast.get_source_segment` rebuilds the module source per call**, so resolving constants through it
   made the corpus walk quadratic: the first `run` was killed at five minutes with no output. Line
   slicing plus a substring pre-check before parsing brings the same walk to 24 s. (Same family as the
   r1403 pit where a self-perturbing census went red on a pin.)

## Wiring and verification

* `scripts/e386_merged_key_cost.py` -- `run` / `verify` (problems=[]) / `selftest` 29/29.
* `scripts/run_e386_smoke_leg.py` execs the suite leg verbatim: 1/1 PASS.
* `smoke_test.py` leg E386 refuses a verdict outside the frozen vocabulary, a schema-variant count
  that disagrees with its own size list, a presence break that disagrees with its scalar row, a
  member list that disagrees with its count, a cost row on a key whose members do not diverge, and the
  study's own verify not coming back clean.
* Pool: E386 done with `result_ref`; successors E388 (accretion vs break) and E389 (what the 18
  family-glob readers compute) seeded, ready floor 4.

## Not run this window (stated, not claimed)

Full smoke suite, S6 chain legs, `update_*` collectors, paper/scorecard faces. GPU untouched (parked,
C-20261014-01). Cloud untouched.