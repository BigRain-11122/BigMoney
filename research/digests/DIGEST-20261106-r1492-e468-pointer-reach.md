# DIGEST 2026-11-06 r1492 bm-b — E468: a pointer the repo root cannot follow is named by its producer or by nobody

**Card.** E468-DOES-A-FACE-WHOSE-POINTER-RESOLVES-ONLY-FROM-ITS-OWN-DIRECTORY-EVER-GET-READ
**Face.** `results/state_tilt/POINTERREACH-2026-11-06.json` (+ `pointerreach_latest.json`)
**Producer.** `scripts/e468_pointer_reach.py` — run rc0, `check` problems=[], `verify` problems=[]
(identical, 37/37), `selftest` **15/15**.
**S6.** `pointer_reach` leg, rc0 (`results/_r1492bmb_s6_chain.json`).
**Smoke.** `e468 is a pointer that needs a base other than the repo root ever read (r1492 bm-b)` —
1/1 green standalone, 1/1 red on a doctored residue label, face restored byte-identical
(sha in == sha out).

## What was measured

E466 left 37 path-form pointers whose required base is not the repo root (33 own-directory, 4
absolute) over 24 distinct targets. This study asked who reaches those targets.

| residue class | pointers |
|---|---|
| no source in the corpus names it | 24 |
| named only by a one-off round script | 4 |
| named only by a smoke/runner leg | 2 |
| named by a source that writes neither face | 7 |

36 naming sites: 9 spell a repo-relative literal, 14 join the literal to their own directory, 13
show no base in the window; **8 sites belong to the producer that writes the target they name**,
and **0 sites resolve the pointer itself**. The 7 remaining rows are genuine consumers of the
*upstream* face that carry its literal (`e448`/`e449`/`e451` → `droppedpath_latest` /
`deadprereg_latest`; `e273` → `BANDSCREEN`; `e406`/`e420` → `REPUBLISH`).

Verdict: `some_pointers_that_need_another_base_are_named_by_a_source_that_writes_neither_face`.

## Two self-caught defects

1. **A field named for the wrong question.** First publish carried
   `pointers_reachable_from_the_repo_root: 37` computed as `isfile(join(root, target))` — true by
   construction. Renamed `target_exists_on_disk_at_that_repo_relative_path`.
2. **"Outside the producer" is not "a reader".** 13 rows first fell into one "outside" class;
   splitting producer-of-target / smoke-leg / one-off round script took the readable number to 7.
   The write test needed target `_latest` → base-stem alias matching to work at all.

## Pointer

`knowledge/METHODOLOGY_ASSETS.md` card E468. Next: E470 (is the target of such a pointer ever
**opened**, by any route) seeded to restore the supply floor to 3.