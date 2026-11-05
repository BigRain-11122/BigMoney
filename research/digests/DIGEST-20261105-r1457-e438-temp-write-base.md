# DIGEST r1457 bm-b — E438: a temp directory the callee never writes into

Card: `E438-WHICH-PASSER-SPENDS-A-TEMP-DIRECTORY-THE-CALLEE-NEVER-WRITES`
Face: `results/state_tilt/tempwritebase_latest.json`
Script: `scripts/e438_temp_write_base.py` (selftest 23/23, `verify problems=[]`)
Methodology card: E438

## What was measured

E437 published 203 call rows that hand a directory parameter a temp marker, and priced the
*name* heuristic against them.  It never asked whether the callee writes inside the directory it
receives.  The population here is E437's, imported rather than re-derived (same corpus, same 310
parameter sites, same call-row unit — the rebuild reproduces 203 of 27,718 rows exactly, which is
the check that the population is shared and not re-invented).

Each call row is graded by the write paths inside its callee:

| class | rows | callees |
|---|---|---|
| every write composes a name onto the directory | 147 | 11 |
| a write names the directory, composes nothing onto it | 0 | 0 |
| the callee writes the parameter path itself (a file-path writer) | 56 | 11 |
| no write names the directory | 0 | 0 |
| callee not resolved | 0 | 0 |

**147 of 203 temp call rows actually spend the directory: 72.4 %.**  The temp population E437
published is an upper bound by 86 rows.

The non-spending 56 are all one shape: `dump(p)`, `save(p)`, `write_json(path)`, `_write_csv(path)`
— a wrapper whose only write is the parameter path itself.  The caller passes `tmpdir` into a slot
that wants a file, so nothing is written inside the temp directory and the call would fail if it
ever ran against the real path.  That is a different defect from "never writes" and it gets its
own class (`..._a_file_path_and_the_directory_lands_on_a_file_slot`) instead of being folded in.

## Two instruments had to be replaced mid-study

1. **First draft graded the raw path text only** and called `hp` an outside write in
   `Tools/heartbeat_write.py::_fixture`, whose body is
   `hp = os.path.join(root, "fleet", "machines", "bm-a.json")` then `open(hp, "w")`.  All 30
   `partial` rows were that one indirection.  Resolving the text through the function's own
   bindings (`e420.resolve`) before grading moved all 30 to `inside` and left zero partials.
2. **A class that only exists because the instrument is coarse is not a finding.**  The 56
   `names_only` rows were, on inspection, one repeated pattern (the file-path wrapper).  Leaving
   them in the named bucket would have read as "callees that join a name but write elsewhere",
   which no callee in this corpus does.

## Limits published, not implied

- a function that writes nothing is not a write site and never entered the population, so the
  "composes a name and somebody else writes it" case is outside this scan and is **not** counted
  as `outside`;
- writes made by functions the callee calls are not followed: `inside` means "this function spells
  a path inside the directory", not "the bytes land there";
- a callee with several directory parameters is graded over all of them.

## Why this matters past the census

The reason to care about a temp directory at all is cleanup and hermeticity: how much of the
"fixture writes to a temp dir" population can actually leak.  E437 answered "which rows say temp";
this answers "which rows spend it", and the answer shrank the population by 42 %.  A consumer that
treats E437's 203 as writers is counting 56 calls that could only ever write onto a file slot.