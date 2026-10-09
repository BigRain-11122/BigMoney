# -*- coding: utf-8 -*-
"""r809 bm-c closeout: heartbeat/state/round-report bookkeeping (single-shift
round, no adoption). Law: fleet/README.md sec.6 machine-split files; epoch
must be JSON int (R170/R178); clock_read ISO8601 T-separator (R262);
products-first 3-line face; DEC/ORD shas READ PROGRAMMATICALLY from the
closing facts file -- ZERO literal sha constants (r583 law); ledger append
carries the r843 tail-CRLF guard; NO %-formatting anywhere in narrative
strings (r661 literal-% pit avoided by construction).
Pattern credit: Tools/_r808bmc_close.py (r808 canon, 1-gen clone)."""
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
facts = json.loads((ROOT / "results" / "_r809bmc_s0_facts.json")
                   .read_text(encoding="utf-8"))
DEC_SHA = facts["dec_sha"]
ORD_SHA = facts["ord_sha"]
assert len(DEC_SHA) == 64 and len(ORD_SHA) == 40, "watermark shape gate"
assert facts.get("shape_assert") is True, "facts shape_assert gate"
assert facts.get("prev_dec_corrupt") is False, "r809: DEC prev must be 64hex clean"
assert facts.get("prev_ord_corrupt") is False, "r809: ORD prev must be 40hex clean"
assert facts.get("unacked") == [], "r809 closing: zero unacked orders"
assert facts.get("inbox_unread") == [], "r809 closing: zero unread inbox"

DEC_METHOD = (
    "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r809 start 16:1x + closing "
    "double-sweep zero-delta; group-tree SSH fetch reset x2 this round -> HTTPS fallback leg "
    "(Tools/_r809bmc_group_https.py, private temp ref refs/tmp/bmc-r809-group, zero origin/main touch, r805 "
    "netpath law): fresh https tip bc54a96de == local origin/main (stale=False) -> start-sweep hashes stand "
    "CONFIRMED via fresh channel; facts-driven from results/_r809bmc_s05_facts.json + results/_r809bmc_s0_facts.json, "
    "64hex shape-asserted; close-face reads sha PROGRAMMATICALLY from facts json, ZERO literal constants (r583 law)")
ORD_METHOD = (
    "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r809 start 16:1x + closing double-sweep "
    "zero-delta; group-tree SSH fetch reset x2 -> HTTPS fallback leg confirmed fresh tip == origin/main; "
    "facts-driven from results/_r809bmc_s05_facts.json + results/_r809bmc_s0_facts.json, 40hex shape-asserted; "
    "close-face reads sha PROGRAMMATICALLY from facts json, ZERO literal constants (r583 law)")

