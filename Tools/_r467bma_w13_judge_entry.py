import json

POOL = "results/runnable_pool.json"
NOW = "2026-09-30T11:2x"

with open(POOL, encoding="utf-8") as fh:
    pool = json.load(fh)

entries = pool["entries"]
scr = next(e for e in entries if e["id"] == "TRIAL-LABOR-W13-SCREEN")

# --- flip SCREEN -> done ---
assert scr["status"] == "ready", f"screen status {scr['status']} != ready"
scr["status"] = "done"
scr["done_at"] = "2026-09-30T11:20:00+08:00"
scr["result_ref"] = (
    "results/trial_labor_w13/w13_screen.json + w13_screen_cells.csv (screen-finalize 2026-09-30 "
    "11:1x exit 0 by bm-a r467; 593/593 cells = 393 distinct + 200 nulls complete; null p95 0.5116 "
    "IN sec.5.2 band [0.50,0.52] = eighth consecutive in-band wave; survivors 99/393 = 25.19%; "
    "ledger 359,980 linear append-verified (+593); RESEARCH FACTS: SUMN-axis prediction sec.5.1(ii) "
    ">=1.3x enrichment FALSIFIED AT SCREEN -- sumn10_lo 8.33% (0.28x) / sumn20_lo 12.24% (0.41x) "
    "vs none 30.07% = severe reverse enrichment (anti-enrichment toxic), same class as W12 rsqr "
    "0.32x; A158-TSGATE OOS strong face did NOT transfer to sixteen-tuple screen; mom_oversold "
    "1.56x (34.78% vs 22.26%) + std10_hi 1.44x (34.72% vs 24.12%) positive enrichment continue "
    "lineage; rsqr reverse enrichment persists 0.72x/0.62x) -- burn on autofill lineage tick "
    "11:00:02 pid 25120 target_met=true, shard ckpt 593 lines complete; finalize + fix-first "
    "surgical pair this round (5 sites: 15->16-tuple G-ANCHOR residue + gvvvsktsamsr_seg "
    "definition + 2 duplicate-sumn loop lines + 2 malformed output keys; selftest 48/48 "
    "zero-regression re-verified; W12 r446 fix-first precedent)"
)
sh = scr["shards"][0]
assert sh["key"] == "screen-0of1"
sh["status"] = "done"
sh["done_note"] = "burn complete 11:04 ckpt 593/593; finalize by lane-owner bm-a r467"

