"""r806 bm-a rebase UU resolver probe (read-only): per-face two-side inspection
for the 18 UU faces. Categories per 207a61507 precedent:
  - ts-empiricism (newer-wins) for S6 regenerable faces
  - union for history-array faces (compute_audit, token_usage)
Decisions printed, no writes."""
import subprocess, json, sys

FILES = ["docs/daily_report/REPORT-2026-10-07.json", "docs/daily_report/REPORT-2026-10-07.md",
         "docs/live_usage/LIVE-2026-10-07.json", "docs/live_usage/LIVE-2026-10-07.md",
         "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md",
         "results/_attrition_guard_scan.json", "results/compute_audit.json",
         "results/dashboard_status.js", "results/dashboard_status.json",
         "results/fundamental_b_layer_filter.json", "results/futures_update_status.json",
         "results/lhb_update_status.json", "results/regime_state.json",
         "results/scorecard_v1.json", "results/strategy_scorecard.json",
         "results/token_usage.json", "results/update_status.json"]


def blob(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True)
    return r.stdout, r.returncode


for f in FILES:
    # ours = stage-2 (HEAD/replayed), theirs = stage-3 (origin side)
    r2 = subprocess.run(["git", "show", f":2:{f}"], capture_output=True)
    r3 = subprocess.run(["git", "show", f":3:{f}"], capture_output=True)
    ours, theirs = r2.stdout, r3.stdout
    if ours == theirs:
        print(f"EQUAL  {f}")
        continue
    # try JSON ts empiricism
    def jts(b):
        try:
            d = json.loads(b.decode("utf-8", errors="replace"))
        except Exception:
            return None
        for k in ("ts", "generated", "generated_ts", "asof", "updated", "last_run"):
            if isinstance(d, dict) and k in d:
                return str(d[k])
        if isinstance(d, dict):
            for k in ("history",):
                if k in d and d[k]:
                    return "history:" + str(d[k][-1].get("ts", "?"))
        return "json-no-ts"
    to, tt = jts(ours), jts(theirs)
    print(f"DIFF   {f} | ours-ts={to} | theirs-ts={tt} | ours={len(ours)}B theirs={len(theirs)}B")
