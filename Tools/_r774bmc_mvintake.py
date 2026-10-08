"""r774 bm-c A-direction intake probe (read-only): fetch group origin, dump
REVIEW-PACKAGE-v1.md from origin blob (fresh-read law), probe ComfyUI API
liveness, list mv_work style/kf/outbound faces."""
import os
import subprocess
import urllib.request
import json
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

G = r"K:\Fluxgroup\FluxGroup"
R = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

subprocess.run(["git", "-C", G, "fetch", "origin"], capture_output=True)
p = subprocess.run(["git", "-C", G, "show", "origin/main:fleet/mv0001-handover/outbound/REVIEW-PACKAGE-v1.md"],
                   capture_output=True)
txt = p.stdout.decode("utf-8", "replace")
out = os.path.join(R, "results", "_r774bmc_review_pkg_origin.md")
with open(out, "w", encoding="utf-8") as fh:
    fh.write(txt)
print("=== REVIEW-PACKAGE-v1.md (origin) len=%d ===" % len(txt))
print(txt[:6000])
print("=== TAIL ===")
print(txt[-2500:])

out = os.path.join(R, "results", "_r774bmc_review_pkg_origin.md")
with open(out, "w", encoding="utf-8") as fh:
    fh.write(txt)

# ComfyUI liveness probe (localhost API, 2s timeout)
for port in (8188, 8189):
    try:
        r = urllib.request.urlopen("http://127.0.0.1:%d/system_stats" % port, timeout=2)
        data = json.loads(r.read().decode("utf-8", "replace"))
        dev = data.get("devices", [{}])
        print("COMFY port=%d ALIVE" % port)
        for d in dev:
            print("  dev", d.get("name"), "vram_free", d.get("vram_free"))
        break
    except Exception as e:
        print("COMFY port=%d dead (%s)" % (port, type(e).__name__))

mv = os.path.join(R, "results", "mv_work")
for sub in ("style", "kf", "outbound_jpg", "seg"):
    d = os.path.join(mv, sub)
    if os.path.isdir(d):
        fs = sorted(os.listdir(d))
        print("DIR %s n=%d" % (sub, len(fs)))
        for f in fs[-8:]:
            fp = os.path.join(d, f)
            sz = os.path.getsize(fp) if os.path.isfile(fp) else -1
            print("  ", f, sz)
    else:
        print("DIR %s missing" % sub)
