"""r724 bm-a merge-conflict per-face probe: read index stages :2: (ours) / :3:
(theirs) blobs via python subprocess bytes (r710-A law: no PS redirection),
surface decision-relevant ts fields per face. Read-only."""
import json
import subprocess
import sys

UU = [
    "docs/daily_report/REPORT-2026-10-05.json",
    "docs/daily_report/REPORT-2026-10-05.md",
    "docs/live_usage/LIVE-2026-10-05.json",
    "docs/live_usage/LIVE-2026-10-05.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]


def blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0 or not r.stdout:
        return None
    return r.stdout


def try_json(b):
    if b is None:
        return None
    try:
        return json.loads(b.decode("utf-8"))
    except Exception:
        return None


def probe_ts(obj, depth=0):
    """Surface plausible top-level timestamp fields."""
    if not isinstance(obj, dict):
        return {}
    out = {}
    for k, v in obj.items():
        if isinstance(v, str) and len(v) >= 8 and ("2026-" in v or "T" in v[:4] or v[0].isdigit()):
            if any(t in k.lower() for t in ("ts", "time", "at", "date", "generated", "updated", "asof", "as_of")):
                out[k] = v[:25]
        elif isinstance(v, (int, float)) and any(t in k.lower() for t in ("epoch",)):
            out[k] = v
    return out


for path in UU:
    o = try_json(blob(2, path))
    t = try_json(blob(3, path))
    print("==", path)
    if o is None or t is None:
        # non-json or missing side: report raw head bytes
        for stage, name in ((2, "ours"), (3, "theirs")):
            b = blob(stage, path)
            head = (ascii(b[:160].decode("utf-8", "replace")) if b else "MISSING")
            print(f"   {name}: {head}")
        continue
    ot, tt = probe_ts(o), probe_ts(t)
    print("   ours-ts  :", json.dumps(ot, ensure_ascii=False)[:180])
    print("   theirs-ts:", json.dumps(tt, ensure_ascii=False)[:180])
    ok = list(o.keys())[:6]
    print("   ours-keys:", ok)
