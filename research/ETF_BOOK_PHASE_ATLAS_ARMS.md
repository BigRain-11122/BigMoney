# 相位臂：把 r1325 的 buffer REJECT 与成本档放回它们自己的尺子里重判

面：`results/etf_book_phase_atlas_arms.json`｜脚本：`scripts/etf_book_phase_atlas_arms.py`｜基线面：`results/etf_book_phase_atlas.json`（cutoff 2026-10-30）

同日基线网格：格间 spread 5.27pp，格内 band 中位 6.73pp。

**面板一致性：ONE_WORLD** — all 11 faces priced a1a42aee64453839

## buffer_k05 — **REJECT**

buffer k=0.05 on every cell (the r1325 arm, re-priced per phase)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +11.03pp | +10.87pp | +0.160pp | 5.34pp |
| 3 | 20 | +8.54pp | +8.58pp | -0.045pp | 6.95pp |
| 3 | 40 | +6.42pp | +6.69pp | -0.270pp | 12.74pp |
| 5 | 10 | +11.93pp | +11.51pp | +0.415pp | 3.23pp |
| 5 | 20 | +9.02pp | +9.09pp | -0.070pp | 6.23pp |
| 5 | 40 | +8.10pp | +8.22pp | -0.125pp | 10.10pp |
| 8 | 10 | +12.03pp | +11.96pp | +0.070pp | 3.62pp |
| 8 | 20 | +9.77pp | +10.12pp | -0.350pp | 6.02pp |
| 8 | 40 | +8.06pp | +8.22pp | -0.160pp | 8.31pp |
| 12 | 10 | +11.48pp | +11.61pp | -0.120pp | 2.22pp |
| 12 | 20 | +9.54pp | +9.59pp | -0.050pp | 7.23pp |
| 12 | 40 | +7.72pp | +7.55pp | +0.170pp | 7.02pp |

- cells 12/12 judged
- not-worse share 0.750 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -0.060pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## cost05 — **NOT-SEPARABLE**

5bp/side on the whole grid (half the production toll)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +12.24pp | +10.87pp | +1.375pp | 4.47pp |
| 3 | 20 | +9.33pp | +8.58pp | +0.750pp | 7.07pp |
| 3 | 40 | +7.06pp | +6.69pp | +0.370pp | 12.48pp |
| 5 | 10 | +12.79pp | +11.51pp | +1.285pp | 3.65pp |
| 5 | 20 | +9.80pp | +9.09pp | +0.720pp | 6.40pp |
| 5 | 40 | +8.58pp | +8.22pp | +0.360pp | 9.71pp |
| 8 | 10 | +13.18pp | +11.96pp | +1.220pp | 3.43pp |
| 8 | 20 | +10.82pp | +10.12pp | +0.705pp | 6.59pp |
| 8 | 40 | +8.59pp | +8.22pp | +0.365pp | 8.58pp |
| 12 | 10 | +12.74pp | +11.61pp | +1.140pp | 2.78pp |
| 12 | 20 | +10.22pp | +9.59pp | +0.630pp | 7.86pp |
| 12 | 40 | +7.89pp | +7.55pp | +0.340pp | 6.93pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.712pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## cost20 — **REJECT**

20bp/side on the whole grid (double the production toll)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +8.16pp | +10.87pp | -2.700pp | 4.22pp |
| 3 | 20 | +7.09pp | +8.58pp | -1.490pp | 6.87pp |
| 3 | 40 | +5.95pp | +6.69pp | -0.745pp | 12.50pp |
| 5 | 10 | +8.96pp | +11.51pp | -2.550pp | 3.44pp |
| 5 | 20 | +7.66pp | +9.09pp | -1.425pp | 6.33pp |
| 5 | 40 | +7.52pp | +8.22pp | -0.700pp | 9.63pp |
| 8 | 10 | +9.55pp | +11.96pp | -2.405pp | 3.29pp |
| 8 | 20 | +8.72pp | +10.12pp | -1.395pp | 6.50pp |
| 8 | 40 | +7.50pp | +8.22pp | -0.715pp | 8.52pp |
| 12 | 10 | +9.38pp | +11.61pp | -2.230pp | 2.70pp |
| 12 | 20 | +8.32pp | +9.59pp | -1.270pp | 7.76pp |
| 12 | 40 | +6.87pp | +7.55pp | -0.685pp | 6.86pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -1.410pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## cost40 — **REJECT**

