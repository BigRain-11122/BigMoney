# 相位臂：把 r1325 的 buffer REJECT 与成本档放回它们自己的尺子里重判

面：`results/etf_book_phase_atlas_arms.json`｜脚本：`scripts/etf_book_phase_atlas_arms.py`｜基线面：`results/etf_book_phase_atlas.json`（cutoff 2026-11-16）

同日基线网格：格间 spread 5.25pp，格内 band 中位 6.71pp。

**面板一致性：ONE_WORLD** — all 11 faces priced 0988c6530a481fa1

## buffer_k05 — **REJECT**

buffer k=0.05 on every cell (the r1325 arm, re-priced per phase)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.82pp | +10.67pp | +0.155pp | 5.45pp |
| 3 | 20 | +8.46pp | +8.37pp | +0.090pp | 7.04pp |
| 3 | 40 | +6.30pp | +6.62pp | -0.320pp | 12.90pp |
| 5 | 10 | +11.82pp | +11.38pp | +0.440pp | 3.24pp |
| 5 | 20 | +8.81pp | +9.03pp | -0.215pp | 6.22pp |
| 5 | 40 | +8.12pp | +8.02pp | +0.105pp | 10.30pp |
| 8 | 10 | +11.94pp | +11.87pp | +0.075pp | 3.46pp |
| 8 | 20 | +9.72pp | +10.07pp | -0.350pp | 5.92pp |
| 8 | 40 | +8.12pp | +8.19pp | -0.070pp | 8.41pp |
| 12 | 10 | +11.44pp | +11.46pp | -0.020pp | 2.29pp |
| 12 | 20 | +9.46pp | +9.47pp | -0.010pp | 7.11pp |
| 12 | 40 | +7.82pp | +7.67pp | +0.145pp | 7.05pp |

- cells 12/12 judged
- not-worse share 0.750 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.033pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## cost05 — **NOT-SEPARABLE**

5bp/side on the whole grid (half the production toll)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +12.04pp | +10.67pp | +1.375pp | 4.58pp |
| 3 | 20 | +9.11pp | +8.37pp | +0.745pp | 7.08pp |
| 3 | 40 | +7.00pp | +6.62pp | +0.385pp | 12.59pp |
| 5 | 10 | +12.65pp | +11.38pp | +1.270pp | 3.65pp |
| 5 | 20 | +9.74pp | +9.03pp | +0.720pp | 6.39pp |
| 5 | 40 | +8.38pp | +8.02pp | +0.360pp | 9.92pp |
| 8 | 10 | +13.09pp | +11.87pp | +1.220pp | 3.33pp |
| 8 | 20 | +10.77pp | +10.07pp | +0.700pp | 6.46pp |
| 8 | 40 | +8.54pp | +8.19pp | +0.355pp | 8.70pp |
| 12 | 10 | +12.60pp | +11.46pp | +1.140pp | 2.85pp |
| 12 | 20 | +10.11pp | +9.47pp | +0.630pp | 7.70pp |
| 12 | 40 | +8.01pp | +7.67pp | +0.340pp | 7.01pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.710pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## cost20 — **REJECT**

20bp/side on the whole grid (double the production toll)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +7.97pp | +10.67pp | -2.700pp | 4.26pp |
| 3 | 20 | +6.91pp | +8.37pp | -1.455pp | 6.96pp |
| 3 | 40 | +5.83pp | +6.62pp | -0.790pp | 12.61pp |
| 5 | 10 | +8.86pp | +11.38pp | -2.525pp | 3.42pp |
| 5 | 20 | +7.60pp | +9.03pp | -1.425pp | 6.34pp |
| 5 | 40 | +7.31pp | +8.02pp | -0.705pp | 9.82pp |
| 8 | 10 | +9.46pp | +11.87pp | -2.405pp | 3.17pp |
| 8 | 20 | +8.68pp | +10.07pp | -1.390pp | 6.41pp |
| 8 | 40 | +7.48pp | +8.19pp | -0.710pp | 8.59pp |
| 12 | 10 | +9.21pp | +11.46pp | -2.240pp | 2.78pp |
| 12 | 20 | +8.23pp | +9.47pp | -1.245pp | 7.59pp |
| 12 | 40 | +6.99pp | +7.67pp | -0.685pp | 6.92pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -1.407pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## cost40 — **REJECT**

