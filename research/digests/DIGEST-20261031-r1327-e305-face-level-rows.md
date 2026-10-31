# DIGEST 2026-10-31 r1327 bm-b — E305: the eight face-bound at-risk rows are all withdrawn

**Face:** `results/state_tilt/PRECISIONGAP-2026-10-31.json` (+ `precisiongap_latest.json`)
**Producer:** `scripts/e305_face_level_row_pricing.py` (run / verify / selftest 25/25)
**Study:** E305_face_level_row_pricing · **Verdict:** `none_of_the_face_level_rows_is_at_risk`

## What was asked

E299 graded 62 numeric comparisons in `smoke_test.py` and called 29 at risk. 21 were graded on the
field's own measured decimals. The other 8 were graded on the **face's coarsest printed quantum**
because no leaf under the key the leg reads could be found. A face-level bound is an upper bound on
resolution, not a measurement of the field — the card asked, for each of the 8: is the key absent,
spelled differently, or read from a nested record the leaf walker truncates?

## What was found

All 8 are withdrawn. None is at risk from rounding, and each carries a named reason.

| resolution | n | what it is |
|---|---|---|
| `in_a_sibling_face` | 3 | the key is absent from the face the row was priced against and present in another face **the same leg names**; 2 print at 15 dp (finer than a 1e-9/1e-12 tolerance), 1 is an integer and carries no fractional quantum |
| `not_a_number_in_priced_face` | 3 | the key is there as a `list[0]/list[2]`, a `dict[8]`, and a `dict[17]/list[2]`; a container is not a printed number |
| `not_a_number_in_a_sibling_face` | 1 | every value is a `bool` — a verdict flag, not a measurement |
| `written_inside_records` | 1 | `session_open` lives in `per_trader/<id>/detail[]`; the t35 open-fill face has six `zero_pending` traders on 2026-10-30, so the list is empty **today** and the key is not absent by design |

Read another way: the census's fallback was not wrong about the arithmetic, it was wrong about what
it had measured. 21 of 29 stand on a measured field; the remaining 8 stand on a face-level bound that
turned out to be answered by a sibling face, a container, or a record list that happened to be empty.

## Pits

1. **A fallback needs its own name in the same sentence as the count.** E299 correctly published
   `n_at_risk_on_face_level_bound_only = 8`, but the headline "29 at risk" reads as 29 measurements.
   Splitting the sentence is cheaper than splitting the number.
2. **"Absent from the face being priced" usually means "present in the sibling face the same leg
   names".** The join that matters is per-Leg, not per-face: two of the three sibling rows already
   had a `key_profiles` row carrying 15 dp, sitting one field away from the at-risk row that said the
   field could not be found.
3. **Dropping containers is right for a quantum and wrong for an absence question.** E299's leaf
   walker skips dict/list values on purpose. The scan that answers "is the key there" must keep them,
   or "no printed number" and "no key" become indistinguishable — 3 of the 8 rows are exactly that.
4. **A record list can be empty on the vintage that was read.** The producer writes `session_open`
   into per-trader detail rows; on a day with no pending entries, the same key that is a float on a
   filled day is simply not in the file. Absence has to be answered from the producer's text, not
   from one day's face.
5. **Mutation evidence (4/4 caught):** flipping the verdict, dropping a row and its count, stripping
   a row's reason, and claiming a row at risk with no printed number behind it all turn the new smoke
   leg red; the baseline passes again after the bytes are restored.

## Wiring

* `Tools/s6_chain_bmb.py` leg `face_level_row_pricing` (verify, 1.7 s, rc=0)
* `smoke_test.py` leg E305 (extracted verbatim and run standalone: PASS; 4/4 mutations caught)
* `knowledge/METHODOLOGY_ASSETS.md` card E309