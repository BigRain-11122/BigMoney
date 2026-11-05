# Digest r1459 -- E436: nobody performs the doubling read that a double-ready row invites

Face: `results/state_tilt/DOUBLEJOIN-2026-11-04.json` (+ `doublejoin_latest.json`).
Card: `knowledge/METHODOLOGY_ASSETS.md` E436. Study: `scripts/e436_double_join.py`
(selftest 13/13, verify problems=0). Smoke leg `# E436 (r1459 bm-b)` in `smoke_test.py`,
extracted verbatim by `scripts/run_e436_smoke_leg.py` (1/1 pass; `--doctor` 1/1 red with the face
restored byte-identical, sha `f26ba329ec3f9221` in and out).

## What was asked

E433 found rows whose directory-named field holds a **file** path while a sibling name field already
equals that basename -- so `dir + name` is armed, and the defect travels one face further. E436's
question: does any read site in the corpus actually join `resolved_directory` with the fragment, and
would the composed path exist?

## What it measured (population imported from E433, corpus 3,4xx sources)

| reading | value |
|---|---|
| double-ready rows carrying a fragment | 18 |
| distinct `(fragment, resolved_directory)` targets | **11** |
| targets with a resolved in-tree directory | 7 |
| published paths that exist on this tree | 0 |
| sites that name a fragment literally | 37 (read 10 / write 9 / path-only 18) |
| read sites joining the published directory (the doubling read) | **0** |
| read sites recomposing from the parent directory | 8 |
| read sites that rebuild exactly the published path | 8 |
| read compositions that exist | 0 (10 resolved, 0 present) |
| targets with no read site at all | 10 of 11 |

Verdict, recomputed by the gate:
`no_reader_joins_a_double_ready_directory_value_and_the_readers_naming_the_same_file_recompose_it_from_the_parent`.

## What changed in the instrument (both caught by the numbers, not by the code)

1. **The base must stop before the fragment.** The first build sliced the composing chain as
   `chain[1:]`, so the fragment stayed inside the base: 8 parent recompositions became 8 "doubling
   reads" composing `.../results/idle_trigger.bm-c.json/idle_trigger.bm-c.json`. The headline
   `a_reader_joins_..._doubled_path_is_absent` was manufactured by that off-by-one and is now a
   `verify`-light selftest fixture (`a runtime parameter base stays unresolved` plus the two
   path-shape legs).
2. **`open` is not a reader.** Grading by callee name put 9 `open(p, "w")` sites in the read tally,
   so every writer counted as a consumer and `fragment_naming_write_sites` read 0. The family is now
   read from the mode argument (`_family_of`), with a selftest leg pinning `'w'` -> write and no
   mode -> read.

## What the zero means

The containment is a property of the read side: a double-ready field is only dangerous if a
consumer starts from the published value instead of from the parent it was built from. All 8
parent recompositions are reads of `idle_trigger.bm-c.json` -- another machine's health face --
composed as `ROOT / "results"` + name, i.e. the correct path, absent here only because that face is
not on this work tree. The remaining 10 targets are written and named but never read.

## Bounds (published, not implied)

A site is attributed only when its composing chain ends in the fragment literal; names built from
f-strings, variables or loops are outside the scan and are never counted as absent. Bases resolve
one hop through module constants and stay `base_unresolved` (21 sites) rather than being guessed
from spelling. Existence is tested against the current work tree, so a gitignored runtime cache this
machine never wrote reads as absent exactly like a mis-composed in-tree path -- and a site that
addresses the same tree through another drive letter (`K:\...`) is graded unrelated by the
resolved-path test, which is why 2 of the 10 reads sit in `composes_from_an_unrelated_base`.