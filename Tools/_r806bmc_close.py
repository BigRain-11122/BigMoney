# -*- coding: utf-8 -*-
"""r806 bm-c closeout: heartbeat/state/round-report bookkeeping.
Law: fleet/README.md sec.6 machine-split files; epoch must be JSON int
(R170/R178); clock_read ISO8601 T-separator (R262); products-first 3-line
face. Pattern credit: Tools/_r805bmc_close.py (canon).
r806 law fix (r805 hand-typed-sha watermark corruption, false dec_delta
at round-start): DEC/ORD shas are READ PROGRAMMATICALLY from the closing
facts file -- ZERO literal sha constants in this script (r583
never-hand-typed law, close-face enforcement)."""
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
facts = json.loads((ROOT / "results" / "_r806bmc_s0_facts.json")
                   .read_text(encoding="utf-8"))
DEC_SHA = facts["dec_sha"]
ORD_SHA = facts["ord_sha"]
assert len(DEC_SHA) == 64 and len(ORD_SHA) == 40, "watermark shape gate"
assert facts.get("shape_assert") is True, "facts shape_assert gate"
assert facts.get("prev_dec_corrupt") is True, "r806: expect corrupt prev (heal face)"

DEC_METHOD = (
    "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r806 sweeps = TRUE zero-delta "
    "BD94A27B hold -- r805 close hand-typed a 65-hex literal watermark -> false dec_delta at r806 round-start; "
    "healed by 3-point verdict (r805 s0 facts dec_bytes 202452B identical + group HTTPS ls-remote tip==local "
    "origin/main ref fd6cb1b0 + fresh 64-hex equals r804 watermark); facts-driven from "
    "results/_r806bmc_s05_facts.json + results/_r806bmc_s0_facts.json (prev_dec_corrupt face), 64hex "
    "shape-asserted; close-face reads sha PROGRAMMATICALLY from facts json, ZERO literal constants (r583 law)")
ORD_METHOD = (
    "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r806 sweeps = ZERO-DELTA hold "
    "31542B89->31542B89 (group tree no new orders rows this round window); facts-driven from "
    "results/_r806bmc_s05_facts.json + results/_r806bmc_s0_facts.json, 40hex shape-asserted; close-face "
    "reads sha PROGRAMMATICALLY from facts json, ZERO literal constants (r583 law)")

