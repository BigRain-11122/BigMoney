# Buffer axis resolution floor (r1354 bm-c)

Face: `results/etf_book_buffer_resolution_floor.json`; script: `scripts/etf_book_phase_atlas_arms.py --floor`; cutoff 2026-11-16.

The family retired as 'unmeasurable at every strength'. This face is the size of that sentence.

| arm | k | median delta | median band | resolvable share | label |
|---|---|---|---|---|---|
| buffer_k02 | 0.02 | -0.010pp | 7.094pp | 0.000 | NOT-SEPARABLE |
| buffer_k05 | 0.05 | +0.033pp | 7.037pp | 0.000 | REJECT |
| buffer_k10 | 0.10 | +0.082pp | 6.832pp | 0.000 | NOT-SEPARABLE |
| buffer_k20 | 0.20 | +0.155pp | 6.562pp | 0.000 | NOT-SEPARABLE |
| buffer_k40 | 0.40 | +0.487pp | 6.180pp | 0.000 | REJECT |

Fit (through the k=0 identity): **+1.225pp per unit k**, r2 0.970, 6 points. Ruler = **6.71pp**. k needed to reach the ruler = **5.507**.

Verdict: **UNREACHABLE_BY_CONSTRUCTION**

- slope +1.225pp per unit k, r2 0.970 on 5 arms + the k=0 identity
- ruler = baseline median cell band 6.71pp (a median effect that size is the floor)
- k required to reach the floor = 5.51
- the whole axis spans 0.497pp = 0.074 of the ruler (flag if >= 0.25)
- k=5.51 sits past k=1, which is 'never trade': this design cannot resolve the axis at any setting that is still a buffer
