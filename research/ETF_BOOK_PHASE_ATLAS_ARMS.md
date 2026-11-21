# 相位臂：把 r1325 的 buffer REJECT 与成本档放回它们自己的尺子里重判

面：`results/etf_book_phase_atlas_arms.json`｜脚本：`scripts/etf_book_phase_atlas_arms.py`｜基线面：`results/etf_book_phase_atlas.json`（cutoff 2026-11-20）

同日基线网格：格间 spread 5.24pp，格内 band 中位 6.80pp。

**面板一致性：MIXED_WORLDS** — 11 faces priced 2 different panels (2e875bf4, 7d93f5cd): per-cell deltas across worlds are world differences, not rule effects

（判词不发布：本表的每个 Δ 都是「同一格、臂减基线」，跨面板相减得到的是世界差，不是规则效应。标签原文保留在 `verdict_if_coherent`；把臂重建到同一面板后自动恢复。）

## 成本档 5bp → 20bp：多收的 15bp 是不是白收 — **TOLL_DRAINS**

两个成本臂只差这一只旋钮，所以「多收的费有没有被赚回来」只在这里能答。但逐格不是受控对照：引擎按 8%% 波动目标只降不升地调仓，集中持仓（3 名）在本轮波动下降后会被加回目标仓位，这一份加仓比 15bp×换手更大——所以判据是「家族整体失血，且没有一格凭自己有把握地涨上去」。

| n_hold | rebal | 5bp | 20bp | Δ | 本格 band | 读数 |
|---|---|---|---|---|---|---|
| 3 | 10 | +11.84pp | +11.84pp | +0.000pp | 4.68pp | 跌 |
| 3 | 20 | +9.06pp | +9.15pp | +0.090pp | 7.50pp | 涨在 band 之内 |
| 3 | 40 | +6.97pp | +5.75pp | -1.220pp | 12.13pp | 跌 |
| 5 | 10 | +12.54pp | +8.77pp | -3.780pp | 3.37pp | 跌 |
| 5 | 20 | +9.80pp | +7.63pp | -2.165pp | 6.55pp | 跌 |
| 5 | 40 | +8.01pp | +7.34pp | -0.665pp | 10.32pp | 跌 |
| 8 | 10 | +13.03pp | +9.04pp | -3.985pp | 3.18pp | 跌 |
| 8 | 20 | +10.70pp | +8.61pp | -2.095pp | 6.41pp | 跌 |
| 8 | 40 | +8.29pp | +7.24pp | -1.060pp | 8.94pp | 跌 |
| 12 | 10 | +12.37pp | +9.62pp | -2.755pp | 2.83pp | 跌 |
| 12 | 20 | +9.82pp | +8.05pp | -1.765pp | 7.37pp | 跌 |
| 12 | 40 | +7.79pp | +6.76pp | -1.020pp | 7.16pp | 跌 |

- cells 12/12 judged against the baseline grid
- family total -20.42pp, median -1.492pp on the extra 15bp/side
- rising cells 1/12 (2 allowed), 0 of them beyond their own band
- the cells that do not fall stay inside their own band, and the family drains: no cell's wobble reads as a gain

## buffer_k05 — **REJECT**

buffer k=0.05 on every cell (the r1325 arm, re-priced per phase)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.62pp | +10.46pp | +0.155pp | 5.56pp |
| 3 | 20 | +8.34pp | +8.32pp | +0.015pp | 7.47pp |
| 3 | 40 | +6.33pp | +6.57pp | -0.235pp | 12.62pp |
| 5 | 10 | +11.78pp | +11.28pp | +0.505pp | 2.98pp |
| 5 | 20 | +8.79pp | +9.07pp | -0.290pp | 6.26pp |
| 5 | 40 | +7.91pp | +7.66pp | +0.255pp | 10.68pp |
| 8 | 10 | +11.87pp | +11.80pp | +0.060pp | 3.47pp |
| 8 | 20 | +9.73pp | +10.01pp | -0.280pp | 5.90pp |
| 8 | 40 | +7.97pp | +7.94pp | +0.030pp | 8.62pp |
| 12 | 10 | +11.16pp | +11.25pp | -0.085pp | 2.25pp |
| 12 | 20 | +9.21pp | +9.19pp | +0.015pp | 6.70pp |
| 12 | 40 | +7.72pp | +7.45pp | +0.280pp | 7.11pp |

