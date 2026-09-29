import json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = json.load(open("results/runnable_pool.json", encoding="utf-8"))
e = [x for x in p["entries"] if x.get("id") == "TRIAL-LABOR-W11-GENERATE"][0]
for k in ("consumer_plan", "prereg_ref", "runner", "runner_args", "workers_plan"):
    print("=== ", k, "===")
    print(e.get(k))
print("=== shards ===")
print(json.dumps(e.get("shards"), ensure_ascii=False, indent=1))
