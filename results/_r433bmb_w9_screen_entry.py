# -*- coding: utf-8 -*-
# r433 bm-b: TRIAL-LABOR-W9 harvest -- mark GENERATE done + submit SCREEN pool entry
# r427 W8 precedent (results/_r427bmb_w8_screen_entry.py entry shape); atomic write via
# os.replace (no torn read for autofill ticks)
import json, os, sys, io, datetime

POOL = r"results\runnable_pool.json"
pool = json.loads(open(POOL, "rb").read().decode("utf-8"))
assert isinstance(pool.get("entries"), list)

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

# --- 1) mark GENERATE done ---
gen = None
for e in pool["entries"]:
    if e.get("id") == "TRIAL-LABOR-W9-GENERATE":
        gen = e
        break
assert gen is not None, "GENERATE entry missing"
assert os.path.exists(r"results\trial_labor_w9\w9_candidates.json"), "candidates marker missing"
cands = json.load(open(r"results\trial_labor_w9\w9_candidates.json", encoding="utf-8"))
assert cands["grammar_sha256"] == "0601dda70b0209fa", "grammar sha drift"
assert cands["n"] == 2515, "n mismatch"
ded = cands["dedup"]
assert ded["raw"] == 5000 and ded["distinct"] == 2515, "dedup mismatch"
prep = json.load(open(r"results\trial_labor_w9\prep_state.json", encoding="utf-8"))
assert prep["grammar_sha256"] == "0601dda70b0209fa", "prep grammar sha drift"
for k in ("G-PANEL", "G-ANCHOR", "G-CENSUS", "G-EXCLUDE",
          "G-VOL", "G-YANG", "G-VCONF", "G-STREAK", "G-TSTATE", "G-AMP"):
    assert prep["gates"][k]["pass"], "prep gate %s fail" % k

gen["status"] = "done"
gen["done_at"] = "2026-09-29T16:40:23+08:00"
gen["result_ref"] = "results/trial_labor_w9/w9_candidates.json"
gen["done_note"] = ("r433 bm-b harvest: autofill launch 16:30:02 pid12712 -> w9_candidates.json landed 16:40:23 "
    "(single-shot completion marker, refuse-if-exists guard honored; pid exited clean, elapsed 589.8s, "
    "zero engine cells burned); n=2515 (raw 5,000 A500/B4500 -> exclusion hits 0 -> dedup 2,515 distinct, "
    "BELOW the [2,800, 4,600] prereg sec.5.1 prediction band -- honest miss, twelve-tuple AMP gate-closed "
    "zeroing raises effective-signal collapse mass vs eleven-tuple W8 2,834; amp faces {amp_narrow 823, "
    "amp_wide 739, none 953}); grammar sha16 0601dda70b0209fa == FROZEN verified at harvest (gate-b); "
    "18-source exclusion face real-read hits 0 (amp=none-only exclusion face, expected-hits ~1.7 at "
    "950-draw none-face mass -- zero hits statistically ordinary); TRIAL_GRAMMAR_LEDGER wave-9 row "
    "runner-appended same-run (consumed 16:40:23); evidence_cutoff 2026-09-22")

# --- 2) submit SCREEN entry ---
assert not any(e.get("id") == "TRIAL-LABOR-W9-SCREEN" for e in pool["entries"]), "SCREEN entry already exists"

