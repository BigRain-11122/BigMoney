# 相位臂：把 r1325 的 buffer REJECT 与成本档放回它们自己的尺子里重判

面：`results/etf_book_phase_atlas_arms.json`｜脚本：`scripts/etf_book_phase_atlas_arms.py`｜基线面：`results/etf_book_phase_atlas.json`（cutoff 2026-11-24）

同日基线网格：格间 spread 6.75pp，格内 band 中位 6.63pp。

**面板一致性：MIXED_WORLDS** — 11 faces priced 2 different panels (2e875bf4, 706c06e0): per-cell deltas across worlds are world differences, not rule effects

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
| 3 | 10 | +10.51pp | +14.09pp | -3.580pp | 5.48pp |
| 3 | 20 | +8.17pp | +10.96pp | -2.790pp | 7.13pp |
| 3 | 40 | +6.22pp | +7.54pp | -1.315pp | 12.47pp |
| 5 | 10 | +11.64pp | +11.18pp | +0.465pp | 3.07pp |
| 5 | 20 | +8.62pp | +9.35pp | -0.725pp | 5.98pp |
| 5 | 40 | +7.84pp | +7.60pp | +0.245pp | 10.34pp |
| 8 | 10 | +11.70pp | +11.60pp | +0.095pp | 3.55pp |
| 8 | 20 | +9.57pp | +9.53pp | +0.045pp | 5.88pp |
| 8 | 40 | +7.91pp | +7.95pp | -0.045pp | 8.36pp |
| 12 | 10 | +11.12pp | +11.21pp | -0.090pp | 2.35pp |
| 12 | 20 | +9.12pp | +9.16pp | -0.040pp | 6.74pp |
| 12 | 40 | +7.58pp | +7.33pp | +0.250pp | 6.98pp |

- cells 12/12 judged
- not-worse share 0.667 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -0.042pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## cost05 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **REJECT**）

5bp/side on the whole grid (half the production toll)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +11.84pp | +14.09pp | -2.250pp | 4.68pp |
| 3 | 20 | +9.06pp | +10.96pp | -1.900pp | 7.50pp |
| 3 | 40 | +6.97pp | +7.54pp | -0.560pp | 12.13pp |
| 5 | 10 | +12.54pp | +11.18pp | +1.365pp | 3.37pp |
| 5 | 20 | +9.80pp | +9.35pp | +0.455pp | 6.55pp |
| 5 | 40 | +8.01pp | +7.60pp | +0.410pp | 10.32pp |
| 8 | 10 | +13.03pp | +11.60pp | +1.425pp | 3.18pp |
| 8 | 20 | +10.70pp | +9.53pp | +1.175pp | 6.41pp |
| 8 | 40 | +8.29pp | +7.95pp | +0.345pp | 8.94pp |
| 12 | 10 | +12.37pp | +11.21pp | +1.165pp | 2.83pp |
| 12 | 20 | +9.82pp | +9.16pp | +0.655pp | 7.37pp |
| 12 | 40 | +7.79pp | +7.33pp | +0.450pp | 7.16pp |

- cells 12/12 judged
- not-worse share 0.750 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.453pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced 2e875bf4, the baseline 706c06e0

## cost20 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **REJECT**）

20bp/side on the whole grid (double the production toll)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +11.84pp | +14.09pp | -2.250pp | 4.86pp |
| 3 | 20 | +9.15pp | +10.96pp | -1.810pp | 9.04pp |
| 3 | 40 | +5.75pp | +7.54pp | -1.780pp | 10.85pp |
| 5 | 10 | +8.77pp | +11.18pp | -2.415pp | 3.14pp |
| 5 | 20 | +7.63pp | +9.35pp | -1.710pp | 8.45pp |
| 5 | 40 | +7.34pp | +7.60pp | -0.255pp | 10.59pp |
| 8 | 10 | +9.04pp | +11.60pp | -2.560pp | 3.02pp |
| 8 | 20 | +8.61pp | +9.53pp | -0.920pp | 6.54pp |
| 8 | 40 | +7.24pp | +7.95pp | -0.715pp | 8.58pp |
| 12 | 10 | +9.62pp | +11.21pp | -1.590pp | 3.77pp |
| 12 | 20 | +8.05pp | +9.16pp | -1.110pp | 7.24pp |
| 12 | 40 | +6.76pp | +7.33pp | -0.570pp | 7.21pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -1.650pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced 2e875bf4, the baseline 706c06e0

## cost40 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **REJECT**）

