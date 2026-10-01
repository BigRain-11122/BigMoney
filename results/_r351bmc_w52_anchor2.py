import json, sys
sys.stdout.reconfigure(encoding="utf-8")
d = json.load(open("results/perpetual_faces/n1_w49_results.json", encoding="utf-8"))
print("[null_pool_cumulative]", json.dumps(d["null_pool_cumulative"], ensure_ascii=False)[:1500])
print("[skill_line_v2_k_lift]", json.dumps(d["skill_line_v2_k_lift"], ensure_ascii=False)[:800])
print("[shards_consumed]", json.dumps(d["shards_consumed"], ensure_ascii=False)[:200])
