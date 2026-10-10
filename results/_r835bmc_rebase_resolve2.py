# -*- coding: utf-8 -*-
"""r835 rebase pick-2 resolver: satengine faces ts-newer-wins."""
import subprocess, re

def stage(side, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (side, path)], capture_output=True)
    return r.stdout.decode("utf-8", "replace")

def ts_of(text):
    m = re.search(r'"ts"\s*:\s*"([^"]+)"', text)
    return m.group(1) if m else "?"

for fp in ["results/saturation_engine/face_bm-c.json", "results/saturation_engine_state.bm-c.json"]:
    o = stage(2, fp)
    t = stage(3, fp)
    to, tt = ts_of(o), ts_of(t)
    pick = t if tt >= to else o
    open(fp, "w", encoding="utf-8", newline="").write(pick)
    print("%s -> remote ts=%s mine ts=%s pick=%s" % (fp, to, tt, "MINE" if tt >= to else "REMOTE"))
