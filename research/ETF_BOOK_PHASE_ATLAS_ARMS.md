# 相位臂：把 r1325 的 buffer REJECT 与成本档放回它们自己的尺子里重判

面：`results/etf_book_phase_atlas_arms.json`｜脚本：`scripts/etf_book_phase_atlas_arms.py`｜基线面：`results/etf_book_phase_atlas.json`（cutoff 2026-11-06）

同日基线网格：格间 spread 5.28pp，格内 band 中位 6.74pp。

**面板一致性：MIXED_WORLDS** — 11 faces priced 2 different panels (58302d9c, a1a42aee): per-cell deltas across worlds are world differences, not rule effects

（判词不发布：本表的每个 Δ 都是「同一格、臂减基线」，跨面板相减得到的是世界差，不是规则效应。标签原文保留在 `verdict_if_coherent`；把臂重建到同一面板后自动恢复。）

## buffer_k05 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **NOT-SEPARABLE**）

buffer k=0.05 on every cell (the r1325 arm, re-priced per phase)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +11.03pp | +10.77pp | +0.260pp | 5.34pp |
| 3 | 20 | +8.54pp | +8.46pp | +0.075pp | 6.95pp |
| 3 | 40 | +6.42pp | +6.66pp | -0.235pp | 12.74pp |
| 5 | 10 | +11.93pp | +11.44pp | +0.490pp | 3.23pp |
| 5 | 20 | +9.02pp | +9.07pp | -0.060pp | 6.23pp |
| 5 | 40 | +8.10pp | +8.10pp | -0.005pp | 10.10pp |
| 8 | 10 | +12.03pp | +11.94pp | +0.095pp | 3.62pp |
| 8 | 20 | +9.77pp | +10.06pp | -0.295pp | 6.02pp |
| 8 | 40 | +8.06pp | +8.03pp | +0.035pp | 8.31pp |
| 12 | 10 | +11.48pp | +11.44pp | +0.045pp | 2.22pp |
| 12 | 20 | +9.54pp | +9.42pp | +0.120pp | 7.23pp |
| 12 | 40 | +7.72pp | +7.70pp | +0.020pp | 7.02pp |

- cells 12/12 judged
- not-worse share 0.833 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.040pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: MIXED_WORLDS -- 11 faces priced 2 different panels (58302d9c, a1a42aee): per-cell deltas across worlds are world differences, not rule effects

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
- label withheld: MIXED_WORLDS -- 11 faces priced 2 different panels (58302d9c, a1a42aee): per-cell deltas across worlds are world differences, not rule effects

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
- label withheld: MIXED_WORLDS -- 11 faces priced 2 different panels (58302d9c, a1a42aee): per-cell deltas across worlds are world differences, not rule effects

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
- label withheld: MIXED_WORLDS -- 11 faces priced 2 different panels (58302d9c, a1a42aee): per-cell deltas across worlds are world differences, not rule effects

## buffer_k10 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **NOT-SEPARABLE**）

buffer k=0.10 on every cell (the middle of the family r1325 named as a cost knob; declared in the pool at r1351 before this face existed)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.90pp | +10.77pp | +0.140pp | 4.60pp |
| 3 | 20 | +8.78pp | +8.46pp | +0.320pp | 7.29pp |
| 3 | 40 | +6.13pp | +6.66pp | -0.520pp | 12.89pp |
| 5 | 10 | +12.46pp | +11.44pp | +1.020pp | 3.42pp |
| 5 | 20 | +9.23pp | +9.07pp | +0.160pp | 6.18pp |
| 5 | 40 | +7.89pp | +8.10pp | -0.205pp | 10.15pp |
| 8 | 10 | +12.48pp | +11.94pp | +0.545pp | 3.16pp |
| 8 | 20 | +10.12pp | +10.06pp | +0.060pp | 5.76pp |
| 8 | 40 | +8.24pp | +8.03pp | +0.215pp | 8.57pp |
| 12 | 10 | +11.59pp | +11.44pp | +0.145pp | 2.74pp |
| 12 | 20 | +9.68pp | +9.42pp | +0.255pp | 6.94pp |
| 12 | 40 | +7.91pp | +7.70pp | +0.205pp | 7.16pp |

- cells 12/12 judged
- not-worse share 0.833 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.182pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: MIXED_WORLDS -- 11 faces priced 2 different panels (58302d9c, a1a42aee): per-cell deltas across worlds are world differences, not rule effects

## buffer_k20 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **NOT-SEPARABLE**）

