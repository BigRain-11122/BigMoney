import json
import subprocess

FILES = [
    "docs/daily_report/REPORT-2026-09-26.json",
    "results/compute_audit.json",
    "results/dashboard_status.json",
    "results/dashboard_status.js",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]

TS_KEYS = ("ts", "updated", "generated", "generated_at", "as_of", "last_attempt",
           "updated_at", "last_round", "swept_at", "date")

def blob(stage, path):
    r = subprocess.run(["git", "show", ":%s:%s" % (stage, path)], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

def ts_candidates(obj, prefix=""):
    """recursively collect ts-candidate keys with non-null scalar values"""
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            kk = prefix + k
            if isinstance(v, str) and k in TS_KEYS:
                out[kk] = v
            elif isinstance(v, dict):
                out.update(ts_candidates(v, kk + "."))
    return out

for p in FILES:
    print("=" * 70)
    print(p)
    for stage, who in (("2", "bm-a(up)"), ("3", "bm-b(me)")):
        raw = blob(stage, p)
        if raw is None:
            print("  :%s MISSING" % stage)
            continue
        if p.endswith(".js"):
            txt = raw.decode("utf-8-sig").strip()
            inner = txt[txt.find("{"): txt.rfind("}") + 1]
            try:
                obj = json.loads(inner)
            except Exception as e:
                print("  :%s JS-PARSE-FAIL %s" % (stage, e))
                continue
        else:
            try:
                obj = json.loads(raw.decode("utf-8-sig"))
            except Exception as e:
                print("  :%s PARSE-FAIL %s" % (stage, e))
                continue
        keys = ts_candidates(obj)
        interesting = {k: v for k, v in keys.items()}
        ledger = [k for k in obj if isinstance(obj.get(k), list)]
        print("  :%s ts=%s ledger-lists=%s" % (stage, interesting, ledger))
