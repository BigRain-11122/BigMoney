## E401 -- a helper that hides a reader can hide nothing if every key it opens is opened elsewhere

What was measured (r1422 bm-b). E384 classified every published key's sites by the stdlib call
family around them and left one residue: `results/perpetual_faces/n1_w192_results.json`, named only
at `Tools/_r789bmc_post_rebase_verify.py:12` inside `json.loads(show(...))`. The worry was that a
project-local helper could hide a whole population behind one name. So the missing table was built:
5,371 project-local callables whose body opens or dumps a file, resolved transitively to 4 hops, and
E384's own classifier was **re-run** with those names added (`e384.classify_call` patched for one
`io_map` call, restored in a `finally`). Result: 86,616 site lines that the stdlib table reads as
"other" move to load/dump, and **0 of 883 keys change class**.

Why that is not a null result. The one residue is not a hidden file reader at all: `show()` in
`Tools/_r789bmc_post_rebase_verify.py` is `subprocess.run(["git","show","HEAD:"+path])`, i.e. a
git-object read. Measured per site, **10 of the 10** sites the stdlib table calls "other" are
git-object reads (they span 4 keys; 1 key is named only that way). So the residual class is scoped,
not silent: no table of file-opening callables could ever classify them, and the honest sentence is
"one key, ten sites, all git blobs", not "a blind spot of unknown size".

Two instrument rules, both measured rather than assumed.
1. A name-keyed helper table merges same-named defs across modules. That makes the moved-SITE count
   an upper bound (86,616 transitive / 48,129 direct-only), so publish both arms and never let a
   moved-site count stand in for a moved-key count. The key arm is the one that cannot flatter
   itself: a key only moves if a stdlib call does not already open it somewhere.
2. The same merge makes a transitive flag dangerous for anything rarer than load/dump. Propagating
   "reads a git object" through callees reported **5,343 git readers against 8,483 defs**; pinning
   the arm to the direct body dropped it to **63**. Publish the arm's propagation depth beside its
   count, and prefer direct-only for any flag whose false-positive rate you have not measured.

How to apply: when a census leaves a residue "behind a helper", do not argue about the helper --
build the helper table, re-run the *published* classifier with it (patch, run, restore in a
`finally`, assert the restore), and then price the residue per site. If the residue turns out to be
a different kind of reader (git blob, subprocess, memcached), that is the finding: the population is
bounded by the kind, and the count of keys behind it is the bill.

Wiring: `scripts/e401_local_reader.py` (run / verify problems=[] / selftest 23/23); smoke leg E401
(1/1, exec'd verbatim by `scripts/run_e401_smoke_leg.py`); S6 leg `local_reader_table`; face
`results/state_tilt/LOCALREADER-2026-11-04.json` + `localreader_latest.json`; successor card E405
stays queued (the never-produced read target); no published face, pointer, caller, reader or key was
edited. Side effect measured: the new `localreader_latest.json` is itself a family-named pointer, so
E398's pointer count moved 176 -> 178 and its face was re-derived from the live build rather than
the leg loosened.