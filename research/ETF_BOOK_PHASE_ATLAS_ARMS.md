# 相位臂：把 r1325 的 buffer REJECT 与成本档放回它们自己的尺子里重判

面：`results/etf_book_phase_atlas_arms.json`｜脚本：`scripts/etf_book_phase_atlas_arms.py`｜基线面：`results/etf_book_phase_atlas.json`（cutoff 2026-11-17）

同日基线网格：格间 spread 5.29pp，格内 band 中位 6.74pp。

**面板一致性：ONE_WORLD** — all 11 faces priced 0d5a9cdcf2beffd5

## buffer_k05 — **REJECT**

buffer k=0.05 on every cell (the r1325 arm, re-priced per phase)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.77pp | +10.62pp | +0.150pp | 5.44pp |
| 3 | 20 | +8.47pp | +8.49pp | -0.015pp | 7.23pp |
| 3 | 40 | +6.40pp | +6.70pp | -0.295pp | 12.80pp |
| 5 | 10 | +11.92pp | +11.43pp | +0.495pp | 3.06pp |
| 5 | 20 | +8.90pp | +9.15pp | -0.250pp | 6.20pp |
| 5 | 40 | +8.15pp | +7.95pp | +0.200pp | 10.46pp |
| 8 | 10 | +12.05pp | +11.98pp | +0.070pp | 3.49pp |
| 8 | 20 | +9.80pp | +10.15pp | -0.355pp | 5.95pp |
| 8 | 40 | +8.15pp | +8.13pp | +0.020pp | 8.49pp |
| 12 | 10 | +11.43pp | +11.47pp | -0.040pp | 2.26pp |
| 12 | 20 | +9.39pp | +9.43pp | -0.035pp | 6.88pp |
| 12 | 40 | +7.86pp | +7.68pp | +0.175pp | 7.13pp |

- cells 12/12 judged
- not-worse share 0.750 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.003pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## cost05 — **NOT-SEPARABLE**

5bp/side on the whole grid (half the production toll)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +11.99pp | +10.62pp | +1.375pp | 4.57pp |
| 3 | 20 | +9.23pp | +8.49pp | +0.740pp | 7.16pp |
| 3 | 40 | +7.09pp | +6.70pp | +0.400pp | 12.40pp |
| 5 | 10 | +12.69pp | +11.43pp | +1.265pp | 3.47pp |
| 5 | 20 | +9.87pp | +9.15pp | +0.720pp | 6.46pp |
| 5 | 40 | +8.30pp | +7.95pp | +0.355pp | 10.09pp |
| 8 | 10 | +13.20pp | +11.98pp | +1.220pp | 3.27pp |
| 8 | 20 | +10.86pp | +10.15pp | +0.700pp | 6.40pp |
| 8 | 40 | +8.48pp | +8.13pp | +0.355pp | 8.80pp |
| 12 | 10 | +12.61pp | +11.47pp | +1.140pp | 2.84pp |
| 12 | 20 | +10.06pp | +9.43pp | +0.635pp | 7.46pp |
| 12 | 40 | +8.03pp | +7.68pp | +0.345pp | 7.09pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.710pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## cost20 — **REJECT**

20bp/side on the whole grid (double the production toll)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +7.92pp | +10.62pp | -2.695pp | 4.31pp |
| 3 | 20 | +7.02pp | +8.49pp | -1.470pp | 7.12pp |
| 3 | 40 | +5.88pp | +6.70pp | -0.815pp | 12.42pp |
| 5 | 10 | +8.93pp | +11.43pp | -2.500pp | 3.24pp |
| 5 | 20 | +7.71pp | +9.15pp | -1.435pp | 6.31pp |
| 5 | 40 | +7.24pp | +7.95pp | -0.715pp | 9.99pp |
| 8 | 10 | +9.57pp | +11.98pp | -2.405pp | 3.10pp |
| 8 | 20 | +8.76pp | +10.15pp | -1.400pp | 6.34pp |
| 8 | 40 | +7.42pp | +8.13pp | -0.710pp | 8.70pp |
| 12 | 10 | +9.23pp | +11.47pp | -2.240pp | 2.76pp |
| 12 | 20 | +8.19pp | +9.43pp | -1.245pp | 7.36pp |
| 12 | 40 | +7.00pp | +7.68pp | -0.680pp | 7.02pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -1.417pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## cost40 — **REJECT**

