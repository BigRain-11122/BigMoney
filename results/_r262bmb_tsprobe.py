# -*- coding: utf-8 -*-
"""R262 bm-b: per-file ts-key probe for the snapshot family (fail-closed)."""
import json
import subprocess


def stage(n, path):
    return subprocess.run(["git", "show", f":{n}:{path}"],
                          capture_output=True).stdout


FILES = ["results/dashboard_status.json", "results/compute_audit.json",
         "results/fundamental_b_layer_filter.json",
         "results/futures_update_status.json",
         "results/heat_update_status.json",
         "results/lhb_update_status.json", "results/token_usage.json",
         "results/update_status.json"]
for p in FILES:
    for n in (2, 3):
        try:
            d = json.loads(stage(n, p).decode("utf-8-sig"))
        except Exception as e:
            print(p, f":{n}", "PARSE FAIL", e)
            continue
        tsish = {k: v for k, v in d.items()
                 if isinstance(v, str) and any(
                     t in k.lower() for t in ("ts", "time", "date", "updated",
                                              "generated", "as_of"))}
        print(p, f":{n}", "keys:", list(d.keys())[:8], "| tsish:", tsish)
