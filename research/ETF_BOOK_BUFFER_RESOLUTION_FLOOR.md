# Buffer axis resolution floor (r1354 bm-c)

Face: `results/etf_book_buffer_resolution_floor.json`; script: `scripts/etf_book_phase_atlas_arms.py --floor`; cutoff 2026-10-29.

The family retired as 'unmeasurable at every strength'. This face is the size of that sentence.

| arm | k | median delta | median band | resolvable share | label |
|---|---|---|---|---|---|
| buffer_k02 | 0.02 | -0.018pp | 7.015pp | 0.000 | NOT-SEPARABLE |
| buffer_k05 | 0.05 | -0.030pp | 6.850pp | 0.000 | REJECT |
| buffer_k10 | 0.10 | +0.072pp | 6.985pp | 0.000 | NOT-SEPARABLE |
| buffer_k20 | 0.20 | +0.138pp | 6.584pp | 0.000 | NOT-SEPARABLE |
| buffer_k40 | 0.40 | +0.318pp | 6.037pp | 0.000 | REJECT |

Fit (through the k=0 identity): **+0.862pp per unit k**, r2 0.965, 6 points. Ruler = **6.68pp**. k needed to reach the ruler = **7.792**.

Verdict: **UNREACHABLE_BY_CONSTRUCTION**

- slope +0.862pp per unit k, r2 0.965 on 5 arms + the k=0 identity
- ruler = baseline median cell band 6.68pp (a median effect that size is the floor)
- k required to reach the floor = 7.79
- the whole axis spans 0.335pp = 0.050 of the ruler (flag if >= 0.25)
- k=7.79 sits past k=1, which is 'never trade': this design cannot resolve the axis at any setting that is still a buffer
