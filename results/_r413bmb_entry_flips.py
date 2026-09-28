import json

# r413 bm-b: dual-entry done-flip (dual-face, r387/r389/r395/r406/r407 precedent).
# (A) TRIAL-LABOR-W6-SCREEN: burn complete pid3984 06:40:05 (worker log
#     "shard 0of1 complete", 4152/4152 cells, normal exit -- screen-finalize is a
#     SEPARATE subcommand, runner never crashes); screen-finalize executed
#     in-round by lane owner bm-b per W5 precedent ->
#     results/trial_labor_w6/w6_screen.json: 3952 distinct + 200 nulls,
#     null p95 0.5196, survivors 293, ledger 328987 + 4152 = 333139 linear.
# (B) DECISION-CHAIN-V3-TOURNAMENT: verdict landed (predecessor r412 closeout
#     commit + harvest push f452727d8 = landed-marker r244 law); relaunch
#     pid21584 06:00:15 (autofill, shard-unflipped face) re-ran deterministic
#     finalize 202.1s -> byte-identical verdict re-write 06:22:42 -> honest
#     negative all arms: chain_win A-H1/A-H2S/A-H3 = False x faces {base,x2},
#     J-TARGET 0/3, winners [], N_eff=16,566; trials ledger NOT counted
#     (audit FLAG:supply_gap,supply_floor -> prereg s0 not-counted law);
#     executed_by bm-b. Flip clears the crash-fuse confirm loop
#     (06:30:03 CONFIRM count=1 same-version relaunch refused).

POOL = "results/runnable_pool.json"
LANE = "results/runnable_pool.bm-b.json"

def flip(path, eid, shard_key, done_at, result_ref, done_note):
    with open(path, encoding="utf-8") as fh:
        pool = json.load(fh)
    ent = next(e for e in pool["entries"] if e["id"] == eid)
    assert ent["status"] == "ready", f"{path}: {eid} status {ent['status']} != ready"
    sh = next(s for s in ent["shards"] if s["key"] == shard_key)
    assert sh["status"] != "done", f"{path}: {eid} shard already done"
    ent["status"] = "done"
    ent["done_at"] = done_at
    ent["result_ref"] = result_ref
    ent["done_note"] = done_note
    sh["status"] = "done"
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(pool, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    with open(path, encoding="utf-8") as fh:
        p2 = json.load(fh)
    e2 = next(e for e in p2["entries"] if e["id"] == eid)
    s2 = next(s for s in e2["shards"] if s["key"] == shard_key)
    assert e2["status"] == "done" and s2["status"] == "done"
    assert e2["done_at"] == done_at and e2["result_ref"] == result_ref
    print(f"{path}: {eid} ready->done OK (shard {shard_key})")

note_screen = (
    "r413 bm-b harvest: screen burn pid3984 complete 06:40:05 (worker log "
    "'shard 0of1 complete', 4152/4152 cells checkpoint append-per-cell, normal "
    "exit -- no crash; screen-finalize = separate subcommand per runner design); "
    "screen-finalize executed in-round by lane owner bm-b (W5 bm-a r409 "
    "precedent): 3952 distinct + 200 nulls, null p95 0.5196, survivors 293 "
    "(survival rule beat6m_rate > null_p95 frozen), vconf segmented survival "
    "surge 0.0878 > none 0.0727 > dry 0.0611; trials_ledger TRIAL_LAB_W6_SCREEN "
    "prev 328987 + 4152 = 333139 cross-wave linear no-reset; grammar "
    "sha16 2d395f5f8e7d16cb anchor; evidence_cutoff 2026-09-22 lockbox. "
    "JUDGE physical dep now satisfied; judge-prep + W6-JUDGE pool entry = "
    "same-round wiring (RAM r354 3-sample gate + serial-position face at "
    "flip per prereg sec.0)."
)
for path in (POOL, LANE):
    flip(path, "TRIAL-LABOR-W6-SCREEN", "screen-0of1",
         "2026-09-29T06:49:00+08:00",
         "results/trial_labor_w6/w6_screen.json", note_screen)

note_v3 = (
    "r413 bm-b harvest: verdict landed (predecessor r412 closeout commit + "
    "harvest push f452727d8 = landed-marker per r244 law; relayed by my r413 "
    "harvest push 45d0f31db). Honest negative: chain_win A-H1/A-H2S/A-H3 all "
    "False on faces {base, x2}, J-TARGET 0/3, winners [], N_eff=16,566 "
    "(3 arms x 5,522); trials ledger NOT counted per prereg s0 (audit "
    "FLAG:supply_gap,supply_floor -> not-counted law, total null honest); "
    "executed_by bm-b, evidence_cutoff 2026-09-22. Relaunch pid21584 06:00:15 "
    "(autofill saw unflipped shard face) re-ran deterministic finalize "
    "202.1s -> byte-identical verdict rewrite 06:22:42 = reproducibility "
    "re-verify free-of-charge; crash-fuse CONFIRM 06:30:03 count=1 loop "
    "cleared by this flip (shard status done -> never a crash, autofill "
    "_confirm_crashes landing check). v4 self-paper tray wiring = 10-01 "
    "month-bound face per O-1506 s4, untouched this round."
)
for path in (POOL, LANE):
    flip(path, "DECISION-CHAIN-V3-TOURNAMENT", "v3-0of1",
         "2026-09-29T06:22:42+08:00",
         "results/decision_chain_v3_tournament.json", note_v3)

# receipt cross-verification
w6 = json.load(open("results/trial_labor_w6/w6_screen.json", encoding="utf-8"))
assert w6["n_distinct"] == 3952 and w6["k_nulls"] == 200
assert w6["n_survivors"] == 293
assert abs(w6["null_family"]["p95_line"] - 0.5196) < 1e-9
assert w6["trials_ledger"]["prev_total"] == 328987
assert w6["trials_ledger"]["batch_trials"] == 4152
assert w6["trials_ledger"]["total"] == 333139
assert w6["grammar_sha256"].startswith("2d395f5f8e7d16cb")
v3 = json.load(open("results/decision_chain_v3_tournament.json", encoding="utf-8"))
for face in ("base", "x2"):
    for arm in ("A-H1", "A-H2S", "A-H3"):
        assert v3["verdict"]["j_c_faces"][face][arm]["chain_win"] is False
assert v3["trials_ledger"]["batch_trials"] == 16566
assert v3["trials_ledger"]["total"] is None
print("receipts cross-verified: w6_screen 293 survivors ledger 333139; "
      "v3 all-arms-fail 6/6 faces x arms, ledger not-counted honest")
print("dual-face dual-entry done-flip complete")
