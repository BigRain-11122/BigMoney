# 相位臂：把 r1325 的 buffer REJECT 与成本档放回它们自己的尺子里重判

面：`results/etf_book_phase_atlas_arms.json`｜脚本：`scripts/etf_book_phase_atlas_arms.py`｜基线面：`results/etf_book_phase_atlas.json`（cutoff 2026-11-19）

同日基线网格：格间 spread 5.29pp，格内 band 中位 6.75pp。

**面板一致性：MIXED_WORLDS** — 11 faces priced 2 different panels (0d5a9cdc, 7d93f5cd): per-cell deltas across worlds are world differences, not rule effects

（判词不发布：本表的每个 Δ 都是「同一格、臂减基线」，跨面板相减得到的是世界差，不是规则效应。标签原文保留在 `verdict_if_coherent`；把臂重建到同一面板后自动恢复。）

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

## cost05 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **NOT-SEPARABLE**）

5bp/side on the whole grid (half the production toll)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +11.99pp | +10.61pp | +1.385pp | 4.57pp |
| 3 | 20 | +9.23pp | +8.48pp | +0.745pp | 7.16pp |
| 3 | 40 | +7.09pp | +6.67pp | +0.420pp | 12.40pp |
| 5 | 10 | +12.69pp | +11.44pp | +1.250pp | 3.47pp |
| 5 | 20 | +9.87pp | +9.18pp | +0.690pp | 6.46pp |
| 5 | 40 | +8.30pp | +7.88pp | +0.425pp | 10.09pp |
| 8 | 10 | +13.20pp | +11.96pp | +1.240pp | 3.27pp |
| 8 | 20 | +10.86pp | +10.18pp | +0.675pp | 6.40pp |
| 8 | 40 | +8.48pp | +8.17pp | +0.315pp | 8.80pp |
| 12 | 10 | +12.61pp | +11.46pp | +1.155pp | 2.84pp |
| 12 | 20 | +10.06pp | +9.44pp | +0.630pp | 7.46pp |
| 12 | 40 | +8.03pp | +7.67pp | +0.365pp | 7.09pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.682pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced 0d5a9cdc, the baseline 7d93f5cd

## cost20 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **REJECT**）

20bp/side on the whole grid (double the production toll)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +7.92pp | +10.61pp | -2.685pp | 4.31pp |
| 3 | 20 | +7.02pp | +8.48pp | -1.465pp | 7.12pp |
| 3 | 40 | +5.88pp | +6.67pp | -0.795pp | 12.42pp |
| 5 | 10 | +8.93pp | +11.44pp | -2.515pp | 3.24pp |
| 5 | 20 | +7.71pp | +9.18pp | -1.465pp | 6.31pp |
| 5 | 40 | +7.24pp | +7.88pp | -0.645pp | 9.99pp |
| 8 | 10 | +9.57pp | +11.96pp | -2.385pp | 3.10pp |
| 8 | 20 | +8.76pp | +10.18pp | -1.425pp | 6.34pp |
| 8 | 40 | +7.42pp | +8.17pp | -0.750pp | 8.70pp |
| 12 | 10 | +9.23pp | +11.46pp | -2.225pp | 2.76pp |
| 12 | 20 | +8.19pp | +9.44pp | -1.250pp | 7.36pp |
| 12 | 40 | +7.00pp | +7.67pp | -0.660pp | 7.02pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -1.445pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced 0d5a9cdc, the baseline 7d93f5cd

## cost40 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **REJECT**）

40bp/side on the whole grid (4x the production toll -- does 'the cadence is quotable' have a toll ceiling, and does the ordering vanish first?)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +2.71pp | +10.61pp | -7.890pp | 4.03pp |
| 3 | 20 | +4.14pp | +8.48pp | -4.340pp | 7.07pp |
| 3 | 40 | +4.26pp | +6.67pp | -2.410pp | 12.36pp |
| 5 | 10 | +4.03pp | +11.44pp | -7.415pp | 2.97pp |
| 5 | 20 | +4.91pp | +9.18pp | -4.270pp | 6.24pp |
| 5 | 40 | +5.83pp | +7.88pp | -2.050pp | 9.87pp |
| 8 | 10 | +4.91pp | +11.96pp | -7.055pp | 2.88pp |
| 8 | 20 | +6.01pp | +10.18pp | -4.165pp | 6.25pp |
| 8 | 40 | +6.00pp | +8.17pp | -2.165pp | 8.60pp |
| 12 | 10 | +4.88pp | +11.46pp | -6.575pp | 2.65pp |
| 12 | 20 | +5.73pp | +9.44pp | -3.705pp | 7.20pp |
| 12 | 40 | +5.66pp | +7.67pp | -2.010pp | 6.91pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -4.217pp (floor -0.05pp)
- resolvable share 0.333 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced 0d5a9cdc, the baseline 7d93f5cd

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

## buffer_k05_cost20 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **REJECT**）

buffer k=0.05 at 20bp/side -- the interaction neither family tested: does a buffer that is harmless at 10bp recover any of the -1.41pp the 20bp toll costs?

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +8.21pp | +10.61pp | -2.390pp | 5.23pp |
| 3 | 20 | +7.10pp | +8.48pp | -1.385pp | 7.17pp |
| 3 | 40 | +5.66pp | +6.67pp | -1.020pp | 12.75pp |
| 5 | 10 | +9.46pp | +11.44pp | -1.985pp | 2.95pp |
| 5 | 20 | +7.51pp | +9.18pp | -1.665pp | 6.18pp |
| 5 | 40 | +7.39pp | +7.88pp | -0.485pp | 10.39pp |
| 8 | 10 | +9.74pp | +11.96pp | -2.215pp | 3.41pp |
| 8 | 20 | +8.45pp | +10.18pp | -1.730pp | 5.93pp |
| 8 | 40 | +7.45pp | +8.17pp | -0.720pp | 8.42pp |
| 12 | 10 | +9.26pp | +11.46pp | -2.195pp | 2.20pp |
| 12 | 20 | +8.19pp | +9.44pp | -1.245pp | 6.81pp |
| 12 | 40 | +7.20pp | +7.67pp | -0.465pp | 7.08pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -1.525pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced 0d5a9cdc, the baseline 7d93f5cd

## cost0 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **NOT-SEPARABLE**）

0bp/side on the whole grid (no toll at all) -- if the ordering only appears here, the ordering is bought with the toll and the 10bp reading stands

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +13.37pp | +10.61pp | +2.765pp | 4.68pp |
| 3 | 20 | +9.97pp | +8.48pp | +1.490pp | 7.18pp |
| 3 | 40 | +7.48pp | +6.67pp | +0.805pp | 12.38pp |
| 5 | 10 | +13.97pp | +11.44pp | +2.530pp | 3.55pp |
| 5 | 20 | +10.60pp | +9.18pp | +1.415pp | 6.52pp |
| 5 | 40 | +8.66pp | +7.88pp | +0.785pp | 10.11pp |
| 8 | 10 | +14.44pp | +11.96pp | +2.480pp | 3.33pp |
| 8 | 20 | +11.56pp | +10.18pp | +1.380pp | 6.42pp |
| 8 | 40 | +8.85pp | +8.17pp | +0.675pp | 8.84pp |
| 12 | 10 | +13.74pp | +11.46pp | +2.290pp | 2.87pp |
| 12 | 20 | +10.69pp | +9.44pp | +1.255pp | 7.50pp |
| 12 | 40 | +8.37pp | +7.67pp | +0.705pp | 7.12pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +1.397pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced 0d5a9cdc, the baseline 7d93f5cd

