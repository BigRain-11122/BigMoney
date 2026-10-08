# -*- coding: utf-8 -*-
"""r766 bm-c closeout driver: state-bm-c.json + fleet/machines/bm-c.json
heartbeat + canonical RPT line append. Facts-driven (r583 S4 law: hashes and
numbers never hand-typed; DEC/ORD watermarks loaded from
results/_r766bmc_s05_facts.json sweep-2; epoch must be JSON int per R170/R178
law; clock_read T-separated ISO per R262 law). Self-verify reload +
isinstance gate before exit. Pattern credit: Tools/_r765bmc_close.py
(canonical clone chain)."""
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

facts = json.load(open(os.path.join(ROOT, "results", "_r766bmc_s05_facts.json"),
                       encoding="utf-8"))
DEC_SHA = facts["dec_sha"]
ORD_SHA = facts["ord_sha"]

SUMMARY = ("r766: QA det-86th 5/5 (pid 7648, S6-first order, 93 trades, 1,017,839 frozen "
           "identity, determinism=True, png 66,154B, 86th consecutive; collision case#4 "
           "disclosed: bm-b 1f82049a6 first-registered same-path r766 pack, same frozen "
           "numbers zero scientific loss, bm-b version git-history preserved, F-20261008-03 "
           "standing namespace proposal) + ORD double-hop consumed 866AE477->8859B105->"
           "6C0018CC (sweep-1 MV orders 17/18 + 呈审纪律总令 + wave-6 homecoming; sweep-2 "
           "wave-4/wave-5 homecoming six-waves-complete; all MV/BigStream domain, zero "
           "BigMoney action; DEC EE70CEF0 UNCHANGED both passes) + S6 40/40 rc0 (dualrun "
           "streak 51; CA flags [pool_starvation,supply_floor] intraday known standing "
           "faces; fund_premium/cta_p1 pre-15:30 no-op -> tonight first snapshot/"
           "auto-wiring; daily_report REPORT-2026-10-08 regenerated) + clone gate "
           "stale765=0 + marks lane 10 rows (14:36 tail, bm-a host) + unacked=0; smoke "
           "49/49; attrition CLEAN; post_review zero new NO (45Y/0N/5W); quartet green; "
           "token delta=0.")

CURTASK = ("当前活: r766 bm-c（14:5x-15:1x 窗·复市 T-0 盘中值守第 86 连守轮·收盘过渡段〔15:00 收盘"
           "已过·15:30 数据门未开〕）——主产出=①QA det-86th 5/5（93 trades·1,017,839 冻结恒等·"
           "determinism=True·png 66,154B·86 连证·撞名族第 4 例披露〔bm-b 1f82049a6 先在册·"
           "同冻结数字零科学损失·git 史保全·F-20261008-03 常设呈报〕）②ORD 双跳全消费"
           "（866AE477→8859B105→6C0018CC——全 MV/BigStream 域研究波归位回执+呈审纪律总令·"
           "零本仓动作·facts-driven·unacked=0·inbox 0）③S6 40/40 rc0（dualrun streak 51）+"
           "克隆门 stale765=0+marks lane 10 行（14:36 尾写·bm-a 宿主车道健康·15:00 收盘 tick "
           "待落）+FleetLink 自证 health 200 node=bm-c port 8790| 最近实物: qa/smoke-r766.md "
           "5/5+qa/equity-curve-r766.png 66,154B+results/_r766bmc_s6_log.txt 40/40+results/"
           "_r766bmc_ord_diff.txt @ " + NOW + " | 下个里程碑: 今晚盘后（10-08 15:30+）数据链 "
           "re-arm+REGIME_GUARD v3 首新 bar enforce+fund_premium 15:30 首采（bm-c 车）+"
           "CTA_P1 首接线+首 marks 验证+marks lane 收盘后复核（≤10-08 23:59）；next 5x=bm-c r770")

