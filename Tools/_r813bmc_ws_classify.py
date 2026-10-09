# -*- coding: utf-8 -*-
"""r813 bm-c C-03 rectification classifier: for each of the 5 modified faces
in the group tree, compare working-tree bytes vs origin/main blob bytes, and
read mtime (active-writer check). Verdict per face:
  MATCH-ORIGIN -> lossless (checkout/reset safe, content already upstream)
  LOCAL-ONLY    -> needs union/commit handling BEFORE any reset (NEVER reset)
Also re-checks the 3 staged fleet-link faces (expected MATCH-ORIGIN) and
confirms local HEAD has zero unique commits vs origin/main (pure-behind)."""
import subprocess
import io
import os
import time

CNW = 0x08000000
G = "K:/Fluxgroup/FluxGroup"
R = "K:/Fluxgroup/FluxGroup/quant/bigmoney"
out = io.open(os.path.join(R, "results", "_r813bmc_ws_classify.txt"), "w",
              encoding="utf-8")
w = out.write


def gb(args, t=60):
    r = subprocess.run(["git", "-C", G] + args, capture_output=True,
                       creationflags=CNW, timeout=t)
    return r.returncode, r.stdout, r.stderr


rc, o, e = gb(["rev-list", "--left-right", "--count", "HEAD...origin/main"])
w("ahead-behind(local left, origin right): %s\n" % o.decode("utf-8", "replace").strip())

faces = ["Tools/fleet-nodes.json", "gaming/CODELY.md", "quant/CODELY.md",
         "gaming/.codely-cli/settings.json", "quant/.codely-cli/settings.json",
         "Tools/fleet-link.ps1", "Tools/register-fleet-link.ps1",
         "Tools/fleet-poke-worker.ps1"]
now = time.time()
for f in faces:
    p = os.path.join(G, f.replace("/", "\\"))
    try:
        disk = open(p, "rb").read()
    except Exception as ex:
        w("%s READ-ERR %s\n" % (f, ex))
        continue
    rc, org, _ = gb(["show", "origin/main:" + f])
    if rc != 0:
        w("%s NO-ORIGIN-BLOB rc=%d\n" % (f, rc))
        continue
    mtime = os.path.getmtime(p)
    age_min = (now - mtime) / 60.0
    match = disk == org
    w("%s match_origin=%s disk=%dB origin=%dB mtime_age=%.1fmin\n"
      % (f, match, len(disk), len(org), age_min))
    if not match:
        # classify the delta shape: line counts + first differing line index
        dl = disk.decode("utf-8", "replace").splitlines()
        ol = org.decode("utf-8", "replace").splitlines()
        w("   disk_lines=%d origin_lines=%d\n" % (len(dl), len(ol)))
        # union-shape check: is disk a superset of origin lines?
        ds = set(l.strip() for l in dl if l.strip())
        os_ = set(l.strip() for l in ol if l.strip())
        w("   disk_minus_origin_lines=%d origin_minus_disk_lines=%d\n"
          % (len(ds - os_), len(os_ - ds)))
        for l in list(ds - os_)[:3]:
            w("   D-ONLY: %s\n" % l[:160])
        for l in list(os_ - ds)[:3]:
            w("   O-ONLY: %s\n" % l[:160])
out.close()
print("classify written")
