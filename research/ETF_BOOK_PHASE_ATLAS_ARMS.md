# 相位臂：把 r1325 的 buffer REJECT 与成本档放回它们自己的尺子里重判

面：`results/etf_book_phase_atlas_arms.json`｜脚本：`scripts/etf_book_phase_atlas_arms.py`｜基线面：`results/etf_book_phase_atlas.json`（cutoff 2026-11-13）

同日基线网格：格间 spread 5.17pp，格内 band 中位 6.72pp。

**面板一致性：ONE_WORLD** — all 11 faces priced e6f9d0e81a64ec75

## buffer_k05 — **NOT-SEPARABLE**

buffer k=0.05 on every cell (the r1325 arm, re-priced per phase)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.94pp | +10.79pp | +0.155pp | 5.44pp |
| 3 | 20 | +8.51pp | +8.45pp | +0.060pp | 6.86pp |
| 3 | 40 | +6.38pp | +6.70pp | -0.310pp | 12.81pp |
| 5 | 10 | +11.83pp | +11.40pp | +0.430pp | 3.34pp |
| 5 | 20 | +8.90pp | +9.02pp | -0.115pp | 6.26pp |
| 5 | 40 | +8.16pp | +8.18pp | -0.010pp | 10.09pp |
| 8 | 10 | +11.94pp | +11.86pp | +0.075pp | 3.45pp |
| 8 | 20 | +9.72pp | +10.07pp | -0.350pp | 5.90pp |
| 8 | 40 | +8.13pp | +8.23pp | -0.100pp | 8.32pp |
| 12 | 10 | +11.46pp | +11.46pp | -0.010pp | 2.28pp |
| 12 | 20 | +9.54pp | +9.55pp | -0.005pp | 7.27pp |
| 12 | 40 | +7.85pp | +7.71pp | +0.145pp | 6.96pp |

- cells 12/12 judged
- not-worse share 0.833 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -0.007pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## cost05 — **NOT-SEPARABLE**

5bp/side on the whole grid (half the production toll)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +12.16pp | +10.79pp | +1.375pp | 4.56pp |
| 3 | 20 | +9.20pp | +8.45pp | +0.745pp | 7.01pp |
| 3 | 40 | +7.06pp | +6.70pp | +0.365pp | 12.50pp |
| 5 | 10 | +12.68pp | +11.40pp | +1.280pp | 3.76pp |
| 5 | 20 | +9.73pp | +9.02pp | +0.720pp | 6.42pp |
| 5 | 40 | +8.53pp | +8.18pp | +0.355pp | 9.68pp |
| 8 | 10 | +13.09pp | +11.86pp | +1.225pp | 3.36pp |
| 8 | 20 | +10.77pp | +10.07pp | +0.700pp | 6.59pp |
| 8 | 40 | +8.60pp | +8.23pp | +0.365pp | 8.56pp |
| 12 | 10 | +12.61pp | +11.46pp | +1.140pp | 2.85pp |
| 12 | 20 | +10.18pp | +9.55pp | +0.630pp | 7.85pp |
| 12 | 40 | +8.04pp | +7.71pp | +0.340pp | 6.89pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.710pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## cost20 — **REJECT**

20bp/side on the whole grid (double the production toll)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +8.09pp | +10.79pp | -2.700pp | 4.31pp |
| 3 | 20 | +6.97pp | +8.45pp | -1.480pp | 6.80pp |
| 3 | 40 | +5.92pp | +6.70pp | -0.780pp | 12.54pp |
| 5 | 10 | +8.86pp | +11.40pp | -2.540pp | 3.55pp |
| 5 | 20 | +7.58pp | +9.02pp | -1.435pp | 6.37pp |
| 5 | 40 | +7.46pp | +8.18pp | -0.715pp | 9.60pp |
| 8 | 10 | +9.45pp | +11.86pp | -2.410pp | 3.21pp |
| 8 | 20 | +8.68pp | +10.07pp | -1.395pp | 6.53pp |
| 8 | 40 | +7.53pp | +8.23pp | -0.710pp | 8.49pp |
| 12 | 10 | +9.22pp | +11.46pp | -2.245pp | 2.75pp |
| 12 | 20 | +8.30pp | +9.55pp | -1.250pp | 7.77pp |
| 12 | 40 | +7.02pp | +7.71pp | -0.685pp | 6.80pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -1.415pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## cost40 — **REJECT**

