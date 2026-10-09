# -*- coding: utf-8 -*-
"""r804 bm-c closeout: heartbeat/state/round-report bookkeeping.
Law: fleet/README.md sec.6 machine-split files; epoch must be JSON int
(R170/R178); clock_read ISO8601 T-separator (R262); products-first 3-line
face. Pattern credit: Tools/_r803bmc_close.py (canon)."""
import json, time, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CST = timezone(timedelta(hours=8))
now = datetime.now(CST)
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())
HM = now.strftime("%H:%M")[:4] + "x"

DEC_SHA = "BD94A27BA4AC39BC9A05037DDCFAF693CD78126AA6189711E8F7F1848A8AC522"
ORD_SHA = "31542B89C3C70E714071D256F0952E1C2204A12D"
DEC_METHOD = (
    "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r804 closing sweep = "
    "ZERO-DELTA hold BD94A27B->BD94A27B (group tree no new decisions rows this round window); "
    "facts-driven from results/_r804bmc_s0_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law)")
ORD_METHOD = (
    "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r804 round-start + closing sweeps = "
    "CONSUMED delta 4AA1A8F6->31542B89 (two added rows = O-20261009-1246 self-drive enforcement order + "
    "O-20261009-1257 council load-monitor order, both quant-relevant: BigMoney named in the no-queue "
    "violation list -> fix mandate (a) state/queue three-file build executed SAME ROUND with "
    "auditor-mirror verify GREEN (results/_r804bmc_ceo1246_verify.json); watermark key advanced same round); "
    "facts-driven from results/_r804bmc_s05_facts.json + results/_r804bmc_s0_facts.json + "
    "results/_r804bmc_ord_delta.txt, 40hex shape-asserted, never hand-typed (r583 S4 law)")

did = (
    "2026-10-09T{hm}+08:00 | r804 | dept:工程/舰队治理（O-20261009-1246/1257 队列违例修复派单 a 当轮执行+常设链全绿+收尾双扫消费·第 105 bm-c 连守轮） | "
    "本地未达 origin commit 数=0（commit 后 push+fetch 自证） | "
    "WM-VERDICT: 绿（red=false·lane=healthy·next_pick=claimed moneyflow IC bm-a 车道合法·"
    "DEC BD94A27B 零差保持/ORD 4AA1A8F6→31542B89 消费〔+2 行=1246 自驱强化令+1257 委员会监控令·两令涉本司="
    "首读板 BigMoney AMBER〔0.6h·无队列〕违例→修复派单 a 当轮执行：state/queue 三文件建面+判读器同构自验 GREEN〕·"
    "unacked 0〔55 orders〕·inbox 0） | "
    "孤儿面=2（探针只读不杀〔r802 判例维持·13:5x 探针 r340 三面判别〕） | "
    "r804: ①S0 定向吸收+rebase 绿（7 件 daemon live-face→吸收 commit de9f36cff·pull --rebase up-to-date 零 UU·"
    "轮中 autofill 自投两 keepalive commit 1c219fbd5/b25450cf1 照录零重叠）；"
    "②S0.5 双扫消费（ORD +2 行涉本司·DEC 零差·closing sweep 重试 30s 过〔首跑撞瞬态超时被取消·零锁零残留〕·"
    "facts=_r804bmc_s05_facts+_r804bmc_s0_facts shape-asserted）；"
    "③S1 smoke 49/49+QA r804 证据包 5/5（smoke-r804-bm-c.md·91 trades·sharpe 0.1994·determinism=True·"
    "equity PNG 65,336B·per-machine 后缀律）；"
    "④1246 修复派单 a 执行=state/queue/{{main,tech,explore}}.md 三面建面（main 6+tech 12+explore 12 条真实种子"
    "〔本轮在飞活+PLAN§7 工具面+数据面先例〕·BigCompute GREEN 样板格式镜像·禁等CEO/他司条目律·"
    "口径=docs/self-drive.md §1+Tools/subsidiary-load-audit.ps1 双读定形）+判读器同构自验 **GREEN**"
    "（Tools/_r804bmc_ceo1246.py verify·m11/t16/e16/OK·prodAge 0.0h·idleDecl 11/30）→"
    "1257 BigMoney AMBER 修复回执并入 1246 窗=委员会下一班判读器直读翻绿；"
    "⑤S6 40/40 rc0 第 25 连绿（dualrun ZERO-DRIFT streak 51 维持·fund_premium 第十六观测窗 pre-15:30 诚实 no-op"
    "〔15:30+ 轮首采收口〕·update_daily 10-08 截止零新行·R31 他机车道 no-op 族+update_options RETIRED 照录）；"
    "⑥compute_audit 诚实旗=supply_gap+ignition_sla（W17 screens 4-7+JUDGE 五件点火 SLA 破窗·"
    "根因=RAM 外部门 1.6-1.8GB<4GB〔ComfyUI 产线+22 GPU compute apps 占用·CEO 前台优先律〕·"
    "autofill AUTOFILL-PARK r797 机制在位·RAM 窗开即自续·SLA 10-10 00:00）+py_watermark=py_low_board_clear"
    "（板清合法 idle）+W17 screen 分片在途 1 片照录（trial_labor_w17.py screen 1 8·13:08 起火）；"
    "⑦S7 自愈批全绿（attrition 4 台账 CLEAN〔3 healed 注记照录〕·loop pin=5 no-op·watchdog -Force 重注册·"
    "双爪 LF 归一重装·SAT 引擎活 rc0·idle 非绿档 RAM 7.1%<40% 无领单义务·idle_rounds=0 维持）"
    " | 下轮指针: r805=①state/queue 消耗律起算（self-drive §1：P1 队头→P2→P3·轮尾补 ≥1 条·剩余较轮首净减）"
    "②fund_premium 15:30+ NAV 首采③W17 RAM 窗自续跟随+screen 在途分片跟随④W18/MV/PARKING-P1 等待态维持"
    "⑤1246 判据回访窗 10-16 跟随⑥T-178 池烧完成前不关票"
).format(hm=HM)

