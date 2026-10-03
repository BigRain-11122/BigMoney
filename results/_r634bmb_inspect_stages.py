"""r634 bm-b: inspect stage2/stage3 blob structures for union-type conflicted faces."""
import json
import subprocess

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"


def side(path, stage):
    p = subprocess.run(
        ["git", "show", f":{stage}:{path}"], cwd=ROOT, capture_output=True
    )
    if p.returncode != 0:
        return None
    return p.stdout


for path in (
    "results/compute_audit.json",
    "results/regime_state.json",
    "results/x2_watch_log.jsonl",
    "results/dashboard_status.js",
    "results/daily_scorecard.json",
    "docs/daily_report/REPORT-2026-10-03.md",
    "docs/live_usage/LIVE-2026-10-03.md",
    "results/token_usage.json",
):
    print("===", path)
    for stage, label in ((2, "S2(origin-side)"), (3, "S3(mine-side)")):
        b = side(path, stage)
        if b is None:
            print(label, "MISSING")
            continue
        head = b.decode("utf-8", errors="replace")[:260].replace("\n", "\\n")
        print(label, "bytes=", len(b), "head=", head)
