# DIGEST 2026-11-07 r1528 bm-b -- E501: are the eight written-but-unread faces still being refreshed?

**Question.** E495 published 8 faces that a producer writes and no consumer reads (2,781,043 B).
"Nobody reads it" and "nothing refreshes it" are different sentences, and only the second one
makes a face retirable without breaking a producer's work.

**Answer.** 0 of 8 are rewritten by any writing-mode path in the tree; all 8 are held only by
read-only chain steps. The population is simultaneously **not live** and **not retirable**.

| face | bytes | wiring in `Tools/s6_chain_bmb.py` | face class |
|---|---|---|---|
| `results/state_tilt/barecallresolve_latest.json` | 108,508 | `e443_bare_call_resolve.py check` | chain-pinned |
| `results/state_tilt/callerclass_latest.json` | 11,797 | `e450_caller_class.py check` | chain-pinned |
| `results/state_tilt/fixturebeyond_latest.json` | 13,905 | `e434_fixture_beyond.py verify` | chain-pinned |
| `results/state_tilt/fixturewrite_latest.json` | 31,250 | `e432_fixture_write.py verify` | chain-pinned |
| `results/state_tilt/importclass_latest.json` | 13,761 | `e456_import_class.py check` | chain-pinned |
| `results/state_tilt/namerecall_latest.json` | 78,526 | `e437_name_recall.py verify` | chain-pinned |
| `results/state_tilt/no_caller_latest.json` | 52,539 | `e434_fixture_beyond.py verify` (writes via `E428_FACE`) | chain-pinned |
| `results/state_tilt/sharedname_latest.json` | 2,470,757 | `e440_shared_wrapper_names.py verify` | chain-pinned |

**Three reusable lessons.**

1. *"Called" has three prices.* `python scripts/eNNN.py check` launches the script and never
   rewrites the face; an importer that calls `mod.write_face()` does rewrite it; a report line
   does neither. Collapsing them produced a wrong answer in this very study: the first build
   graded `e450._tree` (a generic opener) as a writer of `callerclass_latest.json` and reported
   2 live faces.
2. *A writer must be connected to the face name, not merely exist in the module.*
   `write_face(os.path.join(OUTDIR, FACE_NAME), face)` is connected; `_tree(rel)` is not.
3. *A read-only chain step pins a face, it does not refresh it.* It makes retirement fail the
   chain while doing nothing against rot. "Who writes it" and "who requires it to exist" are
   separate questions and must be reported separately.

**Boundary.** Caller scan covers `scripts/`, `Tools/`, `docs/`, `research/` and five root
documents; `results/` is excluded (a face naming a study is not a caller). Entries are
`__main__` bodies and module-level dispatch tables only. Writer linkage is an AST
approximation (face constant, literal, or the name flowing into an opener as an argument); no
dataflow. `mtime_floor_days=21` is published because checkout materialises mtimes (E453).

**Verification.** `scripts/e501_unread_refresh.py` -- `run` rc0, `check` problems=[],
`verify` problems=[] (summary and verdict re-derive from the rows), `selftest` **17/17**.
Artifacts: `results/state_tilt/UNREADREFRESH-2026-11-07.json`, `results/state_tilt/unreadrefresh_latest.json`.
Card: `knowledge/METHODOLOGY_ASSETS.md` E501. Pool: `E501-...` flipped to done with `result_ref`.