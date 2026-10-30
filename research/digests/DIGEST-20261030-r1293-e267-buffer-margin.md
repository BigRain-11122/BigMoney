# E267 -- a margin is not a substitute for the row's own side

**Face** `results/state_tilt/BANDMARGIN-2026-10-29.json` (+ `bandmargin_latest.json`)
**Runner** `scripts/e267_screen_buffer_margin.py` (run / verify / selftest 36/36)
**Source** E266's 36 comparisons (E262's 48 published pairs x measured recipient rows), re-read.
No band rebuilt, no shuffle drawn, no bill.

## The question

E266's bracket screen is exact on the 36 published comparisons -- and it is a knife edge: a donor
`0.0001` above the row's own-side threshold counts exactly as much as one `0.3` above it. Anyone
acting on the screen has to decide how much clearance to demand. E267 measures that cost on the same
comparisons, without drawing anything:

```
margin = donor_p95 / t - 1        the clearance a donor has over the flip threshold t
rule with buffer b:  donor_p95 > t * (1 + b)
```

Four rules are swept: with and without the own-side guard E266 found necessary, on both threshold
forms (`t_side`, and E264/E266's `t_max_end`).

## Answer

A buffer cannot buy precision here. Every non-move that the row-side rule flags sits on a row whose
**own end had already rejected nothing** -- and one of them clears its threshold by **246%**, so no
buffer that keeps a move can reach it.

| rule | b=0 flags | tp | fp | precision | best buffer precision | exact at any b |
|---|---|---|---|---|---|---|
| single, `t_max_end` (E266 S1) | 18 | 2 | 16 | 0.111 | 0.143 @ b=0.0553 | no |
| guarded, `t_max_end` (E266 S2) | 1 | 1 | 0 | 1.000 | 1.000 @ b=0 | **no -- loses the move** |
| single, `t_side` | 14 | 2 | 12 | 0.143 | **0.154 @ b=0.0443** | no |
| guarded, `t_side` (E266 S3) | 2 | 2 | 0 | **1.000** | 1.000 @ b=0 | **yes, for every b ≤ 0.0454** |

Three readings that decide the question:

1. **The buffer's whole upside is 0.143 -> 0.154.** The peak sits in a b window **0.00116 wide**
   (`0.04429` to `0.04545`) and it is bounded by one non-move below it and one move above it. That is
   not an operating point, it is the gap between two adjacent published clearances.
2. **Separability fails on the largest non-move, not the nearest.** The nearest non-move clears by
   `0.0443`, the nearest move by `0.0455` -- so a naive read says "a tiny buffer separates them". The
   binding constraint is the **largest** non-move: `2.4595` (246% of its threshold). A buffer big
   enough to clear every non-move (`b = 2.46`) clears every move too. `separation()` publishes the
   whole ordering, `separable=false`, and a leg pins that separability binds on the largest non-move.
3. **The guard already tolerates a buffer; the buffer without the guard never works.** The guarded
   side rule is exact at b=0 **and stays exact for every b up to `0.0454`** (12 exact b values
   published). So the buffer is not an alternative to the guard -- it is a free tightening *on top
   of* the guard, and once the guard is in place the buffer buys nothing it did not already have.

## The two moves, in clearance terms

| row | arm | donor | margin over `t_side` | margin over `t_max_end` |
|---|---|---|---|---|
| era_2023_2024 `star_lag1_residual` | cross:60 | all_five | 0.0739 | 0.0739 |
| era_2025_now `cross` | cross:60 | all_five | **0.0455** | 0.1726 |

These are the "0.074 and 0.045 above t" the card predicted from E266's published rows -- reproduced,
and now placed against the non-moves that bracket them. The block of non-moves at clearance
`1.235, 1.445, 1.452, 2.385, 2.450, 2.460` are all `own:inside` rows (self:60 era cells): donors that
are 2.5x the threshold and still move nothing, because there is no rejection to take away.

## Method notes (published, not implied)

- **The b grid is exact, not sampled.** A ladder only changes where a clearance crosses the line, so
  the breakpoints are every observed clearance value on either threshold form (43 values) plus a
  frozen coarse grid. The published curve is therefore exact on this population.
- **b ≥ 0 only.** A buffer demands *more* clearance; accepting a donor below the threshold is a
  different rule, not a weaker setting. Negative clearances exist in the data and are deliberately
  not swept (leg-pinned).
- 36 comparisons with 2 positives: the curve is a consistency read on published pairs, not a
  validated operating point. `first_b_with_no_true_positive = 0.0739` says the last move dies exactly
  at its own margin -- strict `>` means a donor sitting on the line has zero clearance.

## Pit (born here, caught in-window)

The first version wrote **two different quantities under one key**: `summary["moves"]` was the count
(`len(moved)`) and then, 12 lines later in the same dict literal, the list of move records. The list
won, so the count never shipped, and the new smoke leg's `isinstance(..., int)` assertion failed on a
bare `moves` key -- which is exactly the E207 "name is semantics" family, and the reason that leg
type-asserts headline counts instead of only checking values. Fixed to `moves_published` / `moves_detail`
(the E266 convention), and the smoke leg now rejects a bare `moves` key outright.

Second, smaller: `separation()` first defined `interleaved` as "the nearest non-move is below the
*furthest* move", which is true for almost any population and would have claimed non-separability
everywhere. The correct predicate is on the **largest** non-move against the **nearest** move, because
a buffer is one number for the whole population. Two selftest fixtures were also miscast (both
"separated" and "interleaved" were separable); the legs caught it, which is what they are for.

## What this changes for anyone acting on the screen

Do not tune a margin. Read the row's own side, and apply the guard. If an operator still wants a
buffer on top, the data supports any b ≤ 0.0454 without losing a move -- but it loses nothing either,
and the first b that costs a move is exactly the clearance of the second-closest published move.

## Method card

`knowledge/METHODOLOGY_ASSETS.md` **E267**.