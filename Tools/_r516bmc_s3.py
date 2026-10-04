# -*- coding: utf-8 -*-
"""r516 bm-c S3 probe: watermark red verdict + satengine status + pool census.
Read-only; prints compact summary AND mirrors it to results/_r516bmc_s3.txt
(UTF-8) so the session reads evidence via file, not huge JSON dumps."""
import json
import os
import subprocess
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE_NO_WINDOW = 0x08000000
out = []

d = json.load(open(os.path.join(ROOT, "results", "watermark_red.json"),
                   encoding="utf-8-sig"))
out.append("WM-RED %s" % d.get("red"))
out.append("WM-REASON %s" % str(d.get("reason"))[:180])
out.append("WM-NEXT-PICK %s" % str(d.get("next_pick"))[:180])
for k in ("ts", "updated", "asof"):
    if d.get(k):
        out.append("WM-TS %s %s" % (k, d.get(k)))
        break

r = subprocess.run([sys.executable, os.path.join(ROOT, "Tools",
                    "saturation_engine.py"), "status"],
                   capture_output=True, creationflags=CREATE_NO_WINDOW)
out.append("SATENGINE-RC %d" % r.returncode)
for l in (r.stdout or b"").decode("utf-8", "replace").strip().splitlines()[:12]:
    out.append("SAT> " + l)
err = (r.stderr or b"").decode("utf-8", "replace").strip()
if err:
    out.append("SAT-ERR " + err[:200])

pool = json.load(open(os.path.join(ROOT, "results", "runnable_pool.json"),
                     encoding="utf-8-sig"))
entries = pool.get("entries", pool) if isinstance(pool, dict) else pool
if isinstance(entries, dict):
    entries = list(entries.values())
c = Counter(str(e.get("status")) for e in entries)
out.append("POOL-CENSUS %d %s" % (len(entries), dict(c)))
ready = [str(e.get("id")) for e in entries if str(e.get("status")) == "ready"]
out.append("POOL-READY %s" % (ready[:8],))

txt = "\n".join(out)
print(txt)
with open(os.path.join(ROOT, "results", "_r516bmc_s3.txt"), "w",
          encoding="utf-8", newline="\n") as fh:
    fh.write(txt + "\n")
