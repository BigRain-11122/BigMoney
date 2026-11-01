# DIGEST 2026-11-01 r1369 (bm-b) — E348: a restored gate protects nothing in retrospect

`scripts/e348_restored_gate_retrospect.py` -> `results/state_tilt/RESTOREDGATE-2026-11-01.json`
+ `restoredgate_latest.json`. S6 leg `restored_gate_retrospect`; smoke leg E348 (standalone
runner `scripts/run_e348_smoke_leg.py`, extracted verbatim from the suite by AST).

## The question

E345 published a 9.26-hour / 10-round window in which the futures-TSMOM smoke check was absent
from this line, and classified it `nothing`: no surviving check asserted the property. That is a
statement about coverage. E348 asks the other question — inside that window, was there a value for
the gate to be wrong about, and did any clause the restore now asserts stand violated?

## Method

The five clauses the restored check literally compares are frozen from `smoke_test.py` at HEAD:
`actionable is False`, `shadow is True`, `book.gross <= 3.0` (1e-9), `generated_for_bar == panel
tail`, `staleness.stale is False`. Every commit of the window is replayed from its own tree: the
face blob and the ten `data/futures_daily/*.csv` blobs are read at that commit (one
`cat-file --batch-check`, then one `--batch`; panel tails are resolved per distinct blob, so cost
tracks blob count and not commit count), and each clause is classified held | violated |
not_evaluable.

## Readings

| | |
|---|---|
| window commits replayed | 28 (2 windows share the same removal/restore pair — 56 row evaluations of 28 commits) |
| commits in which the face existed | **0 of 28** |
| clause-states | 5 clauses x 28 commits = 140, all `not_evaluable` |
| violated clauses inside the window | 0 |
| gate and its subject | **first appear in the SAME commit** `b768f21763d` (the union merge that restored the check) |
| clauses at the restore commit | 5/5 held — the face was imported already satisfying them |
| after the restore, through `b45cb4ae6` | 279 commits, face present in 279, 0 violations |
| distinct face blobs / distinct panel tails in those 279 | **1 / 1** (`data/futures_daily/*.csv` is byte-identical at the restore and at HEAD; panel tail `2026-10-28`) |

Verdict: `nothing_to_evaluate`. The window was **empty, not clean**. And the 279 green commits
after it are **one observation repeated 279 times**: a byte-identical face against a panel that has
not printed a new bar since 2026-10-28. The restored gate has never had to decide anything on this
line.

## Five reusable findings

1. **An empty window must not be published as clean.** `nothing_to_evaluate` is its own verdict;
   folding it into `window_was_clean` would let an absence certify the very period it failed to
   cover. The mechanical tell is cheap: check whether the gate and its subject arrive in the same
   commit — read the restore's parent tree, not the restore itself.
2. **N green runs are not N observations.** Count distinct states (blob shas, panel tails), not
   runs. 279 consecutive greens over one frozen blob is a single observation; publishing the run
   count as evidence is the version of this mistake that looks like diligence.
3. **A lookup miss is not `not_evaluable`.** My first build queried the face at the boundary
   commits but not the panel, so `clauses_at_restore_commit.bar_matches_panel_tail` published
   `not_evaluable` for a panel that was in that tree the whole time. Boundary commits have to be in
   the same single batch as the range.
4. **The condition is computed before the check call.** The first selftest leg sliced the file
   forward from the check label and reported `actionable` missing from a gate that compares it —
   the `_ok` expression sits ~15 lines above. Read backwards from the label.
5. **The clause model must be exactly as loose as the gate.** `isinstance(gross,(int,float))`
   accepts `True` (`bool` is `int`), and the gate tolerates `1e-9`. Reproducing the gate's own
   expression — rather than a tidier one — is what makes the replay a measurement of the gate and
   not of the author's taste.

## Bound

This face does not re-run the suite and does not re-measure coverage (that is E345). It answers
"what would a correct gate have said", over the commits of one window plus the commits after it up
to the pinned `replay_head`. The post-restore population is time-scoped on purpose: verify
re-derives at the face's own `replay_head`, so new commits are not read as drift.

## Observation handed forward (not a claim)

The futures panel's last bar is 2026-10-28 while the round clock is 2026-11-01; the blob is
identical across all 279 commits, i.e. `data/futures_daily` has not advanced in three days. The
panel is refreshed by `scripts/update_futures.py`, a bm-a lane (R31), so this is reported, not
touched.