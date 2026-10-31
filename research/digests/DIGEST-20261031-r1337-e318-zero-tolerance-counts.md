# DIGEST 2026-10-31 r1337 bm-b -- E318: the zero-tolerance headline is half counts

**Face** `results/state_tilt/ZEROTOLPRUNE-2026-10-31.json` (+ `zerotolprune_latest.json`)
**Runner** `scripts/e318_count_named_gate_leaves.py` -- `run` / `verify` (0 problems, 7 checks) /
`selftest` (25/25)
**Chain** `Tools/s6_chain_bmb.py` leg `zero_tolerance_prune` (rc=0, 0.08 s)
**Smoke** leg 105 "the zero-tolerance headline is half counts" -- executed standalone, PASS
**Card** `knowledge/METHODOLOGY_ASSETS.md` E318

## Question

E317 (r1336) published: *289 faces / 1108 gate leaves, the unit missing on 1047 of them, and **122
published gates carry a zero tolerance** -- a zero tolerance cannot be met by any numeric
comparison.*  E317 pruned `frac` because a name is not a measurement.  It then read every remaining
tolerance-named leaf as a gate.  One of those names is `n_tolerance_named_not_gate`.  Does the
headline survive its own rule, and what is a surviving zero actually gating?

## Answer

| step | gate leaves | exactly-zero |
|---|---|---|
| E317 as published | 1108 | 122 |
| after the count-word guard | 1046 | **69** |
| survivors on this programme's own study faces (E299/E305/E308/E312) | -- | 68 |
| survivors on a real data face | -- | **1** |

* 62 leaves are counts (5.6% of the census): `n_tolerance_named_not_gate` x55 plus six absence
  counters (`pairs_no_leg_tolerance`, `faces_with_no_tolerance_name_at_all`,
  `ordering_between_copies_no_tolerance`, `comparisons_not_graded_tolerance_from_face`,
  `faces_with_tolerance_named_not_gate_only`, `n_cross_face_rows_exceeding_tolerance`) and one
  `numeric_values`.
* 53 of those 62 are zero, i.e. **43.4% of the headline is counts of gates**, not gates.
* The rest of E317 barely moves: readable-in-place 33 -> 33 (share 2.98% -> 3.15%), substitution-span
  leaves 225 -> 219, max span unchanged at 19.5935 decades, whole-decade counts 68 -> 68.  The
  guard lands exactly where the headline was.
* The unpruned control reproduces E317's five published numbers to 1e-4 (the span is published to 4
  decimals), so the movement is the guard, not a re-derivation.
* All 69 survivors sit in blocks that publish floats. 68 of them are census faces describing somebody
  else's gate: E312's `GATEOPERANDS`, E308's `GATETOL`, E299's `PRECISIONCENSUS`, E305's
  `PRECISIONGAP` -- the earlier members of the same method, which E317's exclusion list (E313-E317
  only) did not cover.
* The single data-face survivor is `results/shortline/t18_deep_manifest.json` `gates.GA.tolerance`:
  a known-answer reproduction check that publishes its own observed maximum
  (`max_abs_close_diff_worst = 0.0`), so the reader can see the exact-equality test and it passes by
  construction on a byte-identical re-read.  A zero tolerance is legitimate exactly where the
  compared number is a **copy** rather than a computation -- and no other surviving zero can tell
  the reader which one it is.

## Pits (all caught in-window)

1. **Substring vs token, in the guard built to fix a name-vs-measurement defect.** The first guard
   took `law.written_law_tol` (1e-8, a real acceptance tolerance on `results/sina_mf_accept.json`)
   because the string `written_law_tol` contains `n_`. Pruning a real quote is worse than the
   over-count (E208). Guard is token-level; leg L6b pins the false positive.
2. **The control's tolerance is not a free parameter.** The recount first failed against E317 at
   `max_substitution_span` 19.59352806507836 vs a published 19.5935 -- a 4-decimal publication, not
   a disagreement. Comparing floats at 1e-9 makes every honest control look broken.
3. **Ordering bug in the build**: the provenance lists were used by an identity check before they
   were computed (UnboundLocalError). Caught by `run`, which is why `run` and `selftest` stay a
   pair.
4. **The smoke leg read two fields from the wrong object** (`count_named` / `residual_gates` are
   top-level on the face, not under `census`) and failed five sub-checks. The standalone harness
   extracted the leg text out of `smoke_test.py` so the shipped leg is the leg that ran.

## Boundaries

Reads E317's published rows; opens a face only to shape the block of a surviving zero. E317's own
selection remains the population under test -- a wider tolerance vocabulary is a different question
and is not claimed here. No re-scan of the 289 faces, no new gate semantics.