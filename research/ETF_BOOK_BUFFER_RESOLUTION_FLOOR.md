# Buffer axis resolution floor (r1354 bm-c)

Face: `results/etf_book_buffer_resolution_floor.json`; script: `scripts/etf_book_phase_atlas_arms.py --floor`; cutoff 2026-10-30.

The family retired as 'unmeasurable at every strength'. This face is the size of that sentence.

| arm | k | median delta | median band | resolvable share | label |
|---|---|---|---|---|---|
| buffer_k02 | 0.02 | -0.015pp | 7.092pp | 0.000 | NOT-SEPARABLE |
| buffer_k05 | 0.05 | -0.060pp | 6.951pp | 0.000 | REJECT |
| buffer_k10 | 0.10 | +0.062pp | 6.943pp | 0.000 | NOT-SEPARABLE |
| buffer_k20 | 0.20 | +0.568pp | 6.617pp | 0.000 | NOT-SEPARABLE |
| buffer_k40 | 0.40 | +0.365pp | 6.151pp | 0.000 | REJECT |

Fit (through the k=0 identity): **+1.266pp per unit k**, r2 0.568, 6 points. Ruler = **6.73pp**. k needed to reach the ruler = **5.328**.

Verdict: **UNREACHABLE_BY_CONSTRUCTION**

- slope +1.266pp per unit k, r2 0.568 on 5 arms + the k=0 identity
- ruler = baseline median cell band 6.73pp (a median effect that size is the floor)
- k required to reach the floor = 5.33
- the whole axis spans 0.380pp = 0.056 of the ruler (flag if >= 0.25)
- k=5.33 sits past k=1, which is 'never trade': this design cannot resolve the axis at any setting that is still a buffer
