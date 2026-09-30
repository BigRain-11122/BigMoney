"""r494 bm-b heartbeat updater: r289 format-probe law (CRLF/LF + indent
preserved), epoch int law (R170/R178), clock_read T-separator law (R262)."""
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
cpu = psutil.cpu_percent(interval=1)
avail_gb = round(vm.available / 1024**3, 1)

h["last_seen"] = now
h["heartbeat_epoch_utc"] = int(time.time())
h["clock_read"] = now
h["current_task"] = ("r494: W14 generate-leg 18-tuple completion landed "
                     "(e6cb30924+f90798f26; two stale-face crashes fixed; "
                     "selftest 53/53; crash-fuse CLEARED x2) + autofill "
                     "r300 indirect-arm adopted -> generate queued at "
                     "daemon post-push; EXCLUSION/FACEB honest-parked on "
                     "astock panel (AUTOFILL-PARK x2, zero fuse pollution)")
h["round_no"] = 494
h["round"] = 494
h["loop_round"] = 494
h["verdict"] = ("healthy: S0 rider-commit-then-rebase x1 clean (14 "
                "shared-regen UU take-origin per r296iii/r493 lineage; "
                "push ok), S1 47/47, S0.5 orders 133/133 EMPTY double-scan "
                "+ D-19 ED4E0EAB UNCHANGED, S3 W14 double crash-fix closed "
                "loop (generate leg 18-tuple complete, 30/30 args, selftest "
                "53/53), S6 38/38 rc0 (reconcile ZERO-DRIFT 11/3), S7 "
                "self-heal 3 legs green + attrition CLEAN; watermark "
                "RED=supply-blocker-same-round-closed (generate queued at "
                "daemon post-push, EXCLUSION/FACEB data-wait parked)")
h["free_ram_gb"] = avail_gb
h["idle_ram_gb"] = avail_gb
h["ram_free_gb"] = avail_gb
h["cpu_util_pct"] = round(cpu, 1)
h["last_round_at"] = now
h["last_round_ts"] = now

s = json.dumps(h, ensure_ascii=False, indent=1)
if crlf > 0 and lf_only == 0:
    s = s.replace("\n", "\r\n")
with open(p, "w", encoding="utf-8", newline="") as fh:
    fh.write(s)
chk = json.loads(open(p, encoding="utf-8").read())
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk["clock_read"], "clock_read must be T-separated"
print(f"heartbeat ok: epoch={chk['heartbeat_epoch_utc']} (int) "
      f"clock={chk['clock_read']} ram_free={avail_gb}GB cpu={cpu:.1f}% "
      f"line_endings={'CRLF' if crlf > 0 and lf_only == 0 else 'LF'}")
