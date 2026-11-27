# 相位臂：把 r1325 的 buffer REJECT 与成本档放回它们自己的尺子里重判

面：`results/etf_book_phase_atlas_arms.json`｜脚本：`scripts/etf_book_phase_atlas_arms.py`｜基线面：`results/etf_book_phase_atlas.json`（cutoff 2026-11-26）

同日基线网格：格间 spread 5.26pp，格内 band 中位 6.65pp。

**面板一致性：MIXED_WORLDS** — 11 faces priced 3 different panels (608916d7, 706c06e0, fdb64c20): per-cell deltas across worlds are world differences, not rule effects

（判词不发布：本表的每个 Δ 都是「同一格、臂减基线」，跨面板相减得到的是世界差，不是规则效应。标签原文保留在 `verdict_if_coherent`；把臂重建到同一面板后自动恢复。）

## 成本档 5bp → 20bp：多收的 15bp 是不是白收 — **TOLL_DRAINS**

两个成本臂只差这一只旋钮，所以「多收的费有没有被赚回来」只在这里能答。但逐格不是受控对照：引擎按 8% 波动目标只降不升地调仓，集中持仓（3 名）在本轮波动下降后会被加回目标仓位，这一份加仓比 15bp×换手更大——所以判据是「家族整体失血，且没有一格凭自己有把握地涨上去」。

| n_hold | rebal | 5bp | 20bp | Δ | 本格 band | 读数 |
|---|---|---|---|---|---|---|
| 3 | 10 | +11.73pp | +7.67pp | -4.065pp | 4.62pp | 跌 |
| 3 | 20 | +9.01pp | +6.82pp | -2.190pp | 7.15pp | 跌 |
| 3 | 40 | +6.83pp | +5.61pp | -1.220pp | 12.30pp | 跌 |
| 5 | 10 | +12.45pp | +8.65pp | -3.790pp | 3.48pp | 跌 |
| 5 | 20 | +9.63pp | +7.47pp | -2.165pp | 6.36pp | 跌 |
| 5 | 40 | +7.87pp | +6.79pp | -1.080pp | 9.97pp | 跌 |
| 8 | 10 | +12.83pp | +9.19pp | -3.645pp | 3.31pp | 跌 |
| 8 | 20 | +10.61pp | +8.50pp | -2.110pp | 6.30pp | 跌 |
| 8 | 40 | +8.30pp | +7.25pp | -1.060pp | 8.69pp | 跌 |
| 12 | 10 | +12.35pp | +8.96pp | -3.380pp | 2.91pp | 跌 |
| 12 | 20 | +9.80pp | +7.92pp | -1.885pp | 7.32pp | 跌 |
| 12 | 40 | +7.67pp | +6.66pp | -1.010pp | 7.01pp | 跌 |

- cells 12/12 judged against the baseline grid
- family total -27.60pp, median -2.138pp on the extra 15bp/side
- rising cells 0/12 (2 allowed), 0 of them beyond their own band
- the cells that do not fall stay inside their own band, and the family drains: no cell's wobble reads as a gain

## buffer_k05 — **REJECT**

buffer k=0.05 on every cell (the r1325 arm, re-priced per phase)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.37pp | +10.22pp | +0.150pp | 5.42pp |
| 3 | 20 | +8.11pp | +8.24pp | -0.135pp | 7.33pp |
| 3 | 40 | +6.12pp | +6.26pp | -0.150pp | 12.35pp |
| 5 | 10 | +11.54pp | +11.04pp | +0.490pp | 3.04pp |
| 5 | 20 | +8.53pp | +8.82pp | -0.300pp | 6.13pp |
| 5 | 40 | +7.64pp | +7.45pp | +0.195pp | 10.52pp |
| 8 | 10 | +11.61pp | +11.53pp | +0.085pp | 3.53pp |
| 8 | 20 | +9.53pp | +9.79pp | -0.265pp | 5.83pp |
| 8 | 40 | +7.77pp | +7.84pp | -0.075pp | 8.53pp |
| 12 | 10 | +10.91pp | +11.05pp | -0.140pp | 2.29pp |
| 12 | 20 | +9.00pp | +9.04pp | -0.035pp | 6.53pp |
| 12 | 40 | +7.45pp | +7.16pp | +0.290pp | 7.03pp |

