# DIGEST 2026-10-31 r1311 bm-b -- E289: a unit word in a count's name is checkable only in its own scope

Pool card `E286-COUNT-FIELD-SCOPE` (pool E286 -> methodology card E289).
Runner `scripts/e286_count_field_scope.py` (selftest 24/24, run/verify green),
face `results/state_tilt/BANDCOUNTSCOPE-2026-10-29.json` (+ `bandcountscope_latest.json`),
S6 leg `count_field_scope` (verify, <1s), smoke leg
`product: a unit-named count is checkable only inside its own scope -- and the share that is
checkable must be reported, not assumed whole`.

## What was asked

E284 swept the dated BAND family for label-scope slips and then had to leave 1338 integer fields
unjudged, because "an integer count's scope depends on that face's own census semantics; guessing it
here would publish a number this face did not measure". That is the same defect class one level
down: a count whose name says rows may be counting cells, arms or draws, and nothing on the face
says which. E286 asks the only answerable version of the question -- which of those counts can be
re-derived from the face's OWN published records, and do those agree with the unit their name claims.

## What was measured (32 dated BAND faces, mirrors and self faces excluded, published records only)

| bucket | fields | why it is its own bucket |
|---|---|---|
| unit-named integer fields | **894** | integer values (bools filtered out) whose key names a unit |
| re-derivable in its own scope | **27 (3.0 pct)** | a sibling list keyed exactly the claimed unit |
| ... of which agrees with the name | **27** | no slip in the checkable set |
| ... of which disagrees | **0** | -- |
| cannot check: unit published elsewhere | **301** | the face has that unit, the COUNT lacks the scope |
| cannot check: unit never published | **566** | the name is a design parameter (draw/seed budget) |
| subset-named counts, not judged | **557** | `rows_where_tails_disagree`, `arms_mismatched` ... (E208) |

Per key (top 10; full table on the face):

| key | unit | occurrences | re-derivable | cannot | why |
|---|---|---|---|---|---|
| draws | draws | 253 | 0 | 253 | never_published 253 |
| n_faces | faces | 149 | 0 | 149 | elsewhere 149 |
| n_rows | rows | 122 | 18 | 104 | elsewhere 104 |
| n_records | records | 115 | 0 | 115 | never_published 115 |
| n_seeds | seeds | 96 | 0 | 96 | never_published 96 |
| seeds | seeds | 56 | 0 | 56 | never_published 56 |
| n_cells | cells | 49 | 8 | 41 | never_published 17 / elsewhere 24 |
| rows | rows | 21 | 0 | 21 | elsewhere 13 / never_published 8 |
| records | records | 19 | 0 | 19 | never_published 19 |
| arms | arms | 11 | 0 | 11 | elsewhere 11 |

Five faces publish at least one checkable count; twenty contain no count that can be checked at all.

## Verdict

`the_checkable_share_of_unit_named_counts_is_a_minority_and_every_one_agrees` -- the name is a
checkable claim for 3 pct of unit-named counts, and where it can be checked it is correct. The
honest headline is therefore not "the counts are right" but "the counts are unauditable by their
names": 96 pct of them name a unit the face does not publish in that count's scope.

## The three rules that make the census trustworthy

1. **Strict name reading.** A key claims a unit only as bare `<unit>`, `n_<unit>`, `num_<unit>`,
   `<unit>_count`. Subset names are a different claim and are disclosed, never judged -- a naive
   unit-word match is the E208 false positive (it moved 3109 real readings in that case), and here
   it would have swept 557 fields into the census.
2. **Same scope only.** Re-derivation requires a SIBLING list keyed exactly the unit. A face-wide
   search publishes slips that do not exist: `BANDTRANSFER` publishes `flat.cross:200.n_rows = 2`
   beside one unrelated 16-row `rows` list, and a face-wide lookup reads that as a 2-vs-16
   disagreement. Booleans are filtered before classification (Python `bool` is an `int`).
3. **Publish the share.** "Every checkable count agrees" and "the name is a checkable claim" are
   different sentences; only the first is true at 3 pct, so the share and the two halves of
   cannot-check are both on the face and both re-derived by the smoke leg.

## Identity that makes the numbers believable

re-derivable + cannot == the field census (894); the two halves of cannot-check sum to 867; the
per-key occurrences sum back to 894 and the per-key re-derivable counts sum to 27; no boolean reached
the census; the census universe is a superset of E284's 30-face scope (two faces added, zero dropped: E284 excluded its own face, which is a sibling here, plus
E285's `BANDGAPCEILING-2026-10-29`) and contains neither this face nor its
mirror.

## What this changes downstream

- Any face that publishes a unit-named count should also publish the records in that count's scope,
  or drop the unit word: otherwise the count can only be believed, not checked.
- E285's "unreachable is not one thing" gets its sibling here: "unchecked is not one thing either" --
  301 scope-fix items and 566 missing-record-face items are not the same work item.