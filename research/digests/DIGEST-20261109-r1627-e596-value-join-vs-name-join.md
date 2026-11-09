# DIGEST r1627 bm-b — E596: a date-keyed join cannot replace the name join

**Study**: `scripts/e596_value_join_vs_name_join.py` (selftest 28/28, `check`/`verify` problems=[])
**Face**: `results/state_tilt/VALUEJOINNAME.json` (+`-latest.json`), evidence_cutoff 2026-11-09
**Pool card**: E596 burned (done) — seeded E600

## The question

E594/E595/E598 all priced *name* joins: a reader names a face, then asks for a spelling, and the bar
travels under whichever name the writer chose. The pool card asked the complementary question: if a
consumer joined on **the date the face states** instead of on the key name, would it land on the
pricing bar, on the decision bar, on several dates at once, or on nothing?

## The one number that decides it

The choice is only visible on a face that states **both** a pricing-role and a decision-role bar.
Of 13,641 JSON faces under `results/`+`docs/`:

| class | faces |
|---|---|
| carries no bar name | 4,984 (outside the population) |
| names a bar but states no date | 6 |
| states one date | 8,017 |
| states several dates | 173 |
| unreadable (>1 MB or parse failure) | 461 |

**18 faces state both roles, and on 18 of 18 the two roles state different dates**
(`docs/live_book/LIVE-BOOK-20261109.json`: `pricing_bar` vs `book_decided_at`;
`results/etf_book_order/TICKET-2026-10-2x.json`). One date cannot stand for both bars, so on those
faces the **name join is load-bearing** and must not be replaced by a date-keyed lookup.

Verdict published on the face:
`the_pricing_bar_and_the_decision_bar_state_different_dates_on_some_face_so_a_value_join_cannot_replace_the_name_join`

## Two defects the window found and fixed

1. **A key name can belong to two families.** `ticket_bar` is both a pricing spelling and an as-of
   spelling; a `{key: family}` inversion silently collapsed it to whichever family was written last,
   i.e. asserted a role the dialect face does not assert. Fixed by publishing every family a name
   belongs to (`as_of+pricing`) and listing `names_in_more_than_one_family` on the face. The leg that
   caught it was a *fixture*, not the real repo — the real repo simply had no `ticket_bar` face.
2. **A sample must carry its own omitted count.** Printing all 8,017 single-date faces would triple
   the face, so 200 are printed; the guard reconciles `published + sampled_out == by_class`. When the
   sampled-out count was first left unpublished, the two "class X does not re-derive" checks passed
   silently (r1261 family).

## Provenance chain

- `scripts/run_e596_smoke_leg.py` — PASS 1/1; `--doctor` (one both-role face is rewritten so its two
  roles share a date) goes **1/1 red**: the leg can fail.
- `smoke_test.py` leg E596 (inserted, idempotent `scripts/_e596_wire.py`).
- Sibling studies: E594 (dialect join), E595 (alias blast radius), E598 (pointer bar demand),
  E599 (redirect-target bar, ready), E600 (does a date identify one face at all — seeded).