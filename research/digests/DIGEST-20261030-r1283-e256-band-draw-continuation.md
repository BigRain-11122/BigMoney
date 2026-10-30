# DIGEST-20261030-r1283-e256-band-draw-continuation

**Study** E256 — at which draw count does the band endpoint stop moving?
**Runner** `scripts/e256_band_draw_continuation.py` (run / selftest 21/21 / verify) · **Faces** `results/state_tilt/BANDDRAW-2026-10-29-d960.json`, `results/state_tilt/BANDDRAW-2026-10-29-d1920.json`
**Verdict** `increments_do_not_decay_with_draws` — the endpoint never settles inside the measured grid, and later doublings add no less than earlier ones

## What was asked

E255 measured the seven rungs at 60/120/240/480 draws and found the 5% quantile still rising
(+9.8% HEAD / +11.7% TAIL from 240 to 480). Its own card left the question open: at which draw count
does NO rung move more than 2%, or — if such a count is not reachable — is the increment per
doubling flat? The answer decides whether E253/E254/E255's session targets can ever be quoted as a
number.

## What was done

The same ladder is stretched to 960 and then 1920 draws, keeping E255's prefix structure: one draw
stream per seed at the top count, every smaller count read as its own PREFIX, so six columns are one
experiment read six ways. Two faces are published (`-d960`, `-d1920`) and the prefix claim is not
assumed — the smoke leg re-reads the 1920 rung table on the 960 grid and requires it to reproduce
the 960 face's verdict and per-family state.

Per family the face publishes the per-rung step table (each consecutive grid pair), `settled_at`
(the FIRST grid point after which every later step moves every rung by ≤2%), and a half-split decay
test with an explicit oscillation flag.

## What it says

- **The endpoint never settles.** Median rise per doubling, all seven rungs — HEAD 8.85 / 1.59 /
  9.83 / 5.25 / **10.27** %, TAIL 5.45 / 0.00 / 11.67 / 6.99 / **8.82** %. `settled_after_draws`
  is `null` in both families at both faces.
- **The rise is not decaying.** Second-half median over first-half: HEAD 1.88 (d1920) / 1.44 (d960),
  TAIL 3.23 / 3.42 — later doublings add as much as earlier ones or more, so there is no countable
  stopping point: buying draws buys a bounded increment every time.
- **The edge is a slow power of the draw count.** At n = 408: 0.4549 (60) → 0.6255 (480) → 0.6691
  (960) → **0.7479** (1920). From 480 to 1920 (×4) that is +19.6%, i.e. edge ∝ D^0.13.
- **So the session target is a function of the draw budget, not a number.** The same E253 inversion
  on the published `b_self` asks 516 (E253) → 1055 HEAD / 681 TAIL (480 draws) → 1250 / 735 (960) →
  **1999 / 951** (1920), against 408 sessions available. Every one of those is a floor, and the floor
  itself moves up with every doubling.
- **Straightness is not monotone in draws either.** HEAD r2 0.539 / 0.647 / 0.679 / 0.890 / 0.924 /
  **0.825**: the ladder is straighter at 960 than at 1920. A face that only quoted `draws_needed`
  (480) would have read the r2 floor as settled at 480 and missed that it moves in both directions.
- **The family split survives.** gamma HEAD 0.3481 → 0.3011, TAIL 0.6468 → 0.5651; gap 0.264 against
  a 0.10 tolerance (2.6×). E254's rule re-applied at the top draws still says
  `exponent_undetermined_inside_the_cell` — but now from the gap, not from a poor fit.
- At the largest rung the two families' edges are IDENTICAL (0.6691 at 960, 0.7479 at 1920) because
  with 408 sessions the HEAD window of 408 and the TAIL window of 408 are the same window. The gap is
  a property of the intermediate rungs, i.e. of the ladder's shape, not of two different top edges.

## Pits that cost this round

1. **One pair of steps cannot tell an oscillation from a floor.** The first cut compared the last
   doubling against the one before it and called 8.8 / 1.6 / 9.8 / 5.2 / 10.3 a plateau — the last
   step happened to exceed its predecessor. A noisy ladder oscillates; the half-split test (do later
   doublings add LESS than earlier ones) is the question that was actually being asked, and the
   oscillation is now published beside the verdict instead of smoothed away. Selftest leg 10 pins the
   old reading as a wrong answer.
2. `verify()` resolved its face path from the module's own budget constant, so a `-d960` face could
   only be checked by falling back to a differently-named file: tag-aware now, and the smoke leg
   verifies both faces.
3. `verdict_from` printed the module-level `D_BUDGET` (1920) while `run()` measured a 960 grid, so a
   960 face would have quoted a budget it never measured; parameterised on `max(grid)`.
4. `verdict_from` raised `KeyError` on any analysis dict lacking the increment block — the verdict
   function has to be total over its inputs, or a future fixture takes the face down instead of the
   fixture.

## Not done

No coefficient re-priced, no bootstrap, no bill, no adoption. Draw counts above 1920 not measured
(the budget is not extendable in-round at 3 seeds × 14 windows × 7 rungs). GPU untouched (parked
C-20261014-01); cloud untouched; no cleanup or quarantine action.