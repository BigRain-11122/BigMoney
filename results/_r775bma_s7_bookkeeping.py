# -*- coding: utf-8 -*-
"""r775 bm-a S7 bookkeeping: state round_no, heartbeat, round-report line,
CODELY.md execution-record line (append-only via python single-file
fresh-read-modify-write per the multi-writer replace-ban law)."""
import json
import time
import io

# 1) state-bm-a.json round_no -> 775
sp = "state-bm-a.json"
s = json.load(open(sp, encoding="utf-8"))
s["round_no"] = 775
s["last_round_ts"] = "2026-10-06T13:0x"
io.open(sp, "w", encoding="utf-8", newline="\n").write(
    json.dumps(s, ensure_ascii=False, indent=1) + "\n")
s2 = json.load(open(sp, encoding="utf-8"))
assert s2["round_no"] == 775, s2["round_no"]

# 2) heartbeat fleet/machines/bm-a.json
hp = "fleet/machines/bm-a.json"
h = json.load(open(hp, encoding="utf-8"))
h["last_seen"] = "2026-10-06T13:0x"
h["current_task"] = "W158 freeze landed (r775, 74th owned/148th wave); next = engine tick burn-off of W158 shards + T-174/175/176 intake faces"
h["cpu_cores"] = 32
h["idle_ram_gb"] = 47.5
h["gpu_free_vram_gb"] = 8.0
h["verdict"] = "green"
h["heartbeat_epoch_utc"] = int(time.time())
assert isinstance(h["heartbeat_epoch_utc"], int)
h["clock_read"] = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
io.open(hp, "w", encoding="utf-8", newline="\n").write(
    json.dumps(h, ensure_ascii=False, indent=1) + "\n")
h2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int) and "T" in h2["clock_read"]

# 3) round report line (append)
rr_path = "round_reports-bm-a.md"
line = ("| 2026-10-06 13:0x | r775 | W158 freeze landed (bm-a 74th owned, "
        "148th wave): pf.py N1_BANDS[158] A 362_404..364_403 / B 364_404..364_603 "
        "(r773 band-gate ADMIT verbatim, staircase 17th instance E36) + "
        "SAME-WINDOW pf.py W157-block prose heal (r774 directive, r773 pit law: "
        "malformed windows -> r772 gate leg3 verbatim) + n1.py WAVE_CONFIGS[158] "
        "entry/materializer(chain 138..157 n=20)/PASS-claim; r773 pit-law editor "
        "compliance (whole-string tokens, pre-TOK probe inventory, full-file "
        "start>end scans CLEAN both files, W159p re-derived from gate leg3); "
        "freeze commit 6957f509e + merge absorb 988fe49a0 pushed behind-0 | "
        "pf selftest 9/9 + smoke 48/48 + S6 38/38 rc0 first-pass (119.9s) + "
        "attrition CLEAN + S7 quartet green | next: W158 shard burn-off via "
        "engine tick (12 shards), T-173 report due 10-08 noon, T-174/175/176 "
        "intake faces |\n")
with io.open(rr_path, "a", encoding="utf-8", newline="") as f:
    f.write(line)

print("S7 bookkeeping landed: state=775, heartbeat epoch int, RR line appended")
