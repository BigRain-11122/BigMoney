# 相位臂：把 r1325 的 buffer REJECT 与成本档放回它们自己的尺子里重判

面：`results/etf_book_phase_atlas_arms.json`｜脚本：`scripts/etf_book_phase_atlas_arms.py`｜基线面：`results/etf_book_phase_atlas.json`（cutoff 2026-11-19）

同日基线网格：格间 spread 5.29pp，格内 band 中位 6.75pp。

**面板一致性：ONE_WORLD** — all 11 faces priced 7d93f5cd045aab6d

## buffer_k05 — **NOT-SEPARABLE**

buffer k=0.05 on every cell (the r1325 arm, re-priced per phase)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +14.43pp | +10.61pp | +3.825pp | 6.21pp |
| 3 | 20 | +9.90pp | +8.48pp | +1.415pp | 8.26pp |
| 3 | 40 | +7.07pp | +6.67pp | +0.390pp | 11.11pp |
| 5 | 10 | +12.21pp | +11.44pp | +0.775pp | 5.44pp |
| 5 | 20 | +10.54pp | +9.18pp | +1.365pp | 7.24pp |
| 5 | 40 | +8.37pp | +7.88pp | +0.485pp | 10.00pp |
| 8 | 10 | +12.29pp | +11.96pp | +0.330pp | 4.80pp |
| 8 | 20 | +10.33pp | +10.18pp | +0.150pp | 8.04pp |
| 8 | 40 | +8.28pp | +8.17pp | +0.110pp | 8.72pp |
| 12 | 10 | +11.41pp | +11.46pp | -0.040pp | 3.12pp |
| 12 | 20 | +9.38pp | +9.44pp | -0.050pp | 6.82pp |
| 12 | 40 | +8.60pp | +7.67pp | +0.930pp | 7.21pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.438pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## cost05 — **NOT-SEPARABLE**

5bp/side on the whole grid (half the production toll)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +11.97pp | +10.61pp | +1.370pp | 4.58pp |
| 3 | 20 | +9.22pp | +8.48pp | +0.735pp | 7.28pp |
| 3 | 40 | +7.08pp | +6.67pp | +0.405pp | 12.38pp |
| 5 | 10 | +12.71pp | +11.44pp | +1.275pp | 3.45pp |
| 5 | 20 | +9.91pp | +9.18pp | +0.730pp | 6.50pp |
| 5 | 40 | +8.23pp | +7.88pp | +0.355pp | 10.08pp |
| 8 | 10 | +13.19pp | +11.96pp | +1.225pp | 3.27pp |
| 8 | 20 | +10.89pp | +10.18pp | +0.715pp | 6.39pp |
| 8 | 40 | +8.53pp | +8.17pp | +0.355pp | 8.76pp |
| 12 | 10 | +12.59pp | +11.46pp | +1.135pp | 2.86pp |
| 12 | 20 | +10.06pp | +9.44pp | +0.630pp | 7.42pp |
| 12 | 40 | +8.01pp | +7.67pp | +0.340pp | 7.08pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.722pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## cost20 — **REJECT**

20bp/side on the whole grid (double the production toll)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +7.92pp | +10.61pp | -2.690pp | 4.28pp |
| 3 | 20 | +7.01pp | +8.48pp | -1.470pp | 7.21pp |
| 3 | 40 | +5.86pp | +6.67pp | -0.820pp | 12.32pp |
| 5 | 10 | +8.92pp | +11.44pp | -2.520pp | 3.21pp |
| 5 | 20 | +7.74pp | +9.18pp | -1.440pp | 6.39pp |
| 5 | 40 | +7.17pp | +7.88pp | -0.705pp | 9.98pp |
| 8 | 10 | +9.54pp | +11.96pp | -2.420pp | 3.08pp |
| 8 | 20 | +8.77pp | +10.18pp | -1.410pp | 6.33pp |
| 8 | 40 | +7.46pp | +8.17pp | -0.710pp | 8.66pp |
| 12 | 10 | +9.21pp | +11.46pp | -2.240pp | 2.76pp |
| 12 | 20 | +8.18pp | +9.44pp | -1.260pp | 7.32pp |
| 12 | 40 | +6.99pp | +7.67pp | -0.680pp | 7.00pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -1.425pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## cost40 — **REJECT**

