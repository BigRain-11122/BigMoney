# r1434 (bm-b) -- E415: the accident shape E414 named, priced over six surfaces

**Card.** E415-DO-BARE-BASENAME-READS-WORK-ONLY-BECAUSE-THE-CWD-HOLDS-THE-FACE (seeded by r1433 out
of E414). **Lane** cpu-only, static plus files on disk. **Face**
`results/state_tilt/CWDACCIDENT-2026-11-04.json` (+ `cwdaccident_latest.json`).

## Population

Every read in the durable corpus (`smoke_test.py` + `scripts/`, `Tools/`, `firm/`, `live/`,
`engine/`, excluding `_*.py` scratch and the artefact trees) whose path argument is a literal
basename at the call -- no separator, a data extension, nothing joined onto it. Two sites, both in
`smoke_test.py`.

## Reading

| site | basename | class | why |
|---|---|---|---|
| `smoke_test.py:7971` | `replaycensus_latest.json` | `resolved_by_its_callee` | `e298_replay_control_census.load()` joins `OUTDIR` -> `ROOT` -> `__file__` (E414, re-derived here) |
| `smoke_test.py:1175` | `CODELY.md` | `cwd_relative_face_shadowed` | plain `open()`; correct only from the repo root, and `~/.codely-cli/CODELY.md` is a **different** document of the same name |

Surfaces probed: repo root, `scripts/`, `Tools/`, `docs/`, `results/state_tilt/`, and the CLI home
`~/.codely-cli`. The memory leg asserts the file is intact (`>=55` lines, no private-use characters,
`>=1` list row). Nine `CODELY.md` files exist in this machine's tree and four satisfy that
assertion, so from another repository's directory the leg goes **green on that repository's memory
file**. The surface that actually reaches it today is the CLI home copy (50,804 B, 81 lines, 65 list
rows) -- which passes.

## Verdict

`every_bare_path_read_is_directed_but_at_least_one_would_read_a_different_document_of_the_same_basename_from_another_launch_directory`

## Pits hit while measuring (both fixed in-window)

1. **A resolver bound through `importlib`.** Site 7971 was first published as
   `cwd_relative_face_missing` because `load` is not defined in `smoke_test.py` -- it is
   `__import__("importlib").import_module("e298_replay_control_census")` bound to `_m298` two lines
   earlier. A same-file search for the callee says "no such function" and the site is then graded as
   if it had no resolver. Fix: follow the `Assign` binding to the module and read that file's body.
2. **Comparing against nothing.** The first version marked `results/state_tilt` as holding a
   "different document" for the resolver-directed site simply because the repo root does not hold
   that basename (`own_sha is None` -> every comparison false). Rows now carry
   `this_tree_holds_the_name` and `different_document` separately, and classification only reads
   `different_document`.

## Wiring

* `scripts/e415_cwd_accident.py` -- run / verify `problems=[]` / selftest 19/19.
* smoke leg `# E415 (r1434 bm-b)`; executed verbatim from the shipped source by
  `scripts/run_e415_smoke_leg.py` (1/1). Proved red on a doctored verdict + class tally, face
  restored byte-identical (sha256 `411ec43fc0483000...`).
* S6 leg `cwd_accident` -- rc 0, 10.9 s (one AST pass over ~900 files).
* `knowledge/METHODOLOGY_ASSETS.md` card E415 (numstat 48/0, pure addition).

## Not done, not claimed

The readers were not edited: making the memory leg resolve its file from the module's own directory
is a separate card. The census bound (vars, f-strings, non-joining wrappers) is E398's and E403's
population and is published as a `bound` field rather than folded in. The full smoke suite was not
run this window; only the E415 block was executed from the shipped source.