# r491bma probe v2: anchor replay vs recorded, correct key extraction.
import json, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, 'scripts')
import p3_portfolio as p3
from t24_prospect_onboard import _compare
lp = __import__('live.paper', fromlist=['x'])

out = {"round": "r491 bm-a anchor-drift diagnosis v2"}
prices = lp.load_core()
for mid in ("PROS-ANTS-01", "PROS-DOJI-CE-01", "PROS-TMU-CE-01"):
    t = json.load(open(f'firm/traders/{mid}.json', encoding='utf-8'))
    r1 = p3.member_run(t, prices)
    r2 = p3.member_run(t, prices, cost_mult=2.0)
    v = _compare(r1, r2, t['prospect'])
    out[mid] = {"checks": v["checks"], "got": v["got"],
                "recorded": {k: t["prospect"][k] for k in (
                    "recorded_full_sharpe", "recorded_oos_sharpe",
                    "recorded_x2_full_sharpe", "recorded_n_trades",
                    "recorded_oos_trades", "recorded_max_dd")},
                "params": t.get("params"), "replay_cutoff": r1["cutoff"]}
with open('results/_r491bma_anchor_drift_probe.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
