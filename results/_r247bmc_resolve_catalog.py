# -*- coding: utf-8 -*-
"""_r247bmc_resolve_catalog.py -- union-resolve the stash-pop UU on
Tools/fill_ladder_catalog.json per r444/r442 blob-recipe law (no
conflict-marker file parsing): :2 = post-rebase HEAD side (bm-b r444
changes), :3 = stash side (my SLOT-5 append). Union = HEAD side
authoritative + SLOT-5 entry + SLOT-5 version note appended."""
import json
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PATH = "Tools/fill_ladder_catalog.json"


def show(rev):
    r = subprocess.run(["git", "show", rev + ":" + PATH],
                       capture_output=True)
    if r.returncode != 0:
        print("git show failed for", rev, r.stderr.decode("utf-8", "replace"))
        raise SystemExit(2)
    return r.stdout.decode("utf-8")


d2 = json.loads(show(":2"))
d3 = json.loads(show(":3"))

ids2 = [e.get("id") for e in d2["entries"]]
extra = [e for e in d3["entries"] if e.get("id") not in ids2]
d2["entries"].extend(extra)

if "SLOT-5 berth (bm-c r247" not in (d2.get("version") or ""):
    d2["version"] = (d2.get("version") or "") + (
        " + SLOT-5 berth (bm-c r247: INNOVATION-QUOTA-SLOT-5 entry added "
        "per berth; zoo #86 icu_ma_timing, prereg BERTH "
        "research/INNOVATION_QUOTA_W5_PREREG.md)")

with open(PATH, "w", encoding="utf-8", newline="\n") as f:
    json.dump(d2, f, ensure_ascii=False, indent=1)

# verify
with open(PATH, encoding="utf-8") as f:
    dv = json.load(f)
vids = [e.get("id") for e in dv["entries"]]
assert "INNOVATION-QUOTA-SLOT-5" in vids, "SLOT-5 missing after union"
print("union ok: entries=%d added_from_stash=%s last=%s" % (
    len(dv["entries"]), [e.get("id") for e in extra], vids[-1]))
