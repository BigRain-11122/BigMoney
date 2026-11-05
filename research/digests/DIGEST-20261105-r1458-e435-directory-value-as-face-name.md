# Digest r1458 -- E435: 626 of 679 directory values are a face's home, and none of the 528 joins lands on anything

Face: `results/state_tilt/DIRISFACE-2026-11-05.json` (+ `dirisface_latest.json`).
Card: `knowledge/METHODOLOGY_ASSETS.md` E435. Study: `scripts/e435_dir_is_a_face.py` (built by the
dead r1458 window at 14:44, absorbed and wired this window).

## What was done

E423 indexed 679 directory-named published fields and 44 that hold a file path. Its promise was
one-directional: a field named `dir` is read as a base. Nobody asked the other half -- whether that
base is itself the *name of a published face*, so a join silently picks a face as its parent.

E435 prices the same 679-value population on four mechanical questions with no vocabulary games:
whether the value's basename equals a published face stem; whether the value is the *home
directory* of a published face; whether the row also carries a name field so a join can be
composed at all; and whether that composed path exists on the tree today.

## What it measured (cutoff 2026-11-05, 12,884 faces scanned, 8,640 distinct face names)

| reading | value |
|---|---|
| directory-named published fields | **679** |
| basename is itself a published face name | **0** |
| value is the home directory of a published face | **626** |
| value points at neither | 53 |
| rows that have a name field to join with | 528 (151 have none) |
| joins that land on an existing path | **0** |
| joins that compose onto a published face | **0** |

Verdict, re-derived by the gate:
`directory_values_are_face_home_directories_and_none_of_them_compose`.

## The three readings worth keeping

1. **The named worry is empty; a different shape is not.** Zero directory values collide with a
   face *name*, but 626 of 679 are the *parent* of a published face (`data/sina_mf`,
   `results/state_tilt`, `results/paper`). A reader that joins such a base lands inside a face
   *family* rather than in a workspace, which is a placement question, not a doubling question.
2. **Armed is not composed.** 528 rows could be joined and **0** of those joins resolves to a file
   that exists today. Publishing the two together is the whole point: 626 alone reads as a live
   defect, 0 alone reads as a non-finding, and the pair reads as "the shape is everywhere, the
   accident has not happened".
3. **A join that lands on nothing is still checked.** 528 of 528 compose onto nothing, which is a
   measurement only because the same instrument was applied to (a) real directories on disk and
   (b) the face-name index that produced the 626. The verify leg refuses a landing that no longer
   exists, so the zero is re-checked against the tree on every run.

## Bound published

- A collision is decided on the basename, so two different directories with the same leaf name
  count once per row, not once per directory.
- Composition is priced against paths that exist on **this** tree at scan time; a target created
  later is graded `lands_on_nothing` today.
- A row offering several name fields is graded `lands` if any of them lands; the published
  `join_target` names which one did.
- Faces larger than 3 MB are outside the shared scanner, so a census carrying such a field sits
  outside this population.

## Wiring

- `scripts/e435_dir_is_a_face.py` -- `run` / `verify` (`problems=[]`) / `selftest` (19/19).
- `Tools/s6_chain_bmb.py` leg `dir_is_a_face` (verify).
- `smoke_test.py` leg E435 (extracted verbatim and executed standalone).
- `results/runnable_pool.json`: E435 done with `result_ref`; supply floor refilled.