ACTIVITY = ("r766 bm-c: reopen T-0 intraday watch round 86th consecutive (14:5x-15:1x "
            "window, close-transition round). (1) S0: round-start dirty 8 = own faces "
            "(orphan probe + autofill/dispatcher/idle_trigger x2/satengine x2 + heartbeat) "
            "absorb commit 562de0183 -> pull --rebase up-to-date zero replay. (2) S0.5 "
            "double sweep: DEC EE70CEF0 UNCHANGED both passes; ORD sweep-1 single-hop "
            "866AE477 -> 8859B105 (bm-a 5135d8a MV order-17 + f508a8f 呈审纪律总令 + "
            "19f23fe wave-6 homecoming; MV/BigStream domain, zero BigMoney action) + "
            "sweep-2 single-hop 8859B105 -> 6C0018CC (bm-a 9c5f021 wave-4 homecoming + "
            "ed40de5 wave-5 homecoming six-waves-complete; MV domain, zero BigMoney "
            "action); both hops consumed facts-driven, watermark updated both hops; "
            "fleet orders 51 disk unacked=0 both passes; inbox 0. (3) S1 smoke 49/49 + "
            "SAT rc0 alive + orphan probe py_faces=5 orphans=1 (resident ComfyUI service "
            "face, CEO asset -- standing MV production lane, read-only no-kill, "
            "standing disposition) + idle NOT-GREEN (RAM 6.9% resident ComfyUI) --worked "
            "(idle_rounds=0). (4) MAIN PRODUCTS: (a) lineage clone gate: s05/s6/"
            "qa_ignite + clone_gate cloned stale765=0, compile OK x3, receipt "
            "_r766bmc_clone_receipt.json. (b) S6 40/40 rc0 via canonical clone (dualrun "
            "ZERO-DRIFT streak 51 @408 entries cutoff 03:47 -- pool blob unchanged, "
            "idempotent sample honestly reported; compute_audit rc0 flags="
            "[pool_starvation,supply_floor] intraday board-clear known standing faces "
            "honestly disclosed; py_watermark py_low_board_clear legal intraday idle; "
            "lane guards honest skips: bm-a/bm-b owned lanes stdout-only no-op; "
            "fund_premium pre-15:30 no-op -> tonight 15:30 bm-c-lane first snapshot; "
            "cta_p1_paper no markable bar -> tonight first-bar auto-wiring; daily_report "
            "REPORT-2026-10-08.md/.json regenerated idempotent). (c) QA det-86th per "
            "ignition order law (r749 pit): S6 full-chain rc0 collected FIRST -> "
            "qa_ignite detached pid 7648 -> poll terminal (.err 0B): 93 trades, equity "
            "1,017,839 frozen identity, determinism=True, png 66,154B, 86th consecutive; "
            "COLLISION CASE #4 disclosed (bm-b 1f82049a6 r766 pack first-registered "
            "golden-week; same-path overwrite; both packs same frozen numbers 93 trades/"
            "determinism=True, md one-line phrasing diff S6 38-leg vs current canon text, "
            "png binary render diff; zero scientific evidence loss; bm-b version "
            "git-history preserved verifiable via git show 1f82049a6:qa/smoke-r766.md; "
            "F-20261008-03 namespace-fix standing proposal, family per r761/r764 "
            "precedent). (d) marks lane watch: 10 rows, tail write 14:36 (bm-a host lane "
            "healthy, 15:00 close tick pending -- post-close rounds re-verify per "
            "next_pointer). (e) FleetLink standing self-cert: health 200 node=bm-c port "
            "8790. (5) closeout: quartet green (loop pin=5 no-op first-fire 15:15 / "
            "watchdog re-registered 15:07 / pre-commit+pre-push claws LF-normalized x2) "
            "+ attrition CLEAN (4 ledgers) + idle --worked + post_review zero new NO "
            "(45Y/0N/5W) + state/heartbeat/RPT close.")

VERIFY = ("smoke 49/49 + qa/smoke-r766.md 5/5 (93 trades equity 1,017,839 frozen identity "
          "determinism=True .err 0B png 66,154B; collision case#4 disclosed, bm-b "
          "1f82049a6 version git-preserved) + results/_r766bmc_s6_log.txt 40/40 rc0 "
          "(dualrun ZERO-DRIFT streak 51) + results/_r766bmc_s05_facts.json double sweep "
          "(DEC EE70CEF0 UNCHANGED both / ORD two hops consumed to 6C0018CC / unacked=0 / "
          "inbox 0 / shape-asserted) + results/_r766bmc_ord_diff.txt (both-hop rows "
          "extracted, all MV domain) + results/_r766bmc_clone_receipt.json (stale765=0, "
          "compile OK x3) + attrition CLEAN (4 ledgers) + post_review zero new NO "
          "(45Y/0N/5W) + quartet green (pin=5 no-op / watchdog re-registered / claws "
          "installed LF-normalized x2) + orphan face=1 standing disposition (py_faces=5) "
          "+ SAT alive rc0 + idle_trigger --worked (idle_rounds=0) + FleetLink health 200 "
          "node=bm-c port 8790 + marks lane 10 rows (14:36 tail) + token_meter delta=0 "
          "(zero LLM calls this round)")

