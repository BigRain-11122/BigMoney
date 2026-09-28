import json, sys

POOL = "results/runnable_pool.json"
NOW = "2026-09-29 02:43:00"

with open(POOL, encoding="utf-8") as fh:
    pool = json.load(fh)

entries = pool["entries"]
scr = next(e for e in entries if e["id"] == "TRIAL-LABOR-W5-SCREEN")
jud = next((e for e in entries if e["id"] == "TRIAL-LABOR-W5-JUDGE"), None)

# --- flip SCREEN -> done (shard burn credit stays bm-c; finalize receipt bm-a r409) ---
assert scr["status"] == "ready", f"screen status {scr['status']} != ready"
scr["status"] = "done"
scr["done_at"] = "2026-09-29T02:43:00+08:00"
scr["result_ref"] = "results/trial_labor_w5/w5_screen.json (finalize bm-a r409: 3926 distinct + 200 nulls, null p95 0.5164, survivors 372, ledger TRIAL_LAB_W5_SCREEN 324489+4126=328615; prereg sec.5-2 bands ALL PASS: null median 0.4972<0.50 / p95 in [0.42,0.62] / survivors 372 in [100,750]; shard burn credit = bm-c autofill tick claim 02:15:39, checkpoint carry-over 36ee7afd)"
sh = scr["shards"][0]
assert sh["key"] == "screen-0of1"
sh["status"] = "done"
sh["result_ref"] = "results/trial_labor_w5/checkpoint/screen_shard_0of1.jsonl (4126/4126 rows complete, bm-c burn 02:15:39->carry-over push 02:25:43; finalize bm-a r409 per MSG-20260929-0235 claim)"

# --- enter W5-JUDGE waiting (mirror W4-JUDGE shape; W2 r362 entry precedent) ---
if jud is None:
    jud = {
        "id": "TRIAL-LABOR-W5-JUDGE",
        "ticket_ref": "T-2026-09-29-114 WAVE-5 judge slice (CEO O-2026-09-27-2245 thousand-trader order + O-2026-09-27-2250 standing law; prereg FROZEN r405 commit 26bab31b + seeds R250 same-commit; runner full-slice built bm-a r406 selftest 73/73 hermetic + fix-first 777e2b5e production-validated; screen-finalize LANDED bm-a r409 per MSG-20260929-0235 claim: 3926/3926 cells, null p95 0.5164, survivors 372 -- judge physical dep satisfied)",
        "prereg_ref": "research/TRIAL_LABOR_W5_PREREG.md FROZEN sec.0 TRIAL_LAB_W5_JUDGE (s3 full judgment batch: batch_trials = survivors 372 judged cells; dual nulls B/P resampling = not ledger +0 per prereg sec.0) + sec.0 W5-JUDGE physical-order gate (RAM r354 three-sample gate + serial-position confirm at flip time per bm-b r369 ruling; W2/W3/W4-JUDGE + MASS-W1-JUDGE all done = queue face re-confirm at flip; 48h CEO report clock starts at judge-finalize) + sec.4 (g1_prime_v2/g2_registration_v2 shared lib zero hand-copy; DSR n_trials = live chain head cross-wave no-reset, run-time live read governs = 328615 post-SCREEN; E[FP]=0.05*N_judged; family PBO CSCV 8 blocks family=strategy-module)",
        "runner": "scripts/trial_labor_w5.py",
        "runner_args": ["judge", "--shard", "0", "--shards", "1"],
        "lane_owner": "bm-b",
        "priority": 1,
        "status": "waiting",
        "entered_at": NOW,
        "workers_plan": {
            "workers": "worker_cap() pool BelowNormal",
            "priority": "BelowNormal",
            "note": "judge initargs carry BOTH leg panels + per-leg ATR20 + per-leg gate/vol/yang state faces = heaviest per-worker state in the fleet (worker_cap RAM guard applies); dual-leg x {6m,12m,24m} x cost {base x1, x2=CostPatch(2)} engine curves per judged cell WITH gate+vol+yang+stop overlays + dual nulls B/P resampling ~4-6x screen-cell weight; W2/W3/W4 judge same-machinery precedent; flip executor = deep-panel machine round (bm-b) post judge-prep + RAM 3-sample gate (W1-JUDGE r357 defer precedent)"
        },
        "data_gates": "WAITING DEPS (flip to ready upon ALL, W4-JUDGE precedent): (1) serial-position face re-confirm at flip time per prereg sec.0 + bm-b r369 ruling (W2/W3/W4-JUDGE + MASS-W1-JUDGE all done as of r409; any newly-entered in-flight verdict face ahead = re-queue behind it); (2) judge-prep run on the deep-panel machine (physical = bm-b t18 sidecar family; cache-less machines exit-2 honest per W1 precedent) -> judge_state.json manifest verdict PASS; (3) machine free RAM >= 4GB three-sample across >=30s (r354 law). IN-RUNNER fail-closed: judge_state/w5_screen absent exit 2; grammar sha != 29720178c39425de refuse; zero-survivor vacuous face n/a (372 survivors). After shards: judge-finalize = separate round work (ledger TRIAL_LAB_W5_JUDGE batch_trials=survivors literal + w5_judge.json G1/G2/DSR/PBO/E[FP] judgment summary + gate x vol x yang segmented disclosure; intake slice lands next per prereg sec.6; 48h CEO report clock starts at judge-finalize)",
        "shards": [
            {
                "key": "judge-0of1",
                "status": "waiting",
                "checkpoint": "results/trial_labor_w5/checkpoint/judge_shard_0of1.jsonl (row-level done-set resume, cross-kill W1 law)",
                "note": "single shard W1/W2/W3/W4-JUDGE precedent; multi-shard i%shards split legal per shard law on partial claim; cell enumeration = sorted survivors global index i = dual-nulls seed binding face (stable across shard counts)"
            }
        ],
        "entered_by": "bm-a r409",
        "worker_class": "bm-hosted"
    }
    entries.append(jud)
    action = "entered"
else:
    action = "already-present (no-op)"

with open(POOL, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(pool, fh, ensure_ascii=False, indent=1)
    fh.write("\n")

# round-trip self-verify
with open(POOL, encoding="utf-8") as fh:
    p2 = json.load(fh)
s2 = next(e for e in p2["entries"] if e["id"] == "TRIAL-LABOR-W5-SCREEN")
j2 = next(e for e in p2["entries"] if e["id"] == "TRIAL-LABOR-W5-JUDGE")
assert s2["status"] == "done" and s2["shards"][0]["status"] == "done"
assert j2["status"] == "waiting" and j2["lane_owner"] == "bm-b"
print(f"pool surgery OK: SCREEN->done, JUDGE {action} waiting; entries={len(p2['entries'])}")
