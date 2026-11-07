# E519 — where does a call-site argument that is a local of the caller come from

- round: r1545 (bm-b), 2026-11-08
- card: `E519-WHERE-DOES-THE-183-LOCAL-ARGUMENTS-THAT-CALLERS-PASS-ACTUALLY-COME-FROM`
- instrument: `scripts/e519_local_arg_origin.py` (build / check / verify / selftest)
- face: `results/state_tilt/LOCALARGORIGIN-2026-11-08.json` + `localargorigin_latest.json`
- smoke leg: `# E519` in `smoke_test.py`, standalone proof `scripts/run_e519_smoke_leg.py` (+ `--doctor`)

## Why

E516 published that 48 of 58 local-carried bindings are never handed a real population by a
caller, and that 183 of the 248 call-site arguments it read are themselves a local of the calling
function. "A local" is the same question one level up: the caller built it in its own body. Without
that hop, "readable only through the local" cannot be distinguished from "a published population
two hops away".

## How

Population is machine-read from E516's LOCALCARRIER face: every call site whose argument_kind is
`a_local_bound_in_the_calling_function` (183, asserted equal to E516's own published count so the
two faces cannot drift). For each, the innermost function containing the call line is located
(nested defs skipped), and the right-hand side of the statement that binds the name is classified
into twelve arms — literal container, literal value, caller module constant, attribute on an
imported module, another in-repo module call, an out-of-repo module call, a method on a value the
caller already holds, the caller's own module call, a file or directory read, a comprehension, a
parameter of the caller itself, computed in the caller — plus an unresolved arm.

## Numbers

| arm | bindings |
| --- | --- |
| built inside the caller | 44 (container 9, own-module call 15, method on a held value 7, comprehension 6, computed 7) |
| population lives elsewhere | 5 (all another in-repo module: e341 / e350 / e468) |
| a parameter of the caller itself | 7 (git_names, index, root, rows, sources, store) |
| no binding in the caller | 5 |

183 arguments over 61 bindings, 37 distinct names, 46 calling functions. Five bindings (carrying
61 of the 183 sites) are assigned by more than one statement, so their published origin is the last
assignment the parser saw.

Verdict: `some_local_arguments_are_a_published_population_two_hops_away_..._so_local_only_has_to_be_read_row_by_row`.

## Lessons worth reusing

1. A parameter is not a local. Seven arguments "built inside the caller" are really forwarded; the
   population is one hop further up. Published as its own arm so the headline cannot absorb them.
2. A name is not a module (E206/E207 family, third occurrence). The first build published 15 rows as
   "a call into another in-repo module" because receivers `payloads` / `src` were not checked
   against the caller's import aliases; requiring the receiver to be an alias cut 15 → 5 and moved
   10 to "a method on a value the caller already holds".
3. Publish the assignment count next to the origin. Five bindings carry 61 sites; without the count
   a reader takes 61 sites as one determinate answer.
4. A gate must be finer than the aggregate: `verify` originally compared only summary/answers/verdict
   and let a tampered row pass. Row-level comparison was added, and the selftest leg that used to be
   falsely green turned red on the tampered row.
5. Arm completeness belongs in the gate: `sum(origin_counts.values()) == row count` survives adding
   arms, unlike a hand-written four-bucket sum.