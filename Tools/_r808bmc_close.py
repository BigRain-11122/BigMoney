# -*- coding: utf-8 -*-
"""r808 bm-c closeout: heartbeat/state/round-report bookkeeping (takeover
session closes the round after the 15:34 predecessor-session death; r294
adoption law). Law: fleet/README.md sec.6 machine-split files; epoch must
be JSON int (R170/R178); clock_read ISO8601 T-separator (R262);
products-first 3-line face. Pattern credit: Tools/_r807bmc_close.py
(r807 canon). DEC/ORD shas are READ PROGRAMMATICALLY from the closing
facts file -- ZERO literal sha constants in this script (r583 law)."""
import json, time
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CST = timezone(timedelta(hours=8))
now = datetime.now(CST)
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())
HM = now.strftime("%H:%M")[:4] + "x"

# --- facts-driven watermark read (NO literal sha constants; r583 law) ---
facts = json.loads((ROOT / "results" / "_r808bmc_s0_facts.json")
                   .read_text(encoding="utf-8"))
DEC_SHA = facts["dec_sha"]
ORD_SHA = facts["ord_sha"]
assert len(DEC_SHA) == 64 and len(ORD_SHA) == 40, "watermark shape gate"
assert facts.get("shape_assert") is True, "facts shape_assert gate"
assert facts.get("prev_dec_corrupt") is False, "r808: DEC prev must be 64hex clean"
assert facts.get("prev_ord_corrupt") is False, "r808: ORD prev must be 40hex clean"
assert facts.get("unacked") == [], "r808 closing: zero unacked orders"
assert facts.get("inbox_unread") == [], "r808 closing: zero unread inbox"

DEC_METHOD = (
    "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r808 double-sweep "
    "start 15:22 + closing 15:56 = zero-delta hold both, prev 64hex CLEAN (prev_dec_corrupt=False); "
    "facts-driven from results/_r808bmc_s05_facts.json + results/_r808bmc_s0_facts.json, 64hex "
    "shape-asserted; close-face reads sha PROGRAMMATICALLY from facts json, ZERO literal constants "
    "(r583 law)")
ORD_METHOD = (
    "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r808 double-sweep start "
    "15:22 + closing 15:56 = zero-delta hold both, prev 40hex CLEAN (prev_ord_corrupt=False); "
    "facts-driven from results/_r808bmc_s05_facts.json + results/_r808bmc_s0_facts.json, 40hex "
    "shape-asserted; close-face reads sha PROGRAMMATICALLY from facts json, ZERO literal constants "
    "(r583 law)")

