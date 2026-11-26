# 相位臂：把 r1325 的 buffer REJECT 与成本档放回它们自己的尺子里重判

面：`results/etf_book_phase_atlas_arms.json`｜脚本：`scripts/etf_book_phase_atlas_arms.py`｜基线面：`results/etf_book_phase_atlas.json`（cutoff 2026-11-25）

同日基线网格：格间 spread 5.18pp，格内 band 中位 6.63pp。

**面板一致性：MIXED_WORLDS** — 11 faces priced 2 different panels (608916d7, 706c06e0): per-cell deltas across worlds are world differences, not rule effects

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

## buffer_k05 — **NOT-SEPARABLE**

buffer k=0.05 on every cell (the r1325 arm, re-priced per phase)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +14.34pp | +10.26pp | +4.080pp | 5.28pp |
| 3 | 20 | +10.49pp | +8.29pp | +2.200pp | 5.87pp |
| 3 | 40 | +7.32pp | +6.38pp | +0.945pp | 10.28pp |
| 5 | 10 | +11.97pp | +11.06pp | +0.905pp | 5.53pp |
| 5 | 20 | +9.40pp | +8.88pp | +0.515pp | 8.28pp |
| 5 | 40 | +7.72pp | +7.50pp | +0.220pp | 10.03pp |
| 8 | 10 | +11.64pp | +11.56pp | +0.085pp | 3.52pp |
| 8 | 20 | +9.56pp | +9.82pp | -0.260pp | 5.37pp |
| 8 | 40 | +7.80pp | +7.88pp | -0.075pp | 8.47pp |
| 12 | 10 | +11.04pp | +11.10pp | -0.060pp | 2.01pp |
| 12 | 20 | +9.04pp | +9.05pp | -0.005pp | 6.50pp |
| 12 | 40 | +7.49pp | +7.20pp | +0.290pp | 7.11pp |

- cells 12/12 judged
- not-worse share 0.917 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.255pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## cost05 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **NOT-SEPARABLE**）

5bp/side on the whole grid (half the production toll)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +11.73pp | +10.26pp | +1.475pp | 4.62pp |
| 3 | 20 | +9.01pp | +8.29pp | +0.715pp | 7.15pp |
| 3 | 40 | +6.83pp | +6.38pp | +0.450pp | 12.30pp |
| 5 | 10 | +12.45pp | +11.06pp | +1.380pp | 3.48pp |
| 5 | 20 | +9.63pp | +8.88pp | +0.750pp | 6.36pp |
| 5 | 40 | +7.87pp | +7.50pp | +0.365pp | 9.97pp |
| 8 | 10 | +12.83pp | +11.56pp | +1.270pp | 3.31pp |
| 8 | 20 | +10.61pp | +9.82pp | +0.790pp | 6.30pp |
| 8 | 40 | +8.30pp | +7.88pp | +0.430pp | 8.69pp |
| 12 | 10 | +12.35pp | +11.10pp | +1.245pp | 2.91pp |
| 12 | 20 | +9.80pp | +9.05pp | +0.750pp | 7.32pp |
| 12 | 40 | +7.67pp | +7.20pp | +0.470pp | 7.01pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.750pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced 706c06e0, the baseline 608916d7

## cost20 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **REJECT**）

20bp/side on the whole grid (double the production toll)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +7.67pp | +10.26pp | -2.590pp | 4.37pp |
| 3 | 20 | +6.82pp | +8.29pp | -1.475pp | 7.06pp |
| 3 | 40 | +5.61pp | +6.38pp | -0.770pp | 12.24pp |
| 5 | 10 | +8.65pp | +11.06pp | -2.410pp | 3.25pp |
| 5 | 20 | +7.47pp | +8.88pp | -1.415pp | 6.17pp |
| 5 | 40 | +6.79pp | +7.50pp | -0.715pp | 9.86pp |
| 8 | 10 | +9.19pp | +11.56pp | -2.375pp | 3.14pp |
| 8 | 20 | +8.50pp | +9.82pp | -1.320pp | 6.20pp |
| 8 | 40 | +7.25pp | +7.88pp | -0.630pp | 8.54pp |
| 12 | 10 | +8.96pp | +11.10pp | -2.135pp | 2.81pp |
| 12 | 20 | +7.92pp | +9.05pp | -1.135pp | 7.21pp |
| 12 | 40 | +6.66pp | +7.20pp | -0.540pp | 6.91pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -1.368pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced 706c06e0, the baseline 608916d7

## cost40 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **REJECT**）

