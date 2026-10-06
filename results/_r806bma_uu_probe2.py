"""r806 bm-a UU resolver probe 2: locate actual differing lines for the ts-less
faces (md twins + regime_state + dashboard) to confirm which side is newer."""
import subprocess, json, difflib

FILES = ["docs/daily_report/REPORT-2026-10-07.md", "docs/live_usage/LIVE-2026-10-07.md",
         "docs/live_usage/LIVE-latest.md", "results/regime_state.json",
         "results/dashboard_status.json", "results/dashboard_status.js"]

for f in FILES:
    b2 = subprocess.run(["git", "show", f":2:{f}"], capture_output=True).stdout
    b3 = subprocess.run(["git", "show", f":3:{f}"], capture_output=True).stdout
    l2 = b2.decode("utf-8", errors="replace").splitlines()
    l3 = b3.decode("utf-8", errors="replace").splitlines()
    print(f"=== {f} (:2: origin/bm-c {len(b2)}B vs :3: mine {len(b3)}B)")
    n = 0
    for line in difflib.unified_diff(l2, l3, lineterm="", n=0):
        if line.startswith(("---", "+++", "@@")):
            continue
        print("   ", line[:180])
        n += 1
        if n >= 6:
            break
