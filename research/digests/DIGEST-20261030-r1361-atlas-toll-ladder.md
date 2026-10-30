# r1361 bm-c -- the atlas ordering is a zero-cost object, and the width knob is the one with a stable sign

**Date** 2026-10-30 · **Round** 1361 · **Machine** bm-c · **Dept** 研究/策略

## The question r1359 left open

r1350 read the phase atlas at one toll (10bp/side) and published "cadence is the quotable
knob, width sits inside the band". E256/E257 then bracketed the toll — 0 / 5 / 10 / 20 / 40
bp per side, same 12-cell grid (names {3,5,8,12} × cadence {10,20,40}) — but every reader so
far consumed those arms one at a time, and `etf_book_phase_atlas_arms` reads them for the
**band** ("the band follows the decision count, not the toll").

Nobody had asked the complementary question, which is the one that decides whether the atlas
sentence may be quoted at all: the atlas judges its ordering by *between-cell spread > median
cell band*, and **both** quantities move with the toll. At what toll does the ordering stop
clearing its own phase noise, and is that decay monotone?

Both newly stocked rows (`E272-ATLAS-COST0` at 14:05, `E272-ATLAS-COST20` at 14:20) were on
disk and unread. The read-back needs no engine.

## Readings

| toll bp/side | spread pp | band pp | clears band | argmax | cadence effect | width effect |
|---|---|---|---|---|---|---|
| 0 | 6.92 | 6.75 | **yes** | n8/R10 | +5.54 | +0.69 |
| 5 | 6.06 | 6.71 | no | n8/R10 | +4.71 | +0.73 |
| 10 | 5.22 | 6.68 | no | n8/R10 | +3.89 | +0.77 |
| 20 | 3.55 | 6.60 | no | n8/R10 | +2.10 | +1.14 |
| 40 | 3.00 | 6.47 | no | n8/**R40** | **−1.32** | +1.56 |

* **The ordering is a toll artefact.** Spread falls 6.92 → 3.00pp, rank corr with the toll
  **−1.000**; the median cell band barely moves (6.75 → 6.47pp). The two series cross at
  **1.045 bp/side**, i.e. the whole 12-cell ordering is worth about one eighth of the toll the
  production card is charged (8bp/side, where interpolated spread is 5.56pp against a 6.70pp
  band). The atlas's own verdict is `CONFIG_ORDER_EXCEEDS_PHASE_NOISE` at exactly one rung —
  cost zero — and `WITHIN` at every positive toll.
* **The cadence knob inverts.** Faster rebalancing (R10 vs R40) is worth +5.54pp/yr at zero
  cost and **−1.32pp/yr at 40bp/side**, and the argmax cell migrates from n8/R10 to n8/R40
  between 20 and 40bp. "Faster is better" is the most toll-exposed claim in the grid.
* **The width knob is the only stable direction.** Wide-minus-narrow goes +0.69 → +1.56pp with
  rank corr **+1.000** — it strengthens at every rung and never flips sign. But even its
  largest value (1.56pp) is a quarter of the band (6.47pp), so the sign is quotable and the
  size is not. That is the exact inverse of r1350's headline: width was the knob dismissed as
  "inside the band", and it is the only knob whose *direction* survives the toll ladder.
* **The buffer ladder is one draw from a grid.** Seven strengths (k = 0, 0.02, 0.05, 0.10,
  0.20, 0.30, 0.40) at the production toll: spread 5.22 / 5.21 / 5.60 / 6.34 / 5.67 / 6.25 /
  5.89, band flat 5.89–6.68. Exactly **one** rung (k=0.30) clears the band, on a non-monotone
  sequence. The drift of spread with k (rank corr 0.714) is carried entirely by rungs that
  never clear — so it is not a dose, and the single crossing is not a rule (r1325).

## Consequence published

No width/cadence sentence from this grid is quotable at 8bp/side. What survives is
**directional only**: wider is worth more at every toll. Everything numeric — the +5.54pp
cadence premium, the argmax cell, the buffer optimum — lives below 1bp/side, i.e. in a world
the production card does not trade in.

## Mechanism

`scripts/etf_book_atlas_toll_ladder.py` (selftest 32/32):

* rung membership comes off each face's own `audit` block (`cost`, `buffer_k`), never off the
  file name — a file called `cost20` whose audit says otherwise is whatever its audit says;
* a face that moves **two** knobs at once (`buffer_k05_cost05`, `buffer_k05_cost20`) is
  excluded with its reason rather than averaged into a one-dimensional ladder;
* spread and band are re-derived from the per-cell scalars; the crossing is interpolated
  linearly between adjacent rungs; the production toll is interpolated (no arm sits at 8bp);
* the verdict is recomputed from the frozen constants in `check()`, and the smoke leg
  re-derives every rung's spread from the **source arm faces** — a ladder row that agrees with
  itself but not with the arm it summarises is red.

Card: `knowledge/METHODOLOGY_ASSETS.md` **E275**. Face:
`results/etf_book_atlas_toll_ladder.json` (+ `.md`). Chain leg: `etf_book_atlas_toll_ladder`.