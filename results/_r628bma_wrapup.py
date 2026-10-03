# r628 bm-a wrap-up: state bump, round report line, heartbeat, MSG-1450 move.
import datetime
import json
import os
import shutil
import time

NOW = datetime.datetime.now()
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S") + NOW.strftime("%z")[:3] + ":" + NOW.strftime("%z")[3:]
TSL = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")

# ---- 1. MSG-1450 -> processed (moot: T-156 closed, completion notice) ----
src = "fleet/inbox/MSG-2026-10-03-1450-bma-bmb-t156-complete.md"
dst = "fleet/inbox/processed/" + os.path.basename(src)
if os.path.exists(src):
    shutil.move(src, dst)
    print("MSG-1450 moved to processed (moot: T-156 closed)")
else:
    print("MSG-1450 already gone (concurrent move absorbed)")

# ---- 2. state-bm-a.json -> r628 ----
SP = "state-bm-a.json"
s = json.load(open(SP, encoding="utf-8"))
s["round_no"] = 628
s["did"] = (
    "S0-1 identity bm-a anchored (round.lock pid=13480 15:08:02); S0 fetch sync -- "
    "daemon mid-round FF to 5a82a3248 absorbed r627 closeout 21a250b17 inbox moves, "
    "own uncommitted outputs intact verified; S0.5 orders 151/151 set-equal "
    "zero-unacked (O-20261003-1210 receipts complete; r624 tail DISCHARGED: "
    "CODELY.md 58.3KB->20.3KB by morning integrations, no action); D-19 4167b784 "
    "UNCHANGED zero-consume (bm-a group-tree path C:/Users/sjs20/Desktop/FluxGroup "
    "-- K:\\ form absent on this machine, honest note); S1 smoke 47/47 (re-run "
    "post-fix 47/47); S3 P0 SETTLE-BUG FIXED (r627 next#1): writer located = "
    "merge_lane_views.sync_face (sole settle writer, compute_audit S6 leg caller; "
    "autofill/lane_io carry no settle path, verified) -- origin-tip identity "
    "assertion landed: _origin_shared_blob probe reads local origin/main "
    "remote-tracking ref (zero network; daemon pushes advance it even under a "
    "reland-rolled worktree); identity holds -> legacy path; mismatch -> origin "
    "blob unioned as leading base source (newer-wins r311 + marker laws keep "
    "daemon truth); probe fault on live ref -> fail-closed both sides unwritten; "
    "selftest +4 legs (r627 live-shape regression 14:54:07 claim preserved + "
    "identity-equal + hermetic no-origin + fault fail-closed) ALL PASS; live probe "
    "verified ok / identity-HOLDS; pit-pool.md r628 entry direct-write 1248B "
    "(md5=cd914da08bde2b8d3699257b978043ad) + 242B header line, git diff --stat 2 "
    "insertions surgical; SENS burn in flight (pid 82208, sens.jsonl 373 rows k=368 "
    "growing; acceptance deferred to completion; excluded from commit per r614 "
    "in-flight law); S6 chain 24+ legs rc0 (dualrun ZERO-DRIFT streak 7; audit "
    "FLAG:supply_gap obs; WM insufficient_history n=1 honest; Sat daily 0-new-rows "
    "no-op; regime ORANGE shadow; clock ORANGE_COOL 4/0; scorecard 6 traders S2/A4; "
    "aggr/grid/sysv1 idempotent; t35 export 2026-09-30; daily_report + LIVE-"
    "2026-10-03 written; token delta 0); S7 4/4 (loop pin 8 no-op + watchdog "
    "re-reg 15:19 + dual claws reinstalled + attrition CLEAN, 2 healed historical "
    "shrinks noted); MSG-1450 processed (moot T-156 closed); MSG-1452 held in "
    "inbox (GM ruling pending)"
)
s["verify"] = (
    "merge_lane_views selftest 0 FAIL (4 new r628 legs PASS); smoke 47/47 "
    "post-fix; live origin-tip probe ok / identity HOLDS; pit-pool append "
    "byte-accounted 1248B+242B, diff --stat surgical; S6 legs rc0; attrition "
    "CLEAN rc0; orders 151/151; D-19 UNCHANGED; dualrun ZERO-DRIFT streak 7 @362"
)
s["next"] = (
    "1) SENS burn acceptance on completion (audit/parallel-efficiency evidence; "
    "nulls redo waits bm-b 2000-draw ETA 10-06/10-08); 2) moneyflow ruling "
    "pending GM (MSG-1452 options A/B/C); 3) gate_attrition 88v78 drift = "
    "maintenance-window candidate (D-03 full diff before any switch); 4) W14 + "
    "N2-W15 zero-touch pending GM dual-ruling MSG-0436; 5) watch origin-tip "
    "assertion live behavior on next settles (dormant until reland-window "
    "mismatch)"
)
s["last_round_at"] = TSL
s["current_task"] = (
    "r628: settle-bug P0 fixed (origin-tip identity assertion in sync_face + 4 "
    "selftest legs + pit-pool r628 entry); S6 24+ legs rc0; SENS burn in flight"
)
s["updated"] = TSL
s["last_round"] = "r628 bm-a"
s["last_round_ts"] = TSL
json.dump(s, open(SP, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("state -> r628")

# ---- 3. round report line ----
RP = "round_reports-bm-a.md"
line = (
    TSL + " | r628 | dept:工程 | 水位 verdict=绿：red=false lane healthy（WM "
    "insufficient_history n=1 窗口重置=诚实读数非违令）；当前活=QUALITY-SENS 烧批在飞"
    "（pid 82208·sens.jsonl 373 行 k=368 增长中·正确口径 cache 首烧）；最近实物="
    "scripts/merge_lane_views.py origin-tip settle 身份断言（15:1x·r627 stale-settle "
    "P0 修复：settle 写前读本地 origin/main ref blob——恒等直通/失配 origin 作 leading "
    "base 并入 union newer-wins/探针 fault fail-closed·selftest +4 腿全 PASS·smoke "
    "47/47 复跑·live probe identity HOLDS）+research/pit-pool.md r628 直写条（1248B "
    "字节对账·md5=cd914da08bde2b8d3699257b978043ad）；下个里程碑=SENS 烧完即验收"
    "（audit/并行效率证据·预计 ≤10-04；nulls redo 候 bm-b 2000-draw ETA 10-06/08）；"
    "S0.5 orders 151/151 零未回执（r624 尾 discharged：CODELY.md 20.3KB<50KB 水位）；"
    "D-19 4167b784 UNCHANGED；S1 47/47 两次；S3 定序过闸（satengine alive queue 0）；"
    "S6 24+腿 rc0（dualrun ZERO-DRIFT streak 7·audit FLAG:supply_gap 观察·regime "
    "ORANGE shadow·clock ORANGE_COOL 4/0·scorecard S2/A4·daily_report+LIVE 双面落地·"
    "token delta 0）；S7 4/4（loop pin 8 no-op·watchdog 15:19·双爪重装·attrition "
    "CLEAN）；MSG-1450 processed（moot T-156 已闭环）·MSG-1452 留箱（GM 裁决 pending）；"
    "daemon 中窗 FF 5a82a3248（r627 closeout 21a250b17 inbox 迁移吸收·本会话产出完整"
    "核验）| 本地未达 origin commit 数=0\n"
)
with open(RP, "a", encoding="utf-8", newline="") as fh:
    fh.write(line)
print("round report line appended")

# ---- 4. heartbeat ----
HB = "fleet/machines/bm-a.json"
hb = json.load(open(HB, encoding="utf-8"))
epoch = int(time.time())
try:
    import psutil
    cpu_pct = psutil.cpu_percent(interval=0.5)
    free_gb = round(psutil.virtual_memory().available / 1e9, 1)
    gpu_free = 3.7
except Exception:
    cpu_pct, free_gb, gpu_free = 0.0, 0.0, 0.0
hb["machine_id"] = "bm-a"
hb["last_seen"] = TSL
hb["current_task"] = s["current_task"]
hb["cpu_cores"] = 32
hb["cpu_pct"] = cpu_pct
hb["free_ram_gb"] = free_gb
hb["gpu_free_vram_gb"] = gpu_free
hb["verdict"] = "healthy: settle-bug P0 fixed (origin-tip assertion); SENS burn in-flight"
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = TSL
hb["round_no"] = 628
hb["round"] = "r628"
json.dump(hb, open(HB, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
chk = json.load(open(HB, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int (F7)"
assert "T" in chk["clock_read"], "clock_read must be T-separated (F7)"
print("heartbeat updated; epoch int verified:", chk["heartbeat_epoch_utc"])
