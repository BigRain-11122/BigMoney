# Width axis resolution floor (r1355 bm-c)

Face: `results/etf_book_width_resolution_floor.json`; script: `scripts/etf_book_phase_atlas_arms.py --width`; source face `results/etf_book_phase_atlas.json`; cutoff 2026-11-16.

r1350 could quote the cadence and not the width. This is how big a width move would have to be to be quotable.

| width | cadences | median CAGR | by cadence |
|---|---|---|---|
| 3 | 3 | +8.365pp | R10 +10.67, R20 +8.37, R40 +6.62 |
| 5 | 3 | +9.025pp | R10 +11.38, R20 +9.03, R40 +8.02 |
| 8 | 3 | +10.070pp | R10 +11.87, R20 +10.07, R40 +8.19 |
| 12 | 3 | +9.475pp | R10 +11.46, R20 +9.47, R40 +7.67 |

Fit: **+0.1290pp per name**, r2 0.492 over 4 widths. Ruler = **6.71pp**. Names of runway needed = **52.03**, i.e. width **55.03** (widest priced rung 20).

Verdict: **DIRECTION_NOT_A_SIZE**

| cadence | rung | step | up |
|---|---|---|---|
| R10 | 3 -> 5 | +0.710pp | yes |
| R10 | 5 -> 8 | +0.485pp | yes |
| R10 | 8 -> 12 | -0.410pp | no |
| R20 | 3 -> 5 | +0.660pp | yes |
| R20 | 5 -> 8 | +1.045pp | yes |
| R20 | 8 -> 12 | -0.595pp | no |
| R40 | 3 -> 5 | +1.395pp | yes |
| R40 | 5 -> 8 | +0.175pp | yes |
| R40 | 8 -> 12 | -0.520pp | no |

Cross-check on `etf_capacity_frontier.json` (its own engine, its own universe, cutoff None): sign flips between cadences = **True**.

| cadence | ladder (median CAGR %) |
|---|---|
| R10 | N5 +19.72, N8 +19.41 |
| R20 | N5 +15.56, N8 +15.00, N12 +14.03, N20 +12.64 |
| R40 | N5 +10.04, N8 +10.71, N12 +11.28, N20 +11.32 |

- 9 rungs over 4 widths (need >= 4)
- 6 of 9 rungs point up (sign agreement 0.667; floor 0.75) -- a line through a hill has a slope, so the sign test runs first
- peak width 8 with turnover inside the tested grid = True
- slope +0.1290pp per name, r2 0.492 on 4 widths
- ruler = median cell band 6.71pp; names of runway required = 52.03
- width required = 55.0 (thinnest tested 3 + runway; widest PRICED rung = 20)
- the whole ladder spans 1.110pp = 0.165 of the ruler
- the rungs disagree about the sign, so no single number of names buys the ruler: width is a trade (CAGR against capacity), not a resolution knob
- cross-check on the capacity face's own engine (7 rungs, 0.429 up): sign flips between cadences = True -- a hill that a second engine cannot reproduce is a panel artefact, not a property of width
