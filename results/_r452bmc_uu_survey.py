"""r452 bm-c merge-conflict UU survey probe (read-only stage-2/3 inspection)."""
import json
import subprocess

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


def show(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    return r.stdout


def probe(path):
    o = show(2, path)
    t = show(3, path)
    info = {"path": path, "ours_b": len(o), "theirs_b": len(t)}
    for tag, raw in (("ours", o), ("theirs", t)):
        try:
            d = json.loads(raw)
            if isinstance(d, dict):
                keys = list(d.keys())
                info[tag] = "dict keys=" + ",".join(keys[:8])
                for tsf in ("ts", "generated_at", "generated", "updated", "asof", "time", "now"):
                    if tsf in d:
                        info[tag + "_ts"] = f"{tsf}={d[tsf]}"
                        break
                if path == "results/compute_audit.json" and "history" in d:
                    info[tag + "_hist_len"] = len(d["history"]) if isinstance(d["history"], list) else "?"
                if "machine" in d:
                    info[tag + "_machine"] = d["machine"]
            elif isinstance(d, list):
                info[tag] = f"list len={len(d)}"
        except Exception as e:
            info[tag] = "non-json (" + type(e).__name__ + ")"
    return info


for p in UU:
    i = probe(p)
    print(json.dumps(i, ensure_ascii=False))
