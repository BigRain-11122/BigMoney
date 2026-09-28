import json

# r413 bm-b: receipt cross-verification (flip script verify-leg, p95 6dp face)
w6 = json.load(open("results/trial_labor_w6/w6_screen.json", encoding="utf-8"))
assert w6["n_distinct"] == 3952 and w6["k_nulls"] == 200
assert w6["n_survivors"] == 293
assert abs(w6["null_family"]["p95_line"] - 0.519553) < 1e-9, w6["null_family"]["p95_line"]
assert round(w6["null_family"]["p95_line"], 4) == 0.5196  # stdout face
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
for path in ("results/runnable_pool.json", "results/runnable_pool.bm-b.json"):
    pool = json.load(open(path, encoding="utf-8"))
    for eid, shard_key in (("TRIAL-LABOR-W6-SCREEN", "screen-0of1"),
                           ("DECISION-CHAIN-V3-TOURNAMENT", "v3-0of1")):
        e = next(x for x in pool["entries"] if x["id"] == eid)
        assert e["status"] == "done" and e["done_at"] and e["result_ref"]
        assert next(s for s in e["shards"] if s["key"] == shard_key)["status"] == "done"
print("receipts + dual-face flip states ALL VERIFIED: w6 293 survivors / p95 0.519553 / ledger 333139; v3 all-arms-fail 6 faces-arms / not-counted honest; both entries done in both faces")
