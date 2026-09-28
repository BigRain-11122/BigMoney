# -*- coding: utf-8 -*-
"""r411 bm-b S7 closeout: state round_no 411 + heartbeat write (epoch int)."""
import datetime as dt
import io
import json
import time

ROOT = r"E:\Fluxgroup\FluxGroup\quant\bigmoney"

p = ROOT + r"\state.json"
s = json.load(io.open(p, encoding="utf-8"))
s["round_no"] = 411
s["note"] = ("r411: T-105 v1.3 slice LANDED (GREENxHOT clock face via market_clock call_latest + "
             "LIVE-latest stable pointers + daily_report embedded sec.2 + dashboard direct link; "
             "selftests 19/19+5-face) + W6 generate fix-first (gvvy_counts tuple typo killed first live "
             "burn, selftest 80/80 re-green, crash-fuse cleared) + V3-TOURNAMENT ignition unblocked "
             "(tick claimLost->git-fault diagnosed: origin churn + dirty-tree rebase block; mid-round "
             "commit+push landed claim commit; generate-0of1 lawfully taken over by bm-c per stale-claim "
             "law, its old-code burn self-heals onto pushed fix) + S6 37 legs rc=0 + MSG-0510 receipted")
s["ts"] = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(s, fh, ensure_ascii=False, indent=1)
    fh.write("\n")

hp = ROOT + r"\fleet\machines\bm-b.json"
h = json.load(io.open(hp, encoding="utf-8"))
now = dt.datetime.now().astimezone()
h["last_seen"] = now.isoformat(timespec="seconds")
h["heartbeat_epoch_utc"] = int(time.time())
h["clock_read"] = now.isoformat(timespec="seconds")
h["round_no"] = 411
h["loop_round"] = 411
h["round"] = 411
h["current_task"] = ("round 411 done: T-105 v1.3 slice (GREENxHOT clock face + daily_report embed + "
                     "dashboard link + LIVE-latest pointers) + W6 generate fix-first (tuple typo, fuse "
                     "cleared) + V3 ignition unblocked (claim commit pushed, tick to launch) -- next: "
                     "V3 burn supervise + W6 SCREEN entry when generate lands + intraday v1.1 slice")
h["verdict"] = ("healthy: smoke 26/26; T-105 v1.3 landed (clock-face wiring 19/19 + report embed 5-face + "
                "dashboard link); W6 fix-first landed (80/80 re-green); V3-TOURNAMENT ignition unblocked "
                "(SLA breach root-caused: tick claim push-reject + dirty-tree rebase block -> mid-round "
                "commit+push landed; W6-GENERATE shard lawfully taken over by bm-c stale-claim law, "
                "old-code burn self-heals onto pushed fix); S6 37 legs rc=0; orders 122/122 double-scan; "
                "MSG-0510 receipted+archived")
import psutil
h["cpu_util_pct"] = psutil.cpu_percent(interval=0.3)
vm = psutil.virtual_memory()
h["free_ram_gb"] = round(vm.available / 1e9, 2)
h["idle_ram_gb"] = h["free_ram_gb"]
h["total_ram_gb"] = round(vm.total / 1e9, 2)
h["idle_ram_mb"] = int(vm.available / 1e6)
h["free_ram_mb"] = int(vm.available / 1e6)
import subprocess
try:
    o = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                       capture_output=True, text=True, timeout=10).stdout.strip().splitlines()[0]
    h["gpu_free_vram_gb"] = round(int(o) / 1024, 2)
    h["gpu_idle_vram_gb"] = h["gpu_free_vram_gb"]
    h["gpu_idle_vram_mb"] = int(int(o))
except Exception:
    pass
assert isinstance(h["heartbeat_epoch_utc"], int), "epoch must be int"
with io.open(hp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(h, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
print("state round_no ->", s["round_no"], "| hb epoch int:", h["heartbeat_epoch_utc"],
      "| clock:", h["clock_read"], "| ram free:", h["free_ram_gb"])
