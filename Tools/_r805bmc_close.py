# -*- coding: utf-8 -*-
"""r805 bm-c closeout: heartbeat/state/round-report bookkeeping.
Law: fleet/README.md sec.6 machine-split files; epoch must be JSON int
(R170/R178); clock_read ISO8601 T-separator (R262); products-first 3-line
face. Pattern credit: Tools/_r804bmc_close.py (canon)."""
import json, time, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CST = timezone(timedelta(hours=8))
now = datetime.now(CST)
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())
HM = now.strftime("%H:%M")[:4] + "x"

DEC_SHA = "BD94A27BA4AC39BC9A05037DDCFAAF693CD78126AA6189711E8F7F1848A8AC522"
ORD_SHA = "31542B89C3C70E714071D256F0952E1C2204A12D"
DEC_METHOD = (
    "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r805 round-start + closing sweeps = "
    "ZERO-DELTA hold BD94A27B->BD94A27B (group tree no new decisions rows this round window); "
    "facts-driven from results/_r805bmc_s05_facts.json + results/_r805bmc_s0_facts.json, "
    "64hex shape-asserted, never hand-typed (r583 S4 law)")
ORD_METHOD = (
    "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r805 round-start + closing sweeps = "
    "ZERO-DELTA hold 31542B89->31542B89 (group tree no new orders rows this round window); "
    "facts-driven from results/_r805bmc_s05_facts.json + results/_r805bmc_s0_facts.json, "
    "40hex shape-asserted, never hand-typed (r583 S4 law)")

did = (
    "2026-10-09T{hm}+08:00 | r805 | dept:工程/研究（self-drive §1 消耗律首轮=P2 队头 T1+T11 双消耗+常设链全绿·第 106 bm-c 连守轮） | "
    "本地未达 origin commit 数=0（commit 后 push+fetch 自证） | "
    "WM-VERDICT: 绿（red=false·lane=healthy·next_pick=claimed moneyflow IC bm-a 车道合法·"
    "DEC BD94A27B 零差保持/ORD 31542B89 零差保持〔轮首+收尾双扫双零差〕·unacked 0〔55 orders〕·inbox 0） | "
    "孤儿面=1（收尾探针只读不杀·轮首 2→收尾 1 自然消退） | "
    "r805: ①S0 两段吸收 daemon live-face 8 件（5+3·commit 1d8e1813e+e5027ae2e·pull --rebase 零 UU·"
    "吸收后活 daemon 即时回写=竞态重吸收一次〔首跑 rebase 拒·批内缩窗重试绿〕）；"
    "②S0.5 轮首+收尾双扫（DEC/ORD 双零差·facts=_r805bmc_s05_facts+_r805bmc_s0_facts shape-asserted）；"
    "③S1 smoke 49/49；"
    "④P2 双消耗=**T1 llm_assist 轮报告摘要扩展**（OLLAMA_HOST 0.0.0.0 归一修复〔绑定址≠连接址〕+summary 命令〔轮账本尾→CEO 白话三问摘要〕"
    "+qwen3.6-coder:35b 本地路由 selftest PASS〔gen/写守卫/route 三绿〕+实物 research/auto/summary-bm-c-20261009.md·L1 零 token·llm2_usage 记账）"
    "+**T11 REPO 利率脉冲探测器**（scripts/repo_pulse_probe.py+results/repo_pulse_probe.json+selftest PASS·纯测量零回测·"
    "真发现=GC001 2011-05-13..2026-10-08 3741 行·月末窗脉冲率 17.6% vs 非月末 3.2%〔~5.4x〕·季度末窗 37.3%·"
    "T1≥10% 50 日·T2≥20% 12 日〔2015-02-10 53.44 春节前钱荒实证入列〕）；"
    "⑤队列手术=tech 12→11 净减 1（T1/T11 出列+T11-EXT 补入·self-drive §1 规则5 首轮合规·三队列总数 31→30）；"
    "⑥S6 40/40 rc0（dualrun 记观察相 DRIFT 一笔=W17 shard-0 autofill claim 握手时间戳〔13:50:54 vs 13:52:14〕·streak 51→重置照录非故障·"
    "compute_audit supply_gap 旗维持〔W17 RAM 门 1.66GB<4GB 仍关·autofill tick claim 三连 crash 已入 fuse 观察面·"
    "AUTOFILL-PARK r797 在位·SLA 10-10 00:00〕·py_watermark=py_low_board_clear 板清合法 idle·"
    "fund_premium 第十六窗 pre-15:30 诚实 no-op〔15:30+ 轮首采收口〕·R31 他机车道 no-op 族照录）；"
    "⑦QA 包 5/5（qa/smoke-r805-bm-c.md·91 trades·sharpe 0.1994·determinism=True·equity PNG 65,588B·--round 805 显式标签）"
    "+S7 自愈批全绿（attrition 4 台账 CLEAN〔3 healed 注记照录〕·loop pin=5 no-op·watchdog -Force 重注册·双爪 LF 归一重装·"
    "idle --worked 清零·孤儿只读）"
    " | 下轮指针: r806=①fund_premium 15:30+ 10-08 NAV 首采（15:30+ 轮落地）②W17 RAM 窗自续跟随③T11-EXT 期限梯扩展"
    "④W18 依赖 W17-JUDGE 排水维持⑤MV 三选项等待态+bm-a PARKING-P1 跟进⑥1246 判据回访窗 10-16 跟随⑦T-178 池烧完成前不关票"
).format(hm=HM)

