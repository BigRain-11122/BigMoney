# RW-1 PROSPECT Anchor Refreeze 2026-09-30 (r491 bm-a)

Context: r472 RW-1 exit look-ahead fix (audit P0-1, D-20260930-05 umbrella)
made exits decided at close T fill at T+1 open UNCONDITIONALLY. The 6
registered live members were refrozen same-cutoff in r472; the 22 PROSPECT
members kept pre-RW-1 recorded evidence and r475's caliber pinning cannot
reproduce it (exit timing is not param-gated). First new-bar window after
the flip (09-30 bar landed 20:42) surfaced 22/22 anchor drift
(t24_prospect_paper rc=2, member files untouched by contract).

Action: recompute every PROSPECT member at its FROZEN evidence_cutoff with
the current engine and the member's declared caliber pins; overwrite the
recorded evidence faces only (prospect.recorded_* + backtest mirror +
anchor_status provenance). g1_pass, paper tracking history, params,
status_history untouched. Old values preserved below for audit.

| member | g1_pass | full_sharpe old->new | oos_sharpe old->new | x2 old->new | trades old->new | oos_trades old->new | max_dd old->new |
|---|---|---|---|---|---|---|---|
| PROS-ANTS-01 | False | +0.2599 -> -0.0086 *SIGN* | +0.6294 -> +0.3455 | +0.0146 -> -0.2533 | 187 -> 181 | 66 -> 64 | -0.0611 -> -0.0756 |
| PROS-ANTS-CE-01 | False | +0.2052 -> +0.0778 | +0.5221 -> +0.5345 | -0.0270 -> -0.1496 | 177 -> 172 | 60 -> 58 | -0.0623 -> -0.0719 |
| PROS-BBS-01 | False | +0.2386 -> +0.1669 | +0.5315 -> +0.4997 | -0.1180 -> -0.1680 | 672 -> 596 | 167 -> 160 | -0.1342 -> -0.1440 |
| PROS-BBS-CE-01 | False | +0.2384 -> +0.1286 | +0.6196 -> +0.4682 | -0.0162 -> -0.1273 | 495 -> 481 | 131 -> 130 | -0.1384 -> -0.1473 |
| PROS-DOJI-01 | False | +0.2102 -> +0.2064 | +0.3398 -> +0.5372 | -0.0340 -> -0.0252 | 541 -> 491 | 141 -> 121 | -0.1913 -> -0.1692 |
| PROS-DOJI-CE-01 | False | +0.2438 -> +0.2440 | +0.4018 -> +0.5113 | +0.0523 -> +0.0525 | 422 -> 396 | 105 -> 97 | -0.1685 -> -0.1642 |
| PROS-DUCK-01 | True | +0.6817 -> +0.2225 | +0.8227 -> +0.2596 | +0.2583 -> -0.1552 | 947 -> 837 | 264 -> 230 | -0.0770 -> -0.1944 |
| PROS-DUCK-CE-01 | True | +0.5347 -> +0.3701 | +0.6059 -> +0.0376 | +0.2097 -> +0.0258 | 798 -> 729 | 225 -> 205 | -0.1165 -> -0.1346 |
| PROS-HAM-01 | False | +0.2326 -> +0.0916 | +0.1544 -> -0.0368 | +0.0256 -> -0.1024 | 360 -> 324 | 124 -> 105 | -0.1287 -> -0.1162 |
| PROS-HAM-CE-01 | False | +0.1957 -> +0.1462 | +0.1283 -> -0.0969 | +0.0447 -> -0.0051 | 267 -> 258 | 95 -> 87 | -0.1229 -> -0.1054 |
| PROS-IBB-01 | False | +0.2694 -> +0.0624 | +1.1122 -> +0.0823 | -0.0697 -> -0.2539 | 1306 -> 1164 | 365 -> 319 | -0.2466 -> -0.2585 |
| PROS-IBB-CE-01 | False | +0.3691 -> +0.2553 | +1.3755 -> +0.4743 | +0.0416 -> -0.0546 | 1192 -> 1087 | 335 -> 300 | -0.2279 -> -0.2207 |
| PROS-IMM-01 | False | +0.0447 -> -0.0286 *SIGN* | +0.4320 -> -0.0796 | -0.2358 -> -0.3127 | 906 -> 828 | 286 -> 254 | -0.2123 -> -0.2478 |
| PROS-IMM-CE-01 | False | +0.0208 -> +0.0186 | +0.3595 -> +0.0881 | -0.2234 -> -0.2294 | 791 -> 754 | 247 -> 227 | -0.2080 -> -0.2449 |
| PROS-MCB-01 | False | +0.2822 -> -0.1934 *SIGN* | +0.7651 -> +0.8278 | -0.3731 -> -0.7393 | 1279 -> 1128 | 345 -> 297 | -0.1132 -> -0.2857 |
| PROS-MCB-CE-01 | False | +0.3370 -> -0.2203 *SIGN* | +0.9458 -> +0.7916 | -0.2443 -> -0.7892 | 1107 -> 996 | 303 -> 277 | -0.1038 -> -0.2419 |
| PROS-OVB-01 | False | +0.3318 -> +0.1144 | +0.4749 -> +0.9148 | +0.1419 -> -0.0199 | 119 -> 111 | 41 -> 40 | -0.0455 -> -0.0798 |
| PROS-OVB-CE-01 | False | +0.3350 -> +0.1417 | +0.4749 -> +0.9148 | +0.1513 -> +0.0095 | 115 -> 109 | 41 -> 40 | -0.0455 -> -0.0743 |
| PROS-RSRS-CE-01 | False | +0.0334 -> +0.0106 | +0.8398 -> +0.9395 | -0.1749 -> -0.1962 | 657 -> 598 | 237 -> 214 | -0.2360 -> -0.2327 |
| PROS-TMU-01 | False | +0.0897 -> -0.2111 *SIGN* | +0.5381 -> -0.2033 | +0.0023 -> -0.2956 | 54 -> 48 | 22 -> 16 | -0.0403 -> -0.0446 |
| PROS-TMU-CE-01 | False | +0.0945 -> -0.0925 *SIGN* | +0.5009 -> -0.0777 | +0.0143 -> -0.1744 | 49 -> 49 | 18 -> 18 | -0.0383 -> -0.0436 |
| PROS-VOB-CE-01 | True | +0.4665 -> +0.4954 | +1.2670 -> +1.3141 | +0.2013 -> +0.2509 | 803 -> 745 | 215 -> 202 | -0.1170 -> -0.1207 |

Sign flips (full_sharpe positive->non-positive): 6/22.
Science-owner note: g1 re-evaluation under refrozen evidence (and any
PROSPECT-pool demotion) is a science-face decision, NOT taken here;
promotion path continues to apply frozen criteria (paper months + G2 +
T-22 beat-rate) to forward tracking only.
