# -*- coding: utf-8 -*-
"""r679 bm-a merge-conflict side inspector (subprocess raw bytes, zero PS pipe).
Shows per-face top-level ts-ish fields both sides for resolution routing."""
import json
import subprocess
import sys

UU = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/token_usage.json",
    "results/update_status.json",
]

TS_KEYS = ["ts", "updated", "generated", "generated_at", "last_run", "timestamp",
           "asof", "as_of", "clock", "date", "checked_at", "verified_at"]


def show(ref, path):
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout


def ts_candidates(obj, depth=0):
    """Top-2-level scalar ts-ish values."""
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (str, int, float)) and any(t in k.lower() for t in
                    ("ts", "time", "date", "updated", "generated", "run", "clock")):
                out[k] = v
            elif isinstance(v, dict) and depth < 1:
                for k2, v2 in v.items():
                    if isinstance(v2, (str, int, float)) and any(
                            t in k2.lower() for t in ("ts", "time", "updated", "generated", "run")):
                        out[f"{k}.{k2}"] = v2
    return out


for p in UU:
    o_raw = show("HEAD", p)
    t_raw = show("MERGE_HEAD", p)
    line = [p.split("/")[-1]]
    for tag, raw in (("ours", o_raw), ("theirs", t_raw)):
        if raw is None:
            line.append(f"{tag}=ABSENT")
            continue
        try:
            d = json.loads(raw.decode("utf-8"))
            cands = ts_candidates(d)
            s = " ".join(f"{k}={v}" for k, v in list(cands.items())[:4])
            keys = list(d.keys())[:6] if isinstance(d, dict) else type(d).__name__
            line.append(f"{tag}: keys={keys} {s}")
        except Exception:
            txt = raw.decode("utf-8", "replace")
            import re
            m = re.findall(r"20\d\d-\d\d-\d\d[T ]\d\d:\d\d(:\d\d)?", txt[:2000])
            line.append(f"{tag}: non-json ts_hits={m[:3]} len={len(raw)}")
    print(" | ".join(line))
