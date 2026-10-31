# DIGEST 2026-11-01 r1348 bm-b -- E328: a stated cutoff is not a fresh one

Card: `knowledge/METHODOLOGY_ASSETS.md` E328.
Face: `results/state_tilt/STALECUTOFF-2026-11-01.json` (+ `stalecutoff_latest.json`).
Runner: `scripts/e328_quoted_number_staleness.py` (run / verify / selftest 20/20).

## The question the two predecessors left open

E326 measured whether a *consumer* carries the parameter (the cutoff) of a face it names.
E327 measured whether a `*_latest` pointer republishes it (3 of 143 "pointers" were pointers).
Both measured faces. Neither asked the question a reader has: of the numbers actually pulled out
of a face, **which come from a vintage that the same family has already outgrown**?

A face can state `evidence_cutoff: 2026-10-29` honestly and still be the wrong file when
`...-2026-10-30.json` exists beside it. That is a stated cutoff and a stale one at the same time.

## Instrument

* faces: `results/**/<STEM>-YYYY-MM-DD.json` and `<STEM>-YYYYMMDD.json`
* family: `(directory, STEM)` -- the same stem in another directory is another family
* cutoff: the first ISO date inside `evidence_cutoff` / `cutoff` / `as_of` / `asof`, else the name
  token (disclosed per row in `cutoff_source`)
* stale: `cutoff < the newest cutoff of the same family`
* quote: a **non-writer** python source names the literal basename and subscripts a quoted key
  (`["key"]` or `.get("key")`) within 8 lines of the naming line
* producer excluded: a source that binds the basename to a name and dumps that name writes the
  face; counting it would make every face self-quoted (E204/r1232, fifth recurrence)

## Readings

| | count |
|---|---|
| dated faces | 550 |
| families | 416 (68 hold more than one cut) |
| faces stating a cutoff | 491 |
| faces older than their family's newest cut | 133 |
| ... of those actually quoted by code | **4** |
| numbers read at a stale vintage | 1,430 |
| numbers that move when re-read at the newest cut | **536** (37.5%) |
| numbers with no fresh counterpart | **0** |

The four quoted stale faces:

| face | cutoff | family newest | days | numbers | move | reader |
|---|---|---|---|---|---|---|
| `etf_book_order/TICKET-2026-10-26.json` | 2026-10-26 | 2026-10-28 | 2 | 116 | 45 | `scripts/etf_book_publish_decision.py` |
| `regime5_labels/REGIME5-2026-09-30.json` | 2026-09-30 | 2026-10-19 | 19 | 0 | 0 | `scripts/regime_matrix_p0.py`, `scripts/sscombo_pit_drift_audit.py` |
| `state_tilt/ADDOS-2026-10-29.json` | 2026-10-29 | 2026-10-30 | 1 | 712 | 306 | `scripts/e298_replay_control_census.py` |
| `state_tilt/STARDIR-2026-10-29.json` | 2026-10-29 | 2026-10-30 | 1 | 602 | 185 | `scripts/e247_era_cell_power.py` |

Verdict: `quoted_numbers_are_read_from_vintages_and_move_when_the_newest_cut_is_opened`.

## What the numbers mean

* The alarm population is 133 but the live one is 4. 129 stale faces are archived artifacts that no
  code path names; publishing only "133 stale faces" would overstate the exposure by a factor of 33.
* **Every** stale quote has a fresh counterpart, so the loss is never "a number is missing" -- it is
  "the number a reader gets is not the number the newest cut prints". Re-reading is always possible.
* One face (`REGIME5-2026-09-30`) is 19 days behind and publishes **zero** numbers, so its staleness
  costs nothing measurable. Age and exposure are different axes.
* The producer/reader line matters: without the writer exclusion the population was every face's own
  module (the fifth appearance of this defect class in the family).

## Pits recorded this round

1. **The writer test must be per naming line, not per file.** Resolving every variable in a source
   against every line is quadratic; on the 2,280-file corpus the first draft did not finish in five
   minutes (`index` now takes 1.7s, 198 distinct face basenames cited in code).
2. **A scan population has to exclude the study's own output**, or the first publish adds one face
   and `verify` can never reproduce (`faces_scanned` drift, E204 family).
3. **A filename token is a fallback, not a cutoff.** `B-2026-10-09.json` states
   `panel 2026-09-30 (bars due 15:30)`; reading the name would have called it fresh.
4. Selftest legs were wrong twice before the code was: a lone face is not "one stale", and the
   fixture corpus must be passed to `build()` or the leg measures the repo instead of the fixture.

## Delivery

Chain leg `quoted_number_staleness` (verify, ~3s) and smoke leg
"product: a quoted number read from a vintage its own family has outgrown is re-measured against
the newest cut" (executed standalone: PASS). Pool: E328 done with result_ref, E329 seeded.