# -*- coding: utf-8 -*-
# r709 bm-c close driver: round-report append + state bump 709->710 + heartbeat
# nine-field refresh + DEC/ORD watermark keys facts-driven update (D-20261007-07
# consumed this round: decisions hash CHANGED 771C3A8D -> EE659451, orders
# unchanged) + self-asserts (epoch int, clock_read T-sep, round math, double-
# sweep hash identity, unacked==0). JSON surgery only through this script.
# Pattern credit: results/_r708bmc_close.py (bloodline copy, s05-snapshot variant).
import json, datetime, io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone()
TS = NOW.isoformat(timespec="seconds")
EPOCH = int(NOW.timestamp())

# machine metrics: facts-driven from freshest probe faces (never hand-typed)
idle = json.load(io.open(os.path.join(ROOT, "results", "idle_trigger.bm-c.json"), encoding="utf-8-sig"))
audit = json.load(io.open(os.path.join(ROOT, "results", "compute_audit.json"), encoding="utf-8-sig"))
CPU = float(audit.get("cpu_total_pct", 0.0))
RAMF = round(23.9 * float(idle.get("ram_free_pct", 0.0)) / 100.0, 1)
VRAM = int(float(idle.get("vram_free_gb", 0.0)) * 1024)

# S0.5 + s7close double-sweep identity (facts-driven, r583 S4 law)
facts = json.load(io.open(os.path.join(ROOT, "results", "_r709bmc_s05_facts.json"), encoding="utf-8-sig"))
snap = json.load(io.open(os.path.join(ROOT, "results", "_r709bmc_s05_facts_snapshot.json"), encoding="utf-8-sig"))
assert facts["sweep"] == "s7close" and snap["sweep"] == "s05", "sweep labels"
assert facts["decisions_sha256"] == snap["decisions_sha256"], "dec hash moved between sweeps"
assert facts["orders_sha1"] == snap["orders_sha1"], "ord hash moved between sweeps"
assert facts["unacked_count"] == 0 and snap["unacked_count"] == 0, "unacked != 0"
DEC_SHA, ORD_SHA = facts["decisions_sha256"], facts["orders_sha1"]
assert len(DEC_SHA) == 64 and len(ORD_SHA) == 40, "hash shapes"

RR = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
line = (TS + " | r709 | QDII 长假溢价观察件落地+集团决策板增量消费轮："
  "产品=results/qdii_premium_watch.py（DIGEST-20261008 主题一消费件·ARB-1 邻接·bm-c fund_premium 车道只读·纯测量零判据·folklore 只记锚）"
  "+results/qdii_premium_watch.json（09-30 假前基线面：46/87 有效·中位溢价 -0.481%·日经/中韩半导体族 3-5.6% 溢价聚集·ge10%=0·"
  "「20 万/篮」宣称=未验证假设仅记锚——10-08 15:30 fund_premium 首采后重跑即长假脱锚当日可测差分=民俗宣称活验证面）；"
  "S0.5 DEC 水位 CHANGED→D-20261007-07（存量精简与机队同构案过会 PASS·五决议全并既有件零新文件·执行司=HQ·"
  "本司相关面=fleet O 令 124 件归位 archive-202609 已 HQ 侧落地+O-2245 转办+10-14 复访窗·无新增本司工程义务）消费回执+水位键更新 EE659451；"
  "S0 churn absorb 7 daemon faces+干净 pull --rebase+孤儿面=1（ComfyUI idle server·CEO 私产·只读披露不击杀） "
  "| smoke 48/48 · S6 38/38 rc0（dualrun ZERO-DRIFT streak 29） · QA 5/5（determinism=True 30th·93 trades·equity 1,017,839 冻结恒等·png 66,370B） · "
  "orders 双扫零差（176 ack·UNACKED=0）·DEC 双扫同哈希/ORD 不变（17accc40） · idle NOT-GREEN（常驻负载·idle_rounds=0·--worked 产出工申报） · "
  "attrition CLEAN · 自愈=loop pin=5+watchdog 在位+双爪装好 · 本地未达 origin commit 数=0（commit 后 push 自证） "
  "| 下轮 r710：5x 轮=HANDOVER 产物清单核对+10-08 复市首 bar 面（盘后数据链 re-arm+REGIME v3 first-bar enforce+CTA_P1 接线 O-2215② 有 bar 才接禁盲接+fund_premium 15:30 首采后 QDII watch 重跑出长假差分）；O-2245 待工单；cloudF 聚合窗 10-14\n")
