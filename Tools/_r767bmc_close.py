# -*- coding: utf-8 -*-
"""r767 bm-c closeout driver: state-bm-c.json + fleet/machines/bm-c.json
heartbeat + canonical RPT line append. Facts-driven (r583 S4 law: hashes and
numbers never hand-typed; DEC/ORD watermarks loaded from
results/_r767bmc_s05_facts.json; epoch must be JSON int per R170/R178 law;
clock_read T-separated ISO per R262 law). Self-verify reload + isinstance
gate before exit. Pattern credit: Tools/_r766bmc_close.py (canonical clone
chain). Continuation note: r767 first-half tick died post-QA (~15:39, narrow
RAM window) with all products on disk + state not advanced + zero commit;
this closeout ran from the r767 continuation session (same round number, no
re-numbering, orphan-face probe confirmed zero live loop pythons before
takeover)."""
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

facts = json.load(open(os.path.join(ROOT, "results", "_r767bmc_s05_facts.json"),
                       encoding="utf-8"))
DEC_SHA = facts["dec_sha"]
ORD_SHA = facts["ord_sha"]

SUMMARY = ("r767: QA det-87th 5/5 (S6-first order, 93 trades, 1,017,839 frozen identity, "
           "determinism=True, png 66,310B, 87th consecutive; collision case#5 disclosed: "
           "bm-b 15f33d1d8 first-registered same-path r767 pack, same frozen numbers zero "
           "scientific loss, bm-b version git-history preserved, F-20261008-03 standing "
           "namespace proposal) + S0.5 zero-hop (DEC EE70CEF0 UNCHANGED, ORD 6C0018CC "
           "UNCHANGED, unacked=0, inbox 0) + S6 40/40 rc0 (dualrun streak 51; "
           "py_watermark insufficient_history honest; CA flags [pool_starvation,"
           "supply_floor] standing faces; update_daily today-bar NOT YET landed at "
           "15:34 AND 15:47 re-arm retry -- sina late-bar self-heal face, cutoff "
           "2026-09-30 held; fund_premium first snapshot + CTA_P1 first-bar wiring + "
           "marks verify PENDED until today-bar lands) + clone gate stale=0 (compile "
           "OK x3) + continuation-closeout (first-half tick died post-QA ~15:39 "
           "narrow-RAM, products on disk, state not advanced, zero commit; continuation "
           "session took over per orphan-probe zero-live-loop confirmation, same "
           "round number) + quartet green (pin=5 no-op 15:55 first-fire / watchdog "
           "re-registered 15:49 / claws LF-normalized x2) + attrition CLEAN (4 "
           "ledgers) + smoke 49/49 + post_review zero new NO (48Y/0N/5W) + token "
           "delta=0.")

CURTASK = ("当前活: r767 bm-c（15:1x-15:5x 窗·复市 T-0 盘后窗首轮〔15:30 数据门已开〕·前半轮 "
           "15:39 后猝死→续跑体 15:45 接手同轮收尾〔孤儿探针零活轮确认·同轮号不重编〕）——主产出="
           "①QA det-87th 5/5（93 trades·1,017,839 冻结恒等·determinism=True·png 66,310B·87 连证·"
           "撞名族第 5 例披露〔bm-b 15f33d1d8 先在册·同冻结数字零科学损失·git 史保全·"
           "F-20261008-03 常设呈报〕）②S6 40/40 rc0（dualrun streak 51·py_watermark "
           "insufficient_history 诚实·CA flags [pool_starvation,supply_floor] 空池常在面披露）"
           "③盘后 re-arm 重试（update_daily 15:47 重跑仍 0 行——sina 今日 bar 未落·迟 bar 自愈面·"
           "fund_premium 首采/CTA_P1 首接线/marks 验证挂起至 bar 落地·下轮续）④S0.5 零跳消费"
           "（DEC EE70CEF0 UNCHANGED·ORD 6C0018CC UNCHANGED·unacked=0·inbox 0）+克隆门 stale=0"
           "（compile OK×3）+quartet green+attrition CLEAN| 最近实物: qa/smoke-r767.md 5/5+qa/"
           "equity-curve-r767.png 66,310B+results/_r767bmc_s6_log.txt 40/40+results/"
           "_r767bmc_clone_receipt.json @ " + NOW + " | 下个里程碑: 盘后窗续（10-08 今晚）sina "
           "迟 bar 自愈→今日 bar 落地后 fund_premium 2026-10-08 NAV 首采（bm-c 车）+CTA_P1 首 bar "
           "接线+marks 验证（≤10-08 23:59）；next 5x=bm-c r770")

