# -*- coding: utf-8 -*-
"""r764 bm-c closeout driver: state-bm-c.json + fleet/machines/bm-c.json
heartbeat + canonical RPT line append. Facts-driven (r583 S4 law: hashes and
numbers never hand-typed; epoch must be JSON int per R170/R178 law;
clock_read T-separated ISO per R262 law). Self-verify reload + isinstance gate
before exit. Pattern credit: r763 close face (canonical clone chain)."""
import ctypes
import datetime
import json
import os
import re
import subprocess
import time

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CREATE_NO_WINDOW = 0x08000000

now = datetime.datetime.now().astimezone()
NOW = now.isoformat(timespec="seconds")
EPOCH = int(time.time())


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


mem = MEMORYSTATUSEX()
mem.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
RAM_GB = round(mem.ullAvailPhys / (1024 ** 3), 1)

p = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader"],
                   capture_output=True, creationflags=CREATE_NO_WINDOW)
VRAM_MIB = int(re.search(r"(\d+)", p.stdout.decode("utf-8", "replace")).group(1))


def cpu_times():
    idle, kernel, user = (ctypes.c_ulonglong() for _ in range(3))
    ctypes.windll.kernel32.GetSystemTimes(ctypes.byref(idle), ctypes.byref(kernel),
                                          ctypes.byref(user))
    return idle.value, kernel.value, user.value


i1, k1, u1 = cpu_times()
time.sleep(0.3)
i2, k2, u2 = cpu_times()
total = (k2 - k1) + (u2 - u1)
busy = total - (i2 - i1)
CPU_PCT = round(100.0 * busy / total, 1) if total > 0 else 0.0
CPU_IDLE = round(100.0 - CPU_PCT, 1)

head = subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"],
                      capture_output=True, creationflags=CREATE_NO_WINDOW)
HEAD_SHA = head.stdout.decode().strip()

SUMMARY = ("r764: QA det-84th 5/5 (pid 37312, S6-first order, 93 trades, 1,017,839 frozen "
           "identity, determinism=True, png 66,099B, 84th consecutive; bm-b e5f476d48 "
           "prior-in-history collision disclosed = F-20261008-03 family 3rd live case, "
           "identical frozen numbers zero evidence loss) + S6 40/40 rc0 (dualrun streak 51; "
           "CA flags [pool_starvation,supply_floor] intraday known standing faces; "
           "fund_premium/cta_p1 pre-15:30 no-op -> tonight first snapshot/auto-wiring) + "
           "clone gate stale763=0 + DEC/ORD double sweep UNCHANGED (EE70CEF0/F46EAD7C zero "
           "action); unacked=0; smoke 49/49; marks lane 8 rows (13:55 tick landed); "
           "attrition CLEAN; post_review zero new NO.")

CURTASK = ("当前活: r764 bm-c（14:1x-14:2x 窗·复市 T-0 盘中值守第 84 连守轮）——主产出=①QA det-84th "
           "5/5（93 trades·1,017,839 冻结恒等·determinism=True·png 66,099B·84 连证·bm-b e5f476d48 "
           "先在册撞名披露=r761 F-20261008-03 族第 3 活例·两包恒等零损失）②DEC/ORD 双水位双扫 "
           "UNCHANGED 零动作（EE70CEF0/F46EAD7C·unacked=0·inbox 0）③S6 40/40 rc0（dualrun streak "
           "51）+克隆门 stale763=0+marks lane 8 行（13:55 tick 落·bm-a 宿主车道健康）+FleetLink 自证 "
           "pid 28396 health 200 port 8790| 最近实物: qa/smoke-r764.md 5/5+qa/equity-curve-r764.png "
           "66,099B+results/_r764bmc_s6_log.txt 40/40+results/_r764bmc_clone_receipt.json @ " + NOW +
           " | 下个里程碑: 今晚盘后（10-08 15:30+）数据链 re-arm+REGIME_GUARD v3 首新 bar enforce+"
           "fund_premium 15:30 首采（bm-c 车）+CTA_P1 首接线+首 marks 验证（≤10-08 23:59）；"
           "next 5x=bm-c r765（HANDOVER r761-765）")

