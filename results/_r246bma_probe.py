# -*- coding: utf-8 -*-
"""R246 bm-a rebase-replay conflict probe: byte-equality + ts-key census for the
25-file UU batch (11 classified + 14 UNKNOWN). Rebase face: :2 = origin/bm-b side
(HEAD during replay), :3 = my replayed commit side. Read-only, prints facts."""
import json
import subprocess
import sys


def blob(rev):
    p = subprocess.run(["git", "show", rev], capture_output=True)
    if p.returncode != 0:
        return None
    return p.stdout


FILES = [
    "results/compute_audit.json", "results/dashboard_status.js",
    "results/dashboard_status.json", "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json", "results/heat_update_status.json",
    "results/lhb_update_status.json", "results/regime_state.json",
    "results/token_usage.json", "results/update_status.json",
    "results/x2_watch_log.jsonl", "docs/daily_report/REPORT-2026-09-26.json",
    "docs/daily_report/REPORT-2026-09-26.md", "results/daily_scorecard.json",
    "results/paper/COMPOSITE-CE-01_paper.json", "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json", "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json", "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-24.json", "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json", "results/prospect_promotion/_summary.json",
    "results/t35_open_fill_verify.json",
]
TS_KEYS = ["ts", "updated", "generated_at", "generated", "as_of", "updated_at",
           "last_attempt", "written_at", "time"]
out = {}
for f in FILES:
    a = blob(f":2:{f}")   # origin/bm-b side
    b = blob(f":3:{f}")    # my replayed side
    rec = {"equal": a == b, "len2": len(a or b""), "len3": len(b or b"")}
    for tag, data in (("s2", a), ("s3", b)):
        if f.endswith(".json") and data:
            try:
                j = json.loads(data)
                if isinstance(j, dict):
                    hits = {k: j[k] for k in TS_KEYS if isinstance(j.get(k), (str, int, float))}
                    if hits:
                        rec[tag + "_ts"] = hits
                    # nested meta.generated_at
                    meta = j.get("meta")
                    if isinstance(meta, dict):
                        rec[tag + "_meta"] = {k: meta[k] for k in TS_KEYS
                                              if isinstance(meta.get(k), (str, int, float))}
            except Exception as e:
                rec[tag + "_parse"] = f"ERR {e}"
    out[f] = rec
print(json.dumps(out, ensure_ascii=False, indent=1))