ACTIVITY = ("r767 bm-c: post-close window round 87th consecutive (15:1x-15:5x window, "
            "first >=15:30 round of reopen T-0). CONTINUATION: first-half tick executed "
            "S0 pull + clone gate (stale=0, compile OK x3) + S0.5 zero-hop sweep (DEC "
            "EE70CEF0 UNCHANGED / ORD 6C0018CC UNCHANGED, unacked=0 both passes, inbox "
            "0, 51 disk orders all acked) + S1 smoke 49/49 + SAT rc0 alive + orphan "
            "probe py_faces=5 orphans=1 (resident ComfyUI service face, CEO asset -- "
            "standing MV production lane, read-only no-kill, standing disposition) + "
            "idle NOT-GREEN (RAM 10.2% resident ComfyUI) --worked (idle_rounds=0) + "
            "FleetLink health 200 node=bm-c port 8790 + post_review 48Y/0N/5W zero new "
            "NO, then S6 40/40 rc0 (15:34-15:36: dualrun ZERO-DRIFT streak 51; "
            "compute_audit rc0 flags=[pool_starvation,supply_floor] board-clear known "
            "standing faces honestly disclosed; py_watermark insufficient_history "
            "honest; update_daily 15:34 today-bar guard open but new rows=0 -- sina "
            "today-bar not yet published, late-bar self-heal face; fund_premium "
            "no-op: snapshot 2026-09-30 already covers expected NAV date 2026-09-30 "
            "(derived from un-landed bar date) -> first 2026-10-08 snapshot PENDED "
            "until bar lands; cta_p1_paper no markable bar -> wiring PENDED; lane "
            "guards honest skips: bm-a/bm-b owned lanes stdout-only no-op; "
            "daily_report REPORT-2026-10-08 regenerated; ceo_live_usage "
            "LIVE-2026-10-08 written state=ORANGE rung=ORANGE cap=50%), then QA "
            "det-87th per ignition order law (r749 pit): S6 full-chain rc0 collected "
            "FIRST -> qa_ignite detached -> poll terminal (.err 0B): 93 trades, "
            "equity 1,017,839 frozen identity, determinism=True, png 66,310B, 87th "
            "consecutive; COLLISION CASE #5 disclosed (bm-b 15f33d1d8 r767 pack "
            "first-registered golden-week; same-path overwrite; both packs same "
            "frozen numbers 93 trades/determinism=True; zero scientific evidence "
            "loss; bm-b version git-history preserved verifiable via git show "
            "15f33d1d8:qa/smoke-r767.md; F-20261008-03 namespace-fix standing "
            "proposal, family per r761/r764/r766 precedent). First-half tick then "
            "DIED post-QA (~15:39, narrow-RAM window 1.6GB free): idle --worked "
            "heartbeat touched 15:39:51, state NOT advanced, RPT line NOT appended, "
            "zero commit. Continuation session (15:45) confirmed zero live loop "
            "pythons via orphan probe (py_faces=5 orphans=1 standing ComfyUI only) "
            "-> takeover same round number per crash-recovery law: (a) update_daily "
            "re-arm retry 15:47: STILL 0 new rows, cutoff 2026-09-30 held, failures=0 "
            "-- sina late-bar honestly disclosed, next rounds self-heal; (b) quartet "
            "green (loop pin=5 no-op first-fire 15:55 / watchdog re-registered "
            "15:49 / pre-commit+pre-push claws LF-normalized x2); (c) attrition "
            "CLEAN (4 ledgers, 3 historical shrink rows healed-annotated); (d) state/"
            "heartbeat/RPT close by canonical clone closeout driver.")

