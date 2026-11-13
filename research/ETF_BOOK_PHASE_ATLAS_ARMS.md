# 相位臂：把 r1325 的 buffer REJECT 与成本档放回它们自己的尺子里重判

面：`results/etf_book_phase_atlas_arms.json`｜脚本：`scripts/etf_book_phase_atlas_arms.py`｜基线面：`results/etf_book_phase_atlas.json`（cutoff 2026-11-12）

同日基线网格：格间 spread 5.18pp，格内 band 中位 6.74pp。

**面板一致性：ONE_WORLD** — all 11 faces priced e383c3a68f5f98af

## buffer_k05 — **NOT-SEPARABLE**

buffer k=0.05 on every cell (the r1325 arm, re-priced per phase)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.98pp | +10.82pp | +0.155pp | 5.36pp |
| 3 | 20 | +8.57pp | +8.48pp | +0.095pp | 6.85pp |
| 3 | 40 | +6.46pp | +6.74pp | -0.280pp | 12.82pp |
| 5 | 10 | +11.91pp | +11.45pp | +0.465pp | 3.25pp |
| 5 | 20 | +8.96pp | +9.06pp | -0.105pp | 6.27pp |
| 5 | 40 | +8.23pp | +8.24pp | -0.010pp | 10.06pp |
| 8 | 10 | +11.99pp | +11.92pp | +0.070pp | 3.40pp |
| 8 | 20 | +9.76pp | +10.12pp | -0.355pp | 5.92pp |
| 8 | 40 | +8.20pp | +8.27pp | -0.070pp | 8.36pp |
| 12 | 10 | +11.51pp | +11.54pp | -0.030pp | 2.25pp |
| 12 | 20 | +9.61pp | +9.61pp | +0.000pp | 7.33pp |
| 12 | 40 | +7.93pp | +7.78pp | +0.150pp | 6.97pp |

- cells 12/12 judged
- not-worse share 0.833 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -0.005pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## cost05 — **NOT-SEPARABLE**

5bp/side on the whole grid (half the production toll)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +12.20pp | +10.82pp | +1.375pp | 4.52pp |
| 3 | 20 | +9.22pp | +8.48pp | +0.745pp | 7.00pp |
| 3 | 40 | +7.11pp | +6.74pp | +0.375pp | 12.52pp |
| 5 | 10 | +12.72pp | +11.45pp | +1.275pp | 3.66pp |
| 5 | 20 | +9.79pp | +9.06pp | +0.720pp | 6.43pp |
| 5 | 40 | +8.60pp | +8.24pp | +0.360pp | 9.68pp |
| 8 | 10 | +13.14pp | +11.92pp | +1.220pp | 3.27pp |
| 8 | 20 | +10.82pp | +10.12pp | +0.705pp | 6.65pp |
| 8 | 40 | +8.62pp | +8.27pp | +0.355pp | 8.56pp |
| 12 | 10 | +12.68pp | +11.54pp | +1.135pp | 2.81pp |
| 12 | 20 | +10.23pp | +9.61pp | +0.630pp | 7.90pp |
| 12 | 40 | +8.12pp | +7.78pp | +0.340pp | 6.90pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.712pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## cost20 — **REJECT**

20bp/side on the whole grid (double the production toll)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +8.12pp | +10.82pp | -2.700pp | 4.27pp |
| 3 | 20 | +7.00pp | +8.48pp | -1.485pp | 6.79pp |
| 3 | 40 | +5.99pp | +6.74pp | -0.745pp | 12.55pp |
| 5 | 10 | +8.93pp | +11.45pp | -2.515pp | 3.46pp |
| 5 | 20 | +7.63pp | +9.06pp | -1.430pp | 6.38pp |
| 5 | 40 | +7.53pp | +8.24pp | -0.715pp | 9.58pp |
| 8 | 10 | +9.51pp | +11.92pp | -2.415pp | 3.14pp |
| 8 | 20 | +8.72pp | +10.12pp | -1.395pp | 6.59pp |
| 8 | 40 | +7.55pp | +8.27pp | -0.715pp | 8.49pp |
| 12 | 10 | +9.30pp | +11.54pp | -2.235pp | 2.70pp |
| 12 | 20 | +8.36pp | +9.61pp | -1.250pp | 7.82pp |
| 12 | 40 | +7.10pp | +7.78pp | -0.680pp | 6.81pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -1.413pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## cost40 — **REJECT**

