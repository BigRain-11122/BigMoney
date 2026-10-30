# 相位臂：把 r1325 的 buffer REJECT 与成本档放回它们自己的尺子里重判

面：`results/etf_book_phase_atlas_arms.json`｜脚本：`scripts/etf_book_phase_atlas_arms.py`｜基线面：`results/etf_book_phase_atlas.json`（cutoff 2026-10-29）

同日基线网格：格间 spread 5.22pp，格内 band 中位 6.68pp。

## buffer_k05 — **REJECT**

buffer k=0.05 on every cell (the r1325 arm, re-priced per phase)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +11.07pp | +10.93pp | +0.150pp | 5.21pp |
| 3 | 20 | +8.59pp | +8.71pp | -0.125pp | 6.85pp |
| 3 | 40 | +6.47pp | +6.78pp | -0.310pp | 12.57pp |
| 5 | 10 | +11.90pp | +11.51pp | +0.395pp | 3.15pp |
| 5 | 20 | +9.13pp | +9.13pp | +0.000pp | 6.09pp |
| 5 | 40 | +8.10pp | +8.32pp | -0.225pp | 9.86pp |
| 8 | 10 | +12.07pp | +12.00pp | +0.070pp | 3.62pp |
| 8 | 20 | +9.78pp | +10.13pp | -0.355pp | 6.02pp |
| 8 | 40 | +8.06pp | +8.30pp | -0.245pp | 8.16pp |
| 12 | 10 | +11.59pp | +11.63pp | -0.050pp | 2.19pp |
| 12 | 20 | +9.63pp | +9.64pp | -0.010pp | 7.28pp |
| 12 | 40 | +7.71pp | +7.55pp | +0.165pp | 7.13pp |

- cells 12/12 judged
- not-worse share 0.667 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -0.030pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## cost05 — **NOT-SEPARABLE**

5bp/side on the whole grid (half the production toll)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +12.29pp | +10.93pp | +1.370pp | 4.30pp |
| 3 | 20 | +9.47pp | +8.71pp | +0.755pp | 7.03pp |
| 3 | 40 | +7.16pp | +6.78pp | +0.380pp | 12.41pp |
| 5 | 10 | +12.81pp | +11.51pp | +1.310pp | 3.57pp |
| 5 | 20 | +9.85pp | +9.13pp | +0.720pp | 6.28pp |
| 5 | 40 | +8.68pp | +8.32pp | +0.360pp | 9.57pp |
| 8 | 10 | +13.22pp | +12.00pp | +1.220pp | 3.36pp |
| 8 | 20 | +10.84pp | +10.13pp | +0.705pp | 6.52pp |
| 8 | 40 | +8.67pp | +8.30pp | +0.365pp | 8.43pp |
| 12 | 10 | +12.77pp | +11.63pp | +1.130pp | 2.80pp |
| 12 | 20 | +10.28pp | +9.64pp | +0.635pp | 7.91pp |
| 12 | 40 | +7.89pp | +7.55pp | +0.340pp | 6.91pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.712pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## cost20 — **REJECT**

20bp/side on the whole grid (double the production toll)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +8.23pp | +10.93pp | -2.690pp | 4.05pp |
| 3 | 20 | +7.22pp | +8.71pp | -1.490pp | 6.77pp |
| 3 | 40 | +6.04pp | +6.78pp | -0.740pp | 12.41pp |
| 5 | 10 | +8.94pp | +11.51pp | -2.565pp | 3.37pp |
| 5 | 20 | +7.71pp | +9.13pp | -1.425pp | 6.18pp |
| 5 | 40 | +7.59pp | +8.32pp | -0.725pp | 9.50pp |
| 8 | 10 | +9.59pp | +12.00pp | -2.410pp | 3.21pp |
| 8 | 20 | +8.73pp | +10.13pp | -1.395pp | 6.43pp |
| 8 | 40 | +7.59pp | +8.30pp | -0.715pp | 8.40pp |
| 12 | 10 | +9.41pp | +11.63pp | -2.220pp | 2.73pp |
| 12 | 20 | +8.37pp | +9.64pp | -1.280pp | 7.80pp |
| 12 | 40 | +6.87pp | +7.55pp | -0.685pp | 6.83pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -1.410pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## cost40 — **REJECT**

