# DIGEST 2026-11-08 r1583 bm-b -- E557: can anything RUN the writers of the message-only faces?

## What was asked

E556 (r1582) found all six faces E555 rescued announced only by the message that names them:
no `_latest` pointer, no source load.  E556's own spawn arm added that five of the six writers
cannot be spawned by any source, and closed with "the six faces cannot be rebuilt except by a
human typing the command line".  That last sentence is the one E557 prices: **is the writer
reachable from an entry point at all** -- the S6 chain, a smoke leg, a run wrapper, a task --
or is a human retyping a docstring the only way back?

## What was measured

Population machine-read from E556's own `rows` (six rows, four distinct writers).  For each
writer, a naming-site census over executable sources, where each site carries a **kind**:

* a **live chain leg** -- the `LEGS` literal of `Tools/s6_chain_bm[abc].py` is read as *data*
  (label, argv) and the leg's verb decides whether it rebuilds (`run` / no argument) or only
  gates (`--check`, `check`, `--selftest`).  bm-a's runner imports bm-c's list rather than
  copying it, so a leg runs on every host that shares that list;
* a **smoke leg** in `smoke_test.py` (often `--selftest` only: the module imports and its
  invariants hold, nothing is written);
* a **speech act**: a subprocess spawn, an import by another module, a task or shell definition;
* a **one-off**: `Tools/_r<N>`, `scripts/e<N>_`, `_dbg`, `_tmp` -- historical command lines,
  never entry points (19 of the 33 raw code-level mentions are these).

Control arms in both directions: `scripts/regime_thermo_build.py` must be found as a build leg
on this machine's own chain, and `scripts/etf_book_hysteresis.py` must be found as a gate leg --
so a build leg and a gate leg cannot collapse into one class, and a "nothing reaches these
writers" reading cannot come from a blind census.

## What came out

| reading | value |
| --- | --- |
| rows / distinct writers | 6 / 4 |
| writers with a **build** entry point | **1** (`scripts/capital_placement.py`) |
| -- and on this machine (bm-b) | **0** |
| writers only ever **gated** by a chain | **3** |
| writers rebuilt on another machine's chain | 1 (bm-c's list, which bm-a also runs) |
| raw code-level naming sources / of which one-off | 33 / 19 |
| rows whose spawn arm says "no source spawns this writer" **while a chain leg names it** | **6 / 6** |
| command line recorded in the writer's own docstring | 4 / 4 |

* **bm-b's own 308-leg chain names none of the four writers.**  bm-c's 81-leg list (also run by
  bm-a) names all four: `capital_placement` with `run` (it rebuilds), and the three
  `etf_book_*` phase/adoption writers with `--check`.
* A `--check` leg is not a rebuild path.  `etf_book_premium_phases.py --check` and
  `etf_book_voltarget_phase.py --check` return `check()` and write nothing; the faces they gate
  are rebuilt only by `run`, which no leg ever passes.

Verdict: `some_message_only_faces_have_a_live_chain_leg_that_rebuilds_them`.

## The four reusable lessons

1. **A chain leg's argv is data, so a call-site spawn scan cannot see it.**  All six rows carry
   E556/E554's "no source spawns this writer" while a live chain names all four -- not a
   contradiction, a blind spot: `LEGS` is a list of `(label, argv)` tuples, and no call site
   mentions the script.  Measure the *runner's table*, not the calls.
2. **Gate is not rebuild.**  `--check` proves a face is still right; it cannot restore a deleted
   or stale one.  Counting any leg that names the script as "reachable" would have turned three
   writers with no rebuild path into three with one.  The verb is part of the measurement.
3. **One non-literal argv element must not erase the table -- and neither may a BOM.**  The first
   build read bm-b's 306-leg table as *empty*: the file starts with a UTF-8 BOM (so `ast.parse`
   raised) and three legs carry `os.path.join(...)` inside their argv (so `literal_eval` over the
   whole list returned nothing).  Both failures read exactly like "this runner runs nothing".
   Elements are now read one at a time, an unreadable element is published as
   `<unreadable:...>` (and still searched for the writer's name), and the leg count that could
   not be read is published beside the count that could.
4. **A shared leg list is a different reach than a copy.**  bm-a runs bm-c's list by import, so
   "which machine can rebuild this" cannot be answered from the file that holds the legs alone.
   The face publishes `machines_that_run_this_list` per runner.

Also measured: 19 of 33 raw naming sources are one-off round snapshots (`Tools/_r<N>`,
`scripts/e<N>_`), so the unclassified grep answer to "who names this writer" overstates wiring by
more than half -- the same shape as E444/E470.

## Where the face lives

`results/state_tilt/FACEENTRYREACH-2026-11-08.json` (+ `faceentryreach_latest.json`), built by
`scripts/e557_face_entry_reach.py` (build/check/verify, selftest 36/36), S6 legs
`face_entry_reach` (32.0 s rc=0) and the newly wired `rescued_face` (19.2 s rc=0), smoke leg
`# E557`.