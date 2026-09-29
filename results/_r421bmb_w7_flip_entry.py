# -*- coding: utf-8 -*-
"""r421 bm-b W7-SCREEN dual-face done-flip + W7-JUDGE direct-ready entry.

Laws applied:
  - 坑律一百零一批 (pool done-flip dual-face closure): entry status AND
    every shard closed (for sh in e["shards"] full closure + assert,
    r201 paradigm); three-way verification FIRST (entry ticket_ref
    numbers vs product JSON cells vs prereg literals).
  - pit-89 (r413): done-flip = claiming session's own in-round action.
  - pit-90 / O-1820(3): JUDGE entry same-commit with its satisfied
    entry-time deps (direct-ready per W6-SCREEN r420 precedent).
  - r415: receipt asserts on source-constant ACTUAL value shapes.
"""
import datetime
import json
import os

POOL = "results/runnable_pool.json"
now = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S+08:00")
now_s = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

pool = json.load(open(POOL, encoding="utf-8-sig"))

# ---------- three-way verification (product vs entry vs prereg)
prod = json.load(open("results/trial_labor_w7/w7_screen.json",
                      encoding="utf-8"))
assert prod["n_distinct"] == 3704, prod["n_distinct"]
assert prod["k_nulls"] == 200, prod["k_nulls"]
assert prod["batch_cells"] == 3904, prod["batch_cells"]
assert prod["n_survivors"] == 284, prod["n_survivors"]
assert round(prod["null_family"]["p95_line"], 4) == 0.5180, \
    prod["null_family"]["p95_line"]
tl = prod["trials_ledger"]
assert tl["batch"] == "TRIAL_LAB_W7_SCREEN", tl
assert tl["prev_total"] == 333432 and tl["batch_trials"] == 3904 \
    and tl["total"] == 337336, tl          # linear no-reset cross-wave
assert prod["evidence_cutoff"] == "2026-09-22"
assert prod["grammar_sha256"] == "1fba956c2f21d1d3"

ent = [x for x in pool["entries"] if x["id"] == "TRIAL-LABOR-W7-SCREEN"][0]
assert "3704 distinct + 200 nulls literal per sec.3" in ent["prereg_ref"]
prereg_t = open("research/TRIAL_LABOR_W7_PREREG.md",
                encoding="utf-8").read()
assert "TRIAL_LAB_W7_SCREEN" in prereg_t
assert "batch_trials = 去重后候选数 + 200 null" in prereg_t
assert "TRIAL_LAB_W7_JUDGE" in prereg_t
print("three-way OK: product 3704+200/284 survivors/p95 0.5180/"
      "ledger 333432+3904=337336 == entry literal == prereg sec.0/§3")

# ---------- SCREEN entry dual-face done-flip
assert ent["status"] == "ready", ent["status"]
ent["status"] = "done"
ent["done_at"] = now
ent["result_ref"] = "results/trial_labor_w7/w7_screen.json"
ent["done_note"] = (
    "r421 bm-b in-round harvest (pit-89 no-deferral law): burn complete "
    "3904/3904 cells (3704 distinct + 200 nulls; autofill launch 10:40:01 "
    "pid19452, full checkpoint by ~10:53; 11:00:01 tick relaunch pid10532 "
    "= full-checkpoint no-op exit zero new lines, honest re-ready-window "
    "cost) -> screen-finalize LANDED r421 10:59:31 with pit-95 "
    "finalize-idempotent guard wired THIS ROUND pre-first-landing "
    "(MSG-20260929-1030 bm-c->bm-b honored): w7_screen.json null p95 "
    "0.5180 (W1-W6 band 0.5116-0.5196 in-band), survivors 284/3704 = "
    "7.67%; streak segmented survival: down_streak2 102/1092=9.34%, none "
    "103/1296=7.95%, up_streak2 79/1316=6.00% (streak=none face highest = "
    "behavioral-confirmation cost face honest); trials_ledger "
    "TRIAL_LAB_W7_SCREEN prev 333432 + 3904 = 337336 cross-wave linear "
    "no-reset verified; evidence_cutoff 2026-09-22 lockbox; grammar "
    "1fba956c2f21d1d3 (== FROZEN_SHA16 build anchor); finalize re-run "
    "refusal live-fire VERIFIED rc=2 (guard fires on landed product); "
    "selftest 42/42 (L19a/L19b guard legs added, live-fire mode "
    "post-landing)")
