# -*- coding: utf-8 -*-
# r710 bm-c close driver: round-report append + state bump 710->711 + heartbeat
# nine-field refresh + watermark keys facts-driven (DEC/ORD both UNCHANGED this
# round: EE659451 / 17accc40, zero delta, zero action) + self-asserts (epoch
# int, clock_read T-sep, round math, unacked==0). JSON surgery only through
# this script. Pattern credit: results/_r709bmc_close.py (bloodline copy).
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

# S0.5 facts: double-sweep identity (both sweeps derived EE659451/17accc40, zero delta)
facts = json.load(io.open(os.path.join(ROOT, "results", "_r710bmc_s05_facts.json"), encoding="utf-8-sig"))
DEC_SHA, ORD_SHA = facts["dec_sha"], facts["ord_sha"]
assert facts["dec_changed"] is False and facts["ord_changed"] is False, "watermark moved between sweeps"
assert facts["unacked"] == [], "unacked != 0"
assert facts["orders_disk_count"] > 0, "disk-side non-empty self-check (r669)"
assert len(DEC_SHA) == 64 and len(ORD_SHA) == 40, "hash shapes"
assert DEC_SHA == "EE6594516C01856ECD1BD4131E49CAFD8F95A61293C131CE5D45C574C20FF6CE", "dec sha drift"
assert ORD_SHA == "17ACCC40ED2039561038BC46B63359E71587D51A", "ord sha drift"

RR = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
line = (TS + " | r710 | dept:工程/舰队（金周复市 T-0 晨间值守轮·第 30 bm-c 连守轮·5x HANDOVER 补报轮） | "
  "水位绿（red=false·lane healthy·next_pick=claimed moneyflow IC 源阻断 bm-a 车道合法·py_low_board_clear=合法 idle 白名单〔板 0 open/176 ack/bandit claimed/金周无 bar〕） | "
  "当前活: r710 S0 carry 手术轮——r709 三连（368b7b1c1/0163a0048/f0b0c5a88）自 machine/bm-c-r709 分支 S0-carry 达 main："
  "rebase 21-UU 双停窗正典解（stop1=orphan probe 取 stage3 链条连续性侧〔r710 churn 00:35:09 最新面随后重放覆盖〕；"
  "stop2=r709 closeout 16 面冲突=r848 bm-a 血统 resolver 收据 _r710bmc_rebase_resolve.json——REPORT/LIVE 孪生四对整侧取新 x8+compute_audit history union 201+201→202 零丢失+token_usage per-key max+regime_state base=新者+历史 asof-union+状态面 newer-wins x5+daemon 活面 live-wins x2；"
  "另 r659/r808 三步治愈 x2 停窗〔dumb-terminal continue 拒进=author-script env 注入+commit -F message〕）+DELIVERED 5b3877a02..a4bda3d8d ahead=0/behind=0 送达自证；"
  "5x=HANDOVER r615..r705 OVERDUE-BACKLOG 单窗补报行落盘（窗 r611-r710·链头 live-read 799,705=W179〔bm-a r850〕·bm-c 窗内自有 W14-SCREEN +493+W14-JUDGE +77） "
  "| smoke 48/48 · S6 38/38 rc0（dualrun ZERO-DRIFT streak 30@406 条） · QA 5/5（determinism=True 31st·93 trades·equity 1,017,839 冻结恒等·png 66,194B） · "
  "orders 双扫零差（176 ack·UNACKED=0）·DEC/ORD 双扫同哈希零 delta（EE659451/17accc40·零动作） · post_review 45Y/0N/5WAIT 零红 · 孤儿面=1（ComfyUI idle server·CEO 私产·只读披露不击杀） · "
  "idle NOT-GREEN（常驻负载·idle_rounds=0·--worked 产出工申报） · attrition CLEAN · 自愈=loop pin=5 no-op+watchdog 在位+双爪 LF 归一装好 · 本地未达 origin commit 数=0（commit 后 push 自证） "
  "| 下轮 r711：值守续（10-08 复市首交易日=今日·盘前零动作）；今晚盘后面=数据链全门 re-arm+REGIME_GUARD v3 新 bar enforce+fund_premium 15:30 首采（bm-c 车道）+QDII watch 重跑=长假脱锚当日差分（DIGEST-20261008 主题一活验证窗）+CTA_P1 纸面接线（O-2215-2 GM 签署·有 bar 才接禁盲接）；O-2245 待工单；cloudF 聚合行窗 10-14；next 5x=r715 HANDOVER\n")
with io.open(RR, "a", encoding="utf-8") as f:
    f.write(line)

