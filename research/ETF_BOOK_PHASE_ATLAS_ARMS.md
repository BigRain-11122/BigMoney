# 相位臂：把 r1325 的 buffer REJECT 与成本档放回它们自己的尺子里重判

面：`results/etf_book_phase_atlas_arms.json`｜脚本：`scripts/etf_book_phase_atlas_arms.py`｜基线面：`results/etf_book_phase_atlas.json`（cutoff 2026-11-24）

同日基线网格：格间 spread 6.75pp，格内 band 中位 6.63pp。

**面板一致性：ONE_WORLD** — all 11 faces priced 706c06e09a2cc87d

## 成本档 5bp → 20bp：多收的 15bp 是不是白收 — **TOLL_DRAINS**

两个成本臂只差这一只旋钮，所以「多收的费有没有被赚回来」只在这里能答。但逐格不是受控对照：引擎按 8%% 波动目标只降不升地调仓，集中持仓（3 名）在本轮波动下降后会被加回目标仓位，这一份加仓比 15bp×换手更大——所以判据是「家族整体失血，且没有一格凭自己有把握地涨上去」。

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

## cost05 — **REJECT**

5bp/side on the whole grid (half the production toll)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +11.73pp | +14.09pp | -2.360pp | 4.62pp |
| 3 | 20 | +9.01pp | +10.96pp | -1.955pp | 7.15pp |
| 3 | 40 | +6.83pp | +7.54pp | -0.710pp | 12.30pp |
| 5 | 10 | +12.45pp | +11.18pp | +1.265pp | 3.48pp |
| 5 | 20 | +9.63pp | +9.35pp | +0.290pp | 6.36pp |
| 5 | 40 | +7.87pp | +7.60pp | +0.270pp | 9.97pp |
| 8 | 10 | +12.83pp | +11.60pp | +1.230pp | 3.31pp |
| 8 | 20 | +10.61pp | +9.53pp | +1.085pp | 6.30pp |
| 8 | 40 | +8.30pp | +7.95pp | +0.355pp | 8.69pp |
| 12 | 10 | +12.35pp | +11.21pp | +1.140pp | 2.91pp |
| 12 | 20 | +9.80pp | +9.16pp | +0.635pp | 7.32pp |
| 12 | 40 | +7.67pp | +7.33pp | +0.335pp | 7.01pp |

- cells 12/12 judged
- not-worse share 0.750 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.345pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## cost20 — **REJECT**

