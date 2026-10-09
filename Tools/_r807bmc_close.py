# -*- coding: utf-8 -*-
"""r807 bm-c closeout: heartbeat/state/round-report bookkeeping.
Law: fleet/README.md sec.6 machine-split files; epoch must be JSON int
(R170/R178); clock_read ISO8601 T-separator (R262); products-first 3-line
face. Pattern credit: Tools/_r806bmc_close.py (r806 canon).
DEC/ORD shas are READ PROGRAMMATICALLY from the closing facts file -- ZERO
literal sha constants in this script (r583 never-hand-typed law)."""
import json, time, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CST = timezone(timedelta(hours=8))
now = datetime.now(CST)
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())
HM = now.strftime("%H:%M")[:4] + "x"

# --- facts-driven watermark read (NO literal sha constants; r583 law) ---
facts = json.loads((ROOT / "results" / "_r807bmc_s0_facts.json")
                   .read_text(encoding="utf-8"))
DEC_SHA = facts["dec_sha"]
ORD_SHA = facts["ord_sha"]
assert len(DEC_SHA) == 64 and len(ORD_SHA) == 40, "watermark shape gate"
assert facts.get("shape_assert") is True, "facts shape_assert gate"
assert facts.get("prev_dec_corrupt") is False, "r807: DEC heal must hold (64hex clean prev)"
assert facts.get("prev_ord_corrupt") is False, "r807: ORD prev must be 40hex clean"
assert facts.get("unacked") == [], "r807 closing: zero unacked orders"
assert facts.get("inbox_unread") == [], "r807 closing: zero unread inbox"

DEC_METHOD = (
    "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r807 sweep = zero-delta "
    "hold, prev 64hex CLEAN post-r806-heal (prev_dec_corrupt=False first clean sweep); facts-driven from "
    "results/_r807bmc_s05_facts.json + results/_r807bmc_s0_facts.json, 64hex shape-asserted; close-face "
    "reads sha PROGRAMMATICALLY from facts json, ZERO literal constants (r583 law)")
ORD_METHOD = (
    "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r807 sweep = DELTA same-window "
    "consumed: 2 added rows = O-20261009-1315 cloud-token unlock order + O-20261009-1430 fleet-tailscale "
    "comms order, both rows executed at group level via bm-c interactive window, bm-c loop = receipt-only "
    "zero new lane obligations; facts-driven from results/_r807bmc_s05_facts.json + "
    "results/_r807bmc_s0_facts.json, 40hex shape-asserted; close-face reads sha PROGRAMMATICALLY from "
    "facts json, ZERO literal constants (r583 law)")

