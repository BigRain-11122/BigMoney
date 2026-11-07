# 相位臂：把 r1325 的 buffer REJECT 与成本档放回它们自己的尺子里重判

面：`results/etf_book_phase_atlas_arms.json`｜脚本：`scripts/etf_book_phase_atlas_arms.py`｜基线面：`results/etf_book_phase_atlas.json`（cutoff 2026-11-06）

同日基线网格：格间 spread 5.28pp，格内 band 中位 6.74pp。

**面板一致性：MIXED_WORLDS** — 11 faces priced 2 different panels (58302d9c, a1a42aee): per-cell deltas across worlds are world differences, not rule effects

（判词不发布：本表的每个 Δ 都是「同一格、臂减基线」，跨面板相减得到的是世界差，不是规则效应。标签原文保留在 `verdict_if_coherent`；把臂重建到同一面板后自动恢复。）

## buffer_k05 — **NOT-SEPARABLE**

buffer k=0.05 on every cell (the r1325 arm, re-priced per phase)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.92pp | +10.77pp | +0.155pp | 5.31pp |
| 3 | 20 | +8.52pp | +8.46pp | +0.055pp | 6.94pp |
| 3 | 40 | +6.34pp | +6.66pp | -0.310pp | 12.70pp |
| 5 | 10 | +11.91pp | +11.44pp | +0.480pp | 3.18pp |
| 5 | 20 | +8.95pp | +9.07pp | -0.125pp | 6.23pp |
| 5 | 40 | +8.22pp | +8.10pp | +0.120pp | 10.04pp |
| 8 | 10 | +12.01pp | +11.94pp | +0.070pp | 3.45pp |
| 8 | 20 | +9.71pp | +10.06pp | -0.350pp | 5.88pp |
| 8 | 40 | +8.05pp | +8.03pp | +0.030pp | 8.41pp |
| 12 | 10 | +11.38pp | +11.44pp | -0.065pp | 2.20pp |
| 12 | 20 | +9.41pp | +9.42pp | -0.005pp | 7.17pp |
| 12 | 40 | +7.84pp | +7.70pp | +0.145pp | 7.03pp |

- cells 12/12 judged
- not-worse share 0.833 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.042pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## cost05 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **NOT-SEPARABLE**）

5bp/side on the whole grid (half the production toll)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +12.24pp | +10.77pp | +1.475pp | 4.47pp |
| 3 | 20 | +9.33pp | +8.46pp | +0.870pp | 7.07pp |
| 3 | 40 | +7.06pp | +6.66pp | +0.405pp | 12.48pp |
| 5 | 10 | +12.79pp | +11.44pp | +1.360pp | 3.65pp |
| 5 | 20 | +9.80pp | +9.07pp | +0.730pp | 6.40pp |
| 5 | 40 | +8.58pp | +8.10pp | +0.480pp | 9.71pp |
| 8 | 10 | +13.18pp | +11.94pp | +1.245pp | 3.43pp |
| 8 | 20 | +10.82pp | +10.06pp | +0.760pp | 6.59pp |
| 8 | 40 | +8.59pp | +8.03pp | +0.560pp | 8.58pp |
| 12 | 10 | +12.74pp | +11.44pp | +1.305pp | 2.78pp |
| 12 | 20 | +10.22pp | +9.42pp | +0.800pp | 7.86pp |
| 12 | 40 | +7.89pp | +7.70pp | +0.190pp | 6.93pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.780pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced a1a42aee, the baseline 58302d9c

## cost20 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **REJECT**）

20bp/side on the whole grid (double the production toll)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +8.16pp | +10.77pp | -2.600pp | 4.22pp |
| 3 | 20 | +7.09pp | +8.46pp | -1.370pp | 6.87pp |
| 3 | 40 | +5.95pp | +6.66pp | -0.710pp | 12.50pp |
| 5 | 10 | +8.96pp | +11.44pp | -2.475pp | 3.44pp |
| 5 | 20 | +7.66pp | +9.07pp | -1.415pp | 6.33pp |
| 5 | 40 | +7.52pp | +8.10pp | -0.580pp | 9.63pp |
| 8 | 10 | +9.55pp | +11.94pp | -2.380pp | 3.29pp |
| 8 | 20 | +8.72pp | +10.06pp | -1.340pp | 6.50pp |
| 8 | 40 | +7.50pp | +8.03pp | -0.520pp | 8.52pp |
| 12 | 10 | +9.38pp | +11.44pp | -2.065pp | 2.70pp |
| 12 | 20 | +8.32pp | +9.42pp | -1.100pp | 7.76pp |
| 12 | 40 | +6.87pp | +7.70pp | -0.835pp | 6.86pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -1.355pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced a1a42aee, the baseline 58302d9c

## cost40 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **REJECT**）

