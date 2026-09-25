# -*- coding: utf-8 -*-
"""r218 (bm-b) S0 stash-pop conflict resolve: results/autofill_state.json
mixed-dict+ledger recipe per Tools/skills/bigmoney-conflict-resolve/SKILL.md:
- launches: union both sides -> sort by ts -> cap 50 (rolling window, R215)
- last_tick: compare inner ts, WHOLE-dict assign, same-second tie -> HEAD (r140)
- isinstance(last_tick, dict) assertion (r203); CRLF mirror (bm-b r223);
  parse-verify before write-back (r185).
Sides here: HEAD = origin/bm-a R218 version; stashed = local watchdog tick 04:50.
"""
import json
import re
import subprocess
import sys

PATH = "results/autofill_state.json"

# Full clean sides from git index stages (r188 authoritative recipe, no marker parsing)
ours = json.loads(subprocess.run(["git", "show", ":2:" + PATH], capture_output=True).stdout.decode("utf-8"))
theirs = json.loads(subprocess.run(["git", "show", ":3:" + PATH], capture_output=True).stdout.decode("utf-8"))

# Probe line endings: mirror the WORKING-TREE producer form (stage3 = local
# watchdog side), per bm-b r223 law - repo converges to producer format, else
# next watchdog tick flips the whole file into a 561-line pseudo-diff.
producer_blob = subprocess.run(["git", "show", ":3:" + PATH], capture_output=True).stdout
crlf = producer_blob.count(b"\r\n") > 0
print("line-ending probe: producer/stage3 CRLF=%s" % crlf)

# launches: union by (ts, machine, entry, pid) identity, sort by ts, cap 50
seen = {}
for ent in ours.get("launches", []) + theirs.get("launches", []):
    key = (ent.get("ts"), ent.get("machine"), ent.get("entry"), ent.get("pid"), ent.get("shard"))
    if key not in seen:
        seen[key] = ent
union = sorted(seen.values(), key=lambda e: (e.get("ts") or "", e.get("machine") or ""))
cap = 50
union_capped = union[-cap:]  # keep the most recent 50 (rolling window)
print("launches: ours=%d theirs=%d union=%d capped=%d" % (len(ours.get("launches", [])), len(theirs.get("launches", [])), len(union), len(union_capped)))

# last_tick: compare inner ts; same-second tie -> HEAD (ours)
lt_ours, lt_theirs = ours.get("last_tick"), theirs.get("last_tick")
assert isinstance(lt_ours, dict) and isinstance(lt_theirs, dict), "last_tick not dict (r203 violation)"
ts_o = lt_ours.get("ts") or ""
ts_t = lt_theirs.get("ts") or ""
if ts_t > ts_o:
    last_tick = lt_theirs
elif ts_t < ts_o:
    last_tick = lt_ours
else:
    last_tick = lt_ours  # r140: same-second tie -> HEAD
print("last_tick: HEAD=%s stash=%s -> take %s" % (ts_o, ts_t, last_tick.get("ts")))
assert isinstance(last_tick, dict)

# Other keys (rebase_union_note etc.): keep HEAD side values (non-rolling annotation)
merged = dict(ours)
merged["launches"] = union_capped
merged["last_tick"] = last_tick

# Write back mirroring producer format: json.dumps indent=1, CRLF (r223)
out = json.dumps(merged, ensure_ascii=False, indent=1)
with open(PATH, "wb") as f:
    if crlf:
        f.write(out.replace("\n", "\r\n").encode("utf-8"))
    else:
        f.write(out.encode("utf-8"))

# Parse-verify after write-back (r185)
chk = json.load(open(PATH, encoding="utf-8"))
assert isinstance(chk["last_tick"], dict), "post-write last_tick not dict"
assert len(chk["launches"]) <= 50
print("WRITE-BACK OK: last_tick=%s launches=%d crlf=%s" % (chk["last_tick"]["ts"], len(chk["launches"]), crlf))
