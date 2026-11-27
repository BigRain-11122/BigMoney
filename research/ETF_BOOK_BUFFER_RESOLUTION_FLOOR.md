# Buffer axis resolution floor (r1354 bm-c)

Face: `results/etf_book_buffer_resolution_floor.json`; script: `scripts/etf_book_phase_atlas_arms.py --floor`; cutoff 2026-11-26.

The family retired as 'unmeasurable at every strength'. This face is the size of that sentence.

| arm | k | median delta | median band | resolvable share | label |
|---|---|---|---|---|---|
| buffer_k02 | 0.02 | -0.010pp | 7.197pp | 0.000 | NOT-SEPARABLE |
| buffer_k05 | 0.05 | -0.055pp | 6.534pp | 0.000 | REJECT |
| buffer_k10 | 0.10 | +0.085pp | 6.457pp | 0.000 | NOT-SEPARABLE |
| buffer_k20 | 0.20 | +0.190pp | 6.210pp | 0.000 | NOT-SEPARABLE |
| buffer_k40 | 0.40 | +0.450pp | 6.260pp | 0.000 | NOT-SEPARABLE |

Fit (with the k=0 identity as one of its points): **+1.217pp per unit k**, intercept **-0.046pp** = -0.7% of the ruler (anchor band 5%), r2 0.958, 6 points. Ruler = **6.65pp**. k needed to reach the ruler = **5.504**.

The intercept is free in that fit, so here is the same slope pinned through the identity: k = **5.466**, which reads **UNREACHABLE_BY_CONSTRUCTION**. The answer does not need the line to float off the anchor.


Verdict: **UNREACHABLE_BY_CONSTRUCTION**

- slope +1.217pp per unit k, r2 0.958 on 5 arms + the k=0 identity
- ruler = baseline median cell band 6.65pp (a median effect that size is the floor)
- k required to reach the floor = 5.50
- the whole axis spans 0.460pp = 0.069 of the ruler (flag if >= 0.25)
- k=5.50 sits past k=1, which is 'never trade': this design cannot resolve the axis at any setting that is still a buffer
