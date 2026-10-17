# -*- coding: utf-8 -*-
# r1042: watermark_red.json UU resolver (r1028/r1029 newer-wins recipe, shared probe face)
import json, subprocess, sys

def stage(n):
    out = subprocess.run(["git", "show", f":{n}:results/watermark_red.json"], capture_output=True)
    if out.returncode != 0:
        print("STAGE_MISSING", n, out.stderr.decode("utf-8", "replace")[:200]); sys.exit(2)
    return out.stdout

try:
    ours = json.loads(stage(2).decode("utf-8"))    # upstream (origin) side
    theirs = json.loads(stage(3).decode("utf-8"))  # my replayed commit side
except Exception as e:
    print("PARSE_FAIL", e); sys.exit(2)

def ts_of(d):
    for k in ("ts", "updated", "updated_at", "now", "probed_at"):
        v = d.get(k)
        if isinstance(v, str) and "T" in v:
            return v
    return ""

o_ts, t_ts = ts_of(ours), ts_of(theirs)
winner = "theirs" if t_ts >= o_ts else "ours"
data = theirs if winner == "theirs" else ours
raw = stage(3) if winner == "theirs" else stage(2)
with open("results/watermark_red.json", "wb") as f:
    f.write(raw)
print("WM_UU_RESOLVED winner=", winner, "ours_ts=", o_ts, "theirs_ts=", t_ts,
      "red=", data.get("red"), "lane=", str(data.get("lane"))[:60])
