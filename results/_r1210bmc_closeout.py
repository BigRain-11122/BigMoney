# -*- coding: utf-8 -*-
"""r1210 closeout: W315 CYCLE CLOSED, state counter, heartbeat, round-report row,
5x HANDOVER roll-up (round_no 1210 is a 5-multiple)."""
import datetime
import hashlib
import io
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ST = os.path.join(REPO, "state-bm-c.json")
HB = os.path.join(REPO, "fleet", "machines", "bm-c.json")
REP = os.path.join(REPO, "logs", "iteration-loop", "round_reports-bm-c.md")
HO = os.path.join(REPO, "research", "HANDOVER.md")

NOW = datetime.datetime.now().astimezone()
ISO = NOW.replace(microsecond=0).isoformat()
EPOCH = int(NOW.timestamp())


def s16(p):
    return hashlib.sha256(io.open(os.path.join(REPO, p), "rb").read()).hexdigest()[:16]


PRE = "research/PERPETUAL_N1_W315_PREREG.md"
prereg_sha = s16(PRE)
prereg_bytes = os.path.getsize(os.path.join(REPO, PRE))
sg = json.load(io.open(os.path.join(REPO, "results/_r1210bmc_w315_sixgate.json"), encoding="utf-8"))
fk = json.load(io.open(os.path.join(REPO, "results/_r1210bmc_w315_fivekeys.json"), encoding="utf-8"))
d = json.load(io.open(os.path.join(REPO, "results/perpetual_faces/n1_w315_results.json"), encoding="utf-8"))
adj = json.load(io.open(os.path.join(REPO, "results/_n1_face_adjudication_w315.json"), encoding="utf-8"))
seat = json.load(io.open(os.path.join(REPO, "results/_w316bmc_20261024_probe_receipt.json"), encoding="utf-8"))
chain = json.load(io.open(os.path.join(REPO, "results/_r1210bmc_s6_chain.json"), encoding="utf-8"))
p = d["null_pool_cumulative"]
s = d["skill_line_v2_k_lift"]
led = d["science_gates"]["ledger"]
A = d["families"]["A_random_engine_exit"]
chain_rc = [(x.get("leg"), x.get("rc")) for x in chain]
chain_nonzero = [x for x in chain_rc if x[1] != 0]
legs = ", ".join(f"{n}:{r}" for n, r in chain_rc[:5])
wA, wB = seat["bands"]["A"], seat["bands"]["B"]

state = json.load(io.open(ST, encoding="utf-8"))
prev_round_no = state.get("round_no")
state["round_no"] = 1210
state["last_round"] = 1210
state["r1210_absorb_note"] = (
 "r1210 absorb note: the dead r1209 window landed W315 end-to-end (seat ADMIT eebc599c33 / prereg "
 "freeze 7f5421ec6f / five-face splice 9152093267 / engine self-burn 12/12 batched appends "
 "025900cde6+3becf4aa74) but died before six-gate/finalize/backfill/seat/closeout and before it "
 "advanced state (round_no stayed 1208). This window took stock first (git log + shard inventory + "
 "engine status: wave_shards_done['315']=12, burns_active=[]), then closed the cycle WITHOUT "
 "re-splicing or re-burning (r1181 no-double-burn law) and executed as r1210 (next after the "
 "highest committed label r1209), advancing {prev}->1210 so next=r1211; zero double-count: the "
 "dead window's body debts were handled by its own commits, S0.5 dual watermark both current "
 "(dec content unchanged, orders unacked=0), and the S6 chain it launched at 20:55 finished "
 "39/39 rc0 at 21:05 into this window (receipt renamed from the launcher's broken "
 "'_r--roundbmc_s6_chain.json' template face to _r1210bmc_s6_chain.json)")
state["current"] = ("r1210 CLOSED: W315 cycle closed (adjudication PASS / six-gate 78th ALL PASS / "
                    "finalize 1,117,341 + K=690,920 / fivekeys 6/6 / sec.7-8 backfilled / W316 seat "
                    "ADMIT published); next = W316 prereg freeze + five-face splice")
state["activity_now"] = ("idle at chain head: W315 registered + finalized; W316 seat published; "
                         "next = r1211 W316 prereg freeze + splice")
