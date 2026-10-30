# Width axis resolution floor (r1355 bm-c)

Face: `results/etf_book_width_resolution_floor.json`; script: `scripts/etf_book_phase_atlas_arms.py --width`; source face `results/etf_book_phase_atlas.json`; cutoff 2026-10-30.

r1350 could quote the cadence and not the width. This is how big a width move would have to be to be quotable.

| width | cadences | median CAGR | by cadence |
|---|---|---|---|
| 3 | 3 | +8.580pp | R10 +10.87, R20 +8.58, R40 +6.69 |
| 5 | 3 | +9.085pp | R10 +11.51, R20 +9.09, R40 +8.22 |
| 8 | 3 | +10.115pp | R10 +11.96, R20 +10.12, R40 +8.22 |
| 12 | 3 | +9.590pp | R10 +11.61, R20 +9.59, R40 +7.55 |

Fit: **+0.1212pp per name**, r2 0.517 over 4 widths. Ruler = **6.73pp**. Names of runway needed = **55.57**, i.e. width **58.57** (widest priced rung 20).

Verdict: **DIRECTION_NOT_A_SIZE**

| cadence | rung | step | up |
|---|---|---|---|
| R10 | 3 -> 5 | +0.645pp | yes |
| R10 | 5 -> 8 | +0.450pp | yes |
| R10 | 8 -> 12 | -0.355pp | no |
| R20 | 3 -> 5 | +0.505pp | yes |
| R20 | 5 -> 8 | +1.030pp | yes |
| R20 | 8 -> 12 | -0.525pp | no |
| R40 | 3 -> 5 | +1.530pp | yes |
| R40 | 5 -> 8 | +0.000pp | no |
| R40 | 8 -> 12 | -0.670pp | no |

Cross-check on `etf_capacity_frontier.json` (its own engine, its own universe, cutoff None): sign flips between cadences = **True**.

| cadence | ladder (median CAGR %) |
|---|---|
| R10 | N5 +19.72, N8 +19.41 |
| R20 | N5 +15.56, N8 +15.00, N12 +14.03, N20 +12.64 |
| R40 | N5 +10.04, N8 +10.71, N12 +11.28, N20 +11.32 |

- 9 rungs over 4 widths (need >= 4)
- 5 of 9 rungs point up (sign agreement 0.556; floor 0.75) -- a line through a hill has a slope, so the sign test runs first
- peak width 8 with turnover inside the tested grid = True
- slope +0.1212pp per name, r2 0.517 on 4 widths
- ruler = median cell band 6.73pp; names of runway required = 55.57
- width required = 58.6 (thinnest tested 3 + runway; widest PRICED rung = 20)
- the whole ladder spans 1.010pp = 0.150 of the ruler
- the rungs disagree about the sign, so no single number of names buys the ruler: width is a trade (CAGR against capacity), not a resolution knob
- cross-check on the capacity face's own engine (7 rungs, 0.429 up): sign flips between cadences = True -- a hill that a second engine cannot reproduce is a panel artefact, not a property of width
