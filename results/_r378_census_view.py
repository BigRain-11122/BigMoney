import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
j = json.load(open("results/_r370bma_lane_census.json", encoding="utf-8-sig"))
cons = j["consumers"]
hits = j["hits"]
A = {"compute_audit.json", "regime_state.json", "autofill_state.json", "runnable_pool.json",
     "gate_attrition.json", "post_review_criteria.json"}
B = {"update_status.json", "heat_update_status.json", "lhb_update_status.json",
     "futures_update_status.json", "fundamental_status.json", "token_usage.json",
     "crash_fuse.json", "market_clock/call_latest.json", "fundamental_b_layer_filter.json"}
print(f"{'face':58s} {'writes':>6s} {'cons':>4s} family")
for face, info in sorted(hits.items(), key=lambda kv: -kv[1]["commits"]):
    fam = "A" if face in A else ("B" if face in B else "C")
    cv = cons.get(face, 0)
    c = len(cv) if isinstance(cv, list) else cv
    print(f"{face:58s} {info['commits']:>6d} {c:>4d} {fam}")