state["current_task"] = state["activity_now"]
state["current_task_at"] = ISO
state["current_task_ts"] = ISO
state["clock_read"] = ISO
state["health"] = "green"
state["verdict"] = ("green r1210: W315 CYCLE CLOSED (six-gate 78th ALL PASS, finalize 1,117,341 / "
                    "K=690,920, fivekeys 6/6, adjudication PASS); W316 seat ADMIT; smoke 57/57; "
                    "attrition CLEAN; orphan 0")
state["verify"] = ("adjudication PASS | six-gate ALL PASS | fivekeys 6/6 (1 disclosed prose dev) | "
                   "ledger exact 1,117,341 | K exact 690,920 | smoke 57/57 | attrition CLEAN | "
                   "orphan 0 | S6 39/39 rc0")
json.dump(state, io.open(ST, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)

hb = json.load(io.open(HB, encoding="utf-8"))
hb["last_seen"] = ISO
hb["ts"] = ISO
hb["clock_read"] = ISO
hb["heartbeat_epoch_utc"] = EPOCH
hb["machine_id"] = "bm-c"
hb["round"] = 1210
hb["round_no"] = 1210
hb["current_task"] = ("W315 cycle closed (finalize 1,117,341 / K=690,920, six-gate 78th ALL PASS, "
                      "fivekeys 6/6); W316 seat ADMIT published, next = W316 freeze + splice")
hb["current"] = hb["current_task"]
hb["verdict"] = "green r1210: W315 CLOSED; W316 seat ADMIT; smoke 57/57; attrition CLEAN; orphan 0"
hb["verify"] = ("sixgate ALL PASS | fivekeys 6/6 | ledger 1,117,341 | K 690,920 | smoke 57/57 | "
                "attrition CLEAN | orphan 0 | S6 39/39")
hb["recent_artifact"] = "results/perpetual_faces/n1_w315_results.json"
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
json.dump(hb, io.open(HB, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)
assert isinstance(json.load(io.open(HB, encoding="utf-8"))["heartbeat_epoch_utc"], int)

row = (
 f"{ISO} | r1210 | W315 CYCLE CLOSED IN A CONTINUATION WINDOW. The dead r1209 window had already "
 f"landed seat ADMIT (eebc599c33), prereg freeze (7f5421ec6f), five-face splice (9152093267, 173 "
 f"parity rows) and the engine self-burn 12/12 (batched ledger appends 025900cde6 + 3becf4aa74) "
 f"but never ran the closure chain and never advanced state (round_no frozen at 1208) -> this round "
 f"took stock first (git log / results/p2cal_ext/n1_w315 12 shards / engine wave_shards_done[315]=12) "
 f"and closed the cycle with ZERO re-splice and ZERO re-burn. PRODUCT = W315 FINALIZE end-to-end: "
 f"freeze-face adjudication PASS (written this window because the dead window left no side-file: "
 f"parent-CRLF == receipt pre, landed-CRLF == receipt post, worktree raw == receipt post and "
 f"worktree LF == landed LF, 0 heal delta, 0 unexplained) -> six-gate 78th consecutive ALL PASS "
 f"(results/_r1210bmc_w315_sixgate.json) -> finalize one-pass EXACT ledger "
 f"{led['prev_total']:,}+{led['batch_trials']:,}={led['total']:,} / merged K 688,720+2,200="
 f"{p['merged']['n_values']:,} (w315-only mu {p['w315_only']['mu']:.8f} sigma "
 f"{p['w315_only']['sigma']:.8f}; merged mu {p['merged']['mu']:.8f} sigma {p['merged']['sigma']:.8f}; "
 f"se_mu@690,920 {p['se_mu_at_k690920']:.6f}; A p95 {A['full_sharpe_p95']} / p99 "
 f"{A['full_sharpe_p99']}) -> fivekeys 6/6 ALL PASS (1 disclosed prose deviation: sec.5 key4 froze "
 f"'+0.0000' on the W314 anchor while this wave moved to +0.0001; disclosed, not smoothed) -> "
 f"sec.7/sec.8 backfilled zero-placeholder ({prereg_bytes:,}B, sha16 {prereg_sha}) -> W316 seat "
 f"ADMIT published live on the post-W315 universe (A {wA[0]:,}..{wA[1]:,} = 69th consecutive A-hop / "
 f"B {wB[0]:,}..{wB[1]:,} = 70th above-own-A; FREE x2; fleet/inbox/MSG-20261024-2115-bmc-w316-seat.md). "
 f"S1 smoke 57/57; S6 chain 39/39 rc0 (launched by the dead window at 20:55, finished 21:05 into "
 f"this window; {legs}...); S7 attrition 4 ledger files CLEAN / orphan face=0; round-zero orphan "
 f"probe py_faces=6 orphans=0. PIT (three, all caught before canon): canon-clone generators break "
 f"when the same literal is BOTH explicitly rewritten and inside the wave-token cascade "
 f"(PREV = 314 / the lineage filename) -- park final values behind pure-letter sentinels; explicit "
 f"replacement ORDER eats literals ('77th'->'78th' first kills the long lineage match); and sec.7/8 "
 f"template text carries the PRIOR wave's numbers, so backfill must machine-read every value while "
 f"declaring the prior anchor explicitly. | CEO face: 当前活=W315 已闭环（finalize 账本 1,117,341 / "
 f"K=690,920），W316 席位已 ADMIT；最近实物=research/PERPETUAL_N1_W315_PREREG.md §7/§8 回填 + "
 f"results/perpetual_faces/n1_w315_results.json {ISO[:16]}；下个里程碑=W316 prereg 冻结+五面 splice"
 f"（≤48h）。 | watermark verdict: GREEN (dualrun ZERO-DRIFT 616 entries streak 51, board 0 "
 f"inflight, no red gate) | local-not-on-origin commits=0 (post-push self-proof) | registry "
 f"zero-hit (no sweep action) | dept:研究/策略"
)
with io.open(REP, "a", encoding="utf-8", newline="\n") as f:
    f.write(row + "\n")

ho_row = (
 f"> bm-c round 1210 五倍轮对账（{ISO}·覆盖 r1206-r1210 十字）·权威明细=round_reports-bm-c.md 全量在册。"
 f"本段=bm-c 面：**PERPETUAL-N1 W312→W315 四波全周期闭环 + D-19 三元组水位落地 + canon-clone 生成器"
 f"三家族坑律成形**。r1206=W313 收口（six-gate 76th ALL PASS·finalize 1,112,941/K=686,520·fivekeys 6/6）"
 f"+ D-20261024-03 三元组 D-19 水位接进 Tools/d19_check.py；r1207=W314 席位 ADMIT（A 706_101..708_100 "
 f"67th / B 708_101..708_300 68th）+ prereg 冻结 5172b1f636；r1208=W314 收口（five-face splice "
 f"249e2abf9e + 引擎自燃 12/12 + adjudication PASS + six-gate 77th + finalize 1,115,141/K=688,720 + "
 f"sec.7/8 回填）+ W314 席位 MSG；r1209=W315 全链（席位 eebc599c33 / prereg 7f5421ec6f / splice "
 f"9152093267·173 parity rows / 引擎自燃 12/12），窗死于 finalize 前；r1210=W315 收口（补写 adjudication "
 f"PASS + six-gate 78th ALL PASS + finalize 1,117,341/K=690,920 + fivekeys 6/6 含 1 条如实披露 + "
 f"sec.7/8 回填 + W316 席位 ADMIT A {wA[0]:,}..{wA[1]:,} 69th / B {wB[0]:,}..{wB[1]:,} 70th）+ S6 "
 f"39/39 rc0 + HANDOVER 本行。产物清单漂移=results/perpetual_faces/n1_w31{{2,3,4,5}}_results.json + "
 f"results/p2cal_ext/n1_w31{{2,3,4,5}}/ 各 12 分片 + research/PERPETUAL_N1_W31{{2,3,4,5}}_PREREG.md + "
 f"results/_n1_face_adjudication_w31{{4,5}}.json + fleet/inbox/MSG-20261024-*-bmc-w31{{4,5,6}}-seat.md + "
 f"results/_r1206/-r1207/-r1208/-r1210bmc_* 工具族。维护面：smoke 57/57 恒绿；attrition 4 账本 CLEAN；孤儿面=0；"
 f"D-19 水位双双当前（orders unacked=0）；S6 每窗 39/39 rc0。下个 5x 指针=bm-c r1215。"
)
with io.open(HO, "a", encoding="utf-8", newline="\n") as f:
    f.write(ho_row + "\n")

print("state round_no=1210 (was", prev_round_no, ") ; heartbeat", ISO, EPOCH)
print("report row", len(row), "chars ; handover row", len(ho_row), "chars")
print("chain_nonzero", chain_nonzero)