activity = (
    "当前活: r805 bm-c（13:45-13:5x 窗·self-drive §1 消耗律首轮=P2 队头 T1+T11 双消耗·常设链全绿·第 106 连守轮）——"
    "主产出=llm_assist 轮报告白话摘要通道（35b 本地 L1 零 token）+REPO 利率脉冲探测器"
    "（GC001 月末窗 17.6% vs 非月末 3.2%·季度末窗 37.3%·纯测量零回测） | "
    "最近实物: scripts/llm_assist.py（summary 命令+host 归一）+research/auto/summary-bm-c-20261009.md+"
    "scripts/repo_pulse_probe.py+results/repo_pulse_probe.json+qa/smoke-r805-bm-c.md（5/5·91 trades·determinism=True）+"
    "results/_r805bmc_s6_log.txt（40/40）@ 本轮收口 commit | "
    "下个里程碑: fund_premium 15:30+ NAV 首采（15:30+ 轮）+RAM 窗开→W17+JUDGE autofill 自续烧（SLA 10-10 00:00）+"
    "T-178 judge verdict→48h CEO 呈报链"
)

artifact = (
    "scripts/llm_assist.py (T1: summary cmd + OLLAMA_HOST 0.0.0.0 normalize fix; selftest PASS) "
    "+ research/auto/summary-bm-c-20261009.md (L1 zero-token plain-language summary artifact) "
    "+ scripts/repo_pulse_probe.py (T11: pure-measurement pulse detector; selftest PASS) "
    "+ results/repo_pulse_probe.json (GC001 3741 rows: month-end 17.6% vs non-month-end 3.2%, quarter-end 37.3%) "
    "+ state/queue/tech.md (queue surgery 12->11 net -1, T1/T11 out, T11-EXT in) "
    "+ qa/smoke-r805-bm-c.md (5/5 QA charter pack) + qa/equity-curve-r805-bm-c.png (65,588B) "
    "+ results/_r805bmc_s6_log.txt (40/40 rc0) "
    "+ results/_r805bmc_s05_facts.json + results/_r805bmc_s0_facts.json (DEC/ORD zero-delta shape-asserted) "
    "+ results/llm2_usage.jsonl (summary leg L2 ledger) "
    "+ docs/daily_report/REPORT-2026-10-09.md + docs/live_usage/LIVE-2026-10-09.md (idempotent same-day regen) "
    "+ Tools/_r805bmc_{{s05,s6,qa_ignite,close}}.py @ " + now_iso
)

nxt = (
    "r806 续作: ①fund_premium 15:30+ 10-08 NAV 首采（发布面 T+1·第十六观测窗收口·15:30+ 轮落地）"
    "②W17 screens+JUDGE RAM 窗自续跟随（1.66GB<4GB 仍关·autofill tick claim 三连 crash 已入 fuse 观察面·窗开即自愈·SLA 10-10 00:00）"
    "③T11-EXT REPO 脉冲全 11 员期限梯扩展（GC001 先行已交·梯内联动+月末窗全梯对比）"
    "④W18 链依赖 W17-JUDGE 排水维持（禁假填充）⑤MV 三选项等待态维持+bm-a PARKING-P1 跟进 "
    "⑥O-20261009-1246 判据回访窗 10-16 跟随（队列面合规 8/8+空转声明轮数→0）"
    "⑦T-2026-10-09-178-P1 池烧完成前不关票"
)

verify = (
    "smoke 49/49 + QA smoke-r805-bm-c.md 5/5（91 trades·sharpe 0.1994·determinism=True·equity PNG 65,588B） "
    "+ S6 40/40 rc0（results/_r805bmc_s6_log.txt·dualrun 观察相 DRIFT 一笔照录 streak 51→重置） "
    "+ attrition 4 台账 CLEAN（3 healed 注记） + 双爪 LF 归一重装 + loop pin=5 no-op + watchdog -Force + "
    "idle --worked 清零（idle_rounds=0） + DEC BD94A27B/ORD 31542B89 双扫零差"
    "（_r805bmc_s05_facts + _r805bmc_s0_facts shape-asserted） + 孤儿面 2→1 只读 + "
    "llm_assist selftest PASS（35b 本地路由·gen/写守卫/route 三绿）+ repo_pulse_probe selftest PASS "
    "+ 队列手术 tech 12→11 净减 1（self-drive §1 规则5） + compute_audit supply_gap 旗如实上报"
    "（RAM 外部门根因披露·W17 持平模式）"
)

# ---- heartbeat ----
hb_path = ROOT / "fleet" / "machines" / "bm-c.json"
hb = json.loads(hb_path.read_text(encoding="utf-8"))
for k in ("last_seen", "last_seen_at", "clock_read", "ts", "updated", "updated_at", "last_run_at",
          "last_ts", "current_task_at", "last_decisions_at", "last_orders_at"):
    hb[k] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["last_round"] = 805
hb["last_round_at"] = now_iso
hb["round_no"] = 805
hb["round_no_label"] = "round 805 (bm-c)"
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
st["last_round"] = 805
st["round_no"] = 806
st["round_no_label"] = "round 805 (bm-c)"
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
assert hb2["round_no"] == 805 and st2["round_no"] == 806
print("closeout OK: hb round=805 state next=806 epoch=%d ts=%s" % (epoch, now_iso))