40bp/side on the whole grid (4x the production toll -- does 'the cadence is quotable' have a toll ceiling, and does the ordering vanish first?)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +2.71pp | +10.62pp | -7.900pp | 4.03pp |
| 3 | 20 | +4.14pp | +8.49pp | -4.345pp | 7.07pp |
| 3 | 40 | +4.26pp | +6.70pp | -2.430pp | 12.36pp |
| 5 | 10 | +4.03pp | +11.43pp | -7.400pp | 2.97pp |
| 5 | 20 | +4.91pp | +9.15pp | -4.240pp | 6.24pp |
| 5 | 40 | +5.83pp | +7.95pp | -2.120pp | 9.87pp |
| 8 | 10 | +4.91pp | +11.98pp | -7.075pp | 2.88pp |
| 8 | 20 | +6.01pp | +10.15pp | -4.140pp | 6.25pp |
| 8 | 40 | +6.00pp | +8.13pp | -2.125pp | 8.60pp |
| 12 | 10 | +4.88pp | +11.47pp | -6.590pp | 2.65pp |
| 12 | 20 | +5.73pp | +9.43pp | -3.700pp | 7.20pp |
| 12 | 40 | +5.66pp | +7.68pp | -2.030pp | 6.91pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -4.190pp (floor -0.05pp)
- resolvable share 0.333 (|delta| > the cell's own band; floor 0.50)

## buffer_k10 — **NOT-SEPARABLE**

buffer k=0.10 on every cell (the middle of the family r1325 named as a cost knob; declared in the pool at r1351 before this face existed)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.75pp | +10.62pp | +0.135pp | 4.63pp |
| 3 | 20 | +8.44pp | +8.49pp | -0.050pp | 7.28pp |
| 3 | 40 | +6.19pp | +6.70pp | -0.505pp | 12.66pp |
| 5 | 10 | +12.30pp | +11.43pp | +0.875pp | 3.48pp |
| 5 | 20 | +9.17pp | +9.15pp | +0.020pp | 6.16pp |
| 5 | 40 | +7.71pp | +7.95pp | -0.240pp | 10.37pp |
| 8 | 10 | +12.40pp | +11.98pp | +0.425pp | 3.05pp |
| 8 | 20 | +10.16pp | +10.15pp | +0.010pp | 5.68pp |
| 8 | 40 | +8.22pp | +8.13pp | +0.090pp | 8.62pp |
| 12 | 10 | +11.41pp | +11.47pp | -0.060pp | 2.71pp |
| 12 | 20 | +9.59pp | +9.43pp | +0.160pp | 6.66pp |
| 12 | 40 | +8.05pp | +7.68pp | +0.365pp | 7.31pp |

- cells 12/12 judged
- not-worse share 0.833 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.055pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k20 — **NOT-SEPARABLE**

buffer k=0.20 on every cell (the strongest arm -- if even this stays inside every cell's band, the buffer family is unmeasurable on this design, not negative)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +12.00pp | +10.62pp | +1.385pp | 4.69pp |
| 3 | 20 | +9.32pp | +8.49pp | +0.835pp | 7.03pp |
| 3 | 40 | +6.62pp | +6.70pp | -0.080pp | 12.80pp |
| 5 | 10 | +11.99pp | +11.43pp | +0.570pp | 3.87pp |
| 5 | 20 | +9.70pp | +9.15pp | +0.550pp | 5.97pp |
| 5 | 40 | +7.83pp | +7.95pp | -0.115pp | 11.13pp |
| 8 | 10 | +11.88pp | +11.98pp | -0.105pp | 2.62pp |
| 8 | 20 | +10.07pp | +10.15pp | -0.085pp | 6.53pp |
| 8 | 40 | +8.46pp | +8.13pp | +0.330pp | 8.50pp |
| 12 | 10 | +11.31pp | +11.47pp | -0.155pp | 2.92pp |
| 12 | 20 | +9.51pp | +9.43pp | +0.080pp | 5.53pp |
| 12 | 40 | +7.91pp | +7.68pp | +0.220pp | 7.62pp |

- cells 12/12 judged
- not-worse share 0.917 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.150pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k02 — **NOT-SEPARABLE**

buffer k=0.02 on every cell (the near-zero end -- a knob that reads the same at 0.02 and at 0.20 is flat, not merely small)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.63pp | +10.62pp | +0.015pp | 4.72pp |
| 3 | 20 | +8.35pp | +8.49pp | -0.140pp | 7.16pp |
| 3 | 40 | +6.76pp | +6.70pp | +0.070pp | 12.38pp |
| 5 | 10 | +11.59pp | +11.43pp | +0.165pp | 3.31pp |
| 5 | 20 | +9.12pp | +9.15pp | -0.030pp | 6.29pp |
| 5 | 40 | +7.95pp | +7.95pp | +0.000pp | 10.11pp |
| 8 | 10 | +11.96pp | +11.98pp | -0.025pp | 3.32pp |
| 8 | 20 | +10.12pp | +10.15pp | -0.040pp | 6.01pp |
| 8 | 40 | +8.12pp | +8.13pp | -0.015pp | 8.59pp |
| 12 | 10 | +11.44pp | +11.47pp | -0.030pp | 2.30pp |
| 12 | 20 | +9.45pp | +9.43pp | +0.015pp | 7.41pp |
| 12 | 40 | +7.71pp | +7.68pp | +0.030pp | 7.32pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -0.007pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k40 — **NOT-SEPARABLE**

buffer k=0.40 on every cell (8x the r1325 arm -- the far end, where a real buffer finally has to hurt)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +12.05pp | +10.62pp | +1.435pp | 3.85pp |
| 3 | 20 | +9.28pp | +8.49pp | +0.785pp | 6.73pp |
| 3 | 40 | +6.18pp | +6.70pp | -0.515pp | 13.00pp |
| 5 | 10 | +12.13pp | +11.43pp | +0.705pp | 4.35pp |
| 5 | 20 | +9.91pp | +9.15pp | +0.760pp | 6.04pp |
| 5 | 40 | +7.88pp | +7.95pp | -0.075pp | 11.64pp |
| 8 | 10 | +11.96pp | +11.98pp | -0.025pp | 2.92pp |
| 8 | 20 | +9.77pp | +10.15pp | -0.390pp | 6.25pp |
| 8 | 40 | +8.47pp | +8.13pp | +0.340pp | 9.65pp |
| 12 | 10 | +11.43pp | +11.47pp | -0.040pp | 2.76pp |
| 12 | 20 | +10.02pp | +9.43pp | +0.590pp | 5.53pp |
| 12 | 40 | +8.45pp | +7.68pp | +0.760pp | 8.34pp |

- cells 12/12 judged
- not-worse share 0.833 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.465pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k05_cost20 — **REJECT**

buffer k=0.05 at 20bp/side -- the interaction neither family tested: does a buffer that is harmless at 10bp recover any of the -1.41pp the 20bp toll costs?

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +8.21pp | +10.62pp | -2.400pp | 5.23pp |
| 3 | 20 | +7.10pp | +8.49pp | -1.390pp | 7.17pp |
| 3 | 40 | +5.66pp | +6.70pp | -1.040pp | 12.75pp |
| 5 | 10 | +9.46pp | +11.43pp | -1.970pp | 2.95pp |
| 5 | 20 | +7.51pp | +9.15pp | -1.635pp | 6.18pp |
| 5 | 40 | +7.39pp | +7.95pp | -0.555pp | 10.39pp |
| 8 | 10 | +9.74pp | +11.98pp | -2.235pp | 3.41pp |
| 8 | 20 | +8.45pp | +10.15pp | -1.705pp | 5.93pp |
| 8 | 40 | +7.45pp | +8.13pp | -0.680pp | 8.42pp |
| 12 | 10 | +9.26pp | +11.47pp | -2.210pp | 2.20pp |
| 12 | 20 | +8.19pp | +9.43pp | -1.240pp | 6.81pp |
| 12 | 40 | +7.20pp | +7.68pp | -0.485pp | 7.08pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -1.512pp (floor -0.05pp)
- resolvable share 0.083 (|delta| > the cell's own band; floor 0.50)

## cost0 — **NOT-SEPARABLE**

0bp/side on the whole grid (no toll at all) -- if the ordering only appears here, the ordering is bought with the toll and the 10bp reading stands

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +13.37pp | +10.62pp | +2.755pp | 4.68pp |
| 3 | 20 | +9.97pp | +8.49pp | +1.485pp | 7.18pp |
| 3 | 40 | +7.48pp | +6.70pp | +0.785pp | 12.38pp |
| 5 | 10 | +13.97pp | +11.43pp | +2.545pp | 3.55pp |
| 5 | 20 | +10.60pp | +9.15pp | +1.445pp | 6.52pp |
| 5 | 40 | +8.66pp | +7.95pp | +0.715pp | 10.11pp |
| 8 | 10 | +14.44pp | +11.98pp | +2.460pp | 3.33pp |
| 8 | 20 | +11.56pp | +10.15pp | +1.405pp | 6.42pp |
| 8 | 40 | +8.85pp | +8.13pp | +0.715pp | 8.84pp |
| 12 | 10 | +13.74pp | +11.47pp | +2.275pp | 2.87pp |
| 12 | 20 | +10.69pp | +9.43pp | +1.260pp | 7.50pp |
| 12 | 40 | +8.37pp | +7.68pp | +0.685pp | 7.12pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +1.425pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

