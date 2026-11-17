# 相位臂：把 r1325 的 buffer REJECT 与成本档放回它们自己的尺子里重判

面：`results/etf_book_phase_atlas_arms.json`｜脚本：`scripts/etf_book_phase_atlas_arms.py`｜基线面：`results/etf_book_phase_atlas.json`（cutoff 2026-11-17）

同日基线网格：格间 spread 5.41pp，格内 band 中位 7.12pp。

**面板一致性：MIXED_WORLDS** — 11 faces priced 2 different panels (0988c653, 0d5a9cdc): per-cell deltas across worlds are world differences, not rule effects

（判词不发布：本表的每个 Δ 都是「同一格、臂减基线」，跨面板相减得到的是世界差，不是规则效应。标签原文保留在 `verdict_if_coherent`；把臂重建到同一面板后自动恢复。）

## buffer_k05 — **NOT-SEPARABLE**

buffer k=0.05 on every cell (the r1325 arm, re-priced per phase)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.77pp | +9.88pp | +0.885pp | 5.44pp |
| 3 | 20 | +8.47pp | +8.49pp | -0.015pp | 7.23pp |
| 3 | 40 | +6.40pp | +6.58pp | -0.175pp | 12.80pp |
| 5 | 10 | +11.92pp | +11.43pp | +0.495pp | 3.06pp |
| 5 | 20 | +8.90pp | +8.87pp | +0.035pp | 6.20pp |
| 5 | 40 | +8.15pp | +7.95pp | +0.200pp | 10.46pp |
| 8 | 10 | +12.05pp | +11.98pp | +0.070pp | 3.49pp |
| 8 | 20 | +9.80pp | +9.54pp | +0.255pp | 5.95pp |
| 8 | 40 | +8.15pp | +7.69pp | +0.460pp | 8.49pp |
| 12 | 10 | +11.43pp | +11.47pp | -0.040pp | 2.26pp |
| 12 | 20 | +9.39pp | +9.43pp | -0.035pp | 6.88pp |
| 12 | 40 | +7.86pp | +7.80pp | +0.060pp | 7.13pp |

- cells 12/12 judged
- not-worse share 0.917 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.065pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## cost05 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **NOT-SEPARABLE**）

5bp/side on the whole grid (half the production toll)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +12.04pp | +9.88pp | +2.165pp | 4.58pp |
| 3 | 20 | +9.11pp | +8.49pp | +0.620pp | 7.08pp |
| 3 | 40 | +7.00pp | +6.58pp | +0.430pp | 12.59pp |
| 5 | 10 | +12.65pp | +11.43pp | +1.225pp | 3.65pp |
| 5 | 20 | +9.74pp | +8.87pp | +0.880pp | 6.39pp |
| 5 | 40 | +8.38pp | +7.95pp | +0.425pp | 9.92pp |
| 8 | 10 | +13.09pp | +11.98pp | +1.105pp | 3.33pp |
| 8 | 20 | +10.77pp | +9.54pp | +1.225pp | 6.46pp |
| 8 | 40 | +8.54pp | +7.69pp | +0.855pp | 8.70pp |
| 12 | 10 | +12.60pp | +11.47pp | +1.125pp | 2.85pp |
| 12 | 20 | +10.11pp | +9.43pp | +0.675pp | 7.70pp |
| 12 | 40 | +8.01pp | +7.80pp | +0.210pp | 7.01pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.867pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced 0988c653, the baseline 0d5a9cdc

## cost20 — **WORLDS_NOT_COMPARABLE**

（withheld: if coherent it would read **REJECT**）

20bp/side on the whole grid (double the production toll)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +7.97pp | +9.88pp | -1.910pp | 4.26pp |
| 3 | 20 | +6.91pp | +8.49pp | -1.580pp | 6.96pp |
| 3 | 40 | +5.83pp | +6.58pp | -0.745pp | 12.61pp |
| 5 | 10 | +8.86pp | +11.43pp | -2.570pp | 3.42pp |
| 5 | 20 | +7.60pp | +8.87pp | -1.265pp | 6.34pp |
| 5 | 40 | +7.31pp | +7.95pp | -0.640pp | 9.82pp |
| 8 | 10 | +9.46pp | +11.98pp | -2.520pp | 3.17pp |
| 8 | 20 | +8.68pp | +9.54pp | -0.865pp | 6.41pp |
| 8 | 40 | +7.48pp | +7.69pp | -0.210pp | 8.59pp |
| 12 | 10 | +9.21pp | +11.47pp | -2.255pp | 2.78pp |
| 12 | 20 | +8.23pp | +9.43pp | -1.200pp | 7.59pp |
| 12 | 40 | +6.99pp | +7.80pp | -0.815pp | 6.92pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -1.232pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)
- label withheld: this arm priced 0988c653, the baseline 0d5a9cdc

## cost40 — **REJECT**

