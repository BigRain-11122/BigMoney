"""r413 stuck-rebase resurrect: daily_scorecard.json snapshot take-new (non-ALL_FACES face).

Probes STAGED blobs (:2: origin side, :3: r412 replay side) per hardened probe laws
(r100 key-normalize + ^20\\d{2}- value shape; R350 wall-clock values require
time-of-day, key-EXCLUDE lists forbidden). Whole-doc take-new, parse-verify before write.
"""
import json
import re
import subprocess
import sys

PATH = "results/daily_scorecard.json"
TS_SHAPE = re.compile(r"^20\d{2}-")
WALLCLOCK = re.compile(r"[T ]\d{2}:\d{2}")


def stage_blob(stage):
    b = subprocess.run(["git", "show", f":{stage}:{PATH}"], capture_output=True).stdout
    return json.loads(b)  # bytes decode, no PS redirect (r209)


def wallclock_max(o, best=""):
    """Deep-scan: only values that are timestamp-shaped AND carry time-of-day feed the max."""
    if isinstance(o, dict):
        vals = o.values()
    elif isinstance(o, list):
        vals = o
    else:
        return best
    for v in vals:
        if isinstance(v, str) and TS_SHAPE.match(v) and WALLCLOCK.search(v) and v > best:
            best = v
        best = wallclock_max(v, best)
    return best


s2, s3 = stage_blob("2"), stage_blob("3")
t2, t3 = wallclock_max(s2), wallclock_max(s3)
print(f"probe :2: max wall-clock = {t2}")
print(f"probe :3: max wall-clock = {t3}")
if not (t2 or t3):
    sys.exit("FAIL: no wall-clock ts in either staged blob -- classify manually (fail-closed)")
winner, side = (s3, ":3: replay-side") if t3 > t2 else (s2, ":2: base-side")
if t3 == t2:
    sys.exit("FAIL: tie -- classify manually (fail-closed)")

# whole-doc take-new: re-serialize the WINNING PARSED blob (not working tree), parse-verify roundtrip
out = json.dumps(winner, ensure_ascii=False, indent=2)
json.loads(out)
with open(PATH, "w", encoding="utf-8", newline="\n") as f:
    f.write(out)
json.loads(open(PATH, encoding="utf-8").read())  # r185 parse-verify after write
print(f"take-new {side} -> wrote {PATH} (parse-verified)")
