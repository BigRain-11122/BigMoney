# -*- coding: utf-8 -*-
"""r412 bm-b rebase conflict probe (batch 2): ts both sides per file."""
import json
import subprocess

ROOT = r"E:\Fluxgroup\FluxGroup\quant\bigmoney"


def blob(stage, path):
    out = subprocess.run(["git", "show", f":{stage}:{path}"], cwd=ROOT,
                         capture_output=True)
    return out.stdout.decode("utf-8-sig")


def deepts(d):
    best = ""
    stack = [d]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            for k, v in cur.items():
                if isinstance(v, str) and v[:4] == "2026" and len(v) > 10 \
                        and (" " in v or "T" in v):
                    if v > best:
                        best = v
                elif isinstance(v, (dict, list)):
                    stack.append(v)
        elif isinstance(cur, list):
            stack.extend(x for x in cur if isinstance(x, (dict, list)))
    return best


FILES = [
    "docs/daily_report/REPORT-2026-09-29.json",
    "docs/live_usage/LIVE-2026-09-29.json",
    "docs/live_usage/LIVE-latest.json",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
    "results/regime_state.json",
]

for p in FILES:
    try:
        t2 = deepts(json.loads(blob(2, p)))
        t3 = deepts(json.loads(blob(3, p)))
        side = "s3" if t3 > t2 else "s2"
        print(f"{p}: s2={t2} s3={t3} -> take {side}")
    except Exception as ex:
        print(f"{p}: ERR {ex}")

a2 = json.loads(blob(2, "results/compute_audit.json"))
a3 = json.loads(blob(3, "results/compute_audit.json"))
print("audit: s2 hist", len(a2.get("history", [])),
      "s3 hist", len(a3.get("history", [])),
      "| latest s2", a2["latest"]["ts"], "s3", a3["latest"]["ts"])
r2 = json.loads(blob(2, "results/regime_state.json"))
r3 = json.loads(blob(3, "results/regime_state.json"))
print("regime: s2 hist", len(r2.get("history", [])),
      "s3 hist", len(r3.get("history", [])),
      "| updated s2", r2.get("updated"), "s3", r3.get("updated"))