NEXT_PTR = ("r767: (a) tonight post-close face (>=15:30 rounds, <=10-08 23:59): data-chain "
            "full re-arm + REGIME_GUARD v3 first-new-bar enforce (set "
            "BIGMONEY_REGIME_GUARD=enforce before live.paper) + fund_premium 15:30 first "
            "snapshot (bm-c lane) + CTA_P1 first-bar auto-wiring + first-marks "
            "verification (marks row + state trial-live + compounding identity) + marks "
            "lane post-close re-verify (bm-a host lane, 15:00 close tick landing); (b) "
            "QA ignition order law standing (S6 rc0 -> qa_ignite -> qa_poll terminal -> "
            "close); QA pack pre-ignite collision check: r767 paths ALREADY TAKEN by "
            "bm-b golden-week r767 pack (commit 15f33d1d8) -- collision case#5 expected, "
            "follow r761/r764/r766 disclosure canon (same frozen numbers assert + "
            "bm-b version git-preserved note + F-20261008-03 standing proposal); (c) "
            "close scripts: RPT path = canonical logs/iteration-loop/round_reports-bm-c.md "
            "(r750 pit; NEVER clone a ROOT template); (d) FleetLink standing self-cert "
            "line per round (listener health); (e) D-20261008-06 suffix-naming law "
            "(_r767bmc_* prefix pattern) + command-dedup law enforcement face; (f) "
            "month-boundary first exam 10-31; next 5x = bm-c r770. [via bm-c r766]")

ARTIFACT = ("qa/smoke-r766.md 5/5 + qa/equity-curve-r766.png 66,154B + results/"
            "_r766bmc_s6_log.txt (40 legs rc0) + results/_r766bmc_clone_receipt.json "
            "(stale765=0) + results/_r766bmc_ord_diff.txt @ " + NOW)

MILESTONE = ("tonight post-close (10-08 15:30+): data-chain re-arm + REGIME_GUARD v3 "
             "first-new-bar enforce + fund_premium 15:30 first snapshot (bm-c lane) + "
             "CTA_P1 first-bar auto-wiring + first-marks verify + marks lane re-verify "
             "(<= 10-08 23:59); next 5x = bm-c r770")

DEC_METHOD = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; "
              "r766 double sweeps = UNCHANGED EE70CEF0 both passes (zero action, "
              "watermark held); facts-driven from results/_r766bmc_s05_facts.json, 64hex "
              "shape-asserted, never hand-typed (r583 S4 law)")

ORD_METHOD = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r766 "
              "double sweep: sweep-1 single-hop 866AE477 -> 8859B105 (bm-a MV order-17 + "
              "呈审纪律总令 + wave-6 homecoming, MV/BigStream domain, zero BigMoney "
              "action) + sweep-2 single-hop 8859B105 -> 6C0018CC (bm-a wave-4 + wave-5 "
              "homecoming six-waves-complete, MV domain, zero BigMoney action); "
              "watermark updated both hops facts-driven, 40hex shape-asserted, hex-case "
              "normalized per r711 pit law (r583 S4 law)")

TS_KEYS = ["clock_read", "last_seen", "last_seen_at", "updated", "updated_at", "ts",
           "last_round_at", "last_round_ts", "last_run_at", "last_ts", "current_task_at",
           "last_decisions_read_at", "last_orders_at"]

GPU_KEYS = ["gpu_free_vram_mib", "gpu_free_vram_mb", "gpu_idle_vram_mb", "gpu_idle_vram_mib",
            "gpu_vram_free_mb", "gpu_free_mb", "gpu_idle_mb", "gpu_free_mib", "gpu_idle_mib"]
RAM_KEYS = ["free_ram_gb", "idle_ram_gb", "ram_free_gb"]

