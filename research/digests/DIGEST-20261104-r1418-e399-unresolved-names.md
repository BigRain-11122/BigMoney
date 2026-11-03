# DIGEST r1418 (bm-b) -- E399: the 98 unresolved published keys are six bills, not one

**Face:** `results/state_tilt/UNRESOLVED-2026-11-04.json` (+ `unresolved_latest.json`)
**Script:** `scripts/e399_unresolved_names.py` (run / verify problems=[] / selftest 28/28)
**Card:** `knowledge/METHODOLOGY_ASSETS.md` E399

## The question

E397 resolved the whole published key population (884 keys: 862 read half + 22 write-only) and
published `names_resolved_to_no_file = 98` as a bare count. A residual count says nothing about
whether the instrument is narrow or the population contains things that were never paths.

## The arms

| arm | what it does | ran |
|---|---|---|
| A0 | the resolver actually in use (`e383._resolve`; index skips `Money02`/`legacy`/`media`/`.codely-cli`) | yes |
| A1 | same suffix rule, index skips only `.git`/`__pycache__` | yes |
| A2 | `git log --diff-filter=D --name-only` | **no** -- published unavailable, see below |
| A3 | form: repo-relative path vs bare basename vs bare token vs template vs absolute | yes |
| A4 | neighbourhood: parent exists / parent is a FILE / same-stem sibling under another date | yes |

## Result

| class | n |
|---|---|
| bare basename whose directory is a runtime variable | **52** |
| template or glob (`FOO-%s.json`) | 13 |
| bare token (`arm`) | 1 |
| found by the wider index (`Money02`) | 1 |
| repo-relative, absent inside an existing directory | 16 |
| repo-relative, directory does not exist | 14 |
| repo-relative, "directory" path is actually a FILE | 1 |

- never a path claim: **66** · instrument gap: **1** · real repo-relative absences: **31**
- same-stem sibling under another date: **0** (the date-shift hypothesis is dead, not plausible)
- share of the population that is unresolved: 11.09% (98/884); of those, 5.9% of all keys are fragments
- sibling check: WALKAMBIG-2026-11-03 published 98, this re-derives 98 exactly (`agree: true`,
  `same_cutoff: false` -- the sibling is a different cutoff and is disclosed as such)

## Verdict

`the_residual_is_classified_but_the_deletion_arm_could_not_run_on_this_partial_clone_so_the_absences_inside_existing_directories_stay_unattributed`

The verdict is recomputed from the summary by `decide()`, and the smoke leg refuses a stored verdict
that does not re-derive.

## What went wrong in-window (and how it is published now)

`git log --all --diff-filter=D --name-only` hung the first burn. This repo is a promisor/partial
clone: touching a ref whose trees are not materialised starts a lazy `git fetch` + `git index-pack
--promisor` that never returns (r1224 family). Two orphan fetches were left behind by the killed run
and had to be killed by pid. Pinning the arm to `HEAD` did not help -- the same lazy fetch fires.

So A2 is off by default, runs only with `BIGMONEY_E399_HISTORY=1` on a complete clone, and otherwise
publishes `available: false` with the reason. Consequence: rows that are absent inside an existing
directory are `repo_relative_inside_an_existing_directory_but_no_file`, and the face says the
deletion arm could not attribute them -- it does not claim they never existed.

## Product bug surfaced (not fixed here)

`results/autofill_state.json.tmp/autofill_state.json` -- `autofill_state.json.tmp` is a *file* in the
tree and the census published paths beneath it as if it were a directory. A4 asks "is the parent a
file?" separately from "does it exist?", which is what makes this visible.

## Wiring

- `Tools/s6_chain_bmb.py` leg `unresolved_names` (rc 0, 0.6 s)
- `smoke_test.py` leg E399 + `scripts/run_e399_smoke_leg.py` (verbatim extract, 1/1 PASS)
- pool: E399 done with `result_ref`; successor seeded
- no published face, pointer or key was rewritten