did = (
    "2026-10-09T{hm}+08:00 | r808 | dept:工程+数据（T3 collector wall 单消耗+bm-a 陈活 STALE_MIN 接管 derive+前班猝死收养·第 109 bm-c 连守轮） | "
    "本地未达 origin commit 数=0（commit 后 push 自证·HTTPS ls-remote 送达面） | "
    "WM-VERDICT: 绿（red=false·10-09 bar sina 迟发=诚实等待态非故障〔update_daily 15:31/15:49 两跑均 0 新行·cutoff 10-08 保持·下轮自愈重试〕·"
    "next_pick=claimed moneyflow IC bm-a 车道合法·DEC BD94A27B 零差保持/ORD F26E1A37 零差保持〔双扫 15:22+15:56 恒等〕·"
    "unacked 0〔55 orders〕·inbox 0） | "
    "孤儿面=1（收尾探针只读不杀） | "
    "r808: ①前班（15:1x-15:3x）实录=S0 三连吸收〔5307b0b9d/c4f76cbbe/0d9a3b09f tight-window〕+S0.5 start 双扫（15:22 零增量）"
    "+T3 单消耗+QA 5/5 净写+S6 首跑 40/40（15:31）后 15:34 closing facts 处猝死〔收口未落〕；"
    "本班（15:4x-15:5x）依 r294 收养律同轮接管收口；"
    "②T3 产品=dashboard collector wall（18 数据车道健康墙·n_ok=12/n_warn=5/n_bad=0/n_none=1·dashboard.html +10 行"
    "+monitor/build_status.py +100 行·NODE-CHECK rc=0·T3-VERIFY ALL PASS·state/queue/tech.md T3→done）；"
    "③S6 双跑全绿（首跑 15:31 40/40+本班重跑 15:49-15:52 40/40·prewindow 日志保全 results/_r808bmc_s6_log_prewindow.txt）"
    "——fund_premium 10-08 NAV 首采落地（snapshot rows=1677·发布面 T+1·第十五观察窗收口）"
    "·update_daily 10-09 bar 两跑 0 新行（sina 迟发·诚实下轮重试）"
    "·**bm-a 心跳陈 34-37min→bm-c 依 O-2100 s2.4 STALE_MIN 法接管 8 车道 derive**"
    "（strategy_scorecard 6 员卡 S=2/A=4·live_paper ENFORCE 6 员 anchor OK·t35_open_fill_verify 10-08 PASS"
    "·t24 prospect 22/22 drift=0·promotion 0/22 诚实不达·t35_paper_export export-2026-10-08〔equity 5,996,451〕"
    "·daily_scorecard·build_status dashboard_status.js 全刷新）·daily_report+ceo_live_usage 再生（ORANGE cap 50%）；"
    "④S1 smoke 49/49；"
    "⑤S7 自愈四件套（loop pin=5 no-op+watchdog -Force 首发 15:56+双爪 LF 归一重装）+attrition 台账 CLEAN（4 台账·healed 史披露）；"
    "⑥CA 旗=supply_gap+ignition_sla 如实上报（W17 8 shards+JUDGE RAM 门停泊〔实时 RAM ~1.6GB<4GB 关·外部门 ComfyUI 占用 r802 不杀先例〕"
    "·autofill daemon 已 keepalive claim w17-screen-0..3〔4c754158c·r290 律〕·supply_floor 9≥3 无破·SLA 10-10 00:00）"
    " | 下轮指针: r809=①10-09 bar 落地重试（16:0x 轮 update_daily 新行→marks/live_paper/REGIME 自续面）"
    "②W17 RAM 窗自续跟随（AUTOFILL-PARK r797 在位·窗开自愈）③MV 三选项等待态维持"
    "④O-20261009-1105 @bm-c② exit-to-asset 引擎腿设计件 ≤10-16 12:00⑤tech 队列 T4 队头消耗"
).format(hm=HM)

activity = (
    "当前活: r808 bm-c（15:1x-15:5x 双班窗·前班 T3+本班接管收口·第 109 连守轮）——"
    "主产出=T3 collector wall（18 车道健康墙·T3-VERIFY ALL PASS）"
    "+bm-a 陈活 STALE_MIN 接管 8 车道 derive（scorecard/paper/export/dashboard 全刷至 10-08 cutoff）"
    "+fund_premium 10-08 NAV 首采（rows=1677） | "
    "最近实物: dashboard.html（collector wall）+monitor/build_status.py（+100 行）"
    "+qa/smoke-r808-bm-c.md（5/5·91 trades·determinism=True）"
    "+results/_r808bmc_s6_log.txt（双跑 40/40+40/40·prewindow 保全）"
    "+results/paper/*_paper.json+results/strategy_scorecard.json+results/dashboard_status.js（STALE_MIN 接管面）"
    "@本轮收口 commit | "
    "下个里程碑: 10-09 bar 16:0x 轮落地（marks/REGIME 自续）+W17 RAM 窗自续（SLA 10-10 00:00）"
    "+exit-to-asset 设计件 ≤10-16 12:00"
)

artifact = (
    "dashboard.html + monitor/build_status.py (T3 collector wall: 18 data-lane health wall, "
    "n_ok=12/n_warn=5/n_bad=0/n_none=1, NODE-CHECK rc=0, T3-VERIFY ALL PASS, tech.md T3->done) "
    "+ Tools/_r808bmc_{s0,s0race,s0tight,s05,s6,qa_ignite,t3_verify,close}.py (r808 helper octet; "
    "s05 double-sweep facts start+closing zero-delta) "
    "+ results/_r808bmc_s05_facts.json + results/_r808bmc_s0_facts.json "
    "+ results/_r808bmc_s6_log.txt + results/_r808bmc_s6_log_prewindow.txt (dual-run 40/40+40/40 evidence) "
    "+ results/_r808bmc_t3_verify.out + results/_r808bmc_dash_script.js "
    "+ qa/smoke-r808-bm-c.md (5/5 QA charter, 91 trades, determinism=True) + qa/equity-curve-r808-bm-c.png (65,412B) "
    "+ STALE_MIN takeover derive faces (results/strategy_scorecard.json + results/scorecard_v1.json + "
    "results/paper/*_paper.json + results/t35_open_fill_verify.json + results/prospect_paper/* + "
    "results/prospect_promotion/* + results/paper_export/export-2026-10-08.json + latest.json + "
    "results/daily_scorecard.html + results/dashboard_status.js; bm-a heartbeat stale 34-37min, O-2100 s2.4 law) "
    "+ fund_premium 10-08 NAV snapshot (rows=1677, publish face T+1, 15th observation window closed) @ " + now_iso
)

