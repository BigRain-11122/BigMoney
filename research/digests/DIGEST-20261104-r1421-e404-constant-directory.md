# DIGEST r1421 bm-b -- E404: an untraceable directory is usually one the reader cannot act on

**Card:** knowledge/METHODOLOGY_ASSETS.md E404
**Face:** `results/state_tilt/CONSTDIRS-2026-11-04.json` (+ `constdirs_latest.json`)
**Runner:** `scripts/e404_constant_directory_resolution.py` (run / verify problems=[] / selftest 15/15)
**Population:** the 18 sites carrying the 10 fragments E402 classed
`directory_expression_not_traceable_statically` in `FRAGMENTPRODUCERS-2026-11-04.json`.

## What was measured

For every site: take the directory expression, follow its first name to the binding that supplies
it (function scope -> module assignment -> one import hop), compose the literal tail onto the
resolved directory, and test whether the file is there.

| class | sites |
|---|---|
| directory supplied by a function parameter or loop value | 6 |
| module constant rebound inside a function | 1 |
| resolved directory outside the tracked tree or a gitignored runtime cache | 8 |
| resolved directory inside the tree and the path is absent | 3 |
| imported constant module absent / still unresolved | 0 / 0 |

Verdict: `a_module_constant_does_name_an_in_tree_directory_and_the_joined_file_is_not_there`.

## The reading

"Not traceable statically" is not one bucket. **7 sites** are supplied at call time (a fixture or a
parameter) -- the trace limit was the reader's, not the corpus's. **8 sites** name a directory the
reader cannot act on from this tree at all: `results/idle_trigger.bm-c.json` and
`results/alphagen_rl_p1/ckpt/train_log.jsonl` (gitignored runtime cache) and
`Money02/data/cache/p1c_stock/*.meta.json` (generated cache, and Money02 is a frozen corpus here).

**The 3 real ones are reads with no writer.** `scripts/p2_deepening.py:420` reads
`firm/traders/COMPOSITE-001.json`; `scripts/trial_labor_w20.py:94/97` read
`results/trial_labor_w20/w20_screen.json` and `w20_reform_face.json`. Nothing in the corpus writes
any of the three (`in_tree_absent_writes = 0`, `in_tree_absent_reads = 3`), so these are not
"pending outputs": they can only ever fail. That is the bill E404 was asked for, and it is smaller
than E402's headline suggested but it is real.

Zero dangling imports: every module constant the walk touched resolves to a file the tree holds.

## Pit

The first cut of the smoke leg asserted that an outside-the-tree path must be absolute and failed on
8 rows. The class name is "outside the **tracked** tree or a gitignored runtime cache", and those
paths are published repo-relative on purpose (they are joined onto the repo root at read time), so
the assertion encoded a wrong reading of the class. Replaced with the landing test in both
directions: an F5 row must compose to a path that exists, an F6 row must compose to one that does
not. A leg may only assert what the class means.

## Wiring

S6 leg `constant_directory_resolution` (`python scripts/e404_constant_directory_resolution.py
verify`); smoke leg E404 exec'd verbatim by `scripts/run_e404_smoke_leg.py` (1/1); pool card E404
closed with `result_ref`; successor **E405** filed -- *does the reader of a never-produced file fail
loudly or silently* (a missing read target is only a defect if the call chain has no guard).