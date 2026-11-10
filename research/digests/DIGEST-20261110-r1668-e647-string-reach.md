# DIGEST-20261110-r1668-e647-string-reach

- study: **E647** — can a name-collision hit reach the counted module through a string rather than an import?
- round: **r1668 bm-b** (2026-11-10) · machine `bm-b` · lane `cpu-only`
- face: `results/state_tilt/STRINGREACH.json` + `stringreach_latest.json`
- tool: `scripts/e647_string_reach.py` (selftest 25/25, `run`/`check`/`verify` rc0, `problems=[]`, rebuild byte-identical sha `137c076797e0`)
- legs: `smoke_test.py` leg E647 (`scripts/run_e647_smoke_leg.py` 1/1 PASS, `--doctor` 1/1 red with the face restored byte-identically, sha `137c076797e0` in = out) + `Tools/s6_chain_bmb.py` leg `string_reach` (rc=0 0.06s)

## Why the question exists

E646 decided that its seven cross-module key-name hits are word collisions, and it did so from
import statements only. It published the hole as a limit rather than a zero: a module that reaches
the read module through `importlib.import_module("…")`, through a path string, or through the face
the module writes is invisible to an import-statement test. A limit that could be measured and was
not is the same defect as an unfloored zero (E453/E488 family), so this round prices it.

## What was measured

The hits are re-derived from the tree with E642's population and owner rule (13,099 files; 7 hits in
6 modules, matching E646's published 7 exactly). For each hit module the study collects every string
the module can be asked to spell:

- plain `Constant` strings,
- `JoinedStr` nodes whose parts are all constants (their concatenation is measurable),
- `"a" + "b"` folds,

and counts separately the strings built from an expression (a `JoinedStr` with a `FormattedValue`,
`str.format` on a literal, `%` formatting), because no static reader can resolve those.

Each counted read module's spellings are built from measurement rather than a hand list: its
relative path, basename, stem, dotted name, and the module-level assignments whose name is upper case
and contains `FACE` or `LATEST` (`FACE`, `LATEST`, `FACE_NAME`, `UPSTREAM_FACE`) where the assigned
value is a literal. Matching is in six classes with the exact ones first and whole-token containment
apart, so a substring is never read as a name; a family prefix (`e382` for
`e382_key_projection_delta`) is not a match.

The consumer of each matching string is found by walking up to the call that takes it (import
machinery, file open, `exec`/`eval`, `sys.path` mutation, path join, other, or none), and every
dynamic loader call in the hit module is counted whether or not its argument is a literal.

## Reading

- 480 measurable strings in the 6 hit modules (all published; 0 elided), **0 naming a target** —
  exact path / basename / stem / dotted / face and whole-token containment all at zero;
- 14 strings built from an expression, published as `unresolved` (seeded as E651 rather than folded);
- 28 dynamic loader calls across the six modules, **27 of them carrying a measured literal argument**
  — none of those literals names either counted read module or its face;
- 6 hit × read pairs (5 against `scripts/e382_key_projection_delta.py`, 2 against
  `scripts/e504_name_compose.py`, 5+2 hits collapsing onto 6 module pairs): all six
  `no_literal_names_the_target`.

## Verdict

> no hit module spells any counted read module, its stem, or its face in any string it can be asked
> to spell, so the importlib/path arm E646 could not see carries no hit either

## Lessons

1. **A limit has to be tested in its own form, not inherited.** E646's limit named a measurable
   population — the strings of those modules and the loader calls they make. Leaving a measurable
   limit standing converts a hole that costs one walk into a permanent disclaimer.
2. **A face name is measured from the assignment, never from a hand list.** The first build knew only
   `FACE`/`LATEST`; `e504` writes `FACE_NAME`, so its face set came out empty and read as "tested,
   nothing there" when it was "never looked at". The fix publishes three states: literal face, face
   assigned but not a literal, and frozen name absent from the module.
3. **A substring is not a name.** Containment is its own class and is published apart from the exact
   classes, and a family prefix does not count — "a string containing the name" and "a string that is
   the name" are two measurements.

## Pointers

- pool: E647 done, E651 (fold the 14 unresolved strings by tracing module-level operands) and E652
  (the same instrument corpus-wide) seeded; ready back to 4 against a floor of 3.
- methodology card: `knowledge/METHODOLOGY_ASSETS.md` E647; registry row in
  `knowledge/TREASURE_REGISTRY.md`; delivery on `machine/bm-b-r1668`.