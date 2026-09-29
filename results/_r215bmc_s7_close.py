# -*- coding: utf-8 -*-
"""r215 bm-c S7 closeout: state round_no + heartbeat refresh (epoch int law)."""
import datetime
import json
import time

now_iso = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S+08:00")
now_plain = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ---------- state-bm-c.json (round_no increment 214 -> 215)
SP = "state-bm-c.json"
s = json.load(open(SP, encoding="utf-8"))
assert s["machine_id"] == "bm-c" and s["round_no"] == 214, (s["machine_id"], s["round_no"])
s["round_no"] = 215
s["updated"] = now_iso
s["note"] = ("r215: W7-JUDGE lane_owner amendment null->bm-b landed origin ab7b72d9 "
             "(W5-JUDGE precedent, Money02 t18 physical-only-bm-b; closes cache-less "
             "claim class via existing dual lane guards; shard stamp untouched); "
             "bm-a 11:52 claim crash third-window receipt + MSG-1158 FYI; "
             "pit-103 lane_owner-at-entry law; 5x HANDOVER entry; "
             "S6 37 legs rc=0 (dualrun streak 22/3; WM py_low_board_clear legal-idle; "
             "regime ORANGE shadow d2; clock ORANGE_COOL; REPORT/LIVE 0929 refreshed; "
             "token delta=0); S7 trio green + heartbeat epoch int")
s["did"] = ("S0 stash-pull-rebase-pop clean -> S0.5 orders 122/122 zero-diff (S7 "
           "double-scan same) + decisions zero-new (09-29 batch already processed; "
           "D-02 fetch-law F-20260929-01 standing) -> S1 smoke 26/26 -> S2 boards 0 open "
           "-> S3 lane_owner amendment three-way verified + escape branch machine/bm-c-r215 "
           "+ pit-93 single merge LANDED ab7b72d9 -> MSG-1158 to bm-a -> S4 pit-103 -> "
           "5x HANDOVER -> S6 37 legs rc=0 -> S7 trio green")
s["verify"] = ("lane fix origin ab7b72d9 real; W7-JUDGE lane_owner=bm-b + shard stamp "
               "bm-c 11:30:05 re-read intact; W5 precedent intact; dualrun streak 22/3; "
               "S6 legs rc=0 each; smoke 26/26; orders 122/122 programmatic")
s["next"] = ("r216: (a) W7-JUDGE bm-b retake watch (12:12:08+ claim-file stale window; "
             "retake -> minutes-scale burn -> finalize -> 48h CEO clock + intake slice) "
             "(b) bm-a hb observation (C-faces fresh 5-6min this window) "
             "(c) 10-01 month-first triple fire + REGIME_GUARD v3 date-gate auto "
             "(d) moneyflow panel self-heal watch")
s["last_round_ts"] = "2026-09-29T11:47:00+08:00"
s["current_task"] = ("r215 closed: lane_owner fix landed + MSG-1158 sent; next = W7-JUDGE "
                     "bm-b retake watch + 10-01 triple fire")
s["updated_at"] = now_iso
s["last_round_at"] = "r214"
json.dump(s, open(SP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(SP, encoding="utf-8"))
assert chk["round_no"] == 215
print("state OK round_no=215")

# ---------- heartbeat fleet/machines/bm-c.json
import subprocess
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                          "--format=csv,noheader,nounits"], capture_output=True,
                         text=True, timeout=20).stdout.strip().splitlines()
    vram = int(out[0]) if out else None
except Exception:
    vram = None
try:
    cpu = subprocess.run(["powershell", "-NoProfile", "-Command",
        "(Get-CimInstance Win32_Processor | Measure-Object -Property "
        "LoadPercentage -Average).Average"], capture_output=True, text=True,
        timeout=30).stdout.strip()
    cpu_pct = float(cpu) if cpu else None
except Exception:
    cpu_pct = None
try:
    ram = subprocess.run(["powershell", "-NoProfile", "-Command",
        "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1)"],
        capture_output=True, text=True, timeout=30).stdout.strip()
    idle_ram = float(ram) if ram else None
except Exception:
    idle_ram = None

HP = "fleet/machines/bm-c.json"
h = json.load(open(HP, encoding="utf-8"))
h["last_seen"] = now_plain
epoch = int(time.time())
assert isinstance(epoch, int)
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = now_iso
h["verdict"] = ("r215 green: W7-JUDGE lane_owner=bm-b amendment LANDED ab7b72d9 (W5 "
                "precedent; closes cache-less claim class; shard stamp untouched; bm-b "
                "retake 12:12:08+); smoke 26/26; S6 37 legs rc=0; dualrun streak 22/3; "
                "escape branch machine/bm-c-r215 home via pit-93 single merge; MSG-1158 "
                "to bm-a; pit-103 + 5x HANDOVER")
h["current_task"] = ("r215 closed: lane_owner fix landed; next = W7-JUDGE bm-b retake "
                     "watch + 10-01 month-first triple fire")
if cpu_pct is not None:
    h["cpu_pct"] = cpu_pct
if idle_ram is not None:
    h["idle_ram_gb"] = idle_ram
if vram is not None:
    h["gpu_free_vram_mib"] = vram
json.dump(h, open(HP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
h2 = json.load(open(HP, encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch int law FAIL"
assert "T" in h2["clock_read"], "clock T-separator law FAIL"
print("heartbeat OK epoch=", h2["heartbeat_epoch_utc"], "clock=", h2["clock_read"],
      "cpu=", cpu_pct, "idle_ram=", idle_ram, "vram=", vram)