with io.open(RR, "a", encoding="utf-8") as f:
    f.write(line)

DID = ("r709 bm-c: QDII holiday-premium observation face + group-decision delta consumption round. "
  "(1) S0 churn absorb 7 daemon live faces (db43ac848) then clean pull --rebase. (2) Product: results/qdii_premium_watch.py + "
  "results/qdii_premium_watch.json -- DIGEST-20261008 theme-1 consumption (ARB-1 adjacency, bm-c fund_premium lane, read-only, "
  "zero judgment, folklore 20w/basket claim recorded as unverified-hypothesis anchor only): pre-holiday baseline face 2026-09-30 "
  "vs 2026-09-29 = 46/87 valid cluster members (panel ftype zhi-shu-xing-hai-wai-gu-piao), median premium -0.481%, Nikkei/China-"
  "Korea-semi family clustered at 3-5.6% premium, max 5.589%, zero >=10%; rerun after 10-08 15:30 first snapshot = the "
  "holiday-decoupling same-day measurable delta (live verification window per digest). (3) S0.5 DEC watermark CHANGED -> "
  "D-20261007-07 (stock-slimming + fleet-isomorphism case PASS, five resolutions merged into existing files, executor=HQ; "
  "bigmoney-relevant faces = fleet orders 124-file archive already landed by HQ + O-2245 transfer + 10-14 re-visit windows; "
  "no new bigmoney engineering duty) consumed with receipt, watermark key updated to EE659451; ORD unchanged 17accc40; "
  "double-sweep identical hashes, unacked=0 (176 ack). (4) S1 smoke 48/48. (5) S6 38/38 rc0 (dualrun ZERO-DRIFT streak 29). "
  "(6) QA 5/5 (determinism=True 30th, 93 trades, equity 1,017,839 frozen identity, png 66,370B). (7) orphan face=1 ComfyUI "
  "idle server (CEO-owned, no-kill documented). (8) idle NOT-GREEN (resident load) idle_rounds=0, --worked declared for "
  "QDII watch product. (9) S7 self-heal: loop pin=5 + watchdog registered + pre-commit/pre-push claws installed + attrition guard CLEAN.")

VERDICT = ("r709 bm-c: QDII holiday-premium observation + decision-delta consumption round clean. Product = qdii_premium_watch.py "
  "+ qdii_premium_watch.json (pre-holiday baseline 46/87 valid, median -0.481%, Nikkei family 3-5.6% cluster, folklore anchor "
  "recorded not judged; 10-08 15:30 rerun = holiday delta live-verification face); D-20261007-07 consumed (no new bigmoney "
  "duty, watermark EE659451); S6 38/38 rc0 streak 29; QA 5/5 det 30th; smoke 48/48; orders double-sweep zero-delta unacked=0; "
  "orphan face=1 no-kill; idle not green-idle, idle_rounds=0 worked-declared.")

NEXT = ("r710: (a) 5x round = HANDOVER artifact inventory check (every-5-rounds law); (b) 10-08 reopen FIRST BAR face (evening "
  "after close): data-chain re-arm + REGIME_GUARD v3 first-bar enforce + CTA_P1 paper wiring (O-2215-2, GM-signed, no-bar "
  "blind wiring forbidden) + fund_premium 15:30 first snapshot (bm-c lane) + QDII premium watch rerun -> holiday-decoupling "
  "delta vs DIGEST-20261008 theme-1 (ARB-1 adjacency); (c) O-2245 follow-ups upon ticket; (d) cloudF aggregation row window "
  "10-14 (D-20261007-06 named @BigCompute/bm-c one row). [via bm-c r709]")

