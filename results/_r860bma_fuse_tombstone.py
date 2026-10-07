"""r860 bm-a: manual tombstone of fused W16-JUDGE sig (r824 W14-screen
precedent, same bug class).

Root cause: enrollment passed --runner-args as a comma-joined string;
submit stored a 1-element list; launcher passed one argv element ->
argparse instant-exit (honest zero-burn, checkpoint untouched). Pool
entry runner_args FIXED in both faces r860 (5-element list). Runner
code never at fault (sha 9331a9dfb72d37e3 unchanged). Move sigs ->
cleared with documented reason per r824 tombstone law.
"""
import json
import datetime

FUSE = r"results/crash_fuse.json"
SIG = "scripts/trial_labor_w16.py|judge,--shard,0,--shards,1"

f = json.load(open(FUSE, encoding="utf-8"))
sigs = f.setdefault("sigs", {})
cleared = f.setdefault("cleared", {})
assert SIG in sigs, "fused sig present"
reg = sigs.pop(SIG)
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
cleared[SIG] = {
    "crashes": int(reg.get("count", 1)),
    "old_code_sha256": reg.get("code_sha256"),
    "cleared_by": "bm-a",
    "cleared_ts": now,
    "reason": ("r860 bm-a manual tombstone: crash root-cause = enrollment "
               "runner_args comma-string (1-element list -> single argv -> "
               "argparse instant-exit, honest zero-burn, checkpoint "
               "untouched); pool entry runner_args FIXED both faces r860 "
               "(5-element list); runner code never at fault (sha "
               "9331a9dfb72d37e3 unchanged); r824 W14-screen tombstone "
               "precedent"),
    "entry": reg.get("entry"),
    "shard": reg.get("shard"),
}
tmp = FUSE + ".tmp"
with open(tmp, "w", encoding="utf-8") as fh:
    json.dump(f, fh, ensure_ascii=False, indent=1)
import os
os.replace(tmp, FUSE)

# round-trip + post-write gates
f2 = json.load(open(FUSE, encoding="utf-8"))
assert SIG not in f2.get("sigs", {})
assert SIG in f2.get("cleared", {})
print("TOMBSTONED:", SIG)
print("cleared reason ok | sigs now:", len(f2.get("sigs", {})),
      "| cleared now:", len(f2.get("cleared", {})))
