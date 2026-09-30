"""r483 bm-a rebase-resolution record (documentary -- not for re-run).

Collision: bm-c r281 (e2350eb89, committed 17:34:54) and bm-a r483 both
reorganized CODELY.md in parallel windows from the same r482 base
(11,564B) -- bm-c merged 6 pointer rows -> 2 compact rows + added the r281
lesson row + removed the r482 corrupted fragment (with archive record);
bm-a archived 7 settled pitlaw entries verbatim + added merged pointer row
+ the r483 track-adoption row. Orthogonal transforms, both legal.

Resolution (bigmoney-conflict-resolve skill, memory-union class per
classifier; r327 entry-level bidirectional coverage law -- NOT byte-concat
because both sides edited in place):
  final tree = base User/Feedback rows
             + bm-c merged Project pointer row (base 6+7+8)
             + bm-c r281 lesson row (new hot entry)
             + bm-a merged pointer row (7 archived hot entries)
             + bm-a r483 track-adoption row
             + base Reference rows 15/16/17 (r276 pointer / 10KB law / flow)
             + bm-c merged Reference pointer row (base 18+19+20)
  -> 15 lines, 5,836 bytes (<10KB hardline), coverage check: every entry
     line of base/origin/mine sides in final-tree UNION archive = 0 missing.

research/memory-archive/202609.md (UNKNOWN class -> append-only md union):
  final = base + bm-c appended block + bm-a appended block (commit-time
  order 17:34 -> 17:4x); line-level zero-loss check: 0 lines missing from
  either side; final 300,605 bytes. The r482 corrupted-orphan fragment is
  verbatim-preserved in BOTH the bm-c block (their archive record) and the
  bm-a block (true-text re-append from git HEAD plus the earlier
  double-backslash-escape artifact correction note).

Post-resolve reconcile: ZERO-DRIFT on market_clock/call_latest; drift
recorded as-is per law on compute_audit + gate_attrition (known lane-mirror
lag faces, same as r481 precedent -- observation-phase data, not failure).

Concurrent-session half-product handling: research/BANNED_DIRECTIONS.json
(written 17:43:27 by a live local session wiring the D-41 banned-direction
gate) was swept by one git add -A mid-round, then REMOVED from the r483
commit via pre-push amend (r280 pre-push-window law) and left untracked in
the working tree for its owner session to commit together with its
Tools/banned_direction_gate.py; its PREREG_TEMPLATE sec.0.5 edit was
stashed (stash@{0} 'r483 concurrent-session template edit') before the
rebase and popped back after push.
"""
