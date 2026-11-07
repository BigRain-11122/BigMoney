# DIGEST 20261108 r1551 bm-b — E524: the second hop past the reader

**Question.** E523 followed every handed-onward production site one hop and stopped at the reader.
A reader that checks a guard and then *forwards* the value has not guarded it — it has passed it
on. So "one hop" is a floor, not an answer to "how deep does the unguarded read sit".

**Population.** The 52 sites of the published E523 face that resolve to an in-repo reader
(`READER_REACHED`: returned-and-guarded 1, returned-and-blind 11, argument-to-a-callee-that-reads
-guarded / -blind / never-loads the rest), pinned by the upstream face sha256.

**Second hop.**
* First reader is a caller of a returning function → the parcels that caller hands onward are the
  call sites E522 already classifies `handed_onward`; they are re-scanned with E523's own rules.
* First reader is an in-repo callee → E523 already resolved what the callee does with the
  parameter (never loads / reads guarded / reads blind). The chain terminates there; no third hop
  is invented.
* First reader reads it at the call site → the chain ends at the depth E523 measured.

**Readings (2026-11-08).** 2,725 sources parsed, 22 unparseable. 52 rows followed; **36 carriers
hand a parcel onward**; **56 depth-2 parcels scanned**. Chain classes: first reader reads it 16,
second reader guards 2, **second reader blind 5**, value dies at the second reader 0, still handed
further 6, unresolved 0, left the tree at the second hop 23. Unguarded reads: **12 at depth 1,
5 at depth 2**, 0 rows carrying both. Verdict `an_unguarded_read_sits_two_hops_from_the_original_hand_on`.

**Method lessons.**
1. "Guarded" and "forwarded" are different facts. A guard on the first read, followed by
   `return f(got)`, hands the value on; any conclusion that closes with "every caller guards it"
   must ask where the value goes after the check.
2. Not every reader admits a second hop. A callee that already reads its parameter terminates the
   chain; following it again recomputes one read and manufactures a third hop.
3. An upstream class name is not a count. `receiver_sites_guarded == 0 and
   receiver_sites_unguarded == 0 and receiver_sites_handed_again > 0` falls into E523's
   "behind a guard" fallback branch; this study ignores the label and follows the actual parcels.
4. Depth is a published column, not a narrative: with `deepest_unguarded_depth` and
   `rows_with_a_read_at_both_depths`, "both depths" is a countable empty set instead of a hedge.
5. Residue stays residue: 23 values left the tree and 6 are still being forwarded — never merged
   into "safe", never recorded as zero. `verify` pins only the live-tree snapshot counters.

**Evidence.** `scripts/e524_reader_onward.py` (`run` rc0, `check` problems=0, `verify` problems=0,
`selftest` clean with a fixture corpus that proves depth 2 / depth 1 and six refused doctored
faces), `results/state_tilt/READERONWARD-2026-11-08.json` + `readeronward_latest.json`, S6 leg
`reader_onward`, smoke leg `# E524` 1/1 green and `--doctor` 1/1 red with the face restored to sha
`9ce17ea693da`, card E524 in `knowledge/METHODOLOGY_ASSETS.md`.

**Not run.** The full smoke suite (~20–30 min), the remaining S6 chain legs (update_*, market_*,
paper), `monitor.build_status` and `daily_scorecard`.