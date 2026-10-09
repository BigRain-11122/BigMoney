# -*- coding: utf-8 -*-
"""r802 bm-c closeout: heartbeat/state/round-report bookkeeping.
Law: fleet/README.md sec.6 machine-split files; epoch must be JSON int
(R170/R178); clock_read ISO8601 T-separator (R262); products-first 3-line
face. Pattern credit: Tools/_r789bmc_closeout.py (canon)."""
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
ORD_SHA = "2D9DF88A18A0F7A36A5E20BFC866C843E864A1AD"
DEC_METHOD = (
    "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r802 closing sweep = "
    "CONSUMED delta A4303E92->BD94A27B (group 10-09 12:00+ batch: C-20261009-01 Biggame council audit "
    "+ C-20261009-02 all-company audit incl BigMoney verdict zhong-pian-healthy + @BigMoney dispatch "
    "3-items executed same round F-20261009-04 + D-20260930-06 orders sweep non-quant); facts-driven "
    "from results/_r802bmc_s0_facts.json + results/_r802bmc_dec_delta.txt, 64hex shape-asserted, "
    "never hand-typed (r583 S4 law)")
ORD_METHOD = (
    "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r802 closing sweep = CONSUMED "
    "delta 40FE3CB2->2D9DF88A (orders group 10-09 update: added rows = O-20261009-1216 Biggame council "
    "audit order + O-20261009-1227 all-company audit+improve order incl @BigMoney 3-item dispatch, "
    "executed same round per CEO immediate law, receipt F-20261009-04); facts-driven from "
    "results/_r802bmc_s0_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law)")