40bp/side on the whole grid (4x the production toll -- does 'the cadence is quotable' have a toll ceiling, and does the ordering vanish first?)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +2.77pp | +10.67pp | -7.905pp | 3.96pp |
| 3 | 20 | +4.07pp | +8.37pp | -4.295pp | 6.90pp |
| 3 | 40 | +4.26pp | +6.62pp | -2.355pp | 12.64pp |
| 5 | 10 | +3.93pp | +11.38pp | -7.450pp | 3.14pp |
| 5 | 20 | +4.79pp | +9.03pp | -4.235pp | 6.26pp |
| 5 | 40 | +5.89pp | +8.02pp | -2.120pp | 9.70pp |
| 8 | 10 | +4.79pp | +11.87pp | -7.070pp | 2.97pp |
| 8 | 20 | +5.94pp | +10.07pp | -4.130pp | 6.32pp |
| 8 | 40 | +6.07pp | +8.19pp | -2.120pp | 8.53pp |
| 12 | 10 | +4.86pp | +11.46pp | -6.595pp | 2.69pp |
| 12 | 20 | +5.75pp | +9.47pp | -3.730pp | 7.43pp |
| 12 | 40 | +5.64pp | +7.67pp | -2.030pp | 6.83pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -4.183pp (floor -0.05pp)
- resolvable share 0.333 (|delta| > the cell's own band; floor 0.50)

## buffer_k10 — **NOT-SEPARABLE**

buffer k=0.10 on every cell (the middle of the family r1325 named as a cost knob; declared in the pool at r1351 before this face existed)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.74pp | +10.67pp | +0.075pp | 4.67pp |
| 3 | 20 | +8.56pp | +8.37pp | +0.195pp | 7.28pp |
| 3 | 40 | +6.17pp | +6.62pp | -0.455pp | 12.78pp |
| 5 | 10 | +12.29pp | +11.38pp | +0.905pp | 3.48pp |
| 5 | 20 | +9.07pp | +9.03pp | +0.050pp | 6.18pp |
| 5 | 40 | +7.75pp | +8.02pp | -0.260pp | 10.23pp |
| 8 | 10 | +12.35pp | +11.87pp | +0.480pp | 3.08pp |
| 8 | 20 | +10.10pp | +10.07pp | +0.025pp | 5.67pp |
| 8 | 40 | +8.28pp | +8.19pp | +0.090pp | 8.64pp |
| 12 | 10 | +11.47pp | +11.46pp | +0.015pp | 2.69pp |
| 12 | 20 | +9.60pp | +9.47pp | +0.120pp | 6.83pp |
| 12 | 40 | +8.02pp | +7.67pp | +0.350pp | 7.13pp |

- cells 12/12 judged
- not-worse share 0.833 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.082pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k20 — **NOT-SEPARABLE**

buffer k=0.20 on every cell (the strongest arm -- if even this stays inside every cell's band, the buffer family is unmeasurable on this design, not negative)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +12.05pp | +10.67pp | +1.380pp | 4.66pp |
| 3 | 20 | +9.39pp | +8.37pp | +1.025pp | 6.98pp |
| 3 | 40 | +6.57pp | +6.62pp | -0.055pp | 12.94pp |
| 5 | 10 | +12.01pp | +11.38pp | +0.630pp | 3.82pp |
| 5 | 20 | +9.65pp | +9.03pp | +0.630pp | 5.92pp |
| 5 | 40 | +7.84pp | +8.02pp | -0.175pp | 11.10pp |
| 8 | 10 | +11.96pp | +11.87pp | +0.090pp | 2.64pp |
| 8 | 20 | +9.97pp | +10.07pp | -0.100pp | 6.56pp |
| 8 | 40 | +8.43pp | +8.19pp | +0.235pp | 8.47pp |
| 12 | 10 | +11.31pp | +11.46pp | -0.145pp | 2.93pp |
| 12 | 20 | +9.53pp | +9.47pp | +0.050pp | 5.49pp |
| 12 | 40 | +7.89pp | +7.67pp | +0.220pp | 7.63pp |

- cells 12/12 judged
- not-worse share 0.917 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.155pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k02 — **NOT-SEPARABLE**

buffer k=0.02 on every cell (the near-zero end -- a knob that reads the same at 0.02 and at 0.20 is flat, not merely small)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.69pp | +10.67pp | +0.015pp | 4.69pp |
| 3 | 20 | +8.24pp | +8.37pp | -0.120pp | 7.09pp |
| 3 | 40 | +6.66pp | +6.62pp | +0.035pp | 12.57pp |
| 5 | 10 | +11.54pp | +11.38pp | +0.165pp | 3.50pp |
| 5 | 20 | +8.99pp | +9.03pp | -0.030pp | 6.27pp |
| 5 | 40 | +8.01pp | +8.02pp | -0.010pp | 10.08pp |
| 8 | 10 | +11.84pp | +11.87pp | -0.025pp | 3.31pp |
| 8 | 20 | +10.03pp | +10.07pp | -0.040pp | 6.08pp |
| 8 | 40 | +8.18pp | +8.19pp | -0.010pp | 8.53pp |
| 12 | 10 | +11.40pp | +11.46pp | -0.050pp | 2.33pp |
| 12 | 20 | +9.51pp | +9.47pp | +0.035pp | 7.47pp |
| 12 | 40 | +7.70pp | +7.67pp | +0.030pp | 7.30pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -0.010pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k40 — **REJECT**

buffer k=0.40 on every cell (8x the r1325 arm -- the far end, where a real buffer finally has to hurt)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +11.34pp | +10.67pp | +0.665pp | 3.81pp |
| 3 | 20 | +9.94pp | +8.37pp | +1.575pp | 6.78pp |
| 3 | 40 | +5.95pp | +6.62pp | -0.670pp | 12.88pp |
| 5 | 10 | +12.08pp | +11.38pp | +0.700pp | 3.75pp |
| 5 | 20 | +10.06pp | +9.03pp | +1.035pp | 5.81pp |
| 5 | 40 | +7.43pp | +8.02pp | -0.580pp | 11.54pp |
| 8 | 10 | +12.34pp | +11.87pp | +0.475pp | 2.96pp |
| 8 | 20 | +9.68pp | +10.07pp | -0.390pp | 6.18pp |
| 8 | 40 | +8.40pp | +8.19pp | +0.215pp | 9.05pp |
| 12 | 10 | +11.62pp | +11.46pp | +0.165pp | 2.33pp |
| 12 | 20 | +9.97pp | +9.47pp | +0.500pp | 6.01pp |
| 12 | 40 | +8.37pp | +7.67pp | +0.695pp | 8.27pp |

- cells 12/12 judged
- not-worse share 0.750 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.487pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k05_cost20 — **REJECT**

buffer k=0.05 at 20bp/side -- the interaction neither family tested: does a buffer that is harmless at 10bp recover any of the -1.41pp the 20bp toll costs?

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +12.41pp | +10.67pp | +1.740pp | 5.19pp |
| 3 | 20 | +9.70pp | +8.37pp | +1.335pp | 5.55pp |
| 3 | 40 | +6.99pp | +6.62pp | +0.370pp | 9.84pp |
| 5 | 10 | +10.11pp | +11.38pp | -1.270pp | 4.60pp |
| 5 | 20 | +8.54pp | +9.03pp | -0.490pp | 6.76pp |
| 5 | 40 | +7.33pp | +8.02pp | -0.690pp | 10.06pp |
| 8 | 10 | +8.72pp | +11.87pp | -3.140pp | 4.14pp |
| 8 | 20 | +8.11pp | +10.07pp | -1.965pp | 6.06pp |
| 8 | 40 | +6.64pp | +8.19pp | -1.550pp | 9.56pp |
| 12 | 10 | +8.86pp | +11.46pp | -2.595pp | 3.47pp |
| 12 | 20 | +8.10pp | +9.47pp | -1.375pp | 7.50pp |
| 12 | 40 | +6.84pp | +7.67pp | -0.825pp | 7.35pp |

- cells 12/12 judged
- not-worse share 0.250 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -1.047pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## cost0 — **NOT-SEPARABLE**

0bp/side on the whole grid (no toll at all) -- if the ordering only appears here, the ordering is bought with the toll and the 10bp reading stands

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +16.95pp | +10.67pp | +6.280pp | 5.11pp |
| 3 | 20 | +12.72pp | +8.37pp | +4.360pp | 5.74pp |
| 3 | 40 | +8.71pp | +6.62pp | +2.085pp | 9.03pp |
| 5 | 10 | +16.12pp | +11.38pp | +4.745pp | 5.72pp |
| 5 | 20 | +12.86pp | +9.03pp | +3.835pp | 6.61pp |
| 5 | 40 | +9.51pp | +8.02pp | +1.490pp | 8.74pp |
| 8 | 10 | +16.01pp | +11.87pp | +4.145pp | 5.48pp |
| 8 | 20 | +12.76pp | +10.07pp | +2.685pp | 6.27pp |
| 8 | 40 | +9.97pp | +8.19pp | +1.780pp | 8.69pp |
| 12 | 10 | +14.13pp | +11.46pp | +2.675pp | 3.04pp |
| 12 | 20 | +12.06pp | +9.47pp | +2.585pp | 3.99pp |
| 12 | 40 | +8.81pp | +7.67pp | +1.145pp | 7.39pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +2.680pp (floor -0.05pp)
- resolvable share 0.083 (|delta| > the cell's own band; floor 0.50)