20bp/side on the whole grid (double the production toll)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +7.67pp | +14.09pp | -6.425pp | 4.37pp |
| 3 | 20 | +6.82pp | +10.96pp | -4.145pp | 7.06pp |
| 3 | 40 | +5.61pp | +7.54pp | -1.930pp | 12.24pp |
| 5 | 10 | +8.65pp | +11.18pp | -2.525pp | 3.25pp |
| 5 | 20 | +7.47pp | +9.35pp | -1.875pp | 6.17pp |
| 5 | 40 | +6.79pp | +7.60pp | -0.810pp | 9.86pp |
| 8 | 10 | +9.19pp | +11.60pp | -2.415pp | 3.14pp |
| 8 | 20 | +8.50pp | +9.53pp | -1.025pp | 6.20pp |
| 8 | 40 | +7.25pp | +7.95pp | -0.705pp | 8.54pp |
| 12 | 10 | +8.96pp | +11.21pp | -2.240pp | 2.81pp |
| 12 | 20 | +7.92pp | +9.16pp | -1.250pp | 7.21pp |
| 12 | 40 | +6.66pp | +7.33pp | -0.675pp | 6.91pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -1.902pp (floor -0.05pp)
- resolvable share 0.083 (|delta| > the cell's own band; floor 0.50)

## cost40 — **REJECT**

40bp/side on the whole grid (4x the production toll -- does 'the cadence is quotable' have a toll ceiling, and does the ordering vanish first?)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +2.50pp | +14.09pp | -11.595pp | 5.95pp |
| 3 | 20 | +5.58pp | +10.96pp | -5.385pp | 6.59pp |
| 3 | 40 | +5.17pp | +7.54pp | -2.370pp | 12.13pp |
| 5 | 10 | +3.72pp | +11.18pp | -7.460pp | 3.77pp |
| 5 | 20 | +5.99pp | +9.35pp | -3.360pp | 6.08pp |
| 5 | 40 | +5.83pp | +7.60pp | -1.765pp | 9.36pp |
| 8 | 10 | +4.92pp | +11.60pp | -6.675pp | 3.19pp |
| 8 | 20 | +5.26pp | +9.53pp | -4.265pp | 6.08pp |
| 8 | 40 | +5.84pp | +7.95pp | -2.110pp | 8.21pp |
| 12 | 10 | +4.61pp | +11.21pp | -6.595pp | 2.69pp |
| 12 | 20 | +5.45pp | +9.16pp | -3.715pp | 7.03pp |
| 12 | 40 | +5.68pp | +7.33pp | -1.655pp | 6.76pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -3.990pp (floor -0.05pp)
- resolvable share 0.333 (|delta| > the cell's own band; floor 0.50)

## buffer_k10 — **REJECT**

buffer k=0.10 on every cell (the middle of the family r1325 named as a cost knob; declared in the pool at r1351 before this face existed)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.53pp | +14.09pp | -3.560pp | 4.67pp |
| 3 | 20 | +8.23pp | +10.96pp | -2.730pp | 7.29pp |
| 3 | 40 | +5.93pp | +7.54pp | -1.605pp | 12.32pp |
| 5 | 10 | +12.08pp | +11.18pp | +0.900pp | 5.76pp |
| 5 | 20 | +9.49pp | +9.35pp | +0.145pp | 6.22pp |
| 5 | 40 | +8.22pp | +7.60pp | +0.620pp | 10.25pp |
| 8 | 10 | +12.21pp | +11.60pp | +0.615pp | 2.60pp |
| 8 | 20 | +9.93pp | +9.53pp | +0.400pp | 5.67pp |
| 8 | 40 | +8.09pp | +7.95pp | +0.135pp | 8.51pp |
| 12 | 10 | +11.13pp | +11.21pp | -0.070pp | 2.76pp |
| 12 | 20 | +9.32pp | +9.16pp | +0.160pp | 6.51pp |
| 12 | 40 | +7.37pp | +7.33pp | +0.030pp | 7.20pp |

- cells 12/12 judged
- not-worse share 0.750 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.140pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k20 — **REJECT**

buffer k=0.20 on every cell (the strongest arm -- if even this stays inside every cell's band, the buffer family is unmeasurable on this design, not negative)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +11.71pp | +14.09pp | -2.385pp | 4.87pp |
| 3 | 20 | +8.97pp | +10.96pp | -1.990pp | 6.97pp |
| 3 | 40 | +6.34pp | +7.54pp | -1.190pp | 12.47pp |
| 5 | 10 | +11.72pp | +11.18pp | +0.545pp | 4.03pp |
| 5 | 20 | +9.42pp | +9.35pp | +0.075pp | 6.03pp |
| 5 | 40 | +7.58pp | +7.60pp | -0.025pp | 10.83pp |
| 8 | 10 | +11.59pp | +11.60pp | -0.010pp | 2.68pp |
| 8 | 20 | +9.81pp | +9.53pp | +0.290pp | 6.35pp |
| 8 | 40 | +8.22pp | +7.95pp | +0.275pp | 8.35pp |
| 12 | 10 | +11.04pp | +11.21pp | -0.165pp | 2.99pp |
| 12 | 20 | +9.23pp | +9.16pp | +0.070pp | 5.43pp |
| 12 | 40 | +7.56pp | +7.33pp | +0.225pp | 7.54pp |

- cells 12/12 judged
- not-worse share 0.667 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.030pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

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

## buffer_k40 — **REJECT**

buffer k=0.40 on every cell (8x the r1325 arm -- the far end, where a real buffer finally has to hurt)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +11.81pp | +14.09pp | -2.280pp | 3.92pp |
| 3 | 20 | +9.13pp | +10.96pp | -1.825pp | 6.81pp |
| 3 | 40 | +5.87pp | +7.54pp | -1.665pp | 12.71pp |
| 5 | 10 | +11.86pp | +11.18pp | +0.675pp | 4.46pp |
| 5 | 20 | +9.62pp | +9.35pp | +0.280pp | 6.11pp |
| 5 | 40 | +7.58pp | +7.60pp | -0.025pp | 11.48pp |
| 8 | 10 | +11.73pp | +11.60pp | +0.130pp | 2.98pp |
| 8 | 20 | +9.46pp | +9.53pp | -0.060pp | 6.14pp |
| 8 | 40 | +8.24pp | +7.95pp | +0.295pp | 9.55pp |
| 12 | 10 | +11.12pp | +11.21pp | -0.080pp | 2.74pp |
| 12 | 20 | +9.73pp | +9.16pp | +0.570pp | 5.54pp |
| 12 | 40 | +8.24pp | +7.33pp | +0.910pp | 8.26pp |

- cells 12/12 judged
- not-worse share 0.750 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.053pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k05_cost20 — **REJECT**

buffer k=0.05 at 20bp/side -- the interaction neither family tested: does a buffer that is harmless at 10bp recover any of the -1.41pp the 20bp toll costs?

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +7.96pp | +14.09pp | -6.130pp | 5.26pp |
| 3 | 20 | +6.79pp | +10.96pp | -4.170pp | 7.04pp |
| 3 | 40 | +5.47pp | +7.54pp | -2.060pp | 12.41pp |
| 5 | 10 | +9.16pp | +11.18pp | -2.015pp | 2.95pp |
| 5 | 20 | +7.22pp | +9.35pp | -2.120pp | 5.94pp |
| 5 | 40 | +7.10pp | +7.60pp | -0.500pp | 10.25pp |
| 8 | 10 | +9.38pp | +11.60pp | -2.225pp | 3.46pp |
| 8 | 20 | +8.22pp | +9.53pp | -1.305pp | 5.83pp |
| 8 | 40 | +7.21pp | +7.95pp | -0.745pp | 8.25pp |
| 12 | 10 | +8.98pp | +11.21pp | -2.220pp | 2.29pp |
| 12 | 20 | +7.92pp | +9.16pp | -1.245pp | 6.67pp |
| 12 | 40 | +6.93pp | +7.33pp | -0.405pp | 6.93pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -2.038pp (floor -0.05pp)
- resolvable share 0.083 (|delta| > the cell's own band; floor 0.50)

## cost0 — **NOT-SEPARABLE**

0bp/side on the whole grid (no toll at all) -- if the ordering only appears here, the ordering is bought with the toll and the 10bp reading stands

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +13.12pp | +14.09pp | -0.975pp | 4.97pp |
| 3 | 20 | +9.88pp | +10.96pp | -1.080pp | 6.08pp |
| 3 | 40 | +7.67pp | +7.54pp | +0.135pp | 11.24pp |
| 5 | 10 | +14.33pp | +11.18pp | +3.150pp | 3.36pp |
| 5 | 20 | +11.40pp | +9.35pp | +2.055pp | 8.18pp |
| 5 | 40 | +8.53pp | +7.60pp | +0.925pp | 10.01pp |
| 8 | 10 | +14.54pp | +11.60pp | +2.940pp | 4.92pp |
| 8 | 20 | +11.32pp | +9.53pp | +1.800pp | 6.69pp |
| 8 | 40 | +8.66pp | +7.95pp | +0.715pp | 8.73pp |
| 12 | 10 | +13.57pp | +11.21pp | +2.370pp | 2.84pp |
| 12 | 20 | +10.44pp | +9.16pp | +1.275pp | 7.35pp |
| 12 | 40 | +8.01pp | +7.33pp | +0.675pp | 7.11pp |

- cells 12/12 judged
- not-worse share 0.833 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +1.100pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

