# Buffer axis resolution floor (r1354 bm-c)

Face: `results/etf_book_buffer_resolution_floor.json`; script: `scripts/etf_book_phase_atlas_arms.py --floor`; cutoff 2026-11-17.

The family retired as 'unmeasurable at every strength'. This face is the size of that sentence.

| arm | k | median delta | median band | resolvable share | label |
|---|---|---|---|---|---|
| buffer_k02 | 0.02 | +0.090pp | 7.157pp | 0.000 | NOT-SEPARABLE |
| buffer_k05 | 0.05 | +0.065pp | 6.877pp | 0.000 | NOT-SEPARABLE |
| buffer_k10 | 0.10 | +1.208pp | 6.305pp | 0.000 | NOT-SEPARABLE |
| buffer_k20 | 0.20 | +0.315pp | 6.530pp | 0.000 | NOT-SEPARABLE |
| buffer_k40 | 0.40 | +0.617pp | 6.045pp | 0.000 | NOT-SEPARABLE |

Fit (with the k=0 identity as one of its points): **+1.238pp per unit k**, intercept **+0.224pp** = 3.1% of the ruler (anchor band 5%), r2 0.163, 6 points. Ruler = **7.12pp**. k needed to reach the ruler = **5.571**.

The intercept is free in that fit, so here is the same slope pinned through the identity: k = **5.751**, which reads **UNREACHABLE_BY_CONSTRUCTION**. The answer does not need the line to float off the anchor.


Verdict: **UNREACHABLE_BY_CONSTRUCTION**

- slope +1.238pp per unit k, r2 0.163 on 5 arms + the k=0 identity
- ruler = baseline median cell band 7.12pp (a median effect that size is the floor)
- k required to reach the floor = 5.57
- the whole axis spans 0.527pp = 0.074 of the ruler (flag if >= 0.25)
- k=5.57 sits past k=1, which is 'never trade': this design cannot resolve the axis at any setting that is still a buffer
