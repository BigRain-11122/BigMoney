# DIGEST r1601 bm-b -- E573: the sentences below their round's legs table, and what the round itself says

**Card**: E573 (from E568). **Machine**: bm-b. **Cutoff**: 2026-11-08.

## Question

E568 recovered a legs table from git for 192 pre-receipt rounds and found 22 printed chain
sentences whose denominator sits below that table while the sentence reads as the whole chain.
Arithmetic was never the issue; provenance is. If the round deliberately ran a subset (an
`--only`, a checkpoint, a resumed window), the sentence is honest and merely quoted from a
second run. So: does anything in that round's own report say it ran a subset?

## Answer

No. Zero of the 22 sentences, and zero of the 7 sibling rows the same rounds print
(closeout/postscript/addendum), carry a chain-scoped subset declaration. The bare words a reader
might take for one (`family`, `subset`, `partial`, `--only`, ...) do appear in 10 of the 22 rows
-- and every single one of the 10 is about a research family, a leg *seed* family, or a
gate family, not about the legs scope. A marker-word scan would have called 10 of 22 rounds
declared; the phrase rule calls 0.

The mechanism does exist in the code: 13 of the 22 rounds' own chain scripts (read out of git at
the commit E568 named) contain a narrowing token, and 11 of those carry a real scope switch
(`--only`); the other 2 only slice a list (`where-object`). The scripts' legs tables were
re-counted from the same blobs: 18 of 22 readable, and all 18 equal E568's published table (0
disagreements), so this study does not inherit the earlier count on faith.

## What this changes

A round whose denominator is below its table is silent in the report *and* has the mechanism to
narrow -- so "the prose understated the chain" and "the round ran a subset" cannot be separated
from report text alone. The witness that would settle it is the invocation (did the run pass
`--only`, and with what), which no row records. That is exactly E575.

## Boundaries

* Whether the run actually passed the flag at run time is not claimed; it is the unnamed witness.
* The 4 rounds whose legs table could not be re-counted from the blob keep E568's number and are
  not re-judged here.
* `sibling_rows` are attributed by the round token in column 3 of a timestamped row; a
  continuation line is not a row (`round_of_row` returns None for it).

## Evidence

`scripts/e573_silent_chain.py` (build/check/verify, selftest 15/15) +
`results/state_tilt/SILENTCHAIN-2026-11-08.json` + `silentchain_latest.json` + S6 leg
`silent_chain` (rc=0 0.05s) + smoke #E573 + `scripts/run_e573_smoke_leg.py` (`--doctor` red as
designed).
