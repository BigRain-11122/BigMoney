# -*- coding: utf-8 -*-
"""token_usage.json structure probe (per-machine union face check)."""
import json
import subprocess


def blob(stage):
    r = subprocess.run(["git", "show", f":{stage}:results/token_usage.json"],
                       capture_output=True)
    return json.loads(r.stdout) if r.returncode == 0 else None


for st, who in ((2, "bm-c"), (3, "bm-a")):
    o = blob(st)
    m = o.get("machines", {})
    print(who, "| machines keys:", list(m.keys()))
    for k, v in m.items():
        print("  ", k, "->", json.dumps(v, ensure_ascii=False)[:140])
    print("  totals:", o.get("total_report_tokens_est"),
          o.get("total_state_tokens_est"), "| generated:", o.get("generated"))
