# DIGEST 2026-11-08 r1582 bm-b -- E556: the six faces E555 rescued are announced only by the message

## What was asked

E555 (r1581) folded six of E554's 67 unresolved `wrote <path>` rows by evaluating
`Path(__file__).resolve().parents[k]` against the writer's own path, and published that all
six faces exist on disk.  E554's at-risk arm -- is there a `<stem>_latest.json` pointer, or
does any other source name the path -- had never been run over those six rows, because E554
could not resolve them.  So the question E556 asks is: **if the message is lost, what is left?**

## What was measured

Population machine-read from E555's own `folded_faces` (six rows, never hand-copied).  For
each face three arms:

* **pointer**: every `results/state_tilt/<stem>_latest.json` on disk, and whether its content
  actually names this face (existence is not naming);
* **load**: every call in the corpus whose function is a loader (`open`, `read_text`, `loads`,
  `read_json`, `read_csv`, ...) and whose argument folds -- through module constants and the
  assignments of the enclosing function *before that line* -- to the face path;
* **mention**: E554's own literal arm, over executable sources only (py/ps1/bat/cmd/sh).

## What came out

| arm | count |
| --- | --- |
| faces on disk | 6 / 6 |
| naming pointer faces | 0 |
| load calls | 0 (0 distinct loading sources) |
| mentions (not loads) | 1 (`scripts/e323_reach_under_wider_needle.py` names `etf_book_premium_phases.json`) |
| faces only the message announces | **6** |
| control arm (`unfoldedname_latest.json`) | 1 load -- the arm is not blind |

E554's spawn arm also says five of the six writers cannot be spawned by any source, so the
six faces cannot be rebuilt except by a human typing the command line.

Verdict: `some_rescued_faces_are_announced_only_by_the_message_that_names_them`.

## The four reusable lessons

1. **On disk is not announced.** A face that exists, named only by a print nobody reads, is
   reproducible only by hand.  E555's "all six exist" is a statement about the filesystem and
   was one reading away from being read as "these faces are usable".
2. **A mention is not a load and a pointer is not a name.** Each arm needs its own falsifier:
   for the mention, ask whether the path is a load's argument or only text in some file; for
   the pointer, ask whether the `_latest` file's content actually contains this face.
3. **A blind arm must raise, not annotate.** A scanner that returns "0 loads" for every face is
   indistinguishable from one that found no loads, unless it is run against a face the tree is
   known to load.  Without the control the verdict "nobody reads these" is unfalsifiable.
4. **Per-call scope resolution is O(n^2).** Reusing the parent's `_local_scope` (an `ast.walk`
   of the whole enclosing function per call) burned six CPU-minutes with zero output on a
   24k-line gate file.  One pass per function with cumulative snapshots per assignment
   boundary, and a lookup by line, produces the same evidence in 16.5 s.  Third instance of
   the E442 family.

## Where the face lives

`results/state_tilt/RESCUEDFACE-2026-11-08.json` (+ `rescuedface_latest.json`), built by
`scripts/e556_rescued_face.py` (selftest 12/12, `check` problems=[], `verify` identical),
smoke leg `# E556` via `scripts/run_e556_smoke_leg.py` (1/1 green, `--doctor` 1/1 red).
