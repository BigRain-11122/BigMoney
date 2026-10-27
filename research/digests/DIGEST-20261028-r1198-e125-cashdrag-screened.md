# E125 the cash leg's contribution is repair-invariant and the book's level is not (r1198 bm-b)

Face: `results/e40_cashleg_drag/CASHLegSCREEN-20261027.json` (new), per-arm checkpoints
`CASHLeg-arm-raw-20261027.json` / `CASHLeg-arm-neutralise_int-20261027.json`.
Base face: E40 `run_cashdrag` (same spec at repo multipliers 0x / 1x / 3x, ladder5 vs the
all-name book), plus a new `ladder_exposure` block.
Screen arm: `panel_screen.screen_universe(mode=neutralise_int)`. Cutoff 2026-10-27.
Selftest `e39` 459 -> 476; `e97` routing re-derived: covered_twin 23 -> 24, uncovered 1 -> **0**.

## What moved

63 cells compared, **18 move, max |delta| 0.42** (percent, on a drawdown column).
Attribution complete: **18 scheme / 0 mechanism / 0 answer / 0 other**.

Every one of the 18 moved cells is in the **all-name book** (`wide_top9999`), and every one is
present in all three multiplier rows at the same delta. **Zero ladder cells move.** Zero
mechanism cells move. Zero derived answers move.

## The multiplier axis is orthogonal to the repair

| cell | raw | screened | delta |
|---|---|---|---|
| wide x0 ann_return_pct | -0.05 | +0.31 | **+0.36** |
| wide x1 ann_return_pct | 0.32 | 0.68 | **+0.36** |
| wide x3 ann_return_pct | 1.06 | 1.42 | **+0.36** |
| wide max_drawdown_pct (all three) | -36.55 | -36.13 | +0.42 |
| wide cost_per_year_bp (all three) | 7.6781 | 7.6280 | -0.050 |
| ladder cash attributable | 36.0bp | 36.0bp | **0.0** |
| wide cash attributable | 37.0bp | 37.0bp | **0.0** |
| ladder / wide x3 delta | 109 / 111 bp | 109 / 111 bp | **0.0** |

A uniform delta across all three rate points is the signature that the repair never touches the
cash accrual: it changes the invested path (the same +36bp at 0x, 1x and 3x) and leaves the
repo leg's contribution exactly where it was. If the repair had moved the rate exposure, the
three deltas would differ. So the leg's headline ("the repo leg is worth ~36-37bp/yr at the
repo rate, ~109-111bp/yr at 3x") is quotable; the levels beside it are not.

## The mechanism cells say WHEN, and they did not move

| mechanism cell | value (both arms) |
|---|---|
| first invested bar | **2021-02-01** |
| first trading rebalance index | 262 of 82 decisions |
| cash bars / share | **263 / 15.95%** |
| mean annual cash rate | 1.98% |
| panel coverage | 1650 days, 0 ffilled |

The eligibility gate that decides when the book first trades is price-driven, so this was the
column most likely to move -- and it is bit-identical. Cross-check of the arithmetic, published
rather than assumed: 1.98% rate × 15.95% of bars = **31.6bp** against the measured 36.0bp
attribution, i.e. the same order and the same sign, with the gap attributable to the accrual
being valued on the equity curve rather than summed linearly.

## The zero on the ladder is a CONTROL, not a clean bill

This is the reading the totals could not give. `ladder_exposure` (new block, published in the
face): 67 of 1317 names are neutralised, and **none of the five ladder names is among them**.
Two ladder names appear in the screen's candidate list only to be declined as gapped prints:
`sh510500` 2015-04-15 (+248.55% over a two-session gap, ratio 3.49) and `sh512100` 2022-09-05
(+176.27% over one session, ratio 2.76), both kept.

So every ladder row in this face -- and the same is true of E121 and E123 -- is a **control
arm**: it reads zero because the repair never reaches those five names, not because the repair
is harmless. The two declined candidates are named in the face because a ladder name that
starts being neutralised tomorrow would move rows that read zero today.

## Controls

- same arm vs itself: **0 of 63** cells, 0 claims.
- cutoff control (`CASHLeg-20261020` raw vs today's raw, arm held fixed): **35 of 63 cells,
  max 5** -- the refresh moves roughly twice the cells and the panel grew five sessions
  (`panel_covered_days` 1645 -> 1650). The refresh's return deltas reach 0.61pp (ladder x3
  0.31 -> -0.30), larger than the repair's 0.36. **Refresh dominates here**, the fourth
  ordering in four consecutive twins (E122 repair 3.6x, E123 same size, E124 refresh
  1.7x/2.3x, E125 refresh ~2x).

Neither number is quoted alone; both ride in the face.

## The E97 uncovered axis is now exhausted

`covered_twin 24, uncovered 0, runners 0`. Every runner the routing audit charges is now
screened by a declared twin. Further supply has to come from a different axis -- seeded this
round as E127 (the screen-reach ledger across all published twins) and E128 (per-book cash
windows), because "one more twin" no longer exists as a source.

## Method card

E164 in `knowledge/METHODOLOGY_ASSETS.md`.

## Honest

Descriptive census only: no gate, no verdict on the strategy, no prereg, no trial count, no
ledger booking. The repo leg is the un-invested weight of the same engine, not a discretionary
allocation, and a multiplier is a counterfactual rate that never existed. The screened arm
repairs prints inside the panel it is handed and does not add or remove bars, so an unchanged
`cash_bars` cell is a property of the repair, not evidence the panel is clean. The two declined
ladder candidates are disclosed here rather than treated as clean prints -- they are exactly
the kind of print this repair exists to fix, and it declines them because of the gap rule.