- cells 12/12 judged
- not-worse share 0.833 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -0.055pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## cost05 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **NOT-SEPARABLE**）

5bp/side on the whole grid (half the production toll)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +11.73pp | +10.22pp | +1.510pp | 4.62pp |
| 3 | 20 | +9.01pp | +8.24pp | +0.760pp | 7.15pp |
| 3 | 40 | +6.83pp | +6.26pp | +0.560pp | 12.30pp |
| 5 | 10 | +12.45pp | +11.04pp | +1.400pp | 3.48pp |
| 5 | 20 | +9.63pp | +8.82pp | +0.810pp | 6.36pp |
| 5 | 40 | +7.87pp | +7.45pp | +0.425pp | 9.97pp |
| 8 | 10 | +12.83pp | +11.53pp | +1.305pp | 3.31pp |
| 8 | 20 | +10.61pp | +9.79pp | +0.820pp | 6.30pp |
| 8 | 40 | +8.30pp | +7.84pp | +0.460pp | 8.69pp |
| 12 | 10 | +12.35pp | +11.05pp | +1.290pp | 2.91pp |
| 12 | 20 | +9.80pp | +9.04pp | +0.765pp | 7.32pp |
| 12 | 40 | +7.67pp | +7.16pp | +0.510pp | 7.01pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.788pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced 706c06e0, the baseline fdb64c20

## cost20 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **REJECT**）

20bp/side on the whole grid (double the production toll)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +7.67pp | +10.22pp | -2.555pp | 4.37pp |
| 3 | 20 | +6.82pp | +8.24pp | -1.430pp | 7.06pp |
| 3 | 40 | +5.61pp | +6.26pp | -0.660pp | 12.24pp |
| 5 | 10 | +8.65pp | +11.04pp | -2.390pp | 3.25pp |
| 5 | 20 | +7.47pp | +8.82pp | -1.355pp | 6.17pp |
| 5 | 40 | +6.79pp | +7.45pp | -0.655pp | 9.86pp |
| 8 | 10 | +9.19pp | +11.53pp | -2.340pp | 3.14pp |
| 8 | 20 | +8.50pp | +9.79pp | -1.290pp | 6.20pp |
| 8 | 40 | +7.25pp | +7.84pp | -0.600pp | 8.54pp |
| 12 | 10 | +8.96pp | +11.05pp | -2.090pp | 2.81pp |
| 12 | 20 | +7.92pp | +9.04pp | -1.120pp | 7.21pp |
| 12 | 40 | +6.66pp | +7.16pp | -0.500pp | 6.91pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -1.323pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced 706c06e0, the baseline fdb64c20

## cost40 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **REJECT**）

40bp/side on the whole grid (4x the production toll -- does 'the cadence is quotable' have a toll ceiling, and does the ordering vanish first?)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +2.50pp | +10.22pp | -7.725pp | 5.95pp |
| 3 | 20 | +5.58pp | +8.24pp | -2.670pp | 6.59pp |
| 3 | 40 | +5.17pp | +6.26pp | -1.100pp | 12.13pp |
| 5 | 10 | +3.72pp | +11.04pp | -7.325pp | 3.77pp |
| 5 | 20 | +5.99pp | +8.82pp | -2.840pp | 6.08pp |
| 5 | 40 | +5.83pp | +7.45pp | -1.610pp | 9.36pp |
| 8 | 10 | +4.92pp | +11.53pp | -6.600pp | 3.19pp |
| 8 | 20 | +5.26pp | +9.79pp | -4.530pp | 6.08pp |
| 8 | 40 | +5.84pp | +7.84pp | -2.005pp | 8.21pp |
| 12 | 10 | +4.61pp | +11.05pp | -6.445pp | 2.69pp |
| 12 | 20 | +5.45pp | +9.04pp | -3.585pp | 7.03pp |
| 12 | 40 | +5.68pp | +7.16pp | -1.480pp | 6.76pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -3.212pp (floor -0.05pp)
- resolvable share 0.333 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced 706c06e0, the baseline fdb64c20

