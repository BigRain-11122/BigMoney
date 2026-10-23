# -*- coding: utf-8 -*-
"""Compact bm-c N1 engine burn poller (read-only)."""
import json
import os
import subprocess
import sys

W = sys.argv[1] if len(sys.argv) > 1 else "303"
d = os.path.join("results", "p2cal_ext", "n1_w%s" % W)
files = sorted(os.listdir(d)) if os.path.isdir(d) else []
out = subprocess.run([sys.executable, "Tools/saturation_engine.py", "status"],
                     capture_output=True).stdout.decode("utf-8", "replace")
try:
    st = json.loads(out)
except Exception:
    print("status parse fail:", out[:200]); sys.exit(1)
act = [b for b in st.get("burns_active", []) if int(b.get("wave", -1)) == int(W)]
print("wave %s shard files=%d/12 active=%d hb_age=%.0fs" % (
    W, len(files), len(act), st.get("heartbeat_age_s") or -1))
print("shards:", sorted(os.path.basename(f) for f in files))