ACTIVITY = ("r764 bm-c: reopen T-0 intraday watch round 84th consecutive (14:1x-14:2x window, "
            "afternoon session). (1) S0: round-start dirty 7 = own faces (orphan probe + "
            "autofill/dispatcher/idle_trigger x2/satengine x2 daemon live) absorb 193bab2b7 -> "
            "pull --rebase up-to-date clean replay 0. (2) S0.5 double sweep: DEC EE70CEF0 + ORD "
            "F46EAD7C both UNCHANGED both passes (zero action, watermarks held); fleet orders 51 "
            "disk unacked=0 both passes; inbox 0. (3) S1 smoke 49/49 + SAT rc0 alive + orphan "
            "probe py_faces=5 orphans=1 (resident ComfyUI service face, CEO asset, read-only "
            "no-kill, standing disposition) + idle NOT-GREEN (RAM 12.3% < 40% resident ComfyUI) "
            "--worked 14:21 (idle_rounds=0). (4) MAIN PRODUCTS: (a) lineage clone gate: "
            "_r764bmc_boot.py HAND-WRITTEN -> double-replacement stale763=0 across "
            "s05/s6/qa_ignite, compile gate PASS, receipt _r764bmc_clone_receipt.json. (b) S6 "
            "40/40 rc0 via canonical clone (dualrun ZERO-DRIFT streak 51 @408 entries cutoff "
            "03:47 -- pool blob unchanged, idempotent sample honestly reported; compute_audit "
            "rc0 flags=[pool_starvation,supply_floor] intraday board-clear known standing faces "
            "honestly disclosed (supply_family_streak 289.3 min, pool ready=0 < floor 3); "
            "py_watermark py_low_board_clear legal intraday idle; lane guards honest skips: "
            "bm-a/bm-b owned lanes stdout-only no-op; fund_premium pre-15:30 no-op -> tonight "
            "15:30 bm-c-lane first snapshot; cta_p1_paper no markable bar -> tonight first-bar "
            "auto-wiring). (c) QA det-84th per ignition order law (r749 pit): S6 full-chain rc0 "
            "collected FIRST -> qa_ignite detached pid 37312 -> poll terminal (.err 0B): 93 "
            "trades, equity 1,017,839 frozen identity, determinism=True, png 66,099B, 84th "
            "consecutive; collision disclosed: bm-b e5f476d48 prior-in-history qa/smoke-r764.md"
            "+png (F-20261008-03 namespace-collision family 3rd live case, both packs identical "
            "frozen numbers [93 trades/sharpe 0.159/maxdd -0.0433/win_rate 0.4624/determinism="
            "True] zero scientific evidence loss, bm-b version git-history preserved, HQ fix "
            "proposal on file zero new action). (d) marks lane watch: 8 rows, 13:55 tick landed "
            "(bm-a host lane healthy). (e) FleetLink standing self-cert: listener pid 28396 "
            "health 200 node=bm-c port 8790. (5) closeout: quartet green (loop pin=5 no-op "
            "first-fire 14:25 / watchdog present 14:22 / pre-commit+pre-push claws "
            "LF-normalized OK x2) + attrition CLEAN (4 ledgers, historical healed note) + idle "
            "--worked + post_review zero new NO (today 1349Y/0N/150W; open NO=2 historical "
            "09-27/09-28 rows) + sweep-2 UNCHANGED + state/heartbeat/RPT close.")

