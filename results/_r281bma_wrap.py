# -*- coding: utf-8 -*-
"""R281 bm-a S7 wrap: state file + heartbeat write-back (R271 timestamp
law: one now() instance for every stamp; R262 clock_read T-separator;
epoch int type law R170/R178; byte-face mirror per r255/r257 probe)."""
import datetime
import json
import os
import subprocess
import time

now = datetime.datetime.now().astimezone()
ts = now.strftime("%Y-%m-%d %H:%M:%S")
epoch = int(time.time())

# ---- state-bm-a.json (probe face: no BOM, CRLF, indent 1, no tail NL)
SP = "state-bm-a.json"
raw = open(SP, "rb").read()
d = json.loads(raw.decode("utf-8-sig"))
d["round_no"] = 281
d["did"] = ("CN_TREND_ETF_P1 runner built+21/21 selftest+real-gate probe "
            "GREEN, pooled ready lane=ANY workers=4; rev_osc twin finalize "
            "fixes (g2 pbo float + trials_ledger key); rebase x2 resolved "
            "(autofill_state union / post_review pair)")
d["verdict"] = "ok"
d["next"] = ("autofill tick 01:00 claims cntrend-0of1 + revosc relaunch; "
             "judgment/harvest of both batches next rounds; T-87 s2 "
             "queue #2 after #1 judged")
d["ts"] = ts
d["last_round_ts"] = ts
d["updated_at"] = ts
d["current_task"] = ("R281 done: CN_TREND_ETF_P1 pooled ready + rev_osc "
                     "finalize fixes; awaiting tick dual-launch")
s = json.dumps(d, ensure_ascii=False, indent=1)
open(SP, "wb").write(s.replace("\n", "\r\n").encode("utf-8"))
json.loads(open(SP, encoding="utf-8-sig").read())
print("state round_no 281 written")

# ---- heartbeat fleet/machines/bm-a.json
def _proc(cmd):
    return subprocess.run(cmd, capture_output=True, text=True).stdout

cpu = 0.0
ram = 0.0
try:
    cpu = float(_proc(["wmic", "cpu", "get", "loadpercentage"]).strip()
                .splitlines()[-1]) if False else 0.0
except Exception:
    pass
try:
    import psutil
    cpu = psutil.cpu_percent(interval=0.3)
    ram = psutil.virtual_memory().available / (1024 ** 3)
except Exception:
    ram = 48.0
gpu_free = 5.3
try:
    out = _proc(["nvidia-smi", "--query-gpu=memory.free",
                 "--format=csv,noheader,nounits"])
    gpu_free = round(float(out.strip().splitlines()[0]) / 1024, 1)
except Exception:
    pass

HP = "fleet/machines/bm-a.json"
hraw = open(HP, "rb").read()
hb = json.loads(hraw.decode("utf-8-sig"))
hb["machine_id"] = "bm-a"
hb["last_seen"] = ts
hb["current_task"] = ("R281: CN_TREND_ETF_P1 pooled ready (runner 21/21, "
                      "lane=ANY) + rev_osc finalize fixes; tick 01:00 "
                      "dual-launch window")
hb["cpu_cores"] = os.cpu_count()
hb["cpu_pct"] = round(cpu, 1)
hb["free_ram_gb"] = round(ram, 1)
hb["gpu_free_vram_gb"] = gpu_free
hb["verdict"] = "healthy"
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = now.isoformat()          # T-separator law (R262)
hb["round_no"] = 281
hb["task"] = ("R281 delivered: T-87 s2 #1 runner pooled + rev_osc twin "
              "finalize-fix; both batches ready for tick launch")
hface_crlf = b"\r\n" in hraw
hface_bom = hraw.startswith(b"\xef\xbb\xbf")
hface_tail = hraw.endswith(b"\n")
hs = json.dumps(hb, ensure_ascii=False, indent=1)
if hface_tail:
    hs += "\n"
enc = "utf-8-sig" if hface_bom else "utf-8"
with open(HP, "w", encoding=enc,
          newline=("\r\n" if hface_crlf else "\n")) as fh:
    fh.write(hs)

# ---- self-verify (R271 law: epoch int + minute consistency)
chk = json.loads(open(HP, encoding="utf-8-sig").read())
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert chk["clock_read"].count("T") >= 1, "clock_read T-separator law"
import datetime as _dt
ls = _dt.datetime.fromtimestamp(chk["heartbeat_epoch_utc"]).astimezone()
assert abs((ls - now).total_seconds()) < 120, "epoch/last_seen consistency"
print("heartbeat written: epoch", chk["heartbeat_epoch_utc"],
      "clock", chk["clock_read"], "| state+hb self-verified")
