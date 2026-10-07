"""r690 bm-c UU conflict probe: for each of the 17 UU faces, read both
blobs (REBASE_HEAD = mine per rebase-inversion law r688; origin/main =
theirs), print newest embedded timestamp + top-level JSON keys (or first
120 chars for non-JSON). Zero writes, pure facts for the resolver."""
import json
import re
import subprocess

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
FACES = [
    "docs/daily_report/REPORT-2026-10-07.json",
    "docs/daily_report/REPORT-2026-10-07.md",
    "docs/live_usage/LIVE-2026-10-07.json",
    "docs/live_usage/LIVE-2026-10-07.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]
TS_RE = re.compile(rb"2026-10-0\d[ T][0-9:]{8}")


def raw(rev, path):
    r = subprocess.run(["git", "-C", REPO, "show", f"{rev}:{path}"],
                       capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout


def side_info(b):
    if b is None:
        return "ABSENT"
    ts = max(TS_RE.findall(b)) if TS_RE.search(b) else b"-"
    try:
        d = json.loads(b)
        keys = ",".join(sorted(d.keys()))[:200] if isinstance(d, dict) else type(d).__name__
        return f"ts={ts.decode()} bytes={len(b)} keys={keys}"
    except Exception:
        return f"ts={ts.decode()} bytes={len(b)} nonjson head={b[:80]!r}"


for p in FACES:
    print("### " + p)
    print("  MINE   :", side_info(raw("REBASE_HEAD", p)))
    print("  THEIRS :", side_info(raw("origin/main", p)))