40bp/side on the whole grid (4x the production toll -- does 'the cadence is quotable' have a toll ceiling, and does the ordering vanish first?)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +6.91pp | +9.88pp | -2.970pp | 4.63pp |
| 3 | 20 | +6.53pp | +8.49pp | -1.960pp | 8.04pp |
| 3 | 40 | +4.38pp | +6.58pp | -2.200pp | 9.69pp |
| 5 | 10 | +4.03pp | +11.43pp | -7.400pp | 2.97pp |
| 5 | 20 | +5.93pp | +8.87pp | -2.935pp | 7.62pp |
| 5 | 40 | +6.20pp | +7.95pp | -1.750pp | 9.87pp |
| 8 | 10 | +4.91pp | +11.98pp | -7.075pp | 2.88pp |
| 8 | 20 | +6.34pp | +9.54pp | -3.200pp | 6.02pp |
| 8 | 40 | +6.29pp | +7.69pp | -1.395pp | 8.09pp |
| 12 | 10 | +4.88pp | +11.47pp | -6.590pp | 3.13pp |
| 12 | 20 | +5.74pp | +9.43pp | -3.690pp | 6.05pp |
| 12 | 40 | +5.78pp | +7.80pp | -2.025pp | 8.35pp |

- cells 12/12 judged
- not-worse share 0.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -2.953pp (floor -0.05pp)
- resolvable share 0.250 (|delta| > the cell's own band; floor 0.50)

## buffer_k10 — **NOT-SEPARABLE**

buffer k=0.10 on every cell (the middle of the family r1325 named as a cost knob; declared in the pool at r1351 before this face existed)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +14.21pp | +9.88pp | +4.330pp | 4.85pp |
| 3 | 20 | +11.23pp | +8.49pp | +2.740pp | 5.89pp |
| 3 | 40 | +7.75pp | +6.58pp | +1.175pp | 9.45pp |
| 5 | 10 | +14.00pp | +11.43pp | +2.575pp | 5.17pp |
| 5 | 20 | +12.04pp | +8.87pp | +3.175pp | 6.30pp |
| 5 | 40 | +9.05pp | +7.95pp | +1.100pp | 8.52pp |
| 8 | 10 | +13.22pp | +11.98pp | +1.240pp | 5.32pp |
| 8 | 20 | +11.66pp | +9.54pp | +2.115pp | 7.59pp |
| 8 | 40 | +8.77pp | +7.69pp | +1.080pp | 8.00pp |
| 12 | 10 | +12.12pp | +11.47pp | +0.655pp | 3.21pp |
| 12 | 20 | +10.10pp | +9.43pp | +0.665pp | 4.51pp |
| 12 | 40 | +8.75pp | +7.80pp | +0.950pp | 6.61pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +1.208pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k20 — **NOT-SEPARABLE**

buffer k=0.20 on every cell (the strongest arm -- if even this stays inside every cell's band, the buffer family is unmeasurable on this design, not negative)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +12.00pp | +9.88pp | +2.120pp | 4.69pp |
| 3 | 20 | +9.32pp | +8.49pp | +0.835pp | 7.03pp |
| 3 | 40 | +6.62pp | +6.58pp | +0.040pp | 12.80pp |
| 5 | 10 | +11.99pp | +11.43pp | +0.570pp | 3.87pp |
| 5 | 20 | +9.70pp | +8.87pp | +0.835pp | 5.97pp |
| 5 | 40 | +7.83pp | +7.95pp | -0.115pp | 11.13pp |
| 8 | 10 | +11.88pp | +11.98pp | -0.105pp | 2.62pp |
| 8 | 20 | +10.07pp | +9.54pp | +0.525pp | 6.53pp |
| 8 | 40 | +8.46pp | +7.69pp | +0.770pp | 8.50pp |
| 12 | 10 | +11.31pp | +11.47pp | -0.155pp | 2.92pp |
| 12 | 20 | +9.51pp | +9.43pp | +0.080pp | 5.53pp |
| 12 | 40 | +7.91pp | +7.80pp | +0.105pp | 7.62pp |

- cells 12/12 judged
- not-worse share 0.917 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.315pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k02 — **NOT-SEPARABLE**

buffer k=0.02 on every cell (the near-zero end -- a knob that reads the same at 0.02 and at 0.20 is flat, not merely small)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +10.63pp | +9.88pp | +0.750pp | 4.72pp |
| 3 | 20 | +8.35pp | +8.49pp | -0.140pp | 7.16pp |
| 3 | 40 | +6.76pp | +6.58pp | +0.190pp | 12.38pp |
| 5 | 10 | +11.59pp | +11.43pp | +0.165pp | 3.31pp |
| 5 | 20 | +9.12pp | +8.87pp | +0.255pp | 6.29pp |
| 5 | 40 | +7.95pp | +7.95pp | +0.000pp | 10.11pp |
| 8 | 10 | +11.96pp | +11.98pp | -0.025pp | 3.32pp |
| 8 | 20 | +10.12pp | +9.54pp | +0.570pp | 6.01pp |
| 8 | 40 | +8.12pp | +7.69pp | +0.425pp | 8.59pp |
| 12 | 10 | +11.44pp | +11.47pp | -0.030pp | 2.30pp |
| 12 | 20 | +9.45pp | +9.43pp | +0.015pp | 7.41pp |
| 12 | 40 | +7.71pp | +7.80pp | -0.085pp | 7.32pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.090pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k40 — **NOT-SEPARABLE**

buffer k=0.40 on every cell (8x the r1325 arm -- the far end, where a real buffer finally has to hurt)

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +12.05pp | +9.88pp | +2.170pp | 3.85pp |
| 3 | 20 | +9.28pp | +8.49pp | +0.785pp | 6.73pp |
| 3 | 40 | +6.18pp | +6.58pp | -0.395pp | 13.00pp |
| 5 | 10 | +12.13pp | +11.43pp | +0.705pp | 4.35pp |
| 5 | 20 | +9.72pp | +8.87pp | +0.855pp | 6.04pp |
| 5 | 40 | +7.88pp | +7.95pp | -0.075pp | 11.64pp |
| 8 | 10 | +11.96pp | +11.98pp | -0.025pp | 2.92pp |
| 8 | 20 | +9.77pp | +9.54pp | +0.220pp | 5.94pp |
| 8 | 40 | +8.47pp | +7.69pp | +0.780pp | 9.65pp |
| 12 | 10 | +11.26pp | +11.47pp | -0.210pp | 2.21pp |
| 12 | 20 | +10.02pp | +9.43pp | +0.590pp | 5.53pp |
| 12 | 40 | +8.45pp | +7.80pp | +0.645pp | 8.34pp |

- cells 12/12 judged
- not-worse share 0.833 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +0.617pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

## buffer_k05_cost20 — **REJECT**

buffer k=0.05 at 20bp/side -- the interaction neither family tested: does a buffer that is harmless at 10bp recover any of the -1.41pp the 20bp toll costs?

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +12.37pp | +9.88pp | +2.490pp | 5.09pp |
| 3 | 20 | +8.43pp | +8.49pp | -0.060pp | 9.56pp |
| 3 | 40 | +5.97pp | +6.58pp | -0.605pp | 12.75pp |
| 5 | 10 | +9.46pp | +11.43pp | -1.970pp | 2.95pp |
| 5 | 20 | +7.99pp | +8.87pp | -0.875pp | 6.47pp |
| 5 | 40 | +7.77pp | +7.95pp | -0.180pp | 10.39pp |
| 8 | 10 | +9.74pp | +11.98pp | -2.235pp | 5.56pp |
| 8 | 20 | +8.29pp | +9.54pp | -1.255pp | 5.93pp |
| 8 | 40 | +7.57pp | +7.69pp | -0.125pp | 8.42pp |
| 12 | 10 | +9.26pp | +11.47pp | -2.210pp | 2.20pp |
| 12 | 20 | +8.19pp | +9.43pp | -1.240pp | 6.02pp |
| 12 | 40 | +7.20pp | +7.80pp | -0.600pp | 7.19pp |

- cells 12/12 judged
- not-worse share 0.250 (floor 0.80, cell floor -0.15pp)
- median per-cell delta -0.740pp (floor -0.05pp)
- resolvable share 0.083 (|delta| > the cell's own band; floor 0.50)

## cost0 — **NOT-SEPARABLE**

0bp/side on the whole grid (no toll at all) -- if the ordering only appears here, the ordering is bought with the toll and the 10bp reading stands

| n_hold | rebal | 中位 CAGR | 基线 | Δ | 本格 band |
|---|---|---|---|---|---|
| 3 | 10 | +13.37pp | +9.88pp | +3.490pp | 4.68pp |
| 3 | 20 | +9.97pp | +8.49pp | +1.485pp | 7.18pp |
| 3 | 40 | +7.48pp | +6.58pp | +0.905pp | 12.38pp |
| 5 | 10 | +13.97pp | +11.43pp | +2.545pp | 3.55pp |
| 5 | 20 | +10.60pp | +8.87pp | +1.730pp | 6.52pp |
| 5 | 40 | +8.66pp | +7.95pp | +0.715pp | 10.11pp |
| 8 | 10 | +14.44pp | +11.98pp | +2.460pp | 3.33pp |
| 8 | 20 | +11.56pp | +9.54pp | +2.015pp | 6.42pp |
| 8 | 40 | +8.85pp | +7.69pp | +1.155pp | 8.84pp |
| 12 | 10 | +13.74pp | +11.47pp | +2.275pp | 2.87pp |
| 12 | 20 | +10.69pp | +9.43pp | +1.260pp | 7.50pp |
| 12 | 40 | +8.37pp | +7.80pp | +0.570pp | 7.12pp |

- cells 12/12 judged
- not-worse share 1.000 (floor 0.80, cell floor -0.15pp)
- median per-cell delta +1.607pp (floor -0.05pp)
- resolvable share 0.000 (|delta| > the cell's own band; floor 0.50)