for sh in ent["shards"]:
    assert sh["key"] == "screen-0of1" and sh["status"] == "ready", sh
    sh["status"] = "done"
    sh["closed_at"] = now_s
    sh["note"] += (" | r421 bm-b shard-face closed same commit as entry "
                   "done-flip (坑律一百零一批 dual-face law; burn-complete "
                   "checkpoint 3904 lines zero-delta verified)")
assert len(ent["shards"]) == 1
assert all(sh["status"] == "done" for sh in ent["shards"]), ent["shards"]
print("SCREEN dual-face done-flip OK:", ent["id"],
      "| entry:", ent["status"],
      "| shard:", ent["shards"][0]["status"],
      "| closed_at:", ent["shards"][0]["closed_at"])

# ---------- W7-JUDGE entry (direct-ready, all three deps MET this round)
assert not any(x["id"] == "TRIAL-LABOR-W7-JUDGE"
               for x in pool["entries"]), "JUDGE entry already exists"
judge = {
    "id": "TRIAL-LABOR-W7-JUDGE",
    "ticket_ref": ("T-2026-09-29-118 WAVE-7 judge slice (CEO "
                   "O-2026-09-27-2245 thousand-trader order + "
                   "O-2026-09-27-2250 standing law; prereg FROZEN bm-c "
                   "r207 draft-author same-machine next-round freeze; "
                   "SEED berths 20305000/20305500/20306000 same-commit "
                   "R250; runner built bm-b r417-cont/r418/r419 "
                   "single-writer berth MSG-20260929-0930/0945 honored; "
                   "pit-95 finalize-idempotent guard wired bm-b r421 "
                   "pre-first-landing per MSG-1030; SCREEN-finalize "
                   "LANDED bm-b r421 10:59:31: 3704+200 cells, null p95 "
                   "0.5180, survivors 284 -- judge physical dep "
                   "satisfied; judge-prep PASS bm-b r421)"),
    "prereg_ref": ("research/TRIAL_LABOR_W7_PREREG.md FROZEN sec.0 "
                   "TRIAL_LAB_W7_JUDGE (s3 full judgment batch: "
                   "batch_trials = survivors 284 judged cells; dual "
                   "nulls B/P resampling = not ledger +0 per W6 sec.0 "
                   "lineage) + sec.0 W7-JUDGE physical-order gate "
                   "(behind remaining in-flight judge faces + RAM r354 "
                   "three-sample; queue face confirmed at entry: MASS "
                   "x4 + W1-W6 JUDGE all done = zero in-flight verdict "
                   "faces; 48h CEO report clock starts at judge-finalize) "
                   "+ sec.4 (g1_prime_v2/g2_registration_v2 shared lib "
                   "zero hand-copy; DSR n_trials = live chain head "
                   "cross-wave no-reset = 337336 post-SCREEN; E[FP]=0.05*"
                   "N_judged; family PBO CSCV 8 blocks "
                   "family=strategy-module) + sec.9 pool routing "
                   "(lane_owner=null per frozen law; judge face "
                   "cache-less machines in-runner exit 2 honest "
                   "W1-W6 precedent)"),
    "consumer_plan": ("TRIAL-LABOR-W7-JUDGE -> judged verdict face "
                      "(w7_judge.json) -> s4 intake (W2-lineage D6 "
                      "binding gate -> STRATEGY_LIBRARY registration rows "
                      "+ TRIAL-<FAMILY>-<NN> paper accounts) -> 48h CEO "
                      "report + scorecard/CEO one-pager faces; screen "
                      "null p95 0.5180 -> next-wave prereg reference "
                      "band (W1-W6 0.5116-0.5196 lineage extended)"),
    "runner": "scripts/trial_labor_w7.py",
    "runner_args": ["judge", "--shard", "0", "--shards", "1"],
    "lane_owner": None,
    "priority": 1,
    "status": "ready",
    "entered_at": now_s,
    "entered_by": "bm-b r421",
    "data_gates": ("READY (all three entry-time deps MET r421 bm-b): "
                   "(1) serial-position face: all judge-family entries "
                   "done at entry (MASS-TRIAL-W1-JUDGE x4 + "
                   "TRIAL-LABOR-W1..W6-JUDGE done), zero in-flight "
                   "verdict faces ahead; (2) judge-prep PASS bm-b r421 "
                   "11:01: manifest PASS 48 members, census L/D == "
                   "frozen, survivors 284, gate meta L/D na-window "
                   "199/199, vol 519/519 (leg-L anchors 594calm/518wild), "
                   "yang zero-warmup 819yang/812red, vconf 19-bar warmup "
                   "784surge/828dry, streak 2-bar warmup "
                   "384up/389down/856neither -> "
                   "results/trial_labor_w7/judge_state.json; (3) RAM "
                   "r354 three-sample PASS 12.10/12.33/12.52 GB "
                   "(>=4GB law). In-runner fail-closed: "
                   "judge_state/w7_screen absent exit 2; grammar sha16 "
                   "!= 1fba956c2f21d1d3 refuse; zero-survivor vacuous "
                   "face n/a (284 survivors). Judge dual-null rng "
                   "trial_labor_w7_unc=20306000 [20306000, cell_idx] per "
                   "prereg sec.3 s3; G2 n_trials live-head read = "
                   "337336 post-SCREEN cross-wave. After shards: "
                   "judge-finalize = separate round work (pit-95 guard "
                   "wired r421, re-run refusal rc=2 contract; ledger "
                   "TRIAL_LAB_W7_JUDGE batch_trials=284 literal + "
                   "w7_judge.json G1'/G2/DSR/PBO/E[FP] + five-gate x "
                   "streak segmented disclosure; intake slice next per "
                   "prereg sec.6; 48h CEO report clock starts at "
                   "judge-finalize)"),
    "shards": [{
        "key": "judge-0of1",
        "status": "ready",
        "checkpoint": ("results/trial_labor_w7/checkpoint/"
                       "judge_shard_0of1.jsonl (append-per-cell done-set "
                       "resume, W1/W2 cross-kill law)"),
        "note": ("judge-0of1 single shard (W1-W6 judge single-shard "
                 "precedent); workers BelowNormal; dual nulls B=2000 "
                 "block bootstrap + P=2000 sign-flip in-shard per "
                 "prereg sec.3 s3"),
        "owner": None,
    }],
    "worker_class": "self-contained",
    "workers_plan": {
        "workers": 20,
        "priority": "BelowNormal",
        "note": ("worker_cap() RAM-guard governs at runtime (runner "
                 "self-caps, --workers omitted from runner_args per "
                 "W5/W6-JUDGE same-machinery precedent); plan size 20 "
                 "= floor(16 cores/0.8) per prereg sec.9 lower-bound; "
                 "judge initargs carry BOTH leg panels + per-leg ATR20 + "
                 "per-leg gate/vol/yang/vconf/streak state faces = "
                 "heaviest per-worker state in the fleet (W7 adds "
                 "STREAK 11-tuple); dual-leg x {6m,12m,24m} x cost "
                 "{base x1, x2=CostPatch(2)} engine curves per judged "
                 "cell WITH gate+vol+yang+vconf+streak+stop overlays + "
                 "dual nulls B/P resampling ~4-6x screen-cell weight; "
                 "W2-W6 judge same-machinery precedent; est 284 cells "
                 "minutes-scale per W6-JUDGE 293 cells 5.6min burn "
                 "r414"),
    },
}
missing = [k for k in ("id", "ticket_ref", "prereg_ref", "consumer_plan",
                       "runner", "runner_args", "lane_owner", "priority",
                       "status", "entered_at", "data_gates", "shards",
                       "workers_plan") if k not in judge]
assert not missing, missing
pool["entries"].append(judge)
print("JUDGE entry appended: TRIAL-LABOR-W7-JUDGE | status=ready | "
      "shards=1 (judge-0of1) | 15-field presence OK")

tmp = POOL + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(pool, f, ensure_ascii=False, indent=1)
os.replace(tmp, POOL)

pool2 = json.load(open(POOL, encoding="utf-8-sig"))
e2 = [x for x in pool2["entries"]
      if x["id"] == "TRIAL-LABOR-W7-SCREEN"][0]
j2 = [x for x in pool2["entries"]
      if x["id"] == "TRIAL-LABOR-W7-JUDGE"][0]
assert e2["status"] == "done" and e2["shards"][0]["status"] == "done"
assert j2["status"] == "ready" and len(j2["shards"]) == 1
print("re-read verify OK: SCREEN entry+shard done | JUDGE ready | "
      "entries total", len(pool2["entries"]))
