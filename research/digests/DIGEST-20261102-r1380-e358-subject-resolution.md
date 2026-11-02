# DIGEST 2026-11-02 · r1380 · E358 unfolded subject resolution

**Question.** E351 (r1372) left 55 of 92 `product:` smoke gates as `unresolved_subject` and
published the bound as "out of scope". Are those subjects uncomputable, or just unfolded?

**Face.** `results/state_tilt/SUBJRES-2026-11-02.json` (+ `subjres_latest.json`), study
`E358_unresolved_subject_resolution`, producer `scripts/e358_subject_resolution.py`
(`build` / `verify problems=[]` / `selftest 16/16`).

**Answer.** 40 of the 55 name a constant file all along; 8 read whatever a directory holds; 7 name
no file at all. Every resolved subject folded at depth 1.

| class | gates |
|---|---|
| frozen_subject | 31 (all mature: ≥50 commits present) |
| live_subject | 9 |
| dynamic_subject (directory listing) | 8 |
| no path expression (numbers only) | 7 |
| never_evaluated | 0 |

Green-by-freeze share: **16.2% → 48.1%** (37 of 77 gates that name a subject).

**Why the first draft was wrong, three times over.**

1. A `-- <paths>` filter on the replay window graded each face over the commits that touched *it*
   (88 instead of 300) — the r1261 shape: a short series that looks like a frozen one.
2. E351's series starts at `None`, so a face older than the window reads `distinct_states == 0`
   and was published `never_evaluated`; seeding with `git ls-tree <oldest>^` turned 9 of those
   into (correctly) frozen rows. A file created inside the window still starts `None`.
3. `os.path.join("data", "futures_daily", "*.csv")` folds to a string ending in `.csv` and was
   counted as a face, then reported "never on disk". Wildcards are now their own class.

**Bound published, not claimed.** 5 of the 31 frozen subjects are dirty in the working tree: the
committed blob is not the bytes the gate read, so their "frozen" status describes git, not the run.
The 8 listing subjects (`os.path.join(_dir, _files[-1])`) can never be replayed from git at all.

**Wiring.** S6 leg `subject_resolution` (verify re-derives folding + classes, ~5 s) and smoke leg
E358 (graded structurally: partition, folded-implies-resolved, verdict re-derives, folding helper
still resolves a constant join). The leg was executed standalone by
`scripts/run_e358_smoke_leg.py`, which lifts its text out of `smoke_test.py` and runs it in the
suite's own namespace (E355 discipline).