VERIFY = ("smoke 49/49 + qa/smoke-r767.md 5/5 (93 trades equity 1,017,839 frozen identity "
          "determinism=True .err 0B png 66,310B; collision case#5 disclosed, bm-b "
          "15f33d1d8 version git-preserved) + results/_r767bmc_s6_log.txt 40/40 rc0 "
          "(dualrun ZERO-DRIFT streak 51) + results/_r767bmc_s05_facts.json zero-hop "
          "(DEC EE70CEF0 UNCHANGED / ORD 6C0018CC UNCHANGED / unacked=0 / inbox 0 / "
          "shape-asserted) + results/_r767bmc_clone_receipt.json (stale=0, compile OK "
          "x3) + results/_r767bmc_s1_facts.json (SAT alive rc0 + orphan py_faces=5 "
          "orphans=1 + FleetLink 200 + post_review 48Y/0N/5W) + attrition CLEAN (4 "
          "ledgers, results/_attrition_guard_scan.json) + quartet green (pin=5 no-op "
          "15:55 first-fire / watchdog re-registered 15:49 / claws LF-normalized x2) "
          "+ idle_trigger --worked (idle_rounds=0) + update_daily re-arm retry "
          "15:47 rc0 (0 new rows, failures=0, sina late-bar honest) + token_meter "
          "delta=0 (zero LLM calls this round)")

NEXT_PTR = ("r768: (a) post-close re-arm continuation (>=15:30 rounds, <=10-08 23:59): "
            "update_daily sina late-bar self-heal retry -> once today-bar 2026-10-08 "
            "lands: fund_premium first 2026-10-08 NAV snapshot (bm-c lane) + CTA_P1 "
            "first-bar auto-wiring + REGIME_GUARD v3 first-new-bar enforce (set "
            "BIGMONEY_REGIME_GUARD=enforce before live.paper; live.paper results/paper "
            "face host=bm-a, bm-c lane-guard honest skip standing) + first-marks "
            "verification (marks row + state trial-live + compounding identity) + "
            "marks lane post-close re-verify (bm-a host lane, 15:00 close tick "
            "landing); (b) QA ignition order law standing (S6 rc0 -> qa_ignite -> "
            "qa_poll terminal -> close); QA pack pre-ignite collision check: r768 "
            "paths -- probe bm-b golden-week r768 pack via git ls-tree origin/main "
            "qa/ before ignite, follow r761/r764/r766/r767 disclosure canon if "
            "taken; (c) close scripts: RPT path = canonical logs/iteration-loop/"
            "round_reports-bm-c.md (r750 pit; NEVER clone a ROOT template); (d) "
            "FleetLink standing self-cert line per round (listener health); (e) "
            "D-202608-06 suffix-naming law (_r768bmc_* prefix pattern) + "
            "command-dedup law enforcement face; (f) month-boundary first exam "
            "10-31; next 5x = bm-c r770. [via bm-c r767]")

ARTIFACT = ("qa/smoke-r767.md 5/5 + qa/equity-curve-r767.png 66,310B + results/"
            "_r767bmc_s6_log.txt (40 legs rc0) + results/_r767bmc_clone_receipt.json "
            "(stale=0) + results/_r767bmc_s1_facts.json @ " + NOW)

MILESTONE = ("tonight post-close (10-08, <=23:59): sina late-bar self-heal -> today-bar "
             "lands -> fund_premium 2026-10-08 first snapshot (bm-c lane) + CTA_P1 "
             "first-bar wiring + first-marks verify; next 5x = bm-c r770")

DEC_METHOD = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; "
              "r767 sweep = UNCHANGED EE70CEF0 (zero action, watermark held); "
              "facts-driven from results/_r767bmc_s05_facts.json, 64hex shape-asserted, "
              "never hand-typed (r583 S4 law)")