- cells 12/12 judged
- not-worse share 0.750 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.022pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## cost05 — **NOT-SEPARABLE**

5bp/side on the whole grid (half the production toll)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +11.84pp | +10.46pp | +1.380pp | 4.68pp |
| 3 | 20 | +9.06pp | +8.32pp | +0.735pp | 7.50pp |
| 3 | 40 | +6.97pp | +6.57pp | +0.410pp | 12.13pp |
| 5 | 10 | +12.54pp | +11.28pp | +1.270pp | 3.37pp |
| 5 | 20 | +9.80pp | +9.07pp | +0.725pp | 6.55pp |
| 5 | 40 | +8.01pp | +7.66pp | +0.355pp | 10.32pp |
| 8 | 10 | +13.03pp | +11.80pp | +1.220pp | 3.18pp |
| 8 | 20 | +10.70pp | +10.01pp | +0.690pp | 6.41pp |
| 8 | 40 | +8.29pp | +7.94pp | +0.355pp | 8.94pp |
| 12 | 10 | +12.37pp | +11.25pp | +1.120pp | 2.83pp |
| 12 | 20 | +9.82pp | +9.19pp | +0.630pp | 7.37pp |
| 12 | 40 | +7.79pp | +7.45pp | +0.340pp | 7.16pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.708pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## cost20 — **REJECT**

20bp/side on the whole grid (double the production toll)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +11.84pp | +10.46pp | +1.380pp | 4.86pp |
| 3 | 20 | +9.15pp | +8.32pp | +0.825pp | 9.04pp |
| 3 | 40 | +5.75pp | +6.57pp | -0.810pp | 10.85pp |
| 5 | 10 | +8.77pp | +11.28pp | -2.510pp | 3.14pp |
| 5 | 20 | +7.63pp | +9.07pp | -1.440pp | 8.45pp |
| 5 | 40 | +7.34pp | +7.66pp | -0.310pp | 10.59pp |
| 8 | 10 | +9.04pp | +11.80pp | -2.765pp | 3.02pp |
| 8 | 20 | +8.61pp | +10.01pp | -1.405pp | 6.54pp |
| 8 | 40 | +7.24pp | +7.94pp | -0.705pp | 8.58pp |
| 12 | 10 | +9.62pp | +11.25pp | -1.635pp | 3.77pp |
| 12 | 20 | +8.05pp | +9.19pp | -1.135pp | 7.24pp |
| 12 | 40 | +6.76pp | +7.45pp | -0.680pp | 7.21pp |

- cells 12/12 judged
- not-worse share 0.167 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -0.973pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## cost40 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **REJECT**）

40bp/side on the whole grid (4x the production toll -- does 'the cadence is quotable' have a toll ceiling, and does the ordering vanish first?)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +4.37pp | +10.46pp | -6.095pp | 6.96pp |
| 3 | 20 | +6.45pp | +8.32pp | -1.875pp | 8.72pp |
| 3 | 40 | +4.79pp | +6.57pp | -1.775pp | 11.74pp |
| 5 | 10 | +4.68pp | +11.28pp | -6.595pp | 6.05pp |
| 5 | 20 | +6.47pp | +9.07pp | -2.600pp | 8.50pp |
| 5 | 40 | +6.41pp | +7.66pp | -1.245pp | 9.86pp |
| 8 | 10 | +5.26pp | +11.80pp | -6.545pp | 3.07pp |
| 8 | 20 | +6.36pp | +10.01pp | -3.650pp | 5.45pp |
| 8 | 40 | +6.05pp | +7.94pp | -1.890pp | 8.53pp |
| 12 | 10 | +5.53pp | +11.25pp | -5.720pp | 3.63pp |
| 12 | 20 | +5.71pp | +9.19pp | -3.480pp | 7.19pp |
| 12 | 40 | +6.07pp | +7.45pp | -1.380pp | 6.90pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -3.040pp (floor -0.05pp)
- resolvable share 0.250 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced 7d93f5cd, the baseline 2e875bf4

