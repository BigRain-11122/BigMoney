# DIGEST — r1460: a refusal has to come with a distance

**asof** 2026-11-09T04:4x · **round** r1460 (bm-c) · **fact** results/etf_book_calendar_distance.json

## The question the red flag never answered

compute_audit has printed, for many rounds:

```
supply_candidates.verdict = AGENDA_DEBT
agenda_cause              = calendar
verdict                   = NO_CANDIDATE_PASSES_CALENDAR   (n_candidates 4, n_refused 4)
```

Three different situations print that same word, and they demand opposite actions:
a candidate that passes next month (wait), one that passes in a year (wait longer),
and one that no year's return can fix (open another family). r1415 built the gate,
r1420 gave it a third word, r1425 proved Y4 is an annual-Sharpe test in disguise,
r1459 pointed at supply as the next block. None of them asked what a desk asks of
a red line: **how far away is it**.

## What the distance is

Every calendar check is a function of seven annual numbers. Six are finished; the
partial current year is the only one that can still move. So each refusal has

- a **distance** in this year's return (the smallest value that makes all four
  checks pass), found by *running* the frozen rule in 0.01pp steps, never by algebra;
- a **hurdle** for the months left: with `c` of the year's four cohorts booked,
  the remaining cohorts must return `(1+v*)/(1+v0) − 1`.

## Readings (published receipts only, nothing re-priced)

| candidate | supply face says | this phase reads | distance | hurdle |
|---|---|---|---|---|
| nobond_vt08_adopted | CONDITIONAL (Y4) | CONDITIONAL (Y4) | **1.24pp** of 2026 | remaining 1 cohort must return **1.22%** |
| all_classes_published | refused (Y4) | refused (Y4) | 6.80pp of 2026 | — |
| nobond_base | UNADJUDICABLE_PHASE (median top2 0.8207) | **ADMIT** | not claimed | — |
| nobond_vt08_floor_050 | refused | no yearly block published | — | — |

The headline: **the desk's adopted book is 1.24pp of 2026 return away from the
concentration line it fails** — smaller than the 1.08pp it was over the line when
r1418 first read it, and now expressible as one number a reader can watch
(2026 must end at ≥ 3.14%, i.e. the last cohort must make +1.22%).

## The defect this file caught in itself

`nobond_base`'s single-phase yearly block reads **ADMIT**, while the supply face
reads it **UNADJUDICABLE_PHASE** because the top-2 share moves across the five
decision phases (median 0.8207, spread 20.82pp). Printing "one candidate already
passes" from the single-phase block would have converted "cannot tell across
phases" back into "already passes" — the E206/E319 class, one layer up. The face
now carries `reading_agrees_with_supply` and reports `READINGS_DISAGREE` without
claiming a distance on the untrusted reading.

## What is not claimed

- No book is re-priced; every yearly row is copied from a published receipt.
- The partial year is not annualised. The hurdle is the return needed over the
  remaining cohorts, not an annualised rate.
- A finite distance is not a forecast: it says what this year must deliver for
  the gate to pass, not what it will deliver.
- `UNREACHABLE_THIS_YEAR` is only printed when the failing check sits on a
  completed year or on the completed-years share; it is a statement about the
  gate, not about the book's future.
- Re-cutting the book is the other way out and is not priced here.

## Wiring

- script `scripts/etf_book_calendar_distance.py` — selftest 14/14, `run` 0.4s, `--check` CHECK_OK
- S6 leg `calendar_distance`, placed immediately after `supply_calendar` (its input)
- smoke legs: selftest + `--check`
- card E466 in knowledge/METHODOLOGY_ASSETS.md