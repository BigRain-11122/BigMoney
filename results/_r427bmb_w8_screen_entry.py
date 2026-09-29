# -*- coding: utf-8 -*-
# r427 bm-b: TRIAL-LABOR-W8 harvest -- mark GENERATE done + submit SCREEN pool entry
# W7 precedent (r420/r421 entry shape); atomic write via os.replace (no torn read for autofill ticks)
import json, os, sys, io, datetime

POOL = r"results\runnable_pool.json"
raw = open(POOL, "rb").read()
pool = json.loads(raw.decode("utf-8"))
assert isinstance(pool.get("entries"), list)

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

# --- 1) mark GENERATE done ---
gen = None
for e in pool["entries"]:
    if e.get("id") == "TRIAL-LABOR-W8-GENERATE":
        gen = e
        break
assert gen is not None, "GENERATE entry missing"
assert os.path.exists(r"results\trial_labor_w8\w8_candidates.json"), "candidates marker missing"
cands = json.load(open(r"results\trial_labor_w8\w8_candidates.json", encoding="utf-8"))
assert cands["grammar_sha256"] == "282c3290d1b431bc", "grammar sha drift"
assert cands["n"] == 2834, "n mismatch"

gen["status"] = "done"
gen["done_at"] = "2026-09-29T13:40:06+08:00"
gen["result_ref"] = "results/trial_labor_w8/w8_candidates.json"
gen["done_note"] = ("r427 bm-b harvest: autofill launch 13:30:01 pid10608 -> w8_candidates.json landed 13:40:06 "
    "(single-shot completion marker, refuse-if-exists guard honored; pid exited clean post-rename ~13:57); "
    "n=2834 (raw 5,000 A500/B4500 -> dedup -> 2,834 distinct, below the '>=3,000' prereg sec.0 estimate -- honest, "
    "11-tuple axis space raises fingerprint collisions; tstate faces {deep_pullback 684, none 1304, oversold_rsv 846}); "
    "grammar sha16 282c3290d1b431bc == FROZEN verified at harvest (gate-b); 16-source exclusion face real-read "
    "hits A=0/B=0 (tstate=none-only exclusion face; new-syntax tstate faces legal-by-construction); "
    "TRIAL_GRAMMAR_LEDGER wave-8 row appended same-run; evidence_cutoff 2026-09-22")

# --- 2) submit SCREEN entry ---
assert not any(e.get("id") == "TRIAL-LABOR-W8-SCREEN" for e in pool["entries"]), "SCREEN entry already exists"
prep = json.load(open(r"results\trial_labor_w8\prep_state.json", encoding="utf-8"))
assert prep["gates"]["G-PANEL"]["pass"] and prep["gates"]["G-ANCHOR"]["pass"]
assert prep["gates"]["G-CENSUS"]["pass"] and prep["gates"]["G-EXCLUDE"]["pass"]

