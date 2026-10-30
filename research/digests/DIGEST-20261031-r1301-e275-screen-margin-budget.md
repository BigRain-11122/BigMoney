# DIGEST 2026-10-31 r1301 bm-b — E277: a cleared row is not equally cleared

Face: `results/state_tilt/BANDSCREENBUDGET-2026-10-29.json`
Runner: `scripts/e275_screen_margin_budget.py` (selftest 25/25, verify 0 problems)
Card: `knowledge/METHODOLOGY_ASSETS.md` E277 (pool id `E275-SCREEN-MARGIN-BUDGET`; card and pool
ids drift in this repo, recorded in the card)

## Why this exists

E274 turned E271's mechanism into an exact screen: a row moves only if its flip multiplier lands
inside the multiplier range its (leg, base) group offers. That is a binary reading. It says a
cleared row is safe and it says nothing about how much room is left. A screen that leaves one row
with 2% of margin is a different instruction from one that leaves every cleared row room.

## What was measured

For each of the 12 measured rows of E274's wide axis, two published numbers (the flip multiplier
and the range the group offers) give a budget: the share of the flip threshold the group's widest
offered multiplier already eats. Rows are then sorted into five zones.

| zone | n | meaning |
|---|---|---|
| straddles | 2 | the flip sits inside the offered range — exactly the two rows the guard screen publishes as moved (9, 13) |
| spent_by_build | 4 | the flip sits at or below the group's **tightest** offered multiplier (8, 10, 11, 15) |
| spent | 2 | outside the range but the widest end already reaches ≥90% of the flip (7: 0.9340; 14: 0.9648) |
| open | 4 | room left (0: 0.7373, 1: 0.6587, 6: 0.8175, 12: 0.5474 spent shares) |
| untested | 0 | — |

## What it says

- **The cleared set is not one reading.** 10 rows read "outside" and they split 4 open / 2 spent /
  4 spent-by-build. The two open rows with the most room have spent 54.7% and 65.9% of their
  threshold; the two spent rows have spent 93.4% and 96.5%.
- **The budget names rows nothing else flags.** BANDNEAR1's `near_one_dependent_rows` is empty and
  BANDMARGIN's guard moves are exactly the two straddlers, so the six near-spent rows (2 spent +
  4 spent-by-build) are named by no other published screen. The budget is not a restatement and it
  is not corroboration.
- **The zone is a statement about the range, not a movement prediction**, and that is pinned:
  none of the six near-spent rows moved in the published donor sweep. `spent_by_build` is the
  sharpest version — the tightest end of what the group offers is already past the row's flip, and
  the row still did not move, because E271's sweep moves a specific borrowed quantity, not the
  bare multiplier.

## Controls

- **Incidence**: the straddle zone reproduces the guard screen's moved set `{9, 13}` exactly, so
  the face is reading the same population as the screen it extends (selftest + smoke leg).
- **Arithmetic**: every `budget_spent` re-derives as `hi / m_flip` to 1e-12, and the zone block is
  the row list grouped rather than a second tally (smoke leg re-derives both independently).
- **Provenance**: `m_flip` is imported from `e274` (which re-derives it from the published `b` and
  band edges), not retyped, so the two faces cannot drift apart.

## Caveats

- 12 measured rows, one book (5 members), one cutoff. No power statement is made beyond that.
- The 4 unreadable rows of the family (`pre2020_four`, `era_2020_2022`) stay untested; they are
  carried through the axis as rows with no flip, never as zeros.
- Pool id vs card id: the study ran as `E275-SCREEN-MARGIN-BUDGET`; the card is E277 because E275
  and E276 were already taken by the r1299 and r1300 cards.