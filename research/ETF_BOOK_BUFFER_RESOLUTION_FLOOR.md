# Buffer axis resolution floor (r1354 bm-c)

Face: `results/etf_book_buffer_resolution_floor.json`; script: `scripts/etf_book_phase_atlas_arms.py --floor`; cutoff 2026-11-13.

The family retired as 'unmeasurable at every strength'. This face is the size of that sentence.

| arm | k | median delta | median band | resolvable share | label |
|---|---|---|---|---|---|
| buffer_k02 | 0.02 | -0.020pp | 7.034pp | 0.000 | NOT-SEPARABLE |
| buffer_k05 | 0.05 | -0.007pp | 6.862pp | 0.000 | NOT-SEPARABLE |
| buffer_k10 | 0.10 | +0.070pp | 6.959pp | 0.000 | NOT-SEPARABLE |
| buffer_k20 | 0.20 | +0.165pp | 6.604pp | 0.000 | NOT-SEPARABLE |
| buffer_k40 | 0.40 | +0.290pp | 6.099pp | 0.000 | REJECT |

Fit (through the k=0 identity): **+0.801pp per unit k**, r2 0.970, 6 points. Ruler = **6.72pp**. k needed to reach the ruler = **8.415**.

Verdict: **UNREACHABLE_BY_CONSTRUCTION**

- slope +0.801pp per unit k, r2 0.970 on 5 arms + the k=0 identity
- ruler = baseline median cell band 6.72pp (a median effect that size is the floor)
- k required to reach the floor = 8.41
- the whole axis spans 0.310pp = 0.046 of the ruler (flag if >= 0.25)
- k=8.41 sits past k=1, which is 'never trade': this design cannot resolve the axis at any setting that is still a buffer