did = (
    "2026-10-09T{hm}+08:00 | r802 | dept:工程/研究（C-20261009-02 @BigMoney 派单三件同轮执行+PARKING 设计件 v0.2 判据键对齐+常设链全绿·第 103 bm-c 连守轮） | "
    "本地未达 origin commit 数=0（commit 后 push+fetch 自证） | "
    "WM-VERDICT: 绿（red=false·probe verdict=insufficient_history 新窗 n=1 合法读数·lane=healthy·"
    "next_pick=claimed moneyflow IC bm-a 车道合法·DEC A4303E92→BD94A27B/ORD 40FE3CB2→2D9DF88A 双消费"
    "〔轮首扫=C-01 Biggame+D-06 长龄专扫非本司零动作·收尾扫=C-20261009-02 全司逐审案涉本司=BigMoney 定谳中偏健康+"
    "@BigMoney 派单三件同轮执行 F-20261009-04 回执落账〕·unacked 0〔55 orders〕·inbox 0） | "
    "孤儿面=1（ComfyUI 产线资产只读不杀〔12:4x 探针 r340 三面判别〕·W17 screens 0-3 autofill 认领 keepalive b8a5e6f50·"
    "RAM 门 1.6GB<4GB 待窗·deadline 判别律只读） | "
    "r802: ①S0 定向吸收+rebase 绿：轮首脏树（r801 收口后 daemon live-face 13 件+inbox processed 移动 2 件）→"
    "定向 add 核 staged 11 件→吸收 commit 4c059fab2（amend×2 竞窗续收 3+2 面）→pull --rebase 干净零 UU"
    "（origin 两新 commit=bm-a r914 daemon 吸收+W197 prereg build·与本地脏面零重叠）→tip 6cf95b06b；"
    "②S0.5 双扫消费见 WM 行（水位键随收尾更新·facts=_r802bmc_s05_facts+_r802bmc_s0_facts+dec_delta 探针件·shape-asserted）；"
    "③S1 smoke 49/49+QA r802 证据包 5/5（smoke-r802-bm-c.md·91 trades·sharpe 0.1994·determinism=True·"
    "equity PNG 65,612B·per-machine 后缀律）；"
    "④S6 40/40 rc0 二十三连绿（dualrun ZERO-DRIFT streak 51 维持·fund_premium 15:30 前诚实 no-op〔第十五观测窗〕·"
    "update_daily 10-08 截止零新行·update_options RETIRED no-op 面·R31 他机车道 no-op 族照录）；"
    "⑤主产出 A=PARKING 引擎腿设计件 v0.2 对齐修订（bm-a prereg FROZEN b904a0a0e 提前到站→判据键引用面全落地："
    "§2.3 成本 26.082bp×1/×2/×3=52.164/78.246 冻结引用+接线出场轴=①策略自有出场声明·§2.4 Face3 红线 p95 A −3.0%/B −6.0%+"
    "硬尾帽 A −10%/B −15% 读数引用+Face4 熊集 510300<MA200 钩子·§3 m1_t_value_gate t≥3.0+bootstrap CI+g1_prime_v2+"
    "g2_registration_v2 键引用+B-直池 honest-gated 不进冻结格集+C2 repo 主基线+seed 94_300+evidence_cutoff 2026-09-22·"
    "82 行结构自检过·两权分立律=引用非重定义·SLA ≤10-16 提前 7 天收口）；"
    "⑥主产出 B=C-20261009-02 @BigMoney 派单三件同轮执行（CEO 直令 O-20261009-1227 委员会通道·回执窗 10-10 00:00）："
    "清临时件=257 件 bmc 属主根级 commit-msg 临时件 treasure_guard 正典链隔离（prescan 登记簿零命中 rc0→"
    "quarantine results/_quarantine/20261009-124800/→assert 257/257 identity-verified·7 天观察窗·"
    "35 件 bma/bmb 他机属主面不动留各自机自清）+README 续鲜（当前状态/下一步节 09-23 纪元→10-09 实况刷新·"
    "根级文档低频编辑律零越界）+池补 1 承接（F-20261009-04：基线 ready=9·委员会改善件④已定谳时点差合法·"
    "真实供给=W18 链按正典序 standing_no_judge_inflight+W17 判词依赖排队·禁假填充）；"
    "⑦S7 自愈批全绿（loop pin=5 no-op·watchdog -Force 重注册·双爪 LF-normalized 重装·attrition 4 台账 CLEAN〔3 healed 注记照录〕）·"
    "SAT 引擎活 rc0·job 板清·idle 非绿档（RAM 9%<40%）无领单义务·idle --worked 清零·"
    "捕获律=方法论资产卡零·宝藏登记零 | 下轮指针: r803=①W17 screens 4-7+JUDGE 池烧随 RAM 窗自续（autofill 常轨·"
    "SLA 10-10 00:00·T-178 judge verdict→s4 intake→48h CEO 呈报链）②池补 1 W18 链承接推进（W17-JUDGE 排水后候选起草→"
    "F-20261009-04 随班回执）③fund_premium 15:30+ NAV 首采（T+1 发布面·第十五观测窗收口）④MV 三选项勾选等待态维持"
    "⑤bm-a PARKING-P1 判决跑窗跟进（<3min 单核·过门→接线 v1.0）"
).format(hm=HM)

activity = (
    "当前活: r802 bm-c（12:2x-12:5x 窗·C-20261009-02 @BigMoney 派单三件执行+PARKING 设计件 v0.2+常设链全绿·第 103 连守轮）——"
    "主产出=派单三件（257 临时件隔离+README 续鲜+池补 1 承接）+设计件 v0.2 判据键对齐（bm-a prereg FROZEN b904a0a0e 消费面） | "
    "最近实物: research/PARKING_P1_ENGINE_LEG_DESIGN.md（v0.2·82 行）+results/_quarantine/20261009-124800/manifest.json（257 件）"
    "+README.md（续鲜）+qa/smoke-r802-bm-c.md（5/5）+HQ-FEEDBACK.md（F-20261009-04）@ 本轮收口 commit | "
    "下个里程碑: r803 W17 池烧随 RAM 窗自续+judge verdict→48h CEO 呈报（SLA 10-10 00:00）+fund_premium 15:30+ 首采+W18 池补链推进"
)

