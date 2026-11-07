# DIGEST 2026-11-08 r1548 bm-b — E518: a literal return is either a declared empty answer or a silent default

## What was asked

E514 published ten literal return paths across six in-repo builders (`return None, None, None`,
`return {}`, `return (1.0, 1.0, [])`). A literal return is not one thing: `return {}` under
`if not paths:` is a declared empty answer, a container initialised to empty and filled in a loop
is a default that stands in for a read if the loop never ran, and `return 2` as a sentinel is
invisible next to a real value of 2. So the unit of measurement is the arm, not the builder.

## What was measured

Population, re-derived from the tree (not copied from the card): every module-level function in
`scripts/Tools/monitor/live/firm/engine/content` plus `smoke_test.py` that returns at least one
literal arm and at least one arm that reads a file, the git store, the tree, or an element of a
loaded structure. 2,719 parseable sources, 22 parse failures (published).

Per literal arm the face publishes: the guard on its own path (and whether that guard names the
value the arm returns), whether the arm is a container initialised empty and filled in the body,
the shape of the arm against the shapes of the builder's read arms, and a risk class the gate
re-derives instead of accepting.

## Readings

| axis | count |
| --- | --- |
| builders with a literal arm and a read arm | 1,239 (67 of them `main`/`_main`) |
| literal arms | 1,985 |
| read arms | 1,717 |
| declared by a guard that names the returned value | 942 |
| guarded only by a test on another value | 14 |
| unguarded but testable from outside | 568 |
| silent: nothing short of reading the values tells the arms apart | 475 |
| — of the silent, inside entry points (`main()` exit codes) | 73 |
| — of the silent, outside entry points | 402 |
| initialised-empty-and-filled arms | 22 |
| — of those, arms the shared trace would still call literals | 3 |

Distinguishability: `is None` 692 / truthiness-or-length 522 / same-arity unpack 54 / type 7 /
nothing 710.
Guards: `if not x` 555 / `x is None` 182 / `len(x)==0` 104 / `== ''` 100 / else-of-presence 1 /
test-on-another-value 14 / none 1,029.

Verdict (re-derived by the gate): `some_literal_arms_are_silent_defaults_a_caller_cannot_tell_apart`.

## Four things worth carrying forward

1. **A guard that tests a different variable is not a declaration.** `if node is None: return lits`
   says something about `node`. Fourteen arms move from "declared" to "not declared" once the guard
   row has to name the value the arm returns — `scripts/e497_twindead._fold_literals`,
   `engine/futures_runner.yearly_returns`, `scripts/grid_p1_screen.load_rows`,
   `scripts/im_ic_pair._resume` among them. Publishing the guard test without its subject reads as
   compliance.

2. **The shared emptiness helper is dead code on Python 3.11.**
   `e514._empty_container` answers `not list(ast.iter_child_nodes(node))`, and every `List`, `Dict`,
   `Set` or `Tuple` carries a `ctx` child, so `[]` and `{}` are both "not empty". The escape hatch
   in `e514.trace` ("an empty container is a starting point, not an answer") therefore never fires,
   which is the mechanism by which initialised-and-filled containers reach upstream faces as
   literals. Proven in the selftest (`_empty_container([]) is False`), counted in the face (3 arms).

3. **The same-arity `None` tuple is the worst shape.** 54 arms share their arity with the read arm,
   so the caller unpacks successfully and receives `(None, None, None)`; nothing but a per-element
   `is None` catches it. `scripts/etf_phase_beta_target.apply_overlay` returns
   `(None, None, None)` under `if not sched` against three `pd.Series` on the normal path.

4. **Entry points must be named separately.** 73 of the 475 silent arms are `main()` exit codes —
   a documented contract — and 402 are not. Publishing 475 without the split would be read as 475
   defects in the repo.

## Two instrument failures caught in-window (both by the selftest, not by review)

- `any(reads_something(...) for fill in ...)` where `reads_something` returns `(bool, via)`: a
  non-empty tuple is always truthy, so every initial-value arm was reported as having a reading
  fill. A predicate that returns a tuple needs `[0]` before `any()`.
- A node-identity cache must include the function parameters and the skip set, and must be cleared
  at the start of each analysis: keyed by `id(node)` alone, a second build in the same process (the
  fixture, then the empty-population arm) inherits the first tree's answers because ids are reused.

## Verification

- `scripts/e518_literal_guard.py` — `run` rc0 (146s), `check` problems=[], `verify` re-derives
  problems=[], **selftest 33/33** (six fixture arms, five doctored arms refused).
- `results/state_tilt/LITERALGUARD-2026-11-08.json` + `literalguard_latest.json` (same bytes).
- S6 leg `literal_guard` rc0 0.09s; smoke leg `# E518` 1/1 green, `--doctor` 1/1 red with the face
  restored byte-identically (sha `b1fdeaa0f810`).

Not run this window: the full smoke suite, the other S6 chain legs, the collector family, the
per-lane paper chains. Nothing is adopted, nothing is rewritten upstream, no charge.