buffer k=0.20 on every cell (the strongest arm -- if even this stays inside every cell's band, the buffer family is unmeasurable on this design, not negative)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +12.41pp | +10.77pp | +1.650pp | 4.34pp |
| 3 | 20 | +9.68pp | +8.46pp | +1.220pp | 6.90pp |
| 3 | 40 | +7.79pp | +6.66pp | +1.140pp | 12.10pp |
| 5 | 10 | +12.50pp | +11.44pp | +1.065pp | 4.51pp |
| 5 | 20 | +9.75pp | +9.07pp | +0.675pp | 5.96pp |
| 5 | 40 | +7.86pp | +8.10pp | -0.240pp | 11.08pp |
| 8 | 10 | +12.11pp | +11.94pp | +0.175pp | 3.77pp |
| 8 | 20 | +10.46pp | +10.06pp | +0.395pp | 6.62pp |
| 8 | 40 | +8.81pp | +8.03pp | +0.785pp | 8.55pp |
| 12 | 10 | +11.47pp | +11.44pp | +0.030pp | 4.75pp |
| 12 | 20 | +9.57pp | +9.42pp | +0.155pp | 5.86pp |
| 12 | 40 | +8.10pp | +7.70pp | +0.395pp | 7.57pp |

- cells 12/12 judged
- not-worse share 0.917 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.535pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: MIXED_WORLDS -- 11 faces priced 2 different panels (58302d9c, a1a42aee): per-cell deltas across worlds are world differences, not rule effects

## buffer_k02 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **NOT-SEPARABLE**）

buffer k=0.02 on every cell (the near-zero end -- a knob that reads the same at 0.02 and at 0.20 is flat, not merely small)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.88pp | +10.77pp | +0.120pp | 4.66pp |
| 3 | 20 | +8.41pp | +8.46pp | -0.045pp | 7.09pp |
| 3 | 40 | +6.69pp | +6.66pp | +0.035pp | 12.45pp |
| 5 | 10 | +11.69pp | +11.44pp | +0.255pp | 3.51pp |
| 5 | 20 | +9.06pp | +9.07pp | -0.015pp | 6.26pp |
| 5 | 40 | +8.23pp | +8.10pp | +0.135pp | 9.90pp |
| 8 | 10 | +11.94pp | +11.94pp | +0.000pp | 3.41pp |
| 8 | 20 | +10.08pp | +10.06pp | +0.020pp | 6.22pp |
| 8 | 40 | +8.21pp | +8.03pp | +0.185pp | 8.46pp |
| 12 | 10 | +11.54pp | +11.44pp | +0.095pp | 2.35pp |
| 12 | 20 | +9.57pp | +9.42pp | +0.150pp | 7.59pp |
| 12 | 40 | +7.61pp | +7.70pp | -0.095pp | 7.25pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.065pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: MIXED_WORLDS -- 11 faces priced 2 different panels (58302d9c, a1a42aee): per-cell deltas across worlds are world differences, not rule effects

## buffer_k40 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **NOT-SEPARABLE**）

buffer k=0.40 on every cell (8x the r1325 arm -- the far end, where a real buffer finally has to hurt)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +12.07pp | +10.77pp | +1.305pp | 3.57pp |
| 3 | 20 | +9.35pp | +8.46pp | +0.885pp | 6.87pp |
| 3 | 40 | +6.30pp | +6.66pp | -0.350pp | 12.76pp |
| 5 | 10 | +12.17pp | +11.44pp | +0.735pp | 4.12pp |
| 5 | 20 | +10.29pp | +9.07pp | +1.215pp | 5.68pp |
| 5 | 40 | +8.05pp | +8.10pp | -0.050pp | 11.34pp |
| 8 | 10 | +12.06pp | +11.94pp | +0.130pp | 2.87pp |
| 8 | 20 | +9.76pp | +10.06pp | -0.305pp | 6.15pp |
| 8 | 40 | +8.56pp | +8.03pp | +0.540pp | 9.36pp |
| 12 | 10 | +11.54pp | +11.44pp | +0.105pp | 2.83pp |
| 12 | 20 | +9.97pp | +9.42pp | +0.555pp | 5.60pp |
| 12 | 40 | +8.38pp | +7.70pp | +0.680pp | 8.21pp |

- cells 12/12 judged
- not-worse share 0.833 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.548pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: MIXED_WORLDS -- 11 faces priced 2 different panels (58302d9c, a1a42aee): per-cell deltas across worlds are world differences, not rule effects

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
- label withheld: MIXED_WORLDS -- 11 faces priced 2 different panels (58302d9c, a1a42aee): per-cell deltas across worlds are world differences, not rule effects

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
- label withheld: MIXED_WORLDS -- 11 faces priced 2 different panels (58302d9c, a1a42aee): per-cell deltas across worlds are world differences, not rule effects

