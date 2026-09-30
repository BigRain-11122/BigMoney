# -*- coding: utf-8 -*-
# r463 bm-a: rebase conflict resolver -- compute_audit ts-distinct
# history union (r446 law; cap 201) + latest takes the newer ts.
# The 17 deterministic regen faces are taken via git checkout --theirs
# in the calling shell (not here).
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = "05c52b088"          # origin side (bm-c r259 S0b union)
REBASE_THEIRS = "6662925bc"  # our r463 (once-unioned) being replayed
PATH = "results/compute_audit.json"
CAP = 201


def blob(rev, path):
    r = subprocess.run(["git", "show", rev + ":" + path],
                       capture_output=True)
    if r.returncode != 0:
        raise SystemExit("blob fail " + rev + ":" + path)
    return r.stdout.decode("utf-8")


a = json.loads(blob(BASE, PATH))
b = json.loads(blob(REBASE_THEIRS, PATH))
seen = {}
for h in a.get("history", []) + b.get("history", []):
    seen[h.get("ts")] = h
merged = sorted(seen.values(), key=lambda h: h.get("ts", ""))
if len(merged) > CAP:
    merged = merged[-CAP:]
ta = a.get("latest", {}).get("ts", "")
tb = b.get("latest", {}).get("ts", "")
latest = b.get("latest") if tb >= ta else a.get("latest")
out = {"history": merged, "latest": latest}
with open(PATH, "w", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps(out, ensure_ascii=False, indent=1))
print("compute_audit union: hist", len(merged),
      "a-only+1 keys merged; latest ts", latest.get("ts"))
