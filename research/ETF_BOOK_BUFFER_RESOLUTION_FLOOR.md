# Buffer axis resolution floor (r1354 bm-c)

Face: `results/etf_book_buffer_resolution_floor.json`; script: `scripts/etf_book_phase_atlas_arms.py --floor`; cutoff 2026-11-12.

The family retired as 'unmeasurable at every strength'. This face is the size of that sentence.

| arm | k | median delta | median band | resolvable share | label |
|---|---|---|---|---|---|
| buffer_k02 | 0.02 | -0.010pp | 7.016pp | 0.000 | NOT-SEPARABLE |
| buffer_k05 | 0.05 | -0.005pp | 6.846pp | 0.000 | NOT-SEPARABLE |
| buffer_k10 | 0.10 | +0.073pp | 6.986pp | 0.000 | NOT-SEPARABLE |
| buffer_k20 | 0.20 | +0.145pp | 6.633pp | 0.000 | NOT-SEPARABLE |
| buffer_k40 | 0.40 | +0.310pp | 6.081pp | 0.000 | REJECT |

Fit (through the k=0 identity): **+0.824pp per unit k**, r2 0.984, 6 points. Ruler = **6.74pp**. k needed to reach the ruler = **8.206**.

Verdict: **UNREACHABLE_BY_CONSTRUCTION**

- slope +0.824pp per unit k, r2 0.984 on 5 arms + the k=0 identity
- ruler = baseline median cell band 6.74pp (a median effect that size is the floor)
- k required to reach the floor = 8.21
- the whole axis spans 0.320pp = 0.047 of the ruler (flag if >= 0.25)
- k=8.21 sits past k=1, which is 'never trade': this design cannot resolve the axis at any setting that is still a buffer
