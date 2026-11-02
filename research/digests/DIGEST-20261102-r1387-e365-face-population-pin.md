# E365 -- a published-face population can be pinned and replayed (r1387)

**Question (E364's queue head).** E364 closed with "can a published-face population be pinned and
replayed like a source population -- stamp E328's faces and replay through its existing seam?"

**Answer.** Yes, and the seam was already there (`e328.build(root=, files=)`). What was missing was
fetchable bytes for the outputs, plus two facts nobody had recorded.

## What the population actually is

| | |
|---|---|
| faces in E328's own scanner | 591 (593 twenty minutes earlier, 587 in E328's published summary) |
| families / directories | 453 / 117 |
| supplied by git (tracked and clean at HEAD) | 526 (89.00 pct) |
| untracked | 21 |
| tracked but dirty | 44 |
| written to the inline store | 65 members / 586,732 bytes compressed |
| not UTF-8 | 1 (`e25_cash_leg/TREND-a0653f-20261021.json`, UTF-16LE, `FF FE`) |
| refuse the study's own loader | 1 (the same face) |

## Three findings, each one measured rather than reasoned

1. **A count is not an address.** E328 publishes `faces_scanned: 587`; the population it walks held
   593 rows at 17:5x and 591 rows at 18:1x. Sixty-eight faces have a stated cutoff and 10 of E328's
   13 summary keys are stable, but the population itself moves under the study, so the published
   number cannot be turned back into members by anyone. The mtime heuristic that tried to name the
   additions over-counted (9 named, delta 4) and is published with that caveat.
2. **The address must be byte level.** The first draft inherited E362's text rule (sha256 over
   LF-normalised UTF-8 text); the replay then convicted `TREND-a0653f-20261021.json`, which had not
   moved at all -- it begins `FF FE`, so a surrogateescape read and a `replace` decode of a git blob
   give two different digests for identical bytes. One non-UTF-8 member is enough to make a text-level
   pin unsound for a directory walk.
3. **A pin must not count its own publisher.** The first real run pinned 593 members and then refused
   its own `FACEPOPPIN-2026-11-02.json`: it entered the population before the store re-read the disk,
   after the face had been rewritten. E319, one layer lower: a pin that includes its output is not
   idempotent, and an address has to be.

## The replay, and what moved

`FACERERUN-2026-11-02.json`: 591/591 members rebuilt from **526 git blobs + 65 stored members**
(no work-tree read), re-hashed, `pin_id` recomputed and equal. E328's own `build` was then executed
over the hydrated vintage:

* `hydrated_members` 591, `replayed_population` 591 == `pinned_population` 591;
* 13 summary keys compared, **3 moved** -- `faces_scanned` 593→591, `families` 455→453,
  `faces_with_stated_cutoff` 532→530 -- and `population_delta_explained_by_own_faces = True`
  (delta 2 == the 2 excluded own faces);
* **10 of 13 keys did not move**, including every derived number: `stale_faces` 137,
  `quoted_numbers` 1430, `numbers_that_move` 536, `numbers_equal` 894, `stale_faces_quoted` 4;
* the reader corpus's content moved between pin and re-run with the **same member count (2373)**, and
  no derived number moved, so the reader drift is measured as harmless here rather than blamed.

## Files

* producer `scripts/e365_face_population_pin.py` -- `stamp | rerun | check | selftest`, selftest 17/17
* pin `results/state_tilt/FACEPOPPIN-2026-11-02.json` + `facepoppin_latest.json`
* store `results/state_tilt/face_store/FACESTORE-e241540f0347c52a.json`
* re-run `results/state_tilt/FACERERUN-2026-11-02.json` + `facererun_latest.json`
* chain leg `face_population_pin` (`... check`, ~8 s, no work-tree read) + one smoke leg
* card `knowledge/METHODOLOGY_ASSETS.md` E365