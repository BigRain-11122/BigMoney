# r707 bm-a merge probe: dump top-level timestamp-ish fields for both sides of each UU face
import subprocess, json

FACES = [
    "docs/daily_report/REPORT-2026-10-05.json",
    "docs/live_usage/LIVE-2026-10-05.json",
    "results/daily_scorecard.json",
    "results/dashboard_status.json",
    "results/update_status.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/regime_state.json",
    "results/compute_audit.json",
    "results/_attrition_guard_scan.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-30.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/token_usage.json",
    "results/crash_fuse.json",
    "results/runnable_pool.json",
]

TS_KEYS = ["generated_at", "updated", "updated_at", "ts", "now", "as_of", "generated",
           "time", "cutoff", "scan_ts", "checked_at", "last_run", "run_ts", "when",
           "last_update", "date", "scan_at", "at", "stamp", "launched_at", "epoch"]

def scalars(obj, depth=0):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and len(v) >= 8 and any(c.isdigit() for c in v):
                out[k] = v[:40]
            elif isinstance(v, (int, float)) and not isinstance(v, bool) and depth == 0:
                out[k] = v
            elif isinstance(v, dict) and depth == 0 and k in ("latest", "state", "status", "meta"):
                out.update({k + "." + kk: str(vv)[:40] for kk, vv in v.items()
                            if isinstance(vv, str) and len(str(vv)) >= 8 and any(c.isdigit() for c in str(vv))})
    return out

for f in FACES:
    try:
        o = json.loads(subprocess.run(["git", "show", f":2:{f}"], capture_output=True).stdout.decode("utf-8"))
    except Exception as ex:
        print(f, "OURS parse fail:", ex.__class__.__name__); continue
    try:
        t = json.loads(subprocess.run(["git", "show", f":3:{f}"], capture_output=True).stdout.decode("utf-8"))
    except Exception as ex:
        print(f, "THEIRS parse fail:", ex.__class__.__name__); continue
    so, st = scalars(o), scalars(t)
    keys = [k for k in TS_KEYS if k in so or k in st] + [k for k in so if k not in TS_KEYS][:3]
    seen = set()
    parts = []
    for k in keys:
        if k in seen: continue
        seen.add(k)
        parts.append(f"{k}: O={so.get(k)!r} T={st.get(k)!r}")
    print(f, " || ".join(parts[:6]))