## buffer_k10 — **NOT-SEPARABLE**

buffer k=0.10 on every cell (the middle of the family r1325 named as a cost knob; declared in the pool at r1351 before this face existed)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.73pp | +10.46pp | +0.270pp | 4.77pp |
| 3 | 20 | +8.24pp | +8.32pp | -0.085pp | 7.64pp |
| 3 | 40 | +6.04pp | +6.57pp | -0.530pp | 12.47pp |
| 5 | 10 | +12.10pp | +11.28pp | +0.820pp | 3.57pp |
| 5 | 20 | +8.99pp | +9.07pp | -0.080pp | 6.20pp |
| 5 | 40 | +7.58pp | +7.66pp | -0.075pp | 10.54pp |
| 8 | 10 | +12.21pp | +11.80pp | +0.400pp | 3.07pp |
| 8 | 20 | +10.02pp | +10.01pp | +0.005pp | 5.81pp |
| 8 | 40 | +8.07pp | +7.94pp | +0.135pp | 8.68pp |
| 12 | 10 | +11.14pp | +11.25pp | -0.105pp | 2.72pp |
| 12 | 20 | +9.35pp | +9.19pp | +0.160pp | 6.62pp |
| 12 | 40 | +7.81pp | +7.45pp | +0.365pp | 7.43pp |

- cells 12/12 judged
- not-worse share 0.917 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.070pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k20 — **NOT-SEPARABLE**

