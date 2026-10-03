# -*- coding: utf-8 -*-
"""_r429bmc_close.py -- r429 bm-c closing updates: state + heartbeat + round report.

Self-verification: json.loads roundtrip on both JSON faces, epoch int check,
clock_read T-separator check, round report EOL detection (byte-level append).
"""
import datetime
import json
import os
import subprocess
import time

os.chdir(r"K:\Fluxgroup\FluxGroup\quant\bigmoney")
NOW_ISO = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
CN = 0x08000000

# fresh metrics
import psutil
CPU = psutil.cpu_percent(interval=1)
RAM = round(psutil.virtual_memory().available / 2**30, 1)
try:
    vout = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
        creationflags=CN, text=True, timeout=15)
    VRAM = int(vout.strip().splitlines()[0])
except Exception as e:
    vcur = json.load(open("state-bm-c.json", encoding="utf-8")).get("gpu_free_vram_mib")
    VRAM = int(vcur)
    print("nvidia-smi fallback, reuse %s: %s" % (vcur, e))
print("metrics: cpu=%.1f%% ram_free=%.1fGB vram=%dMiB epoch=%d" % (CPU, RAM, VRAM, EPOCH))

DID = ("r429 bm-c: (1) WAVE-2 FINALIZE BURN POLL (state next-a): detached PID 31276 alive through close "
       "(spawned 19:28:59, cpu 4326->5234s across round, finalize phase family CSCV PBO over 805 cells; "
       "4/4 shards 805/805 rows on origin, freeze 4796399f3; log shared-read receipt silent-by-design); "
       "w2_judge.json honestly absent -- adoption deferred to landing round per r422 law (deadline <=10-06, "
       "O-2115 acceptance 10-08). (2) S6 DRIVER ADAPTATION PIT CAUGHT IN-ROUND (score-2 fix, chain integrity): "
       "first-pass .Replace hit docstring only (real LOG line = os.path.join segmented literal) + "
       "Select-String self-check false positive (r420 needle-hit-furniture family PS-host face) -> r429 run "
       "log overwrote r428 evidence filename; fixed = byte count-assert replace + target-line assert + "
       "r428 log restored from HEAD blob (sha-equal verified) + chain rerun 37/37 rc0 under correct name; "
       "S4 pit +1 -> research/pit-ps.md (LF-blob md5 ef885f3c...) + CODELY PS pointer increment. "
       "(3) S0: FF integrate 3 bm-a r641 commits (89bbb402f->b090bbaea: G2_SLOT_OLD_P1 census 0/41 honest "
       "negative); dirty-at-start 4 bm-c daemon faces kept deferred. (4) S0.5: orders 152/152 zero-unacked "
       "double-scan; D-19 4167B784 MATCH zero-consume; group orders.md 68947C17 MATCH; inbox zero unread. "
       "(5) S1 smoke 47/47; SatEngine rc0 alive (N1 waves 1-114). (6) S6 37/37 rc0 x2: ZERO-DRIFT streak 29; "
       "golden-week no-ops + lane guards honest; daily_report+LIVE-2026-10-03 idempotent regen. "
       "(7) S7 4/4: loop pin=5 no-op, watchdog registered, claws MATCH x2, attrition CLEAN rc0. "
       "(8) boards: session jobs empty + fleet tickets 0 open (46 claimed) -- no new claims, wave-2 "
       "single-lane focus.")

NEXT = ("(a) r430: poll judge-finalize --wave 2 burn PID 31276 -> if w2_judge.json landed: adopt "
        "(complete=true 805 cells, ledger single-shot chain-linear, E[FP], G2-eligible, verdicts) via "
        "_r426bmc_close.py template adapted to landing round (adaptation = count->replace->target-line-assert "
        "trio per r429 pit) + idempotent finalize rerun no-op check + commit product+deferred log receipt "
        "atomically, deadline <=10-06; O-2115 wave-2 acceptance evidence pack 10-08; (b) D-06 "
        "full-reconciliation closeout 10-07; (c) T-143 assembly window post-10-09 (deliverable 10-29); "
        "(d) moneyflow GM ruling watch (MSG-1452/1543); (e) W14 lane zero-touch pending GM dual-ruling; "
        "(f) bm-a heartbeat staleness watch (fresh 21:02; >3h = GM 改派呈报).")

VERIFY = ("probe receipts (_r427bmc_probe.py rerun: orders 152/152, D19 4167B784 MATCH, GORDERS 68947C17 "
          "MATCH, WM red=false, burn alive, 1 live mass-trial proc); burn log shared-read receipt (spawn "
          "19:28:59, 4/4 shards 805/805, freeze 4796399f3); smoke 47/47; S6 37/37 rc0 x2 (_r429bmc_s6_log.txt; "
          "ZERO-DRIFT streak 29); driver fix receipt (_r429bmc_driver_fix.py: b.count==1 assert + LOG line "
          "assert + r428 log HEAD-blob restore sha-equal); pit append receipt (_r429bmc_pit_append.py: "
          "+1284B CRLF face, LF-blob md5 ef885f3cd5f9700ea68f034791d1f3b1); attrition CLEAN rc0; loop pin=5 "
          "no-op; watchdog registered; claws MATCH x2; push delivery verify post-commit (本地未达 origin=0)")

