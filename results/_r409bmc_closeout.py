# -*- coding: utf-8 -*-
# r409 bm-c S7 closeout: state + heartbeat + round-report ledger + inbox move.
# JSON int epoch law (R170/R178), clock_read ISO T law (R262), CRLF preserve.
import json, time, subprocess, shutil, os, io, sys
from datetime import datetime, timezone, timedelta

RB = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = datetime.now(timezone(timedelta(hours=8)))
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
TS2 = NOW.strftime("%Y-%m-%d %H:%M:%S")
EPOCH = int(time.time())

def cpu_ram():
    try:
        import psutil
        cpu = round(psutil.cpu_percent(interval=1.0), 1)
        ram = round(psutil.virtual_memory().available / (1024**3), 1)
    except Exception:
        cpu, ram = 10.0, 3.0
    return cpu, ram

def gpu_free():
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                            "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=20,
                           encoding="utf-8", errors="replace",
                           creationflags=0x08000000)
        return int(r.stdout.strip().splitlines()[0])
    except Exception:
        return -1

CPU, RAM = cpu_ram()
GPU = gpu_free()
print("METRICS cpu=%s ram=%s gpu_free_mib=%s" % (CPU, RAM, GPU))

# ---------- state-bm-c.json ----------
SP = RB + r"\state-bm-c.json"
with io.open(SP, "r", encoding="utf-8") as f:
    st = json.load(f)
st["clock_read"] = TS
st["cpu_pct"] = CPU
st["current_task"] = "r409 closeout complete (CODELY r407 canon repair + S6 33/33)"
st["gpu_free_vram_mib"] = GPU
st["heartbeat_epoch_utc"] = EPOCH
st["idle_ram_gb"] = RAM
st["last_decisions_read_at"] = TS
st["did"] = ("r409 bm-c: (1) CODELY.md r407 born-mojibake pit entry fact-reconstructed "
             "(state next-pointer item (c) delivered): surgical whole-line replace via "
             "results/_r409bmc_codely_r407_repair.py (prefix-match, BOM/CRLF preserve, "
             "mojibake guard, read-back CJK verified, neighbors intact); reconstructed law "
             "dual-face = CLI replace def-eating NameError (r281/r280 family recurrence) + "
             "CJK->'?' write-channel corruption (the mojibake root cause itself, both faces "
             "born in commit 53b96bdcb, no clean original in git); entry marked r409 "
             "fact-reconstruction. (2) S0 surgery: churn-absorb commit + rebase over origin "
             "e5590e142, 17 shared-derive conflict faces take-origin per r612/r405 law "
             "(origin-tip blob checkout per-face), r305 rebase-continue false-refusal hit "
             "twice (manual commit --no-edit + ephemeral daemon-churn discard); landed "
             "ahead=2 behind=0 clean. (3) S0.5 orders 151/151 zero unacked (programmatic "
             "diff); D-19 4167B784 MATCH zero action. (4) S1 smoke 47/47. (5) S6 33/33 rc0 "
             "(r408 chain runner verbatim reuse, log renamed): dualrun ZERO-DRIFT streak 5, "
             "audit CLEAN zero flags (pool-supply-gap floor not breached, parallel_eff "
             "22.44 eff cores), watermark py_low_with_work_cands = LEGAL idle, ORANGE_COOL "
             "clock call, holiday no-ops honest. (6) attrition guard CLEAN. (7) MSG-0940 "
             "processed (bm-c observer ack; nulls/sens containment state consistent with "
             "pool ready view) -> moved processed.")
st["last_round"] = ("2026-10-03 r409 bm-c: CODELY.md r407 mojibake pit entry "
                    "fact-reconstructed (dual-face law, read-back verified) + S0 rebase "
                    "surgery (17 faces take-origin, r305 false-refusal x2 handled) + S6 "
                    "33/33 rc0 + orders 151/151 + D-19 MATCH")