did = (
    "2026-10-09T" + HM + "+08:00 | r809 | dept:工程+数据（S6 全链 40/40+sina 迟 bar 第 3 轮守+QA det-99th 净写·第 110 bm-c 连守轮） | "
    "本地未达 origin commit 数=0（commit 后 push+fetch 自证·HTTPS ls-remote 送达面） | "
    "WM-VERDICT: 绿（red=false·lane=healthy·next_pick=claimed moneyflow IC bm-a 车道合法"
    "·DEC BD94A27B 零差/ORD F26E1A37 零差〔SSH fetch 两连重置→HTTPS 备胎腿复核：新 tip bc54a96de==origin/main 陈旧=False·零差经新鲜通道确认〕"
    "·unacked 0〔55 orders〕·inbox 0） | "
    "孤儿面=1（只读不杀） | "
    "r809: ①S0 吸收 6 daemon 面（55ecbf02a）+rebase origin/main CLEAN（并入 bm-a r919 三连收口 commit·0 UU）"
    "+S0.5 双扫（start+closing 零增量）+inbox 1 件消费（MSG-2026-10-09-1507-bma-w199-seat：W199 席位公示=reserved bm-a 114th owned/189th wave"
    "·W200+ 投影须 post-W199 宇宙重derive〔W141 leg2 律〕——bm-c 零动作·移 processed·回执本行）；"
    "②S1 smoke 49/49+SAT 引擎活（rc0·N1 注册面 W199 在册可见）+S2 板清（job 板零·T-178=W17 本机在飞线·T-177=bm-a 已认领）；"
    "③**S6 全链 40/40 rc0（本轮主产出·分离点火防 25min 斩首〔bm-a r919 晚链先例〕**"
    "——update_daily 10-09 bar 第 3 轮 sina 迟发守（16:23:41 new rows=0·cutoff 10-08 保持"
    "·tencent 探针 upstream_has_newer_bar tencent_latest=10-09=bar 上游已在·sina 面迟发诚实下轮重试）"
    "·marks/live_paper/REGIME 自续面候 bar 落地·paper 族（aggressive/grid/alloc/cta/system_v1）rc0 幂等"
    "·fund_premium 第 16 观察窗 no-op（10-09 NAV T+1 明日发布面）·daily_report+ceo_live_usage 再生；"
    "④**QA det-99th 证据包 r809 槽净写**：撞名预检 origin 全列零 r809 件→分离点火 --round 809 显式轮标（r758 律）"
    "→qa/smoke-r809-bm-c.md 5/5+qa/equity-curve-r809-bm-c.png（65,409B·800 bar 终值 1,023,027·CALL cell=ORA·determinism）"
    "→r640 轮询律 close 前终态核验；"
    "⑤S7 自愈四件套（loop pin=5 no-op+watchdog 16:26 首发+双爪 LF 归一重装）+attrition 4 台账 CLEAN（healed 史披露）；"
    "⑥诚实披露：根级 round_reports-bm-c.md 尾=r779 观察=r646 冻结孤儿面误警（legacy 正典件 r775-r779 五行双在册·r780-r808 零缺口·零治愈需求）"
    "+wrapper 单串输出行滤误探针×2（pit-ps-wrapper 单串输出/行拆消费面已知坑·facts 件直读恢复·无新坑条目）"
    "+idle 非绿（RAM 8.8 pct<40 pct 实工轮·idle_rounds=0·agenda 未饿）"
    "+W17 屏烧在飞（JUDGE RAM 门停泊 1.6GB<4GB·池 claimable=9·supply_floor 9>=3 无破·SLA >=10 due 10-10 00:00 候屏烧翻面 r810+ 核验）"
    "+tech T4 未消耗（25min 窗优先级让位 S6+QA+收口完整性·留队头）"
    " | 下轮指针: r810=①10-09 bar 落地重试（sina 迟发第 3 轮·tencent 已证 bar 在·落地即 marks/live_paper/REGIME 自续）"
    "②W17 屏烧翻面跟随+池 >=10 SLA 核验（10-10 00:00 窗）③tech 队列 T4 队头消耗（town.html 对齐 org_chart v2）"
    "④O-20261009-1105 @bm-c② exit-to-asset 设计件 <=10-16 12:00"
)

activity = (
    "当前活: r809 bm-c S6 全链 40/40 rc0+QA det-99th 净写+sina 迟 bar 第 3 轮守（第 110 连守轮） | "
    "最近实物: qa/smoke-r809-bm-c.md（5/5）+qa/equity-curve-r809-bm-c.png（65,409B）"
    "+results/_r809bmc_s6_log.txt（40/40 rc0·DONE 16:24:48）+Tools/_r809bmc_* helper 六件套"
    "@本轮收口 commit | "
    "下个里程碑: 10-09 bar 落地（marks/REGIME 自续）+W17 屏烧翻面（SLA 10-10 00:00）+tech T4 下轮队头"
)

artifact = (
    "Tools/_r809bmc_{s05,s6,s6_ignite,qa_ignite,group_https,close}.py (r809 helper sextet; s05 double-sweep "
    "start+closing zero-delta; s6 detached-ignite per bm-a r919 evening-chain precedent; group_https = "
    "SSH-reset fallback leg per r805 netpath law) "
    "+ results/_r809bmc_s05_facts.json + results/_r809bmc_s0_facts.json + results/_r809bmc_group_https.json "
    "+ results/_r809bmc_s6_log.txt + results/_r809bmc_s6_runner.out (40/40 rc0 evidence, DONE 16:24:48) "
    "+ results/_r809bmc_qa_runner.out "
    "+ qa/smoke-r809-bm-c.md (5/5 QA charter, 800-bar final 1,023,027, CALL cell ORA, determinism) "
    "+ qa/equity-curve-r809-bm-c.png (65,409B, det-99th clean first-write) "
    "+ results/_attrition_guard_scan.json CLEAN (4 ledgers, healed history disclosed) "
    "+ results/_orphan_face_probe.bm-c.json (orphan face 1, read-only) @ " + now_iso
)