DID = ("r710 bm-c: S0 carry-surgery + 5x HANDOVER backfill watch round (30th consecutive bm-c watch round). "
  "(1) S0: r709 trio (churn/closeout/addendum) carried from machine/bm-c-r709 branch onto origin/main via pull --rebase with two "
  "canonical conflict stops: stop-1 orphan probe resolved stage3 (chain-continuity side; r710 churn 00:35:09 newest face replays last), "
  "stop-2 16-face window resolved per r848 bm-a bloodline resolver (receipt _r710bmc_rebase_resolve.json: REPORT/LIVE twins whole-side "
  "take-newer x8 by generated ts with format-normalized compare, compute_audit history (ts,machine) union 201+201->202 zero-loss, "
  "token_usage per-key max, regime_state base=newer+asof-union, status faces newer-ts x5, daemon live faces live-wins x2) + two "
  "dumb-terminal continue refusals cured per r659/r808 three-step (author-script env inject + commit -F message). DELIVERED "
  "5b3877a02..a4bda3d8d, ahead=0/behind=0. (2) 5x HANDOVER: r615..r705 stamps OVERDUE-BACKLOG single-window backfill row filed "
  "(window r611-r710; ledger live-read 799,705 = PERPETUAL-N1-W179 per bm-a r850; bm-c-owned window adds = W14-SCREEN +493 + "
  "W14-JUDGE +77; main lines = golden-week watch era + D-06 CODELY main-file campaign + dead-session adoption chains + push-race "
  "resolver era + W14-JUDGE full arc + lane_io third-signal fix + O-2245 OSS faces + EngineTick idle-trigger deployment + QDII "
  "holiday-premium watch + D-20261007-07 consumption). (3) S0.5 double-sweep: DEC/ORD both unchanged (EE659451/17accc40), unacked=0 "
  "(176 ack). (4) S1 smoke 48/48. (5) S6 38/38 rc0 (dualrun ZERO-DRIFT streak 30). (6) QA 5/5 31st (determinism=True, 93 trades, "
  "equity 1,017,839 frozen identity, png 66,194B). (7) post_review 45Y/0N/5WAIT zero red. (8) orphan face=1 ComfyUI idle server "
  "(CEO-owned, no-kill documented). (9) idle NOT-GREEN (resident load) idle_rounds=0, --worked declared. (10) S7 self-heal: loop "
  "pin=5 no-op + watchdog registered + both claws LF-normalized installed + attrition guard CLEAN.")

VERDICT = ("r710 bm-c: S0 carry surgery + 5x HANDOVER backfill round clean. Product = r709 trio delivered to origin/main (21-UU "
  "two-stop canonical resolve, receipt _r710bmc_rebase_resolve.json) + HANDOVER r615..r705 overdue-backfill window row (ledger "
  "live-read 799,705); D-19 both watermarks unchanged zero action; S6 38/38 rc0 streak 30; QA 5/5 det 31st; smoke 48/48; orders "
  "double-sweep zero-delta unacked=0; post_review zero red; orphan face=1 no-kill; idle not green-idle, idle_rounds=0 worked-declared.")

NEXT = ("r711: (a) watch continuation (10-08 reopen first trading day, pre-open zero action); (b) evening post-close face: data-chain "
  "full re-arm + REGIME_GUARD v3 first-new-bar enforce + fund_premium 15:30 first snapshot (bm-c lane) + QDII premium watch rerun = "
  "holiday-decoupling same-day delta (DIGEST-20261008 theme-1 live-verification window) + CTA_P1 paper wiring (O-2215-2, GM-signed, "
  "no-bar blind wiring forbidden); (c) O-2245 follow-ups upon ticket; (d) cloudF aggregation row window 10-14 (D-20261007-06 named "
  "@BigCompute/bm-c one row); (e) next 5x = r715 HANDOVER. [via bm-c r710]")

ART = ("research/HANDOVER.md r710 5x backfill row (window r611-r710, ledger live-read 799,705) + results/_r710bmc_rebase_resolve.json "
  "(16-face canonical resolve receipt) + qa/smoke-r710.md 5/5 + qa/equity-curve-r710.png 66,194B (determinism=True 31st, 93 trades, "
  "equity 1,017,839 frozen identity) + results/_r710bmc_s6_log.txt (38 legs rc0, dualrun streak 30) + results/_r710bmc_s05_facts.json "
  "(double-sweep identical, DEC EE659451 / ORD 17accc40 both unchanged, unacked=0) + results/_r710bmc_s6_chain.py + Tools/_r710bmc_qa_ignite.py")

CUR = ("当前活: r710 bm-c S0 carry 手术+5x HANDOVER 补报轮收口（r709 三连达 main·21-UU 双停窗正典解·HANDOVER r615-r705 逾期窗单窗补报） "
  "| 最近实物: research/HANDOVER.md r710 5x 行（链头 live-read 799,705·bm-c 窗内 W14 双面 +570）+results/_r710bmc_rebase_resolve.json（16 面收据）"
  "+qa/smoke-r710.md 5/5（determinism 31st·equity 1,017,839 冻结恒等）@ " + TS +
  " | 下个里程碑: 10-08 复市首交易日（今晚盘后：数据链 re-arm+REGIME v3 enforce+fund_premium 15:30 首采+QDII watch 重跑出长假溢价差分+CTA_P1 接线有 bar 才接）；next 5x=r715 HANDOVER")

