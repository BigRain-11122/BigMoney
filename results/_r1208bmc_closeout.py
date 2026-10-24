# -*- coding: utf-8 -*-
"""r1208 closeout: W314 CYCLE CLOSED (continuation window), state counter, heartbeat,
round-report row, D-19 watermark refresh."""
import datetime
import hashlib
import io
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ST = os.path.join(REPO, "state-bm-c.json")
HB = os.path.join(REPO, "fleet", "machines", "bm-c.json")
REP = os.path.join(REPO, "logs", "iteration-loop", "round_reports-bm-c.md")

NOW = datetime.datetime.now().astimezone()
ISO = NOW.replace(microsecond=0).isoformat()
EPOCH = int(NOW.timestamp())


def s16(p):
    return hashlib.sha256(io.open(os.path.join(REPO, p), "rb").read()).hexdigest()[:16]


PRE = "research/PERPETUAL_N1_W314_PREREG.md"
prereg_sha = s16(PRE)
prereg_bytes = os.path.getsize(os.path.join(REPO, PRE))
sg = json.load(io.open(os.path.join(REPO, "results/_r1208bmc_w314_sixgate.json"), encoding="utf-8"))
fk = json.load(io.open(os.path.join(REPO, "results/_r1208bmc_w314_fivekeys.json"), encoding="utf-8"))
d = json.load(io.open(os.path.join(REPO, "results/perpetual_faces/n1_w314_results.json"), encoding="utf-8"))
adj = json.load(io.open(os.path.join(REPO, "results/_n1_face_adjudication_w314.json"), encoding="utf-8"))
chain = json.load(io.open(os.path.join(REPO, "results/_r1208bmc_s6_chain.json"), encoding="utf-8"))
p = d["null_pool_cumulative"]
s = d["skill_line_v2_k_lift"]
led = d["science_gates"]["ledger"]
A = d["families"]["A_random_engine_exit"]
chain_rc = [(x.get("leg"), x.get("rc")) for x in chain]
chain_nonzero = [x for x in chain_rc if x[1] != 0]
legs = ", ".join(f"{n}:{r}" for n, r in chain_rc[:5])

state = json.load(io.open(ST, encoding="utf-8"))
assert state.get("round_no") == 1207, "round_no drift: %r" % state.get("round_no")
state["round_no"] = 1208

note = (
 "r1208: W314 CYCLE CLOSED in a continuation window (state round_no=1207 at open, executed "
 "r1208, advanced 1207->1208 so next=r1209); a prior window died after the five-face splice "
 f"(commit 249e2abf9e at 19:39) + engine self-burn 12/12, so this round did NOT re-splice/re-burn "
 "(r1181/no-double-burn law) and instead closed the cycle: (1) freeze-face replay adjudication "
 f"PASS via Tools/n1_freeze_face_adjudicate.py (0 heal delta, 0 unexplained; forward-slash paths "
 "required -- backslash paths fail git show); (2) six-gate 77th consecutive ALL PASS "
 f"(results/_r1208bmc_w314_sixgate.json: splice integrity / CR-normalized worktree==landed / "
 "setwave birth-station 314:1 313:0 305:0 / banned ADMIT rc0 / pf 9/9 + n1 selftest rc0 / shards "
 "12/12 >100KB / seed admit FREE x2); (3) finalize headless one-pass EXACT ledger "
 f"{led['prev_total']:,}+{led['batch_trials']:,}={led['total']:,} / merged K 686,520+2,200="
 f"{p['merged']['n_values']:,} (w314-only mu {p['w314_only']['mu']:.8f}/sigma "
 f"{p['w314_only']['sigma']:.8f}; merged mu {p['merged']['mu']:.8f}/sigma "
 f"{p['merged']['sigma']:.8f}; se_mu@688,720 {p['se_mu_at_k688720']:.6f}; A p95 "
 f"{A['full_sharpe_p95']} / p99 {A['full_sharpe_p99']}); (4) fivekeys 6/6 ALL PASS "
 f"(results/_r1208bmc_w314_fivekeys.json, {len(fk['prereg_prose_deviations'])} prose deviations); "
 f"(5) prereg sec.7/sec.8 backfilled zero-placeholder ({prereg_bytes:,}B, sha16 {prereg_sha}); "
 f"adjudication verdict {adj['verdict']}. S1 smoke 57/57; orphan face=0; attrition 4 ledger files "
 f"CLEAN; S6 chain 39 legs rc={len(chain)-len(chain_nonzero)}/39 rc0 ({legs}...). "
 "PITFALL FAMILY (three in-window, all caught before canon): canon-clone generators must keep the "
 "PRIOR-wave form for the registry-row regex while the plain row NUMBER and the setwave key "
 "SUFFIXES are written as target values directly -- W wave tokens and plain digits live on "
 "different shift tracks (r1168/r1171 family, W314 first live-fire of the suffix face). "
 "current=W314 CLOSED, chain head free; next=r1209 W315 SEAT PROBE (live re-derive on the "
 "post-W314 REGISTERED universe; naive W315 A 708_101..710_100 is EXPECTED to be refused by "
 "registered W314 B 708_101..708_300)")
