# Buffer axis resolution floor (r1354 bm-c)

Face: `results/etf_book_buffer_resolution_floor.json`; script: `scripts/etf_book_phase_atlas_arms.py --floor`; cutoff 2026-11-19.

The family retired as 'unmeasurable at every strength'. This face is the size of that sentence.

| arm | k | median delta | median band | resolvable share | label |
|---|---|---|---|---|---|
| buffer_k02 | 0.02 | -0.007pp | 7.271pp | 0.000 | NOT-SEPARABLE |
| buffer_k05 | 0.05 | +0.438pp | 7.240pp | 0.000 | NOT-SEPARABLE |
| buffer_k10 | 0.10 | +0.048pp | 6.655pp | 0.000 | NOT-SEPARABLE |
| buffer_k20 | 0.20 | +0.155pp | 6.544pp | 0.000 | NOT-SEPARABLE |
| buffer_k40 | 0.40 | +0.448pp | 6.239pp | 0.000 | NOT-SEPARABLE |

Fit (with the k=0 identity as one of its points): **+0.858pp per unit k**, intercept **+0.070pp** = 1.0% of the ruler (anchor band 5%), r2 0.376, 6 points. Ruler = **6.75pp**. k needed to reach the ruler = **7.785**.

The intercept is free in that fit, so here is the same slope pinned through the identity: k = **7.867**, which reads **UNREACHABLE_BY_CONSTRUCTION**. The answer does not need the line to float off the anchor.


Verdict: **UNREACHABLE_BY_CONSTRUCTION**

- slope +0.858pp per unit k, r2 0.376 on 5 arms + the k=0 identity
- ruler = baseline median cell band 6.75pp (a median effect that size is the floor)
- k required to reach the floor = 7.79
- the whole axis spans 0.455pp = 0.067 of the ruler (flag if >= 0.25)
- k=7.79 sits past k=1, which is 'never trade': this design cannot resolve the axis at any setting that is still a buffer