# --- enter W13-JUDGE waiting (W5/W12 entry precedent; judge-prep = bm-b deep-panel physical) ---
assert not any(e["id"] == "TRIAL-LABOR-W13-JUDGE" for e in entries), "judge already present"
jud = {
    "id": "TRIAL-LABOR-W13-JUDGE",
    "ticket_ref": "T-2026-09-30-125 WAVE-13 judge slice (TRIAL_LABOR_LAW sec.1 standing supply; prereg FROZEN bm-a r461; runner bm-a r465/r466 landed selftest 48/48 FROZEN grammar sha16 868cd0c6413636e6; GENERATE 393 distinct bm-a autofill 10:40 flip r467; SCREEN 593 cells finalize bm-a r467: null p95 0.5116 in-band, survivors 99 -- judge physical dep satisfied)",
    "prereg_ref": "research/TRIAL_LABOR_W13_PREREG.md FROZEN sec.0 TRIAL_LAB_W13_JUDGE (s3 full judgment batch: batch_trials = survivors 99 judged cells; dual nulls B/P resampling = not ledger +0 per prereg sec.0; DSR n_trials = live chain head cross-wave no-reset, run-time live read governs = 359,980 post-SCREEN; E[FP]=0.05*N_judged; family PBO CSCV 8 blocks family=strategy-module) + physical-order gate (RAM r354 three-sample + serial-position confirm at flip time per bm-b r369 ruling; W2-W12-JUDGE + MASS-W1-JUDGE all done = queue face re-confirm at flip; 48h CEO report clock starts at judge-finalize)",
    "runner": "scripts/trial_labor_w13.py",
    "runner_args": ["judge", "--shard", "0", "--shards", "1"],
    "lane_owner": "bm-b",
    "priority": 1,
    "status": "waiting",
    "entered_at": NOW,
    "entered_by": "bm-a r467",
    "workers_plan": {
        "workers": "worker_cap() pool BelowNormal (judge initargs carry BOTH leg panels + per-leg ATR20 + per-leg eleven-gate state faces incl sumn = heaviest per-worker state in the fleet (worker_cap RAM guard applies); dual-leg x {6m,12m,24m} x cost {base x1, x2=CostPatch(2)} engine curves per judged cell WITH gate+vol+yang+vconf+streak+tstate+amp+mom+std+rsqr+sumn overlays + dual nulls B/P resampling ~4-6x screen-cell weight; W2-W12 judge same-machinery precedent; flip executor = deep-panel machine round (bm-b) post judge-prep + RAM 3-sample gate (W1-JUDGE r357 defer precedent)",
        "priority": "BelowNormal",
        "note": "99 judged cells = second-lightest judge batch in lineage (W12 188 judged); single shard W1-W12-JUDGE precedent; multi-shard i%shards split legal per shard law"
    },
    "data_gates": "WAITING DEPS (flip to ready upon ALL, W12-JUDGE precedent): (1) serial-position face re-confirm at flip time per prereg sec.0 + bm-b r369 ruling (W2/W3/W4/W5/W6/W7/W8/W9/W10/W11/W12-JUDGE + MASS-W1-JUDGE all done as of r467; any newly-entered in-flight verdict face ahead = re-queue behind it); (2) judge-prep run on the deep-panel machine (physical = bm-b t18 sidecar family; cache-less machines exit-2 honest per W1 precedent) -> judge_state.json manifest verdict PASS; (3) machine free RAM >= 4GB three-sample across >=30s (r354 law). IN-RUNNER fail-closed: judge_state/w13_screen absent exit 2; grammar sha != 868cd0c6413636e6 refuse; zero-survivor vacuous face n/a (99 survivors). After shards: judge-finalize = separate round work (ledger TRIAL_LAB_W13_JUDGE batch_trials=survivors literal + w13_judge.json G1'v2/G2/DSR/PBO/E[FP] judgment summary + eleven-gate segmented disclosure incl sumn_face_judgment + sumn interaction faces) -- NOTE judge-finalize same fix-first surgical pair landed r467 (gvvvsktsamsr_sum loop line + output keys; selftest 48/48 re-verified); intake slice lands next per prereg sec.6; 48h CEO report clock starts at judge-finalize",
    "shards": [
        {
            "key": "judge-0of1",
            "status": "waiting",
            "checkpoint": "results/trial_labor_w13/checkpoint/judge_shard_0of1.jsonl (row-level done-set resume, cross-kill W1 law)",
            "note": "single shard W1-W12-JUDGE precedent; multi-shard i%shards split legal per shard law on partial claim; cell enumeration = sorted survivors global index i = dual-nulls seed binding face (stable across shard counts)"
        }
    ],
    "consumer_plan": "TRIAL-LABOR-W13-JUDGE -> w13_judge.json verdict face -> s4 intake (D6 binding gate, TRIAL-SUMN-* accounts spawn only on G2 eligible) -> CEO-REPORT-WAVE13 48h face + scorecard CEO face; sumn negative readout already carried from screen (0.28x-0.41x anti-enrichment) = judge confirms at full caliber",
    "worker_class": "bm-hosted"
}
entries.append(jud)

with open(POOL, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(pool, fh, ensure_ascii=False, indent=1)
    fh.write("\n")

# round-trip self-verify
with open(POOL, encoding="utf-8") as fh:
    p2 = json.load(fh)
s2 = next(e for e in p2["entries"] if e["id"] == "TRIAL-LABOR-W13-SCREEN")
j2 = next(e for e in p2["entries"] if e["id"] == "TRIAL-LABOR-W13-JUDGE")
assert s2["status"] == "done" and s2["shards"][0]["status"] == "done"
assert j2["status"] == "waiting" and j2["lane_owner"] == "bm-b"
print(f"pool surgery OK: SCREEN->done, JUDGE entered waiting; entries={len(p2['entries'])}")