40bp/side on the whole grid (4x the production toll -- does 'the cadence is quotable' have a toll ceiling, and does the ordering vanish first?)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +2.99pp | +10.77pp | -7.775pp | 3.91pp |
| 3 | 20 | +4.20pp | +8.46pp | -4.260pp | 6.82pp |
| 3 | 40 | +4.43pp | +6.66pp | -2.220pp | 12.54pp |
| 5 | 10 | +4.04pp | +11.44pp | -7.400pp | 3.19pp |
| 5 | 20 | +4.86pp | +9.07pp | -4.215pp | 6.26pp |
| 5 | 40 | +6.08pp | +8.10pp | -2.020pp | 9.52pp |
| 8 | 10 | +4.89pp | +11.94pp | -7.040pp | 3.09pp |
| 8 | 20 | +5.98pp | +10.06pp | -4.080pp | 6.38pp |
| 8 | 40 | +6.08pp | +8.03pp | -1.945pp | 8.48pp |
| 12 | 10 | +5.03pp | +11.44pp | -6.415pp | 2.65pp |
| 12 | 20 | +5.81pp | +9.42pp | -3.610pp | 7.62pp |
| 12 | 40 | +5.51pp | +7.70pp | -2.190pp | 6.76pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -4.147pp (floor -0.05pp)
- resolvable share 0.333 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced a1a42aee, the baseline 58302d9c

## buffer_k10 — **NOT-SEPARABLE**

buffer k=0.10 on every cell (the middle of the family r1325 named as a cost knob; declared in the pool at r1351 before this face existed)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.80pp | +10.77pp | +0.035pp | 4.58pp |
| 3 | 20 | +8.68pp | +8.46pp | +0.220pp | 7.06pp |
| 3 | 40 | +6.28pp | +6.66pp | -0.375pp | 12.86pp |
| 5 | 10 | +12.38pp | +11.44pp | +0.950pp | 3.35pp |
| 5 | 20 | +9.22pp | +9.07pp | +0.150pp | 6.12pp |
| 5 | 40 | +7.69pp | +8.10pp | -0.410pp | 10.00pp |
| 8 | 10 | +12.40pp | +11.94pp | +0.465pp | 3.04pp |
| 8 | 20 | +10.10pp | +10.06pp | +0.040pp | 5.75pp |
| 8 | 40 | +8.14pp | +8.03pp | +0.115pp | 8.49pp |
| 12 | 10 | +11.36pp | +11.44pp | -0.080pp | 2.64pp |
| 12 | 20 | +9.46pp | +9.42pp | +0.045pp | 6.88pp |
| 12 | 40 | +7.97pp | +7.70pp | +0.275pp | 7.13pp |

- cells 12/12 judged
- not-worse share 0.833 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.080pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k20 — **NOT-SEPARABLE**

