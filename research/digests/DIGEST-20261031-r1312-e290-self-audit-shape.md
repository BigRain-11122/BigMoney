# E290 - the self-auditable shape, and why copying it still leaves five of six counts un-auditable

**Round** r1312 (bm-b) · **evidate_cutoff** 2026-10-29 · **card** E290 · **pool** E290-SELF-AUDITABLE-FACE-PROFILE

## The question E286 could not answer

E286 established the date: 894 unit-named integer counts across 32 dated BAND faces, 27 of them
(3.0 pct) re-derivable from the records their name points at, and all 27 counting the unit they claim.
The follow-up a face author needs is not "how many" but "if I publish like those faces do, will MY
count be checkable?" That is a question about shape, and it re-reads published faces only -- no draw,
no band rebuild, no engine.

## Three parts of the shape, and the part that fails

| feature | measurement |
| --- | --- |
| count sits beside a list of exactly the claimed unit, in the SAME parent dict | 27 of 27 (100.0 pct) |
| the count equals that list's length | 27 of 27 |
| no OTHER list of the same unit in the same face has that length | **15 of 27**; 12 are ambiguous |
| records are dicts (one record per row, carries its own unit) | 19 of 27; 8 sit beside scalars |

The ambiguity is not hypothetical. `BANDFLIPBUDGET` publishes eight `tail_budget.*.n_cells` beside a
`cells` list, and `BANDGAPCEILING` publishes `arms[*].n_rows` / `beyond_ceiling.n_rows` /
`below_floor.n_rows` beside a `rows` list -- in each case a count agrees with its own list and also
with a rival length available elsewhere in the same face, so the agreement cannot be told from a
coincidence of size. Co-location is not evidence; agreement plus the absence of an equal-length rival
is the whole test.

## The pattern's own coverage is the number that matters

| scope | checkable | unit-named counts | share |
| --- | --- | --- | --- |
| the 5 exemplar faces | 27 | 151 | **17.9 pct** |
| whole family | 27 | 894 | 3.0 pct |

`BANDDONORCHOICE` is 4 of 4 and `BANDGAPCEILING` 6 of 6, but `BANDARRIVAL` is 1 of 47 and `BANDTIGHT`
4 of 57. "Publish the way these faces do" multiplies your odds about sixfold and still leaves five of
six counts un-auditable, because those faces also publish plenty of counts with no records in scope.
Any recommendation that quotes the exemplars must publish their own rate first.

## The un-derivable majority is two jobs

| half | rows | distinct targets | fix |
| --- | --- | --- | --- |
| unit published elsewhere in the same face | 301 | 299 scopes | move the count into that scope / name the scope it counts |
| unit never published at all | 566 | 8 keys (draws 253, n_records 115, n_seeds 96, seeds 56, ...) | needs a record face; no naming convention can rescue it |

Adding the halves into one "unchecked" number tells a reader to fix the wrong thing.

## Pits taken in-window

1. **Self-inclusion, third sighting.** The study's own face is named `BANDSELFAUDIT-*`, so on the second
   run it entered the `BAND*` universe it censuses: `unit_named_counts` moved and `verify` went red on
   two keys. E286 excludes its own faces; a consumer that names its sibling's universe must filter its
   own face too. Fixed by filtering `SELF_FACES` in `build()`.
2. **Two fixture legs were wrong, not the code.** The first selftest expected the fixture's checkable set
   to be two `n_rows` (it also contains `n_cells` and `n_seeds`, each with a same-parent list), and
   expected `arms[0].n_rows` to be unambiguous (its rival is `summary.rows`, length 2, same face). Both
   assertions were narrowed to what the code actually promises.

## Verification

* `python scripts/e290_selfauditable_face_profile.py selftest` -> **15/15**
* `run` then `verify` -> **0 problem(s)**; decisive values re-derive twice
* S6 leg `self_auditable_face_profile` -> **rc=0, 0.29s**
* smoke leg `product: a count is self-auditable only when its own records share its scope` -> PASS
  (verified standalone by exec-ing the leg's own source out of `smoke_test.py`)
* identity: checkable rows join E286's `n_re_derivable` (27 = 27), record-type partition sums, every
  published row carries its sibling in scope, exemplar face set equals the row set