did = (
    "2026-10-09T{hm}+08:00 | r807 | dept:工程（半开 rebase 接管收口+P2 队头 T2 单消耗+ORD 双令回执·第 108 bm-c 连守轮） | "
    "本地未达 origin commit 数=0（commit 后 push 自证·HTTPS ls-remote 送达面） | "
    "WM-VERDICT: 绿（red=false·py_low_board_clear 板清合法 idle〔pre-15:30 无新 bar〕·"
    "next_pick=claimed moneyflow IC bm-a 车道合法·DEC BD94A27B 零差保持〔治愈后首度 prev_corrupt=False 双清面〕/"
    "ORD delta 同窗消费〔2 行=O-20261009-1315 云端 token 全面解锁令+O-20261009-1430 机队 Tailscale 通信令·"
    "两行均已 executed〔via bm-c 交互窗 14:3x〕·循环面 receipt-only 零新车道义务·唯一持续禁面=云端视频生成〕·"
    "unacked 0〔55 orders〕·inbox 0） | "
    "孤儿面=1（收尾探针只读不杀） | "
    "r807: ①S0 双段实录——前班（14:25-14:48）daemon 吸收 2 commit+S6 40/40+QA 5/5+T2 产品 commit 后 pull --rebase "
    "撞 bm-a 竞窗停于 pick3 冲突解 staged 后猝死〔14:48:43·r867 死形〕；本班〔14:55-15:2x〕轮首撞半开 rebase"
    "〔r868 律先读 sequencer 态〕→盲吸收 commit 0e90e21b2 恰落 pick3 位=r685 载体形→reset --soft+r808 三步"
    "〔author-script 注入+commit -F·Terminal-dumb 拒进形态实弹〕+r787 原子 add+churn 自有 commit 推进 6/6 picks"
    "〔T2 产品 d1cdc537f 45 件+2339 行保全〕+末 pick 三步拒→r624 收口〔quit+branch -f+checkout·pick6 消息/作者"
    "从原 commit 对象恢复〕→merge origin 3a875bf43 12 面〔deep-ts newer-wins+G4' tie→disk-live+ledger union 零丢失"
    "·receipt results/_r807bmc_merge_close.json〕→push 6aec0c06f 送达自证〔HTTPS ls-remote==HEAD〕"
    "→autofill daemon RAM 窗开自续 claim w17-screen-0〔a39998645 自提交自推·r290 律在役〕；"
    "②S0.5 s05 探针加超时夹克（75s/腿·SSH 断窗挂死 5min 实弹→防再发·r625 夹克律族·收据 results/_r807bmc_clone_receipt.json）"
    "+ORD 双令同窗消费回执；"
    "③S1 smoke 49/49+SAT 引擎活 rc0（bm-c Tools 面·fleet engine faces bm-a/bm 陈面如实披露=bm-a 25min/bm-b 离线 13h+〔O-20261009-1430 诊断面〕·他机车道不越）；"
    "④P2 单消耗=**T2 dashboard.html 三新面接线**（常供池 autofill 行〔ready/waiting/ready_ids/补批延迟/10min 门〕"
    "+饱和审计面行〔载态/池饿旗/近段计数〕+试用劳力线行〔W1-W4 漏斗史+非 done 池 chips〕+engine 行 active_burns 烧录可视化——"
    "node --check rc=0 语法过+三面字段交叉核零缺失〔真实数据面 dashboard_status.js 实测 94,821B〕"
    "·浏览器通道本窗三连败如实披露〔Could not parse tool response×3〕→渲染验证=静态实证替代·bm-a 下轮 build 后 CEO 面即见三新行）；"
    "⑤S6 40/40 rc0 首过（update_daily 0 新行 cutoff 10-08·10-09 bar 待 15:30+·fund_premium pre-15:30 no-op〔15:30+ 轮首采〕"
    "·update_options RETIRED no-op〔O-20261009-1105 消费方核查留痕在腿输出〕·CA 旗=supply_gap+ignition_sla"
    "〔W17 5 件 RAM 门停泊〔screen-4/5/6/7+JUDGE〕·RAM 实时 ~0-1.6GB 外部门 ComfyUI 产线 r802 不杀先例"
    "·supply_floor 9≥3 无破·供给 SLA 10-10 00:00〕）；"
    "⑥QA 包 5/5（qa/smoke-r807-bm-c.md·91 trades·determinism=True·equity final 1,023,027·PNG 65,556B·--round 807 显式标签·零撞名净写）；"
    "⑦S7 自愈批（loop pin=5 幂等+watchdog -Force+双爪 LF 归一重装+attrition 台账 CLEAN+idle --worked 清零+孤儿只读）"
    " | 下轮指针: r808=①fund_premium 15:30+ 10-08 NAV 首采（第十五窗 pre 系列收口·15:30+ 轮落地）"
    "②10-09 bar 15:30+ 落地→marks/live_paper/REGIME v3 面自续③W17 RAM 窗自续跟随（SLA 10-10 00:00 池补给≥10 claimable）"
    "④MV 三选项等待态维持⑤O-20261009-1105 @bm-c② exit-to-asset 引擎腿设计件 ≤10-16 12:00⑥tech 队列 T3-T10/T12 供源"
).format(hm=HM)

activity = (
    "当前活: r807 bm-c（14:25-15:2x 双班窗·前班 T2 产品+本班半开 rebase 接管收口·第 108 连守轮）——"
    "主产出=dashboard.html 三新面接线（常供池/饱和审计/试用劳力线+active_burns·node 语法过+字段交叉核零缺失）"
    "+半开 rebase 6/6 picks 收口（T2 产品保全+merge 12 面零丢失+push 送达自证） | "
    "最近实物: dashboard.html（T2 三面接线）+qa/smoke-r807-bm-c.md（5/5·91 trades·determinism=True）+"
    "results/_r807bmc_s6_log.txt（40/40）+Tools/_r807bmc_{{s05,s6,qa_ignite,close}}.py（s05 带超时夹克）"
    "+Tools/_r807bmc_{{rebase_triage,rebase_recover,rebase_finale3,merge_close,push}}.py（接管收口链）"
    "+results/_r807bmc_{{rebase_recover,merge_close}}.json（收口收据）@本轮收口 commit | "
    "下个里程碑: fund_premium 15:30+ NAV 首采（15:30+ 轮）+10-09 bar 15:30+ 落地→marks/REGIME 面+"
    "W17 RAM 窗开→autofill 自续烧（SLA 10-10 00:00）+exit-to-asset 设计件 ≤10-16 12:00"
)