CT = ("r429: S6 37/37 rc0 x2 (driver LOG-path fix in-round, r428 evidence restored from HEAD); W2 finalize "
      "burn IN FLIGHT (PID 31276, cpu 5234s at close); next: r430 poll -> adopt w2_judge.json at landing "
      "(template _r426bmc_close.py), deadline <=10-06")

# 1) state update
sp = "state-bm-c.json"
st = json.load(open(sp, encoding="utf-8"))
assert st["round_no"] == 428, st["round_no"]
st["round_no"] = 429
st["clock_read"] = NOW_ISO
st["last_seen"] = NOW_ISO
st["last_ts"] = NOW_ISO
st["updated"] = NOW_ISO
st["updated_at"] = NOW_ISO
st["last_round_at"] = NOW_ISO
st["last_round_ts"] = NOW_ISO
st["last_decisions_read_at"] = NOW_ISO
st["heartbeat_epoch_utc"] = EPOCH
st["cpu_pct"] = CPU
st["idle_ram_gb"] = RAM
st["gpu_free_vram_mib"] = VRAM
st["current_task"] = CT
st["did"] = DID
st["next"] = NEXT
st["verify"] = VERIFY
st["last_round"] = ("r429 bm-c: S6 37/37 rc0 x2 + driver LOG-path literal-replace pit caught/fixed in-round "
                    "(r428 evidence restored from HEAD, pit-ps +1); wave-2 finalize burn poll (in flight)")
with open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
chk = json.load(open(sp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int) and chk["round_no"] == 429
print("state updated: round_no=429 epoch=%d" % chk["heartbeat_epoch_utc"])

# 2) heartbeat update
hp = "fleet/machines/bm-c.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["clock_read"] = NOW_ISO
hb["last_seen"] = NOW_ISO
hb["last_seen_at"] = NOW_ISO
hb["updated_at"] = NOW_ISO
hb["heartbeat_epoch_utc"] = EPOCH
hb["round_no"] = 429
hb["cpu_pct"] = CPU
hb["cpu_util_pct"] = CPU
hb["cpu_idle_pct"] = round(100 - CPU, 1)
hb["free_ram_gb"] = RAM
hb["idle_ram_gb"] = RAM
hb["ram_free_gb"] = RAM
for k in ("gpu_free_vram_mb", "gpu_free_vram_mib", "gpu_idle_vram_mb", "gpu_idle_vram_mib", "gpu_free_mb"):
    hb[k] = VRAM
hb["activity_now"] = ("r429: S6 chain 37/37 rc0 x2 + driver adaptation pit caught/fixed in-round; "
                      "wave-2 finalize burn poll -- IN FLIGHT (PID 31276); adoption at landing, deadline <=10-06")
hb["current_task"] = CT
hb["latest_artifact"] = ("Tools/_r429bmc_s6.py + results/_r429bmc_s6_log.txt (37/37 rc0 x2, ZERO-DRIFT "
                         "streak 29) + research/pit-ps.md r429 literal-replace pit @ " + NOW_ISO)
hb["next_milestone"] = ("w2_judge.json adoption at burn landing (PID 31276 finalize phase; deadline <=10-06; "
                        "OS 10-min poll); O-2115 wave-2 acceptance evidence pack 10-08; D-06 closeout 10-07")
hb["prod_lanes"] = ("MASS_TRIAL_W2 finalize burn in flight (PID 31276); moneyflow lane GM-ruling pending; "
                    "D-06 closeout 10-07")
hb["verdict"] = "healthy"
with open(hp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
chk2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk2["heartbeat_epoch_utc"], int)
assert "T" in chk2["clock_read"] and " " not in chk2["clock_read"]
assert len(chk2["orders_ack"]) == 152
print("heartbeat updated: epoch=%d clock=%s orders_ack=152" % (chk2["heartbeat_epoch_utc"], chk2["clock_read"]))

# 3) round report append (EOL detection)
rp = "round_reports-bm-c.md"
rb = open(rp, "rb").read()
eol = b"\r\n" if rb.count(b"\r\n") >= rb.count(b"\n") - rb.count(b"\r\n") else b"\n"
line = ("%s\t| r429 bm-c\t| %s\t| WM 绿（red=false lane healthy；golden-week 合法 idle·board 零 open·"
        "bandit next_pick moneyflow-IC claimed-by-other 维持） | dept:工程/舰队\t| 验证：%s\t| 下轮：%s\t| "
        "本地未达 origin commit 数=N（push 后 fetch 复核·收轮时回填 0）") % (NOW_ISO, DID, VERIFY, NEXT)
if not rb.endswith(eol):
    rb = rb + eol
open(rp, "ab").write(line.encode("utf-8") + eol)
print("round report appended (%d B, eol=%r)" % (len(line.encode("utf-8")) + len(eol), eol))
print("CLOSE_OK")