activity = (
    "当前活: r804 bm-c（13:2x-13:5x 窗·CEO 令 1246/1257 队列违例修复=当轮主产出+常设链全绿·第 105 连守轮）——"
    "主产出=state/queue 三面建面+判读器同构自验 GREEN（BigMoney AMBER→GREEN 修复回执并入 1246 窗） | "
    "最近实物: state/queue/{{main,tech,explore}}.md（m11/t16/e16/OK·6/12/12 条真实种子）+"
    "results/_r804bmc_ceo1246_verify.json（GREEN）+qa/smoke-r804-bm-c.md（5/5·91 trades·determinism=True）+"
    "results/_r804bmc_s6_log.txt（40/40 第 25 连绿）@ 本轮收口 commit | "
    "下个里程碑: 委员会值守班 15:07 判读器直读=BigMoney AMBER→GREEN+fund_premium 15:30+ NAV 首采+"
    "RAM 窗开→W17+JUDGE autofill 自续烧（SLA 10-10 00:00）+T-178 judge verdict→48h CEO 呈报链"
)

artifact = (
    "state/queue/main.md + state/queue/tech.md + state/queue/explore.md "
    "(O-20261009-1246 fix mandate (a): m11/t16/e16 rows OK) "
    "+ results/_r804bmc_ceo1246_verify.json (auditor-mirror verdict GREEN) "
    "+ results/_r804bmc_ceo1246_probe.json + results/_r804bmc_selfdrive.md "
    "+ results/_r804bmc_loadaudit_tool.txt "
    "+ qa/smoke-r804-bm-c.md (5/5 QA charter pack) + qa/equity-curve-r804-bm-c.png (65,336B) "
    "+ results/_r804bmc_s6_log.txt (40/40 rc0 25th green) "
    "+ results/_r804bmc_s05_facts.json + results/_r804bmc_s0_facts.json + results/_r804bmc_ord_delta.txt "
    "+ docs/daily_report/REPORT-2026-10-09.md + docs/live_usage/LIVE-2026-10-09.md "
    "+ Tools/_r804bmc_{{s05,s6,qa_ignite,ceo1246,close}}.py @ " + now_iso
)

nxt = (
    "r805 续作: ①state/queue 消耗律起算（self-drive §1 轮次启动规则：P1 队头有活就干→P2→P3·"
    "轮尾补 ≥1 条新待办·三队列剩余较轮首净减）②fund_premium 15:30+ 10-08 NAV 首采（发布面 T+1·第十六观测窗收口）"
    "③W17 screens+JUDGE 池烧 RAM 窗自续跟随+screen 在途分片跟随（SLA 10-10 00:00）"
    "④W18 链依赖 W17-JUDGE 排水维持（禁假填充）⑤MV 三选项等待态维持+bm-a PARKING-P1 跟进 "
    "⑥O-20261009-1246 判据回访窗 10-16 跟随（队列面合规 8/8+空转声明轮数→0）"
    "⑦T-2026-10-09-178-P1 池烧完成前不关票"
)

