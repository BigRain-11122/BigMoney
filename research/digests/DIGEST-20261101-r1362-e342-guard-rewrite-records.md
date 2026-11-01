# DIGEST 2026-11-01 r1362 -- E342: what a rewritten gate leaves behind

**Card question.** E339 found 86 literal-count guards and exactly 2 relaxations, both rewrites of the
T+1 invariant, each explained in prose, neither leaving a machine-readable statement of what the gate
now accepts. Ask the general question over the whole guard population: (a) enumerate every
assertion-style check edited out of existence or widened in place, and split by whether the same
commit recorded the new acceptance set where a machine can read it; (b) price what a reader needs to
re-derive the old reach; (c) propose the cheapest mechanism that would have caught the c169c702 shape.

**Population.** 41 commits that delete a line in `smoke_test.py` or `Tools/s6_chain_bmb.py` (the same
commits E339 used; a rewrite of an existing check requires a deletion). 264 `check(...)` labels and
135 `LEGS` rows at head.

**Answer, in the order it was measured.**

| reading | value |
|---|---|
| events (rewrites + removals) | 8 |
| rewrites under the same name | 5 |
| — renames only (`changed_by_renaming_only`) | 2 |
| — reach moved behind helper names | 1 |
| — chain leg command changed (`audit` → `apply`) | 1 |
| — condition strengthened, direction undecidable from text | 1 |
| checks removed (all three re-added later) | 3 |
| rewrites with a machine-readable record | **0 of 5** |
| — recorded only in a commit message | 1 |
| — silent (no face, no number, no prose) | **1 — c169c702** |
| price of the 8 no-record rows | 6 commits, 23,670 diff bytes, median 3,503 |
| mechanism shipped | `Tools/guard_reach_claw.py` (staged-only, 8/8 selftest) |

**The two defects this study had to repair before it could publish anything.**

1. `check(name, ok, detail)` takes three arguments. The first draft joined `args[1:]` as "the
   condition", which reported 11 events; four of them were detail-string edits. The condition is
   `args[1]`. Over-report factor on this tree: 11 → 8.
2. A removed check is not "pinned". Three removals came back later, so `(name, condition)` exists at
   HEAD, and the first draft published `pinned_at_head=True` for all three — a statement that cannot
   be true of something that was deleted. Split into `present_at_head` (removals) and
   `pinned_at_head` (rewrites, `null` on removals).

**Why the finding generalises.** The one silent rewrite is not a corner case, it is the median shape:
a gate repaired after a false positive, the diff small, the file larger, every counting face green.
The face that would have recorded it does not exist because nothing forces one, and nothing forces one
because the cost of recovering the old reach is six commits. The claw makes the record a two-line
condition on the commit instead of a decision about whether the commit deserves one.

**Independent corroboration of E339.** E339 found the silent commit by parsing `Compare` nodes;
this study found the same commit by parsing `check(...)` labels. Different extractor, same answer,
which is the strongest form of agreement available inside one repository.

**What was not run.** The full ~335-leg suite (~35 min). The new smoke leg was extracted verbatim
(`scripts/run_e342_smoke_leg.py`) and run standalone against the published face; the new S6 legs were
run as `verify` (0 problems) and `selftest` (8/8). Solver, GPU, cloud and the lane collectors were not
touched this round.