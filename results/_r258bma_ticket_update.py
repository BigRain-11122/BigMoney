import io
import json

PATH = r'fleet\tasks\T-2026-09-26-73-P1.json'
d = json.load(io.open(PATH, encoding='utf-8'))
assert 'progress_r258' not in d, 'r258 already present'
d['progress_r258'] = (
    "R258 s2 slice-D = SIZE/LOWVOL/DIVIDEND factor-history law in-repo census "
    "empirical ONE ROUND (fourth s2 topic closed, slice-C paradigm): NEW data "
    "leg scripts/t73_mktcap_sidecar.py builds mktcap_raw.npy sidecar via "
    "exchange-EXACT raw_close reconstruction preclose*(1+pct/100) (verified "
    "000001 final bar 11.71==cache, 5-sym recon rel_dev<=4e-8, align 0 "
    "unmatched, 19s) x osh; DATA-FACE DEFECT SELF-CAUGHT same round: bars "
    "outstanding_share = CURRENT snapshot ffilled BACKWARD (000001/300750/"
    "600519 full history ~zero changes, final-bar micro-adjust only) NOT "
    "per-row historical -> SIZE = PROXY (splits/dilutive issuance overstate "
    "past caps; OOS 2025+ segment near-TRUE osh_today==osh_t); meta "
    "honesty_face+osh_provenance_probe gate added BEFORE commit; "
    "cross-family note: turnover_derived sidecar shares this osh provenance "
    "(final-bar-only recon gate passes for the same reason; slice-C IS "
    "turnover levels carry inverse distortion -- NOT a reopen: law face "
    "alive both sides + OOS near-true, disclosed in digest SS5). Main: "
    "scripts/t73_s2_factor_history.py prereg-frozen + selftest (std windows "
    "ddof=1 single-obs NaN law, equal_nan compare law r251, era/CAGR/maxDD "
    "helpers, event detector, corpus 4784-bar assert) + batch 82.8s 9 IC "
    "faces (VOL{20,60} x h{5,10,20} + SIZE x h{5,10,20}) -> results/"
    "t73_s2/factor_history.json + digest DIGEST-20260926-t73-s2-sliceD-"
    "factors.md. VERDICT (frozen): (1) LOWVOL law ALIVE ALL 6 ERAS (FIRST "
    "all-era-uniform s2 law): VOL60/h10 IS -0.0504/OOS -0.0479 (30x 1.6bp "
    "thr), 6/6 eras negative pre2005..2025+, strengthened 2017+ (VOL20 "
    "2021-2024 ir -0.534 peak), 2015-2016 weak ir -0.11 disclosed; gates "
    "v1/v3/a3 pass v2 fail 9/9 (plain-face daily-IC IR below 0.3 = "
    "IC!=tradable; composed tradeable form = VOLATILITY-CE-01 registered "
    "trader cross-cite). (2) SIZE small-premium law NET-ALIVE but "
    "REGIME-DEPENDENT: SIZE/h10 IS -0.0453/OOS -0.0565 (35x thr), era table "
    "= crown jewel: 2015-2016 super-premium -0.1161/ir -0.812, 2017-2020 "
    "SIGN FLIP +0.0086 (large-cap core-asset era = small premium DEAD), "
    "2021-2024 revival -0.0537, 2025+ near-true -0.0565 alive; applicability "
    "honesty: NOT all-weather, consumers must carry regime guard (v3 guard/"
    "market-clock L5 exist). (3) DIVIDEND style face descriptive: 510880 "
    "price-face era table 2007-2026 + overlap vs 510300 2020-01-02..2026-09-22 "
    "1631d: CAGR +2.21% vs +1.65%, maxDD -22.0% vs -45.1% (drawdown HALVED), "
    "relative_cum 1.036, zero |ret|>11% fund events across 4784 bars; "
    "price-face excludes cash distributions = CONSERVATIVE LOWER BOUND "
    "disclosed. trials_N 9 faces + 50 nulls in-ledger ref, zero RNG. Design "
    "input: low-vol all-era axis for CN-CORE-SATELLITE ballast + market-clock "
    "L4 sleeve filter; size regime-guarded only; dividend defensive face "
    "feeds T-59 allocation line narrative. Next s2: style-rotation slice-E "
    "(2017/2021/2023/2024 via ETF panels) = LAST remaining s2 topic + T+1 "
    "limit-rule topic check in slice-A digest."
)
io.open(PATH, 'w', encoding='utf-8', newline='\n').write(
    json.dumps(d, ensure_ascii=False, indent=1))
print('written, no trailing newline')
