# Buffer axis resolution floor (r1354 bm-c)

Face: `results/etf_book_buffer_resolution_floor.json`; script: `scripts/etf_book_phase_atlas_arms.py --floor`; cutoff 2026-11-16.

The family retired as 'unmeasurable at every strength'. This face is the size of that sentence.

| arm | k | median delta | median band | resolvable share | label |
|---|---|---|---|---|---|
| buffer_k10 | 0.10 | +0.082pp | 6.832pp | 0.000 | NOT-SEPARABLE |
| buffer_k20 | 0.20 | +0.155pp | 6.562pp | 0.000 | NOT-SEPARABLE |
| buffer_k40 | 0.40 | +0.487pp | 6.180pp | 0.000 | REJECT |

- 3 buffer arms on the axis (need >= 4, or the slope is one point)
- 2 rung(s) left out of the fit for pricing another panel: buffer_k02, buffer_k05
