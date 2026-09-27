# -*- coding: utf-8 -*-
"""r378 bm-a heartbeat update (F7: epoch int + clock_read T-separated)."""
import json
import time
import datetime as dt
import subprocess

f = "fleet/machines/bm-a.json"
j = json.load(open(f, encoding="utf-8-sig"))
now = dt.datetime.now().astimezone()
j["last_seen"] = now.isoformat(timespec="seconds")
j["clock_read"] = now.isoformat(timespec="seconds")
epoch = int(time.time())
j["heartbeat_epoch_utc"] = epoch
j["round_no"] = 378
j["round"] = 378
j["loop_round"] = 378
j["task"] = "idle-round-done"
j["current_task"] = ("r378 done: D-03(1) batch-3 C-family slice-1 -- single-writer host-guard "
                      "(census C treatment: byte-identical re-derives -> lanes=pure churn; "
                      "dashboard_status.js file:// HTML consumers cannot merge-read) wired 6 faces "
                      "host=bm-a w/ stale-takeover O-2100 law, 3 writers guarded, selftest 7/7, "
                      "non-host sim all-skip + OBS-WINDOW CATCH #4 same round: session pool defer "
                      "bypasses lane mirror -> merger rank resurrected V2-P1 deliberate defer -- "
                      "fixed via defer_note governance field + marker law (marked-waiting beats "
                      "bare-ready, risk-asymmetric) + runnable_pool joins compute_audit mirror "
                      "family; merger selftest 47/47, reconcile 14/14 zero-drift restored")
j["verdict"] = ("py_low_board_clear legal-idle round-closed (board 0 open / pool non-done all "
                "bm-b-lane-or-gated: W2B ~12h burn + V2-P1 waiting defer RAM-serialize + judge "
                "shards on bm-b declare; audit CLEAN flags=[]; reconcile 14/14; next = batch-3 "
                "slice-2 paper family + TODAY 15:30 first bar -> T-91 s3 first-marks auto-fire)")
try:
    cpu = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "(Get-CimInstance Win32_Processor | Measure-Object -Property "
                          "LoadPercentage -Average).Average"],
                         capture_output=True, text=True, timeout=15)
    j["cpu_pct"] = float(cpu.stdout.strip() or 0)
    j["cpu_util_pct"] = j["cpu_pct"]
except Exception:
    pass
try:
    ram = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1)"],
                         capture_output=True, text=True, timeout=15)
    j["free_ram_gb"] = float(ram.stdout.strip() or 0)
    j["idle_ram_gb"] = j["free_ram_gb"]
except Exception:
    pass
json.dump(j, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
k = json.load(open(f, encoding="utf-8-sig"))
ok_int = isinstance(k["heartbeat_epoch_utc"], int) and not isinstance(k["heartbeat_epoch_utc"], bool)
ok_t = "T" in k["clock_read"]
print(f"readback: epoch={k['heartbeat_epoch_utc']} int_ok={ok_int} "
      f"clock={k['clock_read']} T_ok={ok_t} round={k['round_no']}")
assert ok_int and ok_t and k["round_no"] == 378