# --- state-bm-c.json ---
sp = os.path.join(ROOT, "state-bm-c.json")
state = json.load(open(sp, encoding="utf-8"))
state["round_no"] = 767
state["round_no_label"] = "round 766 (bm-c)"
state["last_round"] = 766
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
hb["round_no"] = 767
hb["round_no_label"] = "round 766 (bm-c)"
hb["last_round"] = 766
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
    "r766",
    "dept:工程+交易（复市 T-0 盘中值守轮·第 86 bm-c 连守轮·收盘过渡段〔15:00 收盘已过·15:30 数据门未开〕）",
    "本地未达 origin commit 数=0（commit 后 push+fetch 自证）",
    ("WM-VERDICT: 绿（red=false·lane=healthy·py_low_board_clear 盘中板清合法 idle〔orders 51 "
     "disk unacked=0 双扫·inbox 0 双扫〕·compute_audit rc0 flags=[pool_starvation,"
     "supply_floor] 盘中席位间隙已知常在面如实披露〔pool ready 0<floor 3〕·idle NOT-GREEN "
     "--worked〔RAM 6.9%<40% 常驻 ComfyUI·idle_rounds=0 已清〕）"),
    ("当前活: r766 bm-c（14:5x-15:1x 窗·复市 T-0 盘中值守第 86 连守轮）——S0 轮首脏 8=自有面"
     "（orphan probe+autofill/dispatcher/idle_trigger×2/satengine×2+心跳）absorb 562de0183→"
     "pull --rebase up-to-date 零重放→克隆门三件+gate（s05/s6/qa_ignite stale765=0·compile "
     "OK×3·收据 _r766bmc_clone_receipt.json）——主产出=①QA det-86th 5/5（律序 S6 40 腿 rc0 "
     "收齐→点火 pid 7648→终态 .err 0B——93 trades·equity 1,017,839 冻结恒等〔r751-766 锚链"
     "续持〕·determinism=True·png 66,154B·86 连证）〔撞名披露：qa/smoke-r766.md+equity-"
     "curve-r766.png 跨机轮号撞名族第 4 例——bm-b 1f82049a6（golden-week·bm-b 自计 r766·QA "
     "pack 5/5）先在册·本机今日包覆写活树件；两包同冻结数字（93 trades/determinism=True）"
     "零科学证据损失·md 唯一行差=S6 38-leg 旧文案 vs 现行文案·png 二进制渲染差·bm-b 版 git "
     "史保全（git show 1f82049a6:qa/smoke-r766.md 可验）·HQ-FEEDBACK F-20261008-03 命名空间"
     "修法常设呈报（r761/r764 先例族）〕②ORD 双跳全消费（sweep-1 866AE477→8859B105〔bm-a "
     "5135d8a MV 令十七+f508a8f 呈审纪律总令+19f23fe 第六波归位回执·MV/BigStream 域·零本仓"
     "动作〕+sweep-2 8859B105→6C0018CC〔bm-a 9c5f021 第四波归位+ed40de5 第五波归位·六波齐·"
     "MV 域·零本仓动作〕·DEC EE70CEF0 双扫 UNCHANGED·facts-driven·unacked=0·inbox 0·证据件 "
     "_r766bmc_ord_diff.txt）③S6 40/40 rc0（dualrun ZERO-DRIFT streak 51 @408 条·cutoff "
     "03:47〔池面未变幂等采样如实〕·py_watermark py_low_board_clear 合法盘中 idle·lane 守卫"
     "诚实 skip 面·fund_premium pre-15:30 no-op→今晚 15:30 bm-c 车道首采·cta_p1 无可标 "
     "bar→今晚首 bar 自动接线·daily_report REPORT-2026-10-08 幂等再生）+④marks lane 盘中"
     "值守复核（10 行·14:36 尾写·bm-a 宿主车道健康·15:00 收盘 tick 待落〔下轮起复核〕·观察"
     "项零干预）+⑤FleetLink 常态自证（health 200 node=bm-c port 8790）+孤儿面=1 standing"
     "（常驻 ComfyUI 服务面·CEO 资产·MV 产线在册·只读不杀·既有处置维持）+idle NOT-GREEN "
     "--worked（RAM 低位常驻 ComfyUI）"),
    ("最近实物: qa/smoke-r766.md 5/5+qa/equity-curve-r766.png 66,154B+results/_r766bmc_"
     "s6_log.txt（40 腿 rc0）+results/_r766bmc_clone_receipt.json+results/_r766bmc_ord_"
     "diff.txt @ " + NOW),
    ("下个里程碑: 今晚盘后（10-08 15:30+）数据链 re-arm+REGIME_GUARD v3 首新 bar enforce+"
     "fund_premium 15:30 首采（bm-c 车）+CTA_P1 首接线+首 marks 验证+marks lane 收盘后复核"
     "（≤10-08 23:59）；next 5x=bm-c r770；r767 撞名预检=路径已被 bm-b golden-week r767 包"
     "（15f33d1d8）占用→第 5 例预期·按 r761/r764/r766 披露制"),
    "[via bm-c r766]",
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
assert s2["round_no"] == 767 and h2["round_no"] == 767
assert s2["last_round"] == 766 and h2["last_round"] == 766
assert s2["last_orders_sha"] == ORD_SHA and s2["last_decisions_sha"] == DEC_SHA
assert re.fullmatch(r"[0-9A-F]{40}", ORD_SHA) and re.fullmatch(r"[0-9A-F]{64}", DEC_SHA)

print(json.dumps({"now": NOW, "epoch": EPOCH, "ram_gb": RAM_GB, "vram_mib": VRAM_MIB,
                  "cpu_pct": CPU_PCT, "head": HEAD_SHA[:10],
                  "dec_sha": DEC_SHA[:8], "ord_sha": ORD_SHA[:8],
                  "self_verify": "PASS (epoch int x2, clock T x2, round_no 767 x2, "
                                 "watermarks facts-driven x2)",
                  "rpt_line_bytes": len(RPT_LINE.encode("utf-8"))}, indent=1))