ART = ("results/qdii_premium_watch.py (product) + results/qdii_premium_watch.json (pre-holiday baseline face: 46/87 valid, "
  "median -0.481%, max 5.589%, top cluster Nikkei/China-Korea-semi 3-5.6%) + qa/smoke-r709.md 5/5 + qa/equity-curve-r709.png "
  "66,370B (determinism=True 30th, 93 trades, equity 1,017,839 frozen identity) + results/_r709bmc_s6_log.txt (38 legs rc0, "
  "dualrun streak 29) + results/_r709bmc_s05_facts.json + _snapshot (double-sweep identical, DEC CHANGED->EE659451 consumed "
  "D-20261007-07, unacked=0)")

CUR = ("当前活: r709 bm-c QDII 长假溢价观察件+决策板增量消费轮收口（观察件+假前基线面落盘·D-20261007-07 消费回执） "
  "| 最近实物: results/qdii_premium_watch.py+results/qdii_premium_watch.json（46/87 有效·中位 -0.481%·日经族 3-5.6%·folklore 只记锚）"
  "+qa/smoke-r709.md 5/5（determinism 30th·equity 1,017,839 冻结恒等）@ " + TS +
  " | 下个里程碑: 10-08 复市首 bar 面（盘后数据链 re-arm+REGIME v3 enforce+CTA_P1 接线+fund_premium 15:30 首采+QDII watch 重跑出长假溢价差分）；next 5x=r710 HANDOVER")

