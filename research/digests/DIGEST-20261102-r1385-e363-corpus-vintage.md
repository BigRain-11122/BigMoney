# DIGEST r1385 -- E363: a published population has no address unless the face writes one down

Round: r1385 (bm-b) · study `e363_corpus_vintage` · face `results/state_tilt/FACEVINTAGE-2026-11-02.json`

## What was asked

r1384's carry-over: *point the corpus-equality legs that still judge a moving corpus at the pin, so
their verdict stops depending on today's disk*. The straightforward reading -- "use the newest pin"
-- turned out not to work, and measuring why is the round.

## What was measured

One corpus rule, proved against each study's own live count before any comparison, applied to four
vintages:

| study | published | live today | newest pin (replayed) | corpus at the commit that wrote the face |
|---|---|---|---|---|
| e331_pointer_only_readers | 2,362 | 2,369 | 2,365 | 2,227 |
| e335_sibling_entry_point | 2,348 | 2,369 | 2,365 | 2,227 |

Neither the newest pin nor the publishing commit reproduces either face. Verdict:
`a_published_population_is_reproducible_only_from_the_working_tree_that_ran_it`.

Why the commit is not the answer either: `pointeronly_latest.json` was last committed at `17ea91d1`
(r1363) while the face content is a working-tree artifact written later, so the commit carries 2,227
python sources against the 2,362 the face counted. A face published from an uncommitted run leaves
no address at all.

## The repair

1. `e361.stamp(files)` -- content address over the population a study scanned (order-free
   `path<TAB>sha256`, the pin's own identity function, not a second implementation).
2. `e331.build` / `e335.build` now write `corpus: {members, pin_id, rule}` in the face envelope;
   `e335.build` gained the `files=` seam it was missing (it was the only registry study that could
   not be replayed over another vintage).
3. `e363 stamp` republished both faces over `CORPUSPIN-2026-11-02.json` (commit `1244ee231290`,
   `pin_id 535be1fe...`) and recorded `corpus_source` naming that file. Populations are now 2,365
   for both, and `corpus.pin_id` is 4a75d62f (e331) / bdea39e8 (e335) -- study-scoped ids for two
   different questions, with the identical pin id beside them.
4. E331's smoke leg rebuilds over **the pin the face names**, not the newest one, and fails a face
   that names none (`_named_pin_corpus`). E335's leg checks presence, on-disk, and that the stamped
   member count equals the quoted population.

## Evidence

* `python scripts/e363_corpus_vintage.py selftest` -> **22/22**
* `python scripts/e363_corpus_vintage.py run` -> verdict
  `every_published_population_is_reproducible_from_the_pin_the_face_names`
* `python scripts/e363_corpus_vintage.py verify` -> `{"problems": [], "count": 0}`
* `python scripts/run_e331_smoke_leg.py` -> **1/1 PASS** (25 pointer-only readers over 20 families,
  31 sources with an invisible tail) -- the leg text extracted verbatim from `smoke_test.py` and
  executed inside `vars(smoke_test)` (E355: no hand-built namespace)
* `python scripts/run_e335_smoke_leg.py` -> **1/1 PASS** (2,365 sources read both ways, 1,425
  differing, E334 delta 29/30 at max abs diff 4.0)

## Limits, stated rather than implied

* Two studies are in the registry; a census without a `files=` seam cannot be replayed over another
  vintage at all and is out of scope here.
* The corpus keeps growing while the round runs (2,365 -> 2,369 within the hour), which is exactly
  why the stamp, not the live count, is the thing a leg should compare.
* `e363` is **not** wired into the S6 chain: one run re-cuts four vintages (~2-4 min) and its answer
  only moves when a face is republished.
* The full 277-leg suite was not re-run this window; the two changed legs were extracted and
  executed verbatim instead.