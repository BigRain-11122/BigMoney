# LOWAMP-DEEPSCAN-P1 (neighborhood deep-scan -- exploration, NOT a verdict)

- O-2026-09-30-2340 sec.3 bm-c burn; T-132 verdict-input deepening; N3 instance
- bench EW19: disc12m 7.26% | val 2020-2025 58.68%
- 2450 cell-rows (450 neighborhood grid + 2000 random draws, wider band), dual cost x1/x2, segment halves
- frozen-band neighborhood (w75-105 x topN2-3 x invvol/eq x always): 121 cells, robust 121, beat_val>30pp 121

| cell | amp_w | topN | gate | sizing | disc12m% | disc sh | val20-25% | val sh | segA% | segB% | valx2% | robust | p5-p95 | perm_p |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C1563 | 79 | 2 | always | eq | 33.47 | 1.78 | 188.46 | 1.10 | 41.7 | 103.6 | 182.2 | True | 0.602..1.841 | 0.0015 |
| C0186 | 85 | 2 | always | eq | 33.05 | 1.77 | 202.56 | 1.18 | 48.8 | 103.3 | 196.6 | True | 0.677..1.897 | 0.0006 |
| C0698 | 85 | 2 | always | eq | 33.05 | 1.77 | 202.56 | 1.18 | 48.8 | 103.3 | 196.6 | True | 0.68..1.917 | 0.0003 |
| C2093 | 79 | 2 | always | invamp | 32.88 | 1.76 | 181.29 | 1.08 | 39.6 | 101.4 | 174.3 | True | 0.569..1.8 | 0.0011 |
| C0188 | 85 | 2 | always | invamp | 32.09 | 1.73 | 197.33 | 1.16 | 47.8 | 101.2 | 190.4 | True | 0.655..1.861 | 0.0015 |
| C1851 | 73 | 2 | always | eq | 31.95 | 1.73 | 192.31 | 1.13 | 40.9 | 107.5 | 186.2 | True | 0.633..1.855 | 0.0008 |
| C0484 | 86 | 2 | always | eq | 31.88 | 1.71 | 196.12 | 1.16 | 45.7 | 103.3 | 190.3 | True | 0.637..1.882 | 0.0009 |
| C0513 | 86 | 2 | always | eq | 31.88 | 1.71 | 196.12 | 1.16 | 45.7 | 103.3 | 190.3 | True | 0.647..1.868 | 0.0013 |
| C1304 | 88 | 2 | always | eq | 31.96 | 1.71 | 185.61 | 1.13 | 40.5 | 103.3 | 178.3 | True | 0.617..1.836 | 0.0008 |
| C1611 | 86 | 2 | always | eq | 31.88 | 1.71 | 196.12 | 1.16 | 45.7 | 103.3 | 190.3 | True | 0.647..1.868 | 0.0013 |
| C1738 | 88 | 2 | always | eq | 31.96 | 1.71 | 185.61 | 1.13 | 40.5 | 103.3 | 178.3 | True | 0.622..1.853 | 0.0009 |
| C0126 | 75 | 2 | always | eq | 31.26 | 1.71 | 208.24 | 1.17 | 50.1 | 105.4 | 201.3 | True | 0.646..1.87 | 0.001 |
| C0934 | 74 | 2 | always | eq | 31.35 | 1.70 | 196.28 | 1.14 | 44.9 | 104.5 | 188.4 | True | 0.625..1.866 | 0.0007 |
| C0451 | 77 | 2 | always | invamp | 31.48 | 1.70 | 187.46 | 1.10 | 43.0 | 101.0 | 180.2 | True | 0.593..1.822 | 0.0024 |
| C1176 | 73 | 2 | always | invamp | 31.14 | 1.69 | 189.29 | 1.12 | 40.9 | 105.3 | 182.1 | True | 0.616..1.836 | 0.0011 |
| C1283 | 73 | 2 | always | invamp | 31.14 | 1.69 | 189.29 | 1.12 | 40.9 | 105.3 | 182.1 | True | 0.603..1.827 | 0.0012 |
| C2077 | 82 | 2 | always | eq | 30.93 | 1.69 | 203.67 | 1.17 | 48.3 | 104.7 | 197.1 | True | 0.653..1.871 | 0.0008 |
| C0128 | 75 | 2 | always | invamp | 30.66 | 1.68 | 203.99 | 1.16 | 49.5 | 103.3 | 195.9 | True | 0.629..1.878 | 0.0009 |
| C0187 | 85 | 2 | always | invvol | 30.44 | 1.68 | 194.78 | 1.18 | 46.9 | 100.7 | 182.4 | True | 0.657..1.889 | 0.0006 |
| C1308 | 86 | 2 | always | invamp | 31.02 | 1.67 | 190.89 | 1.14 | 44.6 | 101.2 | 184.1 | True | 0.626..1.84 | 0.0022 |
| C1761 | 86 | 2 | always | invamp | 31.02 | 1.67 | 190.89 | 1.14 | 44.6 | 101.2 | 184.1 | True | 0.621..1.847 | 0.0014 |
| C1040 | 72 | 2 | always | eq | 30.37 | 1.67 | 192.04 | 1.13 | 41.2 | 106.9 | 184.3 | True | 0.616..1.848 | 0.0007 |
| C1605 | 82 | 2 | always | invamp | 30.45 | 1.67 | 195.92 | 1.14 | 46.2 | 102.4 | 188.8 | True | 0.631..1.837 | 0.0018 |
| C1843 | 82 | 2 | always | invamp | 30.45 | 1.67 | 195.92 | 1.14 | 46.2 | 102.4 | 188.8 | True | 0.627..1.85 | 0.001 |
| C0426 | 125 | 2 | always | eq | 30.53 | 1.66 | 123.87 | 0.92 | 10.1 | 103.3 | 121.9 | True | 0.436..1.672 | 0.0066 |

## Honest notes
- exploration face: selection-bias law applies; true out-of-sample = T-132 judged face (frozen prereg, K>=1000 virtual starts, dual nulls, x2 cost)
- Top-2/3 concentration = single-name risk face; liquidity/tradability entry gates belong to the T-132 judged face (frozen there)
- 19-ETF small universe; panel starts 2020 (no pre-2020 face on this universe)
