import json, io

P = 'fleet/tasks/T-2026-09-26-73-P1.json'
d = json.load(io.open(P, encoding='utf-8'))
assert 'progress_r256' in d

d['progress_r257'] = (
    "R257 s2 slice-C = RETAIL-HERDING law in-repo census empirical ONE ROUND "
    "(third s2 law closed): scripts/t73_s2_retail_herding.py prereg-frozen header + "
    "selftest 8 legs (thr load/window math no-lookahead/IC sign/NaN-day drop/split+era "
    "boundaries) + batch 81.2s 9 IC faces (TO{5,20,60} x h{5,10,20}, turnover_derived "
    "sidecar trailing nanmean min_periods=ceil(w/2), no ffill on suspension NaNs, "
    "close-fwd P1C convention, 50-nulls p95 thresholds CITED not re-run seed0=20260923) "
    "-> results/t73_s2/retail_herding.json + digest DIGEST-20260926-t73-s2-sliceC-herding.md. "
    "VERDICT (frozen): herding law ALIVE BOTH SIDES -- TO20/h10 OOS ic -0.0635 (40x "
    "1.6bp thr) IS -0.0632 ir -0.407, gates_v123 5/5 PASS (FIRST s2 law to pass all "
    "gates; slice-A v2 fail, slice-B primary FAIL), ALL eras negative pre2005..2025+ "
    "(2017-2020 strongest -0.0927/ir -0.69, 2025+ alive -0.0635/ir -0.312 = decayed "
    "~55% vs peak but 40x thr), 8/9 faces gates-pass (to60/h5 v2 fail sole exception), "
    "short-window crowding strongest (TO5>TO20>TO60), premium persists at h20. "
    "Anti-repeat verified BEFORE build: plain turnover-level face absent from P-1c "
    "(alpha191 lib)/P-1d (quarterly ext slots gdhs/margin)/P-1e (turnover composites "
    "stv/arc) -- zero rebuild zero duplication, cross-cites in digest. Design input: "
    "low-turnover tilt = negative-selection/risk-style axis for CN-CORE-SATELLITE "
    "ballast leg + market-clock L4 sleeve turnover filter; IC!=tradable returns "
    "(BACKTEST_PLAN three laws on any strategy face). trials_N 9 faces + 50 nulls "
    "in-ledger reference, zero RNG zero seed-registry surface. NEXT SLICE (exact "
    "resume): s2 remaining = factor-history slice (size/lowvol/dividend; lowvol+size "
    "amount-proxy computable from P1C cache, dividend face via ETF style index 510880 "
    "honest proxy, fundamentals absent disclosed) then style-rotation slice "
    "(2017/2021/2023/2024 windows via ETF panels, all within ETF history); T+1/limit "
    "law face = consumed by T-57 s1/s2 coverage (cite-not-rebuild, closed); "
    "CORE-SATELLITE still blocked on T-57 satellite supply; 09-28 Monday new-bar chain."
)

io.open(P, 'w', encoding='utf-8', newline='\n').write(
    json.dumps(d, ensure_ascii=False, indent=1))   # no trailing newline = producer face
print('written, keys:', len(d))
