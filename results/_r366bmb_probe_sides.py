import subprocess
import re

FILES = [
    "results/compute_audit.json",
    "results/regime_state.json",
    "results/dashboard_status.json",
    "results/dashboard_status.js",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/token_usage.json",
    "results/update_status.json",
    "docs/daily_report/REPORT-2026-09-28.json",
    "results/daily_scorecard.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/t35_open_fill_verify.json",
]


def blob(stage, path):
    return subprocess.run(["git", "show", f":{stage}:{path}"],
                           capture_output=True).stdout


for p in FILES:
    a, b = blob("2", p), blob("3", p)
    same = "IDENTICAL" if a == b else "DIFFER"
    tss = []
    for s in (a, b):
        m = re.findall(rb"2026-09-2[78]T?\s?\d?\d?:?\d?\d?:?\d?\d?", s)
        t = s.decode("utf-8", errors="replace")
        m2 = re.findall(r'"(ts|generated|updated|asof|last_seen)"\s*:\s*'
                       r'("?[^",}]+"?)', t)[:3]
        tss.append((len(m), m[:3]))
    print(f"{p}: {same} o={len(a)}B m={len(b)}B "
          f"ts_hits(origin)={tss[0]} ts_hits(mine)={tss[1]}")
