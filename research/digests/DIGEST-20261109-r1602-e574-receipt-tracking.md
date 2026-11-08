# DIGEST-20261109-r1602-e574-receipt-tracking

Card E574 (r1602 bm-b). Question: for every chain receipt on disk, does git carry it, does a
round-report row name it, and is the round it belongs to reachable at all?

Answer, and the reason the first draft of this card would have been wrong: the untracked receipts
are not lost carriers, they are carriers switched off. `git check-ignore -v` shows
`.gitignore:256` with pattern `_r[0-9]*` matching **213** of the **331** receipts on disk, so
"untracked" there is deliberate policy and the round-report row is the designed witness. The other
**118** were added before that rule existed.

Three classes (first match wins): carried_by_git 118, named_but_not_carried 26, vanishing 187.
Of the 187: 185 belong to bm-b's own rounds (bm-c 2), 180 rounds are at least named by a commit
subject, and **7 round numbers no commit names at all** — r1221, r1225, r1342, r1366, r1374,
r1445, r1515. Separately, **7 file names are not integer rounds** (`_r--all`, `_r--round`,
`_rr1483leg`, `_rrun` x2, `_rspread_floor`, `_rverify`) — the ad-hoc-test-receipt family E562
recorded; published as its own flag, never folded in as zero.

Three things measured rather than assumed:
1. "Not in git" has opposite meanings depending on whether a `.gitignore` rule matches it. Without
   `check-ignore -v` the honest reading (187 runs whose only witness is a row that does not name
   them) is indistinguishable from a broken commit habit 331 files wide.
2. A round number in a commit subject is a label on the round, not a witness for that receipt.
   Publishing `round_named_by_a_commit` beside `cited` is what keeps "the round exists" from being
   read as "this run left evidence".
3. The citation token has a wide and a narrow form: `r1246bmb_s6` (the receipt's own token) matches
   26 receipts, `r1246bmb` (the round token) would match 90. The 64 in between name the round and
   not the receipt, and are published as `run_token_cited` rather than merged into `cited`.

Bound published, not claimed: static only. `git ls-files` is a name face, so a tracked path whose
bytes are gone is not distinguished here (`on_disk` and `tracked` are separate columns); the report
corpus is `logs/iteration-loop/round_reports*.md` only; nothing was executed, no receipt rewritten,
and `.gitignore` untouched.

Evidence: scripts/e574_receipt_tracking.py (build/check/verify, selftest 16/16),
results/state_tilt/RECEIPTTRACK-2026-11-08.json, RECEIPTTRACK_latest.json,
knowledge/METHODOLOGY_ASSETS.md card E574.
