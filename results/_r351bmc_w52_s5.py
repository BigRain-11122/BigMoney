import json, sys
sys.stdout.reconfigure(encoding="utf-8")
for w in (50, 51, 52):
    d = json.load(open(f"results/perpetual_faces/n1_w{w}_results.json", encoding="utf-8"))
    print(f"===W{w}===")
    print("[null_pool_cumulative]", json.dumps(d["null_pool_cumulative"], ensure_ascii=False)[:600])
    print("[skill_line]", json.dumps(d["skill_line_v2_k_lift"], ensure_ascii=False)[:400])
    fA = d["families"]["A_random_engine_exit"]
    print("[A p95]", fA["full_sharpe_p95"], "[A p99]", fA["full_sharpe_p99"], "[A mu]", fA["full_sharpe_mu"])
    print("[shards]", len(d["shards_consumed"]), "[universe]", d["universe"])
    print("[audit]", json.dumps(d["audit"], ensure_ascii=False)[:200])