40bp/side on the whole grid (4x the production toll -- does 'the cadence is quotable' have a toll ceiling, and does the ordering vanish first?)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +2.87pp | +10.79pp | -7.920pp | 4.00pp |
| 3 | 20 | +4.11pp | +8.45pp | -4.340pp | 6.71pp |
| 3 | 40 | +4.35pp | +6.70pp | -2.345pp | 12.57pp |
| 5 | 10 | +3.93pp | +11.40pp | -7.470pp | 3.28pp |
| 5 | 20 | +4.77pp | +9.02pp | -4.245pp | 6.28pp |
| 5 | 40 | +6.01pp | +8.18pp | -2.165pp | 9.48pp |
| 8 | 10 | +4.79pp | +11.86pp | -7.075pp | 3.03pp |
| 8 | 20 | +5.93pp | +10.07pp | -4.140pp | 6.44pp |
| 8 | 40 | +6.12pp | +8.23pp | -2.120pp | 8.41pp |
| 12 | 10 | +4.86pp | +11.46pp | -6.605pp | 2.65pp |
| 12 | 20 | +5.83pp | +9.55pp | -3.725pp | 7.67pp |
| 12 | 40 | +5.67pp | +7.71pp | -2.035pp | 6.71pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -4.192pp (floor -0.05pp)
- resolvable share 0.333 (|delta| > the cell's own band; floor 0.50)

## buffer_k10 — **NOT-SEPARABLE**

buffer k=0.10 on every cell (the middle of the family r1325 named as a cost knob; declared in the pool at r1351 before this face existed)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.86pp | +10.79pp | +0.075pp | 4.73pp |
| 3 | 20 | +8.74pp | +8.45pp | +0.295pp | 7.21pp |
| 3 | 40 | +6.24pp | +6.70pp | -0.455pp | 12.92pp |
| 5 | 10 | +12.32pp | +11.40pp | +0.925pp | 3.52pp |
| 5 | 20 | +9.14pp | +9.02pp | +0.125pp | 6.21pp |
| 5 | 40 | +7.83pp | +8.18pp | -0.340pp | 10.06pp |
| 8 | 10 | +12.37pp | +11.86pp | +0.505pp | 3.09pp |
| 8 | 20 | +10.06pp | +10.07pp | -0.010pp | 5.71pp |
| 8 | 40 | +8.30pp | +8.23pp | +0.065pp | 8.47pp |
| 12 | 10 | +11.53pp | +11.46pp | +0.065pp | 2.65pp |
| 12 | 20 | +9.61pp | +9.55pp | +0.060pp | 6.99pp |
| 12 | 40 | +8.05pp | +7.71pp | +0.345pp | 6.96pp |

- cells 12/12 judged
- not-worse share 0.833 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.070pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k20 — **NOT-SEPARABLE**

buffer k=0.20 on every cell (the strongest arm -- if even this stays inside every cell's band, the buffer family is unmeasurable on this design, not negative)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +12.15pp | +10.79pp | +1.370pp | 4.63pp |
| 3 | 20 | +9.53pp | +8.45pp | +1.080pp | 6.96pp |
| 3 | 40 | +6.61pp | +6.70pp | -0.085pp | 13.06pp |
| 5 | 10 | +12.05pp | +11.40pp | +0.655pp | 3.88pp |
| 5 | 20 | +9.63pp | +9.02pp | +0.620pp | 5.88pp |
| 5 | 40 | +7.92pp | +8.18pp | -0.250pp | 10.95pp |
| 8 | 10 | +12.01pp | +11.86pp | +0.145pp | 2.63pp |
| 8 | 20 | +9.96pp | +10.07pp | -0.105pp | 6.60pp |
| 8 | 40 | +8.43pp | +8.23pp | +0.195pp | 8.26pp |
| 12 | 10 | +11.38pp | +11.46pp | -0.080pp | 2.91pp |
| 12 | 20 | +9.56pp | +9.55pp | +0.010pp | 5.43pp |
| 12 | 40 | +7.89pp | +7.71pp | +0.185pp | 7.61pp |

- cells 12/12 judged
- not-worse share 0.917 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.165pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k02 — **NOT-SEPARABLE**

buffer k=0.02 on every cell (the near-zero end -- a knob that reads the same at 0.02 and at 0.20 is flat, not merely small)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.80pp | +10.79pp | +0.015pp | 4.74pp |
| 3 | 20 | +8.28pp | +8.45pp | -0.170pp | 7.03pp |
| 3 | 40 | +6.64pp | +6.70pp | -0.050pp | 12.47pp |
| 5 | 10 | +11.55pp | +11.40pp | +0.155pp | 3.60pp |
| 5 | 20 | +8.98pp | +9.02pp | -0.030pp | 6.29pp |
| 5 | 40 | +8.16pp | +8.18pp | -0.010pp | 9.89pp |
| 8 | 10 | +11.83pp | +11.86pp | -0.030pp | 3.32pp |
| 8 | 20 | +10.03pp | +10.07pp | -0.040pp | 6.20pp |
| 8 | 40 | +8.22pp | +8.23pp | -0.010pp | 8.48pp |
| 12 | 10 | +11.41pp | +11.46pp | -0.055pp | 2.32pp |
| 12 | 20 | +9.60pp | +9.55pp | +0.050pp | 7.63pp |
| 12 | 40 | +7.74pp | +7.71pp | +0.030pp | 7.15pp |

- cells 12/12 judged
- not-worse share 0.917 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -0.020pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k40 — **REJECT**

buffer k=0.40 on every cell (8x the r1325 arm -- the far end, where a real buffer finally has to hurt)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +11.84pp | +10.79pp | +1.050pp | 3.71pp |
| 3 | 20 | +9.26pp | +8.45pp | +0.810pp | 6.83pp |
| 3 | 40 | +6.24pp | +6.70pp | -0.455pp | 12.72pp |
| 5 | 10 | +12.05pp | +11.40pp | +0.650pp | 4.07pp |
| 5 | 20 | +10.23pp | +9.02pp | +1.220pp | 5.67pp |
| 5 | 40 | +7.66pp | +8.18pp | -0.520pp | 11.35pp |
| 8 | 10 | +11.89pp | +11.86pp | +0.035pp | 2.83pp |
| 8 | 20 | +9.77pp | +10.07pp | -0.305pp | 6.10pp |
| 8 | 40 | +8.40pp | +8.23pp | +0.170pp | 9.38pp |
| 12 | 10 | +11.39pp | +11.46pp | -0.070pp | 2.77pp |
| 12 | 20 | +9.96pp | +9.55pp | +0.410pp | 5.45pp |
| 12 | 40 | +8.31pp | +7.71pp | +0.610pp | 8.16pp |

- cells 12/12 judged
- not-worse share 0.750 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.290pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k05_cost20 — **REJECT**

buffer k=0.05 at 20bp/side -- the interaction neither family tested: does a buffer that is harmless at 10bp recover any of the -1.41pp the 20bp toll costs?

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +8.38pp | +10.79pp | -2.405pp | 5.22pp |
| 3 | 20 | +7.13pp | +8.45pp | -1.315pp | 6.81pp |
| 3 | 40 | +5.64pp | +6.70pp | -1.055pp | 12.80pp |
| 5 | 10 | +9.36pp | +11.40pp | -2.040pp | 3.23pp |
| 5 | 20 | +7.49pp | +9.02pp | -1.525pp | 6.23pp |
| 5 | 40 | +7.45pp | +8.18pp | -0.725pp | 10.02pp |
| 8 | 10 | +9.62pp | +11.86pp | -2.240pp | 3.39pp |
| 8 | 20 | +8.37pp | +10.07pp | -1.700pp | 5.92pp |
| 8 | 40 | +7.43pp | +8.23pp | -0.805pp | 8.27pp |
| 12 | 10 | +9.28pp | +11.46pp | -2.185pp | 2.24pp |
| 12 | 20 | +8.35pp | +9.55pp | -1.205pp | 7.23pp |
| 12 | 40 | +7.18pp | +7.71pp | -0.525pp | 6.92pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -1.420pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## cost0 — **NOT-SEPARABLE**

0bp/side on the whole grid (no toll at all) -- if the ordering only appears here, the ordering is bought with the toll and the 10bp reading stands

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +13.55pp | +10.79pp | +2.770pp | 4.68pp |
| 3 | 20 | +9.95pp | +8.45pp | +1.495pp | 7.08pp |
| 3 | 40 | +7.43pp | +6.70pp | +0.740pp | 12.49pp |
| 5 | 10 | +13.97pp | +11.40pp | +2.570pp | 3.83pp |
| 5 | 20 | +10.46pp | +9.02pp | +1.445pp | 6.44pp |
| 5 | 40 | +8.89pp | +8.18pp | +0.715pp | 9.71pp |
| 8 | 10 | +14.32pp | +11.86pp | +2.460pp | 3.40pp |
| 8 | 20 | +11.48pp | +10.07pp | +1.410pp | 6.62pp |
| 8 | 40 | +8.96pp | +8.23pp | +0.720pp | 8.62pp |
| 12 | 10 | +13.76pp | +11.46pp | +2.290pp | 2.88pp |
| 12 | 20 | +10.81pp | +9.55pp | +1.260pp | 7.88pp |
| 12 | 40 | +8.38pp | +7.71pp | +0.680pp | 6.92pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +1.427pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

