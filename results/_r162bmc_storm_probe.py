# -*- coding: utf-8 -*-
"""r162 bm-c push-storm ts-probe (15-UU vs bm-b same-window faces). Canon r158/r161 recipe."""
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def stage(n, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (n, path)], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("stage read fail %s" % path)
    return r.stdout

def probe_ts(data, path):
    """Extract a comparison ts from a JSON or text face."""
    if path.endswith(".json"):
        try:
            d = json.loads(data.decode("utf-8"))
        except Exception:
            return None
        for k in ("ts", "generated", "updated", "updated_at"):
            v = d.get(k) if isinstance(d, dict) else None
            if isinstance(v, str) and ("T" in v or ":" in v):
                return v
        # nested common spots
        for k in ("latest",):
            if isinstance(d, dict) and isinstance(d.get(k), dict):
                v = d[k].get("ts")
                if isinstance(v, str):
                    return v
        return None
    else:
        # text face: last ISO-ish stamp
        import re
        m = re.findall(r"20\d\d-\d\d-\d\d[T ]\d\d:\d\d(:\d\d)?", data.decode("utf-8", errors="replace"))
        return m[-1] if m else None

FACES = [
    "docs/daily_report/REPORT-2026-09-28.json",
    "docs/daily_report/REPORT-2026-09-28.md",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]

for p in FACES:
    t2 = probe_ts(stage(2, p), p)
    t3 = probe_ts(stage(3, p), p)
    if t3 and (not t2 or str(t3) >= str(t2)):
        side = ":3: (mine)"
    elif t2 and (not t3 or str(t2) > str(t3)):
        side = ":2: (origin)"
    else:
        side = "AMBIGUOUS"
    print("%-46s | :2: %s | :3: %s | take %s" % (p, t2, t3, side))
