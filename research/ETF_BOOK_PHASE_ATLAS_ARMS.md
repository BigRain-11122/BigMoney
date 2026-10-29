# 三个相位臂：把 r1325 的 buffer REJECT 放回它自己的尺子里重判

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