## buffer_k10 — **NOT-SEPARABLE**

buffer k=0.10 on every cell (the middle of the family r1325 named as a cost knob; declared in the pool at r1351 before this face existed)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.43pp | +10.22pp | +0.205pp | 4.62pp |
| 3 | 20 | +8.05pp | +8.24pp | -0.190pp | 7.43pp |
| 3 | 40 | +5.75pp | +6.26pp | -0.520pp | 12.20pp |
| 5 | 10 | +11.88pp | +11.04pp | +0.835pp | 3.61pp |
| 5 | 20 | +8.70pp | +8.82pp | -0.125pp | 6.09pp |
| 5 | 40 | +7.49pp | +7.45pp | +0.040pp | 10.40pp |
| 8 | 10 | +11.98pp | +11.53pp | +0.455pp | 3.09pp |
| 8 | 20 | +9.79pp | +9.79pp | +0.000pp | 5.77pp |
| 8 | 40 | +7.97pp | +7.84pp | +0.130pp | 8.42pp |
| 12 | 10 | +10.95pp | +11.05pp | -0.110pp | 2.75pp |
| 12 | 20 | +9.19pp | +9.04pp | +0.150pp | 6.46pp |
| 12 | 40 | +7.55pp | +7.16pp | +0.395pp | 7.32pp |

- cells 12/12 judged
- not-worse share 0.833 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.085pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k20 — **NOT-SEPARABLE**