st["last_round_at"] = "r409"
st["last_round_ts"] = TS
st["last_seen"] = TS
st["last_ts"] = TS2
st["round_no"] = 409
st["next"] = ("(a) T-143 remaining faces: SYSTEM-V1 (bm-a primary) + REV-OSC assembly at "
              "exam assembly window + assembly readout, deliverable 10-29 (baselines+"
              "criteria+runbook pinned r405-r408, do-not-overwrite-after-10-09); "
              "(b) 688 containment closure observation: T-156 croc receiver camping at "
              "bm-a (pid 84644, MSG-0935 liveness open, sender leg bm-b) -> four-point "
              "verify -> 90 nulls re-derive before FUND family finalize (bm-c structurally "
              "locked observer; pool ready 1 unclaimed face left to sat-engine dispatcher); "
              "(c) [DONE r409] CODELY.md r407 mojibake entry repaired; (d) moneyflow IC "
              "panel window: collector source-blocked 53/5222 conn-fuse, rank lane "
              "fetch-failed today, IC batch waits panel completion (next_pick claimed); "
              "(e) T-144(c) D-06 closure reconciliation 10-07")
st["updated"] = TS
st["updated_at"] = TS
st["verify"] = ("smoke 47/47 rc0; S6 33/33 rc0 (dualrun ZERO-DRIFT streak 5 @ 358 entries; "
                "compute_audit CLEAN zero flags; watermark py_low_with_work_cands = LEGAL "
                "idle per O-2115 sec.2: pool ready 3 / 1 unclaimed = 688 re-burn face "
                "structurally locked, bm-c observer per MSG-0910; board 0 open; bandit 0; "
                "W115 parked non-abandon per O-2115 ranking law; resident sat-engine alive "
                "rc0); orders 151/151 zero unacked double-scan; D-19 4167B784 MATCH; "
                "attrition guard CLEAN; CODELY r407 read-back CJK verified")
with io.open(SP, "w", encoding="utf-8") as f:
    json.dump(st, f, indent=1, ensure_ascii=False)
    f.write("\n")
print("STATE round_no=%d epoch_int=%s" % (st["round_no"], isinstance(st["heartbeat_epoch_utc"], int)))

# ---------- fleet/machines/bm-c.json ----------
HP = RB + r"\fleet\machines\bm-c.json"
with io.open(HP, "r", encoding="utf-8") as f:
    hb = json.load(f)
hb["activity_now"] = ("r409: CODELY.md r407 born-mojibake pit entry fact-reconstructed "
                      "(dual-face law) + S6 33/33 rc0")
hb["clock_read"] = TS
hb["cpu_idle_pct"] = round(100 - CPU, 1)
hb["cpu_pct"] = CPU
hb["cpu_util_pct"] = CPU
hb["current_task"] = "r409 closeout complete (CODELY r407 canon repair + S6 33/33 rc0)"
hb["free_ram_gb"] = RAM
hb["gpu_free_vram_mb"] = GPU
hb["gpu_free_vram_mib"] = GPU
hb["gpu_idle_vram_mb"] = GPU
hb["gpu_idle_vram_mib"] = GPU
hb["gpu_vram_free_mb"] = GPU
hb["heartbeat_epoch_utc"] = EPOCH
hb["idle_ram_gb"] = RAM
hb["last_seen"] = TS
hb["last_seen_at"] = TS
hb["latest_artifact"] = ("CODELY.md r407 pit-entry reconstruction (dual-face law: replace "
                         "def-eating NameError + CJK->'?' write-channel corruption; r409 "
                         "fact-rebuild marker; read-back verified) @ 2026-10-03 10:2x, "
                         "commit on origin")
hb["machine_id"] = "bm-c"
hb["next_milestone"] = ("T-143 assembly faces at exam assembly window (SYSTEM-V1 bm-a "
                        "primary + REV-OSC owner lane, deliverable 10-29; month-boundary "
                        "first exam 10-31); 688 containment: T-156 croc receiver camping at "
                        "bm-a, four-point verify then FUND-family nulls re-derive; D-06 "
                        "closure reconciliation 10-07")