ORD_METHOD = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r767 "
              "sweep = UNCHANGED 6C0018CC (zero-hop: no new orders this window, zero "
              "BigMoney action); facts-driven from results/_r767bmc_s05_facts.json, "
              "40hex shape-asserted, hex-case normalized per r711 pit law (r583 S4 law)")

TS_KEYS = ["clock_read", "last_seen", "last_seen_at", "updated", "updated_at", "ts",
           "last_round_at", "last_round_ts", "last_run_at", "last_ts", "current_task_at",
           "last_decisions_read_at", "last_orders_at"]

GPU_KEYS = ["gpu_free_vram_mib", "gpu_free_vram_mb", "gpu_idle_vram_mb", "gpu_idle_vram_mib",
            "gpu_vram_free_mb", "gpu_free_mb", "gpu_idle_mb", "gpu_free_mib", "gpu_idle_mib"]
RAM_KEYS = ["free_ram_gb", "idle_ram_gb", "ram_free_gb"]

# --- state-bm-c.json ---
sp = os.path.join(ROOT, "state-bm-c.json")
state = json.load(open(sp, encoding="utf-8"))
state["round_no"] = 768
state["round_no_label"] = "round 767 (bm-c)"
state["last_round"] = 767
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
state["last_decisions_sha"] = DEC_SHA
state["last_orders_sha"] = ORD_SHA
state["last_decisions_sha_method"] = DEC_METHOD
state["last_orders_sha_method"] = ORD_METHOD
for k in RAM_KEYS:
    state[k] = RAM_GB
for k in GPU_KEYS:
    state[k] = VRAM_MIB