screen = {
 "id": "TRIAL-LABOR-W9-SCREEN",
 "ticket_ref": ("T-2026-09-29-121 WAVE-9 screen slice (CEO O-2026-09-27-2245 thousand-trader order + "
    "O-2026-09-27-2250 standing law; prereg FROZEN bm-b r432 draft-author same-machine next-round freeze per "
    "r431 next-pointer; SEED berths 20309500/20310000/20310500 held same-commit R250 one-step, in-draft-window "
    "double-collision re-pick lineage disclosed in prereg banner + registry comments; pool routing lane_owner=bm-b "
    "SCREEN+JUDGE per prereg sec.6 both-faces value (W8 freeze-time correction lineage, pit-103 dead-hand "
    "recurrence-proof); runner slice-1 built bm-b r432; GENERATE landed r433 harvest commit (autofill 16:30:02 "
    "pid12712 -> n=2515 16:40:23 + TRIAL_GRAMMAR_LEDGER wave-9 row))"),
 "prereg_ref": ("research/TRIAL_LABOR_W9_PREREG.md FROZEN sec.0 TRIAL_LAB_W9_SCREEN (s2 cheap initial screen "
    "batch: batch_trials = 2,515 distinct + 200 nulls = 2,715 cells at 1 trial/cell; raw 5,000 -> dedup 2,515 "
    "honest BELOW the [2,800, 4,600] sec.5.1 prediction band; evidence_cutoff 2026-09-22 P-5C frozen binding on "
    "both batches; twelve-tuple grammar sha16 0601dda70b0209fa == FROZEN)"),
 "runner": "scripts/trial_labor_w9.py",
 "runner_args": ["screen", "--shard", "0", "--shards", "1"],
 "lane_owner": "bm-b",
 "priority": 1,
 "status": "ready",
 "entered_at": now,
 "data_gates": ("GATES ALL GREEN (direct-ready r433, W1-W8-SCREEN lineage): (1) TRIAL-LABOR-W9-GENERATE done -- "
    "landed 16:40:23 w9_candidates.json n=2515 single-shot completion marker in-repo this commit "
    "(refuse-if-exists guard); (2) screen-prep PASS -- results/trial_labor_w9/prep_state.json bm-b r433 16:52: "
    "panel 48/48, anchors 6/6 faithful (grammar_replay IS/OOS == frozen), census {6m 1253, 12m 1127, 24m 875} == "
    "frozen, starts 1253, passive 6m precomputed, gate na-window 199 bars, G-VOL 594calm/518wild first-valid 519, "
    "G-YANG 819yang/812red zero-warmup, G-VCONF 784surge/828dry warmup 19, G-STREAK 384up/389down/856neither "
    "warmup 2, G-TSTATE mad60 188true/1453decidable warmup 178 + rsv60 332true/1572decidable warmup 59, "
    "G-AMP 801wide/811narrow decidable 1612 warmup 19 (NEW wave-9 fail-closed anchor face, prep-window "
    "replay; full-history 1718/1746/3464 per r431 probe facts); (3) grammar sha16 0601dda70b0209fa == FROZEN "
    "pinned at candidates serialization (fail-closed gate-b)"),
 "shards": [{
    "key": "screen-0of1",
    "status": "ready",
    "checkpoint": "results/trial_labor_w9/checkpoint/screen_shard_0of1.jsonl (append-per-cell done-set resume, W1/W2 cross-kill law; dir gitignored per r429 root-cause class fix)",
    "note": ("single shard; worker_cap() parallelism inside the shard (W2-W8-SCREEN same shape); multi-shard "
             "i%shards split legal per shard law on partial claim")
 }],
 "entered_by": "bm-b r433",
 "worker_class": "self-contained",
 "workers_plan": {
    "workers": "worker_cap() pool BelowNormal (16-core bm-b: <=12; W6-SCREEN 4,152 cells; W7-SCREEN 3,904 cells; W8-SCREEN 3,034 cells)",
    "priority": "BelowNormal",
    "note": ("W9 2,715 cells (2,515 distinct + 200 nulls) est minutes-level pool batch; per-cell jsonl "
             "checkpoint cross-kill resume (W1 law); 50-candidate checkpoint cadence per prereg sec.0; "
             "null family = 200 same-grammar random-signal candidates, amp gate legs drawn in the same "
             "grid/param space per BACKTEST_PLAN three-iron-law, seed trial_labor_w9_scrnull=20310000")
 },
 "consumer_plan": ("TRIAL-LABOR-W9-SCREEN -> screen-finalize (lane-owner separate round work per W5-W8 "
    "precedent) -> w9_screen.json + w9_screen_cells.csv + null p95 (W1-W8 lineage 0.5116-0.5196 reference band, "
    "W8=0.5156; W9 sec.5.2 recalibrated band [0.50, 0.52] honest) + ledger TRIAL_LAB_W9_SCREEN row "
    "(science_gates.append_ledger live-head prev read, pit-112 out-dict embed law) -> TRIAL-LABOR-W9-JUDGE entry "
    "next (judge-prep + RAM r354 three-sample gate + serial-position face = zero in-flight judge faces ahead + "
    "host_gates MSG-1305 wiring per pit-103: dir_nonempty Money02/data/cache/t18_deep_panel/ohlcv *.parquet 48 "
    "files verified non-empty at JUDGE submission pre-flight) -> judged verdict face w9_judge.json "
    "(seven-gate x amp interaction disclosure columns per sec.3) -> s4 intake (D6 binding gate -> "
    "STRATEGY_LIBRARY registration rows) -> 48h CEO report clock starts at judge landing; W10 prereg "
    "reference-band feed per consumer lineage")
}
pool["entries"].append(screen)
pool["updated_at"] = now

# --- atomic write, preserving format: utf-8 no BOM, indent=2, CRLF ---
tmp = POOL + ".tmp_r433bmb"
with io.open(tmp, "w", encoding="utf-8", newline="") as f:
    json.dump(pool, f, ensure_ascii=False, indent=2)
    f.write("\n")
data = open(tmp, "rb").read()
data = data.replace(b"\n", b"\r\n")
open(tmp, "wb").write(data)
os.replace(tmp, POOL)

# verify reparse
chk = json.load(open(POOL, encoding="utf-8"))
ids = [e["id"] for e in chk["entries"]]
gen_status = [e["status"] for e in chk["entries"] if e["id"] == "TRIAL-LABOR-W9-GENERATE"][0]
scr = [e for e in chk["entries"] if e["id"] == "TRIAL-LABOR-W9-SCREEN"][0]
req = all(k in scr for k in ("consumer_plan", "lane_owner", "workers_plan", "data_gates", "runner_args"))
print("OK entries:", len(ids), "| GENERATE:", gen_status, "| SCREEN present: ready | pit-103 required fields:", req)
