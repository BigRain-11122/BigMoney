# -*- coding: utf-8 -*-
"""r803 bm-c closeout: heartbeat/state/round-report bookkeeping.
Law: fleet/README.md sec.6 machine-split files; epoch must be JSON int
(R170/R178); clock_read ISO8601 T-separator (R262); products-first 3-line
face. Pattern credit: Tools/_r802bmc_close.py (canon)."""
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
ORD_SHA = "4AA1A8F61C37ECB400BECB07F8B7E039211F2625"
DEC_METHOD = (
    "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r803 closing sweep = "
    "ZERO-DELTA hold BD94A27B->BD94A27B (group tree no new decisions rows this round window; "
    "r802 consumed the C-20261009-02 batch already); facts-driven from results/_r803bmc_s0_facts.json, "
    "64hex shape-asserted, never hand-typed (r583 S4 law)")
ORD_METHOD = (
    "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r803 closing sweep = CONSUMED "
    "delta 2D9DF88A->4AA1A8F6 (single added row = 10-09 12:2x MiniGame U360-L4B full-screen walk-through "
    "receipt = non-quant row, science-judgment gate verdict = zero-action for BigMoney per routing law, "
    "watermark key advanced same round); facts-driven from results/_r803bmc_s0_facts.json + "
    "results/_r803bmc_ord_delta.txt, 40hex shape-asserted, never hand-typed (r583 S4 law)")

did = (
    "2026-10-09T{hm}+08:00 | r803 | dept:工程/研究（W17 池烧 RAM 门等窗跟随+常设链全绿+收尾双扫消费·第 104 bm-c 连守轮·"
    "holding-pattern 等开闸豁免面=一行声明不重扫） | "
    "本地未达 origin commit 数=0（commit 后 push+fetch 自证） | "
    "WM-VERDICT: 绿（red=false·lane=healthy·next_pick=claimed moneyflow IC bm-a 车道合法·"
    "DEC BD94A27B 零差保持/ORD 2D9DF88A→4AA1A8F6 消费〔唯一新增行=MiniGame U360-L4B 走查回执=非本司例科学闸零动作〕·"
    "unacked 0〔55 orders〕·inbox 0） | "
    "孤儿面=1（ComfyUI 产线资产只读不杀〔r802 判例维持·13:0x 探针 r340 三面判别〕） | "
    "r803: ①S0 定向吸收+rebase 绿（7 件 daemon live-face→吸收 commit c88ba9d1e·pull --rebase 干净零 UU·"
    "轮中 autofill 自投两 commit 8976e856b/b63f59ad0 keepalive+claim 照录零重叠）；"
    "②S0.5 双扫消费（ORD 单行差=MiniGame 非本司零动作·DEC 零差·facts=_r803bmc_s05_facts+_r803bmc_s0_facts shape-asserted）；"
    "③S1 smoke 49/49+QA r803 证据包 5/5（smoke-r803-bm-c.md·91 trades·sharpe 0.1994·determinism=True·"
    "equity PNG 65,631B·per-machine 后缀律）；"
    "④S6 40/40 rc0 第 24 连绿（dualrun ZERO-DRIFT streak 51 维持·fund_premium 第十六观测窗 pre-15:30 诚实 no-op"
    "〔15:30+ 轮首采收口〕·update_daily 10-08 截止零新行·update_options RETIRED no-op·R31 他机车道 no-op 族照录）；"
    "⑤compute_audit 诚实旗上报=supply_gap+ignition_sla（W17 screens 4-7+JUDGE 五件点火 SLA 破窗·"
    "根因=RAM 外部门 1.7-1.8GB<4GB〔ComfyUI 产线+22 GPU compute apps 占用·CEO 前台优先律〕·"
    "autofill AUTOFILL-PARK r797 机制在位·RAM 窗开即自续·SLA 10-10 00:00 池补给窗与 RAM 窗联动风险如实披露）；"
    "⑥等待态一行声明（W18 链依赖 W17-JUDGE 排水禁假填充·MV 三选项等待态维持·fund_premium 首采待 15:30+ 轮）；"
    "⑦S7 自愈批全绿（attrition 4 台账 CLEAN〔3 healed 注记照录〕·loop pin=5 no-op·watchdog -Force 重注册·"
    "双爪 LF 归一重装·SAT 引擎活 rc0·idle 非绿档 RAM 7%<40% 无领单义务·idle_rounds=0 维持）"
    " | 下轮指针: r804=①W17 池烧 RAM 窗自续跟随②fund_premium 15:30+ NAV 首采③W18 链依赖维持"
    "④MV 等待态维持⑤bm-a PARKING-P1 跟进⑥T-178 池烧完成前不关票"
).format(hm=HM)