verify = (
    "smoke 49/49 + QA smoke-r804-bm-c.md 5/5（91 trades·sharpe 0.1994·determinism=True·equity PNG 65,336B） "
    "+ S6 40/40 rc0 第 25 连绿（results/_r804bmc_s6_log.txt） + dualrun ZERO-DRIFT streak 51 + "
    "attrition 4 台账 CLEAN（3 healed 注记） + 双爪 LF 归一重装 + loop pin=5 no-op + watchdog -Force + "
    "SAT 引擎活 rc0 + DEC BD94A27B 零差/ORD 31542B89 消费（_r804bmc_s05_facts + _r804bmc_s0_facts + "
    "_r804bmc_ord_delta.txt shape-asserted） + 孤儿面=2 只读 + 1246 修复自验 GREEN"
    "（_r804bmc_ceo1246_verify.json·m11/t16/e16/OK·prodAge 0.0h） + "
    "compute_audit supply_gap/ignition_sla 旗如实上报（RAM 外部门根因披露·K:\Fluxgroup 事实面）"
)

# ---- heartbeat ----
hb_path = ROOT / "fleet" / "machines" / "bm-c.json"
hb = json.loads(hb_path.read_text(encoding="utf-8"))
for k in ("last_seen", "last_seen_at", "clock_read", "ts", "updated", "updated_at", "last_run_at",
          "last_ts", "current_task_at", "last_decisions_at", "last_orders_at"):
    hb[k] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["last_round"] = 804
hb["last_round_at"] = now_iso
hb["round_no"] = 804
hb["round_no_label"] = "round 804 (bm-c)"
hb["current_task"] = activity
hb["activity_now"] = activity
hb["did"] = did
hb["note"] = did
hb["verdict"] = did
hb["last_round_summary"] = did
hb["last_action"] = did
hb["latest_artifact"] = artifact
hb["next"] = nxt
hb["next_pointer"] = nxt
hb["next_milestone"] = nxt
hb["verify"] = verify
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["last_pulled_at"] = now_iso
hb["head_sha"] = "pending-this-round-commit"
hb["last_decisions_sha"] = DEC_SHA
hb["last_decisions_sha_method"] = DEC_METHOD
hb["dec_sha_method"] = DEC_METHOD
hb["last_orders_sha"] = ORD_SHA
hb["last_orders_sha_method"] = ORD_METHOD
hb["ord_sha_method"] = ORD_METHOD
hb_path.write_text(json.dumps(hb, ensure_ascii=False, indent=1), encoding="utf-8")

# ---- state ----
st_path = ROOT / "state-bm-c.json"
st = json.loads(st_path.read_text(encoding="utf-8"))
for k in ("clock_read", "current_task_at", "last_round_at", "last_round_ts", "last_seen",
          "last_seen_at", "last_run_at", "last_ts", "ts", "updated", "updated_at",
          "last_decisions_read_at", "last_decisions_at", "last_orders_at"):
    if k in st:
        st[k] = now_iso
for k in ("did", "note", "last_round_summary", "last_action", "verdict"):
    if k in st:
        st[k] = did
st["heartbeat_epoch_utc"] = epoch
st["last_round"] = 804
st["round_no"] = 805
st["round_no_label"] = "round 804 (bm-c)"
st["current_task"] = activity
st["activity_now"] = activity
st["latest_artifact"] = artifact
st["next"] = nxt
st["next_pointer"] = nxt
st["next_milestone"] = nxt
st["verify"] = verify
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["last_decisions_sha"] = DEC_SHA
st["last_decisions_sha_method"] = DEC_METHOD
st["dec_sha_method"] = DEC_METHOD
st["last_orders_sha"] = ORD_SHA
st["last_orders_sha_method"] = ORD_METHOD
st["ord_sha_method"] = ORD_METHOD
st_path.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")

# ---- round report ----
rr_path = ROOT / "logs" / "iteration-loop" / "round_reports-bm-c.md"
with rr_path.open("a", encoding="utf-8") as f:
    f.write(did + "\n")

# ---- self-checks ----
hb2 = json.loads(hb_path.read_text(encoding="utf-8"))
st2 = json.loads(st_path.read_text(encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int"
assert isinstance(st2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in hb2["clock_read"] and "+" in hb2["clock_read"], "clock_read must be ISO8601 T-form"
assert hb2["round_no"] == 804 and st2["round_no"] == 805
print("closeout OK: hb round=804 state next=805 epoch=%d ts=%s" % (epoch, now_iso))