did = (
    "2026-10-09T{hm}+08:00 | r806 | dept:研究/工程（P2 队头 T11-EXT 单消耗+r805 水位污染治愈+常设链全绿·第 107 bm-c 连守轮） | "
    "本地未达 origin commit 数=0（commit 后 push 自证·SSH 断窗备胎=daemon HTTPS keepalive 代投+HTTPS ls-remote 双源核〔r805 netpath 配方〕） | "
    "WM-VERDICT: 绿（red=false·lane=healthy·next_pick=claimed moneyflow IC bm-a 车道合法·"
    "DEC BD94A27B 真零差保持〔r805 close 手抄 65 位水位污染→假 dec_delta·三定点谳真零差+本轮 close 面改 facts 程序化读取治愈〕/"
    "ORD 31542B89 零差保持〔轮首+收尾双扫双零差〕·unacked 0〔55 orders〕·inbox 0） | "
    "孤儿面=1（收尾探针只读不杀） | "
    "r806: ①S0 daemon live-face 吸收 9 件 stage-1（commit 3a333fb6d·pull 撞活 daemon 窗=behind 0 集成需求零·SSH 断窗 fetch rc128 实录"
    "·HTTPS ls-remote tip=97186ef04 双源对账·daemon keepalive 通道在役）；"
    "②S0.5 轮首+收尾双扫（DEC 假差揭发=prev 65 位污染〔SHA-256 恒 64hex·肉眼同串不可辨〕·真零差三定点谳=r805 s0 facts bytes 202452B 恒等"
    "+集团 HTTPS tip==本地 ref fd6cb1b0+fresh 64 位==r804 水位·s05 探针加 prev_dec/ord_corrupt 检出位·水位治愈=close 零 sha 字面量·"
    "unacked 0〔55〕·inbox 0）；"
    "③S1 smoke 49/49；"
    "④P2 单消耗=**T11-EXT REPO 脉冲全 11 员期限梯扩展**（scripts/repo_pulse_probe.py 全 11 员+梯内联动+跨期限传导+月末/季度窗全梯对比+"
    "selftest PASS〔ladder join 腿新增〕+results/repo_pulse_probe.json·纯测量零回测·"
    "真发现=月末脉冲率随期限单调衰减〔GC001 17.6%/lift 5.4x→GC003 13.2%→GC004 11.1%→GC007 8.2%→GC014 2.6%/GC028 0.8% 两员反转低于非月末〕"
    "+深市 R-001 lift 4.7x+传导衰减〔GC001 脉冲日 GC003 mean z 5.73→GC014 2.67→GC028 1.19·R-001 7.14 最强〕"
    "+GC091/182 非有限 z〔平基线 MAD=0→±∞ 毒均值〕剔除+计数披露+严格 JSON）；"
    "⑤队列手术 tech 11→10（T11-EXT 出列·零补入·prereg 面按 T-67 §2 冻结律+P1 署名门不自动开·纯测量纪律维持）；"
    "⑥S6 40/40 rc0（dualrun ZERO-DRIFT streak 1 新起·compute_audit supply_gap+ignition_sla 旗维持"
    "〔W17 RAM 门 1.6GB<4GB 仍关·外部门根因 ComfyUI 生产只读不杀 r802 先例·supply_family_streak 978min·SLA 10-10 00:00〕·"
    "py_watermark=py_low_board_clear 板清合法 idle·fund_premium 第十七窗 pre-15:30 诚实 no-op〔15:30+ 轮首采〕·"
    "update_options RETIRED no-op〔O-20261009-1105〕·R31 他机车道 no-op 族照录）；"
    "⑦QA 包 5/5（qa/smoke-r806-bm-c.md·91 trades·determinism=True·equity PNG 65,399B·--round 806 显式标签）"
    "+S7 自愈批全绿（attrition 台账 CLEAN·loop pin=5 no-op·watchdog -Force 重注册·双爪 LF 归一重装·idle --worked 清零·孤儿只读）"
    " | 下轮指针: r807=①fund_premium 15:30+ 10-08 NAV 首采（15:30+ 轮落地）②W17 RAM 窗自续跟随（SLA 10-10 00:00）"
    "③MV 三选项等待态+bm-a PARKING-P1 跟进④1246 判据回访窗 10-16 跟随⑤T-178 池烧完成前不关票⑥tech 队列 T2-T10/T12 供源"
).format(hm=HM)

activity = (
    "当前活: r806 bm-c（14:05-14:3x 窗·P2 队头 T11-EXT 单消耗+r805 水位污染治愈·常设链全绿·第 107 连守轮）——"
    "主产出=REPO 脉冲全 11 员期限梯扩展（月末脉冲率随期限单调衰减 GC001 17.6%→GC028 0.8%·GC014/028 两员反转·"
    "传导衰减 GC003 z 5.73→GC028 1.19·纯测量零回测） | "
    "最近实物: scripts/repo_pulse_probe.py（11 员梯扩展+selftest PASS）+results/repo_pulse_probe.json+"
    "qa/smoke-r806-bm-c.md（5/5·91 trades·determinism=True）+results/_r806bmc_s6_log.txt（40/40）+"
    "Tools/_r806bmc_{{s05,s6,qa_ignite,close}}.py@本轮收口 commit | "
    "下个里程碑: fund_premium 15:30+ NAV 首采（15:30+ 轮）+RAM 窗开→W17+JUDGE autofill 自续烧（SLA 10-10 00:00）+"
    "T-178 judge verdict→48h CEO 呈报链"
)

