# E232 + E233 — the ledger carried a marker that no gate could see, and three chain records were named after flags (r1343 bm-c)

**Cards:** E232, E233 in `knowledge/METHODOLOGY_ASSETS.md`.
**Code:** `smoke_test.py` (`_hunk_state`, `_marker_fragments`, one new leg),
`Tools/s6_chain_bmc.py` (argument parsing + atomic record write).
**Faces:** `results/_r1343bmc_s6_chain.json`, this digest, the new smoke leg.

## Why this round exists

The round opened 9 commits ahead and 3 behind `origin/main`: two machines had each kept
counting rounds from the same base (`e30dab6dd5` = bm-b's r1251 receipt). The worktree also
carried 49 modified faces and two untracked product docs from windows that committed
nothing — including a 2026-10-29 production card and order ticket that were already priced
on that bar.

So the round had three parts, in this order: recover the dead-window estate as found (not
re-typed), merge the two lines, then measure something new.

## The merge, by class (not by one side)

- 8 conflicting faces. Six are generated (`compute_audit`, `data_lag_audit`,
  `regime_state`, `update_status`, `_attrition_guard_scan`, `machine-health`): took the
  local side and let the chain legs re-derive them — a face that describes a book is
  produced, not merged (r1290 rule). All six parse as JSON after resolution.
- `runnable_pool.json`: the two sides turn out to be **semantically identical** (698
  entries, identical ids, identical order, every other key equal) — the conflict was a
  formatting artefact, so the local blob was taken verbatim rather than re-serialised, to
  avoid 1.9MB of churn that would read as a real edit.
- `knowledge/METHODOLOGY_ASSETS.md`: append-only, resolved by union. bm-b's trailing card
  was **E225** and bm-c already owned E225, so bm-b's card was kept verbatim under **E231**
  with the renumbering stated in its own heading. Nothing was dropped from either side.

## The defect this round found (E232)

The pre-commit claw (r1305) only inspects markers being *added*. At HEAD `c07483b9`,
`knowledge/METHODOLOGY_ASSETS.md` carried a lone `||||||| parent of ed40e56da3` line at
4062 — it had survived the eight hours in which five cards were appended below it, because
no leg reads committed blobs for markers.

The gate that closes it is a balance test, not a name list: open `<<<<<<<` -> optional
`|||||||` -> `=======` -> `>>>>>>>`, and anything outside that state machine is a fragment
(unclosed hunk at EOF included). A probe file that quotes a whole hunk stays legal;
`=======` as a markdown underline cannot trip it. The one scope decision is printed rather
than hidden: `results/_*` are raw diff captures, six of them holding 103 unbalanced marker
lines by design, and they are skipped by the repo's own underscore convention.

Live reading: **0 fragments at HEAD 0034e48e9, 1 at c07483b9** (the ledger). The gate is
red exactly on the case it was written for, which is how it is verified rather than
asserted.

## The defect this round found (E233)

`Tools/s6_chain_bmc.py` took the first surviving `sys.argv` token as the round number, so
`--all` became a filename: three committed records are named after flags
(`_r--all`, `_r--round`, `_rrun`). The round that ran is unrecoverable from those names and
a second run of the same kind silently overwrites the first — a chain record is the whole
S6 sweep's evidence. The record is now also written `tmp + fsync + os.replace`, so an
interrupted dump can no longer leave a stub that reads as a legitimately short chain.

## What the chain and suite had to say

The S6 chain (78 legs) and the smoke suite were both launched detached with file redirects
(RAM free 0.4–1.4GB of 23.9GB all window, CEO desktop) and are recorded verbatim in the
round report, not summarised from expectation.

## Honest note

A pre-existing chain from a dead window (started 17:49) was re-deriving faces when this
round opened; it was live (product mtimes moving), so it was left alone per r1241. This
round later killed it while trying to stop a duplicate chain it had itself started with the
old argument parser — the wrong PID was matched. Nothing was lost (the same legs re-ran in
this round's own chain), but it is recorded because the kill was a mistake, not a decision.