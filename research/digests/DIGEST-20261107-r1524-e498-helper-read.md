# DIGEST r1524 bm-b -- E498: which helpers hide readers across the other families

**Question.** E497 found the one twin E496 called never-opened is read by three S6 chain
producers through an in-module helper that opens its own parameter. One instance on one twin.
Is that an instance or the shape of the instrument?

**Population.** The 36 latest-pointer twins E479 froze and E496 re-classed with the mode arm.
Same population on purpose: the class deltas are then comparable to E496's row for row.

**Method (reuse, not reimplementation).** `e497.scan()` already carries all three arms. This
study swaps only the population, the candidate-token prefilter (otherwise 35 of 36 twins are
filtered out before the scan starts) and the family glob/prefix pair (so the CALL family's
`.md` writers cannot land on these twins), restores all three in a `finally`, and pins the swap
in the selftest.

**Readings.**
- 36 twins, 1553 sources parsed with a tree, 1646 candidate sources after the prefilter.
- 1 of the 2 baseline-unread twins becomes read: `results/market_clock/CALL_latest.json`
  (3 `_read_json` sites). The other stays at zero: `results/state_tilt/BASISRECOVERY_latest.json`.
  The arm discriminates; it does not repeal everything it touches.
- 11 twins that already had a literal reader gain helper read sites: 24 read sites a literal
  opener census cannot see (`_load` 7, `sha` 3, `_read_face`/`_read`/`read_callee`/`_read_json` 1
  each). So "this face has readers" is true only through the second arm on 12/36 of the twins,
  and on 11 of those the literal census got the conclusion right and the reader count wrong.

**The lesson worth carrying.** A class delta of 1 and a site delta of 24 describe the same
finding. Publishing only the class change would say "the helper blindness affects 1/36"; the
blindness actually reaches 12/36. A right conclusion is not the same as a right measurement.

**Two traps hit in-window.**
1. `e497.scan()` reads `member["kind"]` in its lane arm; a non-lane population must supply a
   neutral kind or the scan dies with `KeyError`. Reusing someone else's scanner means supplying
   the fields it reads.
2. `e483.source_tree()` resolves repo-relative paths against *its own* module `ROOT`, so a
   fixture tree is invisible until that is repointed too -- every fixture source then "fails to
   load", and that reads exactly like "no reader", which is the false negative this study exists
   to price.

**Wiring.** S6 leg `helper_read` (rc0, 0.07 s) + smoke leg `E498 ...` (1/1 green standalone,
1/1 red on a doctored face, face bytes restored). No charge, no adoption, no upstream face
rewritten.