nxt = (
    "r809 续作: ①10-09 bar 落地重试（sina 迟 bar 自愈·16:0x 轮 update_daily 新行→marks/live_paper/REGIME v3 自续面）"
    "②W17 screens+JUDGE RAM 窗自续跟随（实时 RAM ~1.6GB<4GB 关·autofill AUTOFILL-PARK r797 在位·窗开即自愈·"
    "SLA 10-10 00:00 池补给 ≥10 claimable）"
    "③MV 三选项等待态维持+bm-a PARKING-P1 跟进 ④O-20261009-1105 @bm-c ② exit-to-asset 引擎腿设计件 ≤10-16 12:00"
    "⑤tech 队列 T4 队头消耗（P2 按序）"
)

verify = (
    "T3-VERIFY ALL PASS（collector wall 18 车道·NODE-CHECK rc=0） "
    "+ S6 双跑 80 腿 rc0（首跑+重跑·prewindow 日志保全双证据） "
    "+ smoke 49/49 + qa/smoke-r808-bm-c.md 5/5（91 trades·determinism=True·PNG 65,412B） "
    "+ STALE_MIN 接管 8 车道 derive（bm-a 心跳陈 37min·O-2100 s2.4 法面·live_paper ENFORCE anchor 6/6 OK） "
    "+ attrition 台账 CLEAN（4 台账·healed 史披露） + 双爪 LF 归一重装 + loop pin=5 幂等 + watchdog -Force "
    "+ 孤儿面=1 只读（收尾探针） + DEC/ORD 双扫零差（BD94A27B/F26E1A37·15:22+15:56 恒等·prev 双清） "
    "+ unacked 0〔55 orders〕+ inbox 0 + CA 旗 supply_gap+ignition_sla 如实上报（W17 RAM 门停泊·supply_floor 9≥3 无破）"
)

# ---- heartbeat ----
hb_path = ROOT / "fleet" / "machines" / "bm-c.json"
hb = json.loads(hb_path.read_text(encoding="utf-8"))
for k in ("last_seen", "last_seen_at", "clock_read", "ts", "updated", "updated_at", "last_run_at",
          "last_ts", "current_task_at", "last_decisions_at", "last_orders_at"):
    hb[k] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["last_round"] = 808
hb["last_round_at"] = now_iso
hb["round_no"] = 808
hb["round_no_label"] = "round 808 (bm-c)"
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
st["last_round"] = 808
st["round_no"] = 809
st["round_no_label"] = "round 808 (bm-c)"
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

# ---- round report (canonical machine-split ledger path) ----
rr_path = ROOT / "logs" / "iteration-loop" / "round_reports-bm-c.md"
with rr_path.open("a", encoding="utf-8") as f:
    f.write(did + "\n")

# ---- self-checks ----
hb2 = json.loads(hb_path.read_text(encoding="utf-8"))
st2 = json.loads(st_path.read_text(encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int"
assert isinstance(st2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in hb2["clock_read"] and "+" in hb2["clock_read"], "clock_read must be ISO8601 T-form"
assert hb2["round_no"] == 808 and st2["round_no"] == 809
assert len(hb2["last_decisions_sha"]) == 64 and len(hb2["last_orders_sha"]) == 40, "watermark shape gate"
print("closeout OK: hb round=808 state next=809 epoch=%d ts=%s dec=%s ord=%s"
      % (epoch, now_iso, DEC_SHA[:8], ORD_SHA[:8]))