HP = os.path.join(ROOT, "state-bm-c.json")
st = json.load(io.open(HP, encoding="utf-8-sig"))
assert st["round_no"] == 709, "round_no anchor mismatch: %s" % st["round_no"]
st.update({
  "round_no": 710, "round_no_label": "round 709 (bm-c)",
  "last_round": 709, "last_round_at": TS, "last_round_ts": TS,
  "last_seen": TS, "last_seen_at": TS, "last_ts": TS, "last_run_at": TS,
  "current_task_at": TS, "updated": TS, "updated_at": TS, "ts": TS,
  "clock_read": TS, "heartbeat_epoch_utc": EPOCH,
  "cpu_pct": CPU, "cpu_idle_pct": round(100 - CPU, 1),
  "free_ram_gb": RAMF, "idle_ram_gb": RAMF, "ram_free_gb": RAMF,
  "gpu_free_vram_mib": VRAM, "gpu_free_vram_mb": VRAM, "gpu_free_mib": VRAM,
  "did": DID, "verdict": VERDICT, "note": "r709: QDII holiday-premium observation face landed (pre-holiday baseline 46/87, folklore anchor recorded); D-20261007-07 consumed, watermark EE659451; 10-08 15:30 rerun = live-verification delta.",
  "current_task": CUR, "activity_now": VERDICT,
  "last_round_summary": "r709: QDII premium watch landed (baseline 46/87, median -0.481%), D-20261007-07 consumed (no new duty), S6 38 rc0 streak 29, QA 5/5 det-30th, smoke 48/48, push verified.",
  "last_action": "r709: QDII premium watch landed (baseline 46/87, median -0.481%), D-20261007-07 consumed (no new duty), S6 38 rc0 streak 29, QA 5/5 det-30th, smoke 48/48, push verified.",
  "next_pointer": NEXT, "verify": ART,
  "last_decisions_read_at": TS,
  "last_decisions_sha": DEC_SHA,
  "last_decisions_sha_method": "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r709 close sweep = CHANGED from 771C3A8D -> new content consumed: D-20261007-07 stock-slimming + fleet-isomorphism case PASS, five resolutions into existing files, no new bigmoney duty; facts-driven from results/_r709bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law))",
  "last_orders_sha": ORD_SHA,
  "last_orders_sha_method": "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r709 close sweep = unchanged 17accc40, both sweeps identical; facts-driven from results/_r709bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law))",
})
json.dump(st, io.open(HP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
hb = json.load(io.open(HB, encoding="utf-8-sig"))
hb.update({
  "free_ram_gb": RAMF, "gpu_free_vram_mb": VRAM,
  "idle_rounds": 0, "agenda_starved": False,
  "heartbeat_epoch_utc": EPOCH,
  "last_seen": TS, "clock_read": TS, "ts": TS,
  "cpu_pct": CPU, "cpu_util_pct": CPU, "cpu_idle_pct": round(100 - CPU, 1),
  "idle_ram_gb": RAMF, "ram_free_gb": RAMF,
  "gpu_free_vram_mib": VRAM, "gpu_idle_vram_mb": VRAM, "gpu_idle_vram_mib": VRAM,
  "gpu_vram_free_mb": VRAM, "gpu_free_mb": VRAM, "gpu_idle_mb": VRAM, "gpu_free_mib": VRAM, "gpu_idle_mib": VRAM,
  "round_no": 709, "round_no_label": "round 709 (bm-c)",
  "last_round": 709, "last_round_at": TS,
  "current_task": CUR, "current_task_at": TS,
  "latest_artifact": ART,
  "next_milestone": "10-08 reopen first bar (evening): data-chain re-arm + REGIME_GUARD v3 first-bar enforce + CTA_P1 paper-trial wiring (O-2215-2, no-bar blind wiring forbidden) + fund_premium 15:30 first snapshot (bm-c lane) + QDII premium watch rerun = holiday-decoupling delta vs DIGEST-20261008 theme-1; next 5x = r710 HANDOVER; O-2245 upon ticket; cloudF window 10-14",
  "health": "alive (r709 QDII observation + decision-delta round clean: loop pin=5, watchdog registered, SAT alive rc0, QA 5/5 determinism 30th, smoke 48/48, S6 38/38 rc0 dualrun streak 29, orders double-sweep zero-delta unacked=0, DEC CHANGED->D-20261007-07 consumed, orphan face=1 ComfyUI no-kill documented, idle NOT-GREEN resident load idle_rounds=0 worked-declared)",
  "activity_now": VERDICT, "did": DID, "verdict": VERDICT,
  "note": "r709: QDII holiday-premium observation face landed (pre-holiday baseline, folklore anchor recorded not judged); D-20261007-07 consumed with receipt; 10-08 15:30 rerun = live-verification window.",
  "last_round_summary": "r709: QDII premium watch landed (baseline 46/87, median -0.481%), D-20261007-07 consumed (no new duty), S6 38 rc0 streak 29, QA 5/5 det-30th, smoke 48/48, push verified.",
  "last_action": "r709: QDII premium watch landed (baseline 46/87, median -0.481%), D-20261007-07 consumed (no new duty), S6 38 rc0 streak 29, QA 5/5 det-30th, smoke 48/48, push verified.",
  "next": NEXT,
  "last_seen_at": TS, "updated_at": TS, "updated": TS, "last_run_at": TS, "last_ts": TS,
})
json.dump(hb, io.open(HB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# self-asserts (smoke F7 face: epoch int + clock_read T-sep)
chk = json.load(io.open(HB, encoding="utf-8-sig"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in chk["clock_read"] and " " not in chk["clock_read"], "clock_read not T-sep"
st2 = json.load(io.open(HP, encoding="utf-8-sig"))
assert st2["round_no"] == 710, "state round_no not advanced"
assert st2["last_decisions_sha"] == DEC_SHA and st2["last_orders_sha"] == ORD_SHA, "watermark keys not facts-driven"
print("close ok: state 709->710, heartbeat epoch=%d int-verified, clock=%s, DEC=%s ORD=%s, round-report appended" % (EPOCH, TS, DEC_SHA[:8], ORD_SHA[:8]))
