import json
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
FACES = [
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/update_status.json",
    "results/token_usage.json",
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-latest.json",
    "results/_attrition_guard_scan.json",
]


def show(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], cwd=ROOT,
                       capture_output=True, timeout=30)
    return json.loads(r.stdout.decode("utf-8"))


for path in FACES:
    try:
        d = show("HEAD", path)
    except Exception as e:
        print(path, "HEAD-ERR", str(e)[:80])
        continue
    if isinstance(d, dict):
        ts_like = {k: str(v)[:30] for k, v in d.items()
                   if "ts" in k.lower() or "time" in k.lower()
                   or "generated" in k.lower() or k == "asof"
                   or "updated" in k.lower()}
        nest = {k: str(v)[:60] for k, v in d.items()
                if isinstance(v, dict) and k in ("latest", "status", "state")}
        print(path)
        print("   ts-like:", ts_like)
        if nest:
            print("   nested:", nest)
    else:
        print(path, "type", type(d).__name__)
