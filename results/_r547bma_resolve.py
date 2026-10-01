# -*- coding: utf-8 -*-
"""r547 bm-a rebase conflict resolver: results/pool_core_samples.jsonl
append-log union (classify_conflicts: append-log, r188/r217 law).

:2: = origin side (rebase ours = new base), :3: = local side (the commit
being replayed = mine). Union = base(:2:) line order preserved + :3:-only
lines appended (minimal append-union, NO global sort -- r524 law). Exact
duplicate lines deduped. Parse-verify every line (r185). Byte-shape
mirror of the base blob line ending (r223/r234).
"""
import json
import subprocess
import sys

PATH = "results/pool_core_samples.jsonl"


def stage(which):
    out = subprocess.check_output(
        ["git", "show", f":{which}:{PATH}"])
    return out.decode("utf-8")


def lines_of(text):
    return [ln for ln in text.split("\n") if ln.strip()]


a = stage(2)   # origin side
b = stage(3)   # local (mine) side
la, lb = lines_of(a), lines_of(b)
seen = set(la)
union = list(la)
added = 0
for ln in lb:
    if ln not in seen:
        union.append(ln)
        seen.add(ln)
        added += 1
print(f"origin lines={len(la)} local lines={len(lb)} "
      f"union={len(union)} appended={added} "
      f"dupes-dropped={len(lb) - added}")

# parse-verify every line (r185)
for ln in union:
    json.loads(ln)

# byte-shape mirror: base blob line ending
crlf = a.count("\r\n") > (a.count("\n") - a.count("\r\n"))
print("base blob CRLF:", crlf)
text = ("\r\n" if crlf else "\n").join(union)
if a.endswith("\r\n") or a.endswith("\n"):
    text += "\r\n" if crlf else "\n"
with open(PATH, "w", encoding="utf-8", newline="") as fh:
    fh.write(text)
# re-verify from disk
back = [ln for ln in open(PATH, encoding="utf-8").read().splitlines()
        if ln.strip()]
assert len(back) == len(union), (len(back), len(union))
for ln in back:
    json.loads(ln)
print("resolve written + parse-verified:", len(back), "lines")
