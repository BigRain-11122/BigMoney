# Buffer axis resolution floor (r1354 bm-c)

Face: `results/etf_book_buffer_resolution_floor.json`; script: `scripts/etf_book_phase_atlas_arms.py --floor`; cutoff 2026-11-17.

The family retired as 'unmeasurable at every strength'. This face is the size of that sentence.

| arm | k | median delta | median band | resolvable share | label |
|---|---|---|---|---|---|
| buffer_k02 | 0.02 | -0.007pp | 7.157pp | 0.000 | NOT-SEPARABLE |
| buffer_k05 | 0.05 | +0.003pp | 6.877pp | 0.000 | REJECT |
| buffer_k10 | 0.10 | +0.055pp | 6.658pp | 0.000 | NOT-SEPARABLE |
| buffer_k20 | 0.20 | +0.150pp | 6.530pp | 0.000 | NOT-SEPARABLE |
| buffer_k40 | 0.40 | +0.465pp | 6.251pp | 0.000 | NOT-SEPARABLE |

Fit (through the k=0 identity): **+1.193pp per unit k**, r2 0.966, 6 points. Ruler = **6.74pp**. k needed to reach the ruler = **5.681**.

Verdict: **UNREACHABLE_BY_CONSTRUCTION**

- slope +1.193pp per unit k, r2 0.966 on 5 arms + the k=0 identity
- ruler = baseline median cell band 6.74pp (a median effect that size is the floor)
- k required to reach the floor = 5.68
- the whole axis spans 0.472pp = 0.070 of the ruler (flag if >= 0.25)
- k=5.68 sits past k=1, which is 'never trade': this design cannot resolve the axis at any setting that is still a buffer
