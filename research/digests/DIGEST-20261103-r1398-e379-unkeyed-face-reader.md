# DIGEST r1398 (bm-b) -- E379: unkeyed is not unread, and one upstream row was wrong

Source: `results/state_tilt/UNKEYEDREADER-2026-11-03.json` (evidence_cutoff 2026-11-03).
Producer: `scripts/e379_unkeyed_face_reader.py` (selftest 17/17, verify 0 problems).

## What was asked

E377 (r1396) published 36 published faces that an unnameable `json.dump` destination can reach and that
no resolved sink in the corpus keys. "Unkeyed by the census" and "unread" are different claims. E379
resolves the reader forms the census cannot name and splits the 36 four ways.

## Readings

Corpus 2,413 sources / 2,395 parsed; 15,174 load calls of which 12,544 resolve; 1,115 resolve only
through the two forms the binding census cannot see (expression-position `json.load(open(P))`, ROOT
joined / pathlib division).

| bucket | faces |
|---|---|
| read at a resolved site | 2 |
| read only at a site the binding census cannot see | 3 |
| only named inside a loading function that loads something | 22 |
| unread | 9 |

## The finding that changed the verdict

The taxonomy defines `read_at_a_resolved_site` as "the census's own universe -- a contradiction if it
appears". It appeared:

* `results/etf_book_production/latest.json` -- assigned load, `joined_constants`,
  `scripts/etf_book_bridge.py:369 run`. This is **inside** the census universe, so E377's "no resolved sink
  keys it" is false for this face. Published as the verdict
  `some_unkeyed_faces_are_read_at_a_site_the_census_itself_resolves_so_the_upstream_claim_..._is_false_...`
  Asking which side is wrong is seeded as E381 rather than answered by decree here.
* `results/runnable_pool.bm-a.json` -- a **literal in expression position**
  (`Tools/_r603bma_wedge_rootfix.py:93`). A binding census cannot see an unassigned load by design, so
  this is the blind spot, not a contradiction.

## Defect caught in the first draft (in-window)

The first build counted census-universe *forms* without testing `assigned`, and reported 2 contradictions.
A literal nobody binds is invisible to a binding census on purpose, so that count invented a defect in
another instrument. The predicate now requires `assigned AND why in {literal, bound_constant,
joined_constants}`; the count fell 2 -> 1 and only the owner of the verdict changed.

## Bound

Static name test only: nothing executed, no corpus source imported, zero network. A reader that computes
its path at run time stays invisible. `named_inside_the_loading_function` is reach, not consumption. The
population is read from E377's published face (read_as_published=True), so a stale upstream narrows the
study. Basename fallback can merge two same-named files.

## Pool

E379 closed with result_ref; E381 seeded ready (cpu-only):
`E381-WHY-DOES-THE-UPSTREAM-READER-CENSUS-MISS-A-LITERAL-READ`.