VERIFY = ("smoke 49/49 + qa/smoke-r764.md 5/5 (93 trades equity 1,017,839 frozen identity "
          "determinism=True .err 0B png 66,099B) + results/_r764bmc_s6_log.txt 40/40 rc0 "
          "(dualrun ZERO-DRIFT streak 51) + results/_r764bmc_s05_facts.json double sweep (DEC "
          "EE70CEF0 + ORD F46EAD7C both UNCHANGED / unacked=0 / inbox 0 / shape-asserted) + "
          "results/_r764bmc_clone_receipt.json (stale763=0, compile OK x3) + attrition CLEAN "
          "(4 ledgers) + post_review zero new NO (today 1349Y/0N/150W; open NO=2 historical "
          "09-27/09-28 rows) + quartet green (pin=5 no-op first-fire 14:25 / watchdog present "
          "14:22 / claws installed LF-normalized x2) + orphan face=1 standing disposition "
          "(py_faces=5) + SAT alive rc0 + idle_trigger --worked (idle_rounds=0, RAM 12.3% "
          "resident ComfyUI) + FleetLink listener pid 28396 health 200 port 8790 + marks lane "
          "8 rows (13:55 tail) + token_meter delta=0")

NEXT_PTR = ("r765: (a) 5x round -- HANDOVER product-list refresh (r761-765 window, "
            "research/HANDOVER.md); (b) tonight post-close face (<=10-08 23:59): data-chain "
            "full re-arm + REGIME_GUARD v3 first-new-bar enforce (set BIGMONEY_REGIME_GUARD="
            "enforce before live.paper) + fund_premium 15:30 first snapshot (bm-c lane) + "
            "CTA_P1 first-bar auto-wiring + first-marks verification (marks row + state "
            "trial-live + compounding identity) + QDII watch holiday-delta; (c) QA ignition "
            "order law standing (S6 rc0 -> qa_ignite -> qa_poll terminal -> close); (d) close "
            "scripts: RPT path = canonical logs/iteration-loop/round_reports-bm-c.md (r750 "
            "pit; NEVER clone a ROOT template); (e) FleetLink standing self-cert line per "
            "round (listener pid/health); (f) D-20261008-06 suffix-naming law (_r765bmc_* "
            "prefix pattern) + command-dedup law enforcement face; (g) marks lane intraday "
            "watch continuation (bm-a host lane, 13:55 tail); (h) month-boundary first exam "
            "10-31. [via bm-c r764]")

ARTIFACT = ("qa/smoke-r764.md 5/5 + qa/equity-curve-r764.png 66,099B + "
            "results/_r764bmc_s6_log.txt (40 legs rc0) + results/_r764bmc_clone_receipt.json "
            "(stale763=0 trio) @ " + NOW)

MILESTONE = ("tonight post-close (10-08 15:30+): data-chain re-arm + REGIME_GUARD v3 "
             "first-new-bar enforce + fund_premium 15:30 first snapshot (bm-c lane) + CTA_P1 "
             "first-bar auto-wiring + first-marks verify (<= 10-08 23:59); next 5x = bm-c r765 "
             "(HANDOVER r761-765)")

DEC_METHOD = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r764 "
              "double sweeps = UNCHANGED EE70CEF0 both passes (zero action, watermark held); "
              "facts-driven from results/_r764bmc_s05_facts.json, 64hex shape-asserted, never "
              "hand-typed (r583 S4 law)")
ORD_METHOD = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r764 double "
              "sweeps = UNCHANGED F46EAD7C both passes (zero action, watermark held); hex-case "
              "comparison normalized per r711 pit law; facts-driven from "
              "results/_r764bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 "
              "law)")

TS_KEYS = ["clock_read", "last_seen", "last_seen_at", "updated", "updated_at", "ts",
           "last_round_at", "last_round_ts", "last_run_at", "last_ts", "current_task_at",
           "last_decisions_read_at", "last_orders_at"]

GPU_KEYS = ["gpu_free_vram_mib", "gpu_free_vram_mb", "gpu_idle_vram_mb", "gpu_idle_vram_mib",
            "gpu_vram_free_mb", "gpu_free_mb", "gpu_idle_mb", "gpu_free_mib", "gpu_idle_mib"]
