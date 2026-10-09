# -*- coding: utf-8 -*-
"""r914 bm-a rebase conflict probe: ts faces on 5 shared regen files
(worktree dirty side vs origin/main side)."""
import io
import json
import subprocess

GIT = r"C:\Program Files\Git\cmd\git.exe"
G = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
FACES = ["results/compute_audit.json", "results/regime_state.json",
         "results/scorecard_v1.json", "results/strategy_scorecard.json",
         "results/update_status.json"]


def show_origin(path):
    b = subprocess.run([GIT, "-C", G, "show", "origin/main:" + path],
                       capture_output=True).stdout
    return json.loads(b.decode("utf-8"))


def probe(obj, depth=0):
    """Pull a few ts-ish scalar fields for comparison."""
    out = {}
    if isinstance(obj, dict):
        for k in ("ts", "generated", "generated_at", "cutoff",
                  "last_run", "updated", "machine", "host"):
            if k in obj and not isinstance(obj[k], (dict, list)):
                out[k] = obj[k]
    return out


for f in FACES:
    try:
        mine = json.load(io.open(f, encoding="utf-8"))
    except Exception as e:
        print(f, "MINE-READ-ERR", e)
        continue
    try:
        theirs = show_origin(f)
    except Exception as e:
        print(f, "ORIGIN-READ-ERR", str(e)[:60])
        continue
    pm, pt = probe(mine), probe(theirs)
    # compute_audit rolling history: count entries + max ts
    extra = ""
    if f.endswith("compute_audit.json") and isinstance(mine, list):
        tsm = max((e.get("ts", "") for e in mine), default="")
        tst = max((e.get("ts", "") for e in theirs), default="")
        extra = " | history mine=%d theirs=%d max_ts mine=%s theirs=%s" % (
            len(mine), len(theirs), tsm, tst)
    print(f)
    print("   mine :", pm, extra.split("|")[1] if "|" in extra else "")
    if "|" in extra:
        print("   extra:", extra)
    print("   orig :", pt)