activity = (
    "当前活: r803 bm-c（13:0x-13:2x 窗·W17 池烧 RAM 门等窗+常设链全绿+双扫消费·第 104 连守轮）——"
    "主产出=QA r803 证据包 5/5+面板四件续鲜+supply_gap/ignition_sla 诚实旗上报（RAM 外部门根因披露） | "
    "最近实物: qa/smoke-r803-bm-c.md（5/5·91 trades·determinism=True）+qa/equity-curve-r803-bm-c.png+"
    "docs/daily_report/REPORT-2026-10-09.md+docs/live_usage/LIVE-2026-10-09.md+"
    "results/_r803bmc_s6_log.txt（40/40 第 24 连绿）@ 本轮收口 commit | "
    "下个里程碑: RAM 窗开→W17 screens 0-7+JUDGE autofill 自续烧（SLA 10-10 00:00）+"
    "fund_premium 15:30+ NAV 首采+T-178 judge verdict→48h CEO 呈报链"
)

artifact = (
    "qa/smoke-r803-bm-c.md (5/5 QA charter pack) + qa/equity-curve-r803-bm-c.png (65,631B) "
    "+ results/_r803bmc_s6_log.txt (40/40 rc0 24th green) + results/_r803bmc_s05_facts.json "
    "+ results/_r803bmc_s0_facts.json + results/_r803bmc_ord_delta.txt "
    "+ docs/daily_report/REPORT-2026-10-09.md + docs/live_usage/LIVE-2026-10-09.md "
    "+ results/daily_scorecard.json + results/dashboard_status.json (S6 panel refreshes) "
    "+ Tools/_r803bmc_{s05,s6,qa_ignite,close}.py @ " + now_iso
)

nxt = (
    "r804 续作: ①W17 screens+JUDGE 池烧 RAM 窗自续跟随（autofill 常轨·AUTOFILL-PARK r797 在位·"
    "ignition_sla 五件旗随 RAM 窗开自愈·SLA 10-10 00:00）②fund_premium 15:30+ 10-08 NAV 首采"
    "（发布面 T+1·第十六观测窗收口）③W18 链依赖 W17-JUDGE 排水维持（禁假填充）④MV 三选项等待态维持 "
    "⑤bm-a PARKING-P1 判决跑窗跟进（<3min 单核·过门→停泊袖接线 v1.0）⑥T-2026-10-09-178-P1 池烧完成前不关票"
)

verify = (
    "smoke 49/49 + QA smoke-r803-bm-c.md 5/5（91 trades·sharpe 0.1994·determinism=True·equity PNG 65,631B） "
    "+ S6 40/40 rc0 第 24 连绿（results/_r803bmc_s6_log.txt） + dualrun ZERO-DRIFT streak 51 + "
    "attrition 4 台账 CLEAN（3 healed 注记） + 双爪 LF 归一重装 + loop pin=5 no-op + watchdog -Force + "
    "SAT 引擎活 rc0 + DEC BD94A27B 零差/ORD 4AA1A8F6 消费（_r803bmc_s05_facts + _r803bmc_s0_facts + "
    "_r803bmc_ord_delta.txt shape-asserted） + 孤儿面=1 只读（ComfyUI 产线） + "
    "compute_audit supply_gap/ignition_sla 旗如实上报（RAM 外部门根因披露·K:\Fluxgroup 事实面）"
)

# ---- heartbeat ----
hb_path = ROOT / "fleet" / "machines" / "bm-c.json"
hb = json.loads(hb_path.read_text(encoding="utf-8"))
for k in ("last_seen", "last_seen_at", "clock_read", "ts", "updated", "updated_at", "last_run_at",
          "last_ts", "current_task_at", "last_decisions_at", "last_orders_at"):
    hb[k] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["last_round"] = 803
hb["last_round_at"] = now_iso
hb["round_no"] = 803
hb["round_no_label"] = "round 803 (bm-c)"
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
st["last_round"] = 803
st["round_no"] = 804
st["round_no_label"] = "round 803 (bm-c)"
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
assert hb2["round_no"] == 803 and st2["round_no"] == 804
print("closeout OK: hb round=803 state next=804 epoch=%d ts=%s" % (epoch, now_iso))