40bp/side on the whole grid (4x the production toll -- does 'the cadence is quotable' have a toll ceiling, and does the ordering vanish first?)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +2.50pp | +10.26pp | -7.760pp | 5.95pp |
| 3 | 20 | +5.58pp | +8.29pp | -2.715pp | 6.59pp |
| 3 | 40 | +5.17pp | +6.38pp | -1.210pp | 12.13pp |
| 5 | 10 | +3.72pp | +11.06pp | -7.345pp | 3.77pp |
| 5 | 20 | +5.99pp | +8.88pp | -2.900pp | 6.08pp |
| 5 | 40 | +5.83pp | +7.50pp | -1.670pp | 9.36pp |
| 8 | 10 | +4.92pp | +11.56pp | -6.635pp | 3.19pp |
| 8 | 20 | +5.26pp | +9.82pp | -4.560pp | 6.08pp |
| 8 | 40 | +5.84pp | +7.88pp | -2.035pp | 8.21pp |
| 12 | 10 | +4.61pp | +11.10pp | -6.490pp | 2.69pp |
| 12 | 20 | +5.45pp | +9.05pp | -3.600pp | 7.03pp |
| 12 | 40 | +5.68pp | +7.20pp | -1.520pp | 6.76pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -3.250pp (floor -0.05pp)
- resolvable share 0.333 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced 706c06e0, the baseline 608916d7

## buffer_k10 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **NOT-SEPARABLE**）

buffer k=0.10 on every cell (the middle of the family r1325 named as a cost knob; declared in the pool at r1351 before this face existed)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.53pp | +10.26pp | +0.275pp | 4.67pp |
| 3 | 20 | +8.23pp | +8.29pp | -0.060pp | 7.29pp |
| 3 | 40 | +5.93pp | +6.38pp | -0.445pp | 12.32pp |
| 5 | 10 | +12.08pp | +11.06pp | +1.015pp | 5.76pp |
| 5 | 20 | +9.49pp | +8.88pp | +0.605pp | 6.22pp |
| 5 | 40 | +8.22pp | +7.50pp | +0.715pp | 10.25pp |
| 8 | 10 | +12.21pp | +11.56pp | +0.655pp | 2.60pp |
| 8 | 20 | +9.93pp | +9.82pp | +0.105pp | 5.67pp |
| 8 | 40 | +8.09pp | +7.88pp | +0.210pp | 8.51pp |
| 12 | 10 | +11.13pp | +11.10pp | +0.035pp | 2.76pp |
| 12 | 20 | +9.32pp | +9.05pp | +0.275pp | 6.51pp |
| 12 | 40 | +7.37pp | +7.20pp | +0.165pp | 7.20pp |

- cells 12/12 judged
- not-worse share 0.917 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.242pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced 706c06e0, the baseline 608916d7

## buffer_k20 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **NOT-SEPARABLE**）

