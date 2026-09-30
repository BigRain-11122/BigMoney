"""r494 heartbeat refresh post re-park: current_task/verdict updated to
the governance closure state; epoch int law + clock T law + r289 format."""
import datetime
import json
import time

import psutil

p = "fleet/machines/bm-b.json"
raw = open(p, "rb").read()
crlf = raw.count(b"\r\n")
lf_only = raw.count(b"\n") - crlf
h = json.loads(raw.decode("utf-8"))
now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
vm = psutil.virtual_memory()
avail_gb = round(vm.available / 1024**3, 1)

h["last_seen"] = now
h["heartbeat_epoch_utc"] = int(time.time())
h["clock_read"] = now
h["current_task"] = ("r494 closure: W14-GENERATE re-parked per r483 "
                     "canon (MSG-0540 honored; in-flight generate killed "
                     "pre-product, trial N=0; unfreeze requires sec-4 "
                     "self-proof or GM dual-ruling); runner 18-tuple "
                     "completion landed (f90798f26, selftest 53/53) = "
                     "mechanical face healthy; EXCLUSION/FACEB parked on "
                     "astock panel completion")
h["verdict"] = ("healthy: S0 rider-commit-then-rebase + ER (CODELY marker "
               "purge fd6200345), S1 47/47, S0.5 orders 133/133 EMPTY + "
               "D-19 UNCHANGED, S3 W14 runner completion + governance "
               "re-park closure (sec-4 gate honored, trial budget "
               "untouched 306/500), S6 38/38 rc0 (reconcile ZERO-DRIFT "
               "11/3), S7 self-heal green + attrition CLEAN; watermark "
               "RED=supply-blocker (W14 governance-parked pending GM "
               "dual-ruling + EXCLUSION/FACEB astock data-wait)")
h["free_ram_gb"] = avail_gb
h["idle_ram_gb"] = avail_gb
h["ram_free_gb"] = avail_gb
h["cpu_util_pct"] = round(psutil.cpu_percent(interval=1), 1)
h["last_round_at"] = now
h["last_round_ts"] = now

s = json.dumps(h, ensure_ascii=False, indent=1)
if crlf > 0 and lf_only == 0:
    s = s.replace("\n", "\r\n")
with open(p, "w", encoding="utf-8", newline="") as fh:
    fh.write(s)
chk = json.loads(open(p, encoding="utf-8").read())
assert isinstance(chk["heartbeat_epoch_utc"], int)
assert "T" in chk["clock_read"]
print(f"heartbeat ok: epoch={chk['heartbeat_epoch_utc']} "
      f"ram={avail_gb}GB")