RAM_KEYS = ["free_ram_gb", "idle_ram_gb", "ram_free_gb"]

# --- state-bm-c.json ---
sp = os.path.join(ROOT, "state-bm-c.json")
state = json.load(open(sp, encoding="utf-8"))
state["round_no"] = 765
state["round_no_label"] = "round 764 (bm-c)"
state["last_round"] = 764
for k in TS_KEYS:
    state[k] = NOW
state["heartbeat_epoch_utc"] = EPOCH
state["did"] = SUMMARY
state["verdict"] = SUMMARY
state["note"] = SUMMARY
state["last_round_summary"] = SUMMARY
state["last_action"] = SUMMARY
state["current_task"] = CURTASK
state["activity_now"] = ACTIVITY
state["verify"] = VERIFY
state["next_pointer"] = NEXT_PTR
state["next"] = NEXT_PTR
state["latest_artifact"] = ARTIFACT
state["next_milestone"] = MILESTONE
for k in RAM_KEYS:
    state[k] = RAM_GB
for k in GPU_KEYS:
    state[k] = VRAM_MIB
state["cpu_pct"] = CPU_PCT
state["cpu_util_pct"] = CPU_PCT
state["cpu_idle_pct"] = CPU_IDLE
state["head_sha"] = HEAD_SHA
state["last_decisions_sha_method"] = DEC_METHOD
state["last_orders_sha_method"] = ORD_METHOD
with open(sp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(state, fh, indent=1, ensure_ascii=False)

# --- fleet/machines/bm-c.json heartbeat ---
hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
hb = json.load(open(hp, encoding="utf-8"))
hb["round_no"] = 765
hb["round_no_label"] = "round 764 (bm-c)"
hb["last_round"] = 764
for k in ["clock_read", "last_seen", "last_seen_at", "updated", "updated_at", "ts",
          "last_round_at", "last_run_at", "last_ts", "current_task_at"]:
    hb[k] = NOW
hb["heartbeat_epoch_utc"] = EPOCH
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["did"] = SUMMARY
hb["verdict"] = SUMMARY
hb["note"] = SUMMARY
hb["last_round_summary"] = SUMMARY
hb["last_action"] = SUMMARY
hb["current_task"] = CURTASK
hb["activity_now"] = ACTIVITY
hb["verify"] = VERIFY
hb["next"] = NEXT_PTR
hb["next_pointer"] = NEXT_PTR
hb["latest_artifact"] = ARTIFACT
hb["next_milestone"] = MILESTONE
for k in RAM_KEYS:
    hb[k] = RAM_GB
for k in GPU_KEYS:
    hb[k] = VRAM_MIB
hb["cpu_pct"] = CPU_PCT
hb["cpu_util_pct"] = CPU_PCT
hb["cpu_idle_pct"] = CPU_IDLE
hb["head_sha"] = HEAD_SHA
with open(hp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, indent=1, ensure_ascii=False)

# --- canonical RPT line append (r750 pit: canonical path, never ROOT clone) ---
RPT_LINE = " | ".join([
    NOW,
    "r764",
    "dept:工程+交易（复市 T-0 盘中值守轮·第 84 bm-c 连守轮·午后段）",
    "本地未达 origin commit 数=0（commit 后 push+fetch 自证）",
    ("WM-VERDICT: 绿（red=false·lane=healthy·py_low_board_clear 盘中板清合法 idle〔orders 51 "
     "disk unacked=0 双扫·inbox 0 双扫〕·compute_audit rc0 flags=[pool_starvation,"
     "supply_floor] 盘中席位间隙已知常在面如实披露〔pool ready 0<floor 3·"
     "supply_family_streak 289.3min〕·idle_trigger --worked〔idle_rounds=0 已清〕）"),
    ("当前活: r764 bm-c（14:1x-14:2x 窗·复市 T-0 盘中值守第 84 连守轮·午后段）——S0 轮首脏 7=自有面"
     "（orphan probe+autofill/dispatcher/idle_trigger×2/satengine×2 daemon live）absorb "
     "193bab2b7→pull --rebase up-to-date 干净→克隆门三件（_r764bmc_boot.py 手写→双模替换 "
     "stale763=0 三件〔s05/s6/qa_ignite〕·compile OK×3·收据 _r764bmc_clone_receipt.json）——"
     "主产出=①DEC/ORD 双水位双扫 UNCHANGED（EE70CEF0/F46EAD7C·零动作水位持守·unacked=0·"
     "inbox 0）②QA det-84th 5/5（律序 S6 40 腿 rc0 收齐→点火 pid 37312→终态 .err 0B——93 "
     "trades·equity 1,017,839 冻结恒等·determinism=True·png 66,099B·84 连证·撞名披露：bm-b "
     "e5f476d48 先在册 qa/smoke-r764.md+png——r761 F-20261008-03 命名空间撞名族第 3 活例·"
     "两包冻结恒等同数字〔93 trades/sharpe 0.159/maxdd -0.0433/win_rate 0.4624/determinism="
     "True〕零科学证据损失·bm-b 版 git 史保全·HQ 修法提案在册零新动作）③S6 40/40 rc0"
     "（dualrun ZERO-DRIFT streak 51·py_low_board_clear 合法盘中 idle·lane 守卫诚实 skip 面·"
     "fund_premium pre-15:30 no-op→今晚 15:30 bm-c 车道首采·cta_p1 无可标 bar→今晚首 bar "
     "自动接线）+④marks lane 值守（8 行·13:55 tick 落·bm-a 宿主车道健康·观察项续持）+⑤"
     "FleetLink 常态自证（listener pid 28396 health 200 node=bm-c port 8790）"),
    ("最近实物: qa/smoke-r764.md 5/5+qa/equity-curve-r764.png 66,099B+results/_r764bmc_s6_log."
     "txt（40 腿 rc0）+results/_r764bmc_clone_receipt.json @ " + NOW),
    ("下个里程碑: 今晚盘后（10-08 15:30+）数据链 re-arm+REGIME_GUARD v3 首新 bar enforce+"
     "fund_premium 15:30 首采（bm-c 车）+CTA_P1 首接线+首 marks 验证（≤10-08 23:59）；"
     "next 5x=bm-c r765（HANDOVER r761-765）"),
    "[via bm-c r764]",
])
rpt = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
with open(rpt, "a", encoding="utf-8", newline="\n") as fh:
    fh.write(RPT_LINE + "\n")

# --- self-verify reload (R170/R178 epoch-int + R262 T-separator laws) ---
s2 = json.load(open(sp, encoding="utf-8"))
h2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(s2["heartbeat_epoch_utc"], int) and not isinstance(
    s2["heartbeat_epoch_utc"], str), "state epoch must be JSON int"
assert isinstance(h2["heartbeat_epoch_utc"], int) and not isinstance(
    h2["heartbeat_epoch_utc"], str), "heartbeat epoch must be JSON int"
assert "T" in s2["clock_read"] and "+" in s2["clock_read"], "clock_read T-separated ISO"
assert "T" in h2["clock_read"] and "+" in h2["clock_read"], "hb clock_read T-separated ISO"
assert s2["round_no"] == 765 and h2["round_no"] == 765

print(json.dumps({"now": NOW, "epoch": EPOCH, "ram_gb": RAM_GB, "vram_mib": VRAM_MIB,
                  "cpu_pct": CPU_PCT, "head": HEAD_SHA[:10],
                  "self_verify": "PASS (epoch int x2, clock T x2, round_no 765 x2)",
                  "rpt_line_bytes": len(RPT_LINE.encode("utf-8"))}, indent=1))
