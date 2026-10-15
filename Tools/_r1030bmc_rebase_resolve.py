# -*- coding: utf-8 -*-
"""r1030 bm-c rebase conflict resolver: 4 shared bookkeeping faces, newer-wins by internal ts.
Reads stage-2 (ours=origin base) and stage-3 (theirs=replayed commit) blobs via git,
picks the side with the newest internal timestamp (recursive scan for ts-like fields),
writes the winner to the worktree path, git-adds it. Zero manual transcription.
"""
import json, re, subprocess, sys

FILES = [
    "results/_attrition_guard_scan.json",
    "results/_r686bmb_d19_check.json",
    "results/token_usage.json",
    "results/update_status.json",
]

TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?")

def git(args):
    return subprocess.run(["git"] + args, capture_output=True).stdout

def best_ts(obj, best=(None,)):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and TS_RE.match(v):
                if best[0] is None or v > best[0]:
                    best = (v,)
            else:
                best = best_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = best_ts(v, best)
    elif isinstance(obj, str) and TS_RE.match(obj):
        if best[0] is None or obj > best[0]:
            best = (obj,)
    return best

def resolve(path):
    ours = git(["show", ":2:%s" % path])
    theirs = git(["show", ":3:%s" % path])
    if not ours and theirs:
        winner, side = theirs, "theirs"
    elif not theirs and ours:
        winner, side = ours, "ours"
    elif not ours and not theirs:
        subprocess.run(["git", "rm", "--", path])
        return "%s: both-empty rm" % path
    else:
        o_str = t_str = ""
        try:
            o_str = best_ts(json.loads(ours))[0] or ""
        except Exception:
            o_str = ""
        try:
            t_str = best_ts(json.loads(theirs))[0] or ""
        except Exception:
            t_str = ""
        side = "theirs" if t_str >= o_str else "ours"
        winner = theirs if side == "theirs" else ours
    with open(path, "wb") as f:
        f.write(winner)
    json.loads(open(path, "rb").read())
    subprocess.run(["git", "add", "--", path])
    return "%s: %s wins (ts %s)" % (path, side, best_ts(json.loads(winner))[0])

for p in FILES:
    print(resolve(p))
print("RESOLVE-DONE")
