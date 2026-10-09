# -*- coding: utf-8 -*-
"""compute_audit.json face probe: history lengths + latest ts both stages."""
import json
import subprocess


def blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    return json.loads(r.stdout) if r.returncode == 0 else None


f = "results/compute_audit.json"
for st in (2, 3):
    o = blob(st, f)
    h = o.get("history", [])
    lat = o.get("latest", {})
    print("stage", st, "| history len:", len(h),
          "| last hist ts:", str(h[-1].get("ts") if h else None)[:30],
          "| latest ts:", str(lat.get("ts"))[:30],
          "| latest machine:", lat.get("machine"))
