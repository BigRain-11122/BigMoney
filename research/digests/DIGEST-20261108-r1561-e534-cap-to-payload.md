# DIGEST 2026-11-08 r1561 bm-b -- E534: does a depth-cap null reach a payload as absence?

Face: `results/state_tilt/CAPTOPAYLOAD-2026-11-08.json` (+ `captopayload_latest.json`)
Runner: `scripts/e534_cap_to_payload.py` (run / check / verify / selftest)
Upstream: `results/state_tilt/depthcapnull_latest.json` (E529, sha pinned in the face)

## Question

E529 published 12 depth-cap arms that return a null sentinel; 8 had readers that never test the
value and 2 tested it against the same null, so no reader could separate "the recursion hit its
cap" from "the thing is not there". A call-site reading is not a publication, though: a value that
is dropped, or only feeds a local branch, never becomes a fact. This study follows each of the 10
arms in those two classes out of its reader.

## Method

Per arm, take the call sites E529 attributed to it (same module, or a module that imports its stem;
recursive self-calls excluded), locate the `Call` by `module:line`, then follow the value:

* a bound value is followed by NAME inside the reader and the walk STOPS at a later rebinding of
  that name (a load of the rebound value is a different value);
* terminal classes: named field of a dict literal (key published), body of a `json.dump`/`write`
  argument (no key names it), counted quantity (`len`/`sum`/`any`/`all`), sentence (f-string, `%`,
  string concat, `.format`), handed to another call or returned, discarded, bound and never read,
  tested narrowly, stops elsewhere;
* a field only counts as a publication when the same reader function contains a write call
  (`dump`/`dumps`/`write`/`writelines`/`write_face`); otherwise it is "assembled, never written".

## Readings

| quantity | value |
|---|---|
| arms in population | 10 (8 `reads_the_sentinel_without_testing_it` + 2 `tests_against_the_same_null`) |
| call sites followed | 20 |
| sources read / parse failures | 2,754 / 1 |
| arms reaching a written payload field | **0** |
| arms reaching a payload body | 0 |
| arms reaching a count | 0 |
| arms reaching a sentence | 0 |
| arms carried into a field nobody writes | 1 (`e503_chain_stale._eval`, key `text`) |
| arms whose value leaves by a call | 3 (`e379._resolve` x2 sites, `e398._resolve_chain_text`) |
| arms that stop inside the reader | 6 (3 discarded, 3 narrow test) |
| arms unresolved | 0 |

Verdict (recomputed by the gate from the summary):
`cap_nulls_reach_named_fields_but_no_reader_in_the_population_writes_a_payload`.

## The disagreement with E529, published rather than absorbed

This scan finds a narrow test in 4 arms, and **2 of them E529 published as "never tests"**:
`scripts/e344_face_consumer_census.py::string_values` (line 172: `values = ...` then
`if not values: continue`) and `scripts/e390_wrong_side_reader.py::binding_exprs`.

Root cause, nameable: E529's sentinel-test rule only recognised an `ast.Compare` against a null
literal. `if not values:` is `UnaryOp(Not, Name)` and `if values:` is a bare `Name` test -- neither
is a `Compare`. So the "no reader tests it" class over-counts. The face publishes
`arms_e529_published_as_never_tested_that_do_test` and the gate re-derives that list.

Note the arm-level reading is undivided by this: `e344.string_values` has three sites, one of which
(172) tests and two of which (252, 255) genuinely stop inside; the arm is published under the
narrow-test class because the precedence is documented in `_PRIMARY`, and the per-site counts are
published beside it.

## Pits worth keeping

1. **"read without a guard" is not "published as a fact".** Two separate measurements: read ->
   terminal class, then field x (does the reader write at all). Collapsing them makes a dropped
   binding look like an entry in a face.
2. **A name-level walk must stop at a rebinding.** The first draft followed every load of the
   bound name in the reader; a later `x = something_else` makes those loads unrelated to the
   sentinel.
3. **A test predicate that only knows one AST shape misses a whole class.** `Compare` is one of
   five falsy tests (`not x`, `if x`, `bool(x)`, `x or default`). E529's over-count is exactly this.
4. **Publish the empty bucket.** Zero arms reach a written payload here; loosening the rule until
   something did would have published `text` -- a field nobody writes -- as a publication.

## Not run / not claimed

Full smoke suite (~20-30 min), the rest of the S6 chain, the collector family and the
market/paper legs were not run this window and are not claimed. Attrition CLEAN (4 ledgers),
dualrun ZERO-DRIFT (1,007 entries, streak 40), orphan faces 0, orders 114 files / 115 acks / 0
unacked.
