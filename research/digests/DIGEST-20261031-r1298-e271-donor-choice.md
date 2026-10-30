# DIGEST 2026-10-31 r1298 bm-b — E271: which donor, not just how wide

**Question.** E262 published 48 ordered (donor, recipient) pairs and E266/E267/E268 all scored
against the donor end that pair had already fixed. Nobody asked the question a reader actually
faces: for one recipient, the group offers SEVERAL foreign ends — does it matter WHICH one you
borrow, or only that you borrowed?

**Answer.** It matters, on one group of four, and the reason is arithmetic rather than taste.

| group     | p95 spread            | donors that move anything | rows moved |
|-----------|-----------------------|---------------------------|------------|
| self:200  | 1.5756 .. 1.7186 (9.1%) | none                    | 0 / 1      |
| self:60   | 1.9881 .. 2.1808 (9.7%) | none                    | 0 / 3      |
| cross:200 | 1.5255 .. 1.7816 (16.8%)| none                    | 0 / 2      |
| cross:60  | 1.9678 .. 2.2963 (16.7%)| `all_five` only (2.2963) | 2 / 6      |

Verdict `donor_choice_matters_do_not_borrow_from_this_cell`: 3 of 4 groups are donor-invariant
(so "do not borrow" is the whole instruction there), 1 is not (so there the instruction is "do not
borrow from *that* cell"). 15 of the 16 donor ends move nothing.

**The mechanism is publishable from two numbers per row.** A row flips only when its flip
multiplier `m_flip = b / band_lo` falls inside the p95 spread its group actually offers. The two
movers:

- row 9 (`era_2025_now` / cross): b −0.91134, band_lo −0.41490 → m_flip **2.1965**
- row 13 (`era_2023_2024` / star_lag1_residual): b −0.83323, band_lo −0.38965 → m_flip **2.1384**

both sit inside [1.9678, 2.2963]; every other row in every group sits outside its own spread, and
none of them moves. `flip_straddle_explains_moves = true` is the identity, verified independently by
the smoke leg (straddled set == moved set, re-derived from the published columns).

**The uncomfortable corollary.** E262's published pair choice per group is the *dominator* — and in
cross:60 the dominator (`all_five`) is the **only** donor that overturns verdicts, i.e. the least
conservative end available. A table that headlines its dominator is headlining its most aggressive
borrow. Conservative = the narrowest end. In the other three groups the question does not arise
(every donor moves nothing, so the choice is inert rather than safe).

**Control.** The own-cell donor is kept in the sweep: it reproduces each row's published
`verdict_wide` on 12/12 rows. Without it "0 moves" would be untestable — the sweep would be
measuring its own arithmetic.

**Cost / honesty.** Read-only census over one published face: no draws, no panel, no engine, no
ledger booking. Face `results/state_tilt/BANDDONORCHOICE-2026-10-29.json`,
runner `scripts/e271_donor_choice_sensitivity.py` (selftest 22/22, verify 0 problems), S6 leg
`donor_choice_sensitivity` (0.15 s), card E274.

## Pit (in-window)

`verdict_of`'s first version computed "donor ends that move nothing" as
`donor_row_pairs − moved_pairs`, mixing two populations (36 foreign row-pairs vs 16 donor ends) and
publishing a sentence that was about the wrong denominator. The summary now publishes
`donor_ends` and `donor_ends_moving_a_row` separately and the sentence reads off those. Same family
as r1280 (a delta keyed by the wrong arm) and r1234 (a count published under a measurement name):
the number was right, the noun was wrong.

## Next

`E272-TIGHT-FLIP-BUDGET` (ready) puts the tight and wide tails on one ruler; `E274-SPREAD-STRADDLE-SWEEP`
(seeded) asks whether the straddle test predicts the moved set across the whole BAND* family
rather than on this one table.