artifact = (
    "scripts/repo_pulse_probe.py (T11-EXT: 11-member term-ladder extension + co-pulse linkage + cross-tenor "
    "z transmission + month-end/quarter-end ladder tables + non-finite-z exclusion with drop counts; selftest "
    "PASS incl. new ladder-join leg) "
    "+ results/repo_pulse_probe.json (11 members: GC001 17.6% month-end vs 3.2% non; decay GC007 8.2% -> GC014 "
    "2.6% -> GC028 0.8% inverted; R-001 lift 4.7x; transmission GC003 z_on 5.73 -> GC028 1.19) "
    "+ state/queue/tech.md (queue surgery 11->10, T11-EXT out, prereg gated per T-67 sec.2 + P1 signature) "
    "+ qa/smoke-r806-bm-c.md (5/5 QA charter pack) + qa/equity-curve-r806-bm-c.png (65,399B) "
    "+ results/_r806bmc_s6_log.txt (40/40 rc0) "
    "+ results/_r806bmc_s05_facts.json + results/_r806bmc_s0_facts.json (DEC false-delta unmasked as 65-hex "
    "prev corruption, TRUE zero-delta 3-point verdict, prev_corrupt detector faces; HTTPS delivery face) "
    "+ results/_r806bmc_dec_log.txt + results/_r806bmc_dec_blob.md (delta-window evidence) "
    "+ research/pit-lineage-receipt.md (direct-write pit r806: hand-typed sha watermark corruption, r666 "
    "precedent) "
    "+ Tools/_r806bmc_{{s05,s6,qa_ignite,close}}.py @ " + now_iso
)

nxt = (
    "r807 续作: ①fund_premium 15:30+ 10-08 NAV 首采（发布面 T+1·第十七观测窗收口·15:30+ 轮落地）"
    "②W17 screens+JUDGE RAM 窗自续跟随（1.6GB<4GB 仍关·autofill AUTOFILL-PARK r797 在位·窗开即自愈·SLA 10-10 00:00）"
    "③MV 三选项等待态维持+bm-a PARKING-P1 跟进 ④O-20261009-1246 判据回访窗 10-16 跟随（队列面合规+空转声明轮数→0）"
    "⑤T-2026-10-09-178-P1 池烧完成前不关票 ⑥tech 队列 T2-T10/T12 供源（下一 P2 队头按序消耗）"
)

verify = (
    "smoke 49/49 + QA smoke-r806-bm-c.md 5/5（91 trades·determinism=True·equity PNG 65,399B） "
    "+ S6 40/40 rc0（results/_r806bmc_s6_log.txt·dualrun ZERO-DRIFT streak 1 新起） "
    "+ attrition 台账 CLEAN + 双爪 LF 归一重装 + loop pin=5 no-op + watchdog -Force + "
    "idle --worked 清零（idle_rounds=0） + 孤儿面=1 只读 + "
    "repo_pulse_probe selftest PASS（pulse tiers+calendar faces+flat-reject+ladder join 四腿） "
    "+ DEC 真零差三定点谳（r805 s0 facts 202452B 恒等+集团 HTTPS tip==本地 fd6cb1b0+fresh 64hex==r804 水位） "
    "+ 水位治愈（65 位污染→close facts 程序化回写+s05 prev_corrupt 检出位） "
    "+ compute_audit supply_gap+ignition_sla 旗如实上报（RAM 外部门根因披露·W17 持平模式）"
)

# ---- heartbeat ----
hb_path = ROOT / "fleet" / "machines" / "bm-c.json"
hb = json.loads(hb_path.read_text(encoding="utf-8"))
for k in ("last_seen", "last_seen_at", "clock_read", "ts", "updated", "updated_at", "last_run_at",
          "last_ts", "current_task_at", "last_decisions_at", "last_orders_at"):
    hb[k] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["last_round"] = 806
hb["last_round_at"] = now_iso
hb["round_no"] = 806
hb["round_no_label"] = "round 806 (bm-c)"
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
st["last_round"] = 806
st["round_no"] = 807
st["round_no_label"] = "round 806 (bm-c)"
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
assert hb2["round_no"] == 806 and st2["round_no"] == 807
assert len(hb2["last_decisions_sha"]) == 64 and len(hb2["last_orders_sha"]) == 40, "watermark heal gate"
print("closeout OK: hb round=806 state next=807 epoch=%d ts=%s dec=%s ord=%s"
      % (epoch, now_iso, DEC_SHA[:8], ORD_SHA[:8]))