40bp/side on the whole grid (4x the production toll -- does 'the cadence is quotable' have a toll ceiling, and does the ordering vanish first?)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +2.56pp | +14.09pp | -11.535pp | 4.06pp |
| 3 | 20 | +3.98pp | +10.96pp | -6.975pp | 7.31pp |
| 3 | 40 | +4.14pp | +7.54pp | -3.395pp | 12.01pp |
| 5 | 10 | +3.85pp | +11.18pp | -7.325pp | 2.83pp |
| 5 | 20 | +4.80pp | +9.35pp | -4.540pp | 6.29pp |
| 5 | 40 | +5.55pp | +7.60pp | -2.050pp | 10.03pp |
| 8 | 10 | +4.71pp | +11.60pp | -6.885pp | 2.77pp |
| 8 | 20 | +5.84pp | +9.53pp | -3.680pp | 6.19pp |
| 8 | 40 | +5.83pp | +7.95pp | -2.125pp | 8.61pp |
| 12 | 10 | +4.67pp | +11.21pp | -6.540pp | 2.63pp |
| 12 | 20 | +5.47pp | +9.16pp | -3.690pp | 7.08pp |
| 12 | 40 | +5.42pp | +7.33pp | -1.915pp | 6.89pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -4.115pp (floor -0.05pp)
- resolvable share 0.333 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced 2e875bf4, the baseline 706c06e0

## buffer_k10 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **REJECT**）

buffer k=0.10 on every cell (the middle of the family r1325 named as a cost knob; declared in the pool at r1351 before this face existed)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.73pp | +14.09pp | -3.360pp | 4.77pp |
| 3 | 20 | +8.24pp | +10.96pp | -2.720pp | 7.64pp |
| 3 | 40 | +6.04pp | +7.54pp | -1.500pp | 12.47pp |
| 5 | 10 | +12.10pp | +11.18pp | +0.915pp | 3.57pp |
| 5 | 20 | +8.99pp | +9.35pp | -0.350pp | 6.20pp |
| 5 | 40 | +7.58pp | +7.60pp | -0.020pp | 10.54pp |
| 8 | 10 | +12.21pp | +11.60pp | +0.605pp | 3.07pp |
| 8 | 20 | +10.02pp | +9.53pp | +0.490pp | 5.81pp |
| 8 | 40 | +8.07pp | +7.95pp | +0.125pp | 8.68pp |
| 12 | 10 | +11.14pp | +11.21pp | -0.060pp | 2.72pp |
| 12 | 20 | +9.35pp | +9.16pp | +0.185pp | 6.62pp |
| 12 | 40 | +7.81pp | +7.33pp | +0.475pp | 7.43pp |

- cells 12/12 judged
- not-worse share 0.667 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.052pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced 2e875bf4, the baseline 706c06e0

## buffer_k20 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **REJECT**）