HP = os.path.join(ROOT, "state-bm-c.json")
st = json.load(io.open(HP, encoding="utf-8-sig"))
assert st["round_no"] == 710, "round_no anchor mismatch: %s" % st["round_no"]
st.update({
  "round_no": 711, "round_no_label": "round 710 (bm-c)",
  "last_round": 710, "last_round_at": TS, "last_round_ts": TS,
  "last_seen": TS, "last_seen_at": TS, "last_ts": TS, "last_run_at": TS,
  "current_task_at": TS, "updated": TS, "updated_at": TS, "ts": TS,
  "clock_read": TS, "heartbeat_epoch_utc": EPOCH,
  "cpu_pct": CPU, "cpu_idle_pct": round(100 - CPU, 1),
  "free_ram_gb": RAMF, "idle_ram_gb": RAMF, "ram_free_gb": RAMF,
  "gpu_free_vram_mib": VRAM, "gpu_free_vram_mb": VRAM, "gpu_free_mib": VRAM,
  "did": DID, "verdict": VERDICT, "note": "r710: S0 carry surgery delivered r709 trio to main (21-UU canonical resolve); 5x HANDOVER r615-r705 overdue window backfilled; both watermarks unchanged.",
  "current_task": CUR, "activity_now": VERDICT,
  "last_round_summary": "r710: r709 trio carried to main (21-UU canonical resolve, receipt filed), HANDOVER 5x backfill row landed, S6 38 rc0 streak 30, QA 5/5 det-31st, smoke 48/48, delivery verified.",
  "last_action": "r710: r709 trio carried to main (21-UU canonical resolve, receipt filed), HANDOVER 5x backfill row landed, S6 38 rc0 streak 30, QA 5/5 det-31st, smoke 48/48, delivery verified.",
  "next_pointer": NEXT, "verify": ART,
  "last_decisions_read_at": TS,
  "last_decisions_sha": DEC_SHA,
  "last_decisions_sha_method": "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r710 both sweeps = UNCHANGED EE659451 zero delta zero action; facts-driven from results/_r710bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law))",
  "last_orders_sha": ORD_SHA,
  "last_orders_sha_method": "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r710 both sweeps = UNCHANGED 17accc40, zero delta; facts-driven from results/_r710bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law))",
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
  "round_no": 710, "round_no_label": "round 710 (bm-c)",
  "last_round": 710, "last_round_at": TS,
  "current_task": CUR, "current_task_at": TS,
  "latest_artifact": ART,
  "next_milestone": "10-08 reopen first trading day (evening post-close): data-chain re-arm + REGIME_GUARD v3 first-bar enforce + fund_premium 15:30 first snapshot (bm-c lane) + QDII watch rerun = holiday-decoupling delta (DIGEST-20261008 theme-1) + CTA_P1 paper wiring (O-2215-2, no-bar blind wiring forbidden); O-2245 upon ticket; cloudF window 10-14; next 5x = r715 HANDOVER",
  "health": "alive (r710 S0 carry surgery + 5x HANDOVER backfill round clean: loop pin=5, watchdog registered, SAT alive rc0, QA 5/5 determinism 31st, smoke 48/48, S6 38/38 rc0 dualrun streak 30, orders double-sweep zero-delta unacked=0, DEC/ORD both unchanged EE659451/17accc40, post_review zero red, orphan face=1 ComfyUI no-kill documented, idle NOT-GREEN resident load idle_rounds=0 worked-declared, DELIVERY: r709 trio landed main 5b3877a02..a4bda3d8d ahead=0)",
  "activity_now": VERDICT, "did": DID, "verdict": VERDICT,
  "note": "r710: S0 carry surgery (r709 trio to main, 21-UU canonical resolve) + HANDOVER r615-r705 overdue window backfilled; both watermarks unchanged.",
  "last_round_summary": "r710: r709 trio carried to main (21-UU canonical resolve, receipt filed), HANDOVER 5x backfill row landed, S6 38 rc0 streak 30, QA 5/5 det-31st, smoke 48/48, delivery verified.",
  "last_action": "r710: r709 trio carried to main (21-UU canonical resolve, receipt filed), HANDOVER 5x backfill row landed, S6 38 rc0 streak 30, QA 5/5 det-31st, smoke 48/48, delivery verified.",
  "next": NEXT,
  "last_seen_at": TS, "updated_at": TS, "updated": TS, "last_run_at": TS, "last_ts": TS,
})
json.dump(hb, io.open(HB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# self-asserts (smoke F7 face: epoch int + clock_read T-sep)
chk = json.load(io.open(HB, encoding="utf-8-sig"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in chk["clock_read"] and " " not in chk["clock_read"], "clock_read not T-sep"
st2 = json.load(io.open(HP, encoding="utf-8-sig"))
assert st2["round_no"] == 711, "state round_no not advanced"
assert st2["last_decisions_sha"] == DEC_SHA and st2["last_orders_sha"] == ORD_SHA, "watermark keys not facts-driven"
print("close ok: state 710->711, heartbeat epoch=%d int-verified, clock=%s, DEC=%s ORD=%s, round-report appended" % (EPOCH, TS, DEC_SHA[:8], ORD_SHA[:8]))
