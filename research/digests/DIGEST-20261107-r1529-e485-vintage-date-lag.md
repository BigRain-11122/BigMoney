# DIGEST 2026-11-07 r1529 bm-b -- E485: the two one-day vintage lags are two different things

**Face** `results/state_tilt/DATELAG-2026-11-07.json` (+ `datelag_latest.json`), 571 rows.
**Study** `scripts/e485_vintage_date_lag.py` (selftest 47/47, check/verify clean).
**Card** E485 in `knowledge/METHODOLOGY_ASSETS.md`.

## What was measured

E484 reconciled E472's 571 unread vintage members and found 5 name-vs-payload date disagreements,
two of them a true one-day lag (both name 2026-10-21, both payload 2026-10-20). E484 split the five
by hand and called the lag "a late-run stamp or a misname". E485 measures it.

Every member whose *name* states a date — ISO or compact `YYYYMMDD` — is compared with the closest
date its payload states. The witness field and its tier are published per row:

- `frozen` — one of the seven names E480 froze, at the payload's top level
- `non_frozen` — another structured string field at depth <= 2 whose value is a bare date
- `prose` — a date mentioned inside a longer free-text string

Family spans come from the siblings' **names**: a payload date before the family's earliest name
date is a data date, not a write date.

## Reading

| class | files |
|---|---|
| same_day | 400 |
| payload_one_day_earlier | 2 |
| payload_one_day_later | 0 |
| payload_outside_one_day | 0 |
| payload_before_family_span | 0 |
| not_a_json_object | 165 |
| ambiguous_name (range names) | 4 |

402 comparable (278 ISO names / 124 compact), same-day share **0.995025**. Witness tiers:
**frozen 388 / non_frozen 12 / prose 2**. Every compared payload date sits inside its own family's
span — neither lag is a cross-era data date.

## The two lags are not the same fact

1. `results/_w280bmc_20261021_probe_receipt.json` — the only witness is the **prose** field `probe`,
   whose text says "2026-10-20 ~01:4x"; the payload has no date field at all.
2. `results/e24_ladder_weighting/WEIGHTING-20261021.json` — the witness is the **frozen** field
   `evidence_cutoff = 2026-10-20`, i.e. the data cutoff, written into a file dated by its run day.

`cause_verdict = the_one_day_cases_split_between_structured_fields_and_free_text`.

Writer evidence for every non-same row: **write_context 4 / names_only 11 / no naming source 156**
(the 156 are the non-JSON and range-named members, which have no JSON writer by construction).
Neither one-day file has a single source that names it in a write context: the names are composed by
round scripts (`_r1509_pool_update.py`, `_r1509_report_row.py`) from a date variable, so no literal
appears in a write statement.

## Three reusable laws

1. **A one-day gap must be published with its witness tier.** A date inside a paragraph and
   `evidence_cutoff` are different facts; collapsing them into "late-run stamp or misname" hides
   which one to fix (the name, or the field).
2. **The denominator must name "has a date and the date can be read".** 0.995 holds over 402; putting
   the 169 incomparable members into the denominator would print a meaningless 0.70 (E392 family).
3. **"The name is one day late" is not repairable at a write site.** Both cases have 0
   write-context sources — the name is composed, so a rule that looks for the literal and declares
   "no writer" when it finds none is blind to this shape (E495's three writer shapes, same family).

## Boundaries

- One representative date per payload (closest, best tier first); the full set is published per row.
- Prose witnesses rank with structured ones for date selection, but the tier is always in the row.
- Writer evidence is source-level (literal + a write verb within two lines), not dataflow: a composed
  path in another module is invisible, so `write_context = 0` means "no source names it in a write
  context", never "no writer exists".