buffer k=0.20 on every cell (the strongest arm -- if even this stays inside every cell's band, the buffer family is unmeasurable on this design, not negative)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +11.71pp | +10.26pp | +1.450pp | 4.87pp |
| 3 | 20 | +8.97pp | +8.29pp | +0.680pp | 6.97pp |
| 3 | 40 | +6.34pp | +6.38pp | -0.030pp | 12.47pp |
| 5 | 10 | +11.72pp | +11.06pp | +0.660pp | 4.03pp |
| 5 | 20 | +9.42pp | +8.88pp | +0.535pp | 6.03pp |
| 5 | 40 | +7.58pp | +7.50pp | +0.070pp | 10.83pp |
| 8 | 10 | +11.59pp | +11.56pp | +0.030pp | 2.68pp |
| 8 | 20 | +9.81pp | +9.82pp | -0.005pp | 6.35pp |
| 8 | 40 | +8.22pp | +7.88pp | +0.350pp | 8.35pp |
| 12 | 10 | +11.04pp | +11.10pp | -0.060pp | 2.99pp |
| 12 | 20 | +9.23pp | +9.05pp | +0.185pp | 5.43pp |
| 12 | 40 | +7.56pp | +7.20pp | +0.360pp | 7.54pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.267pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced 706c06e0, the baseline 608916d7

## buffer_k02 — **NOT-SEPARABLE**

buffer k=0.02 on every cell (the near-zero end -- a knob that reads the same at 0.02 and at 0.20 is flat, not merely small)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.27pp | +10.26pp | +0.015pp | 4.78pp |
| 3 | 20 | +8.11pp | +8.29pp | -0.180pp | 7.27pp |
| 3 | 40 | +6.46pp | +6.38pp | +0.090pp | 12.00pp |
| 5 | 10 | +11.23pp | +11.06pp | +0.165pp | 3.22pp |
| 5 | 20 | +8.86pp | +8.88pp | -0.030pp | 6.21pp |
| 5 | 40 | +7.51pp | +7.50pp | +0.010pp | 10.06pp |
| 8 | 10 | +11.53pp | +11.56pp | -0.035pp | 3.28pp |
| 8 | 20 | +9.79pp | +9.82pp | -0.035pp | 5.75pp |
| 8 | 40 | +7.87pp | +7.88pp | -0.010pp | 8.44pp |
| 12 | 10 | +11.07pp | +11.10pp | -0.030pp | 2.29pp |
| 12 | 20 | +9.07pp | +9.05pp | +0.025pp | 7.16pp |
| 12 | 40 | +7.31pp | +7.20pp | +0.110pp | 7.19pp |

- cells 12/12 judged
- not-worse share 0.917 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.000pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k40 — **NOT-SEPARABLE**

buffer k=0.40 on every cell (8x the r1325 arm -- the far end, where a real buffer finally has to hurt)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +11.77pp | +10.26pp | +1.510pp | 3.95pp |
| 3 | 20 | +9.52pp | +8.29pp | +1.225pp | 7.27pp |
| 3 | 40 | +7.24pp | +6.38pp | +0.865pp | 12.26pp |
| 5 | 10 | +11.82pp | +11.06pp | +0.755pp | 4.13pp |
| 5 | 20 | +9.55pp | +8.88pp | +0.670pp | 6.24pp |
| 5 | 40 | +7.87pp | +7.50pp | +0.365pp | 11.61pp |
| 8 | 10 | +11.65pp | +11.56pp | +0.090pp | 3.00pp |
| 8 | 20 | +9.44pp | +9.82pp | -0.385pp | 6.05pp |
| 8 | 40 | +8.19pp | +7.88pp | +0.310pp | 9.60pp |
| 12 | 10 | +11.26pp | +11.10pp | +0.155pp | 2.36pp |
| 12 | 20 | +9.73pp | +9.05pp | +0.680pp | 5.65pp |
| 12 | 40 | +8.35pp | +7.20pp | +1.145pp | 8.26pp |

- cells 12/12 judged
- not-worse share 0.917 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.675pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k05_cost20 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **REJECT**）

buffer k=0.05 at 20bp/side -- the interaction neither family tested: does a buffer that is harmless at 10bp recover any of the -1.41pp the 20bp toll costs?

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +7.96pp | +10.26pp | -2.295pp | 5.26pp |
| 3 | 20 | +6.79pp | +8.29pp | -1.500pp | 7.04pp |
| 3 | 40 | +5.47pp | +6.38pp | -0.900pp | 12.41pp |
| 5 | 10 | +9.16pp | +11.06pp | -1.900pp | 2.95pp |
| 5 | 20 | +7.22pp | +8.88pp | -1.660pp | 5.94pp |
| 5 | 40 | +7.10pp | +7.50pp | -0.405pp | 10.25pp |
| 8 | 10 | +9.38pp | +11.56pp | -2.185pp | 3.46pp |
| 8 | 20 | +8.22pp | +9.82pp | -1.600pp | 5.83pp |
| 8 | 40 | +7.21pp | +7.88pp | -0.670pp | 8.25pp |
| 12 | 10 | +8.98pp | +11.10pp | -2.115pp | 2.29pp |
| 12 | 20 | +7.92pp | +9.05pp | -1.130pp | 6.67pp |
| 12 | 40 | +6.93pp | +7.20pp | -0.270pp | 6.93pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -1.550pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced 706c06e0, the baseline 608916d7

## cost0 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **NOT-SEPARABLE**）

0bp/side on the whole grid (no toll at all) -- if the ordering only appears here, the ordering is bought with the toll and the 10bp reading stands

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +13.12pp | +10.26pp | +2.860pp | 4.97pp |
| 3 | 20 | +9.88pp | +8.29pp | +1.590pp | 6.08pp |
| 3 | 40 | +7.67pp | +6.38pp | +1.295pp | 11.24pp |
| 5 | 10 | +14.33pp | +11.06pp | +3.265pp | 3.36pp |
| 5 | 20 | +11.40pp | +8.88pp | +2.515pp | 8.18pp |
| 5 | 40 | +8.53pp | +7.50pp | +1.020pp | 10.01pp |
| 8 | 10 | +14.54pp | +11.56pp | +2.980pp | 4.92pp |
| 8 | 20 | +11.32pp | +9.82pp | +1.505pp | 6.69pp |
| 8 | 40 | +8.66pp | +7.88pp | +0.790pp | 8.73pp |
| 12 | 10 | +13.57pp | +11.10pp | +2.475pp | 2.84pp |
| 12 | 20 | +10.44pp | +9.05pp | +1.390pp | 7.35pp |
| 12 | 40 | +8.01pp | +7.20pp | +0.810pp | 7.11pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +1.547pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced 706c06e0, the baseline 608916d7

