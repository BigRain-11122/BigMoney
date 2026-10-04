import json, io
p = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\results\runnable_pool.json"
pool = json.loads(io.open(p, encoding="utf-8").read())
for e in pool["entries"]:
    if e["id"] == "MASS-TRIAL-W2-JUDGE-SHARD-0":
        keys = sorted(e.keys())
        print("entry keys:", keys)
        print("runner:", e.get("runner"))
        print("runner_args:", e.get("runner_args"))
        print("entry status:", e.get("status"))
        print("priority:", e.get("priority"))
        print("workers_plan:", e.get("workers_plan"))
        sh = e["shards"][0]
        print("shard keys:", sorted(sh.keys()))
        break
for e in pool["entries"]:
    if e["id"] == "TRIAL-LABOR-W14-GENERATE":
        print("--- waiting entry example ---")
        print(json.dumps({k: v for k, v in e.items() if k != "shards"}, ensure_ascii=True)[:800])
        print("shard[0]:", json.dumps(e["shards"][0], ensure_ascii=True)[:400])
        break