nxt = (
    "r810 续作: ①10-09 bar 落地重试（sina 迟发第 3 轮·tencent 探针已证 bar 上游在·落地即 "
    "marks/live_paper/REGIME v3 自续+paper export 刷新）"
    "②W17 screens 烧翻面跟随+池 claimable >=10 SLA 核验（10-10 00:00 窗·现 9 ready）"
    "③tech 队列 T4 队头消耗（town.html 楼名/详情对齐 firm/org_chart.md v2）"
    "④O-20261009-1105 @bm-c② exit-to-asset 引擎腿设计件 <=10-16 12:00"
    "⑤MV 三选项等待态维持+bm-a PARKING-P1 跟进"
)

verify = (
    "smoke 49/49 + S6 40/40 rc0（results/_r809bmc_s6_log.txt + _r809bmc_s6_runner.out·DONE 16:24:48） "
    "+ qa/smoke-r809-bm-c.md 5/5（PNG 65,409B·800 bar 终值 1,023,027·det-99th 零撞名净写·r640 close 前终态核验） "
    "+ attrition 4 台账 CLEAN（healed 史披露） + 自愈四件全绿（loop pin=5 幂等+watchdog 16:26 首发+双爪 LF 归一重装） "
    "+ 孤儿面=1 只读（收尾探针） + DEC/ORD 双扫零差（BD94A27B/F26E1A37·SSH 两连重置后 HTTPS 备胎新鲜通道确认·prev 双清） "
    "+ unacked 0〔55 orders〕 + inbox 0（W199 席位 MSG 消费移 processed·回执轮报行） "
    "+ idle 非绿（RAM 8.8 pct<40 pct 实工轮·idle_rounds=0） + W17 屏烧在飞披露（JUDGE RAM 门停泊·claimable 9·SLA 10-10 00:00 候核验）"
)

# ---- heartbeat ----
hb_path = ROOT / "fleet" / "machines" / "bm-c.json"
hb = json.loads(hb_path.read_text(encoding="utf-8"))
for k in ("last_seen", "last_seen_at", "clock_read", "ts", "updated", "updated_at", "last_run_at",
          "last_ts", "current_task_at", "last_decisions_at", "last_orders_at"):
    hb[k] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["last_round"] = 809
hb["last_round_at"] = now_iso
hb["round_no"] = 809
hb["round_no_label"] = "round 809 (bm-c)"
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
st["last_round"] = 809
st["round_no"] = 810
st["round_no_label"] = "round 809 (bm-c)"
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

# ---- round report (canonical machine-split ledger path, fleet/README sec.6) ----
rr_path = ROOT / "logs" / "iteration-loop" / "round_reports-bm-c.md"
raw = rr_path.read_bytes()
if not raw.endswith((b"\r\n", b"\n")):   # r843 tail-terminator guard
    with rr_path.open("a", encoding="utf-8") as f:
        f.write("\r\n")
with rr_path.open("a", encoding="utf-8") as f:
    f.write(did + "\n")

# ---- self-checks ----
hb2 = json.loads(hb_path.read_text(encoding="utf-8"))
st2 = json.loads(st_path.read_text(encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int"
assert isinstance(st2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in hb2["clock_read"] and "+" in hb2["clock_read"], "clock_read must be ISO8601 T-form"
assert hb2["round_no"] == 809 and st2["round_no"] == 810
assert len(hb2["last_decisions_sha"]) == 64 and len(hb2["last_orders_sha"]) == 40, "watermark shape gate"
tail = rr_path.read_text(encoding="utf-8", errors="replace").rstrip().splitlines()[-1]
assert tail.startswith("2026-10-09T"), "ledger tail must be this round row"
print("closeout OK: hb round=809 state next=810 epoch=%d ts=%s dec=%s ord=%s"
      % (epoch, now_iso, DEC_SHA[:8], ORD_SHA[:8]))
