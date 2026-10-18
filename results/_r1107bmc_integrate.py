# -*- coding: utf-8 -*-
# r1107 integration: ff-pull origin with watermark ts-newer-wins heal (r1028 family).
import io, os, shutil, subprocess, sys

def g(*args):
    r = subprocess.run(["git"] + list(args), capture_output=True, text=True, encoding="utf-8")
    return r.returncode, (r.stdout or "") + (r.stderr or "")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO)
wm = os.path.join("results", "watermark_red.json")
bak = os.path.join("results", "_r1107bmc_wm_backup.json")
shutil.copyfile(wm, bak)
rc, out = g("checkout", "--", wm)
print("checkout rc", rc, out.strip()[:80])
rc, out = g("pull", "--ff-only")
print("pull rc", rc)
print(out.strip()[:300])
if rc != 0:
    print("PULL FAILED -- restoring backup and aborting")
    shutil.copyfile(bak, wm)
    sys.exit(1)
shutil.copyfile(bak, wm)
rc, out = g("status", "--porcelain")
print("status after restore:")
print(out)
import json
loc = json.load(io.open(wm, encoding="utf-8"))
print("watermark now ts:", loc["ts"], "machine:", loc["machine"])
print("INTEGRATION OK")
