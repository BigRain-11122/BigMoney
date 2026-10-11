# -*- coding: utf-8 -*-
# r914 helper: W216 burn completeness check (12/12) + engine queue state
import json, re, subprocess, sys, os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
r = subprocess.run(["python", os.path.join(REPO, "Tools", "saturation_engine.py"), "status"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
d = r.stdout
m = re.search(r'"wave": 216.*?"local_done": (\d+)', d, re.S)
remote = re.search(r'"wave": 216.*?"remote_done": (\d+)', d, re.S)
print("W216 local_done:", m.group(1) if m else "not-in-queue",
      "| remote_done:", remote.group(1) if remote else "?")
print("burns_active:", re.findall(r'"burns_active": \[[^\]]*\]', d)[:1])
print("queue_next:", re.findall(r'"queue_next": \[[^\]]*\]', d)[:1])
shd = os.path.join(REPO, "results", "p2cal_ext", "n1_w216")
files = sorted(os.listdir(shd)) if os.path.isdir(shd) else []
print("shard files:", len(files), files[:3], "...")
# validate shard coverage: shard-k-of-12 for k=0..11
expect = {f"shard-{k}-of-12.json" for k in range(12)}
print("coverage 12/12:", expect.issubset(set(files)))