40bp/side on the whole grid (4x the production toll -- does 'the cadence is quotable' have a toll ceiling, and does the ordering vanish first?)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +2.99pp | +10.87pp | -7.875pp | 3.91pp |
| 3 | 20 | +4.20pp | +8.58pp | -4.380pp | 6.82pp |
| 3 | 40 | +4.43pp | +6.69pp | -2.255pp | 12.54pp |
| 5 | 10 | +4.04pp | +11.51pp | -7.475pp | 3.19pp |
| 5 | 20 | +4.86pp | +9.09pp | -4.225pp | 6.26pp |
| 5 | 40 | +6.08pp | +8.22pp | -2.140pp | 9.52pp |
| 8 | 10 | +4.89pp | +11.96pp | -7.065pp | 3.09pp |
| 8 | 20 | +5.98pp | +10.12pp | -4.135pp | 6.38pp |
| 8 | 40 | +6.08pp | +8.22pp | -2.140pp | 8.48pp |
| 12 | 10 | +5.03pp | +11.61pp | -6.580pp | 2.65pp |
| 12 | 20 | +5.81pp | +9.59pp | -3.780pp | 7.62pp |
| 12 | 40 | +5.51pp | +7.55pp | -2.040pp | 6.76pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -4.180pp (floor -0.05pp)
- resolvable share 0.333 (|delta| > the cell's own band; floor 0.50)

## buffer_k10 — **NOT-SEPARABLE**

buffer k=0.10 on every cell (the middle of the family r1325 named as a cost knob; declared in the pool at r1351 before this face existed)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.90pp | +10.87pp | +0.040pp | 4.60pp |
| 3 | 20 | +8.78pp | +8.58pp | +0.200pp | 7.29pp |
| 3 | 40 | +6.13pp | +6.69pp | -0.555pp | 12.89pp |
| 5 | 10 | +12.46pp | +11.51pp | +0.945pp | 3.42pp |
| 5 | 20 | +9.23pp | +9.09pp | +0.150pp | 6.18pp |
| 5 | 40 | +7.89pp | +8.22pp | -0.325pp | 10.15pp |
| 8 | 10 | +12.48pp | +11.96pp | +0.520pp | 3.16pp |
| 8 | 20 | +10.12pp | +10.12pp | +0.005pp | 5.76pp |
| 8 | 40 | +8.24pp | +8.22pp | +0.020pp | 8.57pp |
| 12 | 10 | +11.59pp | +11.61pp | -0.020pp | 2.74pp |
| 12 | 20 | +9.68pp | +9.59pp | +0.085pp | 6.94pp |
| 12 | 40 | +7.91pp | +7.55pp | +0.355pp | 7.16pp |

- cells 12/12 judged
- not-worse share 0.833 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.062pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k20 — **NOT-SEPARABLE**

buffer k=0.20 on every cell (the strongest arm -- if even this stays inside every cell's band, the buffer family is unmeasurable on this design, not negative)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +12.41pp | +10.87pp | +1.550pp | 4.34pp |
| 3 | 20 | +9.68pp | +8.58pp | +1.100pp | 6.90pp |
| 3 | 40 | +7.79pp | +6.69pp | +1.105pp | 12.10pp |
| 5 | 10 | +12.50pp | +11.51pp | +0.990pp | 4.51pp |
| 5 | 20 | +9.75pp | +9.09pp | +0.665pp | 5.96pp |
| 5 | 40 | +7.86pp | +8.22pp | -0.360pp | 11.08pp |
| 8 | 10 | +12.11pp | +11.96pp | +0.150pp | 3.77pp |
| 8 | 20 | +10.46pp | +10.12pp | +0.340pp | 6.62pp |
| 8 | 40 | +8.81pp | +8.22pp | +0.590pp | 8.55pp |
| 12 | 10 | +11.47pp | +11.61pp | -0.135pp | 4.75pp |
| 12 | 20 | +9.57pp | +9.59pp | -0.015pp | 5.86pp |
| 12 | 40 | +8.10pp | +7.55pp | +0.545pp | 7.57pp |

- cells 12/12 judged
- not-worse share 0.917 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.568pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k02 — **NOT-SEPARABLE**

buffer k=0.02 on every cell (the near-zero end -- a knob that reads the same at 0.02 and at 0.20 is flat, not merely small)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.88pp | +10.87pp | +0.020pp | 4.66pp |
| 3 | 20 | +8.41pp | +8.58pp | -0.165pp | 7.09pp |
| 3 | 40 | +6.69pp | +6.69pp | +0.000pp | 12.45pp |
| 5 | 10 | +11.69pp | +11.51pp | +0.180pp | 3.51pp |
| 5 | 20 | +9.06pp | +9.09pp | -0.025pp | 6.26pp |
| 5 | 40 | +8.23pp | +8.22pp | +0.015pp | 9.90pp |
| 8 | 10 | +11.94pp | +11.96pp | -0.025pp | 3.41pp |
| 8 | 20 | +10.08pp | +10.12pp | -0.035pp | 6.22pp |
| 8 | 40 | +8.21pp | +8.22pp | -0.010pp | 8.46pp |
| 12 | 10 | +11.54pp | +11.61pp | -0.070pp | 2.35pp |
| 12 | 20 | +9.57pp | +9.59pp | -0.020pp | 7.59pp |
| 12 | 40 | +7.61pp | +7.55pp | +0.055pp | 7.25pp |

- cells 12/12 judged
- not-worse share 0.917 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -0.015pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k40 — **REJECT**

buffer k=0.40 on every cell (8x the r1325 arm -- the far end, where a real buffer finally has to hurt)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +12.07pp | +10.87pp | +1.205pp | 3.57pp |
| 3 | 20 | +9.35pp | +8.58pp | +0.765pp | 6.87pp |
| 3 | 40 | +6.30pp | +6.69pp | -0.385pp | 12.76pp |
| 5 | 10 | +12.17pp | +11.51pp | +0.660pp | 4.12pp |
| 5 | 20 | +10.29pp | +9.09pp | +1.205pp | 5.68pp |
| 5 | 40 | +8.05pp | +8.22pp | -0.170pp | 11.34pp |
| 8 | 10 | +12.06pp | +11.96pp | +0.105pp | 2.87pp |
| 8 | 20 | +9.76pp | +10.12pp | -0.360pp | 6.15pp |
| 8 | 40 | +8.56pp | +8.22pp | +0.345pp | 9.36pp |
| 12 | 10 | +11.54pp | +11.61pp | -0.060pp | 2.83pp |
| 12 | 20 | +9.97pp | +9.59pp | +0.385pp | 5.60pp |
| 12 | 40 | +8.38pp | +7.55pp | +0.830pp | 8.21pp |

- cells 12/12 judged
- not-worse share 0.750 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.365pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k05_cost20 — **REJECT**

buffer k=0.05 at 20bp/side -- the interaction neither family tested: does a buffer that is harmless at 10bp recover any of the -1.41pp the 20bp toll costs?

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +8.46pp | +10.87pp | -2.400pp | 5.13pp |
| 3 | 20 | +7.16pp | +8.58pp | -1.425pp | 6.89pp |
| 3 | 40 | +5.68pp | +6.69pp | -1.005pp | 12.72pp |
| 5 | 10 | +9.46pp | +11.51pp | -2.045pp | 3.11pp |
| 5 | 20 | +7.61pp | +9.09pp | -1.475pp | 6.21pp |
| 5 | 40 | +7.37pp | +8.22pp | -0.850pp | 10.04pp |
| 8 | 10 | +9.72pp | +11.96pp | -2.235pp | 3.53pp |
| 8 | 20 | +8.41pp | +10.12pp | -1.700pp | 5.99pp |
| 8 | 40 | +7.36pp | +8.22pp | -0.865pp | 8.27pp |
| 12 | 10 | +9.36pp | +11.61pp | -2.245pp | 2.18pp |
| 12 | 20 | +8.35pp | +9.59pp | -1.245pp | 7.17pp |
| 12 | 40 | +7.05pp | +7.55pp | -0.495pp | 6.99pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -1.450pp (floor -0.05pp)
- resolvable share 0.083 (|delta| > the cell's own band; floor 0.50)

## cost0 — **NOT-SEPARABLE**

0bp/side on the whole grid (no toll at all) -- if the ordering only appears here, the ordering is bought with the toll and the 10bp reading stands

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +13.63pp | +10.87pp | +2.765pp | 4.58pp |
| 3 | 20 | +10.09pp | +8.58pp | +1.510pp | 7.15pp |
| 3 | 40 | +7.43pp | +6.69pp | +0.745pp | 12.47pp |
| 5 | 10 | +14.09pp | +11.51pp | +2.580pp | 3.72pp |
| 5 | 20 | +10.53pp | +9.09pp | +1.445pp | 6.41pp |
| 5 | 40 | +8.93pp | +8.22pp | +0.710pp | 9.73pp |
| 8 | 10 | +14.41pp | +11.96pp | +2.455pp | 3.49pp |
| 8 | 20 | +11.53pp | +10.12pp | +1.410pp | 6.62pp |
| 8 | 40 | +8.95pp | +8.22pp | +0.725pp | 8.61pp |
| 12 | 10 | +13.88pp | +11.61pp | +2.280pp | 2.81pp |
| 12 | 20 | +10.85pp | +9.59pp | +1.260pp | 7.89pp |
| 12 | 40 | +8.24pp | +7.55pp | +0.690pp | 6.96pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +1.427pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