40bp/side on the whole grid (4x the production toll -- does 'the cadence is quotable' have a toll ceiling, and does the ordering vanish first?)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +4.37pp | +10.61pp | -6.240pp | 6.96pp |
| 3 | 20 | +6.45pp | +8.48pp | -2.035pp | 8.72pp |
| 3 | 40 | +4.79pp | +6.67pp | -1.885pp | 11.74pp |
| 5 | 10 | +4.68pp | +11.44pp | -6.760pp | 6.05pp |
| 5 | 20 | +6.47pp | +9.18pp | -2.705pp | 8.50pp |
| 5 | 40 | +6.41pp | +7.88pp | -1.470pp | 9.86pp |
| 8 | 10 | +5.26pp | +11.96pp | -6.700pp | 3.07pp |
| 8 | 20 | +6.36pp | +10.18pp | -3.820pp | 5.45pp |
| 8 | 40 | +6.05pp | +8.17pp | -2.120pp | 8.53pp |
| 12 | 10 | +5.53pp | +11.46pp | -5.925pp | 3.63pp |
| 12 | 20 | +5.71pp | +9.44pp | -3.725pp | 7.19pp |
| 12 | 40 | +6.07pp | +7.67pp | -1.600pp | 6.90pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -3.215pp (floor -0.05pp)
- resolvable share 0.250 (|delta| > the cell's own band; floor 0.50)

## buffer_k10 — **NOT-SEPARABLE**

buffer k=0.10 on every cell (the middle of the family r1325 named as a cost knob; declared in the pool at r1351 before this face existed)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.79pp | +10.61pp | +0.185pp | 4.68pp |
| 3 | 20 | +8.40pp | +8.48pp | -0.080pp | 7.42pp |
| 3 | 40 | +6.17pp | +6.67pp | -0.510pp | 12.64pp |
| 5 | 10 | +12.24pp | +11.44pp | +0.800pp | 3.54pp |
| 5 | 20 | +9.12pp | +9.18pp | -0.055pp | 6.22pp |
| 5 | 40 | +7.75pp | +7.88pp | -0.135pp | 10.41pp |
| 8 | 10 | +12.39pp | +11.96pp | +0.430pp | 3.06pp |
| 8 | 20 | +10.19pp | +10.18pp | +0.005pp | 5.68pp |
| 8 | 40 | +8.26pp | +8.17pp | +0.090pp | 8.61pp |
| 12 | 10 | +11.38pp | +11.46pp | -0.080pp | 2.73pp |
| 12 | 20 | +9.59pp | +9.44pp | +0.155pp | 6.66pp |
| 12 | 40 | +8.04pp | +7.67pp | +0.375pp | 7.29pp |

- cells 12/12 judged
- not-worse share 0.917 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.048pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k20 — **NOT-SEPARABLE**

buffer k=0.20 on every cell (the strongest arm -- if even this stays inside every cell's band, the buffer family is unmeasurable on this design, not negative)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +11.99pp | +10.61pp | +1.390pp | 4.77pp |
| 3 | 20 | +9.21pp | +8.48pp | +0.720pp | 7.11pp |
| 3 | 40 | +6.55pp | +6.67pp | -0.125pp | 12.79pp |
| 5 | 10 | +11.97pp | +11.44pp | +0.530pp | 3.96pp |
| 5 | 20 | +9.70pp | +9.18pp | +0.520pp | 6.09pp |
| 5 | 40 | +7.83pp | +7.88pp | -0.055pp | 11.07pp |
| 8 | 10 | +11.82pp | +11.96pp | -0.140pp | 2.64pp |
| 8 | 20 | +10.10pp | +10.18pp | -0.080pp | 6.54pp |
| 8 | 40 | +8.47pp | +8.17pp | +0.305pp | 8.52pp |
| 12 | 10 | +11.31pp | +11.46pp | -0.140pp | 2.94pp |
| 12 | 20 | +9.50pp | +9.44pp | +0.065pp | 5.48pp |
| 12 | 40 | +7.91pp | +7.67pp | +0.245pp | 7.68pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.155pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k02 — **NOT-SEPARABLE**

buffer k=0.02 on every cell (the near-zero end -- a knob that reads the same at 0.02 and at 0.20 is flat, not merely small)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.62pp | +10.61pp | +0.015pp | 4.75pp |
| 3 | 20 | +8.34pp | +8.48pp | -0.150pp | 7.27pp |
| 3 | 40 | +6.79pp | +6.67pp | +0.110pp | 12.37pp |
| 5 | 10 | +11.61pp | +11.44pp | +0.165pp | 3.29pp |
| 5 | 20 | +9.15pp | +9.18pp | -0.025pp | 6.33pp |
| 5 | 40 | +7.89pp | +7.88pp | +0.015pp | 10.04pp |
| 8 | 10 | +11.93pp | +11.96pp | -0.030pp | 3.31pp |
| 8 | 20 | +10.14pp | +10.18pp | -0.035pp | 6.01pp |
| 8 | 40 | +8.16pp | +8.17pp | -0.010pp | 8.44pp |
| 12 | 10 | +11.42pp | +11.46pp | -0.035pp | 2.33pp |
| 12 | 20 | +9.43pp | +9.44pp | -0.005pp | 7.41pp |
| 12 | 40 | +7.70pp | +7.67pp | +0.035pp | 7.31pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -0.007pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k40 — **NOT-SEPARABLE**

buffer k=0.40 on every cell (8x the r1325 arm -- the far end, where a real buffer finally has to hurt)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +12.10pp | +10.61pp | +1.495pp | 3.89pp |
| 3 | 20 | +9.30pp | +8.48pp | +0.820pp | 6.80pp |
| 3 | 40 | +6.12pp | +6.67pp | -0.555pp | 13.02pp |
| 5 | 10 | +12.13pp | +11.44pp | +0.690pp | 4.40pp |
| 5 | 20 | +9.80pp | +9.18pp | +0.620pp | 6.15pp |
| 5 | 40 | +7.85pp | +7.88pp | -0.030pp | 11.57pp |
| 8 | 10 | +11.97pp | +11.96pp | +0.010pp | 2.94pp |
| 8 | 20 | +9.75pp | +10.18pp | -0.430pp | 6.24pp |
| 8 | 40 | +8.48pp | +8.17pp | +0.310pp | 9.65pp |
| 12 | 10 | +11.39pp | +11.46pp | -0.060pp | 2.76pp |
| 12 | 20 | +10.02pp | +9.44pp | +0.585pp | 5.48pp |
| 12 | 40 | +8.46pp | +7.67pp | +0.790pp | 8.35pp |

- cells 12/12 judged
- not-worse share 0.833 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.448pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k05_cost20 — **REJECT**

buffer k=0.05 at 20bp/side -- the interaction neither family tested: does a buffer that is harmless at 10bp recover any of the -1.41pp the 20bp toll costs?

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +8.21pp | +10.61pp | -2.395pp | 5.24pp |
| 3 | 20 | +7.11pp | +8.48pp | -1.375pp | 7.34pp |
| 3 | 40 | +5.67pp | +6.67pp | -1.005pp | 12.73pp |
| 5 | 10 | +9.45pp | +11.44pp | -1.995pp | 2.96pp |
| 5 | 20 | +7.53pp | +9.18pp | -1.655pp | 6.26pp |
| 5 | 40 | +7.36pp | +7.88pp | -0.520pp | 10.47pp |
| 8 | 10 | +9.71pp | +11.96pp | -2.255pp | 3.40pp |
| 8 | 20 | +8.48pp | +10.18pp | -1.700pp | 5.90pp |
| 8 | 40 | +7.49pp | +8.17pp | -0.685pp | 8.39pp |
| 12 | 10 | +9.26pp | +11.46pp | -2.200pp | 2.21pp |
| 12 | 20 | +8.18pp | +9.44pp | -1.260pp | 6.76pp |
| 12 | 40 | +7.22pp | +7.67pp | -0.440pp | 7.03pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -1.515pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## cost0 — **NOT-SEPARABLE**

0bp/side on the whole grid (no toll at all) -- if the ordering only appears here, the ordering is bought with the toll and the 10bp reading stands

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +13.37pp | +10.61pp | +2.760pp | 4.72pp |
| 3 | 20 | +9.96pp | +8.48pp | +1.480pp | 7.31pp |
| 3 | 40 | +7.49pp | +6.67pp | +0.815pp | 12.39pp |
| 5 | 10 | +14.01pp | +11.44pp | +2.565pp | 3.54pp |
| 5 | 20 | +10.64pp | +9.18pp | +1.465pp | 6.57pp |
| 5 | 40 | +8.60pp | +7.88pp | +0.715pp | 10.10pp |
| 8 | 10 | +14.43pp | +11.96pp | +2.465pp | 3.34pp |
| 8 | 20 | +11.61pp | +10.18pp | +1.425pp | 6.41pp |
| 8 | 40 | +8.88pp | +8.17pp | +0.715pp | 8.80pp |
| 12 | 10 | +13.72pp | +11.46pp | +2.265pp | 2.89pp |
| 12 | 20 | +10.70pp | +9.44pp | +1.265pp | 7.45pp |
| 12 | 40 | +8.35pp | +7.67pp | +0.680pp | 7.12pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +1.445pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

