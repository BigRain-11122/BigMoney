# -*- coding: utf-8 -*-
"""r306 bm-b: probe UU conflict shapes (stage1 base / stage2 ours=rebase-base bm-a / stage3 theirs=replayed bm-b r305).
Per skill discipline: subprocess bytes, repr, no PS redirection. Read-only."""
import subprocess, json, sys

UU = [
    "docs/daily_report/REPORT-2026-09-27.json",
    "docs/daily_report/REPORT-2026-09-27.md",
    "results/daily_scorecard.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-24.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
]

def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    return r.stdout if r.returncode == 0 else None

TS_KEYS = ["generated", "generated_at", "updated_at", "ts", "as_of", "date", "cutoff",
           "evidence_cutoff", "data_cutoff", "last_update", "report_date", "trade_date", "run_ts"]

def shape(b):
    if b is None:
        return "NO-BLOB"
    try:
        j = json.loads(b.decode("utf-8"))
    except Exception as e:
        # non-JSON: show head lines + length
        txt = b.decode("utf-8", "replace")
        lines = txt.splitlines()
        return "RAW len=%d lines=%d head=%r" % (len(b), len(lines), lines[:3])
    if isinstance(j, dict):
        out = {}
        for k in TS_KEYS:
            if k in j:
                out[k] = repr(j[k])[:60]
        lens = {}
        for k, v in j.items():
            if isinstance(v, list):
                lens[k] = "list:%d" % len(v)
            elif isinstance(v, dict):
                lens[k] = "dict:%d" % len(v)
        return "dict keys=%d ts_fields=%s lens=%s" % (len(j), json.dumps(out, ensure_ascii=False)[:200] if out else "{}", json.dumps(lens)[:300])
    return type(j).__name__

for p in UU:
    print("=" * 10, p)
    for st, name in ((1, "base"), (2, "ours(base=bm-a)"), (3, "theirs(bm-b r305)")):
        b = blob(st, p)
        print("  stage%d %-18s %s" % (st, name, shape(b)))
print("PROBE-DONE")
