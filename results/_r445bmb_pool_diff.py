# -*- coding: utf-8 -*-
"""_r445bmb_pool_diff.py -- inspect the two sides of the runnable_pool
conflict (rebase stages 2/3) before writing the union resolver."""
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def blob(stage):
    raw = subprocess.run(
        ["git", "show", ":%d:results/runnable_pool.json" % stage],
        capture_output=True).stdout
    return json.loads(raw.decode("utf-8"))


def face(pool):
    if isinstance(pool, dict):
        return pool.get("entries", pool)
    return pool


base = face(blob(2))   # rebase: stage2 = new base (origin/main tip)
mine = face(blob(3))   # stage3 = my commit being replayed
bi = {e.get("id"): e for e in base}
mi = {e.get("id"): e for e in mine}
print("base entries", len(bi), "| mine entries", len(mi))
print("ids only in base:", sorted(set(bi) - set(mi)))
print("ids only in mine:", sorted(set(mi) - set(bi)))
print("order-equal:", [e.get("id") for e in base] ==
      [e.get("id") for e in mine])
for k in sorted(set(bi) & set(mi)):
    if json.dumps(bi[k], sort_keys=True) != json.dumps(mi[k], sort_keys=True):
        bks = {kk: bi[k].get(kk) for kk in ("status", "state", "claimed_by",
                                            "done_at", "updated")}
        mks = {kk: mi[k].get(kk) for kk in ("status", "state", "claimed_by",
                                            "done_at", "updated")}
        print("DIFF id", k, "base:", bks, "| mine:", mks)
# also show top-level dict keys if wrapped
raw2 = subprocess.run(["git", "show", ":2:results/runnable_pool.json"],
                      capture_output=True).stdout
raw3 = subprocess.run(["git", "show", ":3:results/runnable_pool.json"],
                      capture_output=True).stdout
d2, d3 = json.loads(raw2.decode("utf-8")), json.loads(raw3.decode("utf-8"))
print("toplevel keys base:", list(d2.keys()) if isinstance(d2, dict) else
      "LIST")
print("toplevel keys mine:", list(d3.keys()) if isinstance(d3, dict) else
      "LIST")
if isinstance(d2, dict):
    for k in d2:
        if k != "entries" and json.dumps(d2.get(k), sort_keys=True) != \
                json.dumps(d3.get(k), sort_keys=True):
            print("META-DIFF", k, "base:", repr(d2.get(k))[:200], "mine:",
                  repr(d3.get(k))[:200])
