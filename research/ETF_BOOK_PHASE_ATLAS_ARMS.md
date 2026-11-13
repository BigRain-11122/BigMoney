# 相位臂：把 r1325 的 buffer REJECT 与成本档放回它们自己的尺子里重判

面：`results/etf_book_phase_atlas_arms.json`｜脚本：`scripts/etf_book_phase_atlas_arms.py`｜基线面：`results/etf_book_phase_atlas.json`（cutoff 2026-11-13）

同日基线网格：格间 spread 5.17pp，格内 band 中位 6.72pp。

**面板一致性：MIXED_WORLDS** — 11 faces priced 2 different panels (e383c3a6, e6f9d0e8): per-cell deltas across worlds are world differences, not rule effects

（判词不发布：本表的每个 Δ 都是「同一格、臂减基线」，跨面板相减得到的是世界差，不是规则效应。标签原文保留在 `verdict_if_coherent`；把臂重建到同一面板后自动恢复。）

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

## cost05 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **NOT-SEPARABLE**）

5bp/side on the whole grid (half the production toll)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +12.20pp | +10.79pp | +1.415pp | 4.52pp |
| 3 | 20 | +9.22pp | +8.45pp | +0.775pp | 7.00pp |
| 3 | 40 | +7.11pp | +6.70pp | +0.415pp | 12.52pp |
| 5 | 10 | +12.72pp | +11.40pp | +1.320pp | 3.66pp |
| 5 | 20 | +9.79pp | +9.02pp | +0.770pp | 6.43pp |
| 5 | 40 | +8.60pp | +8.18pp | +0.425pp | 9.68pp |
| 8 | 10 | +13.14pp | +11.86pp | +1.280pp | 3.27pp |
| 8 | 20 | +10.82pp | +10.07pp | +0.750pp | 6.65pp |
| 8 | 40 | +8.62pp | +8.23pp | +0.390pp | 8.56pp |
| 12 | 10 | +12.68pp | +11.46pp | +1.210pp | 2.81pp |
| 12 | 20 | +10.23pp | +9.55pp | +0.685pp | 7.90pp |
| 12 | 40 | +8.12pp | +7.71pp | +0.415pp | 6.90pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.760pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced e383c3a6, the baseline e6f9d0e8

## cost20 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **REJECT**）

20bp/side on the whole grid (double the production toll)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +8.12pp | +10.79pp | -2.660pp | 4.27pp |
| 3 | 20 | +7.00pp | +8.45pp | -1.455pp | 6.79pp |
| 3 | 40 | +5.99pp | +6.70pp | -0.705pp | 12.55pp |
| 5 | 10 | +8.93pp | +11.40pp | -2.470pp | 3.46pp |
| 5 | 20 | +7.63pp | +9.02pp | -1.380pp | 6.38pp |
| 5 | 40 | +7.53pp | +8.18pp | -0.650pp | 9.58pp |
| 8 | 10 | +9.51pp | +11.86pp | -2.355pp | 3.14pp |
| 8 | 20 | +8.72pp | +10.07pp | -1.350pp | 6.59pp |
| 8 | 40 | +7.55pp | +8.23pp | -0.680pp | 8.49pp |
| 12 | 10 | +9.30pp | +11.46pp | -2.160pp | 2.70pp |
| 12 | 20 | +8.36pp | +9.55pp | -1.195pp | 7.82pp |
| 12 | 40 | +7.10pp | +7.71pp | -0.605pp | 6.81pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -1.365pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced e383c3a6, the baseline e6f9d0e8

## cost40 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **REJECT**）

40bp/side on the whole grid (4x the production toll -- does 'the cadence is quotable' have a toll ceiling, and does the ordering vanish first?)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +2.92pp | +10.79pp | -7.860pp | 3.98pp |
| 3 | 20 | +4.13pp | +8.45pp | -4.315pp | 6.71pp |
| 3 | 40 | +4.42pp | +6.70pp | -2.275pp | 12.59pp |
| 5 | 10 | +4.00pp | +11.40pp | -7.400pp | 3.19pp |
| 5 | 20 | +4.82pp | +9.02pp | -4.195pp | 6.30pp |
| 5 | 40 | +6.07pp | +8.18pp | -2.105pp | 9.48pp |
| 8 | 10 | +4.83pp | +11.86pp | -7.030pp | 2.96pp |
| 8 | 20 | +5.97pp | +10.07pp | -4.095pp | 6.49pp |
| 8 | 40 | +6.14pp | +8.23pp | -2.095pp | 8.41pp |
| 12 | 10 | +4.96pp | +11.46pp | -6.510pp | 2.60pp |
| 12 | 20 | +5.88pp | +9.55pp | -3.675pp | 7.71pp |
| 12 | 40 | +5.75pp | +7.71pp | -1.960pp | 6.74pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -4.145pp (floor -0.05pp)
- resolvable share 0.333 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced e383c3a6, the baseline e6f9d0e8

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

## buffer_k05_cost20 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **REJECT**）

buffer k=0.05 at 20bp/side -- the interaction neither family tested: does a buffer that is harmless at 10bp recover any of the -1.41pp the 20bp toll costs?

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +8.43pp | +10.79pp | -2.360pp | 5.14pp |
| 3 | 20 | +7.19pp | +8.45pp | -1.260pp | 6.78pp |
| 3 | 40 | +5.71pp | +6.70pp | -0.980pp | 12.80pp |
| 5 | 10 | +9.44pp | +11.40pp | -1.965pp | 3.14pp |
| 5 | 20 | +7.55pp | +9.02pp | -1.460pp | 6.25pp |
| 5 | 40 | +7.51pp | +8.18pp | -0.665pp | 10.00pp |
| 8 | 10 | +9.68pp | +11.86pp | -2.185pp | 3.33pp |
| 8 | 20 | +8.41pp | +10.07pp | -1.660pp | 5.94pp |
| 8 | 40 | +7.50pp | +8.23pp | -0.735pp | 8.31pp |
| 12 | 10 | +9.34pp | +11.46pp | -2.125pp | 2.19pp |
| 12 | 20 | +8.40pp | +9.55pp | -1.150pp | 7.28pp |
| 12 | 40 | +7.26pp | +7.71pp | -0.445pp | 6.93pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -1.360pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced e383c3a6, the baseline e6f9d0e8

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

