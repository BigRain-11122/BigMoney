# _r769bmb_probe.py -- side-by-side structure probe for UU faces (bytes via git, r209 read discipline)
import subprocess, json, sys

def blob(side, path):
    r = subprocess.run(["git", "show", f":{side}:{path}"], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

FACES = [
    "docs/daily_report/REPORT-2026-10-06.json",
    "docs/live_usage/LIVE-2026-10-06.json",
    "results/compute_audit.json",
    "results/dashboard_status.json",
    "results/regime_state.json",
    "results/strategy_scorecard.json",
    "results/scorecard_v1.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/_attrition_guard_scan.json",
]

FAM = ("generated","updated","asof","ts","timestamp","lastupdated","lastupdate","lastseen",
       "scannedat","checkedat","scanned","checked","heartbeat","clock","lastrun","runtime",
       "last_round","epoch","cutoff","complete","done")

def deep_ts(obj, path="", out=None):
    if out is None: out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = "".join(ch for ch in k.lower() if ch not in "_- ")
            if isinstance(v, str) and nk.startswith(FAM) and len(v) >= 16 and v[:4] == "2026":
                if v[10] in "T " and ":" in v[11:16]:
                    out.append((path + "/" + k, v))
            deep_ts(v, path + "/" + k, out)
    elif isinstance(obj, list):
        # do not descend into big ledger arrays for probe; only first entry for shape
        if obj and isinstance(obj[0], (dict, list)):
            deep_ts(obj[0], path + "/*", out)
    return out

for path in FACES:
    print("=" * 8, path)
    for side in (2, 3):
        b = blob(side, path)
        if b is None:
            print(f"  :{side}: <missing>")
            continue
        try:
            j = json.loads(b)
        except Exception as e:
            print(f"  :{side}: JSON ERR {e}")
            continue
        if isinstance(j, dict):
            keys = list(j.keys())
            print(f"  :{side}: keys={keys[:14]}")
            for kp, v in deep_ts(j)[:6]:
                print(f"        {kp} = {v}")
            for lk in ("history", "transitions", "launches"):
                if lk in j and isinstance(j[lk], list):
                    print(f"        ledger '{lk}': {len(j[lk])} entries; first={json.dumps(j[lk][0])[:150] if j[lk] else None}")
    print()
