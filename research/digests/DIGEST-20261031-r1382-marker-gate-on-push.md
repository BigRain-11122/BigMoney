# r1382 bm-c — the only marker gate sat on `commit`, and the surgery push never commits

**Live incident.** `knowledge/METHODOLOGY_ASSETS.md:7316` carried a lone
`||||||| parent of 552f00ce84 (round 1381: ...)` line into the r1381 commit at
09:42. It sat in a ledger every reader opens for 44 minutes, until a *dead*
window's smoke run flagged it at 10:14. The pre-commit claw was working that
day: staging a file with a base marker makes the hook exit 1 (probed live at
10:33).

**Why the gate did not fire.** The claw only runs on `git commit`. The surgery
push path every recent bm-c round used is "cherry-pick onto the origin tip,
then push", and `rebase` / `cherry-pick` / `commit-tree` do not run pre-commit —
the hook file says so in its own header ("Rebase replays are not affected").
Two live incidents (r1304, r1381) entered through exactly that door, and both
were caught late by a reader rather than at the writer.

**The fix.** The gate moves to the one step every path shares: the push.
`Tools/git_claw.py` gained `marker_fragments()` and `marker_violations()`, and
`check_push()` now refuses a push whose AMCR blobs carry a marker fragment. The
installed pre-push hook already calls `check_push`, so this needs no new
installation and no name list. Scope mirrors the smoke leg: `results/_*` scratch
captures quote raw diffs on purpose and are excluded; a whole balanced
open/base/sep/close hunk (a document quoting a conflict) stays legal; a lone
`|||||||`/`=======`/`>>>>>>>` or an unclosed hunk is refused.

**One rule, two gates.** `smoke_test._hunk_state` now delegates to
`git_claw.marker_fragments` instead of restating the state machine (the r1374
law: a copy of a rule is the next defect). The delegated signature returns
`(fragments, state, opened_at)`; smoke keeps its 2-tuple contract.

**Evidence.** `Tools/git_claw.py selftest` 38 → **44/44 PASS** (lone base
refused / balanced quotation passes / `results/_` capture out of scope /
unclosed hunk refused / the refusal names file and line / pure-function legs).
Live fire: `check_push(origin/main, r1381)` returns **rc=1** naming
`knowledge/METHODOLOGY_ASSETS.md:7316 |||||||` — the gate would have stopped the
real push that shipped it.

**Limits.** The gate lives on this machine's hook; `--no-verify` remains the
documented escape hatch (reason required in the round report). Fragments already
in history are not rewritten by this gate; r1381's is removed by a line-level
edit in this same commit.
