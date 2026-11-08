# DIGEST 2026-11-09 r1599 bm-b — E568: does git still hold a pre-receipt round's legs table?

**Question.** E567 judged 28 of 878 printed chain sentences and could not judge 809, for one
reason: the receipt corpus starts at r1204 and its join needs a receipt to name the round. It
noted that a table is a property of the runner source at that round, and that git has every
version. This round tested that note.

**Population.** E567's `the_round_carries_no_receipt_in_the_corpus` class, read from its own
build (imported, not copied): 809 sentences over 727 distinct (machine, round) pairs.

**Two arms, priced separately.**
* `arm_canonical_path` — guess `Tools/s6_chain_bm<X>.py` at that round's commit. **19 rounds.**
* `arm_tree_scan` — list the commit's tree and keep any `results/` or `Tools/` path whose basename
  carries both an `s6` and a `chain` token plus that round's number. **192 rounds**, of which 173
  are found by the scan alone.

**Answer.** Git does still hold the table, but only for 26% of the rounds. 206 of the 809
sentences become judgeable: 175 equal the table of their round, 1 is below it and says it is a
subset, **22 are below it and read as the whole chain**, 8 are above it. 569 rounds have no chain
script naming the round in that commit at all; 34 have one whose legs table could not be read.

**Three lessons.**
1. "Git has it" is only a fact once it can be taken out: the same note yields 19 rounds by
   guessing and 192 by scanning, and the guessing arm cannot see its own blindness.
2. A round number is shared across the fleet; the table is not. The first build read bm-c's script
   as the witness for a bm-b round — 8 of the first 10 "above the table" rows were that mismatch,
   and machine-scoping cut 92 above-rows to 8.
3. Count inside the container. The `$legs = @(...)` block has two item shapes
   (`@{n=...}` and `@('name','script','args')`); counting "lines starting with @(" and subtracting
   the opener read thirty-leg rounds as twenty-nine for eight consecutive rounds.

**Not claimed.** The 8 "above the table" rows were not individually triaged (their pair may not be
a leg count at all); the 569 no-script rounds are published as unrecoverable, not as an estimate.

**Evidence.** `scripts/e568_old_chain_table.py` (build / check / check-fast / selftest 23/23),
`results/state_tilt/OLDCHAINTABLE-2026-11-08.json` + `oldchaintable_latest.json`, S6 leg
`old_chain_table` (check-fast, rc=0 0.35s, 206/206 witnesses re-read), smoke leg #E568 +
`scripts/run_e568_smoke_leg.py` (`--doctor` red as designed).
