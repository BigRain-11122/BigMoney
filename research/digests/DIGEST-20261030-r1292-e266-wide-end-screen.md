# E266 -- a donor above the row is not yet a screen: it needs the row's own side

**Face** `results/state_tilt/BANDSCREEN-2026-10-29.json` (+ `bandscreen_latest.json`)
**Runner** `scripts/e266_wide_end_screen_holdout.py` (run / verify / selftest 26/26)
**Source** E262's 48 published ordered pairs, re-read. No band rebuilt, no shuffle drawn, no bill.

## The claim under test

E265 wrote the wide-end rule as a per-row screen: a row's verdict flips at the multiplier
`t = |b| / max(|lo|, |hi|)`, so *any* donor whose p95 exceeds `t` flips that row. E264 then ranked
the 12 read rows by that threshold and found both rows E262 moved inside the top 3, with a
third-closest row that did not move. E266 asks the screen question directly, over every published
pair: is "donor p95 > t" exactly the set that moved?

## Answer

No. The written screen flags **18 of 36** comparisons and only **2** move -- precision **0.111**.

| screen | predicted | tp | fp | fn | exact |
|---|---|---|---|---|---|
| S1 `donor_p95 > t_max_end` (as written) | 18 | 2 | 16 | 0 | no |
| S2 `donor_p95 > t_max_end and own_p95 < t_max_end` | 1 | 1 | 0 | 1 | no |
| S3 `min(donor,own) < t_side < max(donor,own)` | 2 | 2 | 0 | 0 | **yes** |

The 16 false positives are two different failures and they are not interchangeable:

- **12** are rows whose own end had already rejected nothing -- the row was *inside* its own band,
  so no donor can take a rejection away from it.
- **4** are rows their own end *does* reject, left alone only because the donor is not wide enough
  **on the side the row actually sits**.

That second class is the interesting one, and it is why S2 alone is not enough. S2 (guard on the
row's own end, same max-end threshold) removes every false positive but then **loses one real
move** -- the very row the published screen reads as "inside at its own end".

## The threshold is side-dependent, and half the pool is on the narrow side

`max(|lo|, |hi|)` is the flip multiplier only when the row sits outside on the **wider** end. A row
below a band whose lower end is the narrow one crosses at `|b| / |lo|`, which is *larger* than
`|b| / max(|lo|, |hi|)`: the published form understates how far such a row sits from flipping.

**18 of the 36** comparisons carry a side-dependent threshold (12 in `cross:60`, 3 each in
`cross:200` and `self:60`). This is not a corner case; it is half the readable pool.

The two moves E262 published, side-aware:

| row | arm | donor | t_max_end | t_side | own p95 | donor p95 | direction |
|---|---|---|---|---|---|---|---|
| era_2023_2024 `star_lag1_residual` | cross:60 | all_five | 2.1384 | 2.1384 | 2.0161 | 2.2963 | rejections_lost |
| era_2025_now `cross` | cross:60 | all_five | 1.9583 | **2.1965** | 1.9678 | 2.2963 | rejections_lost |

The second row is the one S2 misses: its own p95 (1.9678) sits *above* the max-end threshold
(1.9583) and *below* its own-side threshold (2.1965), so the max-end guard reads it as "inside at
its own end" while it is in fact outside and the borrowed donor breaks it.

## What this changes for anyone borrowing a wide end

The screen is not "is the donor's number bigger than mine". It is three things at once:

1. the row must already be rejected by **its own** end (`own_p95 < t_side`);
2. the donor must cross **the same** threshold (`donor_p95 > t_side`);
3. the threshold has to be read on **the side the row sits beyond** -- `|b|/|lo|` below the band,
   `|b|/|hi|` above it -- not off the wider end.

## Resolution (published, not implied)

36 comparisons carry 2 positives. Exactness at n = 2 is a **consistency check on the published
pairs, not a validated screen**. What the face does publish honestly:

- the whole comparison set is re-derivable (`comparison_rows`, 36 records, one per pair x row);
- the confusion matrices are recomputed by the smoke leg from those rows, not carried as prose;
- the counterexample list *is* the written screen's false-positive set, row for row;
- the one-direction class (`rejections_invented`) is empty here, so the screen's ability to predict
  the *direction* of a flip is untested at this sample size.

## Pit (born here, worth the ink)

The first draft of the counterexample list labelled **all 16** false positives "its own end had
already rejected this row" -- a single explanation copied onto two mechanistically different
classes (E207 name-is-semantics family). Four of them were outside at their own end and simply not
reached by the donor on that side. The `why` field now derives from `own_verdict` instead of being
written once.

Second: `base` is not a stable key name across these faces -- E262's rows carry `base`, the
E259-style source rows carry `band_draws`. Reading only `base` silently produced **0 comparisons**
on the fixture (empty comparison set, and an "exact" screen over nothing), which is the r1261
"both curves equal because neither ran" shape one file over. `base_of()` now reads either key.

## Method card

`knowledge/METHODOLOGY_ASSETS.md` **E266**.