buffer k=0.20 on every cell (the strongest arm -- if even this stays inside every cell's band, the buffer family is unmeasurable on this design, not negative)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +11.84pp | +10.46pp | +1.380pp | 4.81pp |
| 3 | 20 | +8.91pp | +8.32pp | +0.590pp | 7.17pp |
| 3 | 40 | +6.40pp | +6.57pp | -0.165pp | 12.63pp |
| 5 | 10 | +11.76pp | +11.28pp | +0.480pp | 4.07pp |
| 5 | 20 | +9.50pp | +9.07pp | +0.425pp | 6.27pp |
| 5 | 40 | +7.67pp | +7.66pp | +0.020pp | 11.19pp |
| 8 | 10 | +11.61pp | +11.80pp | -0.195pp | 2.72pp |
| 8 | 20 | +9.97pp | +10.01pp | -0.035pp | 6.48pp |
| 8 | 40 | +8.31pp | +7.94pp | +0.370pp | 8.61pp |
| 12 | 10 | +11.13pp | +11.25pp | -0.120pp | 2.92pp |
| 12 | 20 | +9.33pp | +9.19pp | +0.140pp | 5.54pp |
| 12 | 40 | +7.71pp | +7.45pp | +0.265pp | 7.81pp |

- cells 12/12 judged
- not-worse share 0.833 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.203pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k02 — **NOT-SEPARABLE**

buffer k=0.02 on every cell (the near-zero end -- a knob that reads the same at 0.02 and at 0.20 is flat, not merely small)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.47pp | +10.46pp | +0.015pp | 4.88pp |
| 3 | 20 | +8.18pp | +8.32pp | -0.145pp | 7.48pp |
| 3 | 40 | +6.66pp | +6.57pp | +0.095pp | 12.12pp |
| 5 | 10 | +11.45pp | +11.28pp | +0.170pp | 3.22pp |
| 5 | 20 | +9.04pp | +9.07pp | -0.030pp | 6.38pp |
| 5 | 40 | +7.67pp | +7.66pp | +0.010pp | 10.27pp |
| 8 | 10 | +11.78pp | +11.80pp | -0.030pp | 3.24pp |
| 8 | 20 | +9.98pp | +10.01pp | -0.030pp | 5.90pp |
| 8 | 40 | +7.93pp | +7.94pp | -0.010pp | 8.60pp |
| 12 | 10 | +11.27pp | +11.25pp | +0.015pp | 2.29pp |
| 12 | 20 | +9.24pp | +9.19pp | +0.055pp | 7.35pp |
| 12 | 40 | +7.54pp | +7.45pp | +0.100pp | 7.37pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.013pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k40 — **NOT-SEPARABLE**

buffer k=0.40 on every cell (8x the r1325 arm -- the far end, where a real buffer finally has to hurt)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +11.93pp | +10.46pp | +1.470pp | 3.98pp |
| 3 | 20 | +9.13pp | +8.32pp | +0.805pp | 6.86pp |
| 3 | 40 | +5.92pp | +6.57pp | -0.640pp | 12.88pp |
| 5 | 10 | +11.94pp | +11.28pp | +0.665pp | 4.55pp |
| 5 | 20 | +9.52pp | +9.07pp | +0.440pp | 6.41pp |
| 5 | 40 | +7.71pp | +7.66pp | +0.060pp | 11.72pp |
| 8 | 10 | +11.83pp | +11.80pp | +0.025pp | 3.02pp |
| 8 | 20 | +9.57pp | +10.01pp | -0.435pp | 6.24pp |
| 8 | 40 | +8.31pp | +7.94pp | +0.370pp | 9.61pp |
| 12 | 10 | +11.21pp | +11.25pp | -0.045pp | 2.73pp |
| 12 | 20 | +9.85pp | +9.19pp | +0.660pp | 5.57pp |
| 12 | 40 | +8.34pp | +7.45pp | +0.890pp | 8.47pp |

- cells 12/12 judged
- not-worse share 0.833 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.405pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k05_cost20 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **REJECT**）

buffer k=0.05 at 20bp/side -- the interaction neither family tested: does a buffer that is harmless at 10bp recover any of the -1.41pp the 20bp toll costs?

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +8.21pp | +10.46pp | -2.250pp | 5.24pp |
| 3 | 20 | +7.11pp | +8.32pp | -1.215pp | 7.34pp |
| 3 | 40 | +5.67pp | +6.57pp | -0.895pp | 12.73pp |
| 5 | 10 | +9.45pp | +11.28pp | -1.830pp | 2.96pp |
| 5 | 20 | +7.53pp | +9.07pp | -1.550pp | 6.26pp |
| 5 | 40 | +7.36pp | +7.66pp | -0.295pp | 10.47pp |
| 8 | 10 | +9.71pp | +11.80pp | -2.100pp | 3.40pp |
| 8 | 20 | +8.48pp | +10.01pp | -1.530pp | 5.90pp |
| 8 | 40 | +7.49pp | +7.94pp | -0.455pp | 8.39pp |
| 12 | 10 | +9.26pp | +11.25pp | -1.995pp | 2.21pp |
| 12 | 20 | +8.18pp | +9.19pp | -1.015pp | 6.76pp |
| 12 | 40 | +7.22pp | +7.45pp | -0.220pp | 7.03pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -1.373pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced 7d93f5cd, the baseline 2e875bf4

## cost0 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **NOT-SEPARABLE**）

0bp/side on the whole grid (no toll at all) -- if the ordering only appears here, the ordering is bought with the toll and the 10bp reading stands

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +13.37pp | +10.46pp | +2.905pp | 4.72pp |
| 3 | 20 | +9.96pp | +8.32pp | +1.640pp | 7.31pp |
| 3 | 40 | +7.49pp | +6.57pp | +0.925pp | 12.39pp |
| 5 | 10 | +14.01pp | +11.28pp | +2.730pp | 3.54pp |
| 5 | 20 | +10.64pp | +9.07pp | +1.570pp | 6.57pp |
| 5 | 40 | +8.60pp | +7.66pp | +0.940pp | 10.10pp |
| 8 | 10 | +14.43pp | +11.80pp | +2.620pp | 3.34pp |
| 8 | 20 | +11.61pp | +10.01pp | +1.595pp | 6.41pp |
| 8 | 40 | +8.88pp | +7.94pp | +0.945pp | 8.80pp |
| 12 | 10 | +13.72pp | +11.25pp | +2.470pp | 2.89pp |
| 12 | 20 | +10.70pp | +9.19pp | +1.510pp | 7.45pp |
| 12 | 40 | +8.35pp | +7.45pp | +0.900pp | 7.12pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +1.583pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced 7d93f5cd, the baseline 2e875bf4

