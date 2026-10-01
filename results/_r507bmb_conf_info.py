import glob
import json
import os
import subprocess


def stage(n, p):
    return subprocess.check_output(["git", "show", f":{n}:{p}"])


faces = ["compute_audit", "regime_state", "token_usage", "p1d_gates",
         "update_status", "lhb_update_status", "futures_update_status",
         "fundamental_b_layer_filter", "_attrition_guard_scan"]
print("=== lane twins present ===")
for f in faces:
    lanes = glob.glob(f"results/{f}.*.json")
    print(f, "->", [os.path.basename(x) for x in lanes] or "NO LANES")

print("=== docs ts compare (ours=:2 vs theirs=:3) ===")
docs = ["docs/daily_report/REPORT-2026-10-01.json",
        "docs/live_usage/LIVE-2026-10-01.json",
        "docs/live_usage/LIVE-latest.json"]
for p in docs:
    try:
        a = json.loads(stage(2, p))
        b = json.loads(stage(3, p))
        ka = a.get("generated") or a.get("generated_at") or a.get("ts")
        kb = b.get("generated") or b.get("generated_at") or b.get("ts")
        print(p, "| :2", ka, "| :3", kb)
    except Exception as ex:
        print(p, "PARSE", ex)

print("=== attrition scan ts ===")
for n in (2, 3):
    d = json.loads(stage(n, "results/_attrition_guard_scan.json"))
    print(n, d.get("generated") or d.get("ts") or list(d)[:4])

print("=== fundamental/lhb/futures/update ts ===")
for p in ["results/fundamental_b_layer_filter.json",
          "results/lhb_update_status.json",
          "results/futures_update_status.json",
          "results/update_status.json",
          "results/p1d_gates.json"]:
    for n in (2, 3):
        d = json.loads(stage(n, p))
        t = (d.get("generated") or d.get("ts") or d.get("updated")
             or (d.get("meta") or {}).get("ts") if isinstance(d, dict) else None)
        print(p, n, t)