artifact = (
    "research/PARKING_P1_ENGINE_LEG_DESIGN.md (v0.2 criteria-key alignment vs frozen prereg b904a0a0e, 82 lines) "
    "+ results/_quarantine/20261009-124800/ (257 bm-c root temp-msg files, manifest 257/257 identity-verified, "
    "prescan zero-hit) + README.md (2026-10-09 refresh) + HQ-FEEDBACK.md (F-20261009-04 dispatch receipt) "
    "+ qa/smoke-r802-bm-c.md 5/5 + qa/equity-curve-r802-bm-c.png + results/_r802bmc_s6_log.txt (40/40 rc0 23rd green) "
    "+ results/_r802bmc_s05_facts.json + results/_r802bmc_s0_facts.json + results/_r802bmc_dec_delta.txt "
    "+ Tools/_r802bmc_{s05,s6,qa_ignite,tempmsg_quarantine,close}.py @ " + now_iso
)

nxt = (
    "r803 续作: ①W17 screens 4-7+JUDGE 池烧随 RAM 窗自续（autofill 常轨·lane 钉 bm-c r429·screens 0-3 keepalive 在飞·"
    "RAM 门 1.6GB<4GB 待窗·SLA 10-10 00:00）②池补 1 W18 链承接推进（W17-JUDGE 排水后 W18 候选起草→探针→冻结→入池·"
    "F-20261009-04 随班回执·依赖链如实披露禁假填充）③fund_premium 10-08 NAV 首采（发布面 T+1·15:30+ 轮·第十五观测窗收口）"
    "④MV 三选项勾选等待态维持 ⑤bm-a PARKING-P1 判决跑窗跟进（<3min 单核·过门→停泊袖接线 v1.0 10-31 月界前）"
    "⑥T-2026-10-09-178-P1 判决链票跟进（池烧完成前不关票）"
)

verify = (
    "C-20261009-02 派单 git 可验（results/_quarantine/20261009-124800/manifest.json 257 件 sha256 + treasure_guard assert OK "
    "257/257 + prescan zero-hit + README diff + F-20261009-04 receipt） + 设计件 v0.2（research/PARKING_P1_ENGINE_LEG_DESIGN.md "
    "82 行·b904a0a0e prereg FROZEN 引用面·两权分立律） + smoke 49/49 + QA smoke-r802-bm-c.md 5/5（91 trades·determinism=True·"
    "equity PNG 65,612B） + S6 40/40 rc0 二十三连绿（results/_r802bmc_s6_log.txt） + dualrun ZERO-DRIFT streak 51 + "
    "attrition 4 台账 CLEAN + 双爪重装 + loop pin=5 + watchdog -Force + SAT 引擎活 + DEC BD94A27B/ORD 2D9DF88A 双消费"
    "（_r802bmc_s05_facts + _r802bmc_s0_facts + _r802bmc_dec_delta.txt shape-asserted） + 孤儿面=1 只读"
    "（ComfyUI 产线+W17 autofill 认领面 deadline 注记）"
)

# ---- heartbeat ----
hb_path = ROOT / "fleet" / "machines" / "bm-c.json"
hb = json.loads(hb_path.read_text(encoding="utf-8"))
for k in ("last_seen", "last_seen_at", "clock_read", "ts", "updated", "updated_at", "last_run_at",
          "last_ts", "current_task_at", "last_decisions_at", "last_orders_at"):
    hb[k] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["last_round"] = 802
hb["last_round_at"] = now_iso
hb["round_no"] = 802
hb["round_no_label"] = "round 802 (bm-c)"
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
st["last_round"] = 802
st["round_no"] = 803
st["round_no_label"] = "round 802 (bm-c)"
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
assert hb2["round_no"] == 802 and st2["round_no"] == 803
print("closeout OK: hb round=802 state next=803 epoch=%d ts=%s" % (epoch, now_iso))
