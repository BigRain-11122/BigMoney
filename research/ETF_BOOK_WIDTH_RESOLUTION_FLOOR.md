# Width axis resolution floor (r1355 bm-c)

Face: `results/etf_book_width_resolution_floor.json`; script: `scripts/etf_book_phase_atlas_arms.py --width`; source face `results/etf_book_phase_atlas.json`; cutoff 2026-11-26.

r1350 could quote the cadence and not the width. This is how big a width move would have to be to be quotable.

| width | cadences | median CAGR | by cadence |
|---|---|---|---|
| 3 | 3 | +8.245pp | R10 +10.22, R20 +8.24, R40 +6.26 |
| 5 | 3 | +8.825pp | R10 +11.04, R20 +8.82, R40 +7.45 |
| 8 | 3 | +9.790pp | R10 +11.53, R20 +9.79, R40 +7.84 |
| 12 | 3 | +9.035pp | R10 +11.05, R20 +9.04, R40 +7.16 |

Fit: **+0.0942pp per name**, r2 0.334 over 4 widths. Ruler = **6.65pp**. Names of runway needed = **70.59**, i.e. width **73.59** (widest priced rung 20).

Verdict: **DIRECTION_NOT_A_SIZE**

| cadence | rung | step | up |
|---|---|---|---|
| R10 | 3 -> 5 | +0.825pp | yes |
| R10 | 5 -> 8 | +0.480pp | yes |
| R10 | 8 -> 12 | -0.470pp | no |
| R20 | 3 -> 5 | +0.580pp | yes |
| R20 | 5 -> 8 | +0.965pp | yes |
| R20 | 8 -> 12 | -0.755pp | no |
| R40 | 3 -> 5 | +1.180pp | yes |
| R40 | 5 -> 8 | +0.400pp | yes |
| R40 | 8 -> 12 | -0.685pp | no |

Cross-check on `etf_capacity_frontier.json` (its own engine, its own universe, cutoff None): sign flips between cadences = **True**.

| cadence | ladder (median CAGR %) |
|---|---|
| R10 | N5 +19.72, N8 +19.41 |
| R20 | N5 +15.56, N8 +15.00, N12 +14.03, N20 +12.64 |
| R40 | N5 +10.04, N8 +10.71, N12 +11.28, N20 +11.32 |

- 9 rungs over 4 widths (need >= 4)
- 6 of 9 rungs point up (sign agreement 0.667; floor 0.75) -- a line through a hill has a slope, so the sign test runs first
- peak width 8 with turnover inside the tested grid = True
- slope +0.0942pp per name, r2 0.334 on 4 widths
- ruler = median cell band 6.65pp; names of runway required = 70.59
- width required = 73.6 (thinnest tested 3 + runway; widest PRICED rung = 20)
- the whole ladder spans 0.790pp = 0.119 of the ruler
- the rungs disagree about the sign, so no single number of names buys the ruler: width is a trade (CAGR against capacity), not a resolution knob
- cross-check on the capacity face's own engine (7 rungs, 0.429 up): sign flips between cadences = True -- a hill that a second engine cannot reproduce is a panel artefact, not a property of width