40bp/side on the whole grid (4x the production toll -- does 'the cadence is quotable' have a toll ceiling, and does the ordering vanish first?)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +3.16pp | +10.93pp | -7.765pp | 3.75pp |
| 3 | 20 | +4.29pp | +8.71pp | -4.425pp | 6.59pp |
| 3 | 40 | +4.57pp | +6.78pp | -2.215pp | 12.39pp |
| 5 | 10 | +4.01pp | +11.51pp | -7.490pp | 3.12pp |
| 5 | 20 | +4.90pp | +9.13pp | -4.230pp | 6.07pp |
| 5 | 40 | +6.16pp | +8.32pp | -2.160pp | 9.36pp |
| 8 | 10 | +4.92pp | +12.00pp | -7.075pp | 3.03pp |
| 8 | 20 | +5.99pp | +10.13pp | -4.140pp | 6.34pp |
| 8 | 40 | +6.17pp | +8.30pp | -2.140pp | 8.36pp |
| 12 | 10 | +5.09pp | +11.63pp | -6.545pp | 2.63pp |
| 12 | 20 | +5.85pp | +9.64pp | -3.795pp | 7.66pp |
| 12 | 40 | +5.50pp | +7.55pp | -2.045pp | 6.75pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -4.185pp (floor -0.05pp)
- resolvable share 0.333 (|delta| > the cell's own band; floor 0.50)

## buffer_k10 — **NOT-SEPARABLE**

buffer k=0.10 on every cell (the middle of the family r1325 named as a cost knob; declared in the pool at r1351 before this face existed)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.96pp | +10.93pp | +0.035pp | 4.54pp |
| 3 | 20 | +8.92pp | +8.71pp | +0.205pp | 7.07pp |
| 3 | 40 | +6.18pp | +6.78pp | -0.595pp | 12.70pp |
| 5 | 10 | +12.53pp | +11.51pp | +1.025pp | 3.34pp |
| 5 | 20 | +9.31pp | +9.13pp | +0.180pp | 6.06pp |
| 5 | 40 | +8.02pp | +8.32pp | -0.300pp | 9.91pp |
| 8 | 10 | +12.53pp | +12.00pp | +0.525pp | 3.14pp |
| 8 | 20 | +10.11pp | +10.13pp | -0.020pp | 5.75pp |
| 8 | 40 | +8.21pp | +8.30pp | -0.095pp | 8.38pp |
| 12 | 10 | +11.74pp | +11.63pp | +0.105pp | 2.63pp |
| 12 | 20 | +9.69pp | +9.64pp | +0.040pp | 6.99pp |
| 12 | 40 | +7.91pp | +7.55pp | +0.355pp | 7.23pp |

- cells 12/12 judged
- not-worse share 0.833 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.072pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k20 — **NOT-SEPARABLE**

buffer k=0.20 on every cell (the strongest arm -- if even this stays inside every cell's band, the buffer family is unmeasurable on this design, not negative)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +12.31pp | +10.93pp | +1.390pp | 4.56pp |
| 3 | 20 | +9.82pp | +8.71pp | +1.105pp | 6.73pp |
| 3 | 40 | +6.64pp | +6.78pp | -0.135pp | 12.85pp |
| 5 | 10 | +12.30pp | +11.51pp | +0.795pp | 3.83pp |
| 5 | 20 | +9.81pp | +9.13pp | +0.685pp | 5.74pp |
| 5 | 40 | +7.93pp | +8.32pp | -0.385pp | 10.87pp |
| 8 | 10 | +12.21pp | +12.00pp | +0.205pp | 2.71pp |
| 8 | 20 | +9.99pp | +10.13pp | -0.140pp | 6.58pp |
| 8 | 40 | +8.38pp | +8.30pp | +0.070pp | 8.12pp |
| 12 | 10 | +11.59pp | +11.63pp | -0.050pp | 2.81pp |
| 12 | 20 | +9.62pp | +9.64pp | -0.025pp | 5.58pp |
| 12 | 40 | +7.93pp | +7.55pp | +0.385pp | 7.51pp |

- cells 12/12 judged
- not-worse share 0.917 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.138pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k02 — **NOT-SEPARABLE**

buffer k=0.02 on every cell (the near-zero end -- a knob that reads the same at 0.02 and at 0.20 is flat, not merely small)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.94pp | +10.93pp | +0.015pp | 4.52pp |
| 3 | 20 | +8.44pp | +8.71pp | -0.275pp | 7.01pp |
| 3 | 40 | +6.75pp | +6.78pp | -0.025pp | 12.39pp |
| 5 | 10 | +11.68pp | +11.51pp | +0.175pp | 3.42pp |
| 5 | 20 | +9.10pp | +9.13pp | -0.030pp | 6.13pp |
| 5 | 40 | +8.34pp | +8.32pp | +0.020pp | 9.62pp |
| 8 | 10 | +11.96pp | +12.00pp | -0.035pp | 3.33pp |
| 8 | 20 | +10.10pp | +10.13pp | -0.035pp | 6.22pp |
| 8 | 40 | +8.29pp | +8.30pp | -0.010pp | 8.34pp |
| 12 | 10 | +11.58pp | +11.63pp | -0.055pp | 2.33pp |
| 12 | 20 | +9.65pp | +9.64pp | +0.005pp | 7.63pp |
| 12 | 40 | +7.59pp | +7.55pp | +0.045pp | 7.26pp |

- cells 12/12 judged
- not-worse share 0.917 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -0.018pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k40 — **REJECT**

buffer k=0.40 on every cell (8x the r1325 arm -- the far end, where a real buffer finally has to hurt)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +12.08pp | +10.93pp | +1.155pp | 3.59pp |
| 3 | 20 | +9.42pp | +8.71pp | +0.705pp | 6.78pp |
| 3 | 40 | +6.34pp | +6.78pp | -0.440pp | 12.56pp |
| 5 | 10 | +12.23pp | +11.51pp | +0.725pp | 3.93pp |
| 5 | 20 | +10.45pp | +9.13pp | +1.315pp | 5.81pp |
| 5 | 40 | +8.09pp | +8.32pp | -0.230pp | 11.04pp |
| 8 | 10 | +12.06pp | +12.00pp | +0.065pp | 2.72pp |
| 8 | 20 | +9.79pp | +10.13pp | -0.345pp | 6.04pp |
| 8 | 40 | +8.61pp | +8.30pp | +0.305pp | 9.21pp |
| 12 | 10 | +11.53pp | +11.63pp | -0.110pp | 2.72pp |
| 12 | 20 | +9.97pp | +9.64pp | +0.330pp | 5.50pp |
| 12 | 40 | +8.31pp | +7.55pp | +0.760pp | 8.10pp |

- cells 12/12 judged
- not-worse share 0.750 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.318pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k05_cost20 — **REJECT**

buffer k=0.05 at 20bp/side -- the interaction neither family tested: does a buffer that is harmless at 10bp recover any of the -1.41pp the 20bp toll costs?

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +8.54pp | +10.93pp | -2.390pp | 5.00pp |
| 3 | 20 | +7.21pp | +8.71pp | -1.510pp | 6.74pp |
| 3 | 40 | +5.73pp | +6.78pp | -1.050pp | 12.55pp |
| 5 | 10 | +9.44pp | +11.51pp | -2.070pp | 3.03pp |
| 5 | 20 | +7.72pp | +9.13pp | -1.410pp | 6.05pp |
| 5 | 40 | +7.38pp | +8.32pp | -0.940pp | 9.79pp |
| 8 | 10 | +9.77pp | +12.00pp | -2.235pp | 3.53pp |
| 8 | 20 | +8.43pp | +10.13pp | -1.705pp | 6.03pp |
| 8 | 40 | +7.35pp | +8.30pp | -0.955pp | 8.12pp |
| 12 | 10 | +9.45pp | +11.63pp | -2.185pp | 2.16pp |
| 12 | 20 | +8.43pp | +9.64pp | -1.220pp | 7.21pp |
| 12 | 40 | +7.04pp | +7.55pp | -0.510pp | 7.12pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -1.460pp (floor -0.05pp)
- resolvable share 0.083 (|delta| > the cell's own band; floor 0.50)

## cost0 — **NOT-SEPARABLE**

0bp/side on the whole grid (no toll at all) -- if the ordering only appears here, the ordering is bought with the toll and the 10bp reading stands

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +13.68pp | +10.93pp | +2.750pp | 4.41pp |
| 3 | 20 | +10.23pp | +8.71pp | +1.515pp | 7.11pp |
| 3 | 40 | +7.54pp | +6.78pp | +0.755pp | 12.41pp |
| 5 | 10 | +14.13pp | +11.51pp | +2.630pp | 3.64pp |
| 5 | 20 | +10.57pp | +9.13pp | +1.440pp | 6.31pp |
| 5 | 40 | +9.04pp | +8.32pp | +0.720pp | 9.60pp |
| 8 | 10 | +14.46pp | +12.00pp | +2.455pp | 3.42pp |
| 8 | 20 | +11.54pp | +10.13pp | +1.415pp | 6.54pp |
| 8 | 40 | +9.03pp | +8.30pp | +0.725pp | 8.44pp |
| 12 | 10 | +13.90pp | +11.63pp | +2.270pp | 2.82pp |
| 12 | 20 | +10.91pp | +9.64pp | +1.270pp | 7.94pp |
| 12 | 40 | +8.24pp | +7.55pp | +0.690pp | 6.95pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +1.427pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

