# DIGEST 2026-10-31 r1314 (bm-b) — duplicate lists, and the vintage freeze that turned four red legs green

Two things happened in this round and they are the same thing seen from two sides: the family's faces
copy lists, and the family's studies re-read those faces as if the directory never grew.

## 1. Four red smoke legs, one defect, and it was not a number

`python -m smoke_test` at round open: **262/269 PASS, 7 FAIL**. Four distinct legs (81, 82, 86, 87) all
read "summary does not re-derive from the published faces". Re-derived by hand they were *self*-
disagreements, not arithmetic errors:

| study | faces it published over | faces it re-derived over |
|---|---|---|
| E286 `BANDCOUNTSCOPE` | 32 | 34 (+BANDSELFAUDIT, +BANDAMBIENT) |
| E281 `BANDSUBSTITUTEAUDIT` | 27 | 34 (+7 newer studies) |
| E282 `BANDDISAGREE` | 55 | 67 (+12) |

Every study in this family censuses `results/state_tilt/BAND*.json`, and **all 69 of those faces are
study faces** — so the family's universe grows by one face each time a sibling publishes, and each new
publication silently rewrote the older face's summary. Nothing was miscomputed; the old faces simply
answered a question about a smaller directory.

The fix is a mechanism, not an assertion edit (`scripts/e_band_family_vintage.py`):

- a face re-derives against **the universe it published** — the name list stored in the face when it has
  one, its own `generated` stamp only when it does not;
- a **new run** is the only thing that widens the universe (`build(extend=True)` in `run()`; frozen default
  everywhere else);
- the freeze is **disclosed** on the face (`universe_vintage`: `faces_used`,
  `faces_in_directory_now`, `faces_excluded_as_later`, and any `faces_published_but_gone_from_disk`).

Two traps worth carrying:

1. **A stamp cutoff is not a vintage.** `BANDPATH-2026-10-30.json` was inside E286's 07:35 universe and
   was rewritten in place at 07:44. Judging by stamps drops it and leaves E286's summary two fields short
   — the name list the face already stores is exact.
2. **A face can store its universe in an unusual place.** E282 keeps all 55 names inside
   `scope_census.faces_excluded[].face` / `faces_qualifying[].face`, not in a `faces_censused` key.
   Reading the shape before assuming the key is what made that freeze exact.

Result: E286 selftest 25/25 (with 6 vintage legs folded in), E281/E282/E291/E293 `verify` 0 problems.

## 2. E293 — 135 alias pairs are 6 groups, and nothing counts them twice

The pool card asked: the 135 alias pairs E291 found — is anything reading a copy as a second record?

Measured on E286's unit-list universe (143 lists, 32 faces):

- **6 alias groups / 38 members = 26.6 % of the family's unit-named lists** are literal copies;
- **pairs recount = 135**, exactly E291's published count — a pair count and a group count are different
  numbers and only the identity leg shows they describe the same copies;
- shape is measured from the paths, not assumed: 2 groups are the same slot over sibling arms
  (`groups.cross:200.cells == groups.cross:60.cells`), **4 are scattered restatements** — a list restated
  inside a record that already carries it (`sweep.label_universe.labels` vs
  `sweep.label_universe.faces[0].labels`). Four of six copies are therefore not forced by any arm schema.
- the **strict aggregate test** (a number whose scope encloses the group, whose value equals the total
  length of *every* list of that unit in its own container, with the copies among them) returns **0
  convictions of 6**. The 11 loose matches (a number equal to the member count or one member's length)
  are published with a coincidence flag and never enter the verdict — 8 of them are ≤ 5, which matches by
  accident.

Verdict: `some_aliases_are_accidental_copies_but_no_scope_counts_one_twice`.

The honest bound: a copy that a face restates is a place where a reader could pick the stale one, but
**nothing in these faces publishes a number built by adding the copies**, so the duplication is a naming
and provenance question, not a live double count.

## 3. Carried forward

- E294 card seeded: which studies are still unfrozen, how many faces each would gain today, and whether a
  published verdict depends on the vintage it happened to see.
- Sibling pit (fifth sighting, documented in E292 card): `e286.face_universe()` excludes only E286's own
  faces; a successor must exclude its predecessors by name *and* assert the absence.