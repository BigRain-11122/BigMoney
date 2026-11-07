# Buffer axis resolution floor (r1354 bm-c)

Face: `results/etf_book_buffer_resolution_floor.json`; script: `scripts/etf_book_phase_atlas_arms.py --floor`; cutoff 2026-11-06.

The family retired as 'unmeasurable at every strength'. This face is the size of that sentence.

| arm | k | median delta | median band | resolvable share | label |
|---|---|---|---|---|---|
| buffer_k02 | 0.02 | +0.002pp | 6.872pp | 0.000 | NOT-SEPARABLE |
| buffer_k05 | 0.05 | +0.042pp | 6.939pp | 0.000 | NOT-SEPARABLE |
| buffer_k10 | 0.10 | +0.080pp | 6.882pp | 0.000 | NOT-SEPARABLE |
| buffer_k20 | 0.20 | +0.062pp | 6.673pp | 0.000 | NOT-SEPARABLE |
| buffer_k40 | 0.40 | +0.378pp | 6.131pp | 0.000 | REJECT |

Fit (through the k=0 identity): **+0.887pp per unit k**, r2 0.885, 6 points. Ruler = **6.74pp**. k needed to reach the ruler = **7.624**.

Verdict: **UNREACHABLE_BY_CONSTRUCTION**

- slope +0.887pp per unit k, r2 0.885 on 5 arms + the k=0 identity
- ruler = baseline median cell band 6.74pp (a median effect that size is the floor)
- k required to reach the floor = 7.62
- the whole axis spans 0.375pp = 0.056 of the ruler (flag if >= 0.25)
- k=7.62 sits past k=1, which is 'never trade': this design cannot resolve the axis at any setting that is still a buffer