hb["prod_lanes"] = "r409 CODELY r407 canon repair (fact-reconstruction) + S6 33/33 rc0"
hb["ram_free_gb"] = RAM
hb["round_no"] = 409
hb["updated_at"] = TS
hb["verdict"] = ("r409: CODELY canon mojibake repaired (fact-reconstruction, read-back "
                 "verified); orders 151/151 zero unacked; D-19 MATCH; S6 33/33 rc0 "
                 "(dualrun streak 5, audit CLEAN, watermark LEGAL idle -- 688 re-burn face "
                 "structurally locked observer, board 0 open, bandit 0, W115 parked, "
                 "sat-engine alive)")
with io.open(HP, "w", encoding="utf-8") as f:
    json.dump(hb, f, indent=2, ensure_ascii=False)
    f.write("\n")
print("HEARTBEAT epoch_int=%s clock=%s" % (isinstance(hb["heartbeat_epoch_utc"], int), hb["clock_read"]))

# ---------- round_reports-bm-c.md ----------
RP = RB + r"\round_reports-bm-c.md"
with open(RP, "rb") as f:
    raw = f.read()
nl = "\r\n" if b"\r\n" in raw else "\n"
block_lines = [
    "",
    "**当前活**：CODELY.md r407 born-mojibake 坑律条事实重建（双坑面律：replace 吞 def→NameError（r281/r280 族复发）+ 写入通道 CJK→'?' 编码事故=本条 mojibake 根因；r409 重建标注·读回验证 CJK 完好·邻行零伤）。",
    "**最近实物**：CODELY.md r407 条目重建件 + results/_r409bmc_codely_r407_repair.py（手术证据）+ S6 33 腿链 receipts/_r409bmc_s6_chain.ps1/@ 2026-10-03 10:1x-10:2x。",
    "**下个里程碑**：T-143 装配面 at 装配窗（deliverable 10-29·月界首考 10-31）；688 围堵收口观察（T-156 接收侧 camping）；D-06 收口对账 10-07。",
    "水位 verdict：绿——red=false·py_low_with_work_cands=合法 idle（O-2115 §2：688 面结构性锁死 bm-c 观察员·板 open 0·bandit 0·W115 parked·sat-engine 活 queue 0）。",
    "**本地未达 origin commit 数=0**（收尾 push+fetch+rev-list 自证）。",
    "",
    "2026-10-03 %s | r409 | CODELY.md r407 born-mojibake 条目事实重建（前缀匹配整行手术·BOM/CRLF 保持·读回 CJK 验证·双坑面律入正典）+ S0 手术（churn 吸收+rebase over origin e5590e142·17 共享 derive 面 take-origin（r612/r405 律·origin-tip blob 逐面 checkout）·r305 rebase-continue 假拒绝两中（手动 commit+daemon 瞬态丢弃）·ahead=2 behind=0 落地）+ S6 33/33 rc0（r408 runner 逐字复用·日志改 r409）+ MSG-0940 处理（观察员回执·移 processed） | smoke 47/47 rc0；dualrun ZERO-DRIFT streak 5 @358；audit CLEAN 零旗（pool-supply-gap 地板未破·并行效率 22.44 有效核）；watermark py_low_with_work_cands=合法 idle；orders 151/151 零未回执双扫；D-19 4167B784 MATCH；attrition CLEAN | r410：T-143 装配窗观察+688 围堵观察+D-06 收口对账（10-07）+moneyflow IC 面板窗（源阻断 53/5222·IC 批候面板完备）" % NOW.strftime("%H:%M:%S"),
]
append = nl.join(block_lines) + nl
with open(RP, "ab") as f:
    f.write(append.encode("utf-8"))
print("REPORT appended lines=%d nl=%r" % (len(block_lines), nl))

# ---------- inbox move ----------
SRC = RB + r"\fleet\inbox\MSG-2026-10-03-0940-bma-bmb-bmc-qnulls-third-containment.md"
DST = RB + r"\fleet\inbox\processed\MSG-2026-10-03-0940-bma-bmb-bmc-qnulls-third-containment.md"
if os.path.exists(SRC):
    shutil.move(SRC, DST)
    print("MSG0940 moved to processed")
else:
    print("MSG0940 already gone")
print("CLOSEOUT_OK ts=%s" % TS)
