# Seat faces: is "not a position" a measurement, or a word list?

Evidence: `results/` as it stands, generated 2026-11-16T00:42:02 by `scripts\seat_subject_census.py`.

## Verdict

**SEAT_SUBJECT_CONFIRMED** -- 252 of 252 seat-classified ADMIT faces carry the shapes of a seat and none of the shapes of a book; 0 wear a seat shape while describing a book.

## What was asked, and what came back

| question | evidence the face had to show | faces that showed it |
|---|---|---|
| is there a seat ledger? | integer `rows` + a `W<n>` wave tail | 252 / 252 |
| is there a band? | a `lo..hi` pair that parses as two numbers, lo <= hi (the thinnest face carries 1, the widest 13) | 252 / 252 |
| does anything carry a price series? | a >=20-point numeric list under any field name | 0 found |
| do any rows describe names rather than seats? | >=3 rows whose keys are not seat words | 0 found |

The 254 unpriced admissions split by shape into 252 seats (all 252 probe-tier, 0 published), 2 registration gates, 0 book claims and 0 face(s) that wear a seat shape while describing a book.

## The word list is not the proof

Four synthetic faces carry every seat mark **and** a book -- one spelled `holdings`, one as a 30-point `book_path`, one whose band is prose instead of numbers, one whose band runs backwards. The word list `BOOK_KEYS` sees **0/4** of them; the shape test sees **4/4** (`scripts\event_exec_gate.py selftest-audit`, legs L20-L23).

On this tree's own unpriced admissions the two readings disagree on **0** face(s): 0 where the shape test finds a book the word list never sees, 0 the other way. That is the whole claim: the seats are out of scope because their shapes say so, not because nobody wrote `positions`.

## Honest

- The test is shape-level, not semantic. A book that held only a four-name list spelled with seat words (`{"hop": ...}`) would still pass; today no face does, but the vocabulary is a boundary, not a proof.
- "No curve" cannot see a book whose price series is stored as one scalar per bar in separate fields; nothing in this tree does that today.
- The seat family is 252 probe faces and 0 published faces: these are research waves admitting a parameter band, not products.
- `seat_lookalikes` counts faces the audit's marks call a seat and this census reads as a book; it is the disagreement number, not a second opinion on the same question.
- The census reads the same live `results/` the audit walks, so the two numbers move together by construction; the agreement is reported, not counted as independent confirmation.
