# Buffer axis resolution floor (r1354 bm-c)

Face: `results/etf_book_buffer_resolution_floor.json`; script: `scripts/etf_book_phase_atlas_arms.py --floor`; cutoff 2026-11-20.

The family retired as 'unmeasurable at every strength'. This face is the size of that sentence.

| arm | k | median delta | median band | resolvable share | label |
|---|---|---|---|---|---|
| buffer_k02 | 0.02 | +0.013pp | 7.352pp | 0.000 | NOT-SEPARABLE |
| buffer_k05 | 0.05 | +0.022pp | 6.698pp | 0.000 | REJECT |
| buffer_k10 | 0.10 | +0.070pp | 6.621pp | 0.000 | NOT-SEPARABLE |
| buffer_k20 | 0.20 | +0.203pp | 6.481pp | 0.000 | NOT-SEPARABLE |
| buffer_k40 | 0.40 | +0.405pp | 6.411pp | 0.000 | NOT-SEPARABLE |

Fit (with the k=0 identity as one of its points): **+1.047pp per unit k**, intercept **-0.016pp** = -0.2% of the ruler (anchor band 5%), r2 0.993, 6 points. Ruler = **6.80pp**. k needed to reach the ruler = **6.509**.

The intercept is free in that fit, so here is the same slope pinned through the identity: k = **6.494**, which reads **UNREACHABLE_BY_CONSTRUCTION**. The answer does not need the line to float off the anchor.


Verdict: **UNREACHABLE_BY_CONSTRUCTION**

- slope +1.047pp per unit k, r2 0.993 on 5 arms + the k=0 identity
- ruler = baseline median cell band 6.80pp (a median effect that size is the floor)
- k required to reach the floor = 6.51
- the whole axis spans 0.393pp = 0.058 of the ruler (flag if >= 0.25)
- k=6.51 sits past k=1, which is 'never trade': this design cannot resolve the axis at any setting that is still a buffer