buffer k=0.20 on every cell (the strongest arm -- if even this stays inside every cell's band, the buffer family is unmeasurable on this design, not negative)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +12.16pp | +10.77pp | +1.400pp | 4.57pp |
| 3 | 20 | +9.46pp | +8.46pp | +1.000pp | 6.88pp |
| 3 | 40 | +6.64pp | +6.66pp | -0.010pp | 13.01pp |
| 5 | 10 | +12.04pp | +11.44pp | +0.610pp | 3.79pp |
| 5 | 20 | +9.79pp | +9.07pp | +0.715pp | 6.02pp |
| 5 | 40 | +7.85pp | +8.10pp | -0.250pp | 10.92pp |
| 8 | 10 | +12.01pp | +11.94pp | +0.070pp | 2.60pp |
| 8 | 20 | +9.99pp | +10.06pp | -0.070pp | 6.67pp |
| 8 | 40 | +8.41pp | +8.03pp | +0.385pp | 8.35pp |
| 12 | 10 | +11.32pp | +11.44pp | -0.120pp | 2.90pp |
| 12 | 20 | +9.44pp | +9.42pp | +0.020pp | 5.40pp |
| 12 | 40 | +7.75pp | +7.70pp | +0.055pp | 7.45pp |

- cells 12/12 judged
- not-worse share 0.917 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.062pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k02 — **NOT-SEPARABLE**

buffer k=0.02 on every cell (the near-zero end -- a knob that reads the same at 0.02 and at 0.20 is flat, not merely small)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.78pp | +10.77pp | +0.015pp | 4.62pp |
| 3 | 20 | +8.35pp | +8.46pp | -0.110pp | 6.87pp |
| 3 | 40 | +6.76pp | +6.66pp | +0.110pp | 12.00pp |
| 5 | 10 | +11.62pp | +11.44pp | +0.180pp | 3.45pp |
| 5 | 20 | +9.04pp | +9.07pp | -0.030pp | 6.29pp |
| 5 | 40 | +8.09pp | +8.10pp | -0.010pp | 9.94pp |
| 8 | 10 | +11.90pp | +11.94pp | -0.030pp | 3.30pp |
| 8 | 20 | +10.03pp | +10.06pp | -0.035pp | 6.25pp |
| 8 | 40 | +8.02pp | +8.03pp | -0.010pp | 8.61pp |
| 12 | 10 | +11.47pp | +11.44pp | +0.030pp | 2.21pp |
| 12 | 20 | +9.47pp | +9.42pp | +0.050pp | 7.53pp |
| 12 | 40 | +7.73pp | +7.70pp | +0.030pp | 7.20pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.002pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k40 — **REJECT**

buffer k=0.40 on every cell (8x the r1325 arm -- the far end, where a real buffer finally has to hurt)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +11.94pp | +10.77pp | +1.175pp | 3.79pp |
| 3 | 20 | +9.27pp | +8.46pp | +0.805pp | 6.64pp |
| 3 | 40 | +6.31pp | +6.66pp | -0.345pp | 12.73pp |
| 5 | 10 | +12.13pp | +11.44pp | +0.700pp | 4.13pp |
| 5 | 20 | +10.09pp | +9.07pp | +1.010pp | 5.89pp |
| 5 | 40 | +7.70pp | +8.10pp | -0.405pp | 11.36pp |
| 8 | 10 | +11.89pp | +11.94pp | -0.040pp | 2.87pp |
| 8 | 20 | +9.71pp | +10.06pp | -0.345pp | 6.13pp |
| 8 | 40 | +8.33pp | +8.03pp | +0.305pp | 9.23pp |
| 12 | 10 | +11.39pp | +11.44pp | -0.050pp | 2.80pp |
| 12 | 20 | +9.87pp | +9.42pp | +0.450pp | 5.38pp |
| 12 | 40 | +8.28pp | +7.70pp | +0.575pp | 8.21pp |

- cells 12/12 judged
- not-worse share 0.750 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.378pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k05_cost20 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **REJECT**）

buffer k=0.05 at 20bp/side -- the interaction neither family tested: does a buffer that is harmless at 10bp recover any of the -1.41pp the 20bp toll costs?

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +8.46pp | +10.77pp | -2.300pp | 5.13pp |
| 3 | 20 | +7.16pp | +8.46pp | -1.305pp | 6.89pp |
| 3 | 40 | +5.68pp | +6.66pp | -0.970pp | 12.72pp |
| 5 | 10 | +9.46pp | +11.44pp | -1.970pp | 3.11pp |
| 5 | 20 | +7.61pp | +9.07pp | -1.465pp | 6.21pp |
| 5 | 40 | +7.37pp | +8.10pp | -0.730pp | 10.04pp |
| 8 | 10 | +9.72pp | +11.94pp | -2.210pp | 3.53pp |
| 8 | 20 | +8.41pp | +10.06pp | -1.645pp | 5.99pp |
| 8 | 40 | +7.36pp | +8.03pp | -0.670pp | 8.27pp |
| 12 | 10 | +9.36pp | +11.44pp | -2.080pp | 2.18pp |
| 12 | 20 | +8.35pp | +9.42pp | -1.075pp | 7.17pp |
| 12 | 40 | +7.05pp | +7.70pp | -0.645pp | 6.99pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -1.385pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced a1a42aee, the baseline 58302d9c

## cost0 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **NOT-SEPARABLE**）

0bp/side on the whole grid (no toll at all) -- if the ordering only appears here, the ordering is bought with the toll and the 10bp reading stands

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +13.63pp | +10.77pp | +2.865pp | 4.58pp |
| 3 | 20 | +10.09pp | +8.46pp | +1.630pp | 7.15pp |
| 3 | 40 | +7.43pp | +6.66pp | +0.780pp | 12.47pp |
| 5 | 10 | +14.09pp | +11.44pp | +2.655pp | 3.72pp |
| 5 | 20 | +10.53pp | +9.07pp | +1.455pp | 6.41pp |
| 5 | 40 | +8.93pp | +8.10pp | +0.830pp | 9.73pp |
| 8 | 10 | +14.41pp | +11.94pp | +2.480pp | 3.49pp |
| 8 | 20 | +11.53pp | +10.06pp | +1.465pp | 6.62pp |
| 8 | 40 | +8.95pp | +8.03pp | +0.920pp | 8.61pp |
| 12 | 10 | +13.88pp | +11.44pp | +2.445pp | 2.81pp |
| 12 | 20 | +10.85pp | +9.42pp | +1.430pp | 7.89pp |
| 12 | 40 | +8.24pp | +7.70pp | +0.540pp | 6.96pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +1.460pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced a1a42aee, the baseline 58302d9c

