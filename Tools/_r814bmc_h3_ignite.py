"""r814 bm-c H3 weight download DETACHED ignite (bm-a r919 evening-chain
precedent: long-runner survives the 25-min wrapper kill window; receipt
verified in-round or next round). Ignition receipt ->
results/_r814bmc_h3_ignite.json. Pattern credit: _r813bmc_s6_ignite.py."""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "_r814bmc_h3_runner.out")
ERR = os.path.join(ROOT, "results", "_r814bmc_h3_runner.err")
o = open(OUT, "w", encoding="utf-8")
e = open(ERR, "w", encoding="utf-8")
flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
p = subprocess.Popen([sys.executable, os.path.join(
    ROOT, "Tools", "_r814bmc_h3_download.py")],
    cwd=ROOT, stdout=o, stderr=e, creationflags=flags, close_fds=True)
now = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")
rec = {"order": "O-20261009-1746", "machine": "bm-c", "pid": p.pid,
       "ignited_at": now, "driver": "Tools/_r814bmc_h3_download.py",
       "state": "results/_r814bmc_h3_download_state.json",
       "manifest_n": 5, "manifest_bytes_total": 40282346779,
       "channel": "hf-mirror.com (only reachable HF face on this machine)"}
with open(os.path.join(ROOT, "results", "_r814bmc_h3_ignite.json"), "w",
          encoding="utf-8") as f:
    json.dump(rec, f, ensure_ascii=False, indent=1)
print("H3 download detached pid=%d state=results/_r814bmc_h3_download_state.json"
      % p.pid)