screen = {
 "id": "TRIAL-LABOR-W8-SCREEN",
 "ticket_ref": ("T-2026-09-29-120 WAVE-8 screen slice (CEO O-2026-09-27-2245 thousand-trader order + "
    "O-2026-09-27-2250 standing law; prereg FROZEN bm-b r424 draft-author same-machine next-round freeze per "
    "r423 next-pointer; SEED berths 20306500/20307000/20307500 held same-commit R250 one-step; freeze-time "
    "correction MSG-20260929-1230-bmc-bmb sec.6 pool routing lane_owner=bm-b SCREEN+JUDGE; runner slice-1 built "
    "bm-b r425; GENERATE landed r427 harvest commit (autofill 13:30:01 pid10608 -> n=2834 13:40:06 + "
    "TRIAL_GRAMMAR_LEDGER wave-8 row))"),
 "prereg_ref": ("research/TRIAL_LABOR_W8_PREREG.md FROZEN sec.0 TRIAL_LAB_W8_SCREEN (s2 cheap initial screen "
    "batch: batch_trials = 2,834 distinct + 200 nulls = 3,034 cells at 1 trial/cell; raw 5,000 -> dedup 2,834 "
    "honest below the >=3,000 sec.0 estimate; evidence_cutoff 2026-09-22 P-5C frozen binding on both batches; "
    "eleven-tuple grammar sha16 282c3290d1b431bc == FROZEN)"),
 "runner": "scripts/trial_labor_w8.py",
 "runner_args": ["screen", "--shard", "0", "--shards", "1"],
 "lane_owner": "bm-b",
 "priority": 1,
 "status": "ready",
 "entered_at": now,
 "data_gates": ("GATES ALL GREEN (direct-ready r427, W1-W7-SCREEN lineage): (1) TRIAL-LABOR-W8-GENERATE done -- "
    "landed 13:40:06 w8_candidates.json n=2834 single-shot completion marker in-repo this commit "
    "(refuse-if-exists guard); (2) screen-prep PASS -- results/trial_labor_w8/prep_state.json bm-b r427 13:41:28: "
    "panel 48/48, anchors 6/6 faithful (grammar_replay IS/OOS == frozen), census {6m 1253, 12m 1127, 24m 875} == "
    "frozen, starts 1253, passive 6m precomputed, gate na-window 199 bars, G-VOL 594calm/518wild first-valid 519, "
    "G-YANG 819yang/812red zero-warmup, G-VCONF 784surge/828dry warmup 19, G-STREAK 384up/389down/856neither "
    "warmup 2, G-TSTATE mad60 188true/1453decidable warmup 178 + rsv60 332true/1572decidable warmup 59; "
    "(3) grammar sha16 282c3290d1b431bc == FROZEN pinned at candidates serialization (fail-closed gate-b)"),
 "shards": [{
    "key": "screen-0of1",
    "status": "ready",
    "checkpoint": "results/trial_labor_w8/checkpoint/screen_shard_0of1.jsonl (append-per-cell done-set resume, W1/W2 cross-kill law)",
    "note": ("single shard; worker_cap() parallelism inside the shard (W2-W7-SCREEN same shape); multi-shard "
             "i%shards split legal per shard law on partial claim")
 }],
 "entered_by": "bm-b r427",
 "worker_class": "self-contained",
 "workers_plan": {
    "workers": "worker_cap() pool BelowNormal (16-core bm-b: <=12; W6-SCREEN 4,152 cells; W7-SCREEN 3,904 cells)",
    "priority": "BelowNormal",
    "note": ("W8 3,034 cells (2,834 distinct + 200 nulls) est minutes-level pool batch; per-cell jsonl "
             "checkpoint cross-kill resume (W1 law); 50-candidate checkpoint cadence per prereg sec.0")
 },
 "consumer_plan": ("TRIAL-LABOR-W8-SCREEN -> screen-finalize (lane-owner separate round work per W5/W6/W7 "
    "precedent) -> w8_screen.json + w8_screen_cells.csv + null p95 (W1-W7 lineage 0.5116-0.5196 reference band) "
    "+ TRIAL_GRAMMAR_LEDGER TRIAL_LAB_W8_SCREEN trials row -> TRIAL-LABOR-W8-JUDGE entry next (judge-prep + RAM "
    "r354 three-sample gate + serial-position face = zero in-flight judge faces ahead + host_gates MSG-1305 "
    "wiring per pit-103: dir_nonempty Money02/data/cache/t18_deep_panel/ohlcv *.parquet 48 files verified "
    "non-empty r427 pre-flight) -> judged verdict face w8_judge.json -> s4 intake (D6 binding gate -> "
    "STRATEGY_LIBRARY registration rows) -> 48h CEO report clock starts at judge landing")
}
pool["entries"].append(screen)
pool["updated_at"] = now

# --- atomic write, preserving format: utf-8 no BOM, indent=2, CRLF ---
tmp = POOL + ".tmp_r427bmb"
with io.open(tmp, "w", encoding="utf-8", newline="") as f:
    json.dump(pool, f, ensure_ascii=False, indent=2)
    f.write("\n")
# normalize LF -> CRLF to match existing file style
data = open(tmp, "rb").read()
data = data.replace(b"\n", b"\r\n")
open(tmp, "wb").write(data)
os.replace(tmp, POOL)

# verify reparse
chk = json.load(open(POOL, encoding="utf-8"))
ids = [e["id"] for e in chk["entries"]]
print("OK entries:", len(ids), "| GENERATE status:", [e["status"] for e in chk["entries"] if e["id"]=="TRIAL-LABOR-W8-GENERATE"][0], "| SCREEN present:", "TRIAL-LABOR-W8-SCREEN" in ids)