40bp/side on the whole grid (4x the production toll -- does 'the cadence is quotable' have a toll ceiling, and does the ordering vanish first?)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +2.92pp | +10.82pp | -7.900pp | 3.98pp |
| 3 | 20 | +4.13pp | +8.48pp | -4.345pp | 6.71pp |
| 3 | 40 | +4.42pp | +6.74pp | -2.315pp | 12.59pp |
| 5 | 10 | +4.00pp | +11.45pp | -7.445pp | 3.19pp |
| 5 | 20 | +4.82pp | +9.06pp | -4.245pp | 6.30pp |
| 5 | 40 | +6.07pp | +8.24pp | -2.170pp | 9.48pp |
| 8 | 10 | +4.83pp | +11.92pp | -7.090pp | 2.96pp |
| 8 | 20 | +5.97pp | +10.12pp | -4.140pp | 6.49pp |
| 8 | 40 | +6.14pp | +8.27pp | -2.130pp | 8.41pp |
| 12 | 10 | +4.96pp | +11.54pp | -6.585pp | 2.60pp |
| 12 | 20 | +5.88pp | +9.61pp | -3.730pp | 7.71pp |
| 12 | 40 | +5.75pp | +7.78pp | -2.035pp | 6.74pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -4.192pp (floor -0.05pp)
- resolvable share 0.333 (|delta| > the cell's own band; floor 0.50)

## buffer_k10 — **NOT-SEPARABLE**

buffer k=0.10 on every cell (the middle of the family r1325 named as a cost knob; declared in the pool at r1351 before this face existed)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.90pp | +10.82pp | +0.075pp | 4.63pp |
| 3 | 20 | +8.80pp | +8.48pp | +0.320pp | 7.21pp |
| 3 | 40 | +6.33pp | +6.74pp | -0.410pp | 12.96pp |
| 5 | 10 | +12.39pp | +11.45pp | +0.945pp | 3.44pp |
| 5 | 20 | +9.21pp | +9.06pp | +0.150pp | 6.22pp |
| 5 | 40 | +7.87pp | +8.24pp | -0.370pp | 10.04pp |
| 8 | 10 | +12.44pp | +11.92pp | +0.515pp | 3.00pp |
| 8 | 20 | +10.11pp | +10.12pp | -0.005pp | 5.75pp |
| 8 | 40 | +8.34pp | +8.27pp | +0.070pp | 8.43pp |
| 12 | 10 | +11.55pp | +11.54pp | +0.010pp | 2.60pp |
| 12 | 20 | +9.66pp | +9.61pp | +0.055pp | 7.03pp |
| 12 | 40 | +8.12pp | +7.78pp | +0.340pp | 6.99pp |

- cells 12/12 judged
- not-worse share 0.833 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.073pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k20 — **NOT-SEPARABLE**

buffer k=0.20 on every cell (the strongest arm -- if even this stays inside every cell's band, the buffer family is unmeasurable on this design, not negative)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +12.18pp | +10.82pp | +1.355pp | 4.55pp |
| 3 | 20 | +9.55pp | +8.48pp | +1.075pp | 6.87pp |
| 3 | 40 | +6.71pp | +6.74pp | -0.030pp | 13.05pp |
| 5 | 10 | +12.11pp | +11.45pp | +0.660pp | 3.82pp |
| 5 | 20 | +9.73pp | +9.06pp | +0.665pp | 5.95pp |
| 5 | 40 | +7.96pp | +8.24pp | -0.285pp | 10.93pp |
| 8 | 10 | +12.06pp | +11.92pp | +0.140pp | 2.56pp |
| 8 | 20 | +10.03pp | +10.12pp | -0.090pp | 6.63pp |
| 8 | 40 | +8.49pp | +8.27pp | +0.220pp | 8.22pp |
| 12 | 10 | +11.40pp | +11.54pp | -0.135pp | 2.90pp |
| 12 | 20 | +9.61pp | +9.61pp | +0.005pp | 5.39pp |
| 12 | 40 | +7.93pp | +7.78pp | +0.150pp | 7.62pp |

- cells 12/12 judged
- not-worse share 0.917 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.145pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k02 — **NOT-SEPARABLE**

buffer k=0.02 on every cell (the near-zero end -- a knob that reads the same at 0.02 and at 0.20 is flat, not merely small)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.84pp | +10.82pp | +0.015pp | 4.70pp |
| 3 | 20 | +8.31pp | +8.48pp | -0.165pp | 7.02pp |
| 3 | 40 | +6.74pp | +6.74pp | +0.005pp | 12.49pp |
| 5 | 10 | +11.60pp | +11.45pp | +0.155pp | 3.52pp |
| 5 | 20 | +9.04pp | +9.06pp | -0.025pp | 6.31pp |
| 5 | 40 | +8.23pp | +8.24pp | -0.010pp | 9.90pp |
| 8 | 10 | +11.88pp | +11.92pp | -0.035pp | 3.26pp |
| 8 | 20 | +10.08pp | +10.12pp | -0.035pp | 6.26pp |
| 8 | 40 | +8.26pp | +8.27pp | -0.010pp | 8.51pp |
| 12 | 10 | +11.48pp | +11.54pp | -0.055pp | 2.28pp |
| 12 | 20 | +9.65pp | +9.61pp | +0.050pp | 7.69pp |
| 12 | 40 | +7.82pp | +7.78pp | +0.035pp | 7.14pp |

- cells 12/12 judged
- not-worse share 0.917 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -0.010pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k40 — **REJECT**

buffer k=0.40 on every cell (8x the r1325 arm -- the far end, where a real buffer finally has to hurt)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +11.86pp | +10.82pp | +1.030pp | 3.69pp |
| 3 | 20 | +9.29pp | +8.48pp | +0.805pp | 6.77pp |
| 3 | 40 | +6.32pp | +6.74pp | -0.420pp | 12.72pp |
| 5 | 10 | +12.11pp | +11.45pp | +0.665pp | 4.05pp |
| 5 | 20 | +10.29pp | +9.06pp | +1.220pp | 5.74pp |
| 5 | 40 | +7.74pp | +8.24pp | -0.500pp | 11.33pp |
| 8 | 10 | +11.91pp | +11.92pp | -0.005pp | 2.80pp |
| 8 | 20 | +9.79pp | +10.12pp | -0.325pp | 6.08pp |
| 8 | 40 | +8.48pp | +8.27pp | +0.210pp | 9.37pp |
| 12 | 10 | +11.45pp | +11.54pp | -0.095pp | 2.77pp |
| 12 | 20 | +10.02pp | +9.61pp | +0.410pp | 5.43pp |
| 12 | 40 | +8.36pp | +7.78pp | +0.575pp | 8.20pp |

- cells 12/12 judged
- not-worse share 0.750 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.310pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k05_cost20 — **REJECT**

buffer k=0.05 at 20bp/side -- the interaction neither family tested: does a buffer that is harmless at 10bp recover any of the -1.41pp the 20bp toll costs?

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +8.43pp | +10.82pp | -2.400pp | 5.14pp |
| 3 | 20 | +7.19pp | +8.48pp | -1.290pp | 6.78pp |
| 3 | 40 | +5.71pp | +6.74pp | -1.020pp | 12.80pp |
| 5 | 10 | +9.44pp | +11.45pp | -2.010pp | 3.14pp |
| 5 | 20 | +7.55pp | +9.06pp | -1.510pp | 6.25pp |
| 5 | 40 | +7.51pp | +8.24pp | -0.730pp | 10.00pp |
| 8 | 10 | +9.68pp | +11.92pp | -2.245pp | 3.33pp |
| 8 | 20 | +8.41pp | +10.12pp | -1.705pp | 5.94pp |
| 8 | 40 | +7.50pp | +8.27pp | -0.770pp | 8.31pp |
| 12 | 10 | +9.34pp | +11.54pp | -2.200pp | 2.19pp |
| 12 | 20 | +8.40pp | +9.61pp | -1.205pp | 7.28pp |
| 12 | 40 | +7.26pp | +7.78pp | -0.520pp | 6.93pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -1.400pp (floor -0.05pp)
- resolvable share 0.083 (|delta| > the cell's own band; floor 0.50)

## cost0 — **NOT-SEPARABLE**

0bp/side on the whole grid (no toll at all) -- if the ordering only appears here, the ordering is bought with the toll and the 10bp reading stands

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +13.59pp | +10.82pp | +2.765pp | 4.59pp |
| 3 | 20 | +9.97pp | +8.48pp | +1.495pp | 7.08pp |
| 3 | 40 | +7.48pp | +6.74pp | +0.745pp | 12.51pp |
| 5 | 10 | +14.01pp | +11.45pp | +2.565pp | 3.73pp |
| 5 | 20 | +10.52pp | +9.06pp | +1.450pp | 6.46pp |
| 5 | 40 | +8.96pp | +8.24pp | +0.720pp | 9.70pp |
| 8 | 10 | +14.38pp | +11.92pp | +2.460pp | 3.33pp |
| 8 | 20 | +11.53pp | +10.12pp | +1.415pp | 6.66pp |
| 8 | 40 | +8.99pp | +8.27pp | +0.720pp | 8.60pp |
| 12 | 10 | +13.82pp | +11.54pp | +2.280pp | 2.85pp |
| 12 | 20 | +10.87pp | +9.61pp | +1.265pp | 7.92pp |
| 12 | 40 | +8.46pp | +7.78pp | +0.685pp | 6.93pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +1.433pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

