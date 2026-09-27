# -*- coding: utf-8 -*-
"""r334 bm-b ad-hoc: verify regime_state history union zero-loss (2+2->1 anomaly)."""
import json, subprocess, io

def show(stage):
    return subprocess.run(["git", "show", f"{stage}:results/regime_state.json"],
                          capture_output=True).stdout.decode("utf-8")

o = json.loads(show(":2"))
t = json.loads(show(":3"))
w = json.load(io.open("results/regime_state.json", encoding="utf-8"))
print("ours history  :", json.dumps(o.get("history"), ensure_ascii=False))
print("theirs history:", json.dumps(t.get("history"), ensure_ascii=False))
print("resolved      :", json.dumps(w.get("history"), ensure_ascii=False))
print("ours keys:", sorted(o.keys()))
print("byte-equal ours==theirs(history):", o.get("history") == t.get("history"))