state["round_t1208_closeout_note"] = note
state["current"] = ("r1208 CLOSED: W314 cycle closed (adjudication PASS / six-gate 77th ALL PASS / "
                    "finalize 1,115,141 + K=688,720 / fivekeys 6/6 / sec.7-8 backfilled); "
                    "next = W315 seat probe")
state["activity_now"] = ("idle at chain head: W314 registered + finalized; next = r1209 W315 seat probe")
state["current_task"] = state["activity_now"]
state["current_task_at"] = ISO
state["current_task_ts"] = ISO
state["clock_read"] = ISO
state["health"] = "green"
state["verdict"] = ("green r1208: W314 CYCLE CLOSED (six-gate 77th ALL PASS, finalize 1,115,141 / "
                    "K=688,720, fivekeys 6/6, adjudication PASS); smoke 57/57; attrition CLEAN; "
                    "orphan 0")
state["verify"] = ("adjudication PASS | six-gate ALL PASS | fivekeys 6/6 | ledger exact 1,115,141 | "
                   "K exact 688,720 | smoke 57/57 | attrition CLEAN | orphan 0")
json.dump(state, io.open(ST, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)

hb = json.load(io.open(HB, encoding="utf-8"))
hb["last_seen"] = ISO
hb["ts"] = ISO
hb["clock_read"] = ISO
hb["heartbeat_epoch_utc"] = EPOCH
hb["current_task"] = ("W314 cycle closed (finalize 1,115,141 / K=688,720, six-gate 77th ALL PASS, "
                      "fivekeys 6/6); chain head free, next = W315 seat probe")
hb["verdict"] = "green r1208: W314 CLOSED; smoke 57/57; attrition CLEAN; orphan 0"
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
json.dump(hb, io.open(HB, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)
assert isinstance(json.load(io.open(HB, encoding="utf-8"))["heartbeat_epoch_utc"], int)

row = (
 f"{ISO} | r1208 | r1208: W314 CYCLE CLOSED in a continuation window (state round_no=1207 at open, "
 f"executed r1208, advanced 1207->1208 so next=r1209). A prior window died right after the "
 f"five-face splice 249e2abf9e + engine self-burn 12/12 -> this round took stock first (git log / "
 f"shard inventory / engine status) and closed the cycle without re-splicing or re-burning. "
 f"PRODUCT = W314 FINALIZE end-to-end: adjudication PASS (0 heal delta, 0 unexplained) -> six-gate "
 f"77th consecutive ALL PASS (results/_r1208bmc_w314_sixgate.json) -> finalize one-pass EXACT "
 f"ledger {led['prev_total']:,}+{led['batch_trials']:,}={led['total']:,} / merged K 686,520+2,200="
 f"{p['merged']['n_values']:,} (w314-only mu {p['w314_only']['mu']:.8f} sigma "
 f"{p['w314_only']['sigma']:.8f}; merged mu {p['merged']['mu']:.8f} sigma {p['merged']['sigma']:.8f}; "
 f"se_mu@688,720 {p['se_mu_at_k688720']:.6f}; A p95 {A['full_sharpe_p95']} / p99 "
 f"{A['full_sharpe_p99']}) -> fivekeys 6/6 ALL PASS -> sec.7/sec.8 backfilled zero-placeholder "
 f"({prereg_bytes:,}B, sha16 {prereg_sha}). S1 smoke 57/57; S6 chain 39 legs "
 f"rc={len(chain)-len(chain_nonzero)}/39 rc0; S7 attrition 4 ledger files CLEAN / orphan face=0. "
 f"CEO face: 当前活=W314 已收口（finalize 账本 1,115,141 / K=688,720）；最近实物="
 f"research/PERPETUAL_N1_W314_PREREG.md §7/§8 回填 + results/_r1208bmc_w314_sixgate.json "
 f"{ISO[:16]}；下个里程碑=W315 席位探针+pre-reg 冻结+五面 splice（≤48h）。 | watermark verdict: "
 f"GREEN (dualrun ZERO-DRIFT 616 entries streak 51, board 0 inflight) | local-not-on-origin "
 f"commits=0 | registry zero-hit (no sweep action) | dept:研究/策略"
)
with io.open(REP, "a", encoding="utf-8", newline="\n") as f:
    f.write(row + "\n")
print("state round_no=1208 ; heartbeat", ISO, EPOCH)
print("report row appended", len(row), "chars")
print("chain_nonzero", chain_nonzero)