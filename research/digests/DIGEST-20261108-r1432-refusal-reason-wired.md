# DIGEST 2026-11-08 r1432 (bm-c) — the adopted reason was never printed

## The question

r1431 decided that the calendar's refusal reason should be `years_for_half` (the ruler
r1429 elected on fixtures, adopted because switching can only ever refuse MORE), and
explicitly left production alone:

> PRODUCTION UNCHANGED on purpose: this is the adoption EVIDENCE; wiring the supply
> calendar to print the new reason is its own next-round action.

So for one round the desk owned a decision that no reader could see. The operator board
still printed `nobond_vt08_adopted: CONDITIONAL via Y4_top2_share` — a number produced
by the ruler r1426 disqualified, and a sentence that reads like "the money is too
concentrated" when the actual finding is "the money was made early".

## What changed

`scripts/supply_calendar_face.py`:
- `elected_ruler()` imports `etf_book_admission_ruler_election.elect()`; the ruler is
  never retyped here and never read off the book being judged.
- `read_phase_gate` carries each book's trusted `caliber_adjudication` block
  (`median`, `line`, `state`) and counts degenerate phases (A5 input) from the
  receipt's own published `net_sum_pct` / `gross_sum_pct`.
- `elected_reason(row, elected)` is pure given the elected name and returns one of
  `refuse` / `admitted` / `indeterminate` / `cannot_adjudicate` / `not_on_record` /
  `no_election`. Only `refuse` and `admitted` carry a sentence.
- `--check` re-derives every sentence from the row plus the PUBLISHED `elected_ruler`,
  so a hand-typed reason is red.

`Tools/fill_ladder.py` `explain` prints the same clauses, because the ladder board —
not the calendar page — is where an operator reads "no lawful supply".

## Live reading (2026-11-08 16:0x)

```
ready=0 floor=3 | catalog 23 rows: spent 22 / blocked 1 / available 0
  -> EXHAUSTED_NO_LAWFUL_SUPPLY
  | calendar: NO_CANDIDATE_PASSES_CALENDAR (4 candidates, 4 refused)
  | reason (years_for_half): nobond_vt08_adopted refused at years_for_half median 2 vs line 3 (FAIL);
    nobond_base refused at ... median 2 vs line 3 (FAIL);
    nobond_vt08_floor_050 refused at ... median 2 vs line 3 (FAIL)
```

Three of four refusals now name the elected ruler and its own line. `all_classes_published`
has no phase set, so it prints `no phase set, ruler not re-read` — it is not given an
inherited sentence.

The verdict words are unchanged: 4 refused before, 4 refused after (r1431 A2).

## Self-catches

1. **`build(elected=None)` could not express "there is no elected ruler"** — the
   parameter default `None` meant "not supplied", so the code fell back to the live
   election and the `no_election` leg read `refuse`. Fixed with a module sentinel
   `_AUTO`; the leg is what found it, not review.
2. **The `not_on_record` note flooded the operator summary** — an existing leg that
   asserts the summary text went red with `| reason: only has no years_for_half reading
   on record`. A note about missing instrumentation is not a reason about the book, so
   the face now publishes `elected_reasons` (actionable) and `elected_notes` separately;
   the md page prints both, the summary prints only the first.
3. **`from scripts import ...` died under direct execution** — `sys.path[0]` is the
   `scripts` directory, not the repo root, so the lazy import of the adoption module
   raised `ImportError: unknown location`. The module now inserts ROOT on sys.path, the
   same pattern the adoption module already used.

## Reusable

A gate's refusal reason is an output with its own consumers; "adopt the reason" is not
done when the decision is signed, it is done when every surface that prints the reason
prints the adopted one — and the number of such surfaces is larger than the number of
places the decision names.