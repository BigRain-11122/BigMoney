# RW-6 Final Old-vs-New Table — 6 Registered Members (fixed engine)

One-time recompute per D-20260930-05 item 6 (ticket T-127). Engine = fully fixed: RW-1 exits fill T+1 open, RW-2 evidence_cutoff hard truncation, RW-3 single-source cost (13.041bp Face A), RW-4 panel gate. Evidence cutoff 2026-09-22 (frozen). Old = pre-fix frozen values (honest overstatement baseline, preserved verbatim); New = fresh recompute. Three-way consistency fresh==r472-refreeze==trader-JSON: BYTE-STABLE, drift 0.

## IS (in_sample)

| member | sharpe old→new | annual old→new | trades old→new | max_dd old→new |
|---|---|---|---|---|
| COMPOSITE-CE-01 | +0.4696→+1.1244 (+0.6548) | +0.0286→+0.0559 (+0.0273) | 312→309 (-3) | -0.1592→-0.0901 (+0.0691) |
| COMPOSITE-CE-02 | +0.5346→+0.7841 (+0.2495) | +0.0412→+0.0591 (+0.0179) | 543→513 (-30) | -0.1614→-0.1179 (+0.0435) |
| DROUGHT-CE-01 | +0.5538→+0.4610 (-0.0928) | +0.0169→+0.0141 (-0.0028) | 76→72 (-4) | -0.0476→-0.0530 (-0.0054) |
| ENGULF-CE-01 | +0.6121→+0.5337 (-0.0784) | +0.0197→+0.0174 (-0.0023) | 104→97 (-7) | -0.0426→-0.0496 (-0.0070) |
| NEEDLE-DE-01 | +0.7781→+0.6862 (-0.0919) | +0.0185→+0.0166 (-0.0019) | 50→49 (-1) | -0.0254→-0.0261 (-0.0007) |
| VOLATILITY-CE-01 | +1.0275→+1.1030 (+0.0755) | +0.0262→+0.0267 (+0.0005) | 375→339 (-36) | -0.0378→-0.0335 (+0.0043) |

## OOS (out_sample)

| member | sharpe old→new | annual old→new | trades old→new | max_dd old→new |
|---|---|---|---|---|
| COMPOSITE-CE-01 | +1.7479→+0.8620 (-0.8859) | +0.1366→+0.0745 (-0.0621) | 181→164 (-17) | -0.0434→-0.0735 (-0.0301) |
| COMPOSITE-CE-02 | +1.6392→+1.5605 (-0.0787) | +0.1140→+0.1024 (-0.0116) | 279→257 (-22) | -0.0380→-0.0381 (-0.0001) |
| DROUGHT-CE-01 | +1.2130→+1.2407 (+0.0277) | +0.0408→+0.0431 (+0.0023) | 44→41 (-3) | -0.0252→-0.0220 (+0.0032) |
| ENGULF-CE-01 | +0.3835→+0.1686 (-0.2149) | +0.0120→+0.0049 (-0.0071) | 46→43 (-3) | -0.0376→-0.0498 (-0.0122) |
| NEEDLE-DE-01 | +0.4089→+0.1927 (-0.2162) | +0.0119→+0.0049 (-0.0070) | 23→19 (-4) | -0.0282→-0.0278 (+0.0004) |
| VOLATILITY-CE-01 | +2.0568→+1.7166 (-0.3402) | +0.0424→+0.0355 (-0.0069) | 147→131 (-16) | -0.0090→-0.0113 (-0.0023) |

## Verdict

- OOS Sharpe sum 6 members: old +7.449 → new +5.741 (Δ -1.708)
- OOS Sharpe deltas per member (RW-1 disclosure, unchanged since r472): CE-01 −0.886, VOLATILITY −0.340, NEEDLE −0.216, ENGULF −0.215, CE-02 −0.079, DROUGHT +0.028
- Byte-stability: fresh recompute == r472 refrozen anchors == current trader JSONs (drift 0, r253 single-count law)
- Old numbers are DEAD for citation (D-20260930-22): no non-recomputed Sharpe to CEO before 10-31
- Null pool v2 + T-28 baseline recompute landed same round r477 (light legs, inline): null v2 = scripts/p2_null_calibration_v2.py (same frozen prereg design, same 48-symbol universe, same window ≤2026-09-22, same seeds; 120 backtests, 68s); T-28 recompute 16s

## Judgement line v2 (skill_line_v2) — engine-effect shift

- Null pool mu: −0.0332 (v1) → −0.0912 (v2); sigma: 0.2429 → 0.2368 — random entries lose more on the honest engine (T+1 open exits removed the same-close look-ahead edge)
- **skill_line_v2: 1.1958 → 1.107 (engine effect −0.0888, n_eff held 362,083)** — the honesty bar is slightly LOWER because even random strategies were flattered by the old exit fill
- Registry: science_gates.null_sharpes prefers p2_calibration_v2.json when present (source disclosed per read); v1 canon file untouched (frozen G1' gate constants for admission scripts unchanged)
- T-28 fixed-engine verdict: J1 True / J2 True / J3 True / J4 pooled 0.4854 < 0.70 → NOT-DEMONSTRATED (honest negative, all faces disclosed)
- t28 re-execution ledger note: first invocation without `--rerun` double-counted +20; surgically repaired same round pre-commit (head restored 362,083, attrition row delta→0, report line fixed) — pit-law candidate: re-execution runners with opt-in rerun flags must be invoked with the flag


