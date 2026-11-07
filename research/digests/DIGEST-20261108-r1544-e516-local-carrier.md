# DIGEST-20261108-r1544-e516-local-carrier

**Study**: E516 -- which function local that E508 called a module constant is the only carrier
of a population. Card: `knowledge/METHODOLOGY_ASSETS.md` E516. Face:
`results/state_tilt/LOCALCARRIER-2026-11-08.json` (+ `localcarrier_latest.json`).
Tool: `scripts/e516_local_carrier.py` (build / check / verify / selftest).

## What was asked

E513 published 58 of 84 "module constant" bindings as locals of the calling function (80 of 123
sites). A local is not a published population -- but it is not automatically unreadable either:
if some *other* call site of the same surface hands the parameter a literal container or a
module-scope constant, a reader can reconstruct the population from the call site. This study
measures that, per binding, over all call sites.

## Readings

| measure | value |
|---|---|
| local-carried bindings / sites / surfaces | 58 / 80 / 23 (matches E513 exactly) |
| call sites read | 248 |
| arguments that are a local of the caller | 183 |
| arguments computed at the call site | 26 |
| arguments that are a caller module constant | 21 |
| literal containers written at the call site | 18 |
| omitted arguments (default stands) | 0 |
| call results passed directly | 0 |
| readable from a call site | **10** |
| readable only through the local | **48** |
| only a parameter default | 0 (structurally empty) |
| never called at all | 0 (structurally empty) |
| locals built by a call into another module | 11 (4 dependency modules) |
| locals built by a method call on a value | 10 |

Verdict: `some_local_carried_bindings_are_still_fed_a_real_population_by_a_caller_and_some_are_
not_so_the_headline_has_to_be_read_row_by_row`.

## Why two arms are empty

`never_supplied` cannot occur: the binding exists *because* E508 recorded a call site, so the
call-site count is at least one by construction. `supplied_only_by_the_default` requires every
call site to omit the parameter -- including the one E508 recorded as passing a constant. Both
arms stay in the vocabulary so that a future read can tell "empty because impossible" from
"empty because nobody looked", and the face publishes them as 0 with that explanation.

## Correction this round made

E513's "built by code" bucket mixes two things. `payloads.get(rel)` and `src.get(...)` are method
calls on a value the caller already holds -- no module is involved. After requiring the receiver
to be an import alias before calling it "another module", the cross-module count fell from 21 to
11 and the other 10 moved to their own counter. Same rows, half the count: name is not module
(E206/E207 family).

## What this does not answer

Whether a caller's expression covers every branch (a guard) is not measured here; and an
argument that is a name counts as a population only when it is bound at module scope of the
surface's own module. That second gap is exactly what E519 asks next.
