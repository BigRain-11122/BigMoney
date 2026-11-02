# DIGEST 2026-11-02 r1382 -- the census leg that was both the judge and the writer

## What the round opened on

The detached suite from r1381 finished: **269/277 PASS, 8 FAIL**, and all eight failures
carried the same sentence -- "the summary does not re-derive". They are the census legs
(e299, e298, e323, e325, e327, e328, e329, e332): each publishes a census over the
repository's own sources and faces, and each leg rebuilds it and demands equality.

Two separate defects were hiding inside that one sentence.

## Defect 1 -- the equality was demanded against a corpus that cannot be reproduced

Measured, not assumed, on leg 298:

    face  evidence_cutoff 2026-11-01   summary.faces_scanned 138  mirror_files_excluded 113
    fresh evidence_cutoff 2026-11-02   summary.faces_scanned 145  mirror_files_excluded 120
    verdict equal, controls 70 == 70, every control's kind and basis equal

The corpus these censuses count is a live working tree that other lanes write all day.
Seven of the eight faces carry *today's* cutoff and a different population, so the date
cannot pin anything: 2340 files became 2356, 2338 became 2354, 566 became 587. A leg that
demands `published_summary == rebuilt_summary` on such a subject is unsatisfiable by
construction, and it fails for a fact about the corpus, not for a defect in the face.

The repair is a gate, not a loosening: `_census_corpus_moved()` reads the population size
out of both documents. If the two builds counted the same corpus, **every** equality stays
strict -- verdict, summary, rows, re-pricing. If they did not, the numbers are pinned to a
population that no longer exists and the leg publishes a `[DRIFT]` line with both sizes,
while every population-independent assertion (partitions sum, classes in the frozen set,
rows agree with counts, at-risk rows carry their basis) keeps running unchanged. A corpus
that **shrank** is still a conviction: growth is a fact about the corpus, losing files is not.

## Defect 2 -- the checker was the writer of the face it checked

`e328`, `e329` and `e332` implement `build(root=None, outdir=None, ...)` as
`target = outdir or OUTDIR`. A smoke leg calling `m.build()` therefore **republished** the
published face, then compared the bytes it had just written. Observed live: my first
verification pass wrote `stalecutoff_latest.json`, `twovintage_latest.json` and
`invisibletail_latest.json` at 13:34-13:37, which made three of the eight legs pass for the
wrong reason -- the comparison was against its own output (r1261 family, one layer up: it
was not two empty series, it was the same series twice).

The repair is `_census_rebuild_scratch()`: rebuilds land in a temporary directory and are
deleted, so the verdict cannot be produced by the act of checking. Proof of the fix is the
negative: the published faces were restored from `HEAD` at 13:39:50 and both later
verification passes left `git status` clean on all three.

## How the eight legs were verified

The legs live inline in `smoke_test.py`, inside a 12,000-line `main()`. The full suite is
~35 minutes, so a round cannot run it twice. Each leg's own text was therefore extracted
(balancing the `check(...)` call so a nested `try/except` cannot truncate the slice),
prepended with `if 1:` and executed in the suite's namespace with a stub `check()`.
A re-implementation would prove the copy.

    leg 95  PASS  leg 298 PASS  leg 308 PASS  leg 311 PASS
    leg 327 PASS  leg 328 PASS  leg 329 PASS  leg 332 PASS
    8 drift lines, 0 failing assertion

Two legs (329, 332) take minutes each because they re-scan ~2,300 sources; they were run
detached with unbuffered output rather than inline.

## What this round does NOT claim

* The three faces were restored from `HEAD`, so a lane that held a newer *uncommitted*
  edition of `stalecutoff_latest.json`, `twovintage_latest.json` or
  `invisibletail_latest.json` had it overwritten before the restore and it is not recovered.
* Reproduction of a published census on today's disk remains **unmeasurable**, not
  verified. Pinning a corpus by content digest (and teaching `build()` to accept a snapshot)
  is the real repair and is not in this round.
* The other six published reds of the r1381 log were not touched.
* The full suite was not re-run; the eight legs were exercised verbatim and standalone.