buffer k=0.20 on every cell (the strongest arm -- if even this stays inside every cell's band, the buffer family is unmeasurable on this design, not negative)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +11.55pp | +10.22pp | +1.330pp | 4.79pp |
| 3 | 20 | +8.81pp | +8.24pp | +0.565pp | 7.00pp |
| 3 | 40 | +6.13pp | +6.26pp | -0.130pp | 12.35pp |
| 5 | 10 | +11.53pp | +11.04pp | +0.485pp | 4.01pp |
| 5 | 20 | +9.26pp | +8.82pp | +0.435pp | 6.02pp |
| 5 | 40 | +7.43pp | +7.45pp | -0.010pp | 10.94pp |
| 8 | 10 | +11.39pp | +11.53pp | -0.135pp | 2.69pp |
| 8 | 20 | +9.71pp | +9.79pp | -0.080pp | 6.21pp |
| 8 | 40 | +8.07pp | +7.84pp | +0.230pp | 8.37pp |
| 12 | 10 | +10.90pp | +11.05pp | -0.155pp | 2.91pp |
| 12 | 20 | +9.19pp | +9.04pp | +0.150pp | 5.59pp |
| 12 | 40 | +7.52pp | +7.16pp | +0.360pp | 7.61pp |

- cells 12/12 judged
- not-worse share 0.917 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.190pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k02 — **NOT-SEPARABLE**

buffer k=0.02 on every cell (the near-zero end -- a knob that reads the same at 0.02 and at 0.20 is flat, not merely small)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.23pp | +10.22pp | +0.015pp | 4.73pp |
| 3 | 20 | +8.05pp | +8.24pp | -0.195pp | 7.29pp |
| 3 | 40 | +6.37pp | +6.26pp | +0.105pp | 12.00pp |
| 5 | 10 | +11.21pp | +11.04pp | +0.165pp | 3.28pp |
| 5 | 20 | +8.79pp | +8.82pp | -0.030pp | 6.20pp |
| 5 | 40 | +7.46pp | +7.45pp | +0.010pp | 10.12pp |
| 8 | 10 | +11.50pp | +11.53pp | -0.025pp | 3.31pp |
| 8 | 20 | +9.75pp | +9.79pp | -0.040pp | 5.78pp |
| 8 | 40 | +7.83pp | +7.84pp | -0.015pp | 8.50pp |
| 12 | 10 | +11.03pp | +11.05pp | -0.025pp | 2.31pp |
| 12 | 20 | +9.03pp | +9.04pp | -0.005pp | 7.20pp |
| 12 | 40 | +7.27pp | +7.16pp | +0.110pp | 7.23pp |

- cells 12/12 judged
- not-worse share 0.917 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -0.010pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k40 — **NOT-SEPARABLE**

buffer k=0.40 on every cell (8x the r1325 arm -- the far end, where a real buffer finally has to hurt)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +11.74pp | +10.22pp | +1.520pp | 3.94pp |
| 3 | 20 | +9.03pp | +8.24pp | +0.785pp | 7.02pp |
| 3 | 40 | +5.68pp | +6.26pp | -0.585pp | 12.65pp |
| 5 | 10 | +11.79pp | +11.04pp | +0.750pp | 4.48pp |
| 5 | 20 | +9.48pp | +8.82pp | +0.655pp | 6.26pp |
| 5 | 40 | +7.44pp | +7.45pp | -0.005pp | 11.62pp |
| 8 | 10 | +11.61pp | +11.53pp | +0.080pp | 2.98pp |
| 8 | 20 | +9.37pp | +9.79pp | -0.420pp | 6.08pp |
| 8 | 40 | +8.12pp | +7.84pp | +0.270pp | 9.63pp |
| 12 | 10 | +10.98pp | +11.05pp | -0.070pp | 2.82pp |
| 12 | 20 | +9.66pp | +9.04pp | +0.630pp | 5.67pp |
| 12 | 40 | +8.18pp | +7.16pp | +1.020pp | 8.29pp |

- cells 12/12 judged
- not-worse share 0.833 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.450pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k05_cost20 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **REJECT**）

buffer k=0.05 at 20bp/side -- the interaction neither family tested: does a buffer that is harmless at 10bp recover any of the -1.41pp the 20bp toll costs?

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +7.96pp | +10.22pp | -2.260pp | 5.26pp |
| 3 | 20 | +6.79pp | +8.24pp | -1.455pp | 7.04pp |
| 3 | 40 | +5.47pp | +6.26pp | -0.790pp | 12.41pp |
| 5 | 10 | +9.16pp | +11.04pp | -1.880pp | 2.95pp |
| 5 | 20 | +7.22pp | +8.82pp | -1.600pp | 5.94pp |
| 5 | 40 | +7.10pp | +7.45pp | -0.345pp | 10.25pp |
| 8 | 10 | +9.38pp | +11.53pp | -2.150pp | 3.46pp |
| 8 | 20 | +8.22pp | +9.79pp | -1.570pp | 5.83pp |
| 8 | 40 | +7.21pp | +7.84pp | -0.640pp | 8.25pp |
| 12 | 10 | +8.98pp | +11.05pp | -2.070pp | 2.29pp |
| 12 | 20 | +7.92pp | +9.04pp | -1.115pp | 6.67pp |
| 12 | 40 | +6.93pp | +7.16pp | -0.230pp | 6.93pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -1.513pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced 706c06e0, the baseline fdb64c20

## cost0 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **NOT-SEPARABLE**）

0bp/side on the whole grid (no toll at all) -- if the ordering only appears here, the ordering is bought with the toll and the 10bp reading stands

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +13.01pp | +10.22pp | +2.790pp | 4.68pp |
| 3 | 20 | +9.78pp | +8.24pp | +1.535pp | 7.30pp |
| 3 | 40 | +7.18pp | +6.26pp | +0.915pp | 12.03pp |
| 5 | 10 | +13.61pp | +11.04pp | +2.565pp | 3.43pp |
| 5 | 20 | +10.34pp | +8.82pp | +1.515pp | 6.45pp |
| 5 | 40 | +8.23pp | +7.45pp | +0.785pp | 10.15pp |
| 8 | 10 | +14.02pp | +11.53pp | +2.495pp | 3.24pp |
| 8 | 20 | +11.21pp | +9.79pp | +1.415pp | 6.23pp |
| 8 | 40 | +8.60pp | +7.84pp | +0.755pp | 8.83pp |
| 12 | 10 | +13.34pp | +11.05pp | +2.285pp | 2.83pp |
| 12 | 20 | +10.32pp | +9.04pp | +1.290pp | 7.21pp |
| 12 | 40 | +7.88pp | +7.16pp | +0.720pp | 7.03pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +1.465pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced 608916d7, the baseline fdb64c20

