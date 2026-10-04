"""r668 bm-a UU ts-key census: probe both sides' timestamp-ish top/deep keys
for the 15 out-of-registry faces (r656 dual-side raw review discipline)."""
import json
import subprocess

FACES = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-latest.json",
    "results/_attrition_guard_scan.json",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
]
KEYS = ["generated_at", "generated", "ts", "updated", "updated_at",
        "asof", "cutoff", "day", "last_run"]


def side(ref, path):
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True)
    return json.loads(r.stdout) if r.returncode == 0 else None


for p in FACES:
    a, b = side("HEAD", p), side("MERGE_HEAD", p)
    row = {"face": p}
    for ref, d in (("HEAD", a), ("MERGE_HEAD", b)):
        found = {}
        for k in KEYS:
            if isinstance(d, dict) and k in d:
                found[k] = str(d[k])[:40]
        if not found and isinstance(d, dict):
            for k0 in list(d)[:6]:
                v = d[k0]
                if isinstance(v, str) and len(v) >= 8 and v[:2] == "20":
                    found[f"top:{k0}"] = v[:40]
        row[ref] = found if found else {f"top{ i }": str(list(d)[:i + 1])[:0] or list(d)[:5] for i in [0]} if isinstance(d, dict) else str(d)[:60]
    print(json.dumps(row, ensure_ascii=False)[:420])
