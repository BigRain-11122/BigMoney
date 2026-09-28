import json

# r407 bm-b: TRIAL-LABOR-W5-JUDGE entry done-flip (dual-face, r387/r389/r395/r406 precedent).
# Receipt: judge-finalize detached pid3108 (r406 @03:26:33) landed 2026-09-29 03:48:39
# -> results/trial_labor_w5/w5_judge.json (372 judged, E[FP]=18.6, G2 eligible 0,
#    ledger 328615+372=328987 linear, evidence_cutoff 2026-09-22, grammar 29720178c39425de).
# 48h CEO report clock starts at finalize landing (standing deadline 2026-10-01 03:48).

POOL = "results/runnable_pool.json"
LANE = "results/runnable_pool.bm-b.json"

for path in (POOL, LANE):
    with open(path, encoding="utf-8") as fh:
        pool = json.load(fh)
    jud = next(e for e in pool["entries"] if e["id"] == "TRIAL-LABOR-W5-JUDGE")
    assert jud["status"] == "ready", f"{path}: entry status {jud['status']} != ready"
    assert jud["shards"][0]["status"] == "done", f"{path}: shard not done"
    jud["status"] = "done"
    jud["done_at"] = "2026-09-29T03:48:39+08:00"
    jud["result_ref"] = "results/trial_labor_w5/w5_judge.json"
    jud["done_note"] = (
        "r407 bm-b harvest: judge-finalize detached pid3108 (r406 detach 03:26:33, r386 law) "
        "landed 03:48:39 -> w5_judge.json: 372 judged cells (== w5_screen survivors 372), "
        "E[FP]=18.6, G2 eligible 0 -> [] (single G1 pass at gate=none|vol=none|yang=none 1/109 "
        "did not clear G2), family PBO 11 modules (momentum 0.9143, sentiment 0.9286, "
        "composite_rotation 0.8571, patterns 0.1714 lowest), dual nulls B/P resampling not "
        "ledger +0 per prereg sec.0; trials_ledger TRIAL_LAB_W5_JUDGE prev 328615 + 372 = "
        "328987 cross-wave linear no-reset verified; evidence_cutoff 2026-09-22 lockbox; "
        "wave-5 funnel honest zero-registration. Intake zero-face landed same round: "
        "results/trial_labor_w5/w5_intake.json (prereg sec.6 s4 actual-count clause, W3 "
        "precedent shape; zero eligible = D6/library/paper-desk all zero-surface). "
        "48h CEO report clock running (deadline 2026-10-01 03:48)."
    )
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(pool, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    # round-trip reload assert
    with open(path, encoding="utf-8") as fh:
        p2 = json.load(fh)
    j2 = next(e for e in p2["entries"] if e["id"] == "TRIAL-LABOR-W5-JUDGE")
    assert j2["status"] == "done", f"{path}: reload entry not done"
    assert j2["done_at"] == "2026-09-29T03:48:39+08:00"
    assert j2["result_ref"] == "results/trial_labor_w5/w5_judge.json"
    assert j2["shards"][0]["status"] == "done"
    print(f"{path}: W5-JUDGE entry ready->done OK")

# receipt cross-verification (harvest acceptance per r406 next-pointer)
with open("results/trial_labor_w5/w5_judge.json", encoding="utf-8") as fh:
    rec = json.load(fh)
assert rec["n_judged_cells"] == 372
assert rec["n_eligible_g2"] == 0
assert rec["trials_ledger"]["prev_total"] == 328615
assert rec["trials_ledger"]["batch_trials"] == 372
assert rec["trials_ledger"]["total"] == 328987
assert rec["evidence_cutoff"] == "2026-09-22"
with open("results/trial_labor_w5/w5_intake.json", encoding="utf-8") as fh:
    itk = json.load(fh)
assert itk["n_eligible"] == 0 and itk["wave"] == "TRIAL_LABOR_W5"
print("receipt + intake cross-verified: 372 judged, ledger 328987 linear, zero-registration honest")
print("dual-face entry done-flip complete")