buffer k=0.20 on every cell (the strongest arm -- if even this stays inside every cell's band, the buffer family is unmeasurable on this design, not negative)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +11.84pp | +14.09pp | -2.250pp | 4.81pp |
| 3 | 20 | +8.91pp | +10.96pp | -2.045pp | 7.17pp |
| 3 | 40 | +6.40pp | +7.54pp | -1.135pp | 12.63pp |
| 5 | 10 | +11.76pp | +11.18pp | +0.575pp | 4.07pp |
| 5 | 20 | +9.50pp | +9.35pp | +0.155pp | 6.27pp |
| 5 | 40 | +7.67pp | +7.60pp | +0.075pp | 11.19pp |
| 8 | 10 | +11.61pp | +11.60pp | +0.010pp | 2.72pp |
| 8 | 20 | +9.97pp | +9.53pp | +0.450pp | 6.48pp |
| 8 | 40 | +8.31pp | +7.95pp | +0.360pp | 8.61pp |
| 12 | 10 | +11.13pp | +11.21pp | -0.075pp | 2.92pp |
| 12 | 20 | +9.33pp | +9.16pp | +0.165pp | 5.54pp |
| 12 | 40 | +7.71pp | +7.33pp | +0.375pp | 7.81pp |

- cells 12/12 judged
- not-worse share 0.750 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.115pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced 2e875bf4, the baseline 706c06e0

## buffer_k02 — **REJECT**

buffer k=0.02 on every cell (the near-zero end -- a knob that reads the same at 0.02 and at 0.20 is flat, not merely small)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.37pp | +14.09pp | -3.720pp | 4.79pp |
| 3 | 20 | +8.12pp | +10.96pp | -2.835pp | 7.14pp |
| 3 | 40 | +6.54pp | +7.54pp | -0.995pp | 12.29pp |
| 5 | 10 | +11.34pp | +11.18pp | +0.160pp | 3.33pp |
| 5 | 20 | +8.88pp | +9.35pp | -0.465pp | 6.19pp |
| 5 | 40 | +7.51pp | +7.60pp | -0.085pp | 9.93pp |
| 8 | 10 | +11.57pp | +11.60pp | -0.025pp | 3.36pp |
| 8 | 20 | +9.86pp | +9.53pp | +0.335pp | 5.89pp |
| 8 | 40 | +7.94pp | +7.95pp | -0.010pp | 8.35pp |
| 12 | 10 | +11.15pp | +11.21pp | -0.055pp | 2.38pp |
| 12 | 20 | +9.16pp | +9.16pp | +0.000pp | 7.28pp |
| 12 | 40 | +7.41pp | +7.33pp | +0.075pp | 7.23pp |

- cells 12/12 judged
- not-worse share 0.667 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -0.040pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k40 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **REJECT**）

buffer k=0.40 on every cell (8x the r1325 arm -- the far end, where a real buffer finally has to hurt)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +11.93pp | +14.09pp | -2.160pp | 3.98pp |
| 3 | 20 | +9.13pp | +10.96pp | -1.830pp | 6.86pp |
| 3 | 40 | +5.92pp | +7.54pp | -1.610pp | 12.88pp |
| 5 | 10 | +11.94pp | +11.18pp | +0.760pp | 4.55pp |
| 5 | 20 | +9.52pp | +9.35pp | +0.170pp | 6.41pp |
| 5 | 40 | +7.71pp | +7.60pp | +0.115pp | 11.72pp |
| 8 | 10 | +11.83pp | +11.60pp | +0.230pp | 3.02pp |
| 8 | 20 | +9.57pp | +9.53pp | +0.050pp | 6.24pp |
| 8 | 40 | +8.31pp | +7.95pp | +0.360pp | 9.61pp |
| 12 | 10 | +11.21pp | +11.21pp | +0.000pp | 2.73pp |
| 12 | 20 | +9.85pp | +9.16pp | +0.685pp | 5.57pp |
| 12 | 40 | +8.34pp | +7.33pp | +1.000pp | 8.47pp |

- cells 12/12 judged
- not-worse share 0.750 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.143pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced 2e875bf4, the baseline 706c06e0

## buffer_k05_cost20 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **REJECT**）

buffer k=0.05 at 20bp/side -- the interaction neither family tested: does a buffer that is harmless at 10bp recover any of the -1.41pp the 20bp toll costs?

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +8.06pp | +14.09pp | -6.030pp | 5.33pp |
| 3 | 20 | +6.96pp | +10.96pp | -3.995pp | 7.45pp |
| 3 | 40 | +5.47pp | +7.54pp | -2.060pp | 12.57pp |
| 5 | 10 | +9.34pp | +11.18pp | -1.840pp | 2.85pp |
| 5 | 20 | +7.38pp | +9.35pp | -1.965pp | 6.23pp |
| 5 | 40 | +7.17pp | +7.60pp | -0.435pp | 9.29pp |
| 8 | 10 | +9.55pp | +11.60pp | -2.045pp | 3.38pp |
| 8 | 20 | +8.14pp | +9.53pp | -1.380pp | 6.09pp |
| 8 | 40 | +6.83pp | +7.95pp | -1.115pp | 8.52pp |
| 12 | 10 | +9.04pp | +11.21pp | -2.165pp | 2.17pp |
| 12 | 20 | +7.97pp | +9.16pp | -1.190pp | 6.63pp |
| 12 | 40 | +6.92pp | +7.33pp | -0.410pp | 7.44pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -1.903pp (floor -0.05pp)
- resolvable share 0.083 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced 2e875bf4, the baseline 706c06e0

## cost0 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **REJECT**）

0bp/side on the whole grid (no toll at all) -- if the ordering only appears here, the ordering is bought with the toll and the 10bp reading stands

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +13.22pp | +14.09pp | -0.865pp | 4.81pp |
| 3 | 20 | +9.80pp | +10.96pp | -1.155pp | 7.53pp |
| 3 | 40 | +7.37pp | +7.54pp | -0.165pp | 12.16pp |
| 5 | 10 | +13.84pp | +11.18pp | +2.655pp | 3.46pp |
| 5 | 20 | +10.54pp | +9.35pp | +1.190pp | 6.62pp |
| 5 | 40 | +8.37pp | +7.60pp | +0.770pp | 10.36pp |
| 8 | 10 | +14.27pp | +11.60pp | +2.665pp | 3.25pp |
| 8 | 20 | +11.40pp | +9.53pp | +1.875pp | 6.44pp |
| 8 | 40 | +8.66pp | +7.95pp | +0.710pp | 8.99pp |
| 12 | 10 | +13.49pp | +11.21pp | +2.290pp | 2.87pp |
| 12 | 20 | +10.46pp | +9.16pp | +1.290pp | 7.42pp |
| 12 | 40 | +8.12pp | +7.33pp | +0.790pp | 7.20pp |

- cells 12/12 judged
- not-worse share 0.750 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.990pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced 2e875bf4, the baseline 706c06e0