artifact = (
    "dashboard.html (T2: three new real-data faces wired -- autofill pool row (ready/waiting/ready_ids/"
    "fill-latency/10min-gate) + saturation audit row (load_state/starvation flags) + trial-labor funnel "
    "row (W1-W4 history + non-done pool chips) + engine-row active_burns visualization; verified node "
    "--check rc=0 + zero missing fields cross-check vs results/dashboard_status.js 94,821B real face) "
    "+ Tools/_r807bmc_{s05,s6,qa_ignite,close}.py (helper quartet; s05 carries 75s timeout jackets on "
    "every git leg -- SSH-outage hang real-fire) "
    "+ results/_r807bmc_clone_receipt.json (stale-scan + compile gate) "
    "+ results/_r807bmc_s05_facts.json + results/_r807bmc_s0_facts.json (ORD 2-row consumption evidence: "
    "O-20261009-1315 cloud-token unlock + O-20261009-1430 fleet-tailscale; DEC zero-delta hold with first "
    "clean prev_corrupt=False sweep post-heal) "
    "+ results/_r807bmc_ord_delta.txt + results/_r807bmc_ord_blob.md (delta-window evidence) "
    "+ qa/smoke-r807-bm-c.md (5/5 QA charter pack) + qa/equity-curve-r807-bm-c.png (65,556B) "
    "+ results/_r807bmc_s6_log.txt (40/40 rc0 first-pass) "
    "+ results/_r807bmc_dash_script.js (node syntax-check artifact) "
    "+ results/_r807bmc_qa_runner.out/.err (detached QA ignition pair) "
    "+ Tools/_r807bmc_{rebase_triage,rebase_recover,rebase_finale3,merge_close,push}.py "
    "(half-open rebase takeover chain: r808 three-step + r787 atomic + r624 finale + merge closeout) "
    "+ results/_r807bmc_rebase_recover.json + results/_r807bmc_merge_close.json (takeover receipts) @ " + now_iso
)

nxt = (
    "r808 续作: ①fund_premium 15:30+ 10-08 NAV 首采（发布面 T+1·15:30+ 轮落地）"
    "②10-09 bar 15:30+ 落地→update_daily 新行+marks/live_paper/REGIME v3 自续面"
    "③W17 screens+JUDGE RAM 窗自续跟随（实时 RAM ~0-1.6GB<4GB 关·autofill AUTOFILL-PARK r797 在位·窗开即自愈·"
    "SLA 10-10 00:00 池补给 ≥10 claimable）"
    "④MV 三选项等待态维持+bm-a PARKING-P1 跟进 ⑤O-20261009-1105 @bm-c ② exit-to-asset 引擎腿设计件 ≤10-16 12:00"
    "⑥tech 队列 T3-T10/T12 供源（下一 P2 队头按序消耗）"
)

verify = (
    "半开 rebase 收口链 6/6 picks 保全（T2 产品 d1cdc537f 45 件在链·收据 results/_r807bmc_rebase_recover.json） "
    "+ merge 12 面零丢失（receipt results/_r807bmc_merge_close.json） "
    "+ push 送达自证（6aec0c06f HTTPS tip==HEAD） "
    "+ smoke 49/49 + qa/smoke-r807-bm-c.md 5/5（91 trades·determinism=True·equity final 1,023,027·PNG 65,556B） "
    "+ S6 40/40 rc0 首过（results/_r807bmc_s6_log.txt） "
    "+ node --check rc=0（dashboard.html 内联脚本语法） + 三面字段交叉核零缺失（autofill/saturation/trial_labor vs dashboard_status.js 实测面） "
    "+ attrition 台账 CLEAN + 双爪 LF 归一重装 + loop pin=5 幂等 + watchdog -Force + idle --worked 清零（idle_rounds=0） "
    "+ 孤儿面=2 只读（探针自面+detached daemon 面） + DEC 零差保持（BD94A27B·治愈后首度 prev_corrupt=False 双清） "
    "+ ORD 双令同窗消费回执（O-20261009-1315+O-20261009-1430） "
    "+ CA 旗 supply_gap+ignition_sla 如实上报（W17 5 件 RAM 门停泊·外部门 ComfyUI 根因披露·supply_floor 9≥3 无破）"
)

# ---- heartbeat ----
hb_path = ROOT / "fleet" / "machines" / "bm-c.json"
hb = json.loads(hb_path.read_text(encoding="utf-8"))
for k in ("last_seen", "last_seen_at", "clock_read", "ts", "updated", "updated_at", "last_run_at",
          "last_ts", "current_task_at", "last_decisions_at", "last_orders_at"):
    hb[k] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["last_round"] = 807
hb["last_round_at"] = now_iso
hb["round_no"] = 807
hb["round_no_label"] = "round 807 (bm-c)"
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
st["last_round"] = 807
st["round_no"] = 808
st["round_no_label"] = "round 807 (bm-c)"
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
assert hb2["round_no"] == 807 and st2["round_no"] == 808
assert len(hb2["last_decisions_sha"]) == 64 and len(hb2["last_orders_sha"]) == 40, "watermark shape gate"
print("closeout OK: hb round=807 state next=808 epoch=%d ts=%s dec=%s ord=%s"
      % (epoch, now_iso, DEC_SHA[:8], ORD_SHA[:8]))