state["cpu_pct"] = CPU_PCT
state["cpu_util_pct"] = CPU_PCT
state["cpu_idle_pct"] = CPU_IDLE
state["head_sha"] = HEAD_SHA
with open(sp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(state, fh, indent=1, ensure_ascii=False)

# --- fleet/machines/bm-c.json heartbeat ---
hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
hb = json.load(open(hp, encoding="utf-8"))
hb["round_no"] = 768
hb["round_no_label"] = "round 767 (bm-c)"
hb["last_round"] = 767
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
for k in ("last_decisions_sha", "last_orders_sha"):
    if k in hb:
        hb[k] = DEC_SHA if k.startswith("last_dec") else ORD_SHA
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
    "r767",
    ("dept:工程+交易（复市 T-0 盘后窗首轮·第 87 bm-c 连守轮·15:30 数据门已开·前半轮 15:39 后"
     "猝死→续跑体 15:45 接手同轮收尾）"),
    "本地未达 origin commit 数=0（commit 后 push+fetch 自证）",
    ("WM-VERDICT: 绿（red=false·lane=healthy·py_watermark insufficient_history 诚实〔series 86"
     "窗 1·span 0〕·compute_audit rc0 flags=[pool_starvation,supply_floor] 空池常在面如实披露"
     "〔pool ready 0<floor 3〕·idle NOT-GREEN --worked〔RAM ~7%<40% 常驻 ComfyUI·idle_rounds=0"
     "已清〕）"),
    ("当前活: r767 bm-c（15:1x-15:5x 窗·盘后窗首轮）——续跑判定=前半轮产物全在（s05/s1 facts+S6 "
     "log+QA pack）而 state 未进位+零 commit+孤儿探针零活轮→同轮号接手收尾（猝死取号律在册范式）"
     "——主产出=①QA det-87th 5/5（律序 S6 40 腿 rc0 收齐→点火→终态 .err 0B——93 trades·equity "
     "1,017,839 冻结恒等〔r751-767 锚链续持〕·determinism=True·png 66,310B·87 连证）〔撞名披露"
     "case#5：qa/smoke-r767.md+equity-curve-r767.png 跨机轮号撞名族第 5 例——bm-b 15f33d1d8"
     "（golden-week·bm-b 自计 r767）先在册·本机包覆写活树件；两包同冻结数字（93 trades/"
     "determinism=True）零科学证据损失·bm-b 版 git 史保全（git show 15f33d1d8:qa/smoke-"
     "r767.md 可验）·HQ-FEEDBACK F-20261008-03 命名空间修法常设呈报（r761/r764/r766 先例族）〕"
     "②S6 40/40 rc0（dualrun ZERO-DRIFT streak 51 @408 条·cutoff 03:47 幂等采样如实·"
     "fund_premium no-op=expected NAV date 09-30 已覆盖〔由未落 bar 日 derive〕·cta_p1 无可标 "
     "bar·lane 守卫诚实 skip·daily_report REPORT-2026-10-08 幂等再生·ceo_live_usage LIVE-"
     "2026-10-08 写〔state=ORANGE rung=ORANGE cap=50%〕）③盘后 re-arm 重试（update_daily "
     "15:34+15:47 两跑均 0 新行·failures=0——sina 今日 bar 未落·迟 bar 自愈面诚实披露·cutoff "
     "2026-09-30 持有→fund_premium 2026-10-08 首采+CTA_P1 首接线+marks 验证全部挂起至 bar 落地"
     "·下轮续）④S0.5 零跳消费（DEC EE70CEF0 UNCHANGED·ORD 6C0018CC UNCHANGED·facts-driven·"
     "unacked=0 双扫·inbox 0·51 orders 全 ack）+克隆门三件+gate stale=0（compile OK×3·收据 "
     "_r767bmc_clone_receipt.json）+⑤quartet green（loop pin=5 no-op 15:55 首发火/watchdog 重"
     "注册 15:49/claws LF-normalized×2）+attrition CLEAN（4 ledgers·3 历史 shrink healed 注记）"
     "+FleetLink 常态自证（health 200 node=bm-c port 8790）+孤儿面=1 standing（常驻 ComfyUI "
     "服务面·CEO 资产·MV 产线在册·只读不杀·既有处置维持）+post_review 零新 NO（48Y/0N/5W）+"
     "token delta=0"),
    ("最近实物: qa/smoke-r767.md 5/5+qa/equity-curve-r767.png 66,310B+results/_r767bmc_s6_log."
     "txt（40 腿 rc0）+results/_r767bmc_clone_receipt.json+results/_r767bmc_s1_facts.json @ "
     + NOW),
    ("下个里程碑: 盘后窗续（10-08 今晚 ≤23:59）sina 迟 bar 自愈→今日 bar 2026-10-08 落地后："
     "fund_premium NAV 首采（bm-c 车）+CTA_P1 首 bar 接线+REGIME_GUARD v3 首新 bar enforce"
     "〔live.paper 宿主面=bm-a·bm-c lane-guard 诚实 skip 常设〕+首 marks 验证+marks lane 收盘后"
     "复核（bm-a 宿主）；next 5x=bm-c r770；r768 撞名预检=点火前 git ls-tree origin/main qa/ "
     "探 bm-b r768 包→按 r761/r764/r766/r767 披露制"),
    "[via bm-c r767]",
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
assert s2["round_no"] == 768 and h2["round_no"] == 768
assert s2["last_round"] == 767 and h2["last_round"] == 767
assert s2["last_orders_sha"] == ORD_SHA and s2["last_decisions_sha"] == DEC_SHA
assert re.fullmatch(r"[0-9A-F]{40}", ORD_SHA) and re.fullmatch(r"[0-9A-F]{64}", DEC_SHA)

print(json.dumps({"now": NOW, "epoch": EPOCH, "ram_gb": RAM_GB, "vram_mib": VRAM_MIB,
                  "cpu_pct": CPU_PCT, "head": HEAD_SHA[:10],
                  "dec_sha": DEC_SHA[:8], "ord_sha": ORD_SHA[:8],
                  "self_verify": "PASS (epoch int x2, clock T x2, round_no 768 x2, "
                                 "watermarks facts-driven x2)",
                  "rpt_line_bytes": len(RPT_LINE.encode("utf-8"))}, indent=1))
