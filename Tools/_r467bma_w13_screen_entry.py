import json

POOL = "results/runnable_pool.json"
NOW = "2026-09-30T11:05:00+08:00"

with open(POOL, encoding="utf-8") as fh:
    pool = json.load(fh)

entries = pool["entries"]
assert not any(e["id"] == "TRIAL-LABOR-W13-SCREEN" for e in entries), "already present"

scr = {
    "id": "TRIAL-LABOR-W13-SCREEN",
    "ticket_ref": "T-2026-09-30-125 WAVE-13 screen slice (TRIAL_LABOR_LAW sec.1 standing supply; prereg FROZEN bm-a r461 drafting-machine self-freeze, AMP->W9/MOM->W10/STD->W11/RSQR->W12/SUMN->W13 five-straight lineage; SEED three keys 20323000/20323500/20324000 R250 one-step law facts results/_r461bma_w13_seed_law_facts.json; runner bm-a r465/r466 landed selftest 48/48 FROZEN grammar sha16 868cd0c6413636e6 axis_combos 282,175,488; GENERATE consumed bm-a autofill tick 10:40:01 pid 87476 target_met=true, 393 distinct, pool flip bm-a r467)",
    "prereg_ref": "research/TRIAL_LABOR_W13_PREREG.md FROZEN sec.0 TRIAL_LAB_W13_SCREEN (s2 cheap initial screen batch: batch_trials = 393 distinct + 200 nulls = 593 cells at 1 trial/cell; raw 5,000 -> dedup 393 = 7.9% HONEST far-below sec.5.1(i) [45%,60%] band AND below the >=3,000 distinct expectation -- falsifiable prediction face judged by actual not by band per W12 below-band precedent; structural read: sixteen-tuple stacked-gate effective-face collapse trend is MONOTONIC in lineage (W9 2,715 -> W11 1,462 -> W12 1,059 -> W13 593 cells) = more stacked gate axes -> rarer co-open -> heavier fingerprint collapse; W14 prereg band refresh note carried; evidence_cutoff 2026-09-22 P-5C frozen binding on both batches; sixteen-tuple grammar sha16 868cd0c6413636e6 == FROZEN pin; screen line = beat6m > null p95 strictly, W12 sec.3 same-structure; null seed 20323500)",
    "runner": "scripts/trial_labor_w13.py",
    "runner_args": ["screen", "--shard", "0", "--shards", "1"],
    "lane_owner": "bm-a",
    "priority": 1,
    "status": "ready",
    "entered_at": NOW,
    "entered_by": "bm-a r467",
    "data_gates": "GATES ALL GREEN (direct-ready r467, W12-SCREEN r446 lineage): (1) TRIAL-LABOR-W13-GENERATE done -- landed 10:46:04 w13_candidates.json n=393 single-shot completion marker in-repo (refuse-if-exists guard; grammar sha16 868cd0c6413636e6, seeds gen=20323000/null=20323500/unc=20324000); (2) screen-prep PASS -- bm-a r467 11:0x 26s: panel 48/48, anchors 6/6 faithful (grammar_replay IS/OOS == frozen live anchor; G-ANCHOR identity-face 15->16-tuple residue IndexError axis[15] surgical fix +1 none this round = W12 r446 one-site-miss same-class precedent, selftest 48/48 zero-regression re-verified), census {6m 1253, 12m 1127, 24m 875} == frozen, starts 1253, passive 6m precomputed, gate na-window 199 bars, G-VOL 594calm/518wild, G-YANG 819yang/812red zero-warmup, G-VCONF 784surge/828dry warmup 19, G-STREAK 384up/389down/856neither warmup 2, G-TSTATE mad60 188true/1453decidable warmup 178 + rsv60 332true/1572decidable warmup 59, G-AMP 801wide/811narrow decidable 1612 warmup 19, G-MOM 153open/1339closed decidable 1492 warmup 139, G-RSQR 163open/1348closed decidable 1511 rsqr10-open 142, G-SUMN 150open/1361closed decidable 1511 sumn10-open 144 -- all frozen-anchor-faithful; (3) free RAM 47.4GB >> 4GB r354 three-sample ban threshold (in-runner gate authoritative)",
    "consumer_plan": "TRIAL-LABOR-W13-SCREEN -> screen-finalize (lane-owner separate round work per W5-W12 precedent) -> w13_screen.json + w13_screen_cells.csv + null p95 (W12 live-read 0.513208 reference carried at freeze; p95 band [0.50,0.52] W12 sec.5.2 face) + ledger TRIAL_LAB_W13_SCREEN row (science_gates.append_ledger live-head prev read, batch_trials=593) + sec.5.1(ii) sumn-axis screen enrichment readout (prediction: sumn20_lo/sumn10_lo survival >=1.3x vs none baseline per A158-TSGATE OOS strong face; negative finding = lawful output; sumn-AND-calm drag-family prediction two-way death disclosed) -> TRIAL-LABOR-W13-JUDGE entry next (judge-prep + RAM r354 three-sample gate) -> w13_judge.json verdict -> s4 intake -> CEO-REPORT-WAVE13 48h face",
    "shards": [
        {
            "key": "screen-0of1",
            "status": "ready",
            "checkpoint": "results/trial_labor_w13/checkpoint/screen_shard_0of1.jsonl (append-per-cell done-set resume, W1/W2 cross-kill law; dir gitignored per r429 root-cause class fix)",
            "note": "single shard; worker_cap() parallelism inside the shard (W2-W12-SCREEN same shape); multi-shard i%shards split legal per shard law on partial claim"
        }
    ],
    "worker_class": "self-contained",
    "workers_plan": {
        "workers": "worker_cap() pool BelowNormal (32-core bm-a: <=26 CEO 10% reserve law; W12-SCREEN 1,059 cells ~3min wall; W13-SCREEN 593 cells = 393 distinct + 200 nulls, lightest in lineage; screen leg-L 6m full-history per cell, eleven-gate face carried per cell incl sumn)",
        "priority": "BelowNormal",
        "note": "minutes-scale pool batch per prereg sec.0 (W9-SCREEN 2,715 cells ~8min; W12 1,059 ~3min; W13 593 lightest); checkpoint every 50 candidates per prereg sec.0; free RAM 47.4GB at arm >> 4GB r354 three-sample ban threshold (in-runner gate authoritative)"
    },
}
entries.append(scr)

with open(POOL, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(pool, fh, ensure_ascii=False, indent=1)
    fh.write("\n")

# round-trip self-verify
with open(POOL, encoding="utf-8") as fh:
    p2 = json.load(fh)
s2 = next(e for e in p2["entries"] if e["id"] == "TRIAL-LABOR-W13-SCREEN")
assert s2["status"] == "ready" and s2["shards"][0]["status"] == "ready"
assert s2["lane_owner"] == "bm-a" and len(p2["entries"]) == len(entries)
print(f"pool entry OK: W13-SCREEN ready; entries={len(p2['entries'])}")
