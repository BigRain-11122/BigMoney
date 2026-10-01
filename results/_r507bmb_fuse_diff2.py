import json
import subprocess


def stage(n):
    return json.loads(subprocess.check_output(
        ["git", "show", f":{n}:results/crash_fuse.json"]))


base, ours, theirs = stage(1), stage(2), stage(3)
bs, os_, ts = base["sigs"], ours["sigs"], theirs["sigs"]
bc, oc, tc = base["cleared"], ours["cleared"], theirs["cleared"]

# which sig did ours drop
dropped = set(bs) - set(os_)
print("ours dropped sig:", dropped)
print("ours cleared entry:",
      json.dumps(oc.get("scripts/lowamp_p2.py|run,--nulls"), ensure_ascii=False))
# value-level changes vs base on common keys
for side, d in (("ours", os_), ("theirs", ts)):
    ch = [k for k in d if k in bs and d[k] != bs[k]]
    print(side, "value-changed vs base:", ch)
    for k in ch:
        print("  ", k, "->", json.dumps(d[k], ensure_ascii=False))
for side, d in (("ours", oc), ("theirs", tc)):
    ch = [k for k in d if k in bc and d[k] != bc[k]]
    print(side, "cleared value